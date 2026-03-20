# Botany of Trees: A Design Report for Parametric SVG Tree Visualization

*Reference document for calibrating the Tree-Shaped Designer visualization.*
*March 2026*

---

## How to Use This Report

This report translates botanical research into actionable parameter ranges for an SVG fractal tree generator. Every section ends with a **Parameters** box giving specific numbers you can plug into code. The existing `tree-viz.js` parameter comments are referenced where relevant so you can see exactly what to adjust.

---

## Part I: Root Systems

### 1. Root Architecture Types

Real trees do not maintain a single root strategy for life. Most broadleaf trees germinate with a **taproot** (a single dominant descending root), but within one to a few years the root system transitions to a **wide-spreading fibrous system** with mainly horizontal surface roots and only a few vertical sinker roots.

**Taproot phase (young trees, deep-rooted species like oaks and hickories):**
- A single central root descends vertically, sometimes to 3-5 m in favorable soil.
- Lateral roots emerge from the taproot at regular intervals, each progressively thinner.
- The taproot tapers roughly as a **neiloid** (concave taper, exponent ~3) in its lowest third, transitioning to paraboloid taper (exponent ~1) in the upper portion.
- Visual character: a strong central axis with side branches radiating outward, like an inverted excurrent tree.

**Fibrous/heart root phase (mature broadleaf trees):**
- The original taproot often stunts or rots away entirely.
- The dominant structure becomes a dense mat of horizontal roots in the top 30-120 cm (12-48 inches) of soil.
- A few vertical "sinker roots" descend from major laterals to provide anchorage.
- Visual character: a broad, shallow plate radiating outward from the trunk base, with occasional downward plunges.

**Adventitious roots:**
- Emerge from the trunk base or lower stem rather than from existing roots.
- Common in willows, mangroves, and tropical figs (aerial roots).
- Visually they appear as a "skirt" or "buttress" flaring from the trunk base before diving into soil.

> **Parameters for the visualization:**
> - Taproot taper: start at trunk width * 0.45, taper to ~6% of trunk width at maximum depth (your current code does this well: `CX-tw*0.45` to `CX-tw*0.06`)
> - Taproot taper curve: use a cubic bezier with concave curvature (neiloid), not linear. The current quadratic is acceptable but a cubic with control points at 50% depth / 15% width would be more accurate.
> - For the "mature tree" look, the taproot should be visually subordinate to the lateral roots -- thinner than the widest lateral.

---

### 2. Root Branching Patterns

Root systems follow one of two dominant architectures, depending on species and soil conditions:

**Herringbone pattern:**
- Branches occur only on the central taproot.
- Laterals are all terminal links -- they do not produce further branches.
- Produces a clean, fishbone-like pattern. Common in trees adapted to nutrient-poor soil where exploration efficiency matters.

**Dichotomous/diffuse pattern:**
- Branching occurs on primary roots AND on lateral roots.
- Each lateral can produce sub-laterals, which produce sub-sub-laterals, creating a fractal branching network.
- This is the pattern most broadleaf trees use, and the pattern your recursive `_root()` function implements.

**Branching angles:**
Root branching angles are classified in three tiers:
- **Horizontal roots**: 0-30 degrees from horizontal
- **Inclined roots**: 30-60 degrees from horizontal
- **Vertical/sinker roots**: 60-90 degrees from horizontal

Most first-order lateral roots emerge from the taproot at **60-90 degrees relative to the parent root** (i.e., nearly perpendicular). They then curve gravitropically: shallow roots curve to near-horizontal within a few centimeters, while deeper roots maintain a steeper angle. The gravitropic setpoint angle (GSA) is highly variable -- lateral roots on the upper side of a horizontal parent root tend toward ~30 degrees from vertical, while those on the lower side grow more vertically (~90 degrees from horizontal = straight down).

**Inter-branch distances:**
Research across 40 species found median inter-branch distances ranging from **0.62 mm to 5.63 mm** (a nine-fold variation). Within a single species, the coefficient of variation is typically **0.5-0.8**, meaning branches are irregularly spaced. For trees specifically, inter-branch distances tend toward the higher end of this range (3-6 mm on fine roots, much larger on structural roots).

**Branching density changes with root order:**
- First-order laterals (off the taproot) are widely spaced: every 5-20 cm on major structural roots.
- Second-order laterals are more closely spaced: every 1-5 cm.
- Third-order and finer: every 0.5-2 cm.
- Fine rootlets (order 4+): spaced 0.5-5 mm apart.

On thinner parent roots, laterals tend to be MORE widely spaced (23 of 40 species showed this negative correlation between parent diameter and branching density). This is counterintuitive but important: fine roots are sparsely branched, while medium roots are densely branched.

