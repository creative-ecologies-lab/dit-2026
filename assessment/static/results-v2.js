/**
 * DIT 2026 v2 — Tree Results page logic.
 * Reads v2 assessment results from sessionStorage, renders the tree, and handles export.
 */

(function() {
    'use strict';

    const data = sessionStorage.getItem('ditResultV2');
    if (!data) {
        // No individual results — show community views, hide Your Tree tab
        document.getElementById('resultsContent').style.display = '';
        document.getElementById('viewYourTree').style.display = 'none';
        document.getElementById('viewCommunity').style.display = '';
        var communitySubtitle = document.getElementById('communitySubtitle');
        if (communitySubtitle) communitySubtitle.style.display = '';
        // Hide the Your Tree button, activate The Forest
        var yourTreeTab = document.querySelector('[data-view="yourTree"]');
        var forestTab = document.querySelector('[data-view="forest"]');
        if (yourTreeTab) yourTreeTab.style.display = 'none';
        if (forestTab) forestTab.classList.add('active');
        return;
    }

    let result;
    if (window.dit) dit.track('v2_results_view');
    try {
        result = JSON.parse(data);
    } catch (e) {
        console.error('Failed to parse v2 results:', e);
        sessionStorage.removeItem('ditResultV2');
        document.getElementById('noResults').style.display = '';
        document.getElementById('resultsContent').style.display = 'none';
        return;
    }

    document.getElementById('noResults').style.display = 'none';
    document.getElementById('resultsContent').style.display = '';

    const saeNames = (typeof DIT_SAE_NAMES !== 'undefined') ? DIT_SAE_NAMES
        : {0: 'Manual', 1: 'AI-Assisted', 2: 'Partially Automated',
           3: 'Guided Automation', 4: 'Mostly Automated', 5: 'Full Automation'};
    const stageNames = (typeof DIT_STAGE_NAMES !== 'undefined') ? DIT_STAGE_NAMES
        : {E: 'Explorer', P: 'Practitioner', I: 'Integrator', A: 'Architect', S: 'Steward'};

    // ---- Section 1: Tree Visualization ----

    if (window.TreeViz && result.viz) {
        const svg = TreeViz.generateTreeSVG(result.viz, {
            balance: result.balance || 'balanced',
            root_code: result.root_code || 'L0-E',
            canopy_code: result.canopy_code || null,
        });
        document.getElementById('treeContainer').innerHTML = svg;
    }

    // ---- Return ID ----
    if (result.tree_id) {
        var retSection = document.getElementById('returnIdSection');
        var retCode = document.getElementById('returnIdCode');
        var retCopy = document.getElementById('copyReturnId');
        if (retSection && retCode) {
            retCode.textContent = result.tree_id;
            retSection.style.display = '';
        }
        if (retCopy) {
            retCopy.addEventListener('click', function() {
                navigator.clipboard.writeText(result.tree_id).then(function() {
                    retCopy.textContent = 'Copied!';
                    setTimeout(function() { retCopy.textContent = 'Copy'; }, 2000);
                });
            });
        }
    }

    // ---- Section 2: Dual Codes ----

    // Species name removed — the tree shape speaks for itself
    document.getElementById('speciesName').textContent = '';
    document.getElementById('speciesDesc').textContent = '';

    // Root card
    document.getElementById('rootCode').textContent = result.root_code || '';
    document.getElementById('rootTitle').textContent =
        'Craft Foundation: ' + (stageNames[result.root_stage] || result.root_stage);
    document.getElementById('rootDesc').textContent = result.root_description || '';

    // Canopy card
    if (result.canopy_code) {
        document.getElementById('canopyCode').textContent = result.canopy_code;
        document.getElementById('canopyTitle').textContent =
            'AI Practice: ' + (stageNames[result.canopy_stage] || '') +
            ' at L' + result.sae_level + ' (' + (saeNames[result.sae_level] || '') + ')';
        document.getElementById('canopyDesc').textContent = result.canopy_description || '';
    } else {
        // L0 — no canopy
        var card = document.getElementById('canopyCard');
        card.innerHTML = '<div class="code-card-header"><span class="code-card-icon">&#x1F343;</span>' +
            '<span class="code-card-label">AI Canopy</span></div>' +
            '<div class="code-card-code" style="opacity:0.5">None</div>' +
            '<div class="code-card-title">No AI canopy yet</div>' +
            '<p class="code-card-desc">Your tree hasn\u2019t grown upward yet \u2014 all your energy is in the roots. That\u2019s a strong foundation to grow from when you\u2019re ready.</p>';
    }

    // Balance indicator
    var balanceColors = {
        'grounded': '#4ade80', 'deeply rooted': '#4ade80',
        'balanced': '#4ade80', 'reaching': '#fbbf24', 'top-heavy': '#f87171',
    };
    document.getElementById('balanceDot').style.background = balanceColors[result.balance] || '#888';
    document.getElementById('balanceText').textContent =
        (result.balance || '').charAt(0).toUpperCase() + (result.balance || '').slice(1) +
        ' \u2014 ' + (result.balance_description || '');

    // ---- Section 3: Growth Path ----

    var growth = result.growth || {};
    document.getElementById('growthDirection').textContent = growth.label || '';
    document.getElementById('growthMessage').textContent = growth.message || '';

    var actionsEl = document.getElementById('growthActions');
    actionsEl.innerHTML = '';
    (growth.actions || []).forEach(function(text) {
        var li = document.createElement('li');
        li.textContent = text;
        actionsEl.appendChild(li);
    });

    // Key insight quote removed

    // ---- Wind Simulation (JS requestAnimationFrame — no CSS animation) ----

    var windSlider = document.getElementById('windSlider');
    var windValue = document.getElementById('windValue');
    var treeContainer = document.getElementById('treeContainer');

    var maxLeanMap = {
        'grounded': 2,
        'deeply rooted': 5,
        'balanced': 12,
        'reaching': 30,
        'top-heavy': 75,
    };
    var maxLean = maxLeanMap[result.balance] || 10;

    // Beaufort 0–12 + Saffir-Simpson Cat 1–5
    var windLabels = [
        'calm', 'light air', 'light breeze', 'gentle breeze',
        'moderate breeze', 'fresh breeze', 'strong breeze', 'near gale',
        'gale', 'strong gale', 'storm', 'severe storm',
        'hurricane cat 1', 'hurricane cat 2', 'hurricane cat 3',
        'hurricane cat 4', 'hurricane cat 5',
    ];

    // Compute ratio and breakThreshold with dice
    var rd = result.root_numeric || result.viz.root_depth || 1;
    var cw = result.sae_level || result.viz.canopy_width || 0;
    var ch = result.canopy_numeric || result.viz.canopy_height || 0;
    var treeRatio = (cw > 0 && rd < 5) ? (cw * 2 + ch * 2) / (rd * 5) : 0;

    var breakThreshold = 99; // default: never breaks

    function rollTreeDice() {
        if (treeRatio <= 0) { breakThreshold = 99; return; }
        var die1 = Math.floor(Math.random() * 9) + 1;
        var die2 = Math.floor(Math.random() * 9) + 1;
        var circumstance = (die1 + die2) / 10;
        var effective = treeRatio * circumstance;
        if (effective <= 2.0) {
            breakThreshold = 99;
        } else {
            var s = Math.min(1.0, (effective - 2.0) / 5.0);
            breakThreshold = 0.98 - s * s * 0.60;
        }
    }

    // Default roll
    rollTreeDice();

    var state = 'calm';
    var animId = null;
    var breakTime = 0;
    var CX = 250, GY_PIVOT = 285;
    var windFracLive = 0;

    // Inject wind filters into SVG
    function ensureFilters(svg) {
        if (svg.querySelector('#windWarp')) return;
        var defs = svg.querySelector('defs');
        if (!defs) { defs = document.createElementNS('http://www.w3.org/2000/svg','defs'); svg.prepend(defs); }
        defs.insertAdjacentHTML('beforeend', [
            '<filter id="windWarp" x="-20%" y="-10%" width="140%" height="120%">',
            '  <feTurbulence id="wTurb" type="fractalNoise" baseFrequency="0.005 0.003" numOctaves="3" seed="1" result="noise"/>',
            '  <feDisplacementMap id="wDisp" in="SourceGraphic" in2="noise" scale="0" xChannelSelector="R" yChannelSelector="G"/>',
            '</filter>',
            '<filter id="motionBlur" x="-10%" y="-10%" width="130%" height="120%">',
            '  <feGaussianBlur id="mBlur" stdDeviation="0 0"/>',
            '</filter>',
        ].join(''));
    }

    function getEls() {
        var svg = treeContainer.querySelector('svg');
        if (!svg) return null;
        ensureFilters(svg);
        return {
            svg: svg,
            whole: svg.querySelector('.tree-whole'),
            canopy: svg.querySelector('.tree-canopy'),
            leaves: svg.querySelector('.tree-leaves'),
            roots: svg.querySelector('.tree-roots'),
            turb: svg.querySelector('#wTurb'),
            disp: svg.querySelector('#wDisp'),
            blur: svg.querySelector('#mBlur'),
        };
    }

    // ── Main animation loop — runs continuously when wind > 0 ──
    function tick(ts) {
        var el = getEls();
        if (!el || (!el.canopy && !el.whole)) { animId = null; return; }
        var t = ts * 0.001; // seconds

        var whole = el.whole || el.canopy;

        if (state === 'calm') {
            whole.removeAttribute('transform');
            if (el.canopy) el.canopy.removeAttribute('filter');
            if (el.leaves) { el.leaves.removeAttribute('filter'); el.leaves.style.opacity = ''; }
            animId = null;
            return;
        }

        if (state === 'swaying') {
            var f = windFracLive;
            var freq = 0.004 + f * 0.008;
            el.turb.setAttribute('baseFrequency', freq.toFixed(4) + ' ' + (freq * 0.5).toFixed(4));
            el.turb.setAttribute('seed', Math.floor(t * (2 + f * 8)) % 100);
            el.disp.setAttribute('scale', (f * 15).toFixed(1));
            if (el.canopy) el.canopy.setAttribute('filter', 'url(#windWarp)');
            if (el.leaves) el.leaves.setAttribute('filter', 'url(#windWarp)');
            // Whole tree sways as one unit
            var bend = Math.sin(t * (1.5 + f * 2)) * f * 3 + f * 2;
            whole.setAttribute('transform', 'rotate(' + bend.toFixed(1) + ' ' + CX + ' ' + GY_PIVOT + ')');
        }

        if (state === 'breaking') {
            breakTime += 0.016;
            var phase = Math.min(breakTime / 1.0, 1); // falls in 1 second

            // Tree blows away
            var shiftX = Math.pow(phase, 1.5) * 600;
            var liftY = -Math.sin(phase * Math.PI) * 80;
            var tumble = phase * 360;
            var scale = 1 - phase * 0.6;
            whole.setAttribute('transform',
                'translate(' + shiftX.toFixed(0) + ' ' + liftY.toFixed(0) + ') ' +
                'rotate(' + tumble.toFixed(0) + ' ' + CX + ' ' + GY_PIVOT + ') ' +
                'scale(' + scale.toFixed(2) + ')');
            if (el.canopy) {
                el.disp.setAttribute('scale', (10 + phase * 15).toFixed(0));
                el.turb.setAttribute('seed', Math.floor(t * 12) % 100);
                el.canopy.setAttribute('filter', 'url(#windWarp)');
            }
            if (el.leaves) el.leaves.style.opacity = Math.max(0, 1 - phase * 1.5).toFixed(2);
            if (phase >= 1) state = 'fallen';
        }

        if (state === 'fallen') {
            whole.setAttribute('transform', 'translate(800 -200) scale(0.1)');
            if (el.canopy) el.canopy.removeAttribute('filter');
            animId = null;
            return;
        }

        animId = requestAnimationFrame(tick);
    }

    if (windSlider) {
        windSlider.addEventListener('input', function() {
            var v = parseInt(this.value);
            windFracLive = v / 100;

            if (windFracLive <= 0) {
                state = 'calm';
                breakTime = 0;
                if (animId) { cancelAnimationFrame(animId); animId = null; }
                tick(0);
                return;
            }

            if (windFracLive >= breakThreshold && state === 'swaying') {
                state = 'breaking';
                breakTime = 0;
            } else if (state !== 'breaking' && state !== 'fallen') {
                state = 'swaying';
            }

            if (!animId) animId = requestAnimationFrame(tick);

            var labelIdx = Math.min(16, Math.floor(windFracLive * 16.99));
            windValue.textContent = windLabels[labelIdx];
            windValue.style.color = (state === 'breaking' || state === 'fallen') ? '#f87171'
                : windFracLive > 0.7 ? '#fbbf24' : '';
        });
    }

    // ── Chance button + info popup ──
    var resultRollBtn = document.getElementById('resultRollDice');
    var resultDiceResult = document.getElementById('resultDiceResult');
    var resultChanceInfo = document.getElementById('resultChanceInfo');
    var resultChancePopup = document.getElementById('resultChancePopup');
    var nightOverlay = document.getElementById('nightOverlay');
    var starsOverlay = document.getElementById('starsOverlay');

    if (resultRollBtn) {
        var rolling = false;
        resultRollBtn.addEventListener('click', function() {
            if (rolling) return;
            rolling = true;
            resultRollBtn.disabled = true;
            resultDiceResult.textContent = '\u00a0';

            // Reset wind and tree state
            if (windSlider) windSlider.value = 0;
            windFracLive = 0;
            state = 'calm';
            breakTime = 0;
            if (animId) { cancelAnimationFrame(animId); animId = null; }
            tick(0);

            // Roll dice
            setTimeout(function() {
                rollTreeDice();
                resultDiceResult.textContent = breakThreshold < 99 ? 'at risk' : 'safe';
                rolling = false;
                resultRollBtn.disabled = false;
            }, 300);
        });
    }

    if (resultChanceInfo && resultChancePopup) {
        resultChanceInfo.addEventListener('click', function(e) {
            e.stopPropagation();
            resultChancePopup.classList.toggle('visible');
        });
        document.addEventListener('click', function() {
            resultChancePopup.classList.remove('visible');
        });
    }

    // ---- PDF Export ----

    document.getElementById('downloadPdf').addEventListener('click', function() {
        if (window.dit) dit.track('v2_share', {action: 'pdf'});
        window.print();
    });

    // ---- Markdown Export ----

    document.getElementById('downloadMd').addEventListener('click', function() {
        if (window.dit) dit.track('v2_share', {action: 'markdown'});
        var md = generateMarkdown(result);
        downloadFile('dit-2026-tree-results.md', md, 'text/markdown');
    });

    // ---- Social Share ----

    var shareSpecies = ''; // species labels removed
    var shareBalance = result.balance || 'balanced';
    var shareRootCode = result.root_code || '';
    var shareCanopyCode = result.canopy_code || '';
    var shareUrl = 'https://aiskillsmap.noahratzan.com';

    var sharePlacement = shareRootCode;
    if (shareCanopyCode) sharePlacement += ' / ' + shareCanopyCode;

    // X
    var xText = 'My tree: ' + sharePlacement + ' on the Tree-Shaped Designer model. ' +
        'What shape is yours? #DesignInTech';
    document.getElementById('shareX').href = 'https://twitter.com/intent/tweet?text=' +
        encodeURIComponent(xText) + '&url=' + encodeURIComponent(shareUrl);
    document.getElementById('shareX').addEventListener('click', function() {
        if (window.dit) dit.track('v2_share', {action: 'x'});
    });

    // LinkedIn
    var liText = 'Took the Tree-Shaped Designer assessment from the Design in Tech 2026 framework. ' +
        'My tree: ' + sharePlacement + ' \u2014 ' + shareBalance + '. ' +
        'What shape is yours? ' + shareUrl + ' #DesignInTech';
    document.getElementById('shareLinkedIn').href =
        'https://www.linkedin.com/feed/?shareActive=true&text=' + encodeURIComponent(liText);
    document.getElementById('shareLinkedIn').addEventListener('click', function() {
        if (window.dit) dit.track('v2_share', {action: 'linkedin'});
    });

    // Bluesky
    var bskyText = 'My tree: ' + sharePlacement + ' on the Tree-Shaped Designer model. ' +
        'What shape is yours? #DesignInTech ' + shareUrl;
    document.getElementById('shareBluesky').href =
        'https://bsky.app/intent/compose?text=' + encodeURIComponent(bskyText);
    document.getElementById('shareBluesky').addEventListener('click', function() {
        if (window.dit) dit.track('v2_share', {action: 'bluesky'});
    });

    // Copy
    var copyText = 'I took the Tree-Shaped Designer assessment from the Design in Tech 2026 framework. ' +
        'My tree: ' + sharePlacement + ' \u2014 ' + shareBalance + '. ' +
        'Every combination of root depth and canopy spread gives you a different shape. What shape is yours? ' +
        shareUrl + ' #DesignInTech';
    document.getElementById('sharePreview').textContent = copyText;
    document.getElementById('copyShare').addEventListener('click', function() {
        if (window.dit) dit.track('v2_share', {action: 'copy'});
        navigator.clipboard.writeText(copyText).then(function() {
            var btn = document.getElementById('copyShare');
            var orig = btn.innerHTML;
            btn.textContent = 'Copied!';
            setTimeout(function() { btn.innerHTML = orig; }, 2000);
        });
    });

    // ---- Markdown Generation ----

    function generateMarkdown(r) {
        var date = new Date().toISOString().split('T')[0];
        var md = '# Tree-Shaped Designer Assessment Results\n\n';
        md += '**Date:** ' + date + '\n';
        // species label removed
        md += '**Balance:** ' + (r.balance || '') + '\n\n';

        md += '## Your Tree\n\n';
        md += '- **Root Code:** ' + (r.root_code || '') + ' \u2014 ' + (r.root_name || '') + '\n';
        if (r.canopy_code) {
            md += '- **Canopy Code:** ' + r.canopy_code + ' \u2014 ' +
                  (r.canopy_name || '') + ' at L' + r.sae_level + ' (' + (r.sae_name || '') + ')\n';
        } else {
            md += '- **Canopy:** None (L0 \u2014 no AI practice)\n';
        }
        md += '\n' + (r.tree_description || '') + '\n\n';
        md += '**Balance:** ' + (r.balance_description || '') + '\n\n';

        var g = r.growth || {};
        md += '## Growth Direction\n\n';
        md += '**' + (g.label || '') + '**\n\n';
        md += (g.message || '') + '\n\n';
        if (g.actions && g.actions.length) {
            md += '**Next steps:**\n';
            g.actions.forEach(function(a) { md += '- ' + a + '\n'; });
            md += '\n';
        }

        if (r.key_insight) {
            md += '## Key Insight\n\n> "' + r.key_insight + '"\n\n';
        }

        md += '---\n*Generated by the [Tree-Shaped Designer Assessment](https://aiskillsmap.noahratzan.com)*\n';
        return md;
    }

    function downloadFile(filename, content, mimeType) {
        var blob = new Blob([content], { type: mimeType + ';charset=utf-8' });
        var url = URL.createObjectURL(blob);
        var a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

})();
