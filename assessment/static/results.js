/**
 * DIT 2026 — Results page logic.
 * Reads assessment results from sessionStorage, renders, and handles export.
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

    const saeNames = {
        0: 'Manual', 1: 'AI-Assisted', 2: 'Partially Automated',
        3: 'Guided Automation', 4: 'Mostly Automated', 5: 'Full Automation'
    };
    const stageNames = {E: 'Explorer', P: 'Practitioner', I: 'Integrator', A: 'Architect', S: 'Steward'};

    const levelExplanations = {
        0: 'You do all your work manually, without AI tools.',
        1: 'You use AI for ideas and drafts but direct every step yourself.',
        2: 'You use AI tools to generate deliverables from specs.',
        3: 'You work in IDE-based multi-step AI workflows with checkpoints.',
        4: 'You run autonomous AI agent harnesses with eval suites.',
        5: 'AI runs most of your workflow; you set goals and review exceptions.',
    };
    const stageExplanations = {
        E: 'Still experimenting and building intuition at this level.',
        P: 'Consistent habits and reliable practices established.',
        I: 'AI is fully integrated into your workflow with documented decisions.',
        A: 'You have built reusable systems that others adopt.',
        S: 'You set organizational standards and mentor others.',
    };

    // Badge
    document.getElementById('badgeLevel').textContent =
        `SAE L${result.sae_level}: ${result.sae_name || saeNames[result.sae_level] || ''}`;
    document.getElementById('badgeStage').textContent =
        `${stageNames[result.epias_stage] || result.epias_stage} (${result.epias_stage})`;

    // Summary explanations
    document.getElementById('summaryLevel').textContent =
        `L${result.sae_level}: ${saeNames[result.sae_level] || ''}`;
    document.getElementById('summaryLevelExplain').textContent =
        levelExplanations[result.sae_level] || '';
    document.getElementById('summaryStage').textContent =
        stageNames[result.epias_stage] || result.epias_stage;
    document.getElementById('summaryStageExplain').textContent =
        stageExplanations[result.epias_stage] || '';

    // Cell description
    document.getElementById('cellDescription').textContent =
        result.cell_description || 'No description available.';

    // Community heatmap link
    const communityLink = document.getElementById('communityLink');
    if (communityLink) {
        const heatmapUrl = result.cohort
            ? '/heatmap/' + encodeURIComponent(result.cohort)
            : '/heatmap';
        document.getElementById('viewHeatmapBtn').href = heatmapUrl;
        communityLink.style.display = '';
    }

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
        const actions = document.querySelector('.action-group');
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

    // ---- PDF Export (via browser print) ----
    document.getElementById('downloadPdf').addEventListener('click', () => {
        window.print();
    });

    // ---- Markdown Export ----
    document.getElementById('downloadMd').addEventListener('click', () => {
        const md = generateMarkdown(result);
        downloadFile('dit-2026-results.md', md, 'text/markdown');
    });

    // Retake clears results
    document.getElementById('retakeLink').addEventListener('click', () => {
        sessionStorage.removeItem('ditResult');
        sessionStorage.removeItem('ditAssessmentState');
    });

    // ---- Markdown Generation ----

    function generateMarkdown(r) {
        const levelName = r.sae_name || saeNames[r.sae_level] || `L${r.sae_level}`;
        const stageName = stageNames[r.epias_stage] || r.epias_stage;
        const gp = r.growth_path || {};
        const date = new Date().toISOString().split('T')[0];

        let md = `# DIT 2026 Assessment Results\n\n`;
        md += `**Date:** ${date}\n`;
        if (r.cohort) md += `**Cohort:** ${r.cohort}\n`;
        md += `\n`;

        md += `## Your Placement\n\n`;
        md += `- **SAE Level:** L${r.sae_level} — ${levelName}\n`;
        md += `- **EPIAS Stage:** ${stageName} (${r.epias_stage})\n\n`;
        md += `${r.cell_description || ''}\n\n`;

        md += `## Growth Path\n\n`;
        if (gp.next) {
            md += `**Next step:** Move to SAE L${gp.next.sae_level}, ${stageNames[gp.next.epias_stage]}\n\n`;
        } else {
            md += `**You've reached the peak of the framework!**\n\n`;
        }
        if (gp.signal) {
            md += `**Signal you've leveled up:**\n> ${gp.signal}\n\n`;
        }
        if (gp.actions && gp.actions.length) {
            md += `**Concrete next steps:**\n`;
            gp.actions.forEach(a => { md += `- ${a}\n`; });
            md += `\n`;
        }

        if (r.key_insight) {
            md += `## Key Insight\n\n> "${r.key_insight}" — John Maeda, DIT 2026\n\n`;
        }

        if (r.growth_chunks && r.growth_chunks.length) {
            md += `## Relevant Framework Excerpts\n\n`;
            r.growth_chunks.forEach(chunk => {
                const src = [chunk.source, chunk.section].filter(Boolean).join(' — ');
                if (src) md += `### ${src}\n\n`;
                md += `${truncateChunk(chunk.text || '', 800)}\n\n---\n\n`;
            });
        }

        md += `---\n*Generated by the [DIT 2026 Assessment](https://dit-maeda.noahratzan.com)*\n`;
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

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
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

    /** Turn a markdown chunk into simple HTML. */
    function renderChunkMarkdown(raw) {
        const lines = raw.split('\n');
        const out = [];
        let inTable = false;
        let headerDone = false;

        for (let i = 0; i < lines.length; i++) {
            let line = lines[i];

            if (line.trim().startsWith('|')) {
                const cells = line.split('|').slice(1, -1).map(c => c.trim());
                if (cells.every(c => /^[-:\s]+$/.test(c))) {
                    headerDone = true;
                    continue;
                }
                if (!inTable) {
                    out.push('<table class="chunk-table">');
                    inTable = true;
                    headerDone = false;
                }
                if (!headerDone) {
                    out.push('<thead><tr>' + cells.map(c => `<th>${escapeHtml(c)}</th>`).join('') + '</tr></thead><tbody>');
                } else {
                    out.push('<tr>' + cells.map(c => `<td>${escapeHtml(c)}</td>`).join('') + '</tr>');
                }
                continue;
            }

            if (inTable) {
                out.push('</tbody></table>');
                inTable = false;
                headerDone = false;
            }

            if (line.trim() === '') {
                out.push('<br>');
                continue;
            }

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
