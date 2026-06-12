# Step 1E + Full Pipeline (Phases 2-7)

Run when: `--step1e` flag.

Substitute `{TICKER}` and `{BASE}` throughout.

First: append to `{BASE}/bugs_encountered.md`:
```
## Step 1E + Analysis
```

## Step 1E — Integrate canonical summaries

Read all of:
- For 10k, 10q, proxy, insider, transcripts, customer_perspective:
  `*_cc.md` + `*_codex.md` + `*_cc_xcheck.md` + `*_codex_xcheck.md` + raw text
- For competitors (CC-only by design): `competitors_cc.md` + raw text

For each document set, write a canonical summary (`raw/10k.md`, `raw/10q.md`, etc.):

1. Incorporate all claims where both models agreed
2. Resolve discrepancies: re-check raw source; use the cross-check verdict that cited the source most precisely; if both verdicts conflict, go back to raw text and decide yourself
3. Unresolved disputes: include the claim with `[HUMAN-VERIFY | Low]` and note both readings in a footnote
4. End with a `## Reconciliation Notes` section listing unresolved disputes, [HUMAN-VERIFY] items, sections where both models disagreed

**For `competitors.md` specifically:** there is no Codex summary or cross-check (separate n=6 narrowing — competitor dual-pass produced redundant broad summaries with no high-yield catches). The reconciliation note must state: `"Built from competitors_cc.md alone (single-source by design). Verification A is the sole reliability layer for competitor data."`

**INTEGRATION WEIGHTING (INT-1):**
- Count items in "CC FOUND, CODEX MISSED" and "CODEX FOUND, CC MISSED" per cross-check.
- If CC caught >3× what Codex caught for a document: start canonical from CC's version. Add Codex-only items explicitly. Use Codex XBRL numbers as verification anchors, not new content.
- If catch ratio is roughly even: integrate as equal inputs.
- Always note the ratio in `## Reconciliation Notes`.

Apply `shared/claim_labeling.md` and `shared/writing_style.md` throughout.

## Verification A — Fact-check canonical summaries

Before any analysis begins, verify canonical summaries against source:

1. Every number in `10k.md` and `10q.md`: check against `xbrl_summary.txt`. Flag mismatches.
2. Brand ownership status: for every brand mentioned, quote Item 1 verbatim. If Item 1 does not explicitly state divested/sold/wind-down, do not write that.
3. Manufacturing geography: keep qualitative language ("predominantly Vietnam"), do not convert to percentages.
4. Executive tenure: WebSearch verify the year each key executive joined.
5. Data vintage: confirm every figure is from the most recent period available. If 10-Q has more recent than 10-K, use 10-Q.
6. Any [HUMAN-VERIFY] items from reconciliation: one more WebSearch attempt.

Write `{BASE}/raw/verification_a.md`:
```
| Claim in canonical summary | Source-verified value | Source | Confidence | Correction needed? |
```

Update canonical files to fix confirmed errors. Add [HUMAN-VERIFY] to any claim that couldn't be independently confirmed.

## Phase 2 — Gate check

Spawn an agent. Substitute `{TICKER}` throughout the prompt.

Prompt (prepend `shared/mission_frame.md`, `shared/claim_labeling.md`, `shared/writing_style.md`):

```
Read: {BASE}/raw/10k.md, raw/10q.md, raw/proxy.md, raw/recent_8k.txt

Run the initial gate for {TICKER}. Decide: does this idea deserve deep analysis?

1. UNDERSTANDABILITY: Can the business model be described simply? If not, flag.
2. ECONOMICS SIGNAL: Attractive returns on capital, deep value, or other clear economic interest?
3. RED FLAGS: Walk-away signals? Excessive leverage, auditor change, material weakness, massive goodwill, SEC investigation?
4. RECENT MATERIAL EVENTS: Anything in recent_8k.txt that would change the gate? Executive departures, guidance cuts, restatements?
5. TOO-HARD PILE: Complex financials, opaque revenue recognition, unpredictable value drivers?
6. TOP 3 REASONS TO REJECT NOW.
7. KEY OPEN QUESTIONS that justify deeper work.

OUTPUT FORMAT — label exactly:
=== GATE VERDICT ===
Reject / Watch / Advance
5-bullet rationale

=== KEY OPEN QUESTIONS ===
[numbered list]

Save output to {BASE}/steps/step2_gate.md.
```

If verdict is REJECT: write a one-paragraph summary to `{BASE}/{TICKER}_research_memo.md` stating rejection reasons. Tell the user: "Gate verdict: REJECT. Rationale in steps/step2_gate.md." Stop.

