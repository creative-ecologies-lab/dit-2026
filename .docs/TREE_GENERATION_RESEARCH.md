# Programmatic Tree Generation: Research Report

*March 2026 — Research for the Tree-Shaped Designer visualization*

---

## Search Strategy

These search queries produced the best results:

1. `"procedural tree generation" beautiful`
2. `"generative tree art" SVG javascript`
3. `"L-system tree" art beautiful`
4. `"space colonization tree" 2D`
5. `"fractal tree" art codepen`
6. `"botanical illustration" generative code`
7. `"tree visualization" organic SVG`
8. `"landscape architecture" procedural generation`
9. `"algorithmic botany" code`
10. `"tree of life" visualization generative`

---

## Top 5 Projects

### 1. Jason Webb — 2D Space Colonization Experiments (THE GOLD STANDARD)

- **URL:** https://github.com/jasonwebb/2d-space-colonization-experiments
- **Live demo:** https://jasonwebb.github.io/2d-space-colonization-experiments/
- **Stars:** 216 | **Language:** Vanilla ES6 + Canvas
- **What it does:** Suite of interactive experiments implementing space colonization for 2D morphogenesis — leaf venation, tree branching, coral fans, root systems. Includes open/closed venation modes, bounding shape constraints, obstacle avoidance, and auxin flux canalization (progressive vein thickening).
- **Visual quality:** Genuinely stunning. The canalization produces naturalistic tapered veins. The "from images" mode grows branching constrained by photographic silhouettes. Opacity blending creates watercolor-like atmosphere.
- **What to borrow:**
  - **Auxin flux canalization** — computing thickness by accumulating child counts upstream (we already use this)
  - **Network.js** — graph data structure for branching with parent/child relationships
  - **Attractor distribution strategies** — random, edge-based, image-masked
  - To adapt for SVG: replace `ctx.lineTo()` with `<path>` elements
