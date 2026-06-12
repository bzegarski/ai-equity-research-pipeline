# AI-Assisted Equity Research Pipeline

A multi-phase company-research pipeline built as [Claude Code](https://claude.com/claude-code) skills, with OpenAI Codex as an independent second model. It takes a US-listed ticker and produces a sourced investment memo — and, optionally, a self-contained HTML report — from SEC primary sources.

I'm building this to systematise my own long-term investing research. It is shaped by the Buffett / Munger / Graham / Fisher / Marks tradition: primary sources over commentary, owner earnings over adjusted EBITDA, an explicit margin of safety, and a forced **"no edge identified"** admission when the work doesn't support a view. It is a work in progress: I don't yet trust it enough to let it drive real decisions, and the calibration discipline for earning that trust is part of the design (see [Known limitations](#known-limitations--roadmap)).

**Sample output:** [`sample-report/CRWD\_full\_report.html`](sample-report/CRWD_full_report.html) — a complete report produced by the pipeline (download and open in a browser).

## What it does

```
/stock-research TICKER
        │
Phase 0   Download primary sources from SEC EDGAR (10-K, 10-Q, proxy, 8-Ks,
          Form 4 insider filings, XBRL financials) + earnings transcripts.
          Python scripts handle extraction; every anomaly goes to a bug log.
        │
Step 1    Both models independently summarize the same six core documents.
          Codex then cross-checks Claude's summaries against the filings.
        │
Phase 3   Five parallel research agents: business model, industry, current
          moat, forensic accounting, management \& capital allocation —
          plus a customer-perspective agent working from verified reviews.
        │
Phase 4   Moat durability: named disruption vectors, historical analogs,
          leading indicators that would falsify the moat claim.
        │
Phase 5   Valuation, twice: Claude and Codex each run an independent
          multi-method valuation from a shared methodology library, then
          the two are reconciled line by line.
        │
Phase 6   Adversarial counter-attack: a dedicated pass that tries to kill
          the thesis, with base rates and falsifying evidence.
        │
Phase 7   Final memo with reliability score, claim-by-claim source labels,
          and four verification passes (A–D) in fresh context.

/stock-report TICKER   (optional, runs after research completes)
          Builds a single-file HTML writeup: narrative sections written
          against hard style rules, SVG charts rendered by Python, a
          hover-tooltip glossary, and inline epistemic markers that tag
          every load-bearing claim as fact / interpretation / verify.
```

## Design decisions that matter

* **Two models, genuinely independent.** Codex doesn't review Claude's conclusions — it re-derives summaries and valuation from the same primary sources, and disagreements surface at explicit reconciliation checkpoints. Cross-model anchoring is treated as a bug: a cross-check that finds zero discrepancies gets logged as suspicious.
* **Forced honesty about edge.** The memo template requires either a specific, falsifiable Key Insight or the literal admission that no edge was identified. Most runs should end in "no edge" — that's the point.
* **Claims carry their sources.** Every factual claim in the working files is labeled `\[FACT|source|confidence]`. The report layer converts these into reader-facing markers: verifiable fact, author's interpretation, or needs-human-verification.
* **Look up, never guess.** Anything not in the filings (GICS classification, regulatory dates, industry statistics) is fetched from a named source or marked as a gap. Inventing a plausible number is treated as the worst possible failure.
* **No CAPM.** Discount rates follow a stated equity hurdle with explicit guardrails (methodology in `stock-research/references/`), not beta. The valuation library covers owner earnings, multi-method triangulation, and a three-tier fair-value / hurdle / buy decision.
* **Bug log discipline.** Every run appends extraction warnings, fallbacks, and corrections to `bugs\_encountered.md`. Skill iteration happens against the accumulated bug logs, not against impressions.

## Repo layout

|Folder|What it is|
|-|-|
|`stock-research/`|The main Claude Code skill: orchestrator (`SKILL.md`), phase instructions, agent prompts, shared methodology references, and standalone Python extraction scripts.|
|`stock-report/`|The report-builder skill: writing rules, per-section prompts, verification gates, chart/template Python, and the GICS-keyed sector \& industry primer system.|
|`stock-research-codex/`|The Codex-side skill: independent summarization, cross-checks, independent valuation, optional adversarial attack.|
|`sample-report/`|One complete HTML report produced by the pipeline.|

## Running it

This is a personal tool published as a portfolio piece, not a packaged product — but it runs if you have the same setup:

1. **Claude Code** with `stock-research/` and `stock-report/` installed under `\~/.claude/skills/`, and **Codex CLI** with `stock-research-codex/` under `\~/.codex/skills/`.
2. **Python 3.13+** on PATH (scripts are stdlib-only).
3. **SEC EDGAR contact email:** EDGAR requires a real contact address in the User-Agent header. Replace `your.email@example.com` (in `stock-research/SKILL.md`, `phases/phase0\_download.md`, and `scripts/`) with yours.
4. Paths in the skill files assume a `\~/Research/` output directory; adjust to taste.

Then: `/stock-research TICKER`, follow the on-screen handoffs between the Claude and Codex terminals, and finish with `/stock-report TICKER`.

## Known limitations \& roadmap

This is a demonstration of pipeline engineering, not a finished research product. The honest list:

* **Early errors propagate.** The pipeline is sequential: if a Phase 0 extraction or an early summary gets something wrong, later phases build on it and the whole line of analysis inherits the broken assumption. The existing mitigations (cross-model checks, the bug log, verification passes A–D) catch many of these but not all, and they catch them *late*.
* **Planned fix — human-in-the-loop gates.** The next architectural step is approval checkpoints at load-bearing conclusions: the pipeline states what it concluded and what that conclusion will be used for downstream, and a human confirms or vetoes before it proceeds. Verification by construction, not just by audit.
* **Calibration before trust.** Every run appends its verdict and three-tier valuation to an outcomes log (`scripts/append\_outcome.py`), so the pipeline's judgments can be scored against what actually happened. Until that record exists, the output is a structured starting point for human work — not a decision input.
* **The sample report is a point-in-time demonstration.** It shows what the pipeline produces; it is not a maintained investment view.

## Disclaimer

Nothing this tool produces is investment advice. The sample report reflects a point-in-time analysis. Do your own work — helping with that is the tool's only job.

