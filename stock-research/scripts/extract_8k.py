"""Download the 10 most recent 8-K filings, strip HTML, write summaries to recent_8k.txt.

Flags any 8-K matching material-event keywords for downstream attention by Phase 2 (Gate)
and Agent E (Management).

Working-directory hardening: tmp files are written next to <output.txt> rather than
relative-to-cwd, so the script doesn't silently fail all fetches if invoked from the
wrong directory. If 8-Ks exist in submissions.json but every fetch fails, exit non-zero.

Usage:
  py scripts/extract_8k.py raw/submissions.json raw/recent_8k.txt
"""
import html
import json
import os
import re
import subprocess
import sys


USER_AGENT = "Research your.email@example.com"

MATERIAL_KEYWORDS = [
    "resignation", "appointed", "restatement", "impairment",
    "material weakness", "SEC investigation", "going concern",
    "departure", "retire", "termination",
]


def fetch_with_retry(url, outfile, attempts=3):
    for i in range(attempts):
        subprocess.run(
            ["curl", "-s", "-A", USER_AGENT, url, "-o", outfile],
            capture_output=True,
        )
        if os.path.exists(outfile) and os.path.getsize(outfile) > 200:
            return True
        if i < attempts - 1:
            import time
            time.sleep(2)
    return False


def extract_8k(submissions_path, output_path):
    submissions_path = os.path.abspath(submissions_path)
    output_path = os.path.abspath(output_path)
    if not os.path.exists(submissions_path):
        print(f"ERROR: submissions file not found: {submissions_path}", file=sys.stderr)
        sys.exit(1)

    base_dir = os.path.dirname(output_path) or os.getcwd()
    os.makedirs(base_dir, exist_ok=True)

    d = json.load(open(submissions_path, encoding="utf-8"))
    cik = str(int(d.get("cik", "0")))

    recent = d["filings"]["recent"]
    forms = recent["form"]
    acc = recent["accessionNumber"]
    fd = recent["filingDate"]
    pd_ = recent["primaryDocument"]

    form8ks = [(fd[i], acc[i], pd_[i]) for i, f in enumerate(forms) if f == "8-K"][:10]
    print(f"Found {len(form8ks)} recent 8-K filings", file=sys.stderr)

    if not form8ks:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("NO_8K_FILINGS_IN_SUBMISSIONS")
        print("INFO: no 8-Ks in submissions; this is not necessarily an error", file=sys.stderr)
        return

    results = []
    material_events = []
    fetch_failures = 0

    for date, accession, doc in form8ks:
        acc_nodash = accession.replace("-", "")
        url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc_nodash}/{doc}"
        outfile = os.path.join(base_dir, f"8k_tmp_{acc_nodash}.htm")

        if not fetch_with_retry(url, outfile):
            print(f"WARNING: 8-K fetch failed for {acc_nodash} ({url})", file=sys.stderr)
            fetch_failures += 1
            continue

        raw = open(outfile, encoding="utf-8", errors="replace").read()
        raw = html.unescape(raw)
        raw = re.sub(
            r"<(?:p|div|br|li|tr|h[1-6]|blockquote|section|article)[^>]*>",
            "\n",
            raw,
            flags=re.IGNORECASE,
        )
        text = re.sub(r"<[^>]+>", " ", raw)
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)

        snippet = text[:3000]
        results.append(f"=== 8-K filed {date} ===\n{snippet}")

        text_lower = text.lower()
        matched = [kw for kw in MATERIAL_KEYWORDS if kw in text_lower]
        if matched:
            material_events.append((date, accession, matched))

        try:
            os.remove(outfile)
        except OSError:
            pass

    if not results:
        print(
            f"ERROR: {len(form8ks)} 8-Ks listed in submissions.json but all "
            f"{fetch_failures} fetches failed. Likely a working-directory or network "
            f"problem. base_dir={base_dir}",
            file=sys.stderr,
        )
        sys.exit(1)

    with open(output_path, "w", encoding="utf-8") as f:
        if material_events:
            f.write("=== MATERIAL EVENTS DETECTED ===\n")
            for date, acc_, matched in material_events:
                f.write(f"  {date} | {acc_} | keywords: {', '.join(matched)}\n")
            f.write("\n")
        f.write("\n\n".join(results))

    print(
        f"Saved {len(results)} 8-K summaries; {len(material_events)} flagged as material; "
        f"{fetch_failures} fetch failures",
        file=sys.stderr,
    )


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: py scripts/extract_8k.py <submissions.json> <output.txt>", file=sys.stderr)
        sys.exit(2)
    extract_8k(sys.argv[1], sys.argv[2])