> **Parameters:**
> - Root spread angle per fork: **0.42-0.50 rad** (24-29 degrees) -- your current `spreadAngle = 0.42 + depth * 0.08` is well-calibrated.
> - Root length decay per generation: **0.60-0.78** -- your `0.60 + rng() * 0.18` is correct.
> - Root width decay per generation: **0.50-0.68** -- your `0.50 + rng() * 0.18` is correct.
> - Number of sub-branches per fork: **2-3** (your current distribution is good).
> - Inter-branch spacing should be IRREGULAR: apply CV of 0.5-0.8 to the positioning along the parent root. Your `rng()` offsets partially achieve this.

---

### 3. Root-to-Shoot Ratio

The folk wisdom that "roots mirror the canopy" is **wrong**.

Measured root-to-shoot ratios (root biomass / shoot biomass) for trees:
- **General range**: 0.08 to 0.66, with 95% of measurements falling here
- **Smaller trees** (DBH < 10 cm): mean ratio ~0.38 (roots are ~38% of shoot mass)
- **Larger trees** (DBH > 30 cm): mean ratio ~0.27 (roots are only ~27% of shoot mass)
- **Extreme range**: 0.035 to 2.42 (some desert species invest enormously in roots)

In terms of **spatial extent**, roots spread far wider than the canopy:
- Maximum root spread ranges from **1.68x to 3.77x the canopy dripline radius**, depending on species.
- Southern magnolia: 3.77x dripline distance
- Green ash: 1.68x dripline distance
- Poplar: 2.9x dripline distance (77% of root length beyond the dripline)
- Sugar maple: roots extend 30 feet beyond branch tips

In terms of **visual volume**, the root system is shallower but wider than the canopy. The root system does NOT mirror the canopy shape. It is more like a very wide, shallow plate or disc.

> **Parameters:**
> - Root lateral spread should be **1.1-1.3x the canopy width** for a naturalistic look (your `maxSpread = maxD * 1.1` is at the low end -- consider 1.2-1.3 for larger trees).
> - Root depth should be roughly **0.4-0.7x the canopy height**. The current code uses roughly equal above/below arcs, which overemphasizes root depth. For botanical accuracy, the root zone should be squashed to about 60-70% of the canopy height.
> - However, for the "Tree Model" metaphor (L0 craft foundation), the conceptual value of showing deep roots may outweigh botanical accuracy. Consider this a deliberate stylistic choice.

---

### 4. Lateral Root Emergence

When lateral roots emerge from the taproot or a major structural root:

1. **Initial angle**: Laterals emerge at roughly **60-90 degrees** to the parent root axis (nearly perpendicular).
2. **Immediate curve**: Within the first few millimeters to centimeters, the root curves due to gravitropism.
3. **Shallow laterals** (the majority): curve from perpendicular to **near-horizontal** (0-30 degrees from horizontal) and then run outward for great distances, staying in the top 30-120 cm of soil.
4. **Sinker roots** (minority): maintain their steep angle or curve slightly, descending to 1-3 m. These are rare -- typically only a few per tree, emerging at intervals along major laterals.
5. **Pattern**: The overall shape of a lateral root system, viewed from the side, resembles a **very flat wine glass** -- roots emerge steeply from the taproot base, immediately curve to horizontal, and extend far outward.

The curve from vertical to horizontal is botanically important and visually distinctive. It follows an exponential approach to the horizontal, not a circular arc:
```
angle(distance) = initial_angle * e^(-k * distance)
```
where k is a gravitropic sensitivity constant. In practice, this means the root makes its sharpest turn close to the parent and then gradually levels off.

> **Parameters:**
> - In `_root()`, the `baseAngle` calculation already handles the horizontal-bias gradient. But consider adding a **curvature bias toward horizontal** in the first segment of each root: the `downBias = 0.05` gravitropism should be complemented by a **horizontal pull** for shallow roots (frac < 0.3). Try: `if (depth === 0 && frac < 0.3) midAngle += side * 0.15` to curve shallow roots outward before they fork.
> - The initial emergence angle from the taproot should be steeper (more perpendicular to the taproot) than the current implementation suggests. Currently shallow roots emerge already aimed outward; botanically, they should emerge more steeply and then curve.

---

### 5. Fine Root Networks

Root orders are classified from the tips inward:
- **Order 1** (finest rootlets): diameter 0.1-0.3 mm, length 1-10 mm. No further branching. These are the absorbing tips.
- **Order 2**: diameter 0.3-0.5 mm, bearing 2-5 order-1 rootlets.
- **Order 3**: diameter 0.5-1.0 mm, bearing 3-8 order-2 branches.
- **Order 4+**: diameter > 1 mm, transitioning to structural/transport roots.

Fine roots (orders 1-3) have these visual characteristics:
- They form dense clusters at the tips of structural roots, like the bristles of a bottlebrush.
- Branching is **irregular** -- not symmetrically bifurcating but stochastically distributed along the parent.
- Total fine root length in a mature tree can exceed **several hundred kilometers** per tree.
- Fine roots are concentrated in the **top 20 cm** of soil, in the organic/humus layer.
- Their visual density creates a "haze" or "cloud" at the periphery of the root system -- not individual lines but a mass.

