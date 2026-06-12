# Phase 0 — Download raw files

Run when: no flag (e.g. `/stock-research TICKER`).

CRITICAL: Phase 0 downloads only. No summarization, no interpretation. Both CC and Codex independently parse the raw files in Step 1.

Substitute `{TICKER}` and `{BASE}` throughout. `{BASE}` is the timestamped path computed by `SKILL.md` (e.g., `~/Research/MSFT_9.5.2026`).

**Before starting Phase 0 work:** if `~/Research/_run_methodology_checklist.md` exists, read it. It is the NEUTRAL Round-3 methodology compliance checklist (ticker-agnostic; no expected answers). Apply its self-checks throughout subsequent phases. Do NOT read any `*_post_run_checklist.md` files — those are user-only and would compromise dual-model independence.

## Step 0.0 — Initialize directories and bug log

```bash
mkdir -p "{BASE}/raw" "{BASE}/steps"
cd "{BASE}"
```

The `{BASE}` folder name encodes the run date (D.M.YYYY format, no leading zeros). Subsequent CC and Codex commands resolve to this same folder by globbing `Research/{TICKER}_*/` and picking the most recent mtime — see `SKILL.md` "Compute {BASE}" for the resolution rule.

Write the header to `bugs_encountered.md`:
```
# bugs_encountered.md -- {TICKER} -- run started YYYY-MM-DD

## Phase 0
```

## Step 0.1 — Resolve CIK

```bash
curl -s -A "Research your.email@example.com" \
  "https://efts.sec.gov/LATEST/search-index?q=%22{TICKER}%22&forms=10-K" \
  -o "raw/cik_search.json"
py "~/.claude/skills/stock-research/scripts/resolve_cik.py" raw/cik_search.json {TICKER}
```

Pass `{TICKER}` as the second arg. The script requires it to verify the returned hit's display_name contains `({TICKER})` — without this, EDGAR full-text search can return any filing that mentions the ticker (e.g. searching `MSFT` returned Activision Blizzard before this fix).

Extract the CIK. Pad to 10 digits → `CIK10`. Log company name.

## Step 0.2 — Fetch submissions JSON

```bash
curl -s -A "Research your.email@example.com" \
  "https://data.sec.gov/submissions/CIK{CIK10}.json" \
  -o "raw/submissions.json"
```

### Step 0.2a — Detect filing track (10-K vs FPI)

A foreign private issuer (FPI) files 20-F annually and 6-K throughout the year
instead of 10-K / 10-Q / 8-K. Detect by scanning `raw/submissions.json` for any
20-F filing in the last 14 months AND no 10-K filing in the same window:

```bash
py "~/.claude/skills/stock-research/scripts/detect_filing_track.py" raw/submissions.json
```

If `track: fpi`: follow the FPI substitution map for the rest of Phase 0:

| US-issuer step | FPI substitute |
|---|---|
| 10-K (Step 0.4) | most recent 20-F. If 20-F is a thin shell with a separate annual-report exhibit (e.g. `nvo-20251231_d2.htm`), prefer the d2/ar exhibit. |
| 10-Q (Step 0.5) | most recent 6-K reporting interim financials. |
| 8-K (Step 0.2b) | 6-K material-event subset filtered by keyword (`extract_8k.py` already accepts 6-K input). |
| DEF 14A (Step 0.6) | most recent Remuneration Report 6-K when present, else write `FPI_NO_PROXY` to `raw/proxy_raw.txt` and log to `bugs_encountered.md`. |
| Form 4 (Step 0.8) | FPI insiders file PDMR transactions via company announcements, not Form 4. Write `FPI_NO_FORM_4` to `raw/insider_raw.txt` and log a documented limitation. Phase 8 (management agent) reads this and treats it as a known gap, not a bug. |

**Refusal rule (per Codex): refuse the ticker only when CORE evidence is missing
— i.e. the most recent annual filing (20-F or equivalent) cannot be located OR
the most recent interim financial filing (6-K with financials) cannot be located.
Absence of proxy / Form-4 substitutes is acceptable; the dispatcher writes
`FPI_NO_PROXY` / `FPI_NO_FORM_4` markers and Phase 8 reads them as documented
limitations.**

