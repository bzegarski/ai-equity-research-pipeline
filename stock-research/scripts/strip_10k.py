"""Strip HTML from a 10-K, 10-Q, proxy, or competitor filing while preserving paragraph structure.

BUG-2 fix applied: block tags (<p>, <div>, <br>, <li>, <tr>, <h1-6>, blockquote, section,
article) are replaced with newlines BEFORE the generic tag-strip pass. Otherwise the entire
file collapses to a few very long lines and breaks the Read tool on large filings.

Usage:
  py scripts/strip_10k.py <input.htm> <output.txt>
"""
import html
import re
import sys


def strip(input_path, output_path):
    raw = open(input_path, encoding="utf-8", errors="replace").read()

    # Decode HTML entities FIRST (xa0 non-breaking spaces become real chars for later detection)
    raw = html.unescape(raw)

    # Replace block elements with newlines to preserve paragraph structure
    raw = re.sub(
        r"<(?:p|div|br|li|tr|h[1-6]|blockquote|section|article)[^>]*>",
        "\n",
        raw,
        flags=re.IGNORECASE,
    )

    # Strip remaining tags
    text = re.sub(r"<[^>]+>", " ", raw)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    open(output_path, "w", encoding="utf-8").write(text)
    print(f"Characters: {len(text)}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: py scripts/strip_10k.py <input.htm> <output.txt>", file=sys.stderr)
        sys.exit(2)
    strip(sys.argv[1], sys.argv[2])
