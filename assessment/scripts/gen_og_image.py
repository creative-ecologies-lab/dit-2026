"""Generate OG image for aiskillsmap.noahratzan.com LinkedIn post.

Output: assessment/static/og-image.jpg (1200x627)

Run from repo root:
    python assessment/scripts/gen_og_image.py
"""

from PIL import Image, ImageDraw, ImageFont
import os

# ── Canvas ─────────────────────────────────────────────────────────────────
W, H = 1200, 627
img = Image.new("RGB", (W, H), "#0a0a0f")
draw = ImageDraw.Draw(img)

# ── Helpers ────────────────────────────────────────────────────────────────
def hex_to_rgb(h):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

# ── Fonts ──────────────────────────────────────────────────────────────────
FONTS = "C:/Windows/Fonts/"

def font(name, size):
    try:
        return ImageFont.truetype(FONTS + name, size)
    except Exception:
        return ImageFont.load_default()

f_bold    = font("arialbd.ttf", 52)
f_sub     = font("segoeui.ttf", 26)
f_label   = font("segoeui.ttf", 16)
f_url     = font("segoeui.ttf", 20)
f_tag     = font("segoeuib.ttf", 18)
f_tiny    = font("segoeui.ttf", 14)

# ── Colors ─────────────────────────────────────────────────────────────────
ACCENT      = "#0070f3"
ACCENT2     = "#8b5cf6"
WHITE       = "#ffffff"
MUTED       = "#6b6b80"
BORDER      = "#1e1e2e"

STAGE_COLORS = {
    "E": "#f59e0b",
    "P": "#10b981",
    "I": "#3b82f6",
    "A": "#8b5cf6",
    "S": "#ec4899",
}

# ── Background gradient ────────────────────────────────────────────────────
for y in range(H):
    t = y / H
    r = int(10 + t * 5)
    g = int(10 + t * 3)
    b = int(15 + t * 10)
    draw.line([(0, y), (W, y)], fill=(r, g, b))

# Subtle concentric circles top-left
for radius in range(280, 0, -18):
    intensity = int(12 * (1 - radius / 280))
    draw.ellipse([-radius + 100, -radius + 90, radius + 100, radius + 90],
                 outline=(0, 80, 180, intensity))

# ── Matrix grid (right side) ───────────────────────────────────────────────
STAGES = ["E", "P", "I", "A", "S"]
LEVELS = list(range(6))

GRID_X = 705
GRID_Y = 60
CELL_W = 78
CELL_H = 68
GAP    = 4

# Column headers (stages)
for ci, stage in enumerate(STAGES):
    cx = GRID_X + ci * (CELL_W + GAP) + CELL_W // 2
    cy = GRID_Y + 12
    draw.text((cx, cy), stage, font=f_tag, fill=hex_to_rgb(STAGE_COLORS[stage]), anchor="mm")

