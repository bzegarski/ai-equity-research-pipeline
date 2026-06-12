#!/usr/bin/env python3
"""
append_outcome.py — auto-append a row to Research/outcomes_log.md after Phase 7.

Usage:
    py append_outcome.py --base ~/Research/MSFT_9.5.2026

Behavior (per plan, Codex corrections 5 + 7):
- Reads step9_valuation_reconciled.md (or step9_valuation.md alias) and
  step11_final_memo.md from {base}/steps/.
- Extracts schema fields. For each field, tries lightweight patterns; if a
  field can't be parsed cleanly, writes [PARSE-FAIL] for that field rather
  than dropping the row or crashing.
- Stores raw range strings (e.g. "[$720, $820]" or "midpoint $770") so the
  user reviewing the row sees what was actually in the file.
- Duplicate prevention: if the outcomes log already contains a row whose
  Notes column references this {base} folder name, no-op + warning.
- Failure mode: append failure does NOT invalidate the memo. Exits non-zero
  and lets the parent (Phase 7 wiring in final_memo.md) write a warning to
  bugs_encountered.md while keeping the memo as the user-facing product.
"""

from __future__ import annotations
import argparse
import datetime as dt
import os
import re
import sys
from pathlib import Path

OUTCOMES_LOG = "~/Research/outcomes_log.md"

SCHEMA_COLUMNS = [
    "Date", "Ticker", "Verdict", "Price at run", "Long bond", "Class",
    "Stage-1 yrs", "MoS used", "Fair low", "Fair high", "Hurdle low",
    "Hurdle high", "Buy trigger", "Buffett-pure (diagnostic)",
    "Reverse DCF @ fair (implied g%)", "Reverse DCF @ hurdle (implied g%)",
    "TSR %", "EPV/share", "Decision-flipping divergence?",
    "Accounting verdict", "Opt-out flag",
    "Reliability %", "Key insight", "Notes",
]

PARSE_FAIL = "[PARSE-FAIL]"
NOT_PRESENT = "—"


def _section_body(text: str, label: str) -> str:
    """Return the body between `=== LABEL ===` and the next `===` or EOF.

    Returns empty string if label not present. Strips outer whitespace.
    """
    pattern = rf"=== {re.escape(label)} ===\s*\n(.*?)(?=\n#{{0,3}}\s*=== |\Z)"
    m = re.search(pattern, text, flags=re.DOTALL)
    return m.group(1).strip() if m else ""


def _first_dollar_amount(s: str) -> str | None:
    """Return the first $-prefixed number in s as a clean string, or None."""
    m = re.search(r"\$\s*([0-9,]+(?:\.[0-9]+)?)", s)
    return m.group(1).replace(",", "") if m else None


def _range_low_high(s: str) -> tuple[str | None, str | None]:
    """Try to extract (low, high) from a range string. None if not parseable.

    Handles: "$720-$820", "[$720, $820]", "$720 to $820", "720-820",
    "Range: [720, 820]", etc. Returns (None, None) if no two-number pattern.
    """
    nums = re.findall(r"\$?\s*([0-9,]+(?:\.[0-9]+)?)", s)
    nums = [n.replace(",", "") for n in nums]
    if len(nums) >= 2:
        return nums[0], nums[1]
    if len(nums) == 1:
        return nums[0], nums[0]
    return None, None


def _first_percent(s: str) -> str | None:
    """Return the first percentage value in s (e.g. '4.5%' or '8.1') as a clean str."""
    m = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*%", s)
    return m.group(1) if m else None


def _extract_classification(body: str) -> str:
    """Pull primary class + modifiers as a single string."""
    if not body:
        return PARSE_FAIL
    primary_m = re.search(r"Primary[:\s]+([A-Z\-/ ]+)", body)
    mods_m = re.search(r"Modifiers?[:\s]+(.+)", body)
    primary = primary_m.group(1).strip() if primary_m else ""
    mods = mods_m.group(1).strip().split("\n")[0].lstrip("+ ").strip() if mods_m else ""
    if primary:
        return f"{primary}{(' + ' + mods) if mods else ''}".strip(" +")
    # Fallback: first non-empty line
    first = next((ln for ln in body.splitlines() if ln.strip()), "")
    return first[:80] if first else PARSE_FAIL


