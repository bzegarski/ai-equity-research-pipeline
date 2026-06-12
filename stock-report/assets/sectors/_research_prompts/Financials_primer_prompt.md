# Financials — Sector Primer Research Prompt

**How to use this file.** Run the prompt below in Claude.ai's Research mode. Save the result as `assets/sectors/Financials_primer.md`. The /stock-report skill loads it when a ticker is detected as Financials and either weaves its concepts into the company write-up or links the reader to it via `→ Learn more`.

---

## The prompt (copy-paste into Claude.ai's Research mode)

```
What does an individual long-term investor in the Buffett / Graham / Fisher / Munger / Marks tradition need to know about the FINANCIALS sector to read a single-company writeup intelligently and to ask the right questions when studying any business in this sector?

Who I am. A long-term individual investor, not a professional analyst. I read company writeups across every GICS sector, and I am green on most of them. The reading list shaping the writing I want is The Essays of Warren Buffett (Cunningham), Poor Charlie's Almanack, Common Stocks and Uncommon Profits (Fisher), The Warren Buffett Way (Hagstrom), The Investment Checklist (Shearn), Security Analysis (Graham & Dodd), The Most Important Thing (Marks). These books teach by anchoring abstractions to concrete businesses. I want a sector primer that does the same.

What I want from a primer. After reading it, I should have intuition for how a Financials business actually works — but Financials is genuinely several different industries, and the primer should teach each engine separately. Banks make money on net interest margin and credit spreads. Insurers make money on the underwriting result plus the float. Asset managers make money on AUM-based fees. Exchanges make money on transaction take-rates and data subscriptions. Each has a different set of metrics, a different cycle exposure, and a different moat shape.

What to attend to particularly for Financials. This sector is the wisdom tradition's deepest territory. Buffett has written about it more than any other sector across sixty years of letters, and the canonical lessons are nearly all here.

(a) Banks. Net interest margin (NIM = the spread between interest income and interest expense), efficiency ratio (operating expenses / revenue), credit cycle behavior (NPL ratios, loss provisions, charge-offs through the cycle), regulatory capital (CET1, Tier 1 leverage). Buffett's Wells Fargo position from 1990 through 2020, his American Express position from 1964 / 1991 to today, his Bank of America purchase 2011, the M&T Bank position, the U.S. Bancorp position — pull from these letters in detail. The 1990 letter on Wells Fargo, the 1991 letter on American Express, and the 2011 letter on Bank of America are the canonical Buffett bank writings.

(b) Insurance. The single most important concept the wisdom tradition has produced in financials: float — premiums collected before claims are paid, which the insurer can invest and earn a return on, effectively at no cost (or at a cost equal to the underwriting loss if the company is undisciplined). Buffett has written about this in nearly every annual letter from 1980 onward; the GEICO 1976 internal memo, the 1996 letter on GEICO's distribution-cost moat, and the dozens of later letters on the float as Berkshire's "interest-free leverage" are the canonical primer. Combined ratio = (losses + expenses) / earned premiums; below 100 means underwriting profit. Marks's Oaktree memos on cycles apply directly to insurance pricing.

(c) Asset managers and broker-dealers. AUM-based fees (sticky), assets-under-administration (also sticky), trading commissions (cyclical), 12b-1 fees, ETF expense ratios. Distribution moats — independent broker-dealers, RIA channels, retirement-plan placement.

(d) Exchanges and financial-data businesses. CME, ICE, Nasdaq, Cboe, S&P Global, Moody's, MSCI. The wisdom tradition treats these as the highest-quality businesses in the sector — network-effect / coordination moats, near-zero capital intensity, recurring data subscription revenue. Buffett's recent commentary on Moody's specifically and on financial-data oligopolies broadly is worth pulling.

(e) Consumer finance and payments. American Express (Buffett's longest-held position, 1964 / 1991 / present), Capital One, Discover. Visa and Mastercard sit in IT under GICS but their economics belong here.

(f) Howard Marks. Oaktree is fundamentally a credit / distressed-debt business; The Most Important Thing and the Oaktree memos engage Financials more deeply than any other wisdom-tradition writer's work. The 2007 "Risk" memo, the 2008 cycle memos ("It's All Good"; "The Limits to Negativism"), and the 2009 "The Long View" are the canonical writings on financial-cycle behavior.

The structure I want. Open with the recognition that Financials is several engines under one GICS label, and frame the primer around them. For each engine, the unit economics, the metrics that matter, the moat shape, and the cycle. Use Buffett's worked examples generously (Wells Fargo 1990; AmEx 1991; GEICO 1996; BofA 2011; the float-as-interest-free-leverage doctrine). Then the typical risks specific to Financials — credit cycles, regulatory cycles, interest-rate cycles, leverage-induced fragility (the 2008 lesson), specific incentive-misalignment patterns Munger has flagged. Then recurring historical patterns (1907, 1929, 1973, 1990, 2000, 2008, 2020 — financials lead and lag the cycle in specific ways). Then the GICS sub-industries with one paragraph each: Banks, Capital Markets, Consumer Finance, Diversified Financial Services, Financial Exchanges, Insurance (P&C, life, reinsurance — different economics), Mortgage Real Estate Investment Trusts.

Style I love. Concrete subjects acting on concrete objects. One specific testable example per abstract claim. Well-chosen historical analogs (Buffett on See's; Marks on 2007–08). Plain English ahead of jargon, jargon defined inline on first use. Sentence rhythm. The small earned surprise.

Style I reject. Institutional sell-side templates (target prices, CAPM, beta-driven discount rates). Generic macro framing. Formulaic SWOT and pasted Porter five-forces. Numbers without narrative. Throat-clearing prose. ESG ratings imported from third-party scorers without engaging what they mean for the unit economics.

Source preferences. Buffett's letters on financial businesses (Wells Fargo 1990; AmEx 1991, 1995; GEICO 1976 memo, 1995, 1996, 2010s; Bank of America 2011; the multi-decade float discussions; Moody's recent commentary). Howard Marks's Oaktree memos (especially 2007 "Risk," the 2008 series, 2009 "The Long View," 2014 "Risk Revisited"). The Federal Reserve's FEDS Notes for plain-English research on banking mechanics. The FDIC Quarterly Banking Profile. The Bank for International Settlements (Basel framework primers). The NAIC for insurance regulatory data. Damodaran's bank, insurance, and asset-management sector data. Pat Dorsey's Little Book chapters on Financials moats. The S&P / Moody's annual default and recovery studies for credit-cycle base rates.

Length: 6,000–8,000 words (Financials earns the most length because the wisdom-tradition input is deepest and the engines most distinct). Organize however best serves the answer.

Note: this is research about how to think about Financials businesses in general. Don't analyze any specific company as an investment.
```