# Row headers + cells
for ri, level in enumerate(LEVELS):
    gy = GRID_Y + 40 + ri * (CELL_H + GAP)

    # Row label
    lbl_color = hex_to_rgb(ACCENT) if level > 0 else hex_to_rgb(MUTED)
    draw.text((GRID_X - 38, gy + CELL_H // 2), f"L{level}",
              font=f_tag, fill=lbl_color, anchor="mm")

    for ci, stage in enumerate(STAGES):
        cx = GRID_X + ci * (CELL_W + GAP)
        cy = gy

        is_highlight = level in (2, 3) and stage in ("P", "I", "A")
        is_peak      = level == 3 and stage == "I"

        cell_fill = (26, 37, 64) if is_highlight else (21, 21, 31)
        if is_peak:
            cell_fill = (26, 26, 58)

        sc = hex_to_rgb(STAGE_COLORS[stage])
        cell_outline = sc if is_highlight else (40, 40, 55)

        draw.rounded_rectangle(
            [cx, cy, cx + CELL_W, cy + CELL_H],
            radius=6,
            fill=cell_fill,
            outline=cell_outline,
            width=1,
        )

        if is_peak:
            dot_x = cx + CELL_W // 2
            dot_y = cy + CELL_H // 2
            a2 = hex_to_rgb(ACCENT2)
            draw.ellipse([dot_x - 10, dot_y - 10, dot_x + 10, dot_y + 10],
                         fill=(a2[0] // 2, a2[1] // 2, a2[2] // 2))
            draw.ellipse([dot_x - 5, dot_y - 5, dot_x + 5, dot_y + 5], fill=a2)
        elif is_highlight:
            dot_x = cx + CELL_W // 2
            dot_y = cy + CELL_H // 2
            draw.ellipse([dot_x - 4, dot_y - 4, dot_x + 4, dot_y + 4],
                         fill=(sc[0] // 2, sc[1] // 2, sc[2] // 2))

# Grid legend
grid_center_x = GRID_X + (5 * (CELL_W + GAP) - GAP) // 2
legend_y = GRID_Y + 6 * (CELL_H + GAP) + 50
draw.text((grid_center_x, legend_y), "SAE × E-P-I-A-S Framework",
          font=f_tiny, fill=hex_to_rgb(MUTED), anchor="mm")

# ── Left side — headline copy ───────────────────────────────────────────────
PAD = 60

# Eyebrow
draw.text((PAD, 100), "John Maeda's DIT 2026", font=f_tiny, fill=hex_to_rgb(ACCENT), anchor="lm")

# Headline
draw.text((PAD, 160), "Where are you on", font=f_bold, fill=hex_to_rgb(WHITE), anchor="lm")
draw.text((PAD, 228), "the AI skills map?", font=f_bold, fill=hex_to_rgb(WHITE), anchor="lm")

# Underline
bbox2 = draw.textbbox((0, 0), "the AI skills map?", font=f_bold)
draw.line([(PAD, 253), (PAD + bbox2[2], 253)], fill=hex_to_rgb(ACCENT), width=3)

# Sub-copy
draw.multiline_text((PAD, 290),
                    "3-minute self-assessment for designers\nand UX researchers using AI tools.",
                    font=f_sub, fill=hex_to_rgb(MUTED), spacing=8)

# Axis pills
def pill(x, y, text, color_hex):
    rgb = hex_to_rgb(color_hex)
    bbox = draw.textbbox((0, 0), text, font=f_label)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    px, py = 14, 8
    bg = (rgb[0] // 6, rgb[1] // 6, rgb[2] // 4)
    draw.rounded_rectangle([x, y, x + tw + 2 * px, y + th + 2 * py],
                            radius=20, fill=bg, outline=rgb, width=1)
    draw.text((x + px, y + py - 1), text, font=f_label, fill=rgb)
    return tw + 2 * px

x_pill, y_pill = PAD, 392
w1 = pill(x_pill, y_pill, "SAE Level  0 → 5", ACCENT)
pill(x_pill + w1 + 10, y_pill, "E-P-I-A-S Stage", ACCENT2)

# URL
draw.text((PAD, H - 70), "aiskillsmap.noahratzan.com",
          font=f_url, fill=hex_to_rgb(MUTED), anchor="lm")

# Divider
draw.line([(PAD, H - 50), (660, H - 50)], fill=hex_to_rgb(BORDER), width=1)

# Bottom tag
draw.text((PAD, H - 30), "Free · Anonymous · No login required",
          font=f_tiny, fill=(80, 80, 95), anchor="lm")

# Vertical separator
draw.line([(682, 40), (682, H - 40)], fill=hex_to_rgb(BORDER), width=1)

# ── Save ────────────────────────────────────────────────────────────────────
out = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "static", "og-image.jpg"))
img.save(out, "JPEG", quality=92, optimize=True)
print(f"Saved: {out}  ({os.path.getsize(out) // 1024} KB)")