## Agent watchdog (applies to every Phase 3+ agent dispatch)

Every Phase 3, Phase 4, Phase 5, Phase 6, and Phase 7 agent dispatch must wrap
the agent in a watchdog with two thresholds. Retry is triggered by EITHER:

- **Soft timeout.** Phase 3 / 4 / 6 agents: 8 minutes warning. Phase 5 valuation
  agent: 12 minutes warning. Log a `[Phase X] WARNING: agent <name> exceeded
  soft timeout (Nm)` entry to `bugs_encountered.md` and continue waiting.
- **Hard timeout.** All Phase 3+ agents: 25 minutes. Kill the agent. Retry once
  with a tighter-scope prompt (drop optional sections; keep core deliverables).
- **Missing or zero-byte output.** After every agent completes (or is killed),
  verify the expected step file exists AND is non-trivial (>500 bytes). If not,
  retry once with the same scope (transient failures are common).

Each retry MUST append a numbered entry to `bugs_encountered.md`:
`[Phase X] RETRY-N: agent <name> — trigger=<hard timeout 25m | missing output |
zero-byte output> — retry status=<succeeded | failed>`. If the retry also fails
on either condition, exit the phase with `[Phase X] FATAL: agent <name>
stalled / missing output after retry`. Do not wait indefinitely.

Empirical motivation (NVO): Phase 4 first attempt completed with 31 tool uses,
0 tokens, 35m41s, no file written; orchestrator caught the missing file and
retried successfully. Phase 5 valuation: 13 tool uses, 6h 37m wall clock — no
watchdog caught it before. The watchdog formalizes both detections.

## Phase 3 — Parallel analysis (5 agents launched concurrently)

Launch all five agents simultaneously using the Agent tool. Do not wait for one to finish before launching the next. Each agent's prompt is the contents of its agent file with `{TICKER}` and `{BASE}` substituted, and `shared/mission_frame.md` + `shared/claim_labeling.md` + `shared/writing_style.md` prepended.

Apply the agent watchdog above to all five (and to Agent F).

- **Agent A (Business Model)** — `agents/business_model.md`
- **Agent B (Industry, deep research)** — `agents/industry.md`
- **Agent C (Current Moat)** — `agents/moat_current.md`
- **Agent D (Accounting)** — `agents/accounting.md`
- **Agent E (Management)** — `agents/management.md`

After all 5 complete, launch:
- **Agent F (Customer Perspective, deep research)** — `agents/customer_perspective.md` — runs separately because it needs Agent A's output

## Phase 3.4 — Write `cc_catches_against_codex.md` (inbox for Codex)

After Agent F completes and before the user is sent to Codex `--consistency`, write `{BASE}/raw/cc_catches_against_codex.md`. This is the inbox Codex's `--consistency` and `--attack` phases read to learn (a) which Codex catches CC accepted vs. rejected and (b) where CC caught errors in Codex's earlier output. Without this file, Codex never sees catches that flow CC → Codex.

**Section 1 — Codex catches and CC's adoption status.** Walk every `raw/*_codex_xcheck.md` "YOU FOUND, CC MISSED" entry and every Step 1D ADOPTION TARGET row. For each, decide adoption status by comparing the canonical file (`raw/10q.md`, `raw/proxy.md`, etc.) to what Codex flagged. Status values:
- `Accepted` — CC integrated the catch into the canonical file. Cite the file path.
- `Rejected` — CC checked source and disagrees. State the reason and the source quote.
- `Already-fixed` — the issue was resolved before this audit (rare).
- `Partial` — Codex's catch was partly adopted. Describe what was kept and what wasn't.

**Section 2 — CC catches against Codex's output.** Anywhere CC found an error in `raw/*_codex.md` or downstream Codex work during Phase 3 (Agent F often finds these in customer-perspective; Verification A occasionally catches XBRL or filing misreads). For each entry:
- What Codex wrote (with file:line if locatable)
- What CC verified is correct (with primary source)
- Which canonical file CC corrected
- Phase where CC found it (e.g. "Phase 3 / Agent F", "Verification A")

**Section 3 — Pattern notes (optional, only if a clear pattern emerges).** Two-to-four sentences on recurring Codex blind spots, e.g. "Codex over-relies on aggregator counts in customer-perspective; primary-source rule should reject those numbers from canonical use." This section feeds Codex's `--attack` blind-spot-adjustment paragraph.

File format:

