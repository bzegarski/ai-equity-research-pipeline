CLAIM LABELING — required on every paragraph of prose output (in step files).
The final memo uses footnote-style sourcing instead — see agents/final_memo.md.

[FACT | source | confidence]
  A specific, source-checkable claim. Source must be named.
  Examples: [FACT | 10-K Item 7 | High]  [FACT | XBRL: us-gaap/Revenues | High]
  Use for: all numbers, dates, ownership status, store counts, tenures,
  geographic splits, auditor names, compensation figures.

[INTERPRETATION | based on: X; Y | confidence]
  A conclusion drawn from facts. Must name the specific facts it rests on.
  Use for: competitive assessments, moat judgments, management quality calls,
  valuation conclusions, industry trend assessments.

[HUMAN-VERIFY | confidence]
  Low confidence, conflicting sources, or a figure derived by inference
  rather than direct citation. The user must check this before relying on it.

Confidence levels:
  High   = two or more independent sources agree, or verified against XBRL
  Medium = single source, or plausible but not independently confirmed
  Low    = inferred, extrapolated, or sources conflict

TRANSCRIPT-DERIVED CLAIMS:
If raw/transcripts_raw.txt has TRANSCRIPT_SOURCE_QUALITY: structured_summary
in its header, every transcript-derived claim must be tagged Medium confidence
at most. Direct quotes should be marked [HUMAN-VERIFY | Medium] because
paraphrasing may have altered exact wording.

No unlabeled prose in step files. Every paragraph opens with one of these labels.
