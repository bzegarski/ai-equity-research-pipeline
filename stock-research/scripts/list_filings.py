"""Print accession numbers + primary documents for 10-K / 10-Q / DEF 14A.

Replaces the inline `py -c` heredoc in phases/phase0_download.md (Step 0.2,
the second block). Standalone-script form keeps the bash invocation under
200 bytes, avoiding the 965-byte command-parser failure.
"""
import json
import sys


def main(submissions_path: str) -> int:
    with open(submissions_path) as f:
        d = json.load(f)

    print("name:", d.get("name"))
    recent = d["filings"]["recent"]
    forms = recent["form"]
    for ft in ["10-K", "10-Q", "DEF 14A"]:
        for i, f in enumerate(forms):
            if f == ft:
                print(
                    ft,
                    recent["filingDate"][i],
                    recent["accessionNumber"][i],
                    recent["primaryDocument"][i],
                )
                break
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: list_filings.py <submissions.json>", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
