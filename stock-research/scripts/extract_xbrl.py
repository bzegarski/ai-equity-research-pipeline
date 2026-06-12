"""Extract key financial concepts from EDGAR XBRL companyfacts JSON.

Reads raw/<json_file>, writes a pipe-delimited summary table to stdout.
Logs missing concepts to stderr.

Includes Slice 1 robustness improvements:
- Stock-split detection (year-over-year jumps > 30% in SharesOutstanding)
- Prefer dei/EntityCommonStockSharesOutstanding (point-in-time) for current count
- 10-K/A vs 10-K dedup by end date

Usage:
  py scripts/extract_xbrl.py raw/10k_xbrl.json > raw/xbrl_summary.txt 2> raw/xbrl_missing.txt
"""
import json
import sys


CONCEPT_GROUPS = [
    ("Revenue", [
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "RevenueFromContractWithCustomerIncludingAssessedTax",  # CRWD precedent (2026-05-10 audit fix)
        "Revenues",
        "SalesRevenueNet",
    ]),
    ("NetIncome", ["NetIncomeLoss"]),
    ("GrossProfit", ["GrossProfit"]),
    ("OperatingIncome", ["OperatingIncomeLoss"]),
    ("EPS_Basic", ["EarningsPerShareBasic"]),
    ("EPS_Diluted", ["EarningsPerShareDiluted"]),
    ("OperatingCashFlow", ["NetCashProvidedByUsedInOperatingActivities"]),
    ("Capex", ["PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsForCapitalImprovements"]),
    ("DA", ["DepreciationDepletionAndAmortization", "DepreciationAndAmortization", "AmortizationOfIntangibleAssets"]),
    ("SBC", ["ShareBasedCompensation", "AllocatedShareBasedCompensationExpense"]),
    ("RnD", ["ResearchAndDevelopmentExpense"]),
    ("SGA", ["SellingGeneralAndAdministrativeExpense"]),
    ("Cash", ["CashAndCashEquivalentsAtCarryingValue", "CashCashEquivalentsAndShortTermInvestments"]),
    ("LongTermDebt", ["LongTermDebt", "LongTermDebtNoncurrent", "DebtLongtermAndShorttermCombinedAmount"]),
    ("TotalAssets", ["Assets"]),
    ("Inventory", ["InventoryNet"]),
    ("CostOfRevenue", ["CostOfRevenue", "CostOfGoodsAndServicesSold"]),
    ("StockholdersEquity", ["StockholdersEquity"]),
    ("DilutedShares", ["WeightedAverageNumberOfDilutedSharesOutstanding"]),
    ("SharesOutstanding", ["CommonStockSharesOutstanding"]),
]


def get_annual(usgaap, concept):
    """Return list of annual FY entries for a concept, deduplicated by end date."""
    if concept not in usgaap:
        return None, None
    for unit_type, entries in usgaap[concept].get("units", {}).items():
        annual = [e for e in entries if e.get("form") in ("10-K", "10-K/A") and e.get("fp") == "FY"]
        annual.sort(key=lambda x: x.get("end", ""), reverse=True)
        seen = set()
        deduped = [e for e in annual if e.get("end") not in seen and not seen.add(e.get("end"))]
        if deduped:
            return deduped, unit_type
    return None, None


def detect_share_jumps(rows):
    """Detect year-over-year share-count jumps > 30% (likely stock splits)."""
    share_rows = [r for r in rows if r.startswith("SharesOutstanding (")]
    if len(share_rows) < 2:
        return []
    parsed = []
    for line in share_rows:
        try:
            parts = line.split(" | ")
            end_date = parts[1]
            val = float(parts[2])
            parsed.append((end_date, val, line))
        except (ValueError, IndexError):
            continue
    parsed.sort(key=lambda x: x[0])  # ascending by date
    jumps = []
    for i in range(len(parsed) - 1):
        older_val = parsed[i][1]
        newer_val = parsed[i + 1][1]
        if older_val <= 0:
            continue
        ratio = newer_val / older_val
        # Forward split: ratio > 1.3. Reverse split: ratio < 0.77 (= 1/1.3).
        # Both directions can silently break per-share intrinsic if undetected.
        if ratio > 1.3 or (ratio > 0 and ratio < 0.77):
            direction = "stock split" if ratio > 1.3 else "reverse split"
            jumps.append(
                f"SHARES_JUMP: {parsed[i][0]} ({older_val:,.0f}) -> {parsed[i+1][0]} ({newer_val:,.0f}) "
                f"= {ratio:.2f}x (possible {direction}; check 8-K for announcement)"
            )
    return jumps


