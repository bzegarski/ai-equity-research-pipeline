"""Extract key financial concepts from EDGAR XBRL companyfacts JSON for IFRS filers.

Mirrors `extract_xbrl.py` for the `ifrs-full` taxonomy. Promoted from the ad-hoc
NVO extractor with the following generalizations the plan required:

  - Broader IFRS concept aliases (33 concepts; covers DKK/EUR/CHF/USD/GBP issuers
    likely to appear: NVO, ONON, ASML, ROG, Diageo, etc.)
  - Documented currency preference order: USD → reporting currency → first available
  - Explicit `TAXONOMY:` and `CURRENCY:` header rows in the summary
  - Pipe-delimited row format that matches `extract_xbrl.py` so downstream
    cross-checks read either taxonomy uniformly:
      `Label (concept) | end | val | unit_type`

Usage:
  py scripts/extract_ifrs_xbrl.py raw/10k_xbrl.json [--reporting-currency DKK]
      > raw/xbrl_summary.txt 2> raw/xbrl_missing.txt

Caller is responsible for choosing this script (or `extract_xbrl.py`) based on
taxonomy detection. `extract_xbrl.py` auto-delegates here when `us-gaap` is empty
and `ifrs-full` is present.
"""
import argparse
import json
import sys
from datetime import date


CONCEPT_GROUPS = [
    ("Revenue", ["Revenue", "RevenueFromContractsWithCustomers"]),
    ("CostOfRevenue", ["CostOfSales"]),
    ("GrossProfit", ["GrossProfit"]),
    ("OperatingIncome", ["ProfitLossFromOperatingActivities", "OperatingIncomeLoss"]),
    ("NetIncome", ["ProfitLoss", "ProfitLossAttributableToOwnersOfParent"]),
    ("EPS_Basic", ["BasicEarningsLossPerShare"]),
    ("EPS_Diluted", ["DilutedEarningsLossPerShare"]),
    ("OperatingCashFlow", [
        "CashFlowsFromUsedInOperatingActivities",
        "NetCashFlowsFromUsedInOperatingActivities",
    ]),
    ("Capex", [
        "PurchaseOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities",
        "PaymentsForPurchaseOfPropertyPlantAndEquipment",
        "PurchaseOfPropertyPlantAndEquipment",
    ]),
    ("DA", [
        "DepreciationAndAmortisationExpense",
        "DepreciationAmortisationAndImpairmentLossReversalOfImpairmentLossRecognisedInProfitOrLoss",
        "Depreciation",
        "AmortisationOfIntangibleAssetsOtherThanGoodwill",
    ]),
    ("RnD", ["ResearchAndDevelopmentExpense"]),
    ("SGA", [
        "SellingGeneralAndAdministrativeExpense",
        "SellingExpense",
        "AdministrativeExpense",
    ]),
    ("FinanceCosts", ["FinanceCosts", "InterestExpense"]),
    ("IncomeTaxExpense", ["IncomeTaxExpenseContinuingOperations", "IncomeTaxExpense"]),
    ("Cash", [
        "CashAndCashEquivalents",
        "CashAndBankBalances",
    ]),
    ("TotalAssets", ["Assets"]),
    ("CurrentAssets", ["CurrentAssets"]),
    ("NonCurrentAssets", ["NoncurrentAssets"]),
    ("Inventory", ["Inventories"]),
    ("TradeReceivables", ["TradeAndOtherCurrentReceivables", "TradeReceivables"]),
    ("CurrentLiab", ["CurrentLiabilities"]),
    ("NonCurrentLiab", ["NoncurrentLiabilities"]),
    ("TotalLiab", ["Liabilities"]),
    ("Equity", ["Equity", "EquityAttributableToOwnersOfParent"]),
    ("LongTermDebt", ["NoncurrentBorrowings", "LongtermBorrowings"]),
    ("ShortTermDebt", ["CurrentBorrowings", "ShorttermBorrowings"]),
    ("LeaseLiabilities", ["LeaseLiabilities"]),
    ("Goodwill", ["Goodwill"]),
    ("Intangibles", ["IntangibleAssetsOtherThanGoodwill"]),
    ("PPE", ["PropertyPlantAndEquipment"]),
    ("DividendsPaid", ["DividendsPaid", "DividendsPaidClassifiedAsFinancingActivities"]),
    ("ShareRepurchases", ["PaymentsForRepurchaseOfTreasuryShares", "PaymentsToAcquireShares"]),
    ("SharesOutstanding", [
        "NumberOfSharesOutstanding",
        "NumberOfSharesIssued",
    ]),
]

CURRENCY_PREFERENCE_DEFAULT = ["USD", "EUR", "DKK", "CHF", "GBP", "SEK", "NOK", "JPY"]

# Sentinel returned by pick_unit when reporting_currency was supplied but the
# concept does not report in that currency. Caller emits CURRENCY_MIX_WARNING
# and skips the concept rather than silently substituting a different currency.
CURRENCY_MISMATCH = object()


def pick_unit(units, reporting_currency=None):
    """Pick the preferred currency unit.

    If `reporting_currency` is supplied, prefer it absolutely. If the concept
    does NOT report in that currency, return (CURRENCY_MISMATCH, None) so the
    caller can log a CURRENCY_MIX_WARNING and skip — never silently substitute
    a different currency (NVO bug: caused 167% net margin from mixed USD/DKK).

    If `reporting_currency` is not supplied, fall back to project default
    preference order (USD-first), then any available unit. Non-monetary units
    (shares, pure) are returned as-is when they're the only key.
    """
    if not units:
        return None, None
    if reporting_currency:
        if reporting_currency in units:
            return reporting_currency, units[reporting_currency]
        # Concept exists but lacks reporting_currency.
        if any(u not in ("shares", "pure") for u in units):
            return CURRENCY_MISMATCH, None
        # Non-monetary concept (e.g. shares-denominated): pass through.
        only = next(iter(units))
        return only, units[only]
    # No reporting_currency supplied: project-default preference order.
    pref_order = []
    for c in CURRENCY_PREFERENCE_DEFAULT:
        if c in units:
            pref_order.append(c)
    for c in pref_order:
        if c in units:
            return c, units[c]
    only = next(iter(units))
    return only, units[only]


