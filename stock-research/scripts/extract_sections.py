"""Extract Item 1, 1A, 7, 8 sections from a stripped 10-K and write per-section chunks.

Three-layer robustness:
1. Primary: detect "Item N." with strict `find_real_section` rules — must be preceded
   by recent "PART I" header AND followed by non-numeric prose within ~100 chars (i.e.
   it's a section header, not an in-body reference like "see Item 1.").
2. Min-length validation: any section whose extracted slice is <500 bytes is rejected
   as a TOC fragment (MSFT bug: AMZN/GOOGL competitor 10-Ks produced 29-byte chunks).
3. Gap-based fallback (two passes): for any item rejected or not found by strict
   logic, look for the (Item A, Item B) pair separated by >= 5000 chars. The
   xa0/regular-space convention is filer-dependent (PANW: TOC uses xa0, body uses
   regular space; FTNT/CRWD: opposite). Real sections have substantial content
   between them; TOC entries cluster.
4. Sequential rescue (DECK/SNOW pattern): if Item7 is still missing AND Item1A is
   located, take the first Item7 candidate whose offset > Item1A's offset and
   whose following text is alpha-rich. If this lands ahead of a previously-set
   Item8 that was a TOC false-positive, override Item8 too.

Per-section chunks are written to `--chunks-dir` (default: `<input-dir>/_chunks`).
Phase 0 dispatches competitor extractions to `<input-dir>/_chunks_comp/{COMP}/` so
they don't clobber the primary ticker's chunks. Downstream agent prompts that read
`raw/_chunks/` are unchanged.

Optional `--track {10k,fpi,20f}`: with `fpi` or `20f`, switch section labels to
20-F equivalents (Item 4 → Item1; Item 3D → Item1A; Item 5 → Item7; Item 18 →
Item8). The output filenames stay `item1.txt` etc. so downstream prompts are
unchanged. The "PART I" anchor is dropped for FPI track since 20-Fs use a
different document structure.

Usage:
  py scripts/extract_sections.py raw/10k_raw.txt
  py scripts/extract_sections.py raw/10k_raw.txt --chunks-dir raw/_chunks_comp/MDB
  py scripts/extract_sections.py raw/20f_raw.txt --track fpi
"""
import argparse
import os
import re
import sys


SECTIONS_10K = [
    ("Item1", r"Item\s+1\."),
    ("Item1A", r"Item\s+1A\."),
    ("Item7", r"Item\s+7\."),
    ("Item8", r"Item\s+8\."),
]

# 20-F equivalents (FPI track). Output filenames stay "item1.txt" etc. so
# downstream agents that read `raw/_chunks/item1.txt` keep working.
SECTIONS_20F = [
    ("Item1", r"Item\s+4\."),       # 4 — Information on the Company
    ("Item1A", r"Item\s+3\.?D\.?"), # 3.D — Risk Factors
    ("Item7", r"Item\s+5\."),       # 5 — Operating and Financial Review
    ("Item8", r"Item\s+18\."),      # 18 — Financial Statements
]

MIN_SECTION_LENGTH = 500
GAP_FALLBACK_MIN = 5000
TRACK_REQUIRES_PART_ANCHOR = {"10k": True, "fpi": False, "20f": False}


def find_real_section_strict(text, pattern, require_part_anchor=True):
    """Find Item N. occurrence that follows 'PART I' (10-K only) and precedes prose."""
    matches = list(re.finditer(pattern, text, re.IGNORECASE))
    for m in matches:
        start = m.start()
        following = text[m.end():m.end() + 150]
        following_stripped = following.lstrip()
        digits_count = sum(1 for c in following_stripped[:50] if c.isdigit())
        alpha_count = sum(1 for c in following_stripped[:100] if c.isalpha())
        if alpha_count <= 30 or digits_count >= 20:
            continue
        if require_part_anchor:
            preceding = text[max(0, start - 3000):start].upper()
            if "PART I" not in preceding:
                continue
        return start
    return -1


def find_section_pair_by_gap(text, pattern_a, pattern_b, min_gap=GAP_FALLBACK_MIN,
                              after_offset=0):
    """Fallback: find the first (a, b) pair separated by >= min_gap and after_offset."""
    a_positions = [m.start() for m in re.finditer(pattern_a, text, re.IGNORECASE)
                   if m.start() >= after_offset]
    b_positions = [m.start() for m in re.finditer(pattern_b, text, re.IGNORECASE)]
    for a in a_positions:
        for b in b_positions:
            if b > a and (b - a) >= min_gap:
                return a, b
    return -1, -1


def compute_spans(positions, text, order):
    spans = {}
    for i, label in enumerate(order):
        start = positions.get(label, -1)
        if start == -1:
            spans[label] = (-1, -1)
            continue
        next_pos = -1
        for j in range(i + 1, len(order)):
            other = positions.get(order[j], -1)
            if other != -1 and other > start:
                next_pos = other
                break
        end = next_pos if next_pos != -1 else len(text)
        spans[label] = (start, end)
    return spans


def reject_short_sections(positions, spans, order, min_length=MIN_SECTION_LENGTH):
    rejected = []
    for label in order:
        start, end = spans.get(label, (-1, -1))
        if start == -1:
            continue
        if (end - start) < min_length:
            print(
                f"INFO: {label} match at {start} produces span of only {end - start} bytes; "
                f"rejecting as TOC fragment, will retry with gap fallback",
                file=sys.stderr,
            )
            positions[label] = -1
            rejected.append(label)
    return rejected


