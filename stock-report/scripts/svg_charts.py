"""Hand-rolled SVG chart generators. Stdlib only.

All functions return either:
  - a bare <svg>...</svg> string when no caption is given, or
  - a <figure><svg>...</svg><figcaption>...</figcaption></figure> string when a
    caption is supplied. The /stock-report template styles both forms.

No matplotlib dependency. Captions carry the takeaway sentence ("Operating margin
held at 45% — the legacy software franchise") and are written by Claude as part
of the per-section drafting pass; Python just slots them in.
"""
from __future__ import annotations

import html as _html
import math
from typing import Sequence


PALETTE = ["#1f5fb4", "#a83232", "#1f7a3a", "#b35a00", "#5a3aa8", "#7a5a3a", "#3a7a8a", "#7a3a5a"]
NEG_COLOR = "#a83232"


# ---------- helpers ----------

def _format_value(v: float) -> str:
    if v is None:
        return ""
    av = abs(v)
    if av >= 1_000_000_000_000:
        return f"{v / 1_000_000_000_000:.1f}T"
    if av >= 1_000_000_000:
        return f"{v / 1_000_000_000:.1f}B"
    if av >= 1_000_000:
        return f"{v / 1_000_000:.1f}M"
    if av >= 1_000:
        return f"{v / 1_000:.1f}K"
    if av >= 10:
        return f"{v:.0f}"
    return f"{v:.2f}"


def _wrap(svg: str, caption: str | None) -> str:
    if not caption:
        return svg
    return f'<figure>{svg}<figcaption>{_html.escape(caption)}</figcaption></figure>'


def _svg_open(width: int, height: int, title: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'role="img" aria-label="{_html.escape(title)}" '
        f'style="font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif; '
        f'font-size: 11px;">'
        f'<title>{_html.escape(title)}</title>'
    )


def _heat_color(t: float, palette: str = "blue") -> str:
    """t in [0,1]; returns hex color along a single-hue ramp."""
    t = max(0.0, min(1.0, t))
    if palette == "blue":
        # white → deep blue
        r = int(round(247 - (247 - 31) * t))
        g = int(round(251 - (251 - 95) * t))
        b = int(round(255 - (255 - 180) * t))
    elif palette == "red":
        r = int(round(253 - (253 - 168) * t))
        g = int(round(243 - (243 - 50) * t))
        b = int(round(243 - (243 - 50) * t))
    elif palette == "green":
        r = int(round(243 - (243 - 31) * t))
        g = int(round(251 - (251 - 122) * t))
        b = int(round(243 - (243 - 58) * t))
    else:
        r = int(round(247 - (247 - 60) * t))
        g = int(round(247 - (247 - 60) * t))
        b = int(round(247 - (247 - 60) * t))
    return f"#{r:02x}{g:02x}{b:02x}"


def _format_value(v: float) -> str:
    if v is None:
        return ""
    av = abs(v)
    if av >= 1_000_000_000:
        return f"{v / 1_000_000_000:.1f}B"
    if av >= 1_000_000:
        return f"{v / 1_000_000:.1f}M"
    if av >= 1_000:
        return f"{v / 1_000:.1f}K"
    if av >= 10:
        return f"{v:.0f}"
    return f"{v:.2f}"


