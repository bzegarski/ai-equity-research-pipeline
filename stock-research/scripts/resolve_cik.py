"""Parse cik_search.json output from EDGAR full-text search to extract CIK and company name.

Prefers hits whose display_name explicitly contains the input ticker in parentheses
(e.g. "PAYCHEX INC (PAYX) (CIK 0000723531)"). EDGAR full-text search returns any
filing mentioning the query string, so without ticker matching, "MSFT" can return
Activision Blizzard or other unrelated issuers that mentioned MSFT in a filing.

Falls back to the canonical SEC `company_tickers.json` map (keyed by upper-cased
ticker) when the full-text-search regex misses. This handles:
  - Multi-ticker display strings ("(NVO, NONOF)" — NVO run)
  - Issuers whose display_name does not contain the ticker at all (DECK)
  - Wrong-issuer first-hit problems (SNOW initially returned Peak Resorts)

Usage:
  py scripts/resolve_cik.py <path_to_cik_search.json> <ticker>
  py scripts/resolve_cik.py <path_to_cik_search.json>          # legacy: first hit (warns)
"""
import json
import re
import sys
import urllib.request


COMPANY_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"


def lookup_company_tickers(ticker_upper):
    """Fetch SEC's canonical ticker→CIK map and return (cik, name) or None."""
    try:
        req = urllib.request.Request(
            COMPANY_TICKERS_URL,
            headers={
                "User-Agent": "stock-research-skill your.email@example.com",
                "Accept": "application/json",
                "Host": "www.sec.gov",
            },
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"WARNING: company_tickers.json fetch failed: {e}", file=sys.stderr)
        return None

    for entry in data.values():
        if entry.get("ticker", "").upper() == ticker_upper:
            cik = str(entry.get("cik_str", "")).zfill(10)
            name = entry.get("title", "")
            return cik, name
    return None


def main(path, ticker=None):
    try:
        d = json.load(open(path, encoding="utf-8"))
    except Exception as e:
        print(f"ERROR: cannot read {path}: {e}", file=sys.stderr)
        sys.exit(1)

    hits = d.get("hits", {}).get("hits", [])
    candidates = []
    for h in hits:
        src = h.get("_source", {})
        names = src.get("display_names", [])
        ciks = src.get("ciks", [])
        if ciks and names:
            candidates.append((ciks[0], names[0]))

    if ticker:
        ticker_upper = ticker.strip().upper()
        # Loosened: also match "(NVO, NONOF)" style multi-ticker display strings.
        # Boundaries: ticker is preceded by `(` or `,\s*`, followed by `)` or `,`.
        ticker_pattern = re.compile(
            r"[(,]\s*" + re.escape(ticker_upper) + r"\s*[),]"
        )
        for cik, name in candidates:
            if ticker_pattern.search(name.upper()):
                print(f"CIK: {cik} | Name: {name}")
                return

        # Fallback: SEC canonical ticker map.
        result = lookup_company_tickers(ticker_upper)
        if result:
            cik, name = result
            print(
                f"INFO: resolved via company_tickers.json fallback "
                f"(no display_name match in cik_search.json hits)",
                file=sys.stderr,
            )
            print(f"CIK: {cik} | Name: {name}")
            return

        if candidates:
            inspected = [c[1] for c in candidates[:5]]
            print(
                f"ERROR: no hit's display_name contains '{ticker_upper}' "
                f"and company_tickers.json has no entry. "
                f"Top candidates inspected: {inspected}",
                file=sys.stderr,
            )
        else:
            print(
                f"ERROR: cik_search.json has no hits and "
                f"company_tickers.json has no entry for '{ticker_upper}'.",
                file=sys.stderr,
            )
        sys.exit(1)

    if not candidates:
        print("ERROR: no CIK match in hits", file=sys.stderr)
        sys.exit(1)

    cik, name = candidates[0]
    print(
        "WARNING: no ticker provided; falling back to first hit. "
        "This is silent-corruption-prone (e.g. 'MSFT' returned Activision Blizzard). "
        "Pass the ticker as the second argument.",
        file=sys.stderr,
    )
    print(f"CIK: {cik} | Name: {name}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: py scripts/resolve_cik.py <cik_search.json> <ticker>", file=sys.stderr)
        sys.exit(2)
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
