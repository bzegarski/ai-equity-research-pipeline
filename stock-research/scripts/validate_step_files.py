#!/usr/bin/env python3
"""
validate_step_files.py — lightweight section-label and parseability validator.

Usage:
    py validate_step_files.py --base ~/Research/MSFT_9.5.2026

Strict scope per plan (Codex correction 6):
- Validate required section labels for files that ARE PRESENT.
- For step9_valuation*.md: confirm fair / hurdle / buy ranges contain at least
  one numeric token so append_outcome.py can extract them.
- SKIP optional files that were not part of the run (e.g., step10_codex_attack
  if --attack wasn't run).
- NOT a full schema validator. Section presence + value parseability only.

Exit codes:
  0 = all present files pass
  1 = one or more failures (printed to stderr)
  2 = script invocation error (e.g., bad --base path)
"""

from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path

# (filename, required_labels, optional_labels) — only checked if file exists
REQUIRED_LABELS_BY_FILE = {
    # Round 3 valuation outputs (14 labels)
    "step9_valuation_cc.md": [
        "BUSINESS CLASSIFICATION",
        "OWNER EARNINGS DERIVATION",
        "MAINTENANCE CAPEX",
        "STAGE-1 GROWTH (TRIANGULATED)",
        "DISCOUNT RATES",
        "METHOD WEIGHTS AND RECONCILIATION NOTES",
        "FAIR VALUE RANGE",
        "HURDLE VALUE RANGE",
        "BUY TRIGGER",
        "REVERSE DCF (implied growth)",
        "TSR DECOMPOSITION",
        "EPV FLOOR",
        "MOST FRAGILE ASSUMPTIONS",
        "VERDICT",
    ],
    "step9_valuation_codex.md": [
        "BUSINESS CLASSIFICATION",
        "OWNER EARNINGS DERIVATION",
        "MAINTENANCE CAPEX",
        "STAGE-1 GROWTH (TRIANGULATED)",
        "DISCOUNT RATES",
        "METHOD WEIGHTS AND RECONCILIATION NOTES",
        "FAIR VALUE RANGE",
        "HURDLE VALUE RANGE",
        "BUY TRIGGER",
        "REVERSE DCF (implied growth)",
        "TSR DECOMPOSITION",
        "EPV FLOOR",
        "MOST FRAGILE ASSUMPTIONS",
        "VERDICT",
    ],
    "step9_valuation_reconciled.md": [
        "BUSINESS CLASSIFICATION",
        "FAIR VALUE RANGE",
        "HURDLE VALUE RANGE",
        "BUY TRIGGER",
        "REVERSE DCF (implied growth)",
        "VERDICT",
        # RECONCILIATION SUMMARY also expected but the alias copy
        # step9_valuation.md may not always have it — keep this list short.
    ],
    "step4_industry.md": [
        "INDUSTRY MAP",
        "COMPETITIVE LANDSCAPE",
    ],
    "step7_accounting.md": [
        "ACCOUNTING QUALITY VERDICT",
        "RED FLAGS",
    ],
    "step8_management.md": [
        "FINAL MANAGEMENT VERDICT",
    ],
}

# Files that MUST exist in a completed Phase 7 run. Their absence is an error,
# not a skip.
REQUIRED_FILES = [
    # At least one of step9_valuation_reconciled.md or step9_valuation.md
    # must exist (the alias). Special-cased in main().
    "step11_final_memo.md",
]


def check_section_labels(path: Path, required: list[str]) -> list[str]:
    """Return list of missing labels (empty list = all present)."""
    text = path.read_text(encoding="utf-8", errors="replace")
    missing = []
    for label in required:
        # Match `=== LABEL ===` with optional `#`/`##`/`###` markdown header prefix
        # (agents sometimes produce `## === LABEL ===` instead of bare label)
        if not re.search(rf"^\s*#{{0,3}}\s*=== {re.escape(label)} ===\s*$", text, flags=re.MULTILINE):
            missing.append(label)
    return missing


def check_valuation_parseability(path: Path) -> list[str]:
    """For step9_valuation*.md: confirm fair/hurdle/buy ranges contain numerics."""
    text = path.read_text(encoding="utf-8", errors="replace")
    issues = []
    for label in ("FAIR VALUE RANGE", "HURDLE VALUE RANGE", "BUY TRIGGER"):
        m = re.search(
            rf"=== {re.escape(label)} ===\s*\n(.*?)(?=\n#{{0,3}}\s*=== |\Z)",
            text,
            flags=re.DOTALL,
        )
        if not m:
            continue  # missing-label case is reported by check_section_labels
        body = m.group(1)
        if not re.search(r"\$?\s*[0-9]+", body):
            issues.append(f"{label}: no numeric value found in body")
    return issues


def check_memo_essentials(path: Path) -> list[str]:
    """Verify step11_final_memo.md has the essentials append_outcome.py needs."""
    text = path.read_text(encoding="utf-8", errors="replace")
    issues = []
    if not re.search(r"Section 1.*?DECISION", text, flags=re.IGNORECASE):
        issues.append("Section 1 (DECISION) header not found")
    if not re.search(r"\b(BUY|WATCHLIST|PASS)\b", text):
        issues.append("verdict keyword (BUY/WATCHLIST/PASS) not found in memo body")
    if not re.search(r"Section 3.*?KEY INSIGHT", text, flags=re.IGNORECASE):
        issues.append("Section 3 (KEY INSIGHT) header not found")
    return issues


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True, help="Path to {BASE} folder for the run")
    args = ap.parse_args()

    base = Path(args.base).resolve()
    if not base.exists():
        print(f"ERROR: base folder does not exist: {base}", file=sys.stderr)
        return 2
    steps = base / "steps"
    if not steps.exists():
        print(f"ERROR: {steps} does not exist", file=sys.stderr)
        return 2

    failures: list[str] = []

    # Required-files check: memo must exist; valuation reconciled OR alias must exist
    if not (steps / "step11_final_memo.md").exists():
        failures.append("REQUIRED FILE MISSING: steps/step11_final_memo.md")
    val_reconciled = steps / "step9_valuation_reconciled.md"
    val_alias = steps / "step9_valuation.md"
    if not val_reconciled.exists() and not val_alias.exists():
        failures.append("REQUIRED FILE MISSING: steps/step9_valuation_reconciled.md (or alias step9_valuation.md)")

    # Section labels check (only files that exist)
    for fname, required in REQUIRED_LABELS_BY_FILE.items():
        path = steps / fname
        if not path.exists():
            continue  # skip absent files per scope constraint
        missing = check_section_labels(path, required)
        if missing:
            failures.append(f"{fname}: missing section labels: {', '.join(missing)}")

    # Valuation parseability (for whichever valuation file exists)
    for vname in ("step9_valuation_reconciled.md", "step9_valuation_codex.md", "step9_valuation_cc.md", "step9_valuation.md"):
        vpath = steps / vname
        if not vpath.exists():
            continue
        issues = check_valuation_parseability(vpath)
        for i in issues:
            failures.append(f"{vname}: {i}")

    # Memo essentials
    memo = steps / "step11_final_memo.md"
    if memo.exists():
        for i in check_memo_essentials(memo):
            failures.append(f"step11_final_memo.md: {i}")

    if failures:
        print("VALIDATION FAILED:", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    print("OK: validation passed (all present files have required labels and parseable values)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