def line_chart(
    title: str,
    x_labels: Sequence[str],
    series: dict,
    ylabel: str = "",
    width: int = 640,
    height: int = 320,
    caption: str | None = None,
) -> str:
    """series: dict of {label: [values]}; values aligned to x_labels."""
    if not x_labels or not series:
        return _wrap(_empty(title, width, height, "No data"), caption)

    margin_left = 60
    margin_right = 130
    margin_top = 40
    margin_bottom = 50
    plot_w = width - margin_left - margin_right
    plot_h = height - margin_top - margin_bottom

    all_vals = [v for vs in series.values() for v in vs if v is not None]
    if not all_vals:
        return _wrap(_empty(title, width, height, "No numeric data"), caption)
    vmin = min(all_vals)
    vmax = max(all_vals)
    if vmin == vmax:
        vmin -= 1
        vmax += 1
    if vmin > 0 and vmin / vmax < 0.4:
        vmin = 0
    span = vmax - vmin

    n = len(x_labels)
    if n == 1:
        x_step = 0
    else:
        x_step = plot_w / (n - 1)

    def x_of(i):
        return margin_left + i * x_step

    def y_of(v):
        return margin_top + plot_h - (v - vmin) / span * plot_h

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'role="img" aria-label="{_html.escape(title)}" '
        f'style="font-family: system-ui, -apple-system, Segoe UI, sans-serif; font-size: 11px;">',
        f'<title>{_html.escape(title)}</title>',
        f'<text x="{margin_left}" y="20" font-size="13" font-weight="600">{_html.escape(title)}</text>',
    ]

    # Y-axis gridlines (4)
    for i in range(5):
        gv = vmin + span * i / 4
        gy = y_of(gv)
        out.append(
            f'<line x1="{margin_left}" x2="{margin_left + plot_w}" y1="{gy:.1f}" y2="{gy:.1f}" '
            f'stroke="#e6e6e6" stroke-width="1"/>'
        )
        out.append(
            f'<text x="{margin_left - 6}" y="{gy + 3:.1f}" text-anchor="end" fill="#666">'
            f'{_format_value(gv)}</text>'
        )

    # X-axis labels
    for i, lbl in enumerate(x_labels):
        out.append(
            f'<text x="{x_of(i):.1f}" y="{margin_top + plot_h + 18}" '
            f'text-anchor="middle" fill="#666">{_html.escape(str(lbl))}</text>'
        )

    # Series lines
    for idx, (label, vals) in enumerate(series.items()):
        color = PALETTE[idx % len(PALETTE)]
        pts = []
        for i, v in enumerate(vals):
            if v is None:
                continue
            pts.append(f"{x_of(i):.1f},{y_of(v):.1f}")
        if pts:
            out.append(
                f'<polyline points="{" ".join(pts)}" fill="none" '
                f'stroke="{color}" stroke-width="2" stroke-linejoin="round"/>'
            )
        # dots
        for i, v in enumerate(vals):
            if v is None:
                continue
            out.append(
                f'<circle cx="{x_of(i):.1f}" cy="{y_of(v):.1f}" r="3" fill="{color}"/>'
            )

    # Legend
    legend_y = margin_top + 4
    for idx, label in enumerate(series.keys()):
        color = PALETTE[idx % len(PALETTE)]
        ly = legend_y + idx * 18
        out.append(
            f'<rect x="{margin_left + plot_w + 14}" y="{ly}" width="10" height="10" fill="{color}"/>'
        )
        out.append(
            f'<text x="{margin_left + plot_w + 28}" y="{ly + 9}" fill="#333">'
            f'{_html.escape(label)}</text>'
        )

    if ylabel:
        out.append(
            f'<text x="{margin_left - 45}" y="{margin_top + plot_h / 2}" '
            f'text-anchor="middle" fill="#666" '
            f'transform="rotate(-90 {margin_left - 45} {margin_top + plot_h / 2})">'
            f'{_html.escape(ylabel)}</text>'
        )

    out.append('</svg>')
    return _wrap("".join(out), caption)