> **Parameters:**
> - At recursion depths 4-6 (the finest root levels), consider rendering roots not as individual paths but as a **semi-transparent cloud or stipple pattern**: many very short, thin strokes radiating from the tip of each order-3 root.
> - Fine root stroke width: **0.3-0.8 px** (your minimum cutoff of 0.3 is appropriate).
> - Fine root opacity: **0.15-0.30** (lower than structural roots).
> - At the deepest recursion levels, increase the number of sub-branches to 3-5 but make each very short (length * 0.3-0.4).

---

### 6. Root Depth vs. Spread

This is one of the most important proportions for visual accuracy:

**For trees, the ratio of lateral spread to rooting depth is approximately 3:1.**

That is, roots typically spread **three times wider than they are deep**. Specific data:
- Trees: lateral-to-depth ratio geometric mean = **3.0**
- Shrubs: ~1.0
- Grasses: ~0.3-0.35

Most tree roots are in the **top 48 inches (120 cm)** of soil. The common mental model of roots as a "mirror image" of the canopy descending deep into the earth is a myth. In reality:
- 80-90% of root biomass is in the top 60 cm of soil.
- Maximum rooting depth for most broadleaf trees: 1-2 m (exceptions: desert species, some oaks to 5 m+).
- Maximum lateral spread: 10-30 m from the trunk (species-dependent).

The root system is shaped more like a **dinner plate** than an inverted tree.

> **Parameters:**
> - Root zone aspect ratio: aim for width ~3x depth for botanical accuracy.
> - The current code uses `ARC_B` (below-ground arc radii) that are roughly equal to `ARC_A` (above-ground). For realism, the root arcs should be wider and shallower: e.g., `ARC_B = [0, 60, 112, 164, 216, 268]` (wider) with max depth reduced to ~70% of the above-ground height.
> - Again, the metaphorical value of showing deep roots may take priority over literal botanical accuracy.

---

## Part II: Canopy & Branch Formation

### 1. Branch Architecture

The two fundamental branching strategies in trees:

**Monopodial (excurrent) growth:**
- A single dominant central leader (apical meristem) grows continuously upward.
- Lateral branches emerge from the leader but never outgrow it.
- Creates a **conical/pyramidal crown** (spruce, fir, sweetgum, pin oak, liquidambar).
- The trunk is visible all the way to the top.
- Branch angles are relatively uniform and increase slightly from top to bottom.

**Sympodial (decurrent/deliquescent) growth:**
- The central leader eventually stops elongating or is outgrown by lateral branches.
- Multiple branches compete for dominance, and the trunk "dissolves" into the crown.
- Creates **round, vase-shaped, or spreading crowns** (most oaks, maples, elms, beeches).
- No single trunk is visible in the upper crown -- instead, several co-dominant stems radiate outward.
- This is the pattern most relevant to the "Tree-Shaped Designer" visualization.

**What determines the form:**
1. Location of leaf and flower buds (terminal vs. lateral)
2. Pattern of bud break along the trunk
3. Differential elongation rates of terminal vs. lateral buds
4. These patterns are **genetically determined** -- environment modifies expression only under extreme conditions.

In decurrent species (oaks, elms, maples), shoots exhibit strong **apical dominance** during the season they're growing, but **weak apical control** over subsequent years. This means the terminal leader grows vigorously each season, but lateral branches from previous years grow almost as fast, eventually overtaking the leader.

> **Parameters:**
> - For a decurrent (broadleaf) tree shape, the trunk should "dissolve" at **55-75% of total tree height**. Above this point, there is no single dominant axis -- only branching.
> - Your current code does this implicitly: the trunk extends to `maxH * 0.88` and then adds a thin central leader extension. This is appropriate for a tree transitioning from trunk to crown.
> - The point of trunk dissolution should vary with tree "maturity" (EPIAS stage): Explorer trees should have a more visible central leader (more excurrent), while Steward trees should have a fully dissolved crown (more decurrent).

---

### 2. Branching Angles

**Species-specific measurements:**

| Species | Typical Branch Angle from Trunk | Crown Shape |
|---------|--------------------------------|-------------|
| European beech (*Fagus*) | 30-50 degrees (mean ~50 degrees vertical insertion) | Broad oval |
| Red maple (*Acer rubrum*) | ~45 degrees | Rounded oval |
| Red oak (*Quercus rubra*) | 45-70 degrees (wide terminal angles) | Broad, spreading |
| White oak (*Quercus alba*) | 50-80 degrees | Very wide, spreading |
| Elm (*Ulmus*) | 30-45 degrees (lower), 20-35 degrees (upper) | Vase-shaped |
| Pin oak (*Q. palustris*) | 30-45 degrees (upper), 80-100 degrees (lower, drooping) | Pyramidal |