```
# cc_catches_against_codex.md — {TICKER} — written {YYYY-MM-DD HH:MM}
# Refreshed before each Codex handoff.

## Section 1 — Codex catches and CC's adoption status

| Catch | Codex source (file:line if known) | Status | Canonical file | Notes |
|---|---|---|---|---|
| ... | ... | Accepted | raw/proxy.md | ... |

## Section 2 — CC catches against Codex's output

| Codex claim | CC's verified correction | Primary source | Canonical fix | Phase detected |
|---|---|---|---|---|
| ... | ... | ... | raw/customer_perspective.md | Phase 3 / Agent F |

## Section 3 — Pattern notes for Codex blind-spot adjustment

(Optional free-text. Omit if nothing pattern-level.)
```

Append to `bugs_encountered.md`: `[Phase 3.4] OK — wrote cc_catches_against_codex.md with N adoption entries and M new catches`.

## Step 3.5 — Cross-step thesis check (instructed at user via Codex)

After Agent F and the inbox writer complete, output to user:

```
==================================================
PHASE 3 COMPLETE -- {TICKER}
==================================================

Step files written:
  [done] step3_business_model.md
  [done] step4_industry.md
  [done] step5_moat_current.md
  [done] step7_accounting.md
  [done] step8_management.md
  [done] step4b_customer_perspective.md

==================================================
NEXT -> Switch to Codex and run:

  $stock-research-codex {TICKER} --consistency

(Note the `$` prefix — Codex activation syntax is `$`, not `/`.)

Codex independently checks for cross-section contradictions and
compound error paths. It also reads `raw/cc_catches_against_codex.md`
(written above) for catches that flow CC -> Codex.

When complete, return here and run:

  /stock-research {TICKER} --step3.5e

→ /clear before running the next flag (preserves your context window).
==================================================
```

Stop here. Do not continue to Phase 4 yet.

## When user runs `--step3.5e`:

Read `{BASE}/steps/step3.5_consistency_check.md`. If it lists contradictions:
- Read each affected step file
- Apply revisions per Codex's recommendations (re-check source if needed)
- Save revised step files
- Append to `bugs_encountered.md`: `[Step 3.5] CORRECTED: [step file] -> [what changed]`

If clean: append `[Step 3.5] OK — no contradictions found`.

### Step 3.5 propagation gate (NEW per n=6 evidence)

For each ISSUE-N you applied, the OLD phrase often lives in multiple files:
canonical summaries, step files, and the customer-perspective canonical. Append-only
correction is what bit NVO (stale FY26 guidance), SNOW (CFLT floor-vs-caveat
contradiction), and DECK (stale 8-K flags). Run a propagation pass:

1. For each ISSUE-N applied above, identify the OLD phrase exactly (the language
   you replaced or the stale figure you updated).
2. For each OLD phrase, search every file under `{BASE}/raw/*.md` and
   `{BASE}/steps/*.md`. Use Grep with the literal phrase. If the phrase appears
   in any file you didn't already update, treat the issue as NOT applied: open
   that file, fix the phrase, and re-run the search.
3. Loop until every ISSUE-N's OLD phrase is gone from every file (except inside
   `step3.5_propagation.md` itself, where it's intentionally quoted).

Write the log to `{BASE}/steps/step3.5_propagation.md`:

```
# Step 3.5 propagation gate — {TICKER} — {YYYY-MM-DD HH:MM}

| Issue | OLD phrase | Files searched | Files where found | Files corrected | Final status |
|---|---|---|---|---|---|
| ISSUE-1 | "FY26 guidance -5% to -13%" | raw/*.md, steps/*.md | raw/10k.md:25, raw/transcripts.md:84 | raw/10k.md, raw/transcripts.md | clean |
| ISSUE-2 | ... | ... | ... | ... | clean |

All issues final status: clean.
```

Step 3.5 does NOT complete until the log shows `clean` for every issue. Append
to `bugs_encountered.md`: `[Step 3.5 propagation] OK — N issues all clean across
M files searched`.

Then proceed to Phase 4.

## Phase 4 — Moat Durability

Spawn an agent with `agents/moat_durability.md` as prompt (prepend shared blocks, substitute `{TICKER}` and `{BASE}`). Apply the agent watchdog (soft 8m, hard 25m, retry on missing/zero-byte output).

Save output to `{BASE}/steps/step6_moat_durability.md`.

## Phase 5A — CC Valuation (multi-method, three-tier)

Spawn an agent with `agents/valuation.md` as prompt (prepend shared blocks, substitute). Apply the agent watchdog (soft 12m for Phase 5, hard 25m, retry on missing/zero-byte output).

The agent's first action is the PRECONDITION CHECK — abort loudly if any of the 5 reference files in `references/` are missing.