def bar_chart(
    title: str,
    x_labels: Sequence[str],
    values: Sequence[float],
    ylabel: str = "",
    width: int = 640,
    height: int = 320,
    caption: str | None = None,
) -> str:
    if not x_labels or not values:
        return _wrap(_empty(title, width, height, "No data"), caption)

    margin_left = 60
    margin_right = 30
    margin_top = 40
    margin_bottom = 50
    plot_w = width - margin_left - margin_right
    plot_h = height - margin_top - margin_bottom

    vals = [v if v is not None else 0 for v in values]
    vmax = max(vals) if vals else 1
    vmin = min(vals + [0])
    if vmax == vmin:
        vmax = vmin + 1
    span = vmax - vmin
    bar_gap = 0.25
    n = len(values)
    bar_w = plot_w / n * (1 - bar_gap)
    slot_w = plot_w / n

    def x_of(i):
        return margin_left + i * slot_w + (slot_w - bar_w) / 2

    def y_of(v):
        return margin_top + plot_h - (v - vmin) / span * plot_h

    zero_y = y_of(0) if vmin <= 0 <= vmax else margin_top + plot_h

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'role="img" aria-label="{_html.escape(title)}" '
        f'style="font-family: system-ui, -apple-system, Segoe UI, sans-serif; font-size: 11px;">',
        f'<title>{_html.escape(title)}</title>',
        f'<text x="{margin_left}" y="20" font-size="13" font-weight="600">{_html.escape(title)}</text>',
    ]

    for i in range(5):
        gv = vmin + span * i / 4
        gy = y_of(gv)
        out.append(
            f'<line x1="{margin_left}" x2="{margin_left + plot_w}" y1="{gy:.1f}" y2="{gy:.1f}" '
            f'stroke="#e6e6e6" stroke-width="1"/>'
        )
        out.append(
            f'<text x="{margin_left - 6}" y="{gy + 3:.1f}" text-anchor="end" fill="#666">'
            f'{_format_value(gv)}</text>'
        )

    for i, v in enumerate(vals):
        x = x_of(i)
        y_top = y_of(max(v, 0))
        h = abs(y_of(v) - zero_y)
        color = PALETTE[0] if v >= 0 else PALETTE[1]
        out.append(
            f'<rect x="{x:.1f}" y="{y_top:.1f}" width="{bar_w:.1f}" height="{h:.1f}" '
            f'fill="{color}" opacity="0.85"/>'
        )
        out.append(
            f'<text x="{x + bar_w / 2:.1f}" y="{(y_top - 4) if v >= 0 else (y_top + h + 12):.1f}" '
            f'text-anchor="middle" fill="#444" font-size="10">{_format_value(v)}</text>'
        )

    for i, lbl in enumerate(x_labels):
        out.append(
            f'<text x="{x_of(i) + bar_w / 2:.1f}" y="{margin_top + plot_h + 18}" '
            f'text-anchor="middle" fill="#666">{_html.escape(str(lbl))}</text>'
        )

    if ylabel:
        out.append(
            f'<text x="{margin_left - 45}" y="{margin_top + plot_h / 2}" '
            f'text-anchor="middle" fill="#666" '
            f'transform="rotate(-90 {margin_left - 45} {margin_top + plot_h / 2})">'
            f'{_html.escape(ylabel)}</text>'
        )

    out.append('</svg>')
    return _wrap("".join(out), caption)


# ---------- new chart types ----------