**How angle changes with position in the crown:**
- **Lower branches**: wider angles (50-80 degrees from trunk), often sweeping nearly horizontal or even drooping below horizontal in older trees.
- **Middle branches**: moderate angles (35-55 degrees).
- **Upper branches**: narrower angles (20-40 degrees), more vertical, competing with the leader.
- This gradient is called **acrotony** (upper branches are more vigorous) combined with gravitational bending of lower branches.

**Structural thresholds:**
- Crotch angles **less than 25 degrees** are structurally unsound (included bark, weak attachment).
- Ideal structural attachment: **45-60 degrees** (bark ridge fully developed).
- Angles **less than 17 degrees** are considered failure-prone.

**Branching angle in sub-branching (Fagus crenata measured data):**
- Main branch insertion: 30.5 +/- 15.0 degrees (basal)
- Sub-branch angles: 20.6 +/- 15.3 degrees
- For the conifer *Abies homolepis*: consistently 14.7 +/- 7.8 degrees (much less variation)

> **Parameters:**
> - Your current `horizontalBias` gradient is the right approach. Refine the angle calculation:
>   - Bottom branches (frac < 0.3): base angle = **55-75 degrees** from vertical = 0.96-1.31 rad from -PI/2
>   - Middle branches (frac 0.3-0.6): **40-55 degrees** from vertical = 0.70-0.96 rad
>   - Top branches (frac > 0.6): **25-40 degrees** from vertical = 0.44-0.70 rad
> - Add variation: +/- 15 degrees (0.26 rad) random offset per branch (your current `rng() * 0.12` is too conservative -- increase to `rng() * 0.26`).
> - The fork angle in sub-branching (`spreadAngle`): 0.45-0.80 rad (26-46 degrees). Your `0.45 + depth * 0.06` reaches 0.81 at max depth, which is correct.

---

### 3. Branch Taper

Branch diameter decreases from trunk to tip following a **compound curve**, not a simple linear or exponential decay. Forestry models describe stem taper as a composite of three geometric solids:

| Stem Region | Geometric Model | Taper Exponent | Visual Character |
|-------------|----------------|----------------|------------------|
| Base (butt swell) | Neiloid | 3 | Concave, flaring outward rapidly |
| Mid-stem | Paraboloid | 1 | Gentle, near-linear taper |
| Upper stem / tip | Cone | 2 | Convex, narrowing to a point |

The formula relating diameter to distance from tip:
```
d(h) = D * (1 - h/H)^(1/r)
```
where D is base diameter, H is total length, h is distance from base, and r is the geometric exponent (3 for neiloid, 1 for paraboloid, 2 for cone).

**Branch-to-trunk diameter ratios:**
- Scaffold branches should be **less than 75%** of trunk diameter at point of attachment.
- In well-formed trees, primary branches are typically **40-65%** of trunk diameter.
- Secondary branches: **50-70%** of parent branch diameter.
- Tertiary branches: **50-65%** of parent diameter.
- This recursive decay means branch diameter at generation n relative to trunk is roughly:
  ```
  d_n / d_trunk = 0.6^n  (approximate)
  ```
  Generation 1: 60%, Generation 2: 36%, Generation 3: 22%, Generation 4: 13%, Generation 5: 8%.

> **Parameters:**
> - Width decay per generation: **0.52-0.68** (your current `0.52 + rng() * 0.16` is well-calibrated).
> - The trunk itself should taper using a **paraboloid curve** (exponent 1): `width(y) = baseWidth * sqrt(1 - y/height)`. Your current cubic bezier trunk approximates this but is slightly too linear. Adjust the control points to create more flare at the base.
> - Branch width at attachment point: enforce maximum of **0.75 * trunk_width_at_that_height**. Currently your branch width is calculated independently -- consider clamping it.

---

### 4. Apical Dominance and Crown Dissolution

**How the trunk "dissolves" into the crown:**

In excurrent trees (conifers, pin oak, sweetgum), the trunk is visible from base to tip. The central leader maintains dominance throughout the tree's life. The crown is a cone of lateral branches radiating from a central axis.

In decurrent trees (most broadleaf species), a critical transition occurs:
1. **Young tree**: strong central leader, conical form (looks excurrent).
2. **Juvenile**: leader begins to slow relative to upper laterals.
3. **Mature**: the top 2-4 lateral branches grow as vigorously as the leader, creating a "multi-stemmed" upper crown.
4. **Old tree**: the original leader is completely lost among co-dominant stems. The crown becomes a dome or irregular mass of major limbs.

The **live crown ratio** (LCR = crown length / total height) tells you how much of the tree is "living crown" vs. bare trunk below:

| Crown Class | Typical LCR |
|-------------|-------------|
| Open-grown broadleaf | 60-80% |
| Dominant (forest) | 45-50% |
| Codominant | 37-42% |
| Intermediate | 35-38% |
| Suppressed | 28-35% |