Save output to `{BASE}/steps/step9_valuation_cc.md`.

### Phase 5A.b — Verification B (orchestrator)

After the valuation agent completes and writes `step9_valuation_cc.md`, the orchestrator (this pipeline, not the valuation agent) runs Verification B. This mirrors the Phase 7b Verification D pattern and fixes the CRWD-run methodology bug where Verification B ran inside the valuation agent — which hit usage cap mid-verification on CRWD, forcing inline orchestrator fallback anyway.

Re-read `step9_valuation_cc.md` and `xbrl_summary.txt`. Then perform inline (or as a fresh `general-purpose` subagent if context budget tight):

1. Re-verify every input number against `xbrl_summary.txt`. Flag mismatches.
2. Re-fetch the current stock price and 30Y Treasury yield + core PCE. Confirm match (within 5%).
3. Manually re-calculate each row of the DCF tables. Correct any arithmetic errors.
4. Verify reverse-DCF inversions: forward DCF at the "required" CAGR should give NPV ≈ market cap. Confirm the valuation file explicitly states which base feeds the reverse-DCF solve (canonical OE / mature after-SBC margin / non-canonical issuer FCF). Flag if missing.
5. Verify the SBC handling per the canonical rule in `references/owner_earnings.md` (starting from GAAP NI → SBC NOT added back; per-share denominator = current diluted shares, NOT projected year-5). If the valuation file uses the non-canonical "issuer FCF + dilution haircut" scenario, confirm it is labeled as such and NOT cited as primary buy/keep/sell.
6. Verify Stage-10 decision logic applied correctly: base verdict + each downgrade fired or not, with explicit reasoning.

Write `{BASE}/steps/verification_b.md`:
```
| Input / Calculation | Value used | Source-verified value | Correct? |
```

Correct any arithmetic errors in `step9_valuation_cc.md` directly before the handoff message.

**Audit trail (mandatory).** The orchestrator's conversation transcript MUST show the Verification B work happening AFTER the valuation agent's invocation completed — not inside the valuation agent's tool calls. If the transcript shows Verification B was performed by the valuation agent itself (i.e., new tool calls under the same `Agent` invocation that produced `step9_valuation_cc.md`), surface as `[Phase 5A.b] FATAL: Verification B not dispatched by orchestrator` in `bugs_encountered.md` and re-run.

After Verification B, output to user:

```
==================================================
CC VALUATION COMPLETE -- {TICKER}
==================================================

step9_valuation_cc.md written.

Three numbers per the new framework: fair value range, hurdle value range, buy trigger.
Methods used per business classification.

==================================================
NEXT -> Switch to Codex for independent valuation:

  $stock-research-codex {TICKER} --valuation

(Note the `$` prefix — Codex activation syntax is `$`, not `/`.)

Codex independently builds its own valuation reading the same primary sources
WITHOUT seeing step9_valuation_cc.md. Catches assumption-level errors
(maintenance capex, owner earnings, growth, discount rate derivation) that
arithmetic verification cannot.

When complete, return and run:

  /stock-research {TICKER} --reconcile-valuation

→ /clear before running the next flag (preserves your context window).
==================================================
```

Stop here. Do NOT continue to Phase 6 yet — Phase 6 runs in `--reconcile-valuation` after the dual-model valuation reconciles.

## When user runs `--reconcile-valuation`:

Read both:
- `{BASE}/steps/step9_valuation_cc.md`
- `{BASE}/steps/step9_valuation_codex.md`

If `step9_valuation_codex.md` is missing (Codex side not updated, or user skipped the Codex valuation step): copy `step9_valuation_cc.md` to `step9_valuation_reconciled.md` AND `step9_valuation.md` (alias). Append to `bugs_encountered.md`: `[Phase 5C] WARNING: step9_valuation_codex.md missing; reconciled = CC valuation alone. Dual-model cross-check skipped.` Skip the rest of Phase 5C and proceed to Phase 6.

If both files exist, run **Phase 5C — Reconciliation** below.

## Phase 5C — Valuation reconciliation (Buffett framework)

Apply the reconciliation guardrails per `references/three_tier_decision.md`, `underwriteability_gate.md`, and `owner_earnings.md`.

### Step 1 — Stage-0 underwriteability check FIRST

Compare CC's `=== UNDERWRITEABILITY GATE ===` verdict to Codex's. This is the FIRST reconciliation question, before any number-level diff.