Parse to extract accession numbers + primary documents for 10-K, 10-Q, DEF 14A
(or 20-F, 6-K, Remuneration-6-K under FPI track):
```bash
py "~/.claude/skills/stock-research/scripts/list_filings.py" raw/submissions.json
```

Record for each filing type: accession (e.g. `0001327567-25-000027`), accession-no-dashes (18 digits), primary doc filename.

## Step 0.2b — Download recent 8-K filings (NEW)

```bash
py "~/.claude/skills/stock-research/scripts/extract_8k.py" raw/submissions.json raw/recent_8k.txt
```

If the script reports MATERIAL_EVENTS_DETECTED, the events table appears at top of `recent_8k.txt`. Phase 2 (Gate) and Agent E (Management) read this file.

## Step 0.3 — Save XBRL financial facts

```bash
curl -s -A "Research your.email@example.com" \
  "https://data.sec.gov/api/xbrl/companyfacts/CIK{CIK10}.json" \
  -o "raw/10k_xbrl.json"

py "~/.claude/skills/stock-research/scripts/extract_xbrl.py" raw/10k_xbrl.json > raw/xbrl_summary.txt 2> raw/xbrl_missing.txt
```

`extract_xbrl.py` auto-detects taxonomy: if `us-gaap` facts are empty/missing
but `ifrs-full` is present, it delegates to `extract_ifrs_xbrl.py`. The
summary's first two lines are always `TAXONOMY: <us-gaap|ifrs-full>` and
`CURRENCY: <currency>` so downstream agents can read either uniformly.

After running:
- Check `raw/xbrl_missing.txt`. If it has content, append to `bugs_encountered.md` as WARNING.
- Look for `SHARES_JUMP:` lines — log to bugs as `[Phase 0] WARNING: stock-split detected ...`
- If `raw/xbrl_summary.txt` is empty: critical failure. Log and abort Phase 0.

## Step 0.4 — Download and strip 10-K (or 20-F under FPI track)

```bash
curl -s -A "Research your.email@example.com" \
  "https://www.sec.gov/Archives/edgar/data/{CIK}/{10K_ACC_NODASH}/{10K_PRIMARY_DOC}" \
  -o "raw/10k_raw.htm"
py "~/.claude/skills/stock-research/scripts/strip_10k.py" raw/10k_raw.htm raw/10k_raw.txt
```

Then run the track-aware TOC/cover trim. `clean_canonical.py` rewrites
`raw/10k_raw.txt` in place with the TOC prefix removed, or leaves it unchanged
when no TOC pattern is detected:

```bash
py "~/.claude/skills/stock-research/scripts/clean_canonical.py" \
  raw/10k_raw.txt --track 10k       # use --track 20f under FPI
```

Log the `STRIPPED_TOC: N chars` (or `skipped`) line to `bugs_encountered.md`.

If the resulting file exceeds 400,000 chars, extract sections:

```bash
py "~/.claude/skills/stock-research/scripts/extract_sections.py" raw/10k_raw.txt
# FPI track: pass --track fpi to apply the 20-F section mapping
#   (Item 4 -> Item1, Item 3D -> Item1A, Item 5 -> Item7, Item 18 -> Item8)
```

This writes per-section chunks to `raw/_chunks/item1.txt`, `item1a.txt`, `item7.txt`, `item8.txt`. Truncates `raw/10k_raw.txt` to concatenated key sections if original >400k chars. Logs which strict-vs-fallback strategy worked per section.

## Step 0.5 — Download and strip 10-Q

```bash
curl -s -A "Research your.email@example.com" \
  "https://www.sec.gov/Archives/edgar/data/{CIK}/{10Q_ACC_NODASH}/{10Q_PRIMARY_DOC}" \
  -o "raw/10q_raw.htm"
py "~/.claude/skills/stock-research/scripts/strip_10k.py" raw/10q_raw.htm raw/10q_raw.txt
```