def run_pair_fallback(positions, text, sections, a_label, b_label):
    """Gap-based fallback. Sets either of (a, b) when -1."""
    if positions.get(a_label, -1) != -1 and positions.get(b_label, -1) != -1:
        return
    a_pat = next(p for l, p in sections if l == a_label)
    b_pat = next(p for l, p in sections if l == b_label)
    a, b = find_section_pair_by_gap(text, a_pat, b_pat)
    if a != -1 and b != -1:
        print(
            f"INFO: gap-based fallback found {a_label} at {a}, {b_label} at {b}",
            file=sys.stderr,
        )
        if positions.get(a_label, -1) == -1:
            positions[a_label] = a
        if positions.get(b_label, -1) == -1:
            positions[b_label] = b


def find_section_after(text, pattern, after_offset, min_alpha=30):
    """Sequential search: first pattern occurrence whose following text is alpha-rich."""
    for m in re.finditer(pattern, text, re.IGNORECASE):
        start = m.start()
        if start <= after_offset:
            continue
        following = text[m.end():m.end() + 150].lstrip()
        alpha = sum(1 for c in following[:100] if c.isalpha())
        digits = sum(1 for c in following[:50] if c.isdigit())
        if alpha >= min_alpha and digits < 20:
            return start
    return -1


def sequential_rescue(positions, text, sections, order):
    """If Item7 still missing after gap-fallback, find first body-prose Item7 after
    Item1A. If that lands ahead of a previously-set Item8 (TOC false-positive),
    override Item8 with the first body-prose Item8 after the new Item7."""
    if positions.get("Item7", -1) != -1:
        return
    item1a_pos = positions.get("Item1A", -1)
    if item1a_pos == -1:
        return
    item7_pat = next(p for l, p in sections if l == "Item7")
    item7_pos = find_section_after(text, item7_pat, after_offset=item1a_pos)
    if item7_pos == -1:
        return
    print(
        f"INFO: sequential rescue placed Item7 at {item7_pos} (after Item1A at {item1a_pos})",
        file=sys.stderr,
    )
    positions["Item7"] = item7_pos

    item8_pos = positions.get("Item8", -1)
    if item8_pos != -1 and item8_pos < item7_pos:
        item8_pat = next(p for l, p in sections if l == "Item8")
        new_item8 = find_section_after(text, item8_pat, after_offset=item7_pos)
        if new_item8 != -1:
            print(
                f"INFO: sequential rescue overrode Item8 from {item8_pos} (TOC) to "
                f"{new_item8} (after Item7 at {item7_pos})",
                file=sys.stderr,
            )
            positions["Item8"] = new_item8


def extract(input_path, chunks_dir=None, track="10k"):
    text = open(input_path, encoding="utf-8").read()
    base_dir = os.path.dirname(input_path)
    if chunks_dir is None:
        chunks_dir = os.path.join(base_dir, "_chunks")
    os.makedirs(chunks_dir, exist_ok=True)

    sections = SECTIONS_20F if track in ("fpi", "20f") else SECTIONS_10K
    require_part = TRACK_REQUIRES_PART_ANCHOR.get(track, True)

    order = ["Item1", "Item1A", "Item7", "Item8"]
    positions = {}
    for label, pattern in sections:
        positions[label] = find_real_section_strict(text, pattern, require_part)

    spans = compute_spans(positions, text, order)
    reject_short_sections(positions, spans, order)

    # First fallback pass.
    run_pair_fallback(positions, text, sections, "Item1", "Item1A")
    run_pair_fallback(positions, text, sections, "Item7", "Item8")

    spans = compute_spans(positions, text, order)
    reject_short_sections(positions, spans, order)

    # Second fallback pass — re-attempt anything still -1.
    run_pair_fallback(positions, text, sections, "Item1", "Item1A")
    run_pair_fallback(positions, text, sections, "Item7", "Item8")

    spans = compute_spans(positions, text, order)
    reject_short_sections(positions, spans, order)

    # Sequential rescue (DECK/SNOW pattern: Item7 TOC false-positive locks Item8
    # at TOC; gap-fallback can't dislodge it because Item8 != -1).
    sequential_rescue(positions, text, sections, order)

    spans = compute_spans(positions, text, order)
    reject_short_sections(positions, spans, order)
    spans = compute_spans(positions, text, order)

    found_labels = []
    extracted_sections = []

    for label in order:
        start, end = spans[label]
        if start == -1:
            print(f"WARNING: {label} not found", file=sys.stderr)
            continue
        section_text = text[start:end]
        extracted_sections.append(section_text)
        found_labels.append(label)

        chunk_path = os.path.join(chunks_dir, f"{label.lower()}.txt")
        open(chunk_path, "w", encoding="utf-8").write(section_text)

    if len(text) > 400000:
        open(input_path, "w", encoding="utf-8").write("\n\n".join(extracted_sections))
        print(
            f"Truncated to key sections (original {len(text)} chars). "
            f"Items found: {found_labels} (chunks_dir={chunks_dir})"
        )
    else:
        print(
            f"Section extraction completed (kept full file, {len(text)} chars). "
            f"Items found: {found_labels} (chunks_dir={chunks_dir})"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_path")
    parser.add_argument("--chunks-dir", default=None)
    parser.add_argument("--track", default="10k", choices=["10k", "fpi", "20f"])
    args = parser.parse_args()
    extract(args.input_path, chunks_dir=args.chunks_dir, track=args.track)