For the visualization, an open-grown tree (which is what the metaphor implies -- a tree with space to develop its full form) should have **60%+ of its height as living crown** and only 20-40% as bare trunk below the first branch.

**Half or more of a well-formed tree's foliage originates from branches in the lower two-thirds of the trunk.** This means branch density and leaf mass are concentrated LOW, not evenly distributed or top-heavy.

> **Parameters:**
> - First branch origin: at **8-20% of total height** from ground (your `frac` starting at 0.08 is correct).
> - Branch origins should cover the range from 8-86% of height (your current range) but with **denser spacing in the lower half**: consider a non-linear distribution where more origins cluster between 15-50% of height.
> - The central leader extension above the topmost branch should be thin (< 15% of trunk base width) and short (< 15% of total height). Your current implementation is appropriate.

---

### 5. Crown Shape

What determines whether a tree is round, vase-shaped, columnar, or spreading:

**Round-crowned (oaks, maples, lindens):**
- Moderate apical dominance that weakens with age.
- Branches at 40-60 degrees from trunk, with roughly equal vigor.
- Height roughly equals crown width. Aspect ratio ~1:1.
- Lower branches droop slightly under their own weight (flexion).

**Vase-shaped (elms, zelkova):**
- Long single trunk extending to 40-60% of height before branching.
- Major branches emerge at 30-45 degrees, sweep upward and outward.
- Crown is WIDER at the top than at the branching point.
- Aspect ratio: height ~1.2-1.5x width, but the crown alone is wider than tall.

**Columnar/fastigiate (lombardy poplar, columnar oak):**
- Very strong apical dominance maintained throughout life.
- Branches at 10-20 degrees from trunk (nearly vertical).
- Height 3-5x width. Very narrow.

**Spreading/horizontal (white oak, valley oak, live oak):**
- Weak apical dominance, very wide branch angles (60-90 degrees).
- Lower branches may sweep below horizontal.
- Width 1.5-2x height. Very broad.

**The key proportions for a "generic broadleaf" tree:**
- Total height : crown width = approximately **1:0.8 to 1:1.2** (roughly as wide as tall).
- Trunk height (to first major branch) : total height = **0.15 to 0.35**.
- Crown height : crown width = approximately **0.7:1 to 1:1** (crown is slightly wider than it is tall).

**The characteristic broadleaf silhouette** has these features:
- An irregular dome or oval outline (not a perfect circle).
- A visible gap between the ground and the lowest branches.
- The widest point is typically at **40-60% of crown height** (below center), not dead center.
- The outline has a "lumpy" quality with individual major limbs pushing the silhouette outward at irregular points.

> **Parameters:**
> - Crown width should be controlled by `SAE_X` (which maps to canopy_width). For a botanically proportioned tree, total crown width (both sides) should be roughly **0.8-1.2x the crown height**.
> - The widest branch reach should occur at branches originating from **30-50% of total height** (not the midpoint of the crown, but lower).
> - Branch lengths should follow a bell curve along the trunk: short at the bottom (close to ground, less light), maximum at 30-50% height, decreasing toward the top. Your `horizontalBias` partially achieves this.

---

### 6. Branch Density and Fill

**How branches fill the canopy volume:**

Branches do NOT fill the canopy evenly. The distribution is:
- **Peripheral shell**: The densest branching (and all the leaves) is concentrated in the outer 1-2 m of the canopy -- the "light-intercepting surface."
- **Interior**: Relatively open. In mature trees, the interior of the crown is largely bare due to self-shading. Interior branches die and are shed (natural pruning).
- **Top vs. bottom**: In unthinned forest trees, leaf area is **skewed toward the top of the crown**. In open-grown trees, it is more evenly distributed but still concentrated peripherally.

The result is that a tree crown is more like a **hollow shell** than a solid mass. Think of it as a brain coral -- dense on the surface, with a sparser interior framework of structural branches connecting the surface to the trunk.

**Branch density by order:**
- First-order branches (from trunk): 4-12 per tree, depending on species and size.
- Second-order (from primary branches): 2-5 per primary branch.
- Third-order: 2-4 per secondary.
- Fourth-order: 2-3 per tertiary.
- Total branch tips on a large oak: **100,000 to 200,000**.

**Leaf area index (LAI)** for broadleaf deciduous trees: typically **4-8 m^2 of leaf per m^2 of ground**. This means the canopy outline represents several overlapping layers of foliage, not a single surface.

> **Parameters:**
> - Your recursion depth of 4-6 levels is correct for producing the right density.
> - Terminal branches (deepest recursion) should cluster near the OUTER boundary of the canopy, not fill the interior evenly. Consider adding a **radial bias**: at deep recursion levels, branches should tend outward (away from CX, GY-midcrown) rather than curving back inward.
> - The interior of the crown should have visible gaps -- structural branches visible through the canopy. This is achieved naturally by your opacity gradient (inner branches more opaque, outer more transparent), but you could enhance it by reducing the number of sub-branches for branches that point back toward the trunk center.

