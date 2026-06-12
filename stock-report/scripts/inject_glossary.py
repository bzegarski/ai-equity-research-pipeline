"""Glossary auto-injection.

Wraps the first occurrence of each glossary term in an HTML section with a
hover-tooltip span, per the CSS-only popover defined in templates/report.html:

    <span class="gloss" tabindex="0"
          data-term="Free cash flow"
          data-def="The cash a company has left after operating costs, taxes, and capex...">FCF</span>

Subsequent occurrences in the same section get `class="gloss repeat"` so the
underline only appears on the first hit (avoids visual noise).

Term sources, in priority order (later sources override earlier on key collision):
  1. assets/glossary_core.json          - cross-cutting finance terms
  2. assets/sectors/<sector>_primer.md  - sector-specific terms (parsed)
  3. _report_drafts/glossary_company.json - per-ticker terms (Claude builds)

The injector skips text inside <a>, <code>, <pre>, <h1>-<h6>, <script>, <style>,
<svg>, and existing <span class="gloss">...</span> blocks. Stdlib-only.
"""
from __future__ import annotations

import json
import re
from html import escape as _esc
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
GLOSSARY_CORE_PATH = SKILL_DIR / "assets" / "glossary_core.json"
SECTORS_DIR = SKILL_DIR / "assets" / "sectors"

# Cache: keyed by (sector_name, company_glossary_path) so the regex builds once
# per section's call when the same arguments are passed.
_TERM_CACHE: dict[tuple, tuple[dict, re.Pattern | None]] = {}


def _load_core_terms() -> list[dict]:
    if not GLOSSARY_CORE_PATH.exists():
        return []
    data = json.loads(GLOSSARY_CORE_PATH.read_text(encoding="utf-8"))
    return data.get("terms", [])


def _load_sector_terms(sector: str | None) -> list[dict]:
    """Pull glossary entries from a sector primer's `## Sector jargon dictionary`
    section. Each entry is `**TERM** — definition` style."""
    if not sector:
        return []
    primer_path = SECTORS_DIR / f"{sector.replace(' ', '_')}_primer.md"
    if not primer_path.exists():
        return []
    text = primer_path.read_text(encoding="utf-8")

    sec_re = re.compile(
        r"(?:^|\n)#{1,4}\s+(?:Sector jargon dictionary|Jargon dictionary)[^\n]*\n(.+?)(?=\n#{1,4}\s|\Z)",
        re.IGNORECASE | re.DOTALL,
    )
    m = sec_re.search(text)
    if not m:
        return []
    body = m.group(1)
    out = []
    # Match `**TERM**` or `**TERM (ABBR)**` followed by - or — then definition.
    line_re = re.compile(r"\*\*([^*]+?)\*\*\s*[-–—:]\s*([^\n*][^\n]*)")
    for line_m in line_re.finditer(body):
        term = line_m.group(1).strip()
        definition = line_m.group(2).strip()
        # If term has a parenthetical abbreviation, add it as an alternate match.
        match_strings = [term]
        abbrev_m = re.search(r"\(([A-Z0-9]{2,8})\)", term)
        if abbrev_m:
            match_strings.append(abbrev_m.group(1))
            # Strip the parenthetical from the canonical
            term = re.sub(r"\s*\([^)]+\)\s*", "", term).strip()
        out.append({
            "term": term,
            "match": match_strings,
            "definition": definition,
            "source": f"sector:{sector}",
        })
    return out


def _load_company_terms(company_glossary_path: Path | None) -> list[dict]:
    if company_glossary_path is None or not company_glossary_path.exists():
        return []
    try:
        data = json.loads(company_glossary_path.read_text(encoding="utf-8"))
    except Exception:
        return []
    if isinstance(data, dict) and "terms" in data:
        entries = data["terms"]
    elif isinstance(data, list):
        entries = data
    else:
        return []
    out = []
    for e in entries:
        if not isinstance(e, dict):
            continue
        term = e.get("term") or e.get("name")
        definition = e.get("definition") or e.get("def") or ""
        if not term or not definition:
            continue
        match = e.get("match") or [term]
        if isinstance(match, str):
            match = [match]
        out.append({
            "term": term,
            "match": match,
            "definition": definition,
            "source": "company",
        })
    return out


def _build_index(sector: str | None,
                 company_glossary_path: Path | None
                 ) -> tuple[dict, re.Pattern | None]:
    """Returns (lookup_dict, compiled_pattern). lookup_dict keys are lowercased
    match strings; values are dicts with canonical_term, definition."""
    cache_key = (sector or "", str(company_glossary_path) if company_glossary_path else "")
    if cache_key in _TERM_CACHE:
        return _TERM_CACHE[cache_key]

    entries: list[dict] = []
    entries.extend(_load_core_terms())
    entries.extend(_load_sector_terms(sector))
    entries.extend(_load_company_terms(company_glossary_path))

    lookup: dict[str, dict] = {}
    for e in entries:
        term = e["term"]
        definition = e["definition"]
        for m in e.get("match") or [term]:
            key = m.lower()
            # Don't overwrite a more-specific (later) term with a generic one.
            # Later entries (sector, company) DO override core; that's by design.
            lookup[key] = {"term": term, "definition": definition,
                           "source": e.get("source", "core")}

    if not lookup:
        result = ({}, None)
        _TERM_CACHE[cache_key] = result
        return result

    # Build alternation regex; sort by length DESC so longer phrases win over
    # shorter substrings ("net revenue retention" > "NRR" if both match a string).
    matches_sorted = sorted(lookup.keys(), key=lambda x: (-len(x), x))
    alternation = "|".join(re.escape(m) for m in matches_sorted)
    # Word boundary on either side. Use lookarounds so we don't gobble adjacent
    # punctuation. Treat / and - and . as boundaries inside terms (e.g. "P/E ratio"
    # and "10-K" need their internal punctuation preserved while still matching
    # at word boundaries).
    pattern = re.compile(
        rf"(?<![A-Za-z0-9])(?:{alternation})(?![A-Za-z0-9])",
        re.IGNORECASE,
    )

    result = (lookup, pattern)
    _TERM_CACHE[cache_key] = result
    return result