def donut_chart(
    title: str,
    segments: Sequence[tuple],  # [(label, value, optional color)]
    width: int = 640,
    height: int = 360,
    inner_ratio: float = 0.55,
    caption: str | None = None,
) -> str:
    """Pie with hollow center. Segments listed largest first by convention.
    Used for revenue-by-segment in Section 2 (Business)."""
    cleaned = [(s[0], float(s[1]), s[2] if len(s) > 2 else None)
               for s in segments if s[1] is not None and s[1] > 0]
    if not cleaned:
        return _wrap(_empty(title, width, height, "No segments"), caption)

    total = sum(v for _, v, _ in cleaned)
    if total <= 0:
        return _wrap(_empty(title, width, height, "Zero total"), caption)

    out = [_svg_open(width, height, title)]
    out.append(
        f'<text x="20" y="22" font-size="13" font-weight="600">{_html.escape(title)}</text>'
    )

    cx, cy = 180, 190
    r_outer = 130
    r_inner = r_outer * inner_ratio
    angle_start = -math.pi / 2  # top

    for idx, (label, value, color) in enumerate(cleaned):
        frac = value / total
        angle_end = angle_start + frac * 2 * math.pi
        large_arc = 1 if frac > 0.5 else 0
        x1 = cx + r_outer * math.cos(angle_start)
        y1 = cy + r_outer * math.sin(angle_start)
        x2 = cx + r_outer * math.cos(angle_end)
        y2 = cy + r_outer * math.sin(angle_end)
        x3 = cx + r_inner * math.cos(angle_end)
        y3 = cy + r_inner * math.sin(angle_end)
        x4 = cx + r_inner * math.cos(angle_start)
        y4 = cy + r_inner * math.sin(angle_start)
        col = color or PALETTE[idx % len(PALETTE)]
        path = (
            f"M {x1:.1f},{y1:.1f} "
            f"A {r_outer},{r_outer} 0 {large_arc} 1 {x2:.1f},{y2:.1f} "
            f"L {x3:.1f},{y3:.1f} "
            f"A {r_inner},{r_inner} 0 {large_arc} 0 {x4:.1f},{y4:.1f} Z"
        )
        out.append(
            f'<path d="{path}" fill="{col}" stroke="#fff" stroke-width="2"/>'
        )

        # Label inside slice if frac > 8%
        if frac > 0.08:
            mid = (angle_start + angle_end) / 2
            lr = (r_outer + r_inner) / 2
            lx = cx + lr * math.cos(mid)
            ly = cy + lr * math.sin(mid)
            out.append(
                f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle" '
                f'fill="#fff" font-weight="600" font-size="12" '
                f'dominant-baseline="middle">{frac*100:.0f}%</text>'
            )

        angle_start = angle_end

    # Center label
    out.append(
        f'<text x="{cx}" y="{cy - 6}" text-anchor="middle" font-size="13" '
        f'fill="#444">Total</text>'
    )
    out.append(
        f'<text x="{cx}" y="{cy + 14}" text-anchor="middle" font-size="15" '
        f'font-weight="600">{_format_value(total)}</text>'
    )

    # Legend
    legend_x = 360
    legend_y = 60
    out.append(
        f'<text x="{legend_x}" y="{legend_y - 14}" font-size="12" '
        f'fill="#444" font-weight="600">Segments</text>'
    )
    for idx, (label, value, color) in enumerate(cleaned):
        col = color or PALETTE[idx % len(PALETTE)]
        ly = legend_y + idx * 24
        out.append(
            f'<rect x="{legend_x}" y="{ly}" width="14" height="14" fill="{col}"/>'
        )
        pct = value / total * 100
        out.append(
            f'<text x="{legend_x + 22}" y="{ly + 11}" fill="#222" font-size="12">'
            f'{_html.escape(label)} '
            f'<tspan fill="#666">— {_format_value(value)} ({pct:.0f}%)</tspan></text>'
        )

    out.append('</svg>')
    return _wrap("".join(out), caption)


def horizontal_bar_chart(
    title: str,
    segments: Sequence[tuple],  # [(label, value, optional color)]
    width: int = 640,
    height: int = 320,
    show_values: bool = True,
    caption: str | None = None,
) -> str:
    """Horizontal bars sized proportionally to values. Used for the
    `$1 of revenue → free cash flow` walk in Section 2 (Business)."""
    cleaned = [(s[0], float(s[1]), s[2] if len(s) > 2 else None) for s in segments]
    if not cleaned:
        return _wrap(_empty(title, width, height, "No data"), caption)

    margin_left = 160
    margin_right = 40
    margin_top = 40
    margin_bottom = 30
    plot_w = width - margin_left - margin_right
    plot_h = height - margin_top - margin_bottom

    vmax = max(abs(v) for _, v, _ in cleaned)
    if vmax == 0:
        vmax = 1
    n = len(cleaned)
    row_h = plot_h / n
    bar_h = row_h * 0.62

    out = [_svg_open(width, height, title)]
    out.append(
        f'<text x="20" y="22" font-size="13" font-weight="600">{_html.escape(title)}</text>'
    )

    for i, (label, value, color) in enumerate(cleaned):
        y = margin_top + i * row_h + (row_h - bar_h) / 2
        bar_w = (abs(value) / vmax) * plot_w
        col = color or (PALETTE[i % len(PALETTE)] if value >= 0 else NEG_COLOR)
        out.append(
            f'<rect x="{margin_left}" y="{y:.1f}" width="{bar_w:.1f}" '
            f'height="{bar_h:.1f}" fill="{col}" opacity="0.88"/>'
        )
        out.append(
            f'<text x="{margin_left - 8}" y="{y + bar_h / 2:.1f}" text-anchor="end" '
            f'dominant-baseline="middle" fill="#222" font-size="12">{_html.escape(label)}</text>'
        )
        if show_values:
            out.append(
                f'<text x="{margin_left + bar_w + 6:.1f}" y="{y + bar_h / 2:.1f}" '
                f'dominant-baseline="middle" fill="#444" font-size="11">'
                f'{_format_value(value)}</text>'
            )

    out.append('</svg>')
    return _wrap("".join(out), caption)


