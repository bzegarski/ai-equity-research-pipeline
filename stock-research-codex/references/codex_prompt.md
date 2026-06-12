# Stock Research Codex Compatibility Note

`SKILL.md` is the authoritative instruction source for this skill. This file exists only to prevent older sessions from loading the retired standalone prompt.

Current Codex-owned phases:

- `$stock-research-codex TICKER --audit`: Phase 0 collection audit.
- `$stock-research-codex TICKER`: Step 1A independent summaries.
- `$stock-research-codex TICKER --step1d`: Step 1D cross-check of CC summaries.
- `$stock-research-codex TICKER --consistency`: cross-step thesis consistency check.
- `$stock-research-codex TICKER --valuation`: independent Buffett-style owner-earnings valuation.
- `$stock-research-codex TICKER --attack`: optional adversarial counter-attack.
- `$stock-research-codex TICKER --deep-customer`: optional manual ChatGPT.com Deep Research handoff for customer evidence.
- `$stock-research-codex TICKER --deep-attack-research`: optional manual ChatGPT.com Deep Research handoff for outside-view attack evidence.

Step 1A writes:

- `RAW/10k_codex.md`
- `RAW/10q_codex.md`
- `RAW/proxy_codex.md`
- `RAW/insider_codex.md`
- `RAW/transcripts_codex.md`
- `RAW/customer_perspective_codex.md`

Step 1D writes:

- `RAW/10k_codex_xcheck.md`
- `RAW/10q_codex_xcheck.md`
- `RAW/proxy_codex_xcheck.md`
- `RAW/insider_codex_xcheck.md`
- `RAW/transcripts_codex_xcheck.md`
- `RAW/customer_perspective_codex_xcheck.md`

Codex does not write `competitors_codex.md` or `competitors_codex_xcheck.md`. CC owns competitor-file analysis unless a future coordinated skill change says otherwise.
