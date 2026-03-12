/**
 * DIT 2026 — Results page logic.
 * Reads assessment results from sessionStorage, renders, and handles export.
 * Includes interactive heatmap with Everyone/Group toggle.
 */

(function() {
    'use strict';

    const data = sessionStorage.getItem('ditResult');
    if (!data) {
        document.getElementById('noResults').style.display = '';
        document.getElementById('resultsContent').style.display = 'none';
        return;
    }

    let result;
    try {
        result = JSON.parse(data);
    } catch (e) {
        console.error('Failed to parse results:', e);
        sessionStorage.removeItem('ditResult');
        document.getElementById('noResults').style.display = '';
        document.getElementById('resultsContent').style.display = 'none';
        return;
    }

    document.getElementById('noResults').style.display = 'none';
    const resultsEl = document.getElementById('resultsContent');
    resultsEl.style.display = '';

    // Use server-injected canonical names, with fallbacks
    const saeNames = (typeof DIT_SAE_NAMES !== 'undefined') ? DIT_SAE_NAMES
        : {0: 'Manual', 1: 'AI-Assisted', 2: 'Partially Automated',
           3: 'Guided Automation', 4: 'Mostly Automated', 5: 'Full Automation'};
    const stageNames = (typeof DIT_STAGE_NAMES !== 'undefined') ? DIT_STAGE_NAMES
        : {E: 'Explorer', P: 'Practitioner', I: 'Integrator', A: 'Architect', S: 'Steward'};
    const cellDescriptions = (typeof DIT_CELL_DESCRIPTIONS !== 'undefined') ? DIT_CELL_DESCRIPTIONS : {};
    const stageDescs = (typeof DIT_STAGE_DESCRIPTIONS !== 'undefined') ? DIT_STAGE_DESCRIPTIONS
        : {E: 'Experimenting and building intuition. Quality varies, still learning what works.',
           P: 'Consistent habits and repeatable techniques. Process is reliable.',
           I: 'Fully integrated into workflow with documented decisions and traceability.',
           A: 'Builds reusable systems and templates that others adopt and trust.',
           S: 'Sets organizational standards, mentors others, and governs practice.'};
    const levelDescs = (typeof DIT_LEVEL_DESCRIPTIONS !== 'undefined') ? DIT_LEVEL_DESCRIPTIONS
        : {0: 'All work is manual. No AI tools in the workflow.',
           1: 'AI used for ideas and drafts. Every step is human-directed.',
           2: 'AI generates deliverables from specs. Human integration and QA.',
           3: 'Multi-step AI workflows in an IDE with checkpoints and context.',
           4: 'Autonomous agent harnesses with eval suites and escalation paths.',
           5: 'AI runs the workflow. Humans set goals and review exceptions.'};

    // Enriched bullets per EPIAS stage — behavioral traits from Maeda's framework
    const stageBulletsMap = {
        E: [
            'Quality varies \u2014 still learning what works',
            'Outputs are hit-or-miss, require judgment to filter',
            'Building intuition through experimentation',
        ],
        P: [
            'Consistent habits and repeatable techniques',
            'Process is reliable with quality checks by default',
            'Knows when the approach will work before starting',
        ],
        I: [
            'Every decision is documented and traceable',
            'Clear framing: what AI does, what humans approve',
            'Failure modes are understood and handled',
        ],
        A: [
            'Others adopt your systems, templates, and workflows',
            'Cross-functional teams operate without your presence',
            'Designs for reuse, not just personal use',
        ],
        S: [
            'Sets organizational standards and governance',
            'Mentoring others is a primary output',
            'Maintains shared infrastructure everyone depends on',
        ],
    };

    // Enriched bullets per SAE level — environment, responsibility, and role
    const levelBulletsMap = {
        0: [
            'All outputs from craft fundamentals \u2014 no AI in the loop',
            'Full creative control in every step',
            'Classical Designer',
        ],
        1: [
            'AI for ideas and drafts \u2014 you direct each step',
            'Every AI output reviewed before use',
            'Marketing Designer \u00d7 AI',
        ],
        2: [
            'AI generates components from your specs',
            'Your work is integration and QA, not generation',
            'Product Designer \u00d7 AI',
        ],
        3: [
            'Multi-step workflows in an IDE with checkpoints',
            'AI executes; you review at defined gates',
            'Design Engineer \u00d7 AI',
        ],
        4: [
            'Agent harnesses run autonomously with eval suites',
            'Work completes unattended; you govern exceptions',
            'Super Design Engineer \u00d7 AI',
        ],
        5: [
            'AI runs the workflow; you set goals and review',
            'Approval gates and quality bars are the interface',
            'AI \u00d7 AI (aspirational)',
        ],
    };

    const levelTitles = {
        0: 'L0: Manual workflow',
        1: 'L1: AI-assisted workflow',
        2: 'L2: Partially automated workflow',
        3: 'L3: Guided workflow automation',
        4: 'L4: Mostly automated workflow',
        5: 'L5: Fully automated workflow',
    };

    function shyStage(name) {
        return name.replace('Practitioner', 'Practi\u00ADtioner').replace('Integrator', 'Inte\u00ADgrator');
    }

    function fillBullets(el, items) {
        el.innerHTML = '';
        (items || []).forEach(function(text) {
            var li = document.createElement('li');
            li.textContent = text;
            el.appendChild(li);
        });
    }

    // ---- Section 1: Placement (left column) ----

    document.getElementById('positionCode').textContent =
        result.epias_stage + result.sae_level;

    // Cell description (uppercase first char)
    const rawDesc = result.cell_description || 'No description available.';
    const desc = rawDesc.charAt(0).toUpperCase() + rawDesc.slice(1);
    document.getElementById('cellDescription').textContent = desc;

    // Left: Leadership Stage card
    document.getElementById('summaryStage').textContent =
        stageNames[result.epias_stage] || result.epias_stage;
    fillBullets(document.getElementById('stageBullets'), stageBulletsMap[result.epias_stage]);

    // Left: Workflow Automation Level card
    document.getElementById('summaryLevel').textContent =
        levelTitles[result.sae_level] || ('L' + result.sae_level);
    fillBullets(document.getElementById('levelBullets'), levelBulletsMap[result.sae_level]);

    // ---- Section 2: Interactive Heatmap ----

    const currentLevel = result.sae_level;
    const currentStage = result.epias_stage;
    const nextStep = result.growth_path && result.growth_path.next;
    const cohort = result.cohort || null;

    // Show toggle bar only if user entered a cohort
    const toggleGroup = document.getElementById('toggleGroup');
    if (cohort) {
        toggleGroup.textContent = cohort.toUpperCase();
        document.getElementById('heatmapToggle').style.display = '';
    }

    let activeView = 'everyone';

    function fetchAndRenderHeatmap(view) {
        activeView = view;
        let url = view === 'group' && cohort
            ? '/api/heatmap?group=' + encodeURIComponent(cohort)
            : '/api/heatmap';

        // Update toggle state
        document.getElementById('toggleEveryone').classList.toggle('active', view === 'everyone');
        document.getElementById('toggleEveryone').setAttribute('aria-selected', view === 'everyone');
        if (toggleGroup.style.display !== 'none') {
            toggleGroup.classList.toggle('active', view === 'group');
            toggleGroup.setAttribute('aria-selected', view === 'group');
        }

        fetch(url)
            .then(r => r.json())
            .then(data => renderHeatmap(data))
            .catch(() => {
                document.getElementById('resultsHeatmap').innerHTML =
                    '<p style="color:var(--text-muted);">Could not load heatmap data.</p>';
            });
    }

    function renderHeatmap(hmData) {
        const container = document.getElementById('resultsHeatmap');
        const counts = hmData.counts || {};
        const total = hmData.total || 0;
        const stages = ['E', 'P', 'I', 'A', 'S'];
        const maxCount = Math.max(1, ...Object.values(counts));

        // Exact same structure as landing page heatmap
        let html = '<div class="map-card">';
        html += '<table class="landing-heatmap" role="table"';
        html += ' aria-label="Community heatmap: ' + total + ' responses, your position highlighted">';
        html += '<caption class="sr-only">Community heatmap showing ' + total + ' responses. Darker cells indicate more people at that position.</caption>';
        html += '<thead><tr>';
        html += '<th scope="col" class="hm-corner"><span class="sr-only">Level</span></th>';
        stages.forEach(s => {
            html += '<th scope="col" class="hm-stage-header" aria-label="' + stageNames[s] + ': ' + stageDescs[s] + '" data-desc="' + escapeAttr(stageDescs[s]) + '" data-label="' + stageNames[s] + '" tabindex="0" role="button">' + shyStage(stageNames[s]) + '</th>';
        });
        html += '</tr></thead><tbody>';

        // L5 at top, L0 at bottom
        for (let level = 5; level >= 0; level--) {
            html += '<tr>';
            html += '<th scope="row" class="hm-level-header" aria-label="Level ' + level + ': ' + saeNames[level] + ' — ' + levelDescs[level] + '" data-desc="' + escapeAttr(levelDescs[level]) + '" data-label="L' + level + ' ' + saeNames[level] + '" tabindex="0" role="button">';
            html += '<span class="hm-level-num">L' + level + '</span>';
            html += '<span class="hm-level-name">' + saeNames[level] + '</span></th>';

            stages.forEach(stage => {
                const key = level + '_' + stage;
                const count = counts[key] || 0;
                const intensity = count > 0 ? count / maxCount : 0;
                const opacity = count > 0 ? (intensity * 0.80 + 0.15).toFixed(2) : '0.04';

                const isCurrent = level === currentLevel && stage === currentStage;
                const isNext = nextStep && level === nextStep.sae_level && stage === nextStep.epias_stage;
                const desc = cellDescriptions[key] || '';

                let classes = 'hm-cell';
                if (count === 0) classes += ' hm-cell-empty';
                if (isCurrent) classes += ' hm-cell-you';
                if (isNext) classes += ' hm-cell-next';

                html += '<td class="' + classes + '"';
                html += ' style="--cell-opacity: ' + opacity + ';"';
                html += ' aria-label="' + count + ' ' + (count === 1 ? 'person' : 'people') + ' at L' + level + ' ' + saeNames[level] + ', ' + stageNames[stage];
                if (isCurrent) html += ' (you are here)';
                if (isNext) html += ' (recommended direction)';
                html += '">';

                if (count > 0) {
                    const textClass = intensity > 0.5 ? 'hm-count-light' : 'hm-count-dark';
                    html += '<span class="hm-count ' + textClass + '">' + count + '</span>';
                }

                if (isCurrent) {
                    html += '<span class="hm-marker hm-marker-you">\u2605 You are here</span>';
                } else if (isNext) {
                    html += '<span class="hm-marker hm-marker-next">Recommended direction</span>';
                }

                html += '</td>';
            });
            html += '</tr>';
        }

        html += '</tbody></table></div>';
        if (total > 0) {
            html += '<p class="heatmap-count">' + total + ' participants</p>';
        }
        container.innerHTML = html;

        // Attach click handlers for popover (headers only)
        container.querySelectorAll('.hm-stage-header[data-desc], .hm-level-header[data-desc]').forEach(el => {
            el.addEventListener('click', function(e) {
                e.stopPropagation();
                showHeaderPopover(el);
            });
            el.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); el.click(); }
            });
        });
    }

    // Toggle handlers
    document.getElementById('toggleEveryone').addEventListener('click', () => fetchAndRenderHeatmap('everyone'));
    document.getElementById('toggleGroup').addEventListener('click', () => fetchAndRenderHeatmap('group'));

    // Initial load
    fetchAndRenderHeatmap('everyone');

    // ---- Popover ----

    const popover = document.getElementById('cellPopover');
    const popTitle = document.getElementById('popoverTitle');
    const popDesc = document.getElementById('popoverDesc');
    let activeCell = null;

    function showHeaderPopover(el) {
        const desc = el.getAttribute('data-desc');
        if (!desc) return;
        if (activeCell === el) { hidePopover(); return; }

        popTitle.textContent = el.getAttribute('data-label') || el.textContent.trim();
        popDesc.textContent = desc;

        const rect = el.getBoundingClientRect();
        const scroll = document.documentElement.scrollTop || document.body.scrollTop;
        popover.style.display = '';
        const pw = popover.offsetWidth;
        let left = rect.left + rect.width / 2 - pw / 2;
        if (left < 8) left = 8;
        if (left + pw > window.innerWidth - 8) left = window.innerWidth - pw - 8;
        popover.style.left = left + 'px';
        popover.style.top = (rect.bottom + scroll + 8) + 'px';

        if (activeCell) activeCell.classList.remove('hm-cell-active');
        activeCell = el;
    }

    function hidePopover() {
        popover.style.display = 'none';
        if (activeCell) activeCell.classList.remove('hm-cell-active');
        activeCell = null;
    }

    popover.querySelector('.cell-popover-close').addEventListener('click', hidePopover);
    document.addEventListener('click', function(e) {
        if (!popover.contains(e.target)) hidePopover();
    });
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') hidePopover();
    });

    // ---- Right column: Growth Path ----

    const gp = result.growth_path || {};

    if (gp.next) {
        const nextEpias = gp.next.epias_stage;
        const nextSae = gp.next.sae_level;
        const isSameSAE = nextSae === result.sae_level;

        // Next stage heading
        if (isSameSAE) {
            document.getElementById('growthNextStage').textContent =
                stageNames[nextEpias] || nextEpias;
        } else {
            document.getElementById('growthNextStage').textContent =
                (stageNames[nextEpias] || nextEpias) +
                ' at L' + nextSae + ' (' + (saeNames[nextSae] || '') + ')';
        }

        // Next stage bullets — shows ONLY the next EPIAS stage traits
        fillBullets(document.getElementById('nextStageBullets'), stageBulletsMap[nextEpias]);
    } else {
        // Peak — S5
        var card = document.getElementById('cardNext');
        card.innerHTML = '<span class="summary-label">You\'ve reached the peak</span>' +
            '<span class="summary-value">Steward at L5</span>' +
            '<p style="font-size:0.875rem;color:var(--text-muted);margin:0.25rem 0 0;">You govern autonomous systems at organizational scale. Stay curious and keep evolving.</p>';
        // Signal/actions sections removed from UI
    }

    // Signal and actions sections removed from results page UI

    // ---- Section 4: Key Insight ----

    document.getElementById('keyInsight').innerHTML =
        '&ldquo;' + (result.key_insight || '') + '&rdquo;<cite>&mdash; John Maeda, Design in Tech Report 2026</cite>';

    // ---- PDF Export ----
    document.getElementById('downloadPdf').addEventListener('click', () => {
        window.print();
    });

    // ---- Markdown Export ----
    document.getElementById('downloadMd').addEventListener('click', () => {
        const md = generateMarkdown(result);
        downloadFile('dit-2026-results.md', md, 'text/markdown');
    });

    // ---- Social Share ----
    const shareCode = result.epias_stage + result.sae_level;
    const shareStage = stageNames[result.epias_stage] || result.epias_stage;
    const shareLevel = saeNames[result.sae_level] || '';
    const shareUrl = 'https://aiskillsmap.noahratzan.com/assess';

    // Readable placement: "Integrator with Partially Automated workflow"
    const sharePlacement = shareStage + ' with ' + shareLevel + ' workflow';

    // X — 280 char limit (URLs = 23 via t.co)
    const xText = 'Took the Design in Tech 2026 self-assessment and found myself at '
        + shareCode + ' \u2014 ' + sharePlacement
        + '. Try it: #DesignInTech';
    document.getElementById('shareX').href =
        'https://twitter.com/intent/tweet?text=' + encodeURIComponent(xText)
        + '&url=' + encodeURIComponent(shareUrl);

    // LinkedIn — professional tone
    const liText = 'Took the Design in Tech 2026 self-assessment from John Maeda\u2019s framework and found myself at '
        + shareCode + ' \u2014 ' + sharePlacement
        + '. It maps where designers and researchers sit on AI adoption. Worth a few minutes: '
        + shareUrl + ' #DesignInTech';
    document.getElementById('shareLinkedIn').href =
        'https://www.linkedin.com/feed/?shareActive=true&text=' + encodeURIComponent(liText);

    // Bluesky — 300 char limit
    const bskyText = 'Took the Design in Tech 2026 self-assessment and found myself at '
        + shareCode + ' \u2014 ' + sharePlacement
        + '. Where are you on the map? #DesignInTech ' + shareUrl;
    document.getElementById('shareBluesky').href =
        'https://bsky.app/intent/compose?text=' + encodeURIComponent(bskyText);

    // Copy — full version for Threads, email, Slack, etc.
    const copyText = 'I took this Design in Tech 2026 self-assessment based on John Maeda\u2019s framework and found myself at '
        + shareCode + ' \u2014 ' + sharePlacement
        + '. It maps AI adoption for designers and researchers. Where do you fall? '
        + shareUrl + ' #DesignInTech';
    document.getElementById('sharePreview').textContent = copyText;
    document.getElementById('copyShare').addEventListener('click', function() {
        navigator.clipboard.writeText(copyText).then(() => {
            var btn = document.getElementById('copyShare');
            var orig = btn.innerHTML;
            btn.textContent = 'Copied!';
            setTimeout(function() { btn.innerHTML = orig; }, 2000);
        });
    });

    // ---- Markdown Generation ----

    function generateMarkdown(r) {
        const levelName = r.sae_name || saeNames[r.sae_level] || 'Level ' + r.sae_level;
        const stageName = stageNames[r.epias_stage] || r.epias_stage;
        const gp = r.growth_path || {};
        const date = new Date().toISOString().split('T')[0];

        let md = '# Design in Tech 2026 Assessment Results\n\n';
        md += '**Date:** ' + date + '\n';
        if (r.cohort) md += '**Group:** ' + r.cohort + '\n';
        md += '\n';

        md += '## Your Placement\n\n';
        md += '- **Workflow Automation Level:** Level ' + r.sae_level + ' \u2014 ' + levelName + '\n';
        md += '- **Leadership Stage:** ' + stageName + '\n\n';
        md += (r.cell_description || '') + '\n\n';

        md += '## Growth Path\n\n';
        if (gp.next) {
            var nextEpias = gp.next.epias_stage;
            var nextSae = gp.next.sae_level;
            if (nextSae === r.sae_level) {
                md += '**Next leadership stage:** ' + (stageNames[nextEpias] || nextEpias) + '\n\n';
            } else {
                md += '**Next step:** ' + (stageNames[nextEpias] || nextEpias) +
                    ' at L' + nextSae + ' (' + (saeNames[nextSae] || '') + ')\n\n';
            }
        } else {
            md += '**You\'ve reached the peak of the framework!**\n\n';
        }
        if (gp.signal) {
            md += '**Signal to move on:**\n> ' + gp.signal + '\n\n';
        }
        if (gp.actions && gp.actions.length) {
            md += '**Next steps:**\n';
            gp.actions.forEach(a => { md += '- ' + a + '\n'; });
            md += '\n';
        }

        if (r.key_insight) {
            md += '## Key Insight\n\n> "' + r.key_insight + '" \u2014 John Maeda, Design in Tech Report 2026\n\n';
        }

        if (r.growth_chunks && r.growth_chunks.length) {
            md += '## Relevant Framework Excerpts\n\n';
            r.growth_chunks.forEach(chunk => {
                const src = [chunk.source, chunk.section].filter(Boolean).join(' \u2014 ');
                if (src) md += '### ' + src + '\n\n';
                md += truncateChunk(chunk.text || '', 800) + '\n\n---\n\n';
            });
        }

        md += '---\n*Generated by the [Design in Tech 2026 Assessment](https://aiskillsmap.noahratzan.com)*\n';
        return md;
    }

    function downloadFile(filename, content, mimeType) {
        const blob = new Blob([content], { type: mimeType + ';charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    // ---- Utilities ----

    function escapeAttr(text) {
        return text.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }

    /** Truncate chunk text without breaking tables mid-row. */
    function truncateChunk(text, limit) {
        if (text.length <= limit) return text;
        const cut = text.lastIndexOf('\n', limit);
        if (cut <= 0) return text.substring(0, limit);
        const truncated = text.substring(0, cut);
        const lines = truncated.split('\n');
        const lastNonEmpty = lines.filter(l => l.trim()).pop() || '';
        if (lastNonEmpty.trim().startsWith('|')) {
            let tableStart = lines.length - 1;
            while (tableStart > 0 && lines[tableStart].trim().startsWith('|')) tableStart--;
            if (tableStart > 0) return lines.slice(0, tableStart + 1).join('\n');
        }
        return truncated;
    }

})();
