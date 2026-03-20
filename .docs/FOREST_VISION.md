# The Forest — Vision Document

*March 18, 2026*

---

## What It Is

The Forest replaces the heatmap as the community view. Instead of a 6×5 grid showing counts per cell, it's a **landscape of trees** — each representing a participant's assessment result. You see an ecosystem, not a spreadsheet.

## How It Looks

- Same cross-section view as the individual tree: sky above, ground line, soil below
- Multiple trees planted on a shared landscape, varying in size and shape
- Each tree is generated with the same `tree-viz.js` engine — same quality, same leaves, same roots, same neighbor root network
- Trees vary by: canopy width (SAE level), canopy height (EPIAS), root depth, and balance
- The overall impression: a diverse forest with different forms coexisting

## How It Moves

- A single **"Winds of change"** slider controls wind for the ENTIRE forest
- As wind increases, all trees sway together
- At higher wind levels, the top-heavy trees blow away while deeply rooted trees barely move
- The contrast is the whole point: you SEE which forms survive and which don't
- The balanced trees, the deeply rooted trees — they hold. The top-heavy ones vanish.

## What It Shows

- **Total participant count**
- **Proportions**: how many are balanced, deeply rooted, reaching, top-heavy
- If a **group ID** is provided, it shows that cohort's forest (e.g., a team of 20)
- The forest is illustrative, not a literal 1:1 mapping of every participant

## The Concern: Latency

Each tree currently takes ~40ms to generate via space colonization. The SVG output is 200-1000KB per tree.

- **20 trees** (a cohort): ~800ms generation, ~10MB SVG — feasible
- **100 trees**: ~4 seconds, ~50MB — slow, heavy
- **500 trees** (global heatmap): ~20 seconds, ~250MB — not viable

The trees cannot be rendered 1:1 at the current quality level for large participant counts. This is the central technical challenge.

## The Solution Direction: Binned Forms

The forest is **illustrative, not literal**. Not every participant gets their own tree.

Instead, participants are **binned by form** — grouped into clusters that share the same shape. If 47 people scored L0-P / L2-P, that's ONE tree in the forest representing 47 people, perhaps with a subtle count indicator or slightly larger presence.

The number of unique forms is bounded: root depth (1-5) × canopy width (0-5) × canopy height (0-5) = **130 possible forms**. In practice, most participants cluster into 15-30 common forms.

So the forest renders **15-30 trees** regardless of whether there are 50 or 5,000 participants. Each tree represents a bin. The SIZE or VISUAL WEIGHT of each tree could indicate how many people share that form.

This makes rendering fast (~1-2 seconds) and keeps the SVG manageable (~5-15MB).

---

*Latency proposals to follow from specialized agent.*