- If gate verdicts AGREE: proceed to Step 2.
- If gate verdicts DISAGREE: re-read primary sources available pre-Phase-6 (`step6_moat_durability.md` — Phase 4 disruption-vector inventory, the load-bearing source; `step4_industry.md`; `step5_moat_current.md`; `step7_accounting.md`; `step8_management.md`; `raw/customer_perspective.md` if present; `raw/competitors.md`) and the criteria in `underwriteability_gate.md`. **Do NOT read `step10_counter_attack.md`; it does not exist at Phase 5C.** Pick the more-defensible verdict. Document why. The downstream methods and MoS sizing depend on this — adjudicate first.
- If either side declared TOO HARD: surface as decision-flipping divergence; the reconciled output is TOO HARD (conservative). The other side's full DCF still runs as illustrative.

### Step 1.5 — Accounting bridge propagation check (NEW per v3 plan; phase-ordering fix)

Read `step7_accounting.md`'s two pre-valuation outputs: the `=== GAAP NI → PRE-VALUATION ECONOMIC EARNINGS BRIDGE (M1) ===` block and the `=== OPT-OUT FLAG ===` block.

**Bridge propagation check.** If `step7_accounting.md` emits opt-out flag != NONE, OR the bridge reconciliation satisfies either of:
  (a) the SIGN of pre-valuation economic earnings differs from GAAP NI, OR
  (b) |bridge magnitude| > 25% of |GAAP NI| (using $50M floor on |GAAP NI| denominator to avoid explosive ratios near zero),

verify that `step9_valuation_cc.md` and `step9_valuation_codex.md` both reference the accounting bridge in their owner-earnings derivation, AND explicitly document any disagreement with the bridge. Silent GAAP-NI consumption when accounting flagged material adjustment = load-bearing inconsistency; surface as a Phase 5C reconciliation finding and route to the reconciled valuation file.

Rationale for sign-flip OR 25% threshold: the original v1 blanket 10% over-fires on healthy SaaS where SBC alone routinely runs 10-20% of GAAP NI without indicating a quality problem. Sign-flip or 25% catches genuine bridge-magnitude inconsistencies.

**Opt-out flag cascade honored check.** If `step7_accounting.md` emits opt-out flag = RECOMMEND PARTIAL or RECOMMEND TOO HARD, verify that both step9_valuation files reflect the cascade downgrade OR explicitly escalate a documented disagreement per the binding-unless-escalated rule in `references/underwriteability_gate.md`. Skipped cascade with no escalation = load-bearing inconsistency.

**Verification mechanic — LLM-driven coherence check, NOT grep.** Dispatch this prompt to a fresh general-purpose Agent (cold context):

> Read `step7_accounting.md` (=== GAAP NI → PRE-VALUATION ECONOMIC EARNINGS BRIDGE === and === OPT-OUT FLAG === blocks), then read `step9_valuation_cc.md` and `step9_valuation_codex.md`. Answer two questions:
>
> (1) Do both valuation files cite the accounting bridge when deriving owner earnings, OR do they explicitly document a source-backed disagreement with the bridge?
>
> (2) If the accounting opt-out flag is RECOMMEND PARTIAL or RECOMMEND TOO HARD, do both valuation files reflect the cascade downgrade OR explicitly escalate with source-backed reason?
>
> Output a single JSON line: `{"bridge_propagation": "honored|silently-skipped|escalated", "cascade_honored": "honored|silently-skipped|escalated|n/a", "evidence_bridge": "<one sentence>", "evidence_cascade": "<one sentence>"}`

A `silently-skipped` verdict on either dimension is a load-bearing inconsistency — log to `bugs_encountered.md` as `[Phase 5C Step 1.5] WARNING: <bridge|cascade> silently skipped — <evidence>` and surface in the reconciled valuation file's `=== RECONCILIATION SUMMARY ===` section.