def paired_bar_chart(
    title: str,
    x_labels: Sequence[str],
    series: dict,  # {label: [values]} — exactly two series typical
    ylabel: str = "",
    width: int = 640,
    height: int = 320,
    caption: str | None = None,
) -> str:
    """Two-series bar chart, side-by-side per x position. Used for FCF vs capex
    in Section 4 (the numbers)."""
    if not x_labels or not series:
        return _wrap(_empty(title, width, height, "No data"), caption)

    margin_left = 60
    margin_right = 130
    margin_top = 40
    margin_bottom = 50
    plot_w = width - margin_left - margin_right
    plot_h = height - margin_top - margin_bottom

    all_vals = [v for vs in series.values() for v in vs if v is not None]
    if not all_vals:
        return _wrap(_empty(title, width, height, "No numeric data"), caption)
    vmax = max(all_vals + [0])
    vmin = min(all_vals + [0])
    if vmax == vmin:
        vmax = vmin + 1
    span = vmax - vmin

    n = len(x_labels)
    k = len(series)
    slot_w = plot_w / n
    bar_gap = 0.18
    bar_w = (slot_w * (1 - bar_gap)) / k

    def y_of(v):
        return margin_top + plot_h - (v - vmin) / span * plot_h

    zero_y = y_of(0) if vmin <= 0 <= vmax else margin_top + plot_h

    out = [_svg_open(width, height, title)]
    out.append(
        f'<text x="{margin_left}" y="20" font-size="13" font-weight="600">'
        f'{_html.escape(title)}</text>'
    )

    for i in range(5):
        gv = vmin + span * i / 4
        gy = y_of(gv)
        out.append(
            f'<line x1="{margin_left}" x2="{margin_left + plot_w}" '
            f'y1="{gy:.1f}" y2="{gy:.1f}" stroke="#e6e6e6" stroke-width="1"/>'
        )
        out.append(
            f'<text x="{margin_left - 6}" y="{gy + 3:.1f}" text-anchor="end" '
            f'fill="#666">{_format_value(gv)}</text>'
        )

    for series_idx, (label, vals) in enumerate(series.items()):
        color = PALETTE[series_idx % len(PALETTE)]
        for i, v in enumerate(vals):
            if v is None:
                continue
            slot_left = margin_left + i * slot_w + (slot_w * bar_gap / 2)
            x = slot_left + series_idx * bar_w
            y_top = y_of(max(v, 0))
            h = abs(y_of(v) - zero_y)
            out.append(
                f'<rect x="{x:.1f}" y="{y_top:.1f}" width="{bar_w * 0.95:.1f}" '
                f'height="{h:.1f}" fill="{color}" opacity="0.9"/>'
            )

    for i, lbl in enumerate(x_labels):
        out.append(
            f'<text x="{margin_left + (i + 0.5) * slot_w:.1f}" '
            f'y="{margin_top + plot_h + 18}" text-anchor="middle" fill="#666">'
            f'{_html.escape(str(lbl))}</text>'
        )

    legend_y = margin_top + 4
    for series_idx, label in enumerate(series.keys()):
        color = PALETTE[series_idx % len(PALETTE)]
        ly = legend_y + series_idx * 18
        out.append(
            f'<rect x="{margin_left + plot_w + 14}" y="{ly}" width="10" '
            f'height="10" fill="{color}"/>'
        )
        out.append(
            f'<text x="{margin_left + plot_w + 28}" y="{ly + 9}" fill="#333">'
            f'{_html.escape(label)}</text>'
        )

    if ylabel:
        out.append(
            f'<text x="{margin_left - 45}" y="{margin_top + plot_h / 2}" '
            f'text-anchor="middle" fill="#666" '
            f'transform="rotate(-90 {margin_left - 45} {margin_top + plot_h / 2})">'
            f'{_html.escape(ylabel)}</text>'
        )

    out.append('</svg>')
    return _wrap("".join(out), caption)


