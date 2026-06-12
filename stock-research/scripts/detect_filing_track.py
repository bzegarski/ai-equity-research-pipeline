"""Detect 10-K vs FPI (20-F) filing track from SEC submissions.json.

Replaces the inline `py -c` heredoc in phases/phase0_download.md (Step 0.2a).
Standalone-script form keeps the bash invocation under 200 bytes, which avoids
the 965-byte command-parser failure that the heredoc form was hitting.
"""
import datetime
import json
import os
import sys


def main(submissions_path: str) -> int:
    with open(submissions_path) as f:
        d = json.load(f)

    recent = d["filings"]["recent"]
    forms = recent["form"]
    dates = recent["filingDate"]
    cutoff = (datetime.date.today() - datetime.timedelta(days=425)).isoformat()

    has_20f = any(f == "20-F" and dates[i] >= cutoff for i, f in enumerate(forms))
    has_10k = any(f == "10-K" and dates[i] >= cutoff for i, f in enumerate(forms))
    track = "fpi" if has_20f and not has_10k else "10k"

    out_dir = os.path.dirname(os.path.abspath(submissions_path))
    out_path = os.path.join(out_dir, "filing_track.yml")
    with open(out_path, "w") as f:
        f.write(f"track: {track}\nhas_20f: {has_20f}\nhas_10k: {has_10k}\n")

    print(f"TRACK: {track} (20F={has_20f}, 10K={has_10k})")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: detect_filing_track.py <submissions.json>", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
