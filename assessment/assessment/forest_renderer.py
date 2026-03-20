"""Server-side forest SVG renderer.

Two modes:
  "trees" — analytical grid (X=SAE, Y=EPIAS), categorized view
  "forest" — naturalistic landscape with groves

Mini organism silhouettes are inlined as <symbol> elements (~1KB each),
placed via <use>. Zero additional HTTP requests.
"""

import math
import pathlib
import re

# Per-mode dimensions
FOREST_W, FOREST_H = 1400, 900   # landscape scene — taller
TREES_W, TREES_H = 1000, 600     # compact rows
PAD = 20
ORG_W, ORG_H, ORG_GY = 530, 540, 285
MAX_VISUAL_TREES = 200

_STATIC_DIR = pathlib.Path(__file__).parent.parent / "static"
_SVG_INNER_RE = re.compile(r"<svg[^>]*>(.*)</svg>", re.DOTALL)

SAE_LABELS = [
    ("L0", "Manual"), ("L1", "AI-Assisted"),
    ("L2", "Partially", "Automated"), ("L3", "Guided", "Automation"),
    ("L4", "Mostly", "Automated"), ("L5", "Full", "Automation"),
]
CH_LABELS = ["\u2014", "Explorer", "Practitioner", "Integrator", "Architect", "Steward"]

GOLDEN_ANGLE = 2.399


def _srand(s: int) -> float:
    s = abs(s * 16807) % 2147483647 or 1
    return (s & 0x7FFFFFFF) / 2147483647


def _classify_balance(rd, cw, ch):
    if cw == 0:
        return "grounded"
    demand = cw * 2 + ch * 2
    capacity = rd * 5
    ratio = demand / capacity if capacity > 0 else 99
    if ratio <= 0.6:
        return "deeply rooted"
    elif ratio <= 1.1:
        return "balanced"
    elif ratio <= 1.8:
        return "reaching"
    return "top-heavy"


def _max_lean(balance):
    return {"grounded": 2, "deeply rooted": 5, "balanced": 12,
            "reaching": 30, "top-heavy": 75}.get(balance, 10)


def _break_at_continuous(rd, cw, ch, roll=5):
    """Compute when a tree falls on the 17-step scale [0, 1.0].

    Each tree gets a random 'roll' (1-9) representing circumstance —
    how the storm hits this particular tree. The vulnerability is:

      effective_ratio = (demand / capacity) × (roll / 5)

    So a roll of 1 halves your exposure (lucky day), roll of 9
    nearly doubles it (worst case). Same tree, same wind, different
    outcomes depending on the roll.

    Rules:
      - No canopy (cw=0): never falls
      - rd=5 (Steward craft): never falls
      - effective_ratio ≤ 1.0: doesn't fall at this wind
      - effective_ratio > 1.0: falls. Higher = falls earlier.

    Falls spread from strong breeze to cat 5.
    """
    if cw == 0:
        return 99

    if rd >= 5:
        return 99

    demand = cw * 2 + ch * 2
    capacity = rd * 5
    ratio = demand / capacity if capacity > 0 else 99

    # Apply the circumstance roll
    effective = ratio * (roll / 5.0)

    if effective <= 2.0:
        return 99

    # effective 2.0 → breakAt 0.98 (cat 5 — barely over threshold)
    # effective 7.0+ → breakAt 0.38 (strong breeze — worst cases)
    t = min(1.0, (effective - 2.0) / 5.0)
    return 0.98 - t * t * 0.60


# ── Shared: enrich trees, load symbols, compute stats ──

