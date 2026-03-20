/**
 * Tree Visualization Engine — v2 Tree-Shaped Designer
 *
 * Ported from inconvergent/tree (MIT License, Anders Hoff).
 * Continuous growth simulation: branches grow step-by-step,
 * thinning linearly, splitting probabilistically. Thinner branches
 * curve more. Rendered with stippled grain shading.
 *
 * Original: https://github.com/inconvergent/tree
 */

(function() {
    'use strict';

    const W = 530, H = 540, CX = W / 2, GY = 285;
    const FONT = "system-ui, -apple-system, sans-serif";
    const PHI = 0.618;

    const ARC_R = [0, 48, 96, 144, 192, 240];
    const ARC_A = ARC_R;
    const ARC_B_RX = ARC_R;
    const ARC_B_RY = ARC_R;
    const SAE_X = [0, ARC_R[1], ARC_R[2], ARC_R[3], ARC_R[4], ARC_R[5]];
    const STAGES = ['', 'E', 'P', 'I', 'A', 'S'];
    const SNAMES = ['', 'Explorer', 'Practitioner', 'Integrator', 'Architect', 'Steward'];

    // Seeded PRNG
    let _s = 1;
    function rng() { _s = (_s * 16807) % 2147483647; return (_s & 0x7fffffff) / 2147483647; }
    function seed(n) { _s = Math.abs(n * 2654435761 | 0) || 1; }
    // Seeded normal distribution (Box-Muller)
    function normal() {
        const u1 = rng(), u2 = rng();
        return Math.sqrt(-2 * Math.log(u1 || 0.001)) * Math.cos(2 * Math.PI * u2);
    }

    const C = {
        bg: '#1a1a28', // fallback, overridden by sky/soil gradients
        skyTop: '#2a4a70', skyBottom: '#4a7aa0', // darker blue sky for white text contrast
        soilTop: '#3a3020', soilMid: '#2e2618', soilBottom: '#221c12',
        grassLine: '#3a5a2a', // subtle ground line
        grid: 'rgba(255,255,255,0.04)', // very subtle grid above ground
        gridSoil: 'rgba(255,255,255,0.03)', // even subtler below
        arcFill: 'rgba(255,255,255,0.06)', arcStroke: 'rgba(255,255,255,0.18)',
        arcRootFill: 'rgba(200,180,140,0.06)', arcRootStroke: 'rgba(200,180,140,0.15)',
        arcDim: 'rgba(255,255,255,0.08)',
        ground: '#6a8a3e',
        // Branch wood — dark brown, visible against green foliage
        wood: '#5a4228',
        woodStroke: '#2a1a0a',
        woodShade: 'rgba(20,14,6,0.45)',
        // Leaves
        leaf: ['#3a6e22','#4a7e2a','#5a8e34','#6a9e3e','#7aae48',
               '#8aba52','#9ac45c','#b8c44a','#c8b43a','#d4aa30'],
        // Root tones — warm earthy brown (not black)
        rootWood: '#7a6040',
        rootStroke: '#3a2e1a',
        rootShade: 'rgba(50,38,20,0.35)',
        // UI
        lblBg: 'rgba(20,30,50,0.8)', lblBgOn: 'rgba(50,45,25,0.9)', lblBgR: 'rgba(50,40,25,0.9)',
        lblStroke: 'rgba(200,200,220,0.6)', lblOn: 'rgba(230,200,110,0.8)', lblRon: 'rgba(220,190,110,0.75)',
        txt: '#ffffff', dim: '#ffffff',
        accent: '#e8c547', green: '#6ee7a0', yellow: '#fbbf24', red: '#f87171',
    };

    // ══════════════════════════════════════════════════════════════
    // TREE GROWTH ENGINE (ported from inconvergent/tree)
    // ══════════════════════════════════════════════════════════════

    function growTree(opts) {
        const {
            rootX, rootY, rootR, rootA,
            stepSize,
            splitAngle,
            probScale,
            diminish,
            splitDiminish,
            angleMax,
            angleExp,
            maxSteps,
            bounds,
        } = opts;

        // Each active branch tracks its full trajectory
        let Q = [{
            x: rootX, y: rootY, r: rootR, a: rootA,
            path: [{ x: rootX, y: rootY, r: rootR }],
        }];
        const branches = []; // completed branch paths

        let steps = 0;
        const MAX_ACTIVE = 150;

        while (Q.length > 0 && steps < maxSteps && branches.length < 500) {
            steps++;
            const newQ = [];
            const toRemove = new Set();

            for (let i = 0; i < Q.length; i++) {
                const b = Q[i];
                b.r -= diminish;

                if (b.r <= stepSize * 0.3) {
                    toRemove.add(i);
                    branches.push(b.path); // save completed path
                    continue;
                }

                // The magic: thinner branches curve more
                const scale = stepSize + rootR - b.r;
                const da = Math.pow(1 + scale / rootR, angleExp);
                b.a += da * normal() * angleMax;

                b.x += Math.cos(b.a) * stepSize;
                b.y += Math.sin(b.a) * stepSize;

                if (bounds && (b.x < bounds.minX || b.x > bounds.maxX ||
                    b.y < bounds.minY || b.y > bounds.maxY)) {
                    toRemove.add(i);
                    branches.push(b.path);
                    continue;
                }

                // Record point on this branch's path
                b.path.push({ x: b.x, y: b.y, r: b.r });

                // Probabilistic split
                const prob = Q.length < MAX_ACTIVE
                    ? (rootR - b.r + stepSize) * probScale : 0;

                if (rng() < prob) {
                    // Save current branch path up to here
                    branches.push([...b.path]);
                    // New child branch splits off
                    const newR = splitDiminish * b.r;
                    const ra = (rng() > 0.5 ? 1 : -1) * rng() * splitAngle;
                    newQ.push({
                        x: b.x, y: b.y, r: newR, a: b.a + ra,
                        path: [{ x: b.x, y: b.y, r: newR }],
                    });
                } else {
                    toRemove.add(i);
                    newQ.push(b);
                }
            }

            Q = Q.filter((_, i) => !toRemove.has(i));
            Q.push(...newQ);
        }

        // Save any still-active branches
        for (const b of Q) branches.push(b.path);

        return branches; // array of paths, each path = [{x,y,r}, ...]
    }

    // ══════════════════════════════════════════════════════════════
    // RENDERER — clean tapered filled shapes, no stipple noise
    // ══════════════════════════════════════════════════════════════

    function renderBranches(branchPaths, woodColor, strokeColor) {
        const parts = [];

        // Sort thick branches first (render behind)
        branchPaths.sort((a, b) => (b[0]?.r || 0) - (a[0]?.r || 0));

        for (const path of branchPaths) {
            if (path.length < 4) continue; // skip tiny fragments

            // Sample path at intervals for SVG efficiency
            const sampled = [path[0]];
            for (let i = 3; i < path.length - 1; i += 3) sampled.push(path[i]);
            sampled.push(path[path.length - 1]);
            if (sampled.length < 2) continue;

            // Build tapered filled shape
            const left = [], right = [];
            for (let i = 0; i < sampled.length; i++) {
                const p = sampled[i];
                let tx, ty;
                if (i === 0) { tx = sampled[1].x - p.x; ty = sampled[1].y - p.y; }
                else if (i === sampled.length - 1) { tx = p.x - sampled[i-1].x; ty = p.y - sampled[i-1].y; }
                else { tx = sampled[i+1].x - sampled[i-1].x; ty = sampled[i+1].y - sampled[i-1].y; }
                const tl = Math.sqrt(tx*tx + ty*ty) || 1;
                const nx = -ty / tl, ny = tx / tl;
                const hw = p.r * 0.5;
                left.push({ x: p.x + nx * hw, y: p.y + ny * hw });
                right.push({ x: p.x - nx * hw, y: p.y - ny * hw });
            }

            // Smooth bezier curves along both edges (not straight lines)
            let d = `M${left[0].x.toFixed(1)} ${left[0].y.toFixed(1)}`;
            for (let i = 1; i < left.length - 1; i++) {
                const mx = (left[i].x + left[i+1].x) / 2;
                const my = (left[i].y + left[i+1].y) / 2;
                d += ` Q${left[i].x.toFixed(1)} ${left[i].y.toFixed(1)} ${mx.toFixed(1)} ${my.toFixed(1)}`;
            }
            d += ` L${left[left.length-1].x.toFixed(1)} ${left[left.length-1].y.toFixed(1)}`;
            // Right edge backward with curves
            d += ` L${right[right.length-1].x.toFixed(1)} ${right[right.length-1].y.toFixed(1)}`;
            for (let i = right.length - 2; i > 0; i--) {
                const mx = (right[i].x + right[i-1].x) / 2;
                const my = (right[i].y + right[i-1].y) / 2;
                d += ` Q${right[i].x.toFixed(1)} ${right[i].y.toFixed(1)} ${mx.toFixed(1)} ${my.toFixed(1)}`;
            }
            d += ` L${right[0].x.toFixed(1)} ${right[0].y.toFixed(1)} Z`;

            const startR = path[0].r;
            // Thicker branches darker, thinner lighter
            const depthFrac = Math.min(1, sampled[0].r / 4);
            const op = Math.max(0.55, 0.65 + depthFrac * 0.3);
            parts.push(`<path d="${d}" fill="${woodColor}" stroke="${strokeColor}" stroke-width="0.3" opacity="${op.toFixed(2)}"/>`);
        }

        return parts.join('');
    }

    // ══════════════════════════════════════════════════════════════
    // CANOPY + ROOTS
    // ══════════════════════════════════════════════════════════════

    function _growCanopy(cw, ch) {
        const maxH = ARC_A[ch];
        const maxW = SAE_X[Math.min(cw, 5)];
        const trunkBaseW = (3 + ch * 1.0) * 1.4;

        // ── 1. Trunk ──
        const trunkH = maxH * 0.35;
        const trunkTopW = trunkBaseW * 0.25;
        const trunkTopY = GY - trunkH;
        const flareW = trunkBaseW * 1.3;
        const flareD = 6 + ch;
        let trunkSvg = `<path d="M${CX-flareW} ${GY+flareD} C${CX-flareW*0.7} ${GY+flareD*0.3} ${CX-trunkBaseW*1.1} ${GY} ${CX-trunkBaseW} ${GY} C${CX-trunkBaseW*0.9} ${GY-trunkH*0.3} ${CX-trunkTopW*1.5} ${GY-trunkH*0.7} ${CX-trunkTopW} ${trunkTopY} L${CX+trunkTopW} ${trunkTopY} C${CX+trunkTopW*1.5} ${GY-trunkH*0.7} ${CX+trunkBaseW*0.9} ${GY-trunkH*0.3} ${CX+trunkBaseW} ${GY} C${CX+trunkBaseW*1.1} ${GY} ${CX+flareW*0.7} ${GY+flareD*0.3} ${CX+flareW} ${GY+flareD} Z" fill="${C.wood}" opacity="0.92"/>`;
        trunkSvg += `<path d="M${CX-trunkBaseW*0.15} ${GY} C${CX-trunkBaseW*0.12} ${GY-trunkH*0.3} ${CX-trunkTopW*0.2} ${GY-trunkH*0.7} ${CX-trunkTopW*0.1} ${trunkTopY} L${CX+trunkTopW*0.1} ${trunkTopY} C${CX+trunkTopW*0.2} ${GY-trunkH*0.7} ${CX+trunkBaseW*0.12} ${GY-trunkH*0.3} ${CX+trunkBaseW*0.15} ${GY} Z" fill="#a89060" opacity="0.15"/>`;

        // ── 2. Space colonization canopy (same approach as roots) ──
        const numAttractors = 500 + ch * 200 + cw * 150;
        const attractors = [];
        let att = 0;
        while (attractors.length < numAttractors && att < numAttractors * 5) {
            att++;
            // V-shape within the semicircular canopy zone
            // Generate within the ellipse directly
            const angle = rng() * Math.PI;
            const rFrac = Math.pow(rng(), 0.65); // edge-weighted
            const x = CX + rFrac * maxW * Math.cos(angle);
            const y = GY - rFrac * maxH * Math.sin(angle);
            if (y >= GY - 8) continue;
            // Elliptical bounds: maxW wide, maxH tall
            const nx = (x - CX) / (maxW + 5);
            const ny = (GY - y) / (maxH + 5);
            if (nx*nx + ny*ny > 1) continue; // outside ellipse
            if (y > trunkTopY + 5) continue; // below trunk top
            attractors.push({ x, y });
        }

        // Seed: trunk line from ground to trunk top
        const nodes = [];
        const trunkSteps = 8;
        for (let i = 0; i <= trunkSteps; i++) {
            nodes.push({ x: CX, y: GY - (i/trunkSteps) * trunkH, parent: i > 0 ? i-1 : null, children: [], thickness: 0 });
        }

        // Space colonization — Webb's parameters
        const SEG_LEN = 5;
        const ATTRACT_DIST = 30;
        const KILL_DIST = 5;
        for (let iter = 0; iter < 300 && attractors.length > 0; iter++) {
            const influences = new Map();
            for (let ai = attractors.length - 1; ai >= 0; ai--) {
                const a = attractors[ai];
                let ci = -1, cd = Infinity;
                for (let ni = 0; ni < nodes.length; ni++) {
                    const d = Math.sqrt((a.x-nodes[ni].x)**2 + (a.y-nodes[ni].y)**2);
                    if (d < cd && d < ATTRACT_DIST) { cd = d; ci = ni; }
                }
                if (cd < KILL_DIST) { attractors.splice(ai, 1); continue; }
                if (ci >= 0) {
                    const n = nodes[ci];
                    const dx = a.x-n.x, dy = a.y-n.y, l = Math.sqrt(dx*dx+dy*dy)||1;
                    if (!influences.has(ci)) influences.set(ci, []);
                    influences.get(ci).push({ dx: dx/l, dy: dy/l });
                }
            }
            if (influences.size === 0 && iter > 10) break;
            for (const [ni, dirs] of influences) {
                let ax=0, ay=0;
                for (const d of dirs) { ax+=d.dx; ay+=d.dy; }
                ax /= dirs.length; ay /= dirs.length;
                ax += (rng()-0.5)*0.2; ay += (rng()-0.5)*0.2;
                const l = Math.sqrt(ax*ax+ay*ay)||1;
                const nn = { x: nodes[ni].x+(ax/l)*SEG_LEN, y: nodes[ni].y+(ay/l)*SEG_LEN, parent: ni, children: [], thickness: 0 };
                // Circular + V-shape bounds
                // Elliptical bounds: maxW wide, maxH tall
                if (nn.y > trunkTopY + 5 || nn.y < GY - maxH - 5) continue;
                const enx = (nn.x-CX)/(maxW+5), eny = (GY-nn.y)/(maxH+5);
                if (enx*enx + eny*eny > 1.05) continue;
                nodes[ni].children.push(nodes.length);
                nodes.push(nn);
            }
        }

        // Canalization
        for (let i = 0; i < nodes.length; i++) {
            if (nodes[i].children.length === 0) {
                let cur = nodes[i];
                while (cur.parent !== null) {
                    const parent = nodes[cur.parent];
                    if (parent.thickness < cur.thickness + 0.07)
                        parent.thickness = cur.thickness + 0.03;
                    cur = parent;
                }
            }
        }

        // Render branches
        const BASE_W = 1.0;
        let branchSvg = '';
        const segs = [];
        for (let i = 0; i < nodes.length; i++) { if (nodes[i].parent !== null) segs.push(i); }
        segs.sort((a,b) => nodes[b].thickness - nodes[a].thickness);
        for (const i of segs) {
            const n = nodes[i], p = nodes[n.parent];
            const w = BASE_W + n.thickness * 2.5;
            branchSvg += `<line x1="${p.x.toFixed(1)}" y1="${p.y.toFixed(1)}" x2="${n.x.toFixed(1)}" y2="${n.y.toFixed(1)}" stroke="${C.wood}" stroke-width="${w.toFixed(1)}" stroke-linecap="round" opacity="${Math.min(0.95, 0.4+n.thickness*0.3).toFixed(2)}"/>`;
        }

        // ── 3. Leaves — at tips AND along outer branches ──
        const leafParts = [];
        for (let i = 0; i < nodes.length; i++) {
            const n = nodes[i];
            const isTip = n.children.length === 0;
            const isOuter = n.thickness < 0.15;
            if (!isTip && !isOuter) continue;
            if (!isTip && rng() > 0.3) continue;
            if (n.y > trunkTopY + 5) continue; // no leaves below trunk top
            const numL = isTip ? (3 + Math.floor(rng() * 5)) : (1 + Math.floor(rng() * 3));
            for (let j = 0; j < numL; j++) {
                const lx = n.x + (rng()-0.5) * 14;
                const ly = n.y + (rng()-0.5) * 11 - 2;
                const lr = rng() < 0.3 ? (3+rng()*4.5) : (1.2+rng()*2.8);
                const lc = C.leaf[Math.floor(rng()*C.leaf.length)];
                const lo = rng() < 0.3 ? (0.25+rng()*0.2) : (0.45+rng()*0.4);
                leafParts.push(`<circle cx="${lx.toFixed(1)}" cy="${ly.toFixed(1)}" r="${lr.toFixed(1)}" fill="${lc}" opacity="${lo.toFixed(2)}"/>`);
            }
        }

        // Assemble: leaves BEHIND, then branches, then trunk ON TOP
        let svg = '';
        if (leafParts.length) svg += `<g class="tree-leaves">${leafParts.join('')}</g>`;
        svg += branchSvg;
        svg += trunkSvg;

        return svg;
    }

    // ══════════════════════════════════════════════════════════════
    // ROOT GROWTH — Space Colonization (Jason Webb approach)
    //
    // Scatter attractors in the root semicircle zone.
    // Seed nodes at trunk base. Roots grow toward attractors,
    // naturally filling the bounded zone. Canalization thickens
    // based on flow (thick near trunk, thin at tips).
    // ══════════════════════════════════════════════════════════════

    // ── Neighbor roots: fixed, pre-computed, same every time ──
    // Generated once from a big tree, then mirrored left/right.
    // They enter from the edges and reach ~40% toward center.
    // The main tree's roots must grow out to meet them.

    var _neighborCache = null;

    function _buildNeighborRoots() {
        if (_neighborCache) return _neighborCache;

        // Use a fixed seed so these are always identical
        var savedSeed = _s;
        seed(999888);

        var maxD = ARC_R[5]; // always use full depth
        var neighborCol = '#6a5a42';

        // Generate one side (right) — big tree roots entering from x=W
        var nodes = [];
        var numSeeds = 12;
        for (var i = 0; i < numSeeds; i++) {
            var frac = i / (numSeeds - 1);
            var y = GY + 6 + Math.pow(frac, 0.45) * maxD * 0.88;
            nodes.push({ x: W + 10, y: y, parent: null, children: [], thickness: 0 });
        }

        // Attractors from edge to ~40% toward center
        var attractors = [];
        for (var a = 0; a < 400; a++) {
            var x = CX + (0.3 + rng() * 0.75) * (W * 0.5);
            var y = GY + 6 + Math.pow(rng(), 0.45) * maxD * 0.9;
            attractors.push({ x, y });
        }

        // Space colonization
        for (var iter = 0; iter < 120 && attractors.length > 0; iter++) {
            var influences = new Map();
            for (var ai = attractors.length - 1; ai >= 0; ai--) {
                var at = attractors[ai];
                var ci = -1, cd = Infinity;
                for (var ni = 0; ni < nodes.length; ni++) {
                    var d = Math.sqrt((at.x-nodes[ni].x)**2 + (at.y-nodes[ni].y)**2);
                    if (d < cd && d < 35) { cd = d; ci = ni; }
                }
                if (cd < 8) { attractors.splice(ai, 1); continue; }
                if (ci >= 0) {
                    var n = nodes[ci];
                    var dx = at.x-n.x, dy = at.y-n.y, l = Math.sqrt(dx*dx+dy*dy)||1;
                    if (!influences.has(ci)) influences.set(ci, []);
                    influences.get(ci).push({ dx: dx/l, dy: dy/l });
                }
            }
            if (influences.size === 0) break;
            for (var [ni2, dirs] of influences) {
                var ax2=0, ay2=0;
                for (var dd of dirs) { ax2+=dd.dx; ay2+=dd.dy; }
                ax2 /= dirs.length; ay2 /= dirs.length;
                ax2 += (rng()-0.5)*0.18; ay2 += (rng()-0.5)*0.18;
                var ll = Math.sqrt(ax2*ax2+ay2*ay2)||1;
                var nn = { x: nodes[ni2].x+(ax2/ll)*6, y: nodes[ni2].y+(ay2/ll)*6, parent: ni2, children: [], thickness: 0 };
                if (nn.x < CX * 0.5 || nn.x > W+15 || nn.y < GY+3 || nn.y > GY+maxD+5) continue;
                nodes[ni2].children.push(nodes.length);
                nodes.push(nn);
            }
        }

        // Canalization
        for (var i2 = 0; i2 < nodes.length; i2++) {
            if (nodes[i2].children.length === 0) {
                var cur = nodes[i2];
                while (cur.parent !== null) {
                    var par = nodes[cur.parent];
                    if (par.thickness < cur.thickness + 0.07) par.thickness = cur.thickness + 0.03;
                    cur = par;
                }
            }
        }

        // Render right side
        var rightLines = [];
        for (var i3 = 0; i3 < nodes.length; i3++) {
            if (nodes[i3].parent === null) continue;
            var n3 = nodes[i3], p3 = nodes[n3.parent];
            var w3 = 0.5 + n3.thickness * 1.6;
            rightLines.push({ x1: p3.x, y1: p3.y, x2: n3.x, y2: n3.y, w: w3 });
        }

        // Mirror for left side (reflect x around CX)
        var leftLines = rightLines.map(function(ln) {
            return { x1: 2*CX - ln.x1, y1: ln.y1, x2: 2*CX - ln.x2, y2: ln.y2, w: ln.w };
        });

        // Build SVG string
        var svg = '';
        var allLines = leftLines.concat(rightLines);
        for (var ln of allLines) {
            svg += `<line x1="${ln.x1.toFixed(1)}" y1="${ln.y1.toFixed(1)}" x2="${ln.x2.toFixed(1)}" y2="${ln.y2.toFixed(1)}" stroke="${neighborCol}" stroke-width="${ln.w.toFixed(1)}" stroke-linecap="round"/>`;
        }

        // Restore original seed
        _s = savedSeed;
        _neighborCache = svg;
        return svg;
    }

    function _neighborRoots(rd) {
        // Always the same roots — just vary opacity by how deep the main tree's roots are
        // Deeper roots = more visible neighbors (they're more connected)
        return _buildNeighborRoots();
    }

    function _growRoots(rd) {
        const maxD = ARC_B_RY[rd];
        const maxW = ARC_B_RX[rd];
        const allRootPaths = [];
        const bounds = { minX: CX - maxW - 8, maxX: CX + maxW + 8, minY: GY - 3, maxY: GY + maxD + 8 };

        // Read trunk width from canopy params to fuse seamlessly
        const trunkBaseW = (3 + Math.min(rd, 5) * 1.0) * 1.4;

        // ── Space colonization for roots (Jason Webb approach) ──
        // Attractors biased shallow/horizontal. Seeds from trunk base.
        // Canalization for natural taper. Light color against dark soil.

        // ── Space colonization using Jason Webb's exact parameters ──
        // SegmentLength=5, AttractionDistance=30, KillDistance=5
        // Canalization: walk tips to root, parent.thickness = child.thickness + 0.03

        const numAttractors = 500 + rd * 200;

        // Attractors: scattered within the circular arc, surface-biased
        const attractors = [];
        let att = 0;
        while (attractors.length < numAttractors && att < numAttractors * 5) {
            att++;
            // Polar coordinates within the semicircle
            const angle = rng() * Math.PI; // 0 to PI (lower semicircle)
            const r = Math.pow(rng(), 0.4) * maxD; // surface-biased radius
            const x = CX + r * Math.cos(angle);
            const y = GY + r * Math.sin(angle);
            if (y <= GY + 3) continue;
            if (Math.abs(x - CX) < 6 && rng() > 0.2) continue;
            attractors.push({ x, y });
        }

        // Seed: single root node at trunk base (like Webb's approach)
        const nodes = [{ x: CX, y: GY + 3, parent: null, children: [], thickness: 0 }];

        // Grow trunk down first (Webb builds trunk before branching starts)
        for (let i = 0; i < Math.round(maxD * 0.15 / 5); i++) {
            const prev = nodes[nodes.length - 1];
            nodes.push({ x: CX + (rng()-0.5)*0.5, y: prev.y + 5, parent: nodes.length - 1, children: [], thickness: 0 });
            nodes[nodes.length - 2].children.push(nodes.length - 1);
        }

        // Space colonization loop — Webb's exact algorithm
        const SEG_LEN = 5;
        const ATTRACT_DIST = 30;
        const KILL_DIST = 5;
        const MAX_ITER = 300;

        for (let iter = 0; iter < MAX_ITER && attractors.length > 0; iter++) {
            // Associate each attractor with its closest node (Open venation)
            const influences = new Map();
            for (let ai = attractors.length - 1; ai >= 0; ai--) {
                const a = attractors[ai];
                let closestIdx = -1, closestDist = Infinity;
                for (let ni = 0; ni < nodes.length; ni++) {
                    const d = Math.sqrt((a.x-nodes[ni].x)**2 + (a.y-nodes[ni].y)**2);
                    if (d < closestDist && d < ATTRACT_DIST) { closestDist = d; closestIdx = ni; }
                }
                if (closestDist < KILL_DIST) { attractors.splice(ai, 1); continue; }
                if (closestIdx >= 0) {
                    const n = nodes[closestIdx];
                    const dx = a.x-n.x, dy = a.y-n.y, l = Math.sqrt(dx*dx+dy*dy)||1;
                    if (!influences.has(closestIdx)) influences.set(closestIdx, []);
                    influences.get(closestIdx).push({ dx: dx/l, dy: dy/l });
                }
            }
            if (influences.size === 0 && iter > 10) break;

            // Grow new nodes
            for (const [ni, dirs] of influences) {
                let ax=0, ay=0;
                for (const d of dirs) { ax+=d.dx; ay+=d.dy; }
                ax /= dirs.length; ay /= dirs.length;
                // Small jitter (Webb: random(-0.1, 0.1))
                ax += (rng()-0.5)*0.2; ay += (rng()-0.5)*0.2;
                const l = Math.sqrt(ax*ax+ay*ay)||1;
                const nn = {
                    x: nodes[ni].x + (ax/l)*SEG_LEN,
                    y: nodes[ni].y + (ay/l)*SEG_LEN,
                    parent: ni, children: [], thickness: 0,
                };
                // Circular bounds — stay within the arc semicircle, not a rectangle
                const dx2 = nn.x - CX, dy2 = nn.y - GY;
                if (dy2 < -3) continue; // don't grow above ground
                if (Math.sqrt(dx2*dx2 + dy2*dy2) > maxD + 5) continue; // stay within arc radius
                nodes[ni].children.push(nodes.length);
                nodes.push(nn);
            }
        }

        // Canalization — Webb's exact method: walk from each tip to root, +0.03 per level
        for (let i = 0; i < nodes.length; i++) {
            if (nodes[i].children.length === 0) { // tip node
                let cur = nodes[i];
                while (cur.parent !== null) {
                    const parent = nodes[cur.parent];
                    if (parent.thickness < cur.thickness + 0.07) {
                        parent.thickness = cur.thickness + 0.03;
                    }
                    cur = parent;
                }
            }
        }

        // Render: each segment as a line with thickness = BranchThickness + canalized thickness
        const BASE_W = 1.0;
        let svg = '';
        // Sort by thickness (thick behind thin)
        const segs = [];
        for (let i = 0; i < nodes.length; i++) {
            if (nodes[i].parent === null) continue;
            segs.push(i);
        }
        segs.sort((a, b) => nodes[b].thickness - nodes[a].thickness);

        for (const i of segs) {
            const n = nodes[i], p = nodes[n.parent];
            const w = BASE_W + n.thickness * 2.5; // scale up for visibility
            const op = Math.min(0.95, 0.4 + n.thickness * 0.3);
            svg += `<line x1="${p.x.toFixed(1)}" y1="${p.y.toFixed(1)}" x2="${n.x.toFixed(1)}" y2="${n.y.toFixed(1)}" stroke="#a08858" stroke-width="${w.toFixed(1)}" stroke-linecap="round" opacity="${op.toFixed(2)}"/>`;
        }
        return svg;
    }

    // ══════════════════════════════════════════════════════════════
    // MAIN
    // ══════════════════════════════════════════════════════════════

    function generateTreeSVG(viz, meta) {
        const rd = viz.root_depth, cw = viz.canopy_width, ch = viz.canopy_height;
        // Unique seed per person — same scores, different branch patterns
        const userSeed = viz.seed || (rd * 1000 + cw * 100 + ch * 10 + 7);
        seed(userSeed);
        let s = '';

        // Sky + soil background
        s += `<defs>
            <linearGradient id="skyG" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="${C.skyTop}"/><stop offset="100%" stop-color="${C.skyBottom}"/></linearGradient>
            <linearGradient id="soilG" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="${C.soilTop}"/><stop offset="50%" stop-color="${C.soilMid}"/><stop offset="100%" stop-color="${C.soilBottom}"/></linearGradient>
        </defs>`;
        // No rounded corners — full bleed to edges
        s += `<rect width="${W}" height="${GY}" fill="url(#skyG)"/>`;
        s += `<rect y="${GY}" width="${W}" height="${H-GY}" fill="url(#soilG)"/>`;
        // Grass line
        s += `<rect x="0" y="${GY-2}" width="${W}" height="4" fill="${C.grassLine}" opacity="0.4"/>`;
        s += _grid();
        s += _arcsBelow(rd);
        s += _arcsAbove(ch);
        s += _groundLine(cw, ch, rd);

        // Neighbor roots — other trees' roots entering from the sides
        // Density scales with root depth: Explorer = none, Steward = dense interlocking
        if (rd >= 2) s += `<g class="neighbor-roots" opacity="0.45">${_neighborRoots(rd)}</g>`;

        // Wrap the whole tree in one group for wind animation
        s += `<g class="tree-whole">`;
        if (rd > 0) s += `<g class="tree-roots">${_growRoots(rd)}</g>`;
        if (cw > 0 && ch > 0) {
            s += `<g class="tree-canopy">${_growCanopy(cw, ch)}</g>`;
        } else if (cw === 0) {
            // L0: dense bushy shrub on the ground
            const shrubW = 40 + rd * 20;
            const shrubH = 25 + rd * 12;
            const numBlobs = 6 + rd * 4;
            const numLeaves = 15 + rd * 8;
            let leafSvg = '';
            // Layer 1: blobby mass of foliage (like canopy blobs but at ground level)
            for (let b = 0; b < numBlobs; b++) {
                const bx = CX + (rng() - 0.5) * shrubW * 0.8;
                const by = GY - 3 - rng() * shrubH;
                const br = 8 + rng() * (8 + rd * 3);
                const bry = br * (0.5 + rng() * 0.3);
                const leafCol = C.leaf[Math.floor(rng() * C.leaf.length)];
                const op = 0.45 + rng() * 0.35;
                leafSvg += `<ellipse cx="${bx.toFixed(0)}" cy="${by.toFixed(0)}" rx="${br.toFixed(0)}" ry="${bry.toFixed(0)}" fill="${leafCol}" opacity="${op.toFixed(2)}"/>`;
            }
            // Layer 2: individual leaf shapes poking out
            for (let i = 0; i < numLeaves; i++) {
                const angle = rng() * Math.PI * 2;
                const dist = rng() * shrubW * 0.5;
                const lx = CX + Math.cos(angle) * dist;
                const ly = GY - 5 - rng() * shrubH * 0.9;
                const leafLen = 6 + rng() * (5 + rd * 2);
                const leafW = leafLen * (0.28 + rng() * 0.12);
                const rot = -90 + (rng() - 0.5) * 80; // mostly pointing up
                const leafCol = C.leaf[Math.floor(rng() * C.leaf.length)];
                const op = 0.5 + rng() * 0.4;
                const tip = leafLen;
                const cp = leafLen * 0.4;
                leafSvg += `<g transform="translate(${lx.toFixed(0)},${ly.toFixed(0)}) rotate(${rot.toFixed(0)})">`;
                leafSvg += `<path d="M0,0 Q${leafW.toFixed(0)},${cp.toFixed(0)} 0,${tip.toFixed(0)} Q${-leafW.toFixed(0)},${cp.toFixed(0)} 0,0 Z" fill="${leafCol}" opacity="${op.toFixed(2)}"/>`;
                leafSvg += `</g>`;
            }
            s += `<g class="tree-ground-leaves">${leafSvg}</g>`;
        }
        s += `</g>`;

        s += _labelsAbove(ch);
        s += _labelsBelow(rd);
        s += _footer(meta);

        return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" role="img" aria-label="Tree: ${meta.root_code}${meta.canopy_code ? ' / '+meta.canopy_code:''}. ${meta.balance}.">${s}</svg>`;
    }

    // ══════════════════════════════════════════════════════════════
    // FRAMEWORK (grid, arcs, ground, labels, footer)
    // ══════════════════════════════════════════════════════════════

    function _grid() {
        let s = '';
        for (let x = 50; x < W; x += 50) s += `<line x1="${x}" y1="0" x2="${x}" y2="${H}" stroke="${C.grid}" stroke-width="0.5"/>`;
        for (let y = 40; y < H; y += 50) s += `<line x1="0" y1="${y}" x2="${W}" y2="${y}" stroke="${C.grid}" stroke-width="0.5"/>`;
        return s;
    }
    function _arcsAbove(ch) {
        let s = '';
        for (let i = 5; i >= 1; i--) { const r = ARC_A[i]; s += `<path d="M${CX-r} ${GY} A${r} ${r} 0 0 1 ${CX+r} ${GY}" fill="none" stroke="${C.arcDim}" stroke-width="0.5"/>`; }
        return s;
    }
    function _arcsBelow(rd) {
        let s = '';
        for (let i = 5; i >= 1; i--) { const rx = ARC_B_RX[i], ry = ARC_B_RY[i]; s += `<path d="M${CX-rx} ${GY} A${rx} ${ry} 0 0 0 ${CX+rx} ${GY}" fill="none" stroke="${C.arcDim}" stroke-width="0.5" stroke-dasharray="3,5"/>`; }
        return s;
    }
    function _groundLine(cw, ch, rd) {
        let s = '';
        // L1-L5 labels just above the tree canopy height
        // Positioned between the user's top arc and the next unfilled arc above
        const topArc = Math.min(ch, 5);
        const labelY = GY - ARC_A[topArc] - (topArc < 5 ? (ARC_A[topArc+1] - ARC_A[topArc]) * 0.5 : 20);
        // "AI Automation" axis title above the L labels
        s += `<text x="${CX + SAE_X[1]}" y="${labelY - 22}" text-anchor="start" fill="#ffffff" font-size="9" letter-spacing="1.5" font-weight="400" font-family="${FONT}" opacity="0.6">AI AUTOMATION</text>`;
        for (let i = 1; i <= 5; i++) {
            const x = SAE_X[i];
            const selected = cw === i;
            const col = selected ? C.accent : C.dim;
            // Accent circle around selected L level
            s += `<text x="${CX+x}" y="${labelY}" text-anchor="middle" fill="${selected?'#ffffff':col}" font-size="12" font-weight="${selected?'700':'400'}" font-family="${FONT}" opacity="${selected?1.0:0.5}">L${i}</text>`;
        }
        // Ground line — clean, no clutter
        s += `<line x1="0" y1="${GY}" x2="${W}" y2="${GY}" stroke="${C.grassLine}" stroke-width="1.5" opacity="0.6"/>`;
        // L0 label centered below the taproot
        const maxD = ARC_B_RY[rd] || ARC_B_RY[1];
        const l0y = GY + maxD + 22; // below the outermost root arc
        s += `<text x="${CX}" y="${l0y}" text-anchor="middle" fill="${C.accent}" font-size="13" font-weight="700" font-family="${FONT}">L0</text>`;
        s += `<text x="${CX}" y="${l0y + 16}" text-anchor="middle" fill="#ffffff" font-size="9" letter-spacing="2.5" font-family="${FONT}" opacity="0.7">FUNDAMENTALS</text>`;
        return s;
    }
    function _labelsAbove(ch) {
        let s = '';
        const lx = 18;
        const topY = GY - ARC_A[5];
        s += `<text x="${lx}" y="${topY - 24}" text-anchor="start" fill="#ffffff" font-size="9" letter-spacing="1.5" font-weight="400" font-family="${FONT}" opacity="0.6">LEADERSHIP</text>`;
        for (let i = 1; i <= 5; i++) {
            const y = GY - ARC_A[i];
            const selected = ch === i; // only the exact level
            const col = selected ? C.txt : C.dim;
            const op = selected ? 1.0 : 0.5;
            // Accent ring around selected level
            s += `<circle cx="${lx}" cy="${y}" r="13" fill="${C.lblBg}" stroke="${C.lblStroke}" stroke-width="1"/>`;
            s += `<text x="${lx}" y="${y+4}" text-anchor="middle" fill="${selected?'#ffffff':col}" font-size="12" font-weight="700" font-family="${FONT}">${STAGES[i]}</text>`;
            s += `<text x="${lx+16}" y="${y+4}" fill="${selected?'#ffffff':col}" font-size="11" font-weight="${selected?'700':'400'}" font-family="${FONT}" opacity="${op}">${SNAMES[i]}</text>`;
        }
        return s;
    }
    function _labelsBelow(rd) {
        let s = '';
        const lx = 18;
        for (let i = 1; i <= 5; i++) {
            const y = GY + ARC_B_RY[i];
            const selected = rd === i;
            const col = selected ? C.txt : C.dim;
            const op = selected ? 1.0 : 0.5;
            s += `<circle cx="${lx}" cy="${y}" r="13" fill="${selected?C.lblBgR:C.lblBg}" stroke="${C.lblStroke}" stroke-width="1"/>`;
            s += `<text x="${lx}" y="${y+4}" text-anchor="middle" fill="${selected?'#ffffff':col}" font-size="12" font-weight="700" font-family="${FONT}">${STAGES[i]}</text>`;
            s += `<text x="${lx+16}" y="${y+4}" fill="${selected?'#ffffff':col}" font-size="11" font-weight="${selected?'700':'400'}" font-family="${FONT}" opacity="${op}">${SNAMES[i]}</text>`;
        }
        const by = GY + ARC_B_RY[5] + 24;
        // "FUNDAMENTALS" label moved to _groundLine, below L0
        return s;
    }
    function _footer(meta) {
        // Rendered at the TOP of the SVG, not bottom
        let s = '';
        const y = 18;
        const bc = {grounded:C.green,'deeply rooted':C.green,balanced:C.green,reaching:C.yellow,'top-heavy':C.red}[meta.balance]||C.dim;
        s += `<circle cx="${CX-60}" cy="${y-4}" r="3.5" fill="${bc}"/>`;
        s += `<text x="${CX}" y="${y}" text-anchor="middle" fill="#ffffff" font-size="14" font-weight="700" font-family="${FONT}"><tspan>${meta.root_code}</tspan>`;
        if (meta.canopy_code) s += `<tspan fill="#ccccdd"> / </tspan><tspan>${meta.canopy_code}</tspan>`;
        s += `</text>`;
        s += `<text x="${CX+65}" y="${y}" text-anchor="start" fill="${bc}" font-size="11" font-weight="600" font-family="${FONT}">${meta.balance}</text>`;
        return s;
    }

    // ══════════════════════════════════════════════════════════════
    // ORGANISM-ONLY — for forest view (no background/grid/arcs/labels)
    // Returns a <g> string centered at (CX, GY) = (265, 285).
    // The caller wraps it in translate/scale for positioning.
    // ══════════════════════════════════════════════════════════════

    function generateOrganismSVG(viz) {
        const rd = viz.root_depth, cw = viz.canopy_width, ch = viz.canopy_height;
        const userSeed = viz.seed || (rd * 1000 + cw * 100 + ch * 10 + 7);
        seed(userSeed);

        let s = '';
        if (rd > 0) s += `<g class="tree-roots">${_growRoots(rd)}</g>`;
        if (cw > 0 && ch > 0) s += `<g class="tree-canopy">${_growCanopy(cw, ch)}</g>`;
        return s;
    }

    // ══════════════════════════════════════════════════════════════
    // MINI ORGANISM — lightweight silhouette for forest view.
    // Filled shapes only: trunk trapezoid, canopy ellipse, root wedge.
    // ~1KB per tree vs ~200KB for the full organism.
    // ══════════════════════════════════════════════════════════════

    function generateMiniOrganismSVG(viz) {
        const rd = viz.root_depth, cw = viz.canopy_width, ch = viz.canopy_height;
        const userSeed = viz.seed || (rd * 1000 + cw * 100 + ch * 10 + 7);
        seed(userSeed);

        let s = '';

        // L0 forms: ground-level leaf cluster — no trunk, no height
        if (cw === 0 && ch === 0) {
            const spread = 12 + rd * 8;
            const numLeaves = 5 + rd * 3;
            for (let i = 0; i < numLeaves; i++) {
                const angle = rng() * Math.PI * 2;
                const dist = rng() * spread * 0.6;
                const lx = CX + Math.cos(angle) * dist;
                const ly = GY - 3 + Math.sin(angle) * dist * 0.3;
                const leafLen = 6 + rng() * (5 + rd * 2);
                const leafW = leafLen * (0.3 + rng() * 0.15);
                const rot = rng() * 360;
                const leafCol = C.leaf[Math.floor(rng() * C.leaf.length)];
                const op = 0.55 + rng() * 0.35;
                // Leaf shape: pointed oval using a path
                const tip = leafLen;
                const cp = leafLen * 0.4;
                s += `<g transform="translate(${lx.toFixed(0)},${ly.toFixed(0)}) rotate(${rot.toFixed(0)})">`;
                s += `<path d="M0,0 Q${leafW.toFixed(0)},${cp.toFixed(0)} 0,${tip.toFixed(0)} Q${-leafW.toFixed(0)},${cp.toFixed(0)} 0,0 Z" fill="${leafCol}" opacity="${op.toFixed(2)}"/>`;
                // Midrib
                s += `<line x1="0" y1="0" x2="0" y2="${tip.toFixed(0)}" stroke="rgba(60,90,30,0.3)" stroke-width="0.5"/>`;
                s += `</g>`;
            }
            return s;
        }

        // Tree dimensions scale with parameters.
        // Trunk height proportional to leadership (ch), width to SAE (cw).
        // Root depth invisible but stored for wind behavior.
        const trunkH = 30 + ch * 25;   // 30-155px tall trunk
        const trunkBotW = 4 + ch * 2;  // wider trunk for mature trees
        const trunkTopW = 2 + ch * 0.5;
        const canopyR = 15 + cw * 18;  // 15-105px radius canopy
        const canopyH = 20 + ch * 22;  // taller canopy for higher maturity

        // ── Trunk: visible brown line ──
        const trunkTopY = GY - trunkH;
        s += `<path d="M${CX-trunkBotW} ${GY+4} Q${CX-trunkBotW*0.8} ${GY-trunkH*0.3} ${CX-trunkTopW} ${trunkTopY} L${CX+trunkTopW} ${trunkTopY} Q${CX+trunkBotW*0.8} ${GY-trunkH*0.3} ${CX+trunkBotW} ${GY+4} Z" fill="${C.wood}" opacity="0.9"/>`;

        // ── Canopy: layered blobby circles that read as a tree crown ──
        if (cw > 0 && ch > 0) {
            const canopyCY = trunkTopY - canopyH * 0.3;
            // 3-5 overlapping circles for organic shape
            const nBlobs = 3 + Math.floor(rng() * 3);
            for (let b = 0; b < nBlobs; b++) {
                const bx = CX + (rng() - 0.5) * canopyR * 0.8;
                const by = canopyCY + (rng() - 0.5) * canopyH * 0.5;
                const br = canopyR * (0.5 + rng() * 0.5);
                const bry = br * (0.6 + rng() * 0.4); // slightly oval
                const leafCol = C.leaf[Math.floor(rng() * C.leaf.length)];
                const op = 0.55 + rng() * 0.3;
                s += `<ellipse cx="${bx.toFixed(0)}" cy="${by.toFixed(0)}" rx="${br.toFixed(0)}" ry="${bry.toFixed(0)}" fill="${leafCol}" opacity="${op.toFixed(2)}"/>`;
            }
            // Darker highlight blob in center
            const hCol = C.leaf[Math.floor(rng() * 5)]; // darker greens
            s += `<ellipse cx="${CX}" cy="${canopyCY}" rx="${(canopyR*0.4).toFixed(0)}" ry="${(canopyH*0.25).toFixed(0)}" fill="${hCol}" opacity="0.4"/>`;
        }

        // ── Roots: visible below ground line (GY) ──
        // Wrapped in class="mini-roots" so they can be hidden in Forest view.
        if (rd > 0) {
            const maxRootD = 20 + rd * 28;
            const numRoots = 2 + rd * 2;
            const rootCol = '#7a6030';

            let rootSvg = '';
            // Taproot
            const tapD = maxRootD * (0.6 + rng() * 0.3);
            const tapW = 2 + rd * 1.2;
            rootSvg += `<line x1="${CX}" y1="${GY+2}" x2="${CX + (rng()-0.5)*8}" y2="${GY + tapD}" stroke="${rootCol}" stroke-width="${(tapW * 2).toFixed(1)}" stroke-linecap="round" opacity="0.85"/>`;

            // Spreading roots — thick enough to be visible at small scale
            for (let i = 0; i < numRoots; i++) {
                const angle = (Math.PI * 0.2) + (i / (numRoots - 1)) * (Math.PI * 0.6);
                const len = (0.3 + rng() * 0.7) * maxRootD;
                const w = 3 + rng() * (3 + rd * 1.2);
                const bend = (rng() - 0.5) * 20;
                const ex = CX + Math.cos(angle) * len + bend;
                const ey = GY + Math.sin(angle) * len;
                const mx = CX + Math.cos(angle) * len * 0.4 + (rng()-0.5) * 15;
                const my = GY + Math.sin(angle) * len * 0.5;
                rootSvg += `<path d="M${CX} ${GY+2} Q${mx.toFixed(0)} ${my.toFixed(0)} ${ex.toFixed(0)} ${ey.toFixed(0)}" fill="none" stroke="${rootCol}" stroke-width="${w.toFixed(1)}" stroke-linecap="round" opacity="0.75"/>`;
            }
            s += `<g class="mini-roots">${rootSvg}</g>`;
        }

        return s;
    }

    // Export constants for forest layout
    window.TreeViz = { generateTreeSVG, generateOrganismSVG, generateMiniOrganismSVG, CX, GY, W, H };
})();