def _extract_verdict(memo_text: str) -> str:
    """Pull verdict from Section 1 of the final memo."""
    if not memo_text:
        return PARSE_FAIL
    # Try to find ### Section 1 — DECISION block
    m = re.search(r"Section 1.*?DECISION.*?\n(.*?)(?=\n###|\n## |\Z)", memo_text, flags=re.DOTALL | re.IGNORECASE)
    if not m:
        return PARSE_FAIL
    block = m.group(1)
    for kw in ("BUY", "WATCHLIST", "PASS"):
        if kw in block.upper():
            # Capture short line containing the verdict
            for line in block.splitlines():
                if kw in line.upper():
                    return line.strip("- *").strip()[:120]
    return PARSE_FAIL


def _extract_reliability(memo_text: str, base: Path) -> str:
    """Pull reliability % from memo or verification_c.md."""
    # Try memo first
    m = re.search(r"[Rr]eliability[:\s]+([0-9]+(?:\.[0-9]+)?)\s*%", memo_text)
    if m:
        return m.group(1)
    # Try verification_c.md
    vc = base / "steps" / "verification_c.md"
    if vc.exists():
        vc_text = vc.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"[Oo]verall reliability[:\s]+([0-9]+(?:\.[0-9]+)?)\s*%", vc_text)
        if m:
            return m.group(1)
    return PARSE_FAIL


def _extract_key_insight(memo_text: str) -> str:
    """First 120 chars of Section 3 body, or 'no edge' if admission text present."""
    if not memo_text:
        return PARSE_FAIL
    m = re.search(r"Section 3.*?KEY INSIGHT.*?\n(.*?)(?=\n###|\n## |\Z)", memo_text, flags=re.DOTALL | re.IGNORECASE)
    if not m:
        return PARSE_FAIL
    body = m.group(1).strip()
    if "no edge identified" in body.lower():
        return "(No edge identified)"
    # First non-trivial line
    for line in body.splitlines():
        line = line.strip("> *").strip()
        if line and not line.startswith("---"):
            return line[:120].replace("|", "/")
    return PARSE_FAIL


def _md_escape(s: str) -> str:
    """Escape pipes in cell content so the markdown table doesn't break."""
    return s.replace("|", "/").replace("\n", " ").strip()