def _prepare(forest_data: dict) -> tuple[list[dict], dict[str, str], dict[str, int], int]:
    """Returns (enriched_trees, symbol_contents, balance_counts, total)."""
    raw_trees = forest_data.get("trees", [])
    total = len(raw_trees)

    enriched = []
    for i, t in enumerate(raw_trees):
        rd = t.get("rd") or 1
        cw = t.get("cw") or 0
        ch = t.get("ch") or 0
        balance = t.get("balance") or _classify_balance(rd, cw, ch)
        ml = _max_lean(balance)

        # Compute raw ratio — the client will multiply by dice roll
        if cw == 0 or rd >= 5:
            ratio = 0  # immune
        else:
            demand = cw * 2 + ch * 2
            capacity = rd * 5
            ratio = round(demand / capacity, 3) if capacity > 0 else 0

        enriched.append({
            "rd": rd, "cw": cw, "ch": ch,
            "symbol_id": f"r{rd}_c{cw}_h{ch}",
            "balance": balance,
            "max_lean": ml,
            "ratio": ratio,
            "seed": rd * 100000 + cw * 10000 + ch * 1000 + i * 137 + 42,
        })

    balance_counts: dict[str, int] = {}
    for t in enriched:
        balance_counts[t["balance"]] = balance_counts.get(t["balance"], 0) + 1

    # Count per form, then deduplicate to one tree per form
    form_counts: dict[str, int] = {}
    for t in enriched:
        form_counts[t["symbol_id"]] = form_counts.get(t["symbol_id"], 0) + 1

    seen: set[str] = set()
    deduped = []
    for t in enriched:
        if t["symbol_id"] not in seen:
            seen.add(t["symbol_id"])
            t["count"] = form_counts[t["symbol_id"]]
            deduped.append(t)

    # Ensure all 130 forms are present, even with count=0
    for rd in range(1, 6):
        for cw in range(0, 6):
            for ch in range(0, 6):
                if cw == 0 and ch != 0:
                    continue
                sid = f"r{rd}_c{cw}_h{ch}"
                if sid not in seen:
                    seen.add(sid)
                    balance = _classify_balance(rd, cw, ch)
                    ml = _max_lean(balance)
                    if cw == 0 or rd >= 5:
                        ratio = 0
                    else:
                        demand = cw * 2 + ch * 2
                        capacity = rd * 5
                        ratio = round(demand / capacity, 3)
                    deduped.append({
                        "rd": rd, "cw": cw, "ch": ch,
                        "symbol_id": sid,
                        "balance": balance,
                        "max_lean": ml,
                        "ratio": ratio,
                        "count": 0,
                        "seed": rd * 100000 + cw * 10000 + ch * 1000 + 42,
                    })
    enriched = deduped

    # Load mini symbols
    needed = {t["symbol_id"] for t in enriched}
    symbols: dict[str, str] = {}
    mini_dir = _STATIC_DIR / "trees" / "mini"
    for sid in needed:
        try:
            raw = (mini_dir / f"{sid}.svg").read_text(encoding="utf-8")
            m = _SVG_INNER_RE.search(raw)
            symbols[sid] = m.group(1) if m else ""
        except FileNotFoundError:
            symbols[sid] = ""

    return enriched, symbols, balance_counts, total


def _defs(symbols: dict[str, str], hide_roots: bool = False) -> str:
    p = ['<defs>']
    p.append(
        '<linearGradient id="fSkyG" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0%" stop-color="#2a4a70"/>'
        '<stop offset="70%" stop-color="#4a7aa0"/>'
        '<stop offset="100%" stop-color="#5a8a50"/>'
        '</linearGradient>'
    )
    import re as _re
    for sid, inner in symbols.items():
        content = inner
        if hide_roots:
            # Strip <g class="mini-roots">...</g> from the symbol content
            content = _re.sub(r'<g class="mini-roots">.*?</g>', '', content, flags=_re.DOTALL)
        p.append(f'<symbol id="sym-{sid}" viewBox="0 0 {ORG_W} {ORG_H}">{content}</symbol>')
    p.append('</defs>')
    return "".join(p)


def _balance_color(balance: str) -> str:
    """Map balance category to a cell background color."""
    colors = {
        "deeply rooted": "rgba(74,222,128,0.25)",
        "balanced":      "rgba(74,222,128,0.18)",
        "grounded":      "rgba(74,222,128,0.12)",
        "reaching":      "rgba(251,191,36,0.35)",
        "top-heavy":     "rgba(248,113,113,0.40)",
    }
    return colors.get(balance, "")