def scatter_chart(
    title: str,
    points: Sequence[tuple],  # [(label, x, y, optional color, optional highlight_bool)]
    xlabel: str = "",
    ylabel: str = "",
    width: int = 640,
    height: int = 360,
    caption: str | None = None,
) -> str:
    """Scatter plot. Used for peer comparison in Section 5
    (e.g. revenue growth × operating margin)."""
    cleaned = []
    for p in points:
        if len(p) < 3 or p[1] is None or p[2] is None:
            continue
        label = p[0]
        x = float(p[1])
        y = float(p[2])
        color = p[3] if len(p) > 3 else None
        highlight = bool(p[4]) if len(p) > 4 else False
        cleaned.append((label, x, y, color, highlight))
    if not cleaned:
        return _wrap(_empty(title, width, height, "No points"), caption)

    margin_left = 60
    margin_right = 30
    margin_top = 40
    margin_bottom = 60
    plot_w = width - margin_left - margin_right
    plot_h = height - margin_top - margin_bottom

    xs = [p[1] for p in cleaned]
    ys = [p[2] for p in cleaned]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    if xmin == xmax: xmax = xmin + 1
    if ymin == ymax: ymax = ymin + 1
    xpad = (xmax - xmin) * 0.08
    ypad = (ymax - ymin) * 0.08
    xmin -= xpad; xmax += xpad
    ymin -= ypad; ymax += ypad
    xspan = xmax - xmin
    yspan = ymax - ymin

    def x_of(v): return margin_left + (v - xmin) / xspan * plot_w
    def y_of(v): return margin_top + plot_h - (v - ymin) / yspan * plot_h

    out = [_svg_open(width, height, title)]
    out.append(
        f'<text x="{margin_left}" y="20" font-size="13" font-weight="600">'
        f'{_html.escape(title)}</text>'
    )

    # Y gridlines
    for i in range(5):
        gv = ymin + yspan * i / 4
        gy = y_of(gv)
        out.append(
            f'<line x1="{margin_left}" x2="{margin_left + plot_w}" '
            f'y1="{gy:.1f}" y2="{gy:.1f}" stroke="#e6e6e6" stroke-width="1"/>'
        )
        out.append(
            f'<text x="{margin_left - 6}" y="{gy + 3:.1f}" text-anchor="end" '
            f'fill="#666">{_format_value(gv)}</text>'
        )

    # X gridlines / ticks
    for i in range(5):
        gv = xmin + xspan * i / 4
        gx = x_of(gv)
        out.append(
            f'<line x1="{gx:.1f}" x2="{gx:.1f}" '
            f'y1="{margin_top}" y2="{margin_top + plot_h}" '
            f'stroke="#f0f0f0" stroke-width="1"/>'
        )
        out.append(
            f'<text x="{gx:.1f}" y="{margin_top + plot_h + 14}" '
            f'text-anchor="middle" fill="#666">{_format_value(gv)}</text>'
        )

    # Points
    for idx, (label, x, y, color, highlight) in enumerate(cleaned):
        cx, cy = x_of(x), y_of(y)
        col = color or (PALETTE[1] if highlight else PALETTE[0])
        r = 7 if highlight else 5
        out.append(
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{col}" '
            f'stroke="#fff" stroke-width="1.5" opacity="0.92"/>'
        )
        # Label slightly offset
        out.append(
            f'<text x="{cx + r + 4:.1f}" y="{cy + 4:.1f}" fill="#222" '
            f'font-size="11" font-weight="{600 if highlight else 400}">'
            f'{_html.escape(label)}</text>'
        )

    if xlabel:
        out.append(
            f'<text x="{margin_left + plot_w / 2}" y="{height - 12}" '
            f'text-anchor="middle" fill="#444" font-size="12">'
            f'{_html.escape(xlabel)}</text>'
        )
    if ylabel:
        out.append(
            f'<text x="{margin_left - 45}" y="{margin_top + plot_h / 2}" '
            f'text-anchor="middle" fill="#444" font-size="12" '
            f'transform="rotate(-90 {margin_left - 45} {margin_top + plot_h / 2})">'
            f'{_html.escape(ylabel)}</text>'
        )

    out.append('</svg>')
    return _wrap("".join(out), caption)


