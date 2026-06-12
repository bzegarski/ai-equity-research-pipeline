"""Track-aware TOC/cover-page trim. Reads `raw/<filing>_raw.txt` (the unmodified
HTML-stripped text from `strip_10k.py`) and writes a canonical version with
TOC and cover-page boilerplate removed.

`strip_10k.py` stays minimal — block-tag-to-newline only. This script handles
prefix trimming downstream so the cleaning step is auditable and per-track.

Tracks:
  10k  — find first body-prose "ITEM 1. BUSINESS" anchor; trim TOC before it.
  20f  — find first body-prose "ITEM 4. INFORMATION ON THE COMPANY" anchor or
         management-report start; trim cover/TOC before it.
  6k   — trim only the SEC cover header (headers + Form 6-K boilerplate);
         leave attachment content untouched.

If no anchor is found, leave the file unchanged and log `STRIPPED_TOC: skipped`.
Otherwise log `STRIPPED_TOC: N chars (track=X)`.

Usage:
  py scripts/clean_canonical.py raw/10k_raw.txt --track 10k [--out raw/10k_canonical.txt]
  py scripts/clean_canonical.py raw/20f_raw.txt --track 20f
  py scripts/clean_canonical.py raw/6k_raw.txt --track 6k
"""
import argparse
import os
import re
import sys


ANCHOR_10K = re.compile(r"item\s*1\.\s*business", re.IGNORECASE)
# Strict uppercase anchor for post-strip enforcement (CRWD 2026-05-10 audit fix):
# After the initial trim, the surviving text must start at the uppercase prose
# form "ITEM 1. BUSINESS". If a secondary inline TOC survived the first pass,
# this catches it. If neither matches, the file is suspect — emit CRITICAL.
ANCHOR_10K_STRICT = re.compile(r"\bITEM\s*1\.\s*BUSINESS\b")
ANCHOR_20F = re.compile(
    r"item\s*4\.?\s*(?:information\s+on\s+the\s+company|introduction)",
    re.IGNORECASE,
)
ANCHOR_20F_LOOSE = re.compile(r"\bintroducing\s+\w+", re.IGNORECASE)

SEC_COVER_END_6K = re.compile(
    r"(securities\s+and\s+exchange\s+commission.*?form\s+6-?k.*?)(?=\n\s*[A-Z][a-z])",
    re.IGNORECASE | re.DOTALL,
)

ALPHA_DENSITY_MIN = 200  # chars of alpha within window must exceed this
ANCHOR_WINDOW = 1500     # chars after anchor candidate to score density
TOC_LOOKBACK = 50        # chars before anchor that should not contain TOC pattern
TOC_PAGE_NUMBER_RE = re.compile(r"\n\s*\d{1,4}\s*\n")


def alpha_density(text):
    return sum(1 for c in text if c.isalpha())


def find_body_anchor(text, anchor_re):
    """First anchor occurrence whose next ANCHOR_WINDOW chars are alpha-rich
    AND not immediately preceded by a TOC-style page-number-only line."""
    for m in anchor_re.finditer(text):
        end = m.end()
        window = text[end:end + ANCHOR_WINDOW]
        if alpha_density(window) < ALPHA_DENSITY_MIN:
            continue
        # Reject TOC-style preceding context (a bare page number on its own line
        # within the previous TOC_LOOKBACK chars suggests TOC).
        before = text[max(0, m.start() - TOC_LOOKBACK):m.start()]
        if TOC_PAGE_NUMBER_RE.search("\n" + before + "\n"):
            continue
        return m.start()
    return -1


def trim_10k(text):
    pos = find_body_anchor(text, ANCHOR_10K)
    if pos == -1 or pos < 200:
        return text, 0
    trimmed_text = text[pos:]
    # Post-strip enforcement (CRWD 2026-05-10 audit precedent): the surviving
    # text must start at the uppercase prose form "ITEM 1. BUSINESS". If a
    # secondary inline TOC survived the first pass (the algorithm matched a
    # case-insensitive TOC entry instead of the body-prose anchor), the strict
    # uppercase anchor will find the real start further down.
    strict_match = ANCHOR_10K_STRICT.search(trimmed_text[:50000])
    if strict_match and strict_match.start() > 200:
        # Real body prose is further in; trim again.
        extra = strict_match.start()
        return trimmed_text[extra:], pos + extra
    return trimmed_text, pos


def assert_10k_anchor(cleaned_text):
    """After the trim, verify the cleaned text actually starts at uppercase
    'ITEM 1. BUSINESS' prose. Returns (ok, distance_to_anchor).
    - ok=True if uppercase anchor is within first 200 chars (clean start)
    - ok=False if anchor is missing entirely or buried > 200 chars in
    """
    m = ANCHOR_10K_STRICT.search(cleaned_text[:50000])
    if m is None:
        return False, -1
    return (m.start() <= 200), m.start()


def trim_20f(text):
    pos = find_body_anchor(text, ANCHOR_20F)
    if pos == -1:
        m = ANCHOR_20F_LOOSE.search(text)
        if m and m.start() > 200:
            window = text[m.end():m.end() + ANCHOR_WINDOW]
            if alpha_density(window) >= ALPHA_DENSITY_MIN:
                return text[m.start():], m.start()
        return text, 0
    if pos < 200:
        return text, 0
    return text[pos:], pos


def trim_6k(text):
    """Strip only the SEC cover header. The attachment body is preserved
    untouched because 6-K attachments vary widely in structure."""
    m = SEC_COVER_END_6K.search(text[:5000])
    if not m:
        return text, 0
    cut = m.end()
    if cut < 200:
        return text, 0
    return text[cut:], cut


TRIMMERS = {"10k": trim_10k, "20f": trim_20f, "fpi": trim_20f, "6k": trim_6k}


def main(input_path, track, out_path=None):
    text = open(input_path, encoding="utf-8").read()
    trimmer = TRIMMERS[track]
    cleaned, trimmed = trimmer(text)

    if out_path is None:
        out_path = input_path  # in-place

    if trimmed == 0:
        # Leave file unchanged when no TOC to strip (anchor missing or already at start).
        print(f"STRIPPED_TOC: skipped (track={track}; no TOC prefix detected)", file=sys.stderr)
        if out_path != input_path:
            open(out_path, "w", encoding="utf-8").write(text)
        return

    open(out_path, "w", encoding="utf-8").write(cleaned)
    print(f"STRIPPED_TOC: {trimmed} chars (track={track})", file=sys.stderr)

    # Post-strip enforcement (CRWD audit precedent): for 10-K specifically,
    # verify the cleaned text starts at the uppercase prose anchor.
    if track == "10k":
        ok, distance = assert_10k_anchor(cleaned)
        if not ok:
            if distance == -1:
                print(
                    f"CRITICAL_TOC_STRIP: uppercase 'ITEM 1. BUSINESS' anchor "
                    f"not found in cleaned 10-K. File is suspect — audit gate "
                    f"should block downstream agents.",
                    file=sys.stderr,
                )
            else:
                print(
                    f"CRITICAL_TOC_STRIP: cleaned 10-K starts {distance} chars "
                    f"before uppercase 'ITEM 1. BUSINESS' anchor. Inline TOC "
                    f"may have survived the strip — audit gate should review.",
                    file=sys.stderr,
                )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_path")
    parser.add_argument("--track", required=True, choices=["10k", "20f", "fpi", "6k"])
    parser.add_argument("--out", default=None)
    args = parser.parse_args()
    main(args.input_path, args.track, args.out)