# ---------- HTML walking ----------

# A single regex that, in priority order, matches:
#   - a paired skip element (opening tag + content + closing tag)
#   - a paired existing gloss span (so we don't double-wrap)
#   - any other single HTML tag (which we keep but treat as transparent)
# Anything not matched is plain text we are allowed to glossarize.
_SKIP_RE = re.compile(
    r"<a\b[^>]*>.*?</a>"
    r"|<code\b[^>]*>.*?</code>"
    r"|<pre\b[^>]*>.*?</pre>"
    r"|<h[1-6]\b[^>]*>.*?</h[1-6]>"
    r"|<script\b[^>]*>.*?</script>"
    r"|<style\b[^>]*>.*?</style>"
    r"|<svg\b[^>]*>.*?</svg>"
    r"|<span\b[^>]*\bclass=\"[^\"]*\bgloss\b[^\"]*\"[^>]*>.*?</span>"
    r"|<[^>]+>",
    re.DOTALL | re.IGNORECASE,
)


def inject(html_text: str,
           scope_id: str | None = None,
           sector: str | None = None,
           company_glossary_path: Path | None = None) -> str:
    """Wrap glossary terms in `html_text` with hover-tooltip spans.

    Args:
        html_text: HTML for one section. First occurrence of each canonical term
                   gets `<span class="gloss">`; subsequent occurrences get `.gloss.repeat`.
        scope_id:  Section anchor (logged via the `data-scope` attribute on each
                   wrap, useful when debugging which section a term first showed up).
        sector:    GICS-11 sector name; loads `assets/sectors/<sector>_primer.md`
                   to extract its jargon dictionary.
        company_glossary_path: Path to per-ticker `glossary_company.json`.

    Returns the HTML with glossary spans inserted. Idempotent: HTML already
    containing `<span class="gloss">` zones is preserved untouched.
    """
    if not html_text:
        return html_text
    lookup, pattern = _build_index(sector, company_glossary_path)
    if pattern is None:
        return html_text

    seen_canonical: set[str] = set()

    parts = []
    last = 0
    for m in _SKIP_RE.finditer(html_text):
        if m.start() > last:
            parts.append(("text", html_text[last:m.start()]))
        parts.append(("skip", m.group(0)))
        last = m.end()
    if last < len(html_text):
        parts.append(("text", html_text[last:]))

    out = []
    for kind, content in parts:
        if kind == "skip":
            out.append(content)
            continue
        out.append(_apply(content, pattern, lookup, seen_canonical, scope_id))
    return "".join(out)


def _apply(text: str,
           pattern: re.Pattern,
           lookup: dict,
           seen: set,
           scope_id: str | None) -> str:
    """Run the glossary pattern across one safe-text segment and wrap matches."""
    def replace(m: re.Match) -> str:
        match_text = m.group(0)
        entry = lookup.get(match_text.lower())
        if entry is None:
            return match_text
        canonical = entry["term"]
        definition = entry["definition"]
        is_repeat = canonical in seen
        seen.add(canonical)
        cls = "gloss repeat" if is_repeat else "gloss"
        scope_attr = f' data-scope="{_esc(scope_id, quote=True)}"' if scope_id else ""
        return (
            f'<span class="{cls}" tabindex="0"'
            f'{scope_attr}'
            f' data-term="{_esc(canonical, quote=True)}"'
            f' data-def="{_esc(definition, quote=True)}">{match_text}</span>'
        )

    return pattern.sub(replace, text)


# ---------- diagnostic / CLI ----------

def stats(sector: str | None = None,
          company_glossary_path: Path | None = None) -> dict:
    """Report what's loaded — useful for debugging which sector primer terms
    actually got picked up."""
    lookup, pattern = _build_index(sector, company_glossary_path)
    by_source: dict[str, int] = {}
    for v in lookup.values():
        by_source[v["source"]] = by_source.get(v["source"], 0) + 1
    return {
        "match_strings": len(lookup),
        "unique_canonical_terms": len({v["term"] for v in lookup.values()}),
        "by_source": by_source,
        "pattern_compiled": pattern is not None,
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Inject glossary spans into HTML or report stats."
    )
    parser.add_argument("--sector", default=None,
                        help="GICS sector name (loads matching primer)")
    parser.add_argument("--company-glossary", default=None,
                        help="Path to per-company glossary JSON")
    parser.add_argument("--stats", action="store_true",
                        help="Print loaded-term stats and exit")
    parser.add_argument("--input", default=None,
                        help="HTML file to process (otherwise stdin)")
    args = parser.parse_args()

    company_path = Path(args.company_glossary) if args.company_glossary else None

    if args.stats:
        print(json.dumps(stats(args.sector, company_path), indent=2))
    else:
        if args.input:
            html = Path(args.input).read_text(encoding="utf-8")
        else:
            import sys
            html = sys.stdin.read()
        print(inject(html, sector=args.sector, company_glossary_path=company_path))