def extract_row(base: Path) -> dict[str, str]:
    """Build the dict of column → value for this run."""
    steps = base / "steps"
    val_path = steps / "step9_valuation_reconciled.md"
    if not val_path.exists():
        # Fallback to alias
        val_path = steps / "step9_valuation.md"
    memo_path = steps / "step11_final_memo.md"

    val_text = val_path.read_text(encoding="utf-8", errors="replace") if val_path.exists() else ""
    memo_text = memo_path.read_text(encoding="utf-8", errors="replace") if memo_path.exists() else ""
    acct_path = steps / "step7_accounting.md"
    acct_text = acct_path.read_text(encoding="utf-8", errors="replace") if acct_path.exists() else ""

    # Ticker from base folder name (strip date suffix if present)
    folder = base.name
    ticker_m = re.match(r"([A-Z]{1,6})(?:_\d|$)", folder)
    ticker = ticker_m.group(1) if ticker_m else folder

    # Sections
    cls_body = _section_body(val_text, "BUSINESS CLASSIFICATION")
    rates_body = _section_body(val_text, "DISCOUNT RATES")
    fair_body = _section_body(val_text, "FAIR VALUE RANGE")
    hurdle_body = _section_body(val_text, "HURDLE VALUE RANGE")
    buy_body = _section_body(val_text, "BUY TRIGGER")
    rdcf_body = _section_body(val_text, "REVERSE DCF (implied growth)")
    tsr_body = _section_body(val_text, "TSR DECOMPOSITION")
    epv_body = _section_body(val_text, "EPV FLOOR")
    method_body = _section_body(val_text, "METHOD WEIGHTS AND RECONCILIATION NOTES")

    # Discount rates: pull long-bond, fair rate, hurdle rate, buffett-pure
    long_bond = NOT_PRESENT
    buffett_pure = NOT_PRESENT
    if rates_body:
        lb_m = re.search(r"long[_\- ]?bond[^0-9]*([0-9]+(?:\.[0-9]+)?)\s*%", rates_body, flags=re.IGNORECASE)
        if lb_m:
            long_bond = lb_m.group(1)
        bp_m = re.search(r"Buffett[\- ]pure[^0-9]*([0-9]+(?:\.[0-9]+)?)\s*%", rates_body, flags=re.IGNORECASE)
        if bp_m:
            buffett_pure = bp_m.group(1)

    # Stage-1 length: try to find in method weights or stage-1 growth
    stage1 = PARSE_FAIL
    s1_body = _section_body(val_text, "STAGE-1 GROWTH (TRIANGULATED)")
    for src in (method_body, s1_body):
        m = re.search(r"Stage[\- ]1.*?([0-9]+)\s*(?:years?|y)\b", src, flags=re.IGNORECASE)
        if m:
            stage1 = m.group(1)
            break

    # MoS from buy trigger body
    mos = PARSE_FAIL
    if buy_body:
        m = re.search(r"MoS[^0-9]*([0-9]+(?:\.[0-9]+)?)\s*%", buy_body, flags=re.IGNORECASE)
        if not m:
            m = re.search(r"required_MoS[^0-9]*([0-9]+(?:\.[0-9]+)?)", buy_body)
        if m:
            mos = m.group(1)

    # Fair / hurdle / buy ranges
    fair_low, fair_high = _range_low_high(fair_body) if fair_body else (None, None)
    hurd_low, hurd_high = _range_low_high(hurdle_body) if hurdle_body else (None, None)
    buy_trig = _first_dollar_amount(buy_body) if buy_body else None

    # Reverse DCF — try to find two implied growth percentages (fair + hurdle)
    rdcf_fair = rdcf_hurdle = PARSE_FAIL
    if rdcf_body:
        # Look for "fair" line then percentage; "hurdle" line then percentage
        fm = re.search(r"fair[^%]*?([0-9]+(?:\.[0-9]+)?)\s*%", rdcf_body, flags=re.IGNORECASE)
        hm = re.search(r"hurdle[^%]*?([0-9]+(?:\.[0-9]+)?)\s*%", rdcf_body, flags=re.IGNORECASE)
        if fm:
            rdcf_fair = fm.group(1)
        if hm:
            rdcf_hurdle = hm.group(1)

    # TSR
    tsr = PARSE_FAIL
    if tsr_body:
        m = re.search(r"=\s*([0-9]+(?:\.[0-9]+)?)\s*%", tsr_body)
        if not m:
            m = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*%", tsr_body)
        if m:
            tsr = m.group(1)

    # EPV
    epv = _first_dollar_amount(epv_body) if epv_body else PARSE_FAIL

    # Decision-flipping divergence
    flip = "no"
    if "DECISION-FLIPPING DIVERGENCE" in val_text:
        flip_body = _section_body(val_text, "DECISION-FLIPPING DIVERGENCE")
        if flip_body and flip_body.strip().lower() not in ("none", "n/a", ""):
            flip = "yes"

    # Memo-derived
    verdict = _extract_verdict(memo_text)
    reliability = _extract_reliability(memo_text, base)
    key_insight = _extract_key_insight(memo_text)

    # Accounting agent verdict + opt-out flag (v1.1 schema additions)
    acct_verdict = PARSE_FAIL
    opt_out_flag = PARSE_FAIL
    if acct_text:
        # Verdict line follows "=== ACCOUNTING QUALITY VERDICT ===" with bolded label
        av_body = _section_body(acct_text, "ACCOUNTING QUALITY VERDICT")
        if av_body:
            m = re.search(
                r"\*?\*?Verdict\*?\*?\s*:?\s*"
                r"(Clean|Acceptable with caveats|Acceptable|Concerning|Conservative)",
                av_body,
                flags=re.IGNORECASE,
            )
            if m:
                acct_verdict = m.group(1).strip()
        # Opt-out flag follows "=== OPT-OUT FLAG ==="
        of_body = _section_body(acct_text, "OPT-OUT FLAG")
        if of_body:
            m = re.search(
                r"\*?\*?Flag\*?\*?\s*:?\s*"
                r"(RECOMMEND TOO HARD|RECOMMEND PARTIAL|WATCH|NONE)",
                of_body,
                flags=re.IGNORECASE,
            )
            if m:
                opt_out_flag = m.group(1).strip().upper()

    # Price at run — try memo data freshness block or step9
    price = PARSE_FAIL
    price_m = re.search(r"price[^0-9$]*\$\s*([0-9,]+(?:\.[0-9]+)?)", memo_text, flags=re.IGNORECASE)
    if price_m:
        price = price_m.group(1).replace(",", "")

    today = dt.date.today().isoformat()

    return {
        "Date": today,
        "Ticker": ticker,
        "Verdict": verdict,
        "Price at run": price,
        "Long bond": long_bond,
        "Class": _extract_classification(cls_body),
        "Stage-1 yrs": stage1,
        "MoS used": mos,
        "Fair low": fair_low if fair_low else PARSE_FAIL,
        "Fair high": fair_high if fair_high else PARSE_FAIL,
        "Hurdle low": hurd_low if hurd_low else PARSE_FAIL,
        "Hurdle high": hurd_high if hurd_high else PARSE_FAIL,
        "Buy trigger": buy_trig if buy_trig else PARSE_FAIL,
        "Buffett-pure (diagnostic)": buffett_pure,
        "Reverse DCF @ fair (implied g%)": rdcf_fair,
        "Reverse DCF @ hurdle (implied g%)": rdcf_hurdle,
        "TSR %": tsr,
        "EPV/share": epv,
        "Decision-flipping divergence?": flip,
        "Accounting verdict": acct_verdict,
        "Opt-out flag": opt_out_flag,
        "Reliability %": reliability,
        "Key insight": key_insight,
        "Notes": f"run={folder}",
    }