Apply section extraction if >400k chars.

## Step 0.6 — Download and strip proxy (DEF 14A)

```bash
curl -s -A "Research your.email@example.com" \
  "https://www.sec.gov/Archives/edgar/data/{CIK}/{PROXY_ACC_NODASH}/{PROXY_PRIMARY_DOC}" \
  -o "raw/proxy_raw.htm"
py "~/.claude/skills/stock-research/scripts/strip_10k.py" raw/proxy_raw.htm raw/proxy_raw.txt
```

Note: proxy structure does NOT match Item 1/1A/7/8; section extraction does not apply. Keep full file.

## Step 0.7 — Download competitor filings (with XBRL)

WebSearch for the 2-3 closest publicly traded competitors to {TICKER}. For each:

1. Resolve their CIK:
   ```bash
   curl -s -A "Research your.email@example.com" \
     "https://efts.sec.gov/LATEST/search-index?q=%22{COMP_TICKER}%22&forms=10-K" \
     -o "raw/comp_{COMP_TICKER}_cik.json"
   py "~/.claude/skills/stock-research/scripts/resolve_cik.py" raw/comp_{COMP_TICKER}_cik.json {COMP_TICKER}
   ```

2. Download competitor's 10-K and submissions:
   ```bash
   curl -s -A "Research your.email@example.com" \
     "https://data.sec.gov/submissions/CIK{COMP_CIK10}.json" \
     -o "raw/comp_{COMP_TICKER}_submissions.json"
   ```
   Get most recent 10-K accession + primary doc, download, strip via `scripts/strip_10k.py`.

3. **Extract competitor's Item 1** using:
   ```bash
   py "~/.claude/skills/stock-research/scripts/extract_sections.py" \
     raw/comp_{COMP_TICKER}_raw.txt \
     --chunks-dir raw/_chunks_comp/{COMP_TICKER}
   ```
   The `--chunks-dir` flag is REQUIRED for competitors so they don't clobber the
   primary ticker's `raw/_chunks/`. (DECK regression: running competitors without
   the flag silently overwrote DECK's primary chunks.) The strict-then-gap-based
   logic handles inverted xa0 conventions (PANW vs FTNT/CRWD experience).

4. **Download competitor XBRL:**
   ```bash
   curl -s -A "Research your.email@example.com" \
     "https://data.sec.gov/api/xbrl/companyfacts/CIK{COMP_CIK10}.json" \
     -o "raw/comp_{COMP_TICKER}_xbrl.json"
   py "~/.claude/skills/stock-research/scripts/extract_xbrl.py" raw/comp_{COMP_TICKER}_xbrl.json > raw/comp_{COMP_TICKER}_xbrl_summary.txt
   ```

5. Append all competitor data to `raw/competitors_raw.txt` with clear separators:
   ```
   === COMPETITOR: {COMP_TICKER} — {COMP_NAME} ===
   [Item 1 text from raw/_chunks_comp/{COMP_TICKER}/item1.txt]

   === COMPETITOR XBRL: {COMP_TICKER} ===
   Revenue FY[YY] | $X.XB | XBRL: [concept]
   GrossProfit FY[YY] | $X.XB | XBRL: GrossProfit
   OperatingIncome FY[YY] | $X.XB | XBRL: OperatingIncomeLoss
   Gross margin FY[YY]: X.X%
   Operating margin FY[YY]: X.X%
   Revenue CAGR 3yr: X.X%
   ```

Log competitor tickers chosen and reasons.

## Step 0.8 — Download insider transactions (EDGAR Form 4)

```bash
py "~/.claude/skills/stock-research/scripts/parse_form4.py" raw/submissions.json raw/insider_raw.txt
```

The script applies BUG-1 fix (unpadded CIK) and writes either rows or `NO_INSIDER_DATA_FOUND`.

## Step 0.9 — Fetch earnings transcripts (with source-quality detection)