def _place_tree(i, t, x, y, sc, show_risk_color=False, show_count=False) -> str:
    w = ORG_W * sc
    h = ORG_H * sc
    ux = x - w / 2
    uy = y - ORG_GY * sc
    count = t.get("count", 1)
    is_empty = count == 0

    overlay = ""
    if show_risk_color and t.get("balance"):
        col = _balance_color(t["balance"])
        if col:
            cr = w * 0.35
            cy_off = ORG_GY * sc * 0.4
            overlay = (
                f'<circle cx="{x:.0f}" cy="{y - cy_off:.0f}" r="{cr:.0f}" '
                f'fill="{col}" />'
            )

    count_label = ""
    if show_count:
        count_label = (
            f'<text x="{x:.0f}" y="{y + h * 0.35:.0f}" text-anchor="middle" '
            f'fill="rgba(0,0,0,{"0.35" if is_empty else "0.75"})" font-size="14" '
            f'font-weight="700" font-family="system-ui,sans-serif">'
            f'{count}</text>'
        )

    tree_opacity = ''
    tree_class = "forest-tree-g"
    data_empty = ' data-empty="1"' if is_empty else ''

    return (
        f'<g id="ftree-{i}" class="{tree_class}" '
        f'data-ratio="{t["ratio"]}" '
        f'data-x="{x:.0f}" data-y="{y:.0f}"{data_empty}{tree_opacity}>'
        f'{overlay}'
        f'<use href="#sym-{t["symbol_id"]}" '
        f'x="{ux:.1f}" y="{uy:.1f}" width="{w:.1f}" height="{h:.1f}"/>'
        f'{count_label}'
        f'</g>'
    )


def _attribution(w, h) -> str:
    return (
        f'<text x="{w / 2}" y="{h - 8}" text-anchor="middle" '
        f'fill="rgba(255,255,255,0.2)" font-size="8" font-family="system-ui,sans-serif">'
        f'Based on the Design in Tech Report 2026 by John Maeda. '
        f'Site and tool built by Noah Ratzan.</text>'
    )


# ══════════════════════════════════════════════════════════════
# "The Trees" — analytical 6×5 grid
#
# 6 columns: L0, L1, L2, L3, L4, L5
# 5 rows: Explorer (bottom) to Steward (top)
# L0 column: 1 tree per row (the root-only form matching that EPIAS level)
# L1-L5 columns: 5 trees per cell (rd 1-5 in a horizontal row)
# ══════════════════════════════════════════════════════════════

_FONT = "system-ui, -apple-system, sans-serif"

_T_PAD_L = 120
_T_PAD_R = 10
_T_PAD_T = 30
_T_PAD_B = 60

_T_ROWS = 5      # Explorer-Steward

_T_PLOT_W = TREES_W - _T_PAD_L - _T_PAD_R
_T_PLOT_H = TREES_H - _T_PAD_T - _T_PAD_B
_T_L0_W = _T_PLOT_W * 0.04          # L0 column: just wide enough for 1 tree
_T_AI_W = _T_PLOT_W - _T_L0_W       # L1-L5 share the rest
_T_COL_W = _T_AI_W / 5              # each AI column
_T_ROW_H = _T_PLOT_H / _T_ROWS

_SAE_SHORT = ["L0", "L1", "L2", "L3", "L4", "L5"]
_SAE_LONG = ["Manual", "AI-Assisted", "Partially\nAutomated", "Guided\nAutomation", "Mostly\nAutomated", "Full\nAutomation"]
_CH_SHORT = ["Explorer", "Practitioner", "Integrator", "Architect", "Steward"]