def heatmap(
    title: str,
    rows: Sequence[str],
    cols: Sequence[str],
    values: Sequence[Sequence[float]],  # rows x cols, in [0,1] or auto-normalized
    palette: str = "blue",
    show_values: bool = True,
    cell_label_format: str = "auto",  # "auto" | "pct" | "raw"
    width: int = 640,
    height: int | None = None,
    caption: str | None = None,
) -> str:
    """Color-graded grid. Used for the moat-rating table in Section 6
    (advantage × strength × durability)."""
    if not rows or not cols or not values:
        return _wrap(_empty(title, width, height or 320, "No data"), caption)
    nr = len(rows)
    nc = len(cols)
    if height is None:
        height = 80 + 38 * nr

    margin_left = 160
    margin_right = 24
    margin_top = 60
    margin_bottom = 24
    plot_w = width - margin_left - margin_right
    plot_h = height - margin_top - margin_bottom
    cell_w = plot_w / nc
    cell_h = plot_h / nr

    flat = [v for row in values for v in row if v is not None]
    if not flat:
        return _wrap(_empty(title, width, height, "No values"), caption)
    raw_min = min(flat)
    raw_max = max(flat)
    span = raw_max - raw_min if raw_max > raw_min else 1.0

    out = [_svg_open(width, height, title)]
    out.append(
        f'<text x="20" y="22" font-size="13" font-weight="600">{_html.escape(title)}</text>'
    )

    # Column headers
    for c, lbl in enumerate(cols):
        cx = margin_left + (c + 0.5) * cell_w
        out.append(
            f'<text x="{cx:.1f}" y="{margin_top - 8}" text-anchor="middle" '
            f'fill="#444" font-size="11" font-weight="600">{_html.escape(lbl)}</text>'
        )

    # Cells + row labels
    for r, row_label in enumerate(rows):
        ry = margin_top + r * cell_h
        out.append(
            f'<text x="{margin_left - 8}" y="{ry + cell_h / 2:.1f}" text-anchor="end" '
            f'dominant-baseline="middle" fill="#222" font-size="11">'
            f'{_html.escape(row_label)}</text>'
        )
        for c, val in enumerate(values[r] if r < len(values) else []):
            cx = margin_left + c * cell_w
            t = (val - raw_min) / span if val is not None else 0
            color = _heat_color(t, palette)
            out.append(
                f'<rect x="{cx:.1f}" y="{ry:.1f}" width="{cell_w:.1f}" '
                f'height="{cell_h:.1f}" fill="{color}" stroke="#fff" stroke-width="1"/>'
            )
            if show_values and val is not None:
                if cell_label_format == "pct":
                    txt = f"{val * 100:.0f}%"
                elif cell_label_format == "raw":
                    txt = f"{val:.2f}"
                else:
                    txt = _format_value(val)
                ink = "#fff" if t > 0.55 else "#1a1a1a"
                out.append(
                    f'<text x="{cx + cell_w / 2:.1f}" y="{ry + cell_h / 2:.1f}" '
                    f'text-anchor="middle" dominant-baseline="middle" '
                    f'fill="{ink}" font-size="11" font-weight="600">{_html.escape(txt)}</text>'
                )

    out.append('</svg>')
    return _wrap("".join(out), caption)


def _empty(title: str, w: int, h: int, msg: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'role="img" style="font-family: system-ui, sans-serif; font-size: 11px;">'
        f'<text x="{w//2}" y="20" text-anchor="middle" font-weight="600">{_html.escape(title)}</text>'
        f'<text x="{w//2}" y="{h//2}" text-anchor="middle" fill="#888">{_html.escape(msg)}</text>'
        f'</svg>'
    )