- **Companion:** [jasonwebb/morphogenesis-resources](https://github.com/jasonwebb/morphogenesis-resources) (2,204 stars) — definitive curated list of morphogenesis algorithms

---

### 2. Anders Hoff (inconvergent) — Differential Line + Sand Spline + Trees

- **URLs:**
  - https://github.com/inconvergent/differential-line (696 stars, Python)
  - https://github.com/inconvergent/sand-spline (309 stars, Python)
  - https://inconvergent.net/generative/trees/ (essay on tree algorithms)
- **What it does:** Highest aesthetic standard in open-source generative art. `differential-line` grows intricate non-self-intersecting curves. `sand-spline` renders splines by scattering thousands of semi-transparent grains along paths — produces unmistakable hand-drawn quality. Trees essay describes a branch-tip-only growth algorithm.
- **Visual quality:** Museum-grade. Exhibited internationally, published in "On Generative Algorithms." Output looks like fine pen-and-ink botanical illustration.
- **Tech stack:** Python (Cairo rendering, SVG export). Newer framework `weird` is Common Lisp.
- **What to borrow:**
  - **Sand-spline rendering** — scatter many tiny semi-transparent circles along each branch path instead of clean strokes. Creates organic texture impossible with vector strokes alone.
  - **Differential line growth** for bark/root textures as secondary detail layer
  - **Tip-only branching rule** from trees essay — simpler than full space colonization, good for fast rendering

---

### 3. Andrew Herman (hippiefuturist) — Fractal Tree Generator (SVG + Golden Ratio)

- **URLs:**
  - https://codepen.io/hippiefuturist/full/KRromj (SVG version, interactive)
  - https://codepen.io/hippiefuturist/pen/NRWOxM (Canvas version)
  - https://codepen.io/hippiefuturist/post/on-the-fractal-tree-generator (write-up)
- **What it does:** Recursive fractal tree using Phi (golden ratio, 1.618) as branch scale ratio. Adjustable parameters: branch count, angle, spiral factor, recursion depth, color. SVG output.
- **Visual quality:** Surprisingly beautiful for pure fractal. Golden ratio scaling produces naturally proportioned trees. The "spiral factor" creates wind-shaped cypresses and twisted bonsai forms.
- **Tech stack:** Pure JavaScript, SVG output, no dependencies.
- **What to borrow:**
  - **Golden ratio branch scaling** — use phi (0.618) as default branch-length decay. More natural than arbitrary ratios.
  - **Spiral factor** — skipping certain branch angles creates asymmetric, wind-shaped forms. Easy parameter to add.
  - **Clean single-file SVG approach** — closest architectural match to our ~560 line target
  - Limitation: no space colonization or tapering. Combine with #1 and #2.

---

### 4. msiric — Procedural Plants (L-Systems Playground)

- **URL:** https://github.com/msiric/procedural-plants
- **Stars:** 5 | **Language:** JavaScript (Canvas)
- **What it does:** Interactive L-systems playground with presets for distinct plant forms. Adjustable axioms, production rules, colors, widths, leaf styles. Animated generation — watch the plant grow stroke by stroke.
- **Visual quality:** Good. The animated generation is compelling. Presets include realistic ferns, bushy shrubs, and conifers. Smooth color transitions from brown trunk to green tips.
- **What to borrow:**
  - **L-system grammar for leaf placement** — use production rules to determine where leaves appear, more botanically plausible than random
  - **Animated growth rendering** — stroke-by-stroke drawing order creates "growing" animation, adaptable to SVG with CSS animation delays
  - **Preset system** — named presets with pre-configured rules, good UX pattern
  - Limitation: L-systems alone produce mathematically regular trees. Combine with space colonization.

---

### 5. kldtz — ABOP (Algorithmic Beauty of Plants in SVG)

- **URL:** https://github.com/kldtz/abop
- **Output gallery:** https://verzettelung.com/23/11/27/
- **Language:** JavaScript, npm, outputs SVG
- **What it does:** Direct implementation of figures from Prusinkiewicz & Lindenmayer's "The Algorithmic Beauty of Plants." Parametric L-systems including context-sensitive rules, stochastic productions, and turtle graphics. Pure SVG output.
- **Visual quality:** Faithful to the ABOP plates — canonical reference for algorithmic plant illustration. Precise, scientific-illustration quality. Clean, elegant, authoritative.
- **What to borrow:**
  - **Parametric L-system engine** — most complete JS implementation of ABOP's grammar
  - **SVG output pipeline** — already generates clean SVG, closest architectural match
  - **Context-sensitive rules** — branch behavior changes based on neighbors (e.g., branch next to fruit grows shorter)
  - Limitation: L-system purity, no space colonization. Best as rule engine feeding into growth system.

---

## Honorable Mentions

| Project | URL | Stars | Why Notable |
|---------|-----|-------|-------------|
| **ez-tree** (dgreenheck) | https://github.com/dgreenheck/ez-tree | 1,239 | Most popular procedural tree lib (Three.js/3D). Excellent parameter system. |
| **proctree.js** (supereggbert) | https://github.com/supereggbert/proctree.js | 191 | Classic procedural tree mesh generator. Branching algorithm is portable to 2D. |
| **Nervous System Floraform** | https://n-e-r-v-o-u-s.com/projects/tags/algorithm/albums/floraform-system/ | N/A | Differential growth on elastic surfaces. Not open source. Use inconvergent as proxy. |
| **Andy Lomas Morphogenetic Creations** | V&A collection | N/A | Cell-based growth simulation. The north star for emergent form from simple rules. |
| **The Coding Train - Algorithmic Botany** | https://thecodingtrain.com/tracks/algorithmic-botany/ | N/A | Daniel Shiffman's p5.js tutorials. Best learning resource for understanding the algorithms. |
| **Algorithmic Botany (U of Calgary)** | https://algorithmicbotany.org/ | N/A | Academic home of L-systems. ABOP book free PDF. |

---

## Synthesis: Recipe for a Beautiful SVG Tree

Based on all research, the optimal recipe for our ~560-line `tree-viz.js`:

| Layer | Source | Purpose |
|-------|--------|---------|
| **Growth algorithm** | Jason Webb (#1) | Space colonization fills bounded canopy shape naturally |
| **Branch thickness** | Webb's auxin flux canalization | Tip-to-root width accumulation = da Vinci's rule |
| **Branch proportions** | hippiefuturist (#3) | Golden ratio (phi = 0.618) for length decay |
| **Rendering** | inconvergent (#2) | Sand-spline grain scattering for organic texture |
| **Leaf placement** | msiric (#4) or kldtz (#5) | L-system rules for botanical leaf distribution |
| **SVG architecture** | kldtz (#5) | Clean programmatic SVG in vanilla JS |

### Three Techniques We Haven't Tried Yet

1. **Sand-spline rendering** (from inconvergent) — scatter hundreds of tiny semi-transparent `<circle>` elements along each branch path instead of solid strokes. Creates the hand-drawn look that distinguishes art from diagrams.

2. **Golden ratio branch decay** (from hippiefuturist) — replace our current `0.62 + rng() * 0.16` decay with phi (0.618) as the base ratio. Mathematically proven to produce the most natural-looking proportions.

3. **Animated growth** (from msiric) — render branches in order from trunk to tips with staggered CSS animation delays. The tree "grows" when the page loads. Could be done with SVG path `stroke-dashoffset` animation.

---

## Key References

- **ABOP Book (free PDF):** https://algorithmicbotany.org/papers/abop/abop.pdf
- **Jason Webb's morphogenesis resources:** https://github.com/jasonwebb/morphogenesis-resources
- **inconvergent's generative algorithms book/site:** https://inconvergent.net/generative/
- **Tyler Hobbs on flow fields:** https://tylerxhobbs.com/essays/2020/flow-fields
- **Pomax's Bezier primer (offset curves):** https://pomax.github.io/bezierinfo/
- **Steve Ruiz's perfect-freehand (SVG tapering):** https://github.com/steveruizok/perfect-freehand

---

*This report supports the Tree-Shaped Designer v2 visualization for the DIT 2026 assessment tool.*