---

### 7. Leonardo da Vinci's Rule and Branch Width

**The rule**: At any cross-section through a tree, the sum of the cross-sectional areas of all branches equals the cross-sectional area of the trunk.

Mathematically: **d_parent^alpha = d_child1^alpha + d_child2^alpha + ...**

Where alpha is the scaling exponent:
- **da Vinci's original rule**: alpha = 2 (area-preserving)
- **Murray's Law**: alpha = 3 (optimized for fluid transport in vascular systems)
- **Measured in real trees**: alpha = **1.8 to 3.0**, with most broadleaf trees near **2.0-2.5**

**What different alpha values look like:**

| Alpha | Visual Effect | Number of branches (10x trunk diameter contrast) | Natural analog |
|-------|---------------|---------------------------------------------------|----------------|
| 1.5 | Very detailed, many thin branches | ~32 | Dense tropical crowns |
| 2.0 | Classic tree proportions | ~100 | Temperate broadleaf |
| 2.5 | Moderate detail | ~316 | Measured average |
| 3.0 | Fewer, thicker branches | ~1,000 | Vines, some tropical trees |

**Translating to visual branch widths in SVG:**

If a parent branch has width W and splits into two children of equal size:
- alpha = 2: each child has width = W * 0.707 (= W / sqrt(2))
- alpha = 2.5: each child has width = W * 0.758
- alpha = 3: each child has width = W * 0.794

For **asymmetric** splits (one dominant child, one subordinate):
- If the dominant child is 80% of parent area: d_dominant = W * 0.894, d_subordinate = W * 0.447

The rule works well for **older, thicker branches and the trunk** but breaks down for thin new growth, where reaction wood, bending forces, and growth timing create deviations. This is actually useful: it means your fine-branch rendering can be less mathematically precise without looking wrong.

