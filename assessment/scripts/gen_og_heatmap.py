"""Generate heatmap-style OG image for LinkedIn.

Grid is the hero. Orange heatmap palette — dark at edges, glowing at the
realistic cluster zone (L1–L2, P–I). Makes people ask "where am I?"

Run from repo root:
    python assessment/scripts/gen_og_heatmap.py
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os, math

W, H = 1200, 627
FONTS = "C:/Windows/Fonts/"

def font(name, size):
    try:
        return ImageFont.truetype(FONTS + name, size)
    except Exception:
        return ImageFont.load_default()

# ── Simulated distribution (realistic cluster) ─────────────────────────────
# Where designers actually land: most at L1-L2, stages E-P-I
LEVEL_WEIGHT  = {0: 0.06, 1: 0.28, 2: 0.32, 3: 0.20, 4: 0.10, 5: 0.04}
STAGE_WEIGHT  = {"E": 0.30, "P": 0.28, "I": 0.22, "A": 0.13, "S": 0.07}

LEVELS = list(range(6))
STAGES = ["E", "P", "I", "A", "S"]

def heat(level, stage):
    """0.0–1.0 intensity for a cell."""
    return LEVEL_WEIGHT[level] * STAGE_WEIGHT[stage]

max_heat = max(heat(l, s) for l in LEVELS for s in STAGES)

def norm_heat(level, stage):
    return heat(level, stage) / max_heat

# ── Orange heatmap palette ─────────────────────────────────────────────────
# 0.0 → near-black deep brown
# 0.5 → burnt orange
# 1.0 → bright amber/gold
def heat_color(t):
    """Map t (0–1) to an orange heatmap RGB tuple."""
    # Three-stop gradient: black → dark orange → bright amber
    if t < 0.0: t = 0.0
    if t > 1.0: t = 1.0
    stops = [
        (0.00, (8,   4,   2)),
        (0.15, (40,  14,  3)),
        (0.35, (120, 40,  5)),
        (0.55, (195, 72,  8)),
        (0.75, (235, 115, 15)),
        (0.90, (250, 165, 30)),
        (1.00, (255, 210, 60)),
    ]
    for i in range(len(stops) - 1):
        t0, c0 = stops[i]
        t1, c1 = stops[i + 1]
        if t0 <= t <= t1:
            f = (t - t0) / (t1 - t0)
            return tuple(int(c0[j] + f * (c1[j] - c0[j])) for j in range(3))
    return stops[-1][1]

def glow_color(t):
    """Slightly lighter outer glow version."""
    r, g, b = heat_color(t)
    return (min(255, r + 30), min(255, g + 15), min(255, b + 5))

# ── Layout ──────────────────────────────────────────────────────────────────
CELL_W   = 100
CELL_H   = 72
GAP      = 6
RADIUS   = 9

GRID_W   = 5 * CELL_W + 4 * GAP
GRID_H   = 6 * CELL_H + 5 * GAP

LABEL_W  = 50   # space left of grid for L0–L5
HEADER_H = 38   # space above grid for E P I A S

TOTAL_W  = LABEL_W + GRID_W
TOTAL_H  = HEADER_H + GRID_H

TEXT_H   = 80   # space below grid for headline + url

# Center the whole block (grid + text below)
ORIGIN_X = (W - TOTAL_W) // 2
ORIGIN_Y  = (H - TOTAL_H - TEXT_H) // 2

# ── Build image ─────────────────────────────────────────────────────────────
img = Image.new("RGB", (W, H), (4, 2, 1))
draw = ImageDraw.Draw(img)

# Background gradient — very dark warm
for y in range(H):
    t = y / H
    r = int(4 + t * 6)
    g = int(2 + t * 3)
    b = int(1 + t * 2)
    draw.line([(0, y), (W, y)], fill=(r, g, b))

# ── Fonts ───────────────────────────────────────────────────────────────────
f_stage   = font("arialbd.ttf", 20)
f_level   = font("arialbd.ttf", 18)
f_head    = font("arialbd.ttf", 44)
f_sub     = font("segoeui.ttf",  20)
f_url     = font("segoeui.ttf",  16)
f_tiny    = font("segoeui.ttf",  13)

# ── Draw grid ────────────────────────────────────────────────────────────────
gx0 = ORIGIN_X + LABEL_W
gy0 = ORIGIN_Y + HEADER_H

# Column headers
for ci, stage in enumerate(STAGES):
    cx = gx0 + ci * (CELL_W + GAP) + CELL_W // 2
    cy = ORIGIN_Y + HEADER_H // 2
    # Color the header by average stage heat
    avg_t = sum(norm_heat(l, stage) for l in LEVELS) / 6
    col = heat_color(min(1.0, avg_t * 3.5))
    draw.text((cx, cy), stage, font=f_stage, fill=col, anchor="mm")

# Row labels + cells
for ri, level in enumerate(LEVELS):
    gy = gy0 + ri * (CELL_H + GAP)

    # Row label
    lx = ORIGIN_X + LABEL_W // 2
    ly = gy + CELL_H // 2
    avg_t = sum(norm_heat(level, s) for s in STAGES) / 5
    lcol = heat_color(min(1.0, avg_t * 3.5))
    draw.text((lx, ly), f"L{level}", font=f_level, fill=lcol, anchor="mm")

    for ci, stage in enumerate(STAGES):
        cx = gx0 + ci * (CELL_W + GAP)
        cy = gy
        t = norm_heat(level, stage)

        fill  = heat_color(t)
        fr, fg, fb = fill
        # Border: brighter than fill for contrast; dark cells get a dim outline
        border = (min(255, fr + 45), min(255, fg + 22), min(255, fb + 8))

        draw.rounded_rectangle(
            [cx, cy, cx + CELL_W, cy + CELL_H],
            radius=RADIUS,
            fill=fill,
            outline=border,
            width=1,
        )

        # Intensity mark for hot cells
        if t > 0.65:
            dot_x = cx + CELL_W // 2
            dot_y = cy + CELL_H // 2
            dot_r = int(6 + 8 * t)
            bright = (255, min(255, int(180 + 75 * t)), min(255, int(40 + 60 * t)))
            draw.ellipse([dot_x - dot_r, dot_y - dot_r,
                          dot_x + dot_r, dot_y + dot_r],
                         fill=bright)

# ── Headline — bottom-left area below or beside grid ────────────────────────
# Figure out how much space is to the right / below
text_y = ORIGIN_Y + TOTAL_H + 28

draw.text((ORIGIN_X + LABEL_W, text_y),
          "Where are you on the AI skills map?",
          font=f_head, fill=(240, 200, 120), anchor="lm")

draw.text((ORIGIN_X + LABEL_W, text_y + 54),
          "3-min self-assessment for designers & UX researchers  ·  aiskillsmap.noahratzan.com",
          font=f_url, fill=(130, 90, 40), anchor="lm")

# ── Save ─────────────────────────────────────────────────────────────────────
out = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "static", "og-image.jpg")
)
img.save(out, "JPEG", quality=93, optimize=True)
print(f"Saved: {out}  ({os.path.getsize(out) // 1024} KB)")