def _render_trees(enriched, symbols):
    by_cell: dict[tuple[int, int, int], dict] = {}
    for t in enriched:
        by_cell[(t["cw"], t["ch"], t["rd"])] = t

    # Column X helpers: L0 is narrow, L1-L5 are wide
    def col_left(c):
        """Left edge of column c (0=L0, 1=L1, ... 5=L5)."""
        if c == 0:
            return _T_PAD_L
        return _T_PAD_L + _T_L0_W + (c - 1) * _T_COL_W

    def col_center(c):
        if c == 0:
            return _T_PAD_L + _T_L0_W / 2
        return col_left(c) + _T_COL_W / 2

    def col_width(c):
        return _T_L0_W if c == 0 else _T_COL_W

    parts = [_defs(symbols)]
    parts.append(f'<rect width="{TREES_W}" height="{TREES_H}" fill="#f5f3ef"/>')

    # Row backgrounds
    for row in range(_T_ROWS):
        ry = _T_PAD_T + row * _T_ROW_H
        shade = 'rgba(0,0,0,0.02)' if row % 2 == 0 else 'rgba(0,0,0,0.04)'
        parts.append(f'<rect x="{_T_PAD_L}" y="{ry}" width="{_T_PLOT_W}" height="{_T_ROW_H}" fill="{shade}"/>')

    # (L0 column has no special background — same as the rest)

    # Grid lines — vertical
    for c in range(7):  # 0=left edge, 1=L0/L1 border, ... 6=right edge
        gx = col_left(c) if c <= 5 else _T_PAD_L + _T_PLOT_W
        w = "1.5" if c == 1 else "0.5"  # thicker divider between L0 and L1
        parts.append(f'<line x1="{gx}" y1="{_T_PAD_T}" x2="{gx}" y2="{_T_PAD_T + _T_PLOT_H}" stroke="rgba(0,0,0,0.1)" stroke-width="{w}"/>')
    # Horizontal
    for row in range(_T_ROWS + 1):
        gy = _T_PAD_T + row * _T_ROW_H
        parts.append(f'<line x1="{_T_PAD_L}" y1="{gy}" x2="{_T_PAD_L + _T_PLOT_W}" y2="{gy}" stroke="rgba(0,0,0,0.08)" stroke-width="0.5"/>')

    # ── X axis labels ──
    x_label_y = _T_PAD_T + _T_PLOT_H + 20
    for c in range(6):
        lx = col_center(c)
        parts.append(
            f'<text x="{lx}" y="{x_label_y}" text-anchor="middle" '
            f'fill="rgba(0,0,0,0.85)" font-size="24" font-weight="700" font-family="{_FONT}">'
            f'{_SAE_SHORT[c]}</text>'
        )
        for j, sub in enumerate(_SAE_LONG[c].split("\n")):
            parts.append(
                f'<text x="{lx}" y="{x_label_y + 18 + j * 14}" text-anchor="middle" '
                f'fill="rgba(0,0,0,0.55)" font-size="16" font-family="{_FONT}">{sub}</text>'
            )

    # (axis title removed — L0-L5 labels are self-explanatory)

    # ── Y axis labels ──
    for row in range(5):
        ch_val = 5 - row
        ly = _T_PAD_T + row * _T_ROW_H + _T_ROW_H / 2 + 6
        parts.append(
            f'<text x="{_T_PAD_L - 10}" y="{ly}" text-anchor="end" '
            f'fill="rgba(0,0,0,0.85)" font-size="18" font-weight="600" font-family="{_FONT}">'
            f'{_CH_SHORT[ch_val - 1]}</text>'
        )

    # (Y axis title removed — row labels are self-explanatory)

    # Label over L1
    parts.append(
        f'<text x="{col_left(1)}" y="{_T_PAD_T - 6}" text-anchor="start" '
        f'fill="rgba(0,0,0,0.55)" font-size="16" font-weight="600" font-family="{_FONT}">'
        f'Each cell ordered by root depth.</text>'
    )

    # ── Place trees ──
    tree_idx = 0
    for row in range(5):
        ch_val = 5 - row

        # L0 column
        t = by_cell.get((0, 0, ch_val))
        if t:
            x = col_center(0)
            y = _T_PAD_T + row * _T_ROW_H + _T_ROW_H / 2 + 10
            sc = 0.10 + ch_val * 0.016
            parts.append(_place_tree(tree_idx, t, x, y, sc, show_risk_color=True, show_count=True))
            tree_idx += 1

        # L1-L5 columns
        for cw in range(1, 6):
            cl = col_left(cw)
            cw_w = col_width(cw)
            cell_cy = _T_PAD_T + row * _T_ROW_H + _T_ROW_H / 2

            for rd in range(1, 6):
                t = by_cell.get((cw, ch_val, rd))
                if not t:
                    continue
                slot = rd - 1
                x = cl + (slot + 0.5) * (cw_w / 5)
                y = cell_cy + 10
                sc = 0.09 + (cw + ch_val) * 0.011
                parts.append(_place_tree(tree_idx, t, x, y, sc, show_risk_color=True, show_count=True))
                tree_idx += 1


    return "".join(parts)