def fy_periods(facts):
    """Return [(end, val, form, fp)] for full-year periods (350-380 day range).
    Deduped by end-date; prefer 20-F entries over 6-K."""
    out = []
    for f in facts:
        end = f.get("end")
        start = f.get("start")
        val = f.get("val")
        if val is None or end is None:
            continue
        if start:
            try:
                s = date.fromisoformat(start)
                e = date.fromisoformat(end)
                days = (e - s).days
                if not (350 <= days <= 380):
                    continue
            except Exception:
                continue
        out.append((end, val, f.get("form", ""), f.get("fp", "")))

    by_end = {}
    for end, val, form, fp in out:
        existing = by_end.get(end)
        if existing is None:
            by_end[end] = (val, form, fp)
        else:
            if "20-F" in form and "20-F" not in existing[1]:
                by_end[end] = (val, form, fp)
    return sorted(by_end.items(), reverse=True)


def instant_snapshots(facts):
    """For balance-sheet facts (no `start` date), return one entry per fiscal year-end."""
    out = []
    for f in facts:
        end = f.get("end")
        val = f.get("val")
        if val is None or end is None or f.get("start"):
            continue
        out.append((end, val, f.get("form", "")))
    by_end = {}
    for end, val, form in out:
        existing = by_end.get(end)
        if existing is None or ("20-F" in form and "20-F" not in existing[1]):
            by_end[end] = (val, form)
    return sorted(by_end.items(), reverse=True)


def detect_share_jumps(rows):
    """Detect year-over-year share-count jumps > 30% (likely splits)."""
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
    parsed.sort(key=lambda x: x[0])
    jumps = []
    for i in range(len(parsed) - 1):
        older = parsed[i][1]
        newer = parsed[i + 1][1]
        if older > 0 and (newer / older) > 1.3:
            ratio = newer / older
            jumps.append(
                f"SHARES_JUMP: {parsed[i][0]} ({older:,.0f}) -> {parsed[i+1][0]} "
                f"({newer:,.0f}) = {ratio:.2f}x (possible split; check 6-K announcement)"
            )
    return jumps


def main(path, reporting_currency=None):
    try:
        d = json.load(open(path, encoding="utf-8"))
    except Exception as e:
        print(f"ERROR: cannot read {path}: {e}", file=sys.stderr)
        sys.exit(1)

    facts = d.get("facts", {}).get("ifrs-full", {})
    if not facts:
        print("ERROR: no ifrs-full facts in companyfacts JSON", file=sys.stderr)
        sys.exit(1)

    rows = []
    missing = []
    currency_mismatches = []
    primary_unit = None

    print(f"TAXONOMY: ifrs-full")
    if reporting_currency:
        print(f"CURRENCY: preference={reporting_currency}")
    else:
        print("CURRENCY: preference=auto (USD>EUR>DKK>CHF>GBP)")

    for label, names in CONCEPT_GROUPS:
        chosen = next((n for n in names if n in facts), None)
        if chosen is None:
            missing.append(label)
            continue
        units = facts[chosen].get("units", {})
        unit, vals = pick_unit(units, reporting_currency)
        if unit is CURRENCY_MISMATCH:
            available = sorted(u for u in units if u not in ("shares", "pure"))
            currency_mismatches.append(
                f"{label} ({chosen}) reports in {available}; "
                f"reporting_currency is {reporting_currency} — concept skipped"
            )
            missing.append(label)
            continue
        if not vals:
            missing.append(label)
            continue

        period_rows = fy_periods(vals)
        if not period_rows:
            period_rows = [
                (end, (val, form, "FY"))
                for end, (val, form) in instant_snapshots(vals)
            ]
        if not period_rows:
            missing.append(label)
            continue

        if primary_unit is None and unit not in ("shares", "pure"):
            primary_unit = unit
            print(f"CURRENCY: detected={unit}")

        for end, (val, form, fp) in period_rows[:5]:
            rows.append(f"{label} ({chosen}) | {end} | {val} | {unit}")

    # Derived ratio with same anchor-mismatch guard as extract_xbrl.py.
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
                f"ratio suppressed",
                file=sys.stderr,
            )

    for r in rows:
        print(r)

    for j in detect_share_jumps(rows):
        print(j, file=sys.stderr)

    if currency_mismatches:
        print(file=sys.stderr)
        print(
            f"CURRENCY_MIX_WARNING: {len(currency_mismatches)} concept(s) "
            f"do not report in reporting_currency={reporting_currency} "
            f"and were skipped to avoid silently mixing currencies:",
            file=sys.stderr,
        )
        for m in currency_mismatches:
            print(f"  {m}", file=sys.stderr)

    if missing:
        print(f"XBRL_MISSING (IFRS): {','.join(missing)}", file=sys.stderr)
        print("Available ifrs-full concepts (first 30):", file=sys.stderr)
        for c in list(facts.keys())[:30]:
            print(f"  {c}", file=sys.stderr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("--reporting-currency", default=None)
    args = parser.parse_args()
    main(args.path, args.reporting_currency)
