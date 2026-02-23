/**
 * Heatmap visualization — fetches aggregated results and renders a colored 6x5 grid.
 * Supports cohort-scoped views with live polling and QR code generation.
 */
(function() {
    'use strict';

    const LEVELS = [0, 1, 2, 3, 4, 5];
    const LEVEL_NAMES = {
        0: 'L0: Manual', 1: 'L1: AI-Assisted', 2: 'L2: Partial',
        3: 'L3: Guided', 4: 'L4: Mostly Auto', 5: 'L5: Full Auto'
    };
    const STAGES = ['E', 'P', 'I', 'A', 'S'];
    const STAGE_NAMES = {E: 'Explorer', P: 'Practitioner', I: 'Integrator', A: 'Architect', S: 'Steward'};

    const POLL_INTERVAL = 12000; // 12 seconds for live cohort pages

    function cellColor(count, maxCount) {
        if (count === 0) return '#f8fafc';
        const intensity = 0.15 + 0.75 * (count / maxCount);
        return `hsla(221, 83%, 53%, ${intensity})`;
    }

    function textColor(count, maxCount) {
        if (count === 0) return '#94a3b8';
        const intensity = count / maxCount;
        return intensity > 0.5 ? '#ffffff' : '#1e293b';
    }

    function renderHeatmap(data) {
        const counts = data.counts;
        const maxCount = Math.max(1, ...Object.values(counts));
        const container = document.getElementById('heatmapContainer');
        document.getElementById('totalCount').textContent = data.total;

        let html = '<table class="matrix-table"><thead><tr><th></th>';
        STAGES.forEach(s => {
            html += `<th>${s}<br><small>${STAGE_NAMES[s]}</small></th>`;
        });
        html += '</tr></thead><tbody>';

        LEVELS.forEach(level => {
            html += `<tr><th>${LEVEL_NAMES[level]}</th>`;
            STAGES.forEach(stage => {
                const key = `${level}_${stage}`;
                const count = counts[key] || 0;
                const bg = cellColor(count, maxCount);
                const fg = textColor(count, maxCount);
                html += `<td class="heatmap-cell" style="background:${bg};color:${fg}">${count || ''}</td>`;
            });
            html += '</tr>';
        });

        html += '</tbody></table>';
        container.innerHTML = html;
    }

    // Build API URL with optional cohort filter
    function apiUrl() {
        if (typeof HEATMAP_COHORT !== 'undefined' && HEATMAP_COHORT) {
            return '/api/heatmap?cohort=' + encodeURIComponent(HEATMAP_COHORT);
        }
        return '/api/heatmap';
    }

    function fetchAndRender() {
        fetch(apiUrl())
            .then(r => r.json())
            .then(renderHeatmap)
            .catch(err => {
                console.error('Failed to load heatmap:', err);
                document.getElementById('heatmapContainer').innerHTML =
                    '<p style="text-align:center;color:var(--text-muted);">Could not load heatmap data.</p>';
            });
    }

    // Initial fetch
    fetchAndRender();

    // Live polling for cohort pages
    if (typeof HEATMAP_COHORT !== 'undefined' && HEATMAP_COHORT) {
        setInterval(fetchAndRender, POLL_INTERVAL);

        // Generate QR code pointing to the assessment with cohort pre-filled
        var joinUrl = window.location.origin + '/assess?cohort=' + encodeURIComponent(HEATMAP_COHORT);
        var urlEl = document.getElementById('cohortJoinUrl');
        if (urlEl) urlEl.textContent = joinUrl;

        var qrEl = document.getElementById('qrCode');
        if (qrEl && typeof qrcode !== 'undefined') {
            var qr = qrcode(0, 'M');
            qr.addData(joinUrl);
            qr.make();
            qrEl.innerHTML = qr.createSvgTag(6, 0);
        }
    }
})();
