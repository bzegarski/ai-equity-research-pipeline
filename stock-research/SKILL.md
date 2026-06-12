---
name: stock-research
description: "Deep qualitative research on a public company using SEC primary sources, two-model independent verification, and adversarial review. Produces a sourced investment memo with reliability score and forced Key Insight (or honest \"no edge identified\" admission). Multi-phase, dual-terminal (CC + Codex). Usage: /stock-research TICKER for Phase 0, then --step1b, then --step1e."
---

Read the args. Extract:
- `{TICKER}` = first word (e.g. AAPL, DECK, PANW). If missing, ask: "Which ticker?"
- `FLAG` = `--step1b`, `--step1e`, `--step3.5e`, `--reconcile-valuation`, `--step11e`, or none

Compute `{BASE}` (timestamped folder convention, D.M.YYYY):

- **No flag (Phase 0, fresh download):** Use today's date in `D.M.YYYY` format (no leading zeros — e.g., 9 May 2026 → `9.5.2026`, 15 December 2026 → `15.12.2026`). Set `{BASE}` = `~/Research/{TICKER}_{D.M.YYYY}`. If a folder with that exact name already exists from earlier today, reuse it. If only an older dated folder exists for this ticker, create the new one (you're starting a fresh run).
- **Continuation flags (`--step1b`, `--step1e`, `--step3.5e`, `--reconcile-valuation`, `--step11e`):** Resolve `{BASE}` by globbing `~/Research/{TICKER}_*/`. If multiple matches, pick the one with the most recent mtime (newest run). Fall back to the legacy untimestamped path `~/Research/{TICKER}/` only if no `{TICKER}_*` folder exists. If neither exists, abort with: `No prior run for {TICKER}. Run /stock-research {TICKER} (no flag) first to start Phase 0.`

Resolve `{BASE}` ONCE at the start of dispatch and use that exact path for every substitution downstream.

## Pre-flight reference check (runs on EVERY flag)

Before doing any other work — including before creating `{BASE}/raw` or making any network calls — verify that all 6 shared methodology references exist:

```
~/.claude/skills/stock-research/references/discount_rate_logic.md
~/.claude/skills/stock-research/references/owner_earnings.md
~/.claude/skills/stock-research/references/moat_durability_tiers.md
~/.claude/skills/stock-research/references/valuation_methods.md
~/.claude/skills/stock-research/references/three_tier_decision.md
~/.claude/skills/stock-research/references/accounting_principles.md
```

If ANY are missing, abort immediately with this exact message and stop:

```
REFERENCES MISSING: methodology files not found. Reinstall the references/ directory from the repo before running.
```

This fails fast at dispatch — catches a broken references directory before Phase 0 burns network calls or any continuation flag opens files. The agent-level precondition block in `agents/valuation.md` and `agents/valuation_codex.md` is defense-in-depth; this orchestrator check is the first line.

Create `{BASE}/raw` and `{BASE}/steps` if they don't exist.

## Flag routing

- **No flag** → run **Phase 0 (download)** by following `phases/phase0_download.md`. Stop at the user-instruction message.
- **`--step1b`** → run **Step 1B + 1C** by following `phases/step1bc.md`. Stop at the user-instruction message.
- **`--step1e`** → run **Step 1E + Verification A + Phase 2 (Gate) + Phase 3 (5 parallel agents + Agent F)** by following `phases/step1e_pipeline.md`. Stop after Phase 3 user message instructing the user to run Codex's `--consistency` then return with `--step3.5e`.
- **`--step3.5e`** → continue from the saved state. Read `steps/step3.5_consistency_check.md`, apply revisions if any, run **Phase 4 (Moat Durability)**, **Phase 5A (CC Valuation, multi-method, three-tier)**. Stop after Phase 5A user message instructing the user to run Codex's `--valuation` then return with `--reconcile-valuation`.
- **`--reconcile-valuation`** → continue from the saved state. Read both `steps/step9_valuation_cc.md` and `steps/step9_valuation_codex.md`. Run **Phase 5C (Reconciliation)** producing `steps/step9_valuation_reconciled.md` and the alias copy `steps/step9_valuation.md`. Then run **Phase 6 (Counter-Attack)**. Stop after Phase 6 user message instructing optional Codex `--attack` then `--step11e`.
- **`--step11e`** → continue from the saved state. Optionally read `steps/step10_codex_attack.md` if it exists. Run **Phase 7 (Final Memo + Verification C + Verification D)**.

## Substitution rules

When dispatching any agent or phase file:

1. Read the file's content.
2. Replace every `{TICKER}` with the actual ticker.
3. Replace every `{BASE}` with the resolved timestamped path (e.g., `~/Research/MSFT_9.5.2026`) — NOT the literal `{TICKER}` substitution.
4. For agents: prepend `shared/mission_frame.md`, `shared/claim_labeling.md`, `shared/writing_style.md` (concatenated) to the agent's prompt.
5. Send the assembled prompt to the agent / Bash / inline execution.

`{TICKER}` and `{BASE}` are the only placeholder tokens. Anything else `{like_this}` is illustrative and stays in the prompt.

## Environment notes (this machine)

- **Python:** use `py` not `python3`. (User has `Bash(py *)` allowed in settings.)
- **EDGAR API:** ALL requests to `data.sec.gov` and `efts.sec.gov` must include the User-Agent header:
  ```
  curl -s -A "Research your.email@example.com" "URL" -o "OUTPUT_FILE"
  ```
  WebFetch alone gets 403.