**Final D9 buyback-vs-IV comparison happens here, not in accounting.** Now that valuation has produced IV, compute avg buyback price last 5y vs. **the LOWER of cc-pessimist-IV and codex-pessimist-IV** (most conservative comparison; matches Buffett's lean-conservative discipline per [TX 43151]). If avg buyback price > that conservative pessimist IV: flag as "buybacks above intrinsic value — destroys per-share value" in the reconciled output. Accounting started this work with pre-valuation optics indicators only; Step 1.5 finishes it.

### Step 2 — Section-by-section divergence diff (single conservative case)

For each output section of the new framework (RATE ANCHOR through VERDICT — see `agents/valuation.md` REQUIRED OUTPUT), compare CC's value to Codex's value. Apply the material-divergence thresholds:

```
Stage-0 gate verdict:              ALWAYS material (Step 1 above)
Intrinsic value (single number):   > 10% OR decision flips        → MATERIAL
Discount rate (Buffett rate):      > 50 bp                         → MATERIAL
Stage-1 growth:                    > 2pp                           → MATERIAL
Stage-1 length:                    > 2 years                       → MATERIAL
Terminal growth:                   > 0.5pp                         → MATERIAL
Maintenance capex:                 > 20% relative OR > 5% intrinsic effect → MATERIAL
SBC handling (starting point + treatment):  ALWAYS material if differs
WC-float treatment (SaaS):         ALWAYS material if magnitude differs > 20%
MoS sizing (cell + modifiers):     > 5pp difference                → MATERIAL
Opportunity-cost floor verdict:    ALWAYS material if differs
Capital-allocation flag states:    flag-by-flag review; always material if any differs

Method weights (which methods trusted):  flag as note, not material
Illustrative-CAPM section:         NOT RECONCILED — preserved as-is from both sides
```

### Step 3 — Adjudicate each material divergence

For each material divergence, write a row of the form:

```
| Divergence | CC value | CC reasoning | Codex value | Codex reasoning | Adopted | Source-backed reason |
```

`Adopted` is one of:
- **CC** — CC's number is more defensible against primary sources
- **Codex** — Codex's number is more defensible
- **Synthesis** — neither is correct; re-derive from primary sources and use the new number
- **[PENDING-CLASS]** — divergence is a downstream consequence of the Step 1 classification dispute and resolves automatically once classification is adjudicated. Use only when the divergence would not exist if both sides agreed on the primary class (e.g., maint-capex treatment, Stage-1 length, MoS sizing). Do NOT use to dodge independent adjudication of divergences that would persist across classifications (e.g., owner-earnings derivation choices, discount-rate certainty premium within the same class).

Source-backed reason is mandatory: cite primary-source line/quote that supports the adoption decision. "CC's reasoning was better" without source backing is not allowed.

### Step 4 — Compute reconciled single conservative output

Combine adopted inputs into ONE reconciled DCF:
```
Reconciled Buffett discount rate    = adopted per Step 3
Reconciled owner-earnings base      = adopted per Step 3 (per starting-point table in owner_earnings.md)
Reconciled Stage-1 growth           = adopted per Step 3
Reconciled Stage-1 length           = adopted per Step 3 (constrained by reconciled Stage-0 verdict)
Reconciled terminal g               = adopted per Step 3
Reconciled MoS                      = adopted per Step 3 (3×3 cell + modifier adders)

Reconciled intrinsic value (per share) = output of DCF with adopted inputs
Reconciled buy trigger                  = reconciled intrinsic × (1 − reconciled MoS)
Reconciled forward TSR check            = re-compute at current price; PASS/FAIL vs e_floor
```

The reconciled output is ONE intrinsic value (not a range across scenarios). The sensitivity table is also re-run with adopted inputs.

If CC and Codex disagree materially on a load-bearing input AND the disagreement cannot be source-resolved (e.g., both readings are defensible from primary sources): adopt the more-conservative value. Document explicitly. Per Buffett 2003 [TX 43151]: be conservative where you must.

### Step 5 — Decision-flipping check

If the reconciled verdict differs from EITHER CC's verdict OR Codex's verdict, this is a load-bearing finding. Document explicitly:

```
=== DECISION-FLIPPING DIVERGENCE ===
[Which divergence flipped the verdict? CC said X; Codex said Y; reconciled is Z.
 Cite the specific divergence (likely classification or maintenance-capex or
 Stage-1 growth) and surface in final memo Section 8.]
```

### Step 6 — Update inbox

Update `{BASE}/raw/cc_catches_against_codex.md` Section 3 (or new Section 5 if 1-4 are taken):

```
## Section 5 — Valuation reconciliation outcomes ({YYYY-MM-DD HH:MM})

| Divergence | Adopted | Reason |
|---|---|---|
| ... | CC / Codex / Synthesis | source-backed reason |
```

### Step 7 — Write reconciled output

Output file: `{BASE}/steps/step9_valuation_reconciled.md`

Format: same 14 required output sections as the individual valuations PLUS a final `=== RECONCILIATION SUMMARY ===` section listing every material divergence and its adoption decision.

Then COPY `step9_valuation_reconciled.md` to `step9_valuation.md` (alias for backwards compatibility — `final_memo.md`, `counter_attack.md`, and other downstream prompts read `step9_valuation.md`).

Append to `bugs_encountered.md`: `[Phase 5C] OK — reconciled N material divergences; verdict-flipping divergence: <yes/no> (<details>)`.

## Phase 6 — Counter-Attack

Spawn an agent with `agents/counter_attack.md` as prompt. Apply the agent watchdog (soft 8m, hard 25m, retry on missing/zero-byte output).

Save output to `{BASE}/steps/step10_counter_attack.md`.

## Phase 6.5 — Refresh `cc_catches_against_codex.md` (inbox refresh)

Before sending the user to Codex `--attack`, refresh `{BASE}/raw/cc_catches_against_codex.md`. Codex's policy is "read current version before each Codex handoff," so the inbox must include any new catches that arose between Phase 3 and now (during Phase 3.5e consistency integration, Phase 4 moat durability, Phase 5A/5C valuation reconciliation, Phase 6 counter-attack).

Append (don't overwrite) a new dated section:

```
## Section 6 — Catches added between Codex --consistency and Codex --attack ({YYYY-MM-DD HH:MM})

| Codex claim | CC's verified correction | Primary source | Canonical fix | Phase detected |
|---|---|---|---|---|
| ... | ... | ... | ... | Phase 3.5e / Phase 4 / Phase 5A / Phase 5C / Phase 6 |
```

If no new catches: append `## Section 6 — No new CC catches against Codex since last refresh`.

Append to `bugs_encountered.md`: `[Phase 6.5] OK — refreshed cc_catches_against_codex.md with N new catches`.

Then output to user:

```
==================================================
COUNTER-ATTACK COMPLETE -- {TICKER}
==================================================

step10_counter_attack.md written.

OPTIONAL: For a second independent adversarial perspective, switch to Codex:

  $stock-research-codex {TICKER} --attack

(Note the `$` prefix — Codex activation syntax is `$`, not `/`.)

Codex independently runs the 8-attack framework against the canonical
summaries (without seeing CC's attack). It also re-reads the refreshed
`raw/cc_catches_against_codex.md` for any new CC catches and adjusts
its blind-spot framing. Genuine model-diversity in attack vectors.

When done, return and run:

  /stock-research {TICKER} --step11e

To skip Codex's attack and proceed directly to the final memo:

  /stock-research {TICKER} --step11e

(Both invocations integrate whatever step10_codex_attack.md exists, or none.)

→ /clear before running the next flag (preserves your context window).
==================================================
```

Stop here.

## When user runs `--step11e`:

Check whether `{BASE}/steps/step10_codex_attack.md` exists.
- If yes: Phase 7's final-memo agent reads BOTH attack files and integrates per `agents/counter_attack.md` "INTEGRATING CODEX'S ATTACK" section.
- If no: Phase 7 reads only `step10_counter_attack.md`.

## Phase 7 — Final Memo + Verification C + Verification D

### Phase 7a — Final-memo agent (writes draft + Verification C inline)

Spawn an agent with `agents/final_memo.md` as prompt. Apply the agent watchdog (soft 8m, hard 25m, retry on missing/zero-byte output).

The agent writes the draft to `{BASE}/steps/step11_final_memo.md`, then runs Verification C (full fact-check) inline as described in the agent file. Corrections applied to the draft. Final corrected memo copied to `{BASE}/{TICKER}_research_memo.md`.

**The agent's job ends after Verification C. Do NOT instruct it to run Verification D.**

### Phase 7b — Verification D (orchestrator dispatches cold subagent)

After the final-memo agent completes, the orchestrator (this pipeline, not the final-memo agent) directly spawns a fresh `general-purpose` Agent for Verification D. This fixes the CRWD-run methodology bug where Verification D ran inline and never actually tested the Key Insight from cold context.

**Dispatch step.** Spawn an Agent (subagent_type: `general-purpose`) with this exact prompt (substitute `{BASE}` and `{TICKER}`):

```
You are doing a single focused task: judging whether the Key Insight section
of an investment memo contains a non-obvious finding or a generic narrative.

Inputs:
- {BASE}/steps/step11_final_memo.md — read Section 3 (THE KEY INSIGHT) only.
- Best-effort WebFetch 2-3 pieces of public market commentary for {TICKER}
  (Seeking Alpha, Motley Fool, Yahoo Finance, MarketWatch, etc.). If none
  accessible, mark "comparison sources unavailable" and proceed using general
  knowledge of analyst-narrative patterns. Web fetch is NOT a hard blocker.

Test: would such public market commentary plausibly write the same paragraph?
- If yes: verdict = generic (or replace-with-no-edge if the paragraph is
  obviously boilerplate with no surprising claim, no specific number, and no
  testable counter-evidence).
- If no: verdict = authentic. Document why it is non-obvious vs the
  comparables.

Write {BASE}/steps/verification_d.md with this exact format:
  KEY INSIGHT VERIFICATION: <authentic | generic | replace-with-no-edge>
  Reasoning: <2 sentences>
  Comparison sources: <list URLs or "unavailable">

DO NOT modify step11_final_memo.md. The orchestrator will apply replacement
if needed. DO NOT read any other step file. DO NOT read raw/ files. Fresh
context is the entire point of this verification.
```

**Read the verdict and apply fail-closed handling.** Read `{BASE}/steps/verification_d.md`. Apply:

- **`authentic`** → keep Section 3 unchanged.
- **`generic`** → MUST act. Two options:
  1. **Rewrite + re-dispatch (preferred if step files contain a defensible non-obvious finding):** orchestrator re-reads step files (Phase 3 outputs, Phase 4 moat durability, Phase 5C reconciliation, Phase 6 counter-attack) for findings that genuinely surprised the analysis. Rewrite Section 3 of `step11_final_memo.md` with a non-obvious insight grounded in those findings. Re-dispatch the same Verification D subagent on the rewritten section. Cap at ONE rewrite attempt — if second verdict is also `generic`, force `replace-with-no-edge`.
  2. **Replace immediately with no-edge:** if step files yield no defensible non-obvious finding, apply the literal text *"No edge identified: the consensus view appears to be correctly pricing this business. The analysis confirms the market's assessment but does not find a differentiated angle."* directly.
- **`replace-with-no-edge`** → immediate no-edge replacement using the literal text above.

**Principle:** a Section 3 flagged as `generic` does NOT make it into the final memo unchanged. Either it gets replaced with something substantive, or with the honest "no edge" admission.

**Log to bug log.** After applying the handling above, append to `{BASE}/bugs_encountered.md`:
```
[Verification D] verdict=<authentic|generic|replace-with-no-edge>; action=<kept|rewrote|replaced-with-no-edge>; dispatched_by=orchestrator
```

Copy the (possibly re-corrected) `step11_final_memo.md` to `{BASE}/{TICKER}_research_memo.md`.

### Audit trail (mandatory)

The orchestrator's conversation transcript MUST show an `Agent` tool invocation for Verification D after the final-memo agent completes. If the transcript shows Verification D being run inline inside the final-memo agent (the CRWD-run bug), the orchestrator failed to enforce dispatch — surface as a `[Phase 7] FATAL: Verification D not dispatched as cold subagent` entry in `bugs_encountered.md` and re-run.

## Final user message

```
==================================================
RESEARCH COMPLETE -- {TICKER}: [COMPANY NAME]
==================================================

Steps completed:
  [done] Step 1E   Canonical summaries + Verification A
  [done] Step 2    Gate: [REJECT / WATCH / ADVANCE]
  [done] Step 3    Business model
  [done] Step 4    Industry structure (deep research)
  [done] Step 4b   Customer perspective (deep research)
  [done] Step 5    Current competitive advantage
  [done] Step 6    Moat durability (deep research, attack test)
  [done] Step 7    Accounting quality
  [done] Step 8    Management
  [done] Step 9    Valuation + reverse DCF + Verification B
  [done] Step 10   Counter-attack [+ Codex attack if present]
  [done] Step 11   Final memo + Verification C + Verification D

Decision: [BUY / WATCHLIST / PASS]
Key insight: [authentic / no-edge admission]
Reliability score: [X]% (see steps/verification_c.md)
Issues logged: [N warnings, M corrections] (see bugs_encountered.md)

Final memo: {BASE}/{TICKER}_research_memo.md

==================================================
NEXT -> Build the comprehensive report (separate skill):

  /stock-report {TICKER}

The /stock-report skill consumes the canonical post-verification files in
{BASE}/raw/ and {BASE}/steps/ and produces a single self-contained HTML
report at {BASE}/{TICKER}_full_report.html. Calibrated for a CFA-Level-1
reader; comprehensive (not just the memo); surfaces the verification
trail and Codex-originated catches in a Reliability section.

==================================================
BEFORE ACTING ON THIS MEMO:

1. Read bugs_encountered.md -- review every warning and correction.
2. Read [HUMAN-VERIFY] items in the memo and check them yourself.
3. Review steps/verification_c.md for the full error table and Verification D outcome.
4. Spot-check the historical analogs in step6 and step10 -- the deep-research
   sections are the highest-confabulation-risk outputs.
5. Write your own one-page thesis from memory before acting. If you cannot do
   this without looking at the memo, you do not understand the business well
   enough to invest.
==================================================
```
