"""Detect whether a transcript file is verbatim or a structured summary, then write
a TRANSCRIPT_SOURCE_QUALITY header at the top of the file.

Classification combines a host-domain prior with a structural-content score:

  Domain prior:
    Verbatim-eligible (positive):  *.q4cdn.com, *.q4ir.com, *.gcs-web.com,
                                   sec.gov, edgar.sec.gov, IR sub-domains
                                   matching investors/ir/<ticker>.com
    Pro-summary (negative):        fool.com, motleyfool.com, finance.yahoo.com,
                                   investing.com, marketwatch.com,
                                   globenewswire.com, seekingalpha.com (often
                                   re-summarised when WebFetched)

  Structural score (added):  ALL-CAPS speaker labels (≥2), '(Operator Direction.)',
                             'Operator:', 'Q&A', 'analyst:', '[Operator
                             Instructions]'.
  Structural score (subtracted): 'key takeaways', 'highlights', short bullet
                                 lists, headings like 'Earnings Call Summary'.

Decision:
  Verbatim only if structure_score >= STRUCT_THRESHOLD AND domain_prior >= 0.
  A strong structure score (>= STRUCT_OVERRIDE) overrides a single negative
  domain prior; multiple negative domains still block.

This replaces the prior text-only OR-logic that auto-tagged Motley Fool / Yahoo /
Investing.com LLM-passthrough content as verbatim on DECK and SNOW.

Usage:
  py scripts/detect_transcript_format.py raw/transcripts_raw.txt [URL1,URL2,...]

A `transcripts_source.txt` sidecar is also accepted (one URL per line) when no
CSV is passed; Phase 0 writes that file when collecting from multiple sources.
"""
import os
import re
import sys


CAPS_LABEL_RE = re.compile(r"(?m)^\s*[A-Z][A-Z][A-Z][A-Z\s,&\.'-]{2,40}:")

VERBATIM_TEXT_SIGNALS = [
    ("question-and-answer", 2),
    ("q&a session", 2),
    ("analyst:", 1),
    ("operator:", 2),
    ("[operator instructions]", 2),
    ("thank you, operator", 1),
    ("(operator direction.)", 2),
    ("(operator instructions)", 2),
    ("conference call participants", 1),
    ("prepared remarks", 1),
]

SUMMARY_TEXT_SIGNALS = [
    ("key takeaways", 2),
    ("earnings call summary", 3),
    ("here are the highlights", 2),
    ("3 things you should know", 2),
    ("what motley fool", 3),
    ("the motley fool", 2),
    ("disclosure: i ", 1),
    ("editor's note", 1),
]

NEGATIVE_DOMAINS = [
    "fool.com",
    "motleyfool.com",
    "finance.yahoo.com",
    "yahoo.com",
    "investing.com",
    "marketwatch.com",
    "globenewswire.com",
    "seekingalpha.com",
    "benzinga.com",
    "thestreet.com",
]

POSITIVE_DOMAINS_SUFFIX = [
    "q4cdn.com",
    "q4ir.com",
    "gcs-web.com",
    "edgar.sec.gov",
    "sec.gov",
]

STRUCT_THRESHOLD = 3
STRUCT_OVERRIDE = 7


def domain_prior(urls):
    if not urls:
        return 0, []
    score = 0
    notes = []
    for u in urls:
        u_low = u.lower()
        for d in NEGATIVE_DOMAINS:
            if d in u_low:
                score -= 2
                notes.append(f"-2 (host {d})")
                break
        else:
            for d in POSITIVE_DOMAINS_SUFFIX:
                if u_low.endswith(d) or f"//{d}" in u_low or f".{d}" in u_low:
                    score += 2
                    notes.append(f"+2 (host {d})")
                    break
    return score, notes


def structure_score(sample_original):
    sample_lower = sample_original.lower()
    score = 0
    notes = []
    caps_count = len(CAPS_LABEL_RE.findall(sample_original))
    if caps_count >= 4:
        score += 4
        notes.append(f"+4 (CAPS labels x{caps_count})")
    elif caps_count >= 2:
        score += 2
        notes.append(f"+2 (CAPS labels x{caps_count})")
    for sig, w in VERBATIM_TEXT_SIGNALS:
        if sig in sample_lower:
            score += w
            notes.append(f"+{w} ({sig!r})")
    for sig, w in SUMMARY_TEXT_SIGNALS:
        if sig in sample_lower:
            score -= w
            notes.append(f"-{w} ({sig!r})")
    return score, notes


def classify(sample, urls):
    dp, dp_notes = domain_prior(urls)
    ss, ss_notes = structure_score(sample)
    rationale = "; ".join(dp_notes + ss_notes) or "(no signals)"

    if ss >= STRUCT_OVERRIDE and dp >= -2:
        return "verbatim", dp, ss, rationale + " | OVERRIDE: strong structure"
    if ss >= STRUCT_THRESHOLD and dp >= 0:
        return "verbatim", dp, ss, rationale
    return "structured_summary", dp, ss, rationale


def parse_sources(sources_csv, sidecar_path):
    urls = []
    if sources_csv:
        urls.extend([u.strip() for u in sources_csv.split(",") if u.strip()])
    if os.path.exists(sidecar_path):
        with open(sidecar_path, encoding="utf-8") as f:
            urls.extend([line.strip() for line in f if line.strip()])
    return urls


def detect_and_tag(path, sources_csv=""):
    text = open(path, encoding="utf-8", errors="replace").read()

    if text.startswith("TRANSCRIPT_SOURCE_QUALITY:"):
        print("Already tagged; no change", file=sys.stderr)
        return

    sidecar = os.path.join(os.path.dirname(path), "transcripts_source.txt")
    urls = parse_sources(sources_csv, sidecar)

    if not text.strip() or text.strip().startswith("TRANSCRIPT_UNAVAILABLE"):
        header = "TRANSCRIPT_SOURCE_QUALITY: unavailable\n"
        if urls:
            header += f"TRANSCRIPT_SOURCES_USED: {','.join(urls)}\n"
        header += "\n"
        with open(path, "w", encoding="utf-8") as f:
            f.write(header + text)
        return

    sample = text[:5000]
    quality, dp, ss, rationale = classify(sample, urls)

    header = f"TRANSCRIPT_SOURCE_QUALITY: {quality}\n"
    if urls:
        header += f"TRANSCRIPT_SOURCES_USED: {','.join(urls)}\n"
    header += f"TRANSCRIPT_DETECTION_NOTES: domain_prior={dp} structure_score={ss} | {rationale}\n"
    if quality == "structured_summary":
        header += (
            "[NOTE: This appears to be a structured summary, not a verbatim transcript. "
            "Numerical data and direct quotes may be paraphrased. Tag transcript-derived "
            "claims Medium confidence at most.]\n"
        )
    header += "\n"

    with open(path, "w", encoding="utf-8") as f:
        f.write(header + text)
    print(
        f"Tagged as {quality} (domain_prior={dp}, structure_score={ss})",
        file=sys.stderr,
    )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: py scripts/detect_transcript_format.py <transcripts.txt> [sources_csv]",
              file=sys.stderr)
        sys.exit(2)
    sources = sys.argv[2] if len(sys.argv) > 2 else ""
    detect_and_tag(sys.argv[1], sources)
