"""Download and parse the 20 most recent Form 4 (insider transactions) filings.

BUG-1 fix applied: EDGAR archive URLs require UNPADDED CIK. submissions.json's
'cik' field is left-padded with zeros (e.g. '0001327567'). Use str(int(cik))
to strip leading zeros.

Working-directory hardening: tmp files are written next to <output.txt> rather
than relative-to-cwd. If Form 4s exist in submissions.json but every fetch fails,
exit non-zero.

Usage:
  py scripts/parse_form4.py raw/submissions.json raw/insider_raw.txt
"""
import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET


USER_AGENT = "Research your.email@example.com"


def fetch_with_retry(url, outfile, attempts=3):
    for i in range(attempts):
        subprocess.run(
            ["curl", "-s", "-A", USER_AGENT, url, "-o", outfile],
            capture_output=True,
        )
        if os.path.exists(outfile) and os.path.getsize(outfile) > 0:
            return True
        if i < attempts - 1:
            import time
            time.sleep(2)
    return False


def parse_form4(submissions_path, output_path):
    submissions_path = os.path.abspath(submissions_path)
    output_path = os.path.abspath(output_path)
    if not os.path.exists(submissions_path):
        print(f"ERROR: submissions file not found: {submissions_path}", file=sys.stderr)
        sys.exit(1)

    base_dir = os.path.dirname(output_path) or os.getcwd()
    os.makedirs(base_dir, exist_ok=True)

    d = json.load(open(submissions_path, encoding="utf-8"))

    # BUG-1: strip leading zeros from CIK; archive URLs require unpadded
    cik = str(int(d.get("cik", "0")))

    recent = d["filings"]["recent"]
    forms = recent["form"]
    acc = recent["accessionNumber"]
    fd = recent["filingDate"]
    pd_ = recent["primaryDocument"]

    form4s = [(fd[i], acc[i], pd_[i]) for i, f in enumerate(forms) if f == "4"][:20]
    print(f"Found {len(form4s)} Form 4 filings in submissions JSON", file=sys.stderr)

    if not form4s:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("NO_INSIDER_DATA_FOUND\n")
        print("INFO: no Form 4s in submissions; this is not necessarily an error", file=sys.stderr)
        return

    rows = []
    parse_errors = 0
    fetch_failures = 0

    for date, accession, doc in form4s:
        acc_nodash = accession.replace("-", "")
        fname = doc.split("/")[-1]
        url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc_nodash}/{fname}"
        outfile = os.path.join(base_dir, f"f4_{acc_nodash}.xml")

        if not fetch_with_retry(url, outfile):
            print(f"WARNING: fetch failed for {acc_nodash} ({url})", file=sys.stderr)
            fetch_failures += 1
            continue

        try:
            tree = ET.parse(outfile)
            root = tree.getroot()
            name = root.findtext(".//rptOwnerName", "Unknown")
            is_dir = root.findtext(".//isDirector", "false")
            is_off = root.findtext(".//isOfficer", "false")
            title = root.findtext(".//officerTitle", "")
            role = (
                "Director" if is_dir == "true"
                else (f"Officer: {title}" if is_off == "true" else "Other")
            )
            for tx in root.findall(".//nonDerivativeTransaction"):
                tx_date = tx.findtext(".//transactionDate/value", "")
                code = tx.findtext(".//transactionCode", "")
                shares = tx.findtext(".//transactionShares/value", "0")
                price = tx.findtext(".//transactionPricePerShare/value", "N/A")
                acq = tx.findtext(".//transactionAcquiredDisposedCode/value", "")
                rows.append(
                    f"{name} | {role} | {tx_date} | {acq}={code} | {shares} shares | ${price}"
                )
        except Exception as e:
            parse_errors += 1
            print(f"WARNING: parse error for {acc_nodash}: {e}", file=sys.stderr)
        finally:
            try:
                os.remove(outfile)
            except OSError:
                pass

    if not rows and fetch_failures == len(form4s):
        print(
            f"ERROR: {len(form4s)} Form 4s listed in submissions.json but all "
            f"{fetch_failures} fetches failed. Likely a working-directory or network "
            f"problem. base_dir={base_dir}",
            file=sys.stderr,
        )
        sys.exit(1)

    with open(output_path, "w", encoding="utf-8") as f:
        if rows:
            f.write("Name | Role | Date | Transaction | Shares | Price\n")
            for r in rows:
                f.write(r + "\n")
            print(f"Wrote {len(rows)} insider transactions", file=sys.stderr)
        else:
            f.write("NO_INSIDER_DATA_FOUND\n")
            print("WARNING: no insider data extracted", file=sys.stderr)

    if parse_errors > 0:
        print(f"WARNING: {parse_errors} Form 4 filings failed to parse", file=sys.stderr)
    if fetch_failures > 0:
        print(f"INFO: {fetch_failures} of {len(form4s)} Form 4 fetches failed", file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: py scripts/parse_form4.py <submissions.json> <output.txt>", file=sys.stderr)
        sys.exit(2)
    parse_form4(sys.argv[1], sys.argv[2])
