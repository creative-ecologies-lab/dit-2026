"""Generate 5-slide LinkedIn carousel PDF for aiskillsmap.noahratzan.com.

Output:
  assessment/static/carousel/slide_01.jpg … slide_05.jpg
  assessment/static/carousel/carousel.pdf

Run from repo root:
    python assessment/scripts/gen_carousel.py
"""

from PIL import Image, ImageDraw, ImageFont
import os, textwrap

# ── Canvas ───────────────────────────────────────────────────────────────────
SW, SH = 1080, 1080   # square — best for LinkedIn carousel

OUT_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "static", "carousel")
)
os.makedirs(OUT_DIR, exist_ok=True)

FONTS = "C:/Windows/Fonts/"
def font(name, size):
    try:
        return ImageFont.truetype(FONTS + name, size)
    except Exception:
        return ImageFont.load_default()

# ── Shared fonts ─────────────────────────────────────────────────────────────
F_TITLE   = font("arialbd.ttf",  64)
F_TITLE2  = font("arialbd.ttf",  52)
F_HEAD    = font("arialbd.ttf",  40)
F_LABEL   = font("arialbd.ttf",  28)
F_BODY    = font("segoeui.ttf",  26)
F_BODY_SM = font("segoeui.ttf",  22)
F_SMALL   = font("segoeui.ttf",  18)
F_TINY    = font("segoeui.ttf",  15)
F_COUNTER = font("segoeui.ttf",  17)
F_STAGE   = font("arialbd.ttf",  22)
F_LEVEL   = font("arialbd.ttf",  20)

# ── Color helpers ─────────────────────────────────────────────────────────────
def hex_rgb(h):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

def heat_color(t):
    """0–1 → orange heatmap RGB. Floor raised so dark cells show against black bg."""
    if t < 0: t = 0
    if t > 1: t = 1
    stops = [
        (0.00, (90,  42, 12)),   # floor clearly visible on near-black bg
        (0.20, (130, 55, 10)),
        (0.40, (175, 72,  8)),
        (0.60, (215, 95, 10)),
        (0.78, (242, 130, 18)),
        (0.92, (252, 175, 35)),
        (1.00, (255, 215, 65)),
    ]
    for i in range(len(stops) - 1):
        t0, c0 = stops[i]
        t1, c1 = stops[i + 1]
        if t0 <= t <= t1:
            f = (t - t0) / (t1 - t0)
            return tuple(int(c0[j] + f * (c1[j] - c0[j])) for j in range(3))
    return stops[-1][1]

WARM_WHITE  = (245, 228, 200)
MUTED       = (195, 168, 120)   # was (138,106,64) — lifted for dark bg
DIM         = (130, 100, 55)    # was (80,58,30)
AMBER       = (255, 185, 40)
DARK_BG     = (4, 2, 1)

# ── Distribution weights ──────────────────────────────────────────────────────
LEVEL_W = {0: 0.06, 1: 0.28, 2: 0.32, 3: 0.20, 4: 0.10, 5: 0.04}
STAGE_W = {"E": 0.30, "P": 0.28, "I": 0.22, "A": 0.13, "S": 0.07}
LEVELS  = list(range(6))
STAGES  = ["E", "P", "I", "A", "S"]

def norm_heat(level, stage):
    v = LEVEL_W[level] * STAGE_W[stage]
    max_v = max(LEVEL_W[l] * STAGE_W[s] for l in LEVELS for s in STAGES)
    return v / max_v

# ── Shared drawing helpers ────────────────────────────────────────────────────
def draw_bg(draw):
    for y in range(SH):
        t = y / SH
        r = int(4 + t * 8)
        g = int(2 + t * 4)
        b = int(1 + t * 2)
        draw.line([(0, y), (SW, y)], fill=(r, g, b))

def draw_counter(draw, n, total=5):
    text = f"{n} / {total}"
    draw.text((SW - 40, SH - 36), text, font=F_COUNTER,
              fill=DIM, anchor="rm")

def draw_brand(draw):
    draw.text((40, SH - 36), "John Maeda · DIT 2026 · SXSW",
              font=F_TINY, fill=DIM, anchor="lm")