# ══════════════════════════════════════════════════════════════
# "The Forest" — naturalistic landscape with groves
# ══════════════════════════════════════════════════════════════

def _hash2(a: int, b: int) -> float:
    """Deterministic hash of two ints to [0, 1). Better spread than _srand."""
    h = ((a * 2654435761) ^ (b * 340573321)) & 0xFFFFFFFF
    return (h & 0x7FFFFFFF) / 0x7FFFFFFF


def _render_forest(enriched, symbols):
    """Scatter actual participants across a landscape.
    Only trees with count > 0 are shown. Trees with the same form
    but different participants get slightly different positions.

    Grove centers are seeded by (cw, ch) so the same form type always
    clusters in the same region. Root depth is invisible — different rd
    values for the same (cw, ch) land in the same grove.
    """
    # Only show trees with actual participants — expand by count
    import random as _rng
    _rng.seed(42)

    MARGIN = 40
    USABLE_W = FOREST_W - 2 * MARGIN
    TREE_TOP = FOREST_H * 0.52
    TREE_BOT = FOREST_H - 20

    expanded = []
    for t in enriched:
        count = t.get("count", 0)
        if count <= 0:
            continue
        for j in range(count):
            copy = dict(t)
            copy["_fx"] = MARGIN + _rng.random() * USABLE_W
            copy["_fy"] = TREE_TOP + _rng.random() * (TREE_BOT - TREE_TOP)
            copy["seed"] = t["seed"] + j * 137  # vary per instance
            expanded.append(copy)

    enriched = expanded
    enriched.sort(key=lambda t: t["_fy"])

    parts = [_defs(symbols, hide_roots=True)]

    # Background — sky and ground as distinct zones
    HORIZON = FOREST_H * 0.38
    parts.append(
        '<defs>'
        '<linearGradient id="fSkyBg" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0%" stop-color="#2a4a70"/>'
        '<stop offset="80%" stop-color="#6a9ab8"/>'
        '<stop offset="100%" stop-color="#8ab0c0"/>'
        '</linearGradient>'
        '<linearGradient id="fGroundBg" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0%" stop-color="#5a7a38"/>'
        '<stop offset="40%" stop-color="#4e7032"/>'
        '<stop offset="100%" stop-color="#456830"/>'
        '</linearGradient>'
        '</defs>'
    )
    # Sky
    parts.append(f'<rect width="{FOREST_W}" height="{HORIZON:.0f}" fill="url(#fSkyBg)"/>')
    # Ground
    parts.append(f'<rect y="{HORIZON:.0f}" width="{FOREST_W}" height="{FOREST_H - HORIZON:.0f}" fill="url(#fGroundBg)"/>')
    # Horizon line — soft blend
    parts.append(f'<rect y="{HORIZON - 3:.0f}" width="{FOREST_W}" height="8" fill="rgba(100,140,70,0.4)"/>')

    # Rolling hills — large overlapping mounds that create terrain contours
    hill_data = [
        # (x_frac, y_frac_below_horizon, width, height, color)
        (0.15, 0.05, 500, 80, 'rgba(75,115,45,0.5)'),
        (0.55, 0.02, 600, 90, 'rgba(70,110,42,0.45)'),
        (0.85, 0.08, 450, 70, 'rgba(80,120,48,0.4)'),
        (0.35, 0.15, 550, 75, 'rgba(65,105,38,0.35)'),
        (0.70, 0.12, 480, 65, 'rgba(72,112,40,0.3)'),
        (0.10, 0.25, 400, 55, 'rgba(58,95,32,0.25)'),
        (0.50, 0.30, 500, 60, 'rgba(55,90,30,0.2)'),
    ]
    for xf, yf, w, h, col in hill_data:
        hx = xf * FOREST_W
        hy = HORIZON + yf * (FOREST_H - HORIZON)
        parts.append(
            f'<ellipse cx="{hx:.0f}" cy="{hy:.0f}" rx="{w}" ry="{h}" fill="{col}"/>'
        )

    # Grass texture — small varied patches
    for patch in range(25):
        px = _hash2(patch, 77) * FOREST_W
        py = HORIZON + 10 + _hash2(patch, 33) * (FOREST_H - HORIZON - 20)
        prx = 40 + _hash2(patch, 55) * 100
        pry = 8 + _hash2(patch, 44) * 18
        shade = ['rgba(85,125,45,0.15)', 'rgba(55,95,28,0.12)', 'rgba(95,140,55,0.10)',
                 'rgba(70,105,35,0.18)', 'rgba(45,80,22,0.14)'][patch % 5]
        parts.append(
            f'<ellipse cx="{px:.0f}" cy="{py:.0f}" rx="{prx:.0f}" ry="{pry:.0f}" fill="{shade}"/>'
        )

    # Dirt/earth patches — exposed soil
    for dp in range(8):
        dx = _hash2(dp + 30, 88) * FOREST_W
        dy = HORIZON + 40 + _hash2(dp + 30, 44) * (FOREST_H - HORIZON - 60)
        drx = 25 + _hash2(dp + 30, 66) * 60
        dry = 6 + _hash2(dp + 30, 22) * 12
        parts.append(
            f'<ellipse cx="{dx:.0f}" cy="{dy:.0f}" rx="{drx:.0f}" ry="{dry:.0f}" '
            f'fill="rgba(85,65,40,0.10)"/>'
        )

    # Small stones
    for st in range(12):
        sx = _hash2(st + 70, 91) * FOREST_W
        sy = HORIZON + 40 + _hash2(st + 70, 37) * (FOREST_H - HORIZON - 60)
        sr = 2 + _hash2(st + 70, 55) * 4
        col = ['rgba(110,100,85,0.20)', 'rgba(95,88,72,0.18)', 'rgba(125,115,100,0.15)'][st % 3]
        parts.append(
            f'<ellipse cx="{sx:.0f}" cy="{sy:.0f}" rx="{sr:.0f}" ry="{sr * 0.5:.0f}" fill="{col}"/>'
        )

    # Place trees
    for i, t in enumerate(enriched):
        x = t["_fx"]
        y = t["_fy"]

        # Perspective: near bottom = foreground = bigger
        depth_frac = y / FOREST_H
        sc = 0.12 + depth_frac * 0.22

        parts.append(_place_tree(i, t, x, y, sc))

    return "".join(parts)


# ══════════════════════════════════════════════════════════════
# Public API
# ══════════════════════════════════════════════════════════════

def render_forest_svg(forest_data: dict, mode: str = "trees") -> tuple[str, dict]:
    """Render the forest visualization.

    Args:
        forest_data: from get_forest_data()
        mode: "trees" (grid) or "forest" (landscape)

    Returns: (svg_string, stats_dict)
    """
    enriched, symbols, balance_counts, total = _prepare(forest_data)

    if mode == "forest":
        inner = _render_forest(enriched, symbols)
        w, h = FOREST_W, FOREST_H
    else:
        inner = _render_trees(enriched, symbols)
        w, h = TREES_W, TREES_H

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'style="width:100%;display:block" id="forestSvg">'
        + inner
        + '</svg>'
    )
    return svg, {"total": total, "balance_counts": balance_counts}