**Aesthetic research findings (from artwork analysis):**
- The Sidi Saiyyed Mosque jali (iconic Islamic tree carving, 16th century): alpha = **2.5 +/- 0.4**
- Gustav Klimt's *Tree of Life*: alpha = **1.7-1.9 +/- 0.3**
- Piet Mondrian's *De grijze boom*: alpha = **~3.0**
- Japanese screen painting (Goshun's Cherry Blossoms): alpha = **1.4-1.5 +/- 0.1** (extremely detailed, many fine branches)

Artists consistently choose alpha values in the **1.5-2.5 range**, which produces visually richer trees than the strict biological alpha of 2.5-3.0.

> **Parameters:**
> - Your current width decay of `0.52 + rng() * 0.16` (mean 0.60) for a binary split implies:
>   - Two children each at 0.60 * parent width means combined area = 2 * (0.60)^2 = 0.72 of parent area. This corresponds to alpha ~2.5 (area decreases slightly per level). When you have 3 children at 0.60: combined area = 3 * 0.36 = 1.08 (slight area increase). This averages out to roughly area-preserving, which is alpha ~2.0.
> - This is a good range. For a **more detailed, artistic** look, decrease width decay to 0.50-0.55 (lower alpha, more branches visible). For a **bolder, structural** look, increase to 0.65-0.72 (higher alpha, fewer visible branches).
> - Consider making alpha a user-facing parameter tied to the tree "species" metaphor: Oak (alpha 2.0-2.2), Maple (alpha 2.2-2.5), Birch (alpha 1.6-1.8).

---

## Part III: Visual Characteristics

### 1. What Makes a Tree "Look Right"

The single most common failure mode of procedural trees is **excessive symmetry and regularity**. A tree that looks "computer-generated" typically has:
- Perfectly symmetric left-right branching
- Uniform branch spacing
- Consistent branch angles at each level
- Smooth, predictable curves
- Regular taper without bumps or irregularities

A tree that looks "real" has:
- **Slight left-right asymmetry**: one side of the crown is always slightly larger/denser than the other.
- **Irregular spacing**: branches are clustered in some areas and sparse in others.
- **Variable angles**: each branch departs at a slightly different angle from its parent.
- **Gnarly lower branches**: smaller branches twist and curl more than large ones (gnarliness inversely proportional to branch radius).
- **Dead zones**: gaps in the canopy where branches have been lost or shaded out.
- **Weight-induced droop**: lower, longer branches sag below their initial growth angle.

**The "gnarliness" principle** is the single most impactful realism parameter: smaller branches should twist and deviate from their growth direction MORE than larger branches. Research on procedural tree generation consistently identifies this as "having the biggest impact on making a tree feel alive instead of sterile and static." The formula:
```
gnarliness = base_gnarl / branch_radius
```
This means a branch with half the radius twists twice as much, creating the organic, tortuous fine-branch character that is immediately recognizable.

**Environmental response cues** that add realism:
- **Phototropism**: branches tend slightly upward and toward light. Even in a symmetric tree, the tips curve upward.
- **Gravity response**: long horizontal branches droop. The longer and heavier the branch, the more it sags.
- **Wind exposure**: trees exposed to prevailing wind develop asymmetric crowns (flagging), with denser growth on the leeward side.
- **Self-pruning**: the interior of the crown is bare. Branches that don't receive light die and fall off, leaving the characteristic bare lower trunk and hollow interior.

> **Parameters:**
> - Increase random angle variation from 0.12 rad to **0.20-0.30 rad** for a more organic look.
> - Add **gnarliness** to the curve calculation: `curve = (rng() - 0.5) * (0.35 + 0.5 / w)` where w is branch width. This makes thin branches twist more.
> - Add **gravity droop** for branches below 40% of crown height: apply a downward angular bias of `0.02 * len / maxW` for long, low branches.
> - Add **asymmetry**: at the top level (branch origins from trunk), give one side 1-2 more branches than the other, or make one side's branches 10-15% longer.
> - The **phototropism** upward bias of 0.06 rad in your current code is botanically sound. Consider making it slightly stronger (0.08-0.10 rad) for terminal branches (deep recursion).

---

### 2. Asymmetry and Variation

Natural trees exhibit asymmetry at multiple scales:

**Macro-asymmetry (crown outline):**
- Crown eccentricity in forest-grown trees: one radius direction is typically **10-30% longer** than the perpendicular radius.
- Open-grown trees are more symmetric but never perfectly so.
- The asymmetry direction is consistent (driven by light, wind, or slope), not random.

**Meso-asymmetry (branch arrangement):**
- Major branches are NOT equally spaced around the trunk. They cluster in bands separated by gaps.
- The spiral phyllotaxis of bud placement means branches emerge at ~137.5-degree rotational intervals (the golden angle), but many buds fail to develop, creating irregular actual spacing.

**Micro-asymmetry (fine branching):**
- Each branch fork is slightly asymmetric: one child is dominant (longer, thicker) and one is subordinate (shorter, thinner). Perfectly equal forks are rare in nature.
- The dominant child tends to continue roughly in the parent's direction, while the subordinate diverges more sharply.

**The "sweet spot" of asymmetry:**
Neuroscience research on visual perception confirms that slight asymmetry (what researchers call the "sweet spot of perceptual fluency") is perceived as more natural, beautiful, and inviting than either perfect symmetry or pure randomness. People report feeling more relaxed viewing naturally varied trees than identical pruned specimens.

> **Parameters:**
> - At each fork, make children **unequal**: the dominant child should get `len * (0.70-0.85)` and the subordinate `len * (0.50-0.65)`. Your current uniform `len * (0.62 + rng() * 0.16)` for all children treats them equally. Consider: `childLen = len * (isFirst ? (0.72 + rng()*0.13) : (0.52 + rng()*0.13))`.
> - Similarly for width: dominant child at `w * (0.62-0.72)`, subordinate at `w * (0.45-0.55)`.
> - Add a **global asymmetry** parameter: multiply all branch lengths on one side by 1.05-1.15 and the other by 0.85-0.95. Seed this from the deterministic PRNG.
> - At each 3-way fork, one branch should be clearly dominant (continuing the parent's trajectory), one moderate (diverging 20-30 degrees), and one clearly subordinate (diverging 40-50 degrees and being thinnest).

---

### 3. The Silhouette

A recognizable tree silhouette has these properties:

**Overall proportions:**

| Tree Type | Height : Width | Trunk : Crown Height | Crown Shape |
|-----------|---------------|---------------------|-------------|
| Generic broadleaf | 1 : 0.8-1.0 | 1:3 to 1:4 | Oval/dome |
| Oak | 1 : 1.0-1.3 | 1:3 to 1:5 | Broad dome, low branches |
| Maple | 1 : 0.7-0.9 | 1:2.5 to 1:3.5 | Round oval |
| Elm | 1 : 0.7-0.9 | 1:1.5 to 1:2 (long trunk) | Vase/fan |
| Birch | 1 : 0.4-0.6 | 1:2 to 1:3 | Narrow oval |

**The silhouette envelope:**
The outline of a tree crown is NOT a smooth ellipse. It is:
- **Lumpy**: individual major limbs push the outline outward at irregular points.
- **Indented**: gaps between major branch clusters create visible notches in the outline.
- **Flat-bottomed**: the lowest branches create a roughly horizontal lower boundary (especially in open-grown trees).
- **Rounded at top**: but with the apex slightly off-center and possibly with a few individual twigs extending above the main mass.
- **Widest below center**: typically at 40-60% of crown height from the bottom of the crown (not the geometric center).

**What makes a tree silhouette instantly recognizable as "tree" (not bush, cloud, or blob):**
1. A visible vertical trunk connecting ground to crown.
2. The trunk TAPERS (wider at base, narrower where it enters the crown).
3. Branches are visible within the crown -- the crown is not a solid fill but a **tracery of branches with gaps**.
4. The outline is irregular but structured -- lumpy, not random.
5. There is a clear separation between trunk and crown (a "neck" where the trunk enters the branch zone).
6. The crown has more mass than the trunk -- it is the dominant visual element.

> **Parameters:**
> - Ensure the **trunk base width** is visually significant: at least 2-3% of total tree width. Your current `bw = 4 + min(cw+ch, 8) * 0.7` gives a maximum trunk base width of ~10 px in a 500 px SVG, which is 2% -- at the low end.
> - The **trunk top width** should be ~20-25% of trunk base width (your `tw = bw * 0.22` is correct).
> - The crown should occupy **60-80% of the total tree height** (your arc system achieves this).
> - Branch visibility within the crown matters: branches should NOT be fully hidden behind a solid canopy fill. The branches ARE the crown in this visualization, which is the right approach.

---

## Summary: Master Parameter Table

| Parameter | Botanical Range | Current Code Value | Recommended Adjustment |
|-----------|----------------|-------------------|----------------------|
| Branch angle, bottom | 55-80 deg from vertical | ~64 deg (horizontalBias * PI/2.8) | Good, increase variation to +/-15 deg |
| Branch angle, top | 25-40 deg from vertical | ~24 deg | Good |
| Branch length decay | 0.62-0.78 per generation | 0.62-0.78 | Correct |
| Branch width decay | 0.52-0.68 per generation | 0.52-0.68 | Correct; consider asymmetric splits |
| Fork count | 2-3 per node | 2-3 (biased 55% toward 3) | Consider dominant/subordinate hierarchy |
| Fork spread angle | 0.45-0.80 rad | 0.45-0.81 rad | Correct |
| Recursion depth | 4-6 levels | 4-6 | Correct |
| Phototropism bias | 0.06-0.10 rad upward | 0.06 rad | Increase slightly for fine branches |
| Gnarliness | inversely proportional to radius | flat 0.35 curve factor | Add `0.5/w` term |
| Random angle variation | +/- 0.20-0.30 rad | +/- 0.12 rad | Increase to 0.20-0.26 |
| Root spread : depth ratio | 3:1 | ~1:1 (equal arcs) | Consider widening root arcs |
| Root lateral emergence | 60-90 deg from parent | variable | Add initial-steep-then-curve behavior |
| Root gravitropism | 0.05 rad downward | 0.05 | Correct |
| Trunk dissolution height | 55-75% of total height | 88% (trunk extends very high) | Consider dissolving lower |
| Live crown ratio | 60-80% (open grown) | ~80% (first branch at 8%) | Correct |
| Crown width : height | 0.8-1.2 : 1 | Variable via SAE | Ensure proportionality |
| Global asymmetry | 10-30% side-to-side | None (symmetric seeds) | Add 5-15% length bias |

---

## Appendix: Species Archetypes for the Tree Model

These map to the designer taxonomy from `tree-model-draft.md`:

**Grass (L1 Explorer)**: No trunk. Dense, uniform, low to ground. Width >> height. Render as many thin vertical strokes from the ground line, no branching hierarchy.

**Birch (L1 Steward)**: Tall, narrow. Single visible trunk to 60% of height. Fine, delicate branches at 25-35 degrees. Crown width ~0.4-0.6x height. Alpha ~1.6-1.8 (many fine branches). White/light trunk.

**Maple (L2 Steward)**: Medium proportions. Trunk dissolves at ~50% height. Round crown, width ~0.8-1.0x height. Branch angles 40-55 degrees. Alpha ~2.2-2.5. Dense, regular canopy.

**Oak (L3 Steward)**: Broad, massive. Short trunk (20-30% of height), trunk dissolves early. Very wide crown, width ~1.0-1.3x height. Branch angles 50-80 degrees. Alpha ~2.0-2.2. Gnarly, characterful branches. Pronounced asymmetry.

**Fig/Banyan (L5 Explorer)**: No visible trunk. Aerial roots creating new trunks. Extremely wide spread, low height. Width ~2-3x height. Multiple trunks. Dense, layered canopy.

**Redwood (L5 Steward)**: Extremely tall, narrow base, massive trunk visible for 50-60% of height. Crown in upper portion. Height ~3-4x crown width. Alpha ~2.0. Deep root system. Very thick trunk relative to crown.

---

*Sources consulted for this report: PMC/PLOS One studies on tree branching biomechanics, ISA Arboriculture & Urban Forestry journal, PNAS Nexus fractal scaling research, The Grove 3D tree modeling research, USDA Forest Service taper equations, multiple botanical reference texts on root architecture and crown structure.*