def wrap(draw, text, font, max_w):
    words = text.split()
    lines, cur = [], []
    for w in words:
        test = " ".join(cur + [w])
        if draw.textbbox((0, 0), test, font=font)[2] > max_w and cur:
            lines.append(" ".join(cur))
            cur = [w]
        else:
            cur.append(w)
    if cur:
        lines.append(" ".join(cur))
    return lines

def draw_heatmap(draw, gx0, gy0, cell_w, cell_h, gap, radius,
                 label_w, header_h, highlight_zone=None, mark_zone=None):
    """Draw the full 6×5 heatmap grid.

    highlight_zone: set of (level, stage) tuples to draw a box around
    mark_zone: tuple (level, stage) to put a "YOU ARE HERE" marker
    """
    # Stage headers
    for ci, stage in enumerate(STAGES):
        cx = gx0 + ci * (cell_w + gap) + cell_w // 2
        cy = gy0 - header_h // 2
        avg_t = sum(norm_heat(l, stage) for l in LEVELS) / 6
        col = heat_color(min(1.0, avg_t * 3.5))
        draw.text((cx, cy), stage, font=F_STAGE, fill=col, anchor="mm")

    # Level labels + cells — L5 at top, L0 at bottom
    for ri, level in enumerate(reversed(LEVELS)):
        cy_row = gy0 + ri * (cell_h + gap)

        avg_t = sum(norm_heat(level, s) for s in STAGES) / 5
        lcol = heat_color(min(1.0, avg_t * 3.5))
        draw.text((gx0 - label_w // 2, cy_row + cell_h // 2),
                  f"L{level}", font=F_LEVEL, fill=lcol, anchor="mm")

        for ci, stage in enumerate(STAGES):
            cx = gx0 + ci * (cell_w + gap)
            cy = cy_row
            t = norm_heat(level, stage)

            fill = heat_color(t)
            fr, fg, fb = fill
            border = (min(255, fr + 45), min(255, fg + 22), min(255, fb + 8))

            draw.rounded_rectangle(
                [cx, cy, cx + cell_w, cy + cell_h],
                radius=radius, fill=fill, outline=border, width=1,
            )

            # Single crosshair on peak cell only
            if norm_heat(level, stage) == 1.0:
                dx, dy = cx + cell_w // 2, cy + cell_h // 2
                cr, arm, gap_r = 10, 18, 4   # circle radius, arm length, gap
                draw.ellipse([dx - cr, dy - cr, dx + cr, dy + cr],
                             outline=(255, 230, 180), width=2)
                # horizontal arms
                draw.line([(dx - arm - gap_r, dy), (dx - cr - gap_r, dy)],
                          fill=(255, 230, 180), width=2)
                draw.line([(dx + cr + gap_r, dy), (dx + arm + gap_r, dy)],
                          fill=(255, 230, 180), width=2)
                # vertical arms
                draw.line([(dx, dy - arm - gap_r), (dx, dy - cr - gap_r)],
                          fill=(255, 230, 180), width=2)
                draw.line([(dx, dy + cr + gap_r), (dx, dy + arm + gap_r)],
                          fill=(255, 230, 180), width=2)

    # Draw highlight box around a zone
    if highlight_zone:
        levels_h = sorted({l for l, s in highlight_zone})
        stages_h = sorted({STAGES.index(s) for l, s in highlight_zone})
        x1 = gx0 + min(stages_h) * (cell_w + gap) - 5
        y1 = gy0 + min(levels_h) * (cell_h + gap) - 5
        x2 = gx0 + (max(stages_h) + 1) * cell_w + max(stages_h) * gap + 5
        y2 = gy0 + (max(levels_h) + 1) * cell_h + max(levels_h) * gap + 5
        for off in range(6, 0, -2):
            draw.rounded_rectangle(
                [x1 - off, y1 - off, x2 + off, y2 + off],
                radius=radius + off,
                outline=(255, 200, 60, max(0, 30 - off * 4)),
                width=1,
            )
        draw.rounded_rectangle([x1, y1, x2, y2], radius=radius,
                                outline=AMBER, width=2)

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 1 — Hook: The heatmap, minimal copy
# ═══════════════════════════════════════════════════════════════════════════════
def slide_1():
    img = Image.new("RGB", (SW, SH), DARK_BG)
    draw = ImageDraw.Draw(img)
    draw_bg(draw)

    # Grid dimensions for 1080×1080
    cell_w, cell_h, gap, radius = 124, 90, 7, 11
    label_w, header_h = 58, 44
    grid_w = 5 * cell_w + 4 * gap
    grid_h = 6 * cell_h + 5 * gap

    # Title above, swipe prompt below — grid centered in remaining space
    title_block_h = 160   # two lines of title text
    foot_h        = 70
    grid_top = title_block_h + header_h
    gx0 = (SW - grid_w) // 2 + label_w // 2
    gy0 = grid_top

    # Title — clear of grid
    draw.text((SW // 2, 62), "Where are you on the",
              font=F_TITLE2, fill=WARM_WHITE, anchor="mm")
    draw.text((SW // 2, 128), "AI Skills Map?",
              font=F_TITLE, fill=AMBER, anchor="mm")

    draw_heatmap(draw, gx0, gy0, cell_w, cell_h, gap, radius, label_w, header_h)

    # Audience + swipe prompt
    draw.text((SW // 2, gy0 + grid_h + 28),
              "For designers & UX researchers",
              font=F_SMALL, fill=DIM, anchor="mm")
    draw.text((SW // 2, gy0 + grid_h + 56), "Swipe to find your coordinates →",
              font=F_BODY_SM, fill=MUTED, anchor="mm")

    draw_brand(draw)
    draw_counter(draw, 1)
    return img

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 2 — SAE Levels
# ═══════════════════════════════════════════════════════════════════════════════
SAE_DATA = [
    (0, "L0 — Manual",                 "You do the work. Tools don't decide or generate."),
    (1, "L1 — AI-Assisted",            "AI suggests. You decide. Cognitive load drops, not responsibility."),
    (2, "L2 — Partially Automated",    "AI builds bounded pieces. You assemble, integrate, and verify."),
    (3, "L3 — Guided Automation",      "You own the checkpoints. Work spans sessions, not just prompts."),
    (4, "L4 — Mostly Automated",       "Work runs while you sleep. You own the rules, not the steps."),
    (5, "L5 — AI × AI",               "You set goals and constraints. AI does the rest. (Not yet real.)"),
]

def slide_2():
    img = Image.new("RGB", (SW, SH), DARK_BG)
    draw = ImageDraw.Draw(img)
    draw_bg(draw)

    draw.text((SW // 2, 68), "Automation Skills",
              font=F_TITLE, fill=AMBER, anchor="mm")
    draw.text((SW // 2, 118), "How much of your design or research work is AI-driven?",
              font=F_BODY_SM, fill=MUTED, anchor="mm")

    # Horizontal rule
    draw.line([(60, 148), (SW - 60, 148)], fill=(50, 30, 10), width=1)

    PAD_L = 60
    ROW_H = 130
    start_y = 168

    for level, role, desc in SAE_DATA:
        # Heat intensity: higher level = hotter (but map naturally)
        t_heat = [0.04, 0.35, 0.65, 0.82, 0.93, 1.0][level]
        col = heat_color(t_heat)
        bright = (min(255, col[0] + 40), min(255, col[1] + 20), min(255, col[2] + 8))

        cy = start_y + level * ROW_H
        mid_y = cy + ROW_H // 2 - 10

        # Level badge circle
        bx, by = PAD_L + 32, mid_y
        draw.ellipse([bx - 28, by - 28, bx + 28, by + 28], fill=col)
        draw.text((bx, by), f"L{level}", font=F_LABEL,
                  fill=(20, 10, 2) if t_heat > 0.5 else WARM_WHITE, anchor="mm")

        # Role name + description — role always warm white, desc lifted muted
        tx = PAD_L + 78
        draw.text((tx, mid_y - 14), role, font=F_LABEL, fill=WARM_WHITE, anchor="lm")
        draw.text((tx, mid_y + 22), desc, font=F_BODY_SM, fill=MUTED, anchor="lm")

        # Divider (skip last)
        if level < 5:
            draw.line([(PAD_L + 62, cy + ROW_H - 2), (SW - PAD_L, cy + ROW_H - 2)],
                      fill=(30, 18, 6), width=1)

    draw_brand(draw)
    draw_counter(draw, 2)
    return img

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 3 — E-P-I-A-S Axis
# ═══════════════════════════════════════════════════════════════════════════════
EPIAS_DATA = [
    ("E", "Explorer",      "#f59e0b",
     "Trying things out.", "Results vary. Still learning what works."),
    ("P", "Practitioner",  "#e07b08",
     "Consistent habits.", "Repeatable techniques. Process is reliable."),
    ("I", "Integrator",    "#c45800",
     "Fully in your workflow.", "Documented decisions. Traceable outputs."),
    ("A", "Architect",     "#9e3a00",
     "You build systems.", "Templates others adopt and trust."),
    ("S", "Steward",       "#742000",
     "You set the standard.", "Mentor others. Govern practice org-wide."),
]

def slide_3():
    img = Image.new("RGB", (SW, SH), DARK_BG)
    draw = ImageDraw.Draw(img)
    draw_bg(draw)

    draw.text((SW // 2, 68), "Leadership Skills",
              font=F_TITLE, fill=AMBER, anchor="mm")
    draw.text((SW // 2, 118), "How mature is your use of AI?",
              font=F_BODY_SM, fill=MUTED, anchor="mm")

    draw.line([(60, 148), (SW - 60, 148)], fill=(50, 30, 10), width=1)

    # Progress bar across top
    bar_y, bar_h = 162, 8
    bar_w = SW - 120
    for ci, (stage, name, color, _, _) in enumerate(EPIAS_DATA):
        seg_w = bar_w // 5
        bx = 60 + ci * seg_w
        r, g, b = hex_rgb(color)
        draw.rectangle([bx, bar_y, bx + seg_w - 4, bar_y + bar_h], fill=(r, g, b))

    PAD_L = 60
    ROW_H = 158
    start_y = 185

    for i, (stage, name, color, bold_desc, rest_desc) in enumerate(EPIAS_DATA):
        cy = start_y + i * ROW_H
        mid_y = cy + ROW_H // 2 - 12

        r, g, b = hex_rgb(color)
        # Stage badge
        bx, by = PAD_L + 32, mid_y
        draw.ellipse([bx - 30, by - 30, bx + 30, by + 30], fill=(r, g, b))
        draw.text((bx, by), stage, font=F_HEAD,
                  fill=(255, 240, 200) if i < 3 else WARM_WHITE, anchor="mm")

        # Name + descriptions
        tx = PAD_L + 80
        draw.text((tx, mid_y - 22), name, font=F_LABEL,
                  fill=(min(255, r + 50), min(255, g + 25), min(255, b + 8)), anchor="lm")
        draw.text((tx, mid_y + 14), bold_desc, font=F_BODY_SM,
                  fill=WARM_WHITE, anchor="lm")
        draw.text((tx, mid_y + 44), rest_desc, font=F_SMALL,
                  fill=MUTED, anchor="lm")

        if i < 4:
            draw.line([(PAD_L + 62, cy + ROW_H - 4), (SW - PAD_L, cy + ROW_H - 4)],
                      fill=(30, 18, 6), width=1)

    draw_brand(draw)
    draw_counter(draw, 3)
    return img

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 4 — Find your location / Maeda quote
# ═══════════════════════════════════════════════════════════════════════════════
def slide_4():
    img = Image.new("RGB", (SW, SH), DARK_BG)
    draw = ImageDraw.Draw(img)
    draw_bg(draw)

    # Title
    draw.text((SW // 2, 68),  "Find your location on the AI Skills Map",
              font=F_HEAD, fill=WARM_WHITE, anchor="mm")
    draw.text((SW // 2, 116), "and plot your course.",
              font=F_TITLE2, fill=AMBER, anchor="mm")

    draw.line([(80, 150), (SW - 80, 150)], fill=(50, 30, 10), width=1)

    # Smaller grid — centered
    cell_w, cell_h, gap, radius = 90, 65, 5, 8
    label_w, header_h = 44, 34
    grid_w = 5 * cell_w + 4 * gap
    grid_h = 6 * cell_h + 5 * gap

    gx0 = (SW - grid_w) // 2 + label_w // 2
    gy0 = 150 + header_h + 14

    draw_heatmap(draw, gx0, gy0, cell_w, cell_h, gap, radius, label_w, header_h)

    grid_bottom = gy0 + grid_h

    # Quote — the hero below the grid
    draw.line([(80, grid_bottom + 28), (SW - 80, grid_bottom + 28)],
              fill=(50, 30, 10), width=1)

    draw.text((SW // 2, grid_bottom + 68),
              "\u201cA Steward at L1 is more valuable",
              font=F_HEAD, fill=WARM_WHITE, anchor="mm")
    draw.text((SW // 2, grid_bottom + 114),
              "than an Explorer at L4.\u201d",
              font=F_HEAD, fill=AMBER, anchor="mm")
    draw.text((SW // 2, grid_bottom + 156),
              "— John Maeda, DIT 2026",
              font=F_LABEL, fill=MUTED, anchor="mm")

    draw_brand(draw)
    draw_counter(draw, 4)
    return img

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 5 — CTA
# ═══════════════════════════════════════════════════════════════════════════════
def slide_5():
    img = Image.new("RGB", (SW, SH), DARK_BG)
    draw = ImageDraw.Draw(img)
    draw_bg(draw)

    # Centered text block
    cx = SW // 2

    draw.text((cx, 310), "Find your", font=F_TITLE, fill=WARM_WHITE, anchor="mm")
    draw.text((cx, 390), "coordinates.", font=F_TITLE, fill=AMBER, anchor="mm")

    draw.line([(cx - 200, 430), (cx + 200, 430)], fill=(70, 45, 15), width=1)

    draw.text((cx, 472), "3 minutes  ·  Anonymous  ·  No login",
              font=F_BODY_SM, fill=MUTED, anchor="mm")

    draw.text((cx, 560), "aiskillsmap.noahratzan.com",
              font=F_HEAD, fill=AMBER, anchor="mm")

    # Underline the URL
    url_bbox = draw.textbbox((0, 0), "aiskillsmap.noahratzan.com", font=F_HEAD)
    url_w = url_bbox[2] - url_bbox[0]
    draw.line([(cx - url_w // 2, 582), (cx + url_w // 2, 582)],
              fill=AMBER, width=2)

    draw.text((cx, 640), "Link in first comment ↓",
              font=F_BODY_SM, fill=MUTED, anchor="mm")

    draw.line([(cx - 200, 700), (cx + 200, 700)], fill=(40, 25, 8), width=1)

    draw.text((cx, 738), "Based on John Maeda's DIT 2026 framework",
              font=F_SMALL, fill=DIM, anchor="mm")
    draw.text((cx, 766), "presented at SXSW 2026",
              font=F_SMALL, fill=DIM, anchor="mm")

    draw_brand(draw)
    draw_counter(draw, 5)
    return img

# ═══════════════════════════════════════════════════════════════════════════════
# Generate all slides
# ═══════════════════════════════════════════════════════════════════════════════
print("Generating slides...")
generators = [slide_1, slide_2, slide_3, slide_4, slide_5]
slides = []
png_paths = []
for i, gen in enumerate(generators, 1):
    s = gen()
    # Save JPG preview
    jpg_path = os.path.join(OUT_DIR, f"slide_0{i}.jpg")
    s.save(jpg_path, "JPEG", quality=95, optimize=True)
    # Save PNG for lossless PDF embedding
    png_path = os.path.join(OUT_DIR, f"slide_0{i}.png")
    s.save(png_path, "PNG")
    print(f"  slide_{i:02d}.jpg  ({os.path.getsize(jpg_path) // 1024} KB)")
    slides.append(s)
    png_paths.append(png_path)

# Build PDF from lossless PNGs — avoids double JPEG compression
from PIL import Image as PILImage
png_imgs = [PILImage.open(p).convert("RGB") for p in png_paths]
pdf_path = os.path.join(OUT_DIR, "carousel.pdf")
png_imgs[0].save(pdf_path, "PDF", save_all=True,
                 append_images=png_imgs[1:], resolution=300)
# Clean up temp PNGs
for p in png_paths:
    os.remove(p)

print(f"\nPDF: {pdf_path}  ({os.path.getsize(pdf_path) // 1024} KB)")
print(f"All files in: {OUT_DIR}")
