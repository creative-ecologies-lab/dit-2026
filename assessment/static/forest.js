/**
 * Forest visualization — community view.
 *
 * Grid layout: X = SAE level (0-5), Y = canopy height (0-5).
 * Each cell can hold multiple trees with different root depths.
 * Root depth is INVISIBLE — revealed only when wind blows.
 *
 * Uses pre-generated organism-only SVGs via <image> tags.
 * Data format: { counts: { "r3_c2_h3": 5, ... }, total: 500 }
 */

(function() {
    'use strict';

    var container = document.getElementById('forestTrees');
    var countEl = document.getElementById('forestCount');
    var statsEl = document.getElementById('forestStats');
    var windSlider = document.getElementById('forestWind');
    var windValue = document.getElementById('forestWindValue');
    var windLabels = ['calm', 'breeze', 'gusty', 'storm', 'hurricane'];

    var counts = HEATMAP_DATA.counts || {};

    // ── Parse tree keys into structured list ──
    var treeTypes = [];
    var totalParticipants = 0;

    for (var key in counts) {
        if (counts[key] <= 0) continue;
        var m = key.match(/^r(\d+)_c(\d+)_h(\d+)$/);
        if (!m) continue;
        var rd = parseInt(m[1]);
        var cw = parseInt(m[2]);
        var ch = parseInt(m[3]);

        // Balance / wind vulnerability
        var demand = cw * 2 + ch * 2;
        var capacity = rd * 5;
        var ratio = capacity > 0 ? demand / capacity : 99;
        var balance;
        if (cw === 0) balance = 'grounded';
        else if (ratio <= 0.6) balance = 'deeply rooted';
        else if (ratio <= 1.1) balance = 'balanced';
        else if (ratio <= 1.8) balance = 'reaching';
        else balance = 'top-heavy';

        var maxLean = {grounded:2, 'deeply rooted':5, balanced:12, reaching:30, 'top-heavy':75}[balance] || 10;
        var breakAt = maxLean > 50 ? 0.55 : maxLean > 20 ? 0.85 : 99;

        treeTypes.push({
            key: key,
            filename: key + '.svg',
            count: counts[key],
            rd: rd, cw: cw, ch: ch,
            balance: balance,
            maxLean: maxLean,
            breakAt: breakAt,
        });
        totalParticipants += counts[key];
    }

    countEl.textContent = totalParticipants + ' participants' + (GROUP ? ' in ' + GROUP : '');

    // ── Stats ──
    var balanceCounts = {};
    treeTypes.forEach(function(t) {
        balanceCounts[t.balance] = (balanceCounts[t.balance] || 0) + t.count;
    });
    var statsHtml = '';
    ['deeply rooted', 'balanced', 'grounded', 'reaching', 'top-heavy'].forEach(function(b) {
        var n = balanceCounts[b] || 0;
        if (n === 0) return;
        var pct = Math.round(n / totalParticipants * 100);
        var col = {'deeply rooted':'#4ade80', balanced:'#4ade80', grounded:'#4ade80', reaching:'#fbbf24', 'top-heavy':'#f87171'}[b];
        statsHtml += '<span class="forest-stat"><span class="forest-stat-dot" style="background:' + col + '"></span>' + b + ' ' + pct + '%</span>';
    });
    statsEl.innerHTML = statsHtml;

    // ── Expand tree types into individual trees ──
    // Cap visual trees so the SVG stays responsive
    var MAX_VISUAL = 200;
    var scale_f = totalParticipants > MAX_VISUAL ? MAX_VISUAL / totalParticipants : 1;

    var allTrees = [];
    treeTypes.forEach(function(t) {
        var n = Math.max(1, Math.round(t.count * scale_f));
        for (var i = 0; i < n; i++) {
            allTrees.push({
                filename: t.filename,
                rd: t.rd, cw: t.cw, ch: t.ch,
                balance: t.balance,
                maxLean: t.maxLean,
                breakAt: t.breakAt,
                seed: t.rd * 100000 + t.cw * 10000 + t.ch * 1000 + i * 137 + 42,
            });
        }
    });

    // Seeded PRNG
    function srand(s) {
        s = Math.abs(s * 16807 | 0) % 2147483647 || 1;
        return (s & 0x7fffffff) / 2147483647;
    }

    // ── SVG layout constants ──
    var SVG_W = 1100;
    var SVG_H = 700;
    var PAD_L = 70, PAD_R = 30, PAD_T = 40, PAD_B = 50;
    var PLOT_W = SVG_W - PAD_L - PAD_R;
    var PLOT_H = SVG_H - PAD_T - PAD_B;

    // Grid: 6 columns (cw 0-5) × 6 rows (ch 0-5)
    // ch=5 at top (Steward, far back), ch=0 at bottom (no canopy maturity)
    // cw=0 at left (Manual), cw=5 at right (Full Automation)
    var COL_W = PLOT_W / 6;
    var ROW_H = PLOT_H / 6;

    // Organism SVG dimensions
    var ORG_W = 530, ORG_H = 540, ORG_GY = 285;

    // Tree scale: smaller in back rows (perspective), bigger in front
    function treeScale(ch) {
        // ch 5 = back (small), ch 0 = front (bigger)
        return 0.10 + (5 - ch) * 0.022;
    }

    // ── Sort: back rows first (ch=5 rendered behind ch=0) ──
    allTrees.sort(function(a, b) {
        if (a.ch !== b.ch) return b.ch - a.ch; // high ch first (back)
        return a.cw - b.cw;
    });

    // ── Build SVG ──
    var svg = '';

    // Background
    svg += '<defs>';
    svg += '<linearGradient id="fSkyG" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#2a4a70"/><stop offset="70%" stop-color="#4a7aa0"/><stop offset="100%" stop-color="#5a8a50"/></linearGradient>';
    svg += '</defs>';
    svg += '<rect width="' + SVG_W + '" height="' + SVG_H + '" fill="url(#fSkyG)"/>';

    // Subtle ground plane — gets greener toward the front
    for (var row = 0; row < 6; row++) {
        var ry = PAD_T + row * ROW_H;
        var greenness = 0.08 + (5 - row) * 0.03; // more green in front rows
        svg += '<rect x="' + PAD_L + '" y="' + ry + '" width="' + PLOT_W + '" height="' + ROW_H + '" fill="rgba(60,90,40,' + greenness.toFixed(2) + ')"/>';
    }

    // Grid lines (very subtle)
    for (var col = 0; col <= 6; col++) {
        var gx = PAD_L + col * COL_W;
        svg += '<line x1="' + gx + '" y1="' + PAD_T + '" x2="' + gx + '" y2="' + (SVG_H - PAD_B) + '" stroke="rgba(255,255,255,0.06)" stroke-width="1"/>';
    }
    for (var row = 0; row <= 6; row++) {
        var gy = PAD_T + row * ROW_H;
        svg += '<line x1="' + PAD_L + '" y1="' + gy + '" x2="' + (SVG_W - PAD_R) + '" y2="' + gy + '" stroke="rgba(255,255,255,0.06)" stroke-width="1"/>';
    }

    // ── Axis labels ──
    var SAE_LABELS = ['L0\nManual', 'L1\nAI-Assisted', 'L2\nPartially\nAutomated', 'L3\nGuided\nAutomation', 'L4\nMostly\nAutomated', 'L5\nFull\nAutomation'];
    var CH_LABELS = ['—', 'Explorer', 'Practitioner', 'Integrator', 'Architect', 'Steward'];

    // X axis (SAE) — bottom
    for (var col = 0; col < 6; col++) {
        var lx = PAD_L + col * COL_W + COL_W / 2;
        var ly = SVG_H - PAD_B + 16;
        var parts = SAE_LABELS[col].split('\n');
        svg += '<text x="' + lx + '" y="' + ly + '" text-anchor="middle" fill="rgba(255,255,255,0.5)" font-size="9" font-family="system-ui,sans-serif">';
        for (var p = 0; p < parts.length; p++) {
            svg += '<tspan x="' + lx + '" dy="' + (p === 0 ? 0 : 11) + '">' + parts[p] + '</tspan>';
        }
        svg += '</text>';
    }

    // X axis title
    svg += '<text x="' + (PAD_L + PLOT_W / 2) + '" y="' + (SVG_H - 4) + '" text-anchor="middle" fill="rgba(255,255,255,0.35)" font-size="10" letter-spacing="2" font-family="system-ui,sans-serif">AI AUTOMATION LEVEL</text>';

    // Y axis (canopy height / EPIAS) — left, ch=5 at top, ch=0 at bottom
    for (var row = 0; row < 6; row++) {
        var ch_val = 5 - row; // top row = ch 5
        var lbl = CH_LABELS[ch_val];
        var ly2 = PAD_T + row * ROW_H + ROW_H / 2 + 4;
        svg += '<text x="' + (PAD_L - 8) + '" y="' + ly2 + '" text-anchor="end" fill="rgba(255,255,255,0.5)" font-size="10" font-family="system-ui,sans-serif">' + lbl + '</text>';
    }

    // Y axis title
    svg += '<text x="12" y="' + (PAD_T + PLOT_H / 2) + '" text-anchor="middle" fill="rgba(255,255,255,0.35)" font-size="10" letter-spacing="2" font-family="system-ui,sans-serif" transform="rotate(-90 12 ' + (PAD_T + PLOT_H / 2) + ')">LEADERSHIP MATURITY</text>';

    // ── Place trees ──
    var treePositions = [];

    // Count trees per cell for jitter distribution
    var cellCounts = {};
    var cellIdx = {};
    allTrees.forEach(function(t) {
        var ck = t.cw + '_' + t.ch;
        cellCounts[ck] = (cellCounts[ck] || 0) + 1;
        cellIdx[ck] = 0;
    });

    allTrees.forEach(function(t, i) {
        var ck = t.cw + '_' + t.ch;
        var myIdx = cellIdx[ck]++;
        var nInCell = cellCounts[ck];

        // Cell center
        var col = t.cw;
        var row = 5 - t.ch; // ch=5 → row 0 (top)
        var cx = PAD_L + col * COL_W + COL_W / 2;
        var cy = PAD_T + row * ROW_H + ROW_H / 2;

        // Distribute within cell — spiral pattern for clusters
        var angle = myIdx * 2.399 + srand(t.seed) * 0.5; // golden angle + jitter
        var radius = Math.sqrt(myIdx / Math.max(nInCell, 1)) * Math.min(COL_W, ROW_H) * 0.35;
        var jx = Math.cos(angle) * radius;
        var jy = Math.sin(angle) * radius * 0.6; // compress vertically for perspective

        var x = cx + jx;
        var y = cy + jy;

        var sc = treeScale(t.ch);
        var imgW = ORG_W * sc;
        var imgH = ORG_H * sc;

        // Position so organism's ground line (ORG_GY) aligns with y
        var imgX = x - imgW / 2;
        var imgY = y - ORG_GY * sc;

        treePositions.push({ x: x, y: y, sc: sc, imgX: imgX, imgY: imgY, imgW: imgW, imgH: imgH });

        svg += '<g id="ftree-' + i + '">';
        svg += '<image href="/static/trees/org/' + t.filename + '" x="' + imgX.toFixed(1) + '" y="' + imgY.toFixed(1) + '" width="' + imgW.toFixed(1) + '" height="' + imgH.toFixed(1) + '"/>';
        svg += '</g>';
    });

    // Attribution
    svg += '<text x="' + (SVG_W / 2) + '" y="' + (SVG_H - PAD_B - 4) + '" text-anchor="middle" fill="rgba(255,255,255,0.2)" font-size="8" font-family="system-ui,sans-serif">Based on the Design in Tech Report 2026 by John Maeda. Site and tool built by Noah Ratzan.</text>';

    container.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ' + SVG_W + ' ' + SVG_H + '" style="width:100%;display:block">' + svg + '</svg>';

    // ── Wind animation ──
    var treeEls = [];
    for (var ei = 0; ei < allTrees.length; ei++) {
        treeEls.push(document.getElementById('ftree-' + ei));
    }

    var animFrame = null;

    windSlider.addEventListener('input', function() {
        var f = parseInt(this.value) / 100;
        var li = Math.min(4, Math.floor(f * 4.99));
        windValue.textContent = windLabels[li];
        windValue.style.color = f > 0.7 ? '#fbbf24' : '';

        if (f <= 0) {
            treeEls.forEach(function(el) {
                if (!el) return;
                el.setAttribute('transform', '');
                el.style.opacity = '';
            });
            if (animFrame) { cancelAnimationFrame(animFrame); animFrame = null; }
            return;
        }

        if (!animFrame) {
            (function tick() {
                var fNow = parseInt(windSlider.value) / 100;
                if (fNow <= 0) { animFrame = null; return; }

                treeEls.forEach(function(el, idx) {
                    if (!el) return;
                    var t = allTrees[idx];
                    var pos = treePositions[idx];

                    if (fNow >= t.breakAt) {
                        // Blown away — translate downwind and fade
                        var drift = 80 + (1 - t.breakAt) * 200;
                        el.setAttribute('transform',
                            'translate(' + drift.toFixed(0) + ', ' + (-30) + ') rotate(40 ' + pos.x.toFixed(0) + ' ' + pos.y.toFixed(0) + ')');
                        el.style.opacity = '0.08';
                    } else {
                        el.style.opacity = '';
                        var sway = Math.sin(Date.now() * 0.002 + idx * 1.5) * fNow * t.maxLean * 0.12;
                        var lean = fNow * t.maxLean * 0.08;
                        el.setAttribute('transform',
                            'rotate(' + (lean + sway).toFixed(1) + ' ' + pos.x.toFixed(0) + ' ' + pos.y.toFixed(0) + ')');
                    }
                });

                animFrame = requestAnimationFrame(tick);
            })();
        }
    });

})();
