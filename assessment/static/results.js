/**
 * DIT 2026 — Results page logic.
 * Reads assessment results from sessionStorage and renders.
 */

(function() {
    'use strict';

    const data = sessionStorage.getItem('ditResult');
    if (!data) {
        document.getElementById('noResults').style.display = 'block';
        document.getElementById('resultsContent').style.display = 'none';
        return;
    }

    const result = JSON.parse(data);
    document.getElementById('noResults').style.display = 'none';
    document.getElementById('resultsContent').style.display = 'block';

    // Badge
    const saeEmojis = {0: '\uD83D\uDE97\uD83D\uDCA8', 1: '\uD83D\uDE97\u2795', 2: '\uD83D\uDE97\uD83E\uDDE0', 3: '\uD83D\uDE97\uD83D\uDE34', 4: '\uD83D\uDE95\uD83E\uDD16', 5: '\uD83D\uDE97\u2728'};
    const stageNames = {E: 'Explorer', P: 'Practitioner', I: 'Integrator', A: 'Architect', S: 'Steward'};

    document.getElementById('badgeLevel').textContent =
        `SAE L${result.sae_level}: ${result.sae_name || ''}`;
    document.getElementById('badgeStage').textContent =
        `${stageNames[result.epias_stage] || result.epias_stage} (${result.epias_stage})`;

    // Cell description
    document.getElementById('cellDescription').textContent =
        result.cell_description || 'No description available.';

    // Matrix
    renderMatrix('matrixContainer', result);

    // Growth path
    const gp = result.growth_path || {};
    if (gp.next) {
        document.getElementById('growthNext').innerHTML =
            `<strong>Next step:</strong> Move to <strong>SAE L${gp.next.sae_level}, ${stageNames[gp.next.epias_stage]}</strong>`;
    } else {
        document.getElementById('growthNext').innerHTML =
            `<strong>You've reached the peak of the framework!</strong>`;
    }

    document.getElementById('growthSignal').textContent = gp.signal || '';

    const actionsList = document.getElementById('growthActions');
    actionsList.innerHTML = '';
    (gp.actions || []).forEach(action => {
        const li = document.createElement('li');
        li.textContent = action;
        actionsList.appendChild(li);
    });

    // Key insight
    document.getElementById('keyInsight').innerHTML =
        `&ldquo;${result.key_insight || ''}&rdquo;<cite>&mdash; John Maeda, DIT 2026</cite>`;

    // Related chunks
    const chunksContainer = document.getElementById('relatedChunks');
    chunksContainer.innerHTML = '';
    (result.growth_chunks || []).forEach(chunk => {
        const card = document.createElement('div');
        card.className = 'chunk-card';
        card.innerHTML = `
            <div class="chunk-source">${escapeHtml(chunk.source || '')} &mdash; ${escapeHtml(chunk.section || '')}</div>
            <div class="chunk-text">${renderChunkMarkdown(truncateChunk(chunk.text || '', 1200))}</div>
        `;
        chunksContainer.appendChild(card);
    });

    // Cohort heatmap link
    if (result.cohort) {
        const cohortBtn = document.createElement('a');
        cohortBtn.href = '/heatmap/' + encodeURIComponent(result.cohort);
        cohortBtn.className = 'btn btn-secondary';
        cohortBtn.textContent = 'View Cohort Heatmap';
        const actions = document.querySelector('.result-actions');
        if (actions) actions.appendChild(cohortBtn);
    }

    // Chat link visibility (check if LLM is available)
    fetch('/api/providers')
        .then(r => r.json())
        .then(data => {
            if (data.providers && data.providers.some(p => p.available)) {
                document.getElementById('chatLink').style.display = 'inline-block';
            }
        })
        .catch(() => {});

    // PDF download via print
    document.getElementById('downloadPdf').addEventListener('click', () => {
        window.print();
    });

    // Retake clears results
    document.getElementById('retakeLink').addEventListener('click', (e) => {
        sessionStorage.removeItem('ditResult');
        sessionStorage.removeItem('ditAssessmentState');
    });

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /** Truncate chunk text without breaking tables mid-row. */
    function truncateChunk(text, limit) {
        if (text.length <= limit) return text;
        // Find the last complete line before the limit
        const cut = text.lastIndexOf('\n', limit);
        if (cut <= 0) return text.substring(0, limit);
        const truncated = text.substring(0, cut);
        // If we're in the middle of a table (last non-empty line starts with |),
        // back up to before the table started
        const lines = truncated.split('\n');
        const lastNonEmpty = lines.filter(l => l.trim()).pop() || '';
        if (lastNonEmpty.trim().startsWith('|')) {
            // Find where this table starts and cut before it
            let tableStart = lines.length - 1;
            while (tableStart > 0 && lines[tableStart].trim().startsWith('|')) tableStart--;
            // If there's content before the table, use that
            if (tableStart > 0) return lines.slice(0, tableStart + 1).join('\n');
        }
        return truncated;
    }

    /** Turn a markdown chunk into simple HTML. */
    function renderChunkMarkdown(raw) {
        const lines = raw.split('\n');
        const out = [];
        let inTable = false;
        let headerDone = false;

        for (let i = 0; i < lines.length; i++) {
            let line = lines[i];

            // Detect markdown table rows: lines starting with |
            if (line.trim().startsWith('|')) {
                const cells = line.split('|').slice(1, -1).map(c => c.trim());

                // Skip separator rows like | --- | --- |
                if (cells.every(c => /^[-:\s]+$/.test(c))) {
                    headerDone = true;
                    continue;
                }

                if (!inTable) {
                    out.push('<table class="chunk-table">');
                    inTable = true;
                    headerDone = false;
                }

                // First row before separator = header
                if (!headerDone) {
                    out.push('<thead><tr>' + cells.map(c => `<th>${escapeHtml(c)}</th>`).join('') + '</tr></thead><tbody>');
                } else {
                    out.push('<tr>' + cells.map(c => `<td>${escapeHtml(c)}</td>`).join('') + '</tr>');
                }
                continue;
            }

            // Close table if we were in one
            if (inTable) {
                out.push('</tbody></table>');
                inTable = false;
                headerDone = false;
            }

            // Empty line = paragraph break
            if (line.trim() === '') {
                out.push('<br>');
                continue;
            }

            // Inline formatting on escaped text
            let safe = escapeHtml(line);
            safe = safe.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
            safe = safe.replace(/\*(.*?)\*/g, '<em>$1</em>');
            safe = safe.replace(/`(.*?)`/g, '<code>$1</code>');
            out.push('<p>' + safe + '</p>');
        }

        if (inTable) out.push('</tbody></table>');
        return out.join('\n');
    }

})();