Try in order:
1. WebSearch: `"[Company Name] investor relations earnings call transcript"` — WebFetch first credible-looking IR-page result.
2. WebFetch: `https://www.fool.com/earnings-call-transcripts/?search={TICKER}` — try the most recent linked transcript.
3. WebSearch: `"[Company Name] earnings call transcript [most recent quarter] site:seekingalpha.com"`
4. WebSearch: `"[Company Name] earnings call transcript [most recent quarter]"` — any remaining credible result.

If found at any step: save full text to `raw/transcripts_raw.txt` and continue.

If no transcript found after 4 attempts:
```
Could not find an earnings transcript for {TICKER} automatically after 4 attempts.

Options:
  (a) Paste a URL here and I will fetch it
  (b) Paste the transcript text directly into the chat
  (c) Type SKIP to proceed without a transcript

Waiting for your choice before continuing Phase 0.
```

Then:
- URL: WebFetch and save.
- Pasted text: save directly.
- SKIP: write `TRANSCRIPT_UNAVAILABLE` to file. Log warning.

After save, run source-quality detection:
```bash
py "~/.claude/skills/stock-research/scripts/detect_transcript_format.py" raw/transcripts_raw.txt "URL1,URL2"
```

This writes a `TRANSCRIPT_SOURCE_QUALITY: [verbatim|structured_summary|unavailable]` header at the top of the file. Downstream agents read this and propagate confidence.

## Step 0.10 — Write phase0_log.txt

```
Company name: [from EDGAR]
CIK: [number]
10-K: filed [date], accession [number], primary doc [filename]
10-Q: filed [date], accession [number], primary doc [filename]
Proxy: filed [date], accession [number], primary doc [filename]
Most recent 8-K: filed [date]
10-K format: [HTML-stripped / truncated to key sections / full]
10-K chars before truncation: [N]
XBRL missing concepts: [list or "none"]
SHARES_JUMP detected: [list or "none"]
Competitors: [ticker list] — reason for each
Insider data: [N transactions found / NO_DATA]
Transcripts: [verbatim / structured_summary / UNAVAILABLE] from [sources]
8-K material events: [list or "none"]
```

Append to `bugs_encountered.md`: if Phase 0 had no warnings beyond the standard, append `[Phase 0] OK`. Otherwise it already has warnings from steps above.

## Step 0.11 — Instruct the user

Output exactly:

```
==================================================
PHASE 0 COMPLETE -- [COMPANY NAME] ({TICKER})
==================================================

Files saved to: {BASE}/raw/

  [done] 10k_raw.txt          ([truncated at N chars / full])
  [done] 10k_xbrl.json        (XBRL financial facts)
  [done] xbrl_summary.txt     ([N rows; SHARES_JUMP: N/none])
  [done] 10q_raw.txt
  [done] proxy_raw.txt
  [done] competitors_raw.txt  ([COMP1], [COMP2] — with XBRL)
  [done] insider_raw.txt      ([N transactions])
  [done] transcripts_raw.txt  ([verbatim / structured_summary / unavailable])
  [done] recent_8k.txt        ([N filings; M material events flagged])
  [done] phase0_log.txt
  [done] bugs_encountered.md  ([N warnings])

==================================================
NEXT -> Switch to your Codex terminal and run:

  $stock-research-codex {TICKER} --audit

(Note the `$` prefix — Codex activation syntax is `$`, not `/`.)

This is the Phase 0 audit gate. Codex spot-checks the raw files
before either model summarizes them. If audit finds CRITICAL issues,
fix and re-run Phase 0 first.

After audit passes, run the all-in-one Codex Step 1A command for compact issuers:

  $stock-research-codex {TICKER}

For large or context-risk issuers, use the resumable Step 1A path instead:

  $stock-research-codex {TICKER} --step1a-10k

Then follow Codex's substep handoffs through `--step1a-status`.
Codex will read the raw files and write independent summaries (Step 1A).
When done, return here and run:

  /stock-research {TICKER} --step1b

→ /clear before running the next flag (preserves your context window).
==================================================
```

Stop here.