def main(path):
    try:
        d = json.load(open(path, encoding="utf-8"))
    except Exception as e:
        print(f"ERROR: cannot read {path}: {e}", file=sys.stderr)
        sys.exit(1)

    usgaap = d.get("facts", {}).get("us-gaap", {})
    ifrs = d.get("facts", {}).get("ifrs-full", {})
    dei = d.get("facts", {}).get("dei", {})

    # Taxonomy dispatch: if us-gaap is empty/missing but ifrs-full is present,
    # delegate to the IFRS extractor. Both extractors emit `TAXONOMY:` and
    # `CURRENCY:` header lines so downstream prompts can read either uniformly.
    #
    # Foreign-filer fix: scan IFRS facts to find the dominant reporting currency
    # and pass it through. Without this, the IFRS extractor's pick_unit defaults
    # to USD-first per-concept and silently mixes currencies (NVO bug: Revenue
    # picks USD supplementary disclosure while NetIncome picks DKK; net margin
    # comes out 167%).
    if not usgaap and ifrs:
        import os
        ifrs_script = os.path.join(os.path.dirname(__file__), "extract_ifrs_xbrl.py")

        # Detect dominant currency: tally unit-types across all monetary concepts
        # (skip shares/pure non-monetary units).
        currency_counts = {}
        for concept_data in ifrs.values():
            for unit in concept_data.get("units", {}):
                if unit not in ("shares", "pure"):
                    currency_counts[unit] = currency_counts.get(unit, 0) + 1
        dominant_currency = (
            max(currency_counts, key=currency_counts.get) if currency_counts else None
        )

        print(
            f"INFO: us-gaap facts empty but ifrs-full present; delegating to {ifrs_script}",
            file=sys.stderr,
        )
        if dominant_currency:
            print(
                f"INFO: detected dominant currency {dominant_currency} "
                f"(counts: {currency_counts}); passing as --reporting-currency",
                file=sys.stderr,
            )

        import runpy
        sys.argv = [ifrs_script, path]
        if dominant_currency:
            sys.argv.extend(["--reporting-currency", dominant_currency])
        runpy.run_path(ifrs_script, run_name="__main__")
        return

    print("TAXONOMY: us-gaap")
    print("CURRENCY: USD")

    rows = []
    missing = []

    for label, names in CONCEPT_GROUPS:
        found = False
        for name in names:
            annual, unit_type = get_annual(usgaap, name)
            if annual:
                for e in annual[:5]:
                    rows.append(
                        f"{label} ({name}) | {e.get('end', '?')} | {e.get('val', '?')} | {unit_type}"
                    )
                found = True
                break
        if not found:
            missing.append(label)

    # Prefer dei point-in-time concepts for current share count (split-aware)
    for concept in ["EntityCommonStockSharesOutstanding"]:
        if concept in dei:
            for unit_type, entries in dei[concept].get("units", {}).items():
                entries_sorted = sorted(entries, key=lambda x: x.get("end", ""), reverse=True)
                if entries_sorted:
                    e = entries_sorted[0]
                    rows.append(
                        f"dei/{concept} | {e.get('end', '?')} | {e.get('val', '?')} | {unit_type}"
                    )

    # Detect stock splits in SharesOutstanding history
    jumps = detect_share_jumps(rows)

    # Compute derived ratios for context. PAYX bug: NetIncomeLoss XBRL only had
    # 2014-2015 entries, so the "first NetIncome" row was 2015 while OCF was FY25.
    # Ratio came out 2.82x (bogus). Now: require both anchors to share fiscal year;
    # if not, emit ANCHOR_INCOMPLETE flag instead of a misleading ratio.
    def first_row(prefix):
        for r in rows:
            if r.startswith(prefix):
                parts = r.split(" | ")
                if len(parts) >= 4:
                    try:
                        return parts[1], float(parts[2])
                    except (ValueError, IndexError):
                        return None
        return None

    ocf = first_row("OperatingCashFlow (")
    ni = first_row("NetIncome (")
    if ocf and ni and ni[1] != 0:
        ocf_end, ocf_val = ocf
        ni_end, ni_val = ni
        if ocf_end[:4] == ni_end[:4]:
            rows.append(
                f"OCF_to_NetIncome (computed) | {ocf_end} | {ocf_val / ni_val:.2f} | ratio"
            )
        else:
            rows.append(
                f"OCF_to_NetIncome (computed) | ANCHOR_INCOMPLETE | "
                f"OCF@{ocf_end} / NI@{ni_end} not from same FY; ratio suppressed | flag"
            )
            print(
                f"WARNING: OCF/NetIncome anchor mismatch (OCF {ocf_end} vs NI {ni_end}); "
                f"ratio suppressed to avoid misleading downstream interpretation",
                file=sys.stderr,
            )

    for r in rows:
        print(r)

    if jumps:
        for j in jumps:
            print(j, file=sys.stderr)

    if missing:
        print(f"XBRL_MISSING: {','.join(missing)}", file=sys.stderr)
        print(file=sys.stderr)
        print("Available us-gaap concepts (first 30):", file=sys.stderr)
        for c in list(usgaap.keys())[:30]:
            print(f"  {c}", file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: py scripts/extract_xbrl.py <xbrl_json>", file=sys.stderr)
        sys.exit(2)
    main(sys.argv[1])