- **OpenInsider unreliable** — use EDGAR Form 4 directly (`scripts/parse_form4.py`).
- **Working directory:** the orchestrator and phase files use absolute `{BASE}`-substituted paths. Each phase begins with `cd "{BASE}"` for safety, but absolute paths in scripts/curl mean the cd is precautionary.
- **Skill scripts:** all in `~/.claude/skills/stock-research/scripts/`. Reference with absolute path; they live with the skill, not with the research data.

## Bug log discipline

Every run creates `{BASE}/bugs_encountered.md` (Phase 0 initializes it empty). Every phase appends warnings as they occur. Logged classes:

- `curl` non-zero exit or empty file
- XBRL concept misses (list which)
- Section extraction fallbacks (strict failed → gap-based, or both failed)
- HTML-stripped (no .txt available)
- File >400k chars truncated
- `SHARES_JUMP` detected (possible stock split)
- Transcript source quality (verbatim/structured_summary/unavailable)
- Material 8-K events flagged
- Any Python script exception (with error message)
- Any step with degraded or partial output
- Cross-check zero-discrepancies (likely anchoring)
- Verification A/B/C/D corrections applied

Format: `[Phase X] WARNING: ...` or `[Phase X] CORRECTED: ... -> ...` or `[Phase X] OK`.

At end of pipeline, append summary: `Total: N warnings, M corrections`.

## Files in this skill

```
SKILL.md                  # this file: orchestrator
shared/                   # blocks prepended to every agent prompt
  mission_frame.md        # epistemic ground rules + prompt-injection note
  claim_labeling.md       # [FACT|source|confidence] format (step files only)
  writing_style.md        # Strunk/Orwell/Munger; prohibited phrases
phases/                   # per-flag instructions
  phase0_download.md      # no flag
  step1bc.md              # --step1b
  step1e_pipeline.md      # --step1e, --step3.5e, --step11e (continuations)
agents/                   # subagent prompt templates
  business_model.md       # Agent A
  industry.md             # Agent B (DEEP research)
  moat_current.md         # Agent C
  accounting.md           # Agent D
  management.md           # Agent E
  customer_perspective.md # Agent F (DEEP research, criteria-based sourcing)
  moat_durability.md      # Phase 4 (DEEP research, attack test)
  valuation.md            # Phase 5 (DCF + reverse DCF; Verification B run by orchestrator)
  counter_attack.md       # Phase 6 (DEEP research on attacks 7-8)
  final_memo.md           # Phase 7 (footnote format, Verification C + D)
scripts/                  # standalone Python (testable in isolation)
  resolve_cik.py          # company_tickers.json fallback for tricky tickers
  extract_xbrl.py         # SHARES_JUMP detection; auto-delegates to IFRS extractor
  extract_ifrs_xbrl.py    # ifrs-full taxonomy (NVO, ONON-style FPI filers)
  strip_10k.py            # block-tags-to-newlines (BUG-2)
  clean_canonical.py      # track-aware TOC/cover trim (10k / 20f / 6k)
  extract_sections.py     # strict + gap-based + sequential rescue; --chunks-dir; --track fpi
  parse_form4.py          # unpadded CIK (BUG-1)
  extract_8k.py           # NEW (D1)
  detect_transcript_format.py  # URL-host prior + structure score (n=6)
```

## Codex side

The Codex skill (`~/.codex/skills/stock-research-codex/SKILL.md`) is updated separately by pasting the Codex prompt from the plan file into a Codex session. CC cannot edit Codex's skill.

Codex flags this skill expects to coordinate with (note: Codex activation prefix is `$`, not `/`):
- `$stock-research-codex {TICKER} --audit` — Phase 0 audit (between CC's Phase 0 and Codex's Step 1A)
- `$stock-research-codex {TICKER}` — Step 1A all-in-one mode (independent summarization of all six core documents)
- `$stock-research-codex {TICKER} --step1a-10k` then `--step1a-10q`, `--step1a-proxy`, `--step1a-insider`, `--step1a-transcripts`, `--step1a-customer`, and `--step1a-status` — resumable Step 1A path for large/context-risk issuers
- `$stock-research-codex {TICKER} --step1d` — cross-check CC's summaries
- `$stock-research-codex {TICKER} --consistency` — cross-step thesis check after CC's Phase 3
- `$stock-research-codex {TICKER} --valuation` — independent multi-method valuation (between CC's Phase 5A and CC's `--reconcile-valuation`)
- `$stock-research-codex {TICKER} --attack` — optional adversarial counter-attack

If the Codex side hasn't been updated yet, the audit / consistency / valuation / attack flags simply won't exist on the Codex side; the rest of the pipeline still runs (CC produces all step files; Codex produces only what its existing flags know about). The CC side handles "Codex file doesn't exist":
- For `step9_valuation_codex.md`: if missing, `--reconcile-valuation` falls back to copying `step9_valuation_cc.md` to `step9_valuation_reconciled.md` (and the alias `step9_valuation.md`) with a logged warning that no Codex independent valuation was available.
- For `step10_codex_attack.md`: final memo reads only `step10_counter_attack.md` if missing.

## Shared references for valuation methodology

Both CC and Codex valuation phases read from `references/`:
- `discount_rate_logic.md` — long-bond + ERP rules; Buffett 10% floor; multi-guardrail terminal growth
- `owner_earnings.md` — 1986 letter formula; equity vs EV rule; maint vs growth capex separation
- `moat_durability_tiers.md` — research (b) empirical durability table; Stage-1 length + certainty premium
- `valuation_methods.md` — six methods + business-type → method matrix
- `three_tier_decision.md` — fair value / hurdle / buy logic with ranges; MoS table

This is the single source of truth. Codex reads from CC's directory (one source of truth, lower drift); CC owns updates. Both `agents/valuation.md` (CC) and Codex's `agents/valuation_codex.md` open with a precondition block that aborts loudly if any reference file is missing.