def already_logged(folder_name: str) -> bool:
    """Duplicate-prevention: check whether outcomes_log already references this run folder."""
    if not os.path.exists(OUTCOMES_LOG):
        return False
    with open(OUTCOMES_LOG, encoding="utf-8") as f:
        return f"run={folder_name}" in f.read()


def format_row(row: dict[str, str]) -> str:
    cells = [_md_escape(str(row.get(c, PARSE_FAIL))) for c in SCHEMA_COLUMNS]
    return "| " + " | ".join(cells) + " |\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True, help="Path to {BASE} folder for the run")
    ap.add_argument("--dry-run", action="store_true", help="Print row without appending")
    args = ap.parse_args()

    base = Path(args.base).resolve()
    if not base.exists():
        print(f"ERROR: base folder does not exist: {base}", file=sys.stderr)
        return 2

    val_present = (base / "steps" / "step9_valuation_reconciled.md").exists() or \
                  (base / "steps" / "step9_valuation.md").exists()
    memo_present = (base / "steps" / "step11_final_memo.md").exists()
    if not val_present and not memo_present:
        print(f"ERROR: neither valuation nor final memo found under {base}/steps/", file=sys.stderr)
        return 3

    # Duplicate prevention
    folder_name = base.name
    if already_logged(folder_name):
        print(f"WARNING: outcomes log already contains a row for run={folder_name}; no-op.", file=sys.stderr)
        return 0  # not a failure, just a no-op

    row = extract_row(base)
    line = format_row(row)

    if args.dry_run:
        print("--- DRY RUN ---")
        print(line.rstrip())
        return 0

    if not os.path.exists(OUTCOMES_LOG):
        print(f"ERROR: outcomes log not found at {OUTCOMES_LOG}", file=sys.stderr)
        return 4

    with open(OUTCOMES_LOG, "a", encoding="utf-8") as f:
        f.write(line)

    # Report summary of any PARSE-FAILs
    failed = [c for c in SCHEMA_COLUMNS if str(row.get(c, "")) == PARSE_FAIL]
    if failed:
        print(f"OK: appended row for run={folder_name} with {len(failed)} [PARSE-FAIL] field(s): {', '.join(failed)}", file=sys.stderr)
    else:
        print(f"OK: appended row for run={folder_name} (all fields parsed)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
