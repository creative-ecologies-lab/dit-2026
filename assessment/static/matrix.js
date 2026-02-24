/**
 * DIT 2026 — E-P-I-A-S x SAE Matrix Visualization.
 * Renders the 6x5 matrix as an HTML table with highlighted position.
 */

function renderMatrix(containerId, placement) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const levels = [0, 1, 2, 3, 4, 5];
    const stages = ['E', 'P', 'I', 'A', 'S'];

    const levelLabels = {
        0: 'L0\nManual',
        1: 'L1\nAI-Assisted',
        2: 'L2\nPartially\nAutomated',
        3: 'L3\nGuided\nAutomation',
        4: 'L4\nMostly\nAutomated',
        5: 'L5\nFull\nAutomation',
    };

    const levelAccessible = {
        0: 'L0 Manual', 1: 'L1 AI-Assisted', 2: 'L2 Partially Automated',
        3: 'L3 Guided Automation', 4: 'L4 Mostly Automated', 5: 'L5 Full Automation',
    };

    const stageLabels = {
        'E': 'Explorer',
        'P': 'Practitioner',
        'I': 'Integrator',
        'A': 'Architect',
        'S': 'Steward',
    };

    const stageEmojis = {
        'E': '\u2776',  // circled 1
        'P': '\u2777',
        'I': '\u2778',
        'A': '\u2779',
        'S': '\u277A',
    };

    const currentLevel = placement.sae_level;
    const currentStage = placement.epias_stage;
    const nextStep = placement.growth_path && placement.growth_path.next;

    var currentDesc = levelAccessible[currentLevel] + ', ' + stageLabels[currentStage];
    var nextDesc = nextStep
        ? levelAccessible[nextStep.sae_level] + ', ' + stageLabels[nextStep.epias_stage]
        : '';

    let html = '<table class="matrix-table" role="table" aria-label="Your position on the E-P-I-A-S by SAE framework matrix">';
    html += '<caption class="sr-only">Framework matrix. Your current position: ' + currentDesc + '.' + (nextDesc ? ' Suggested next step: ' + nextDesc + '.' : '') + '</caption>';

    // Header row — EPIAS stages as columns
    html += '<thead><tr><th scope="col"><span class="sr-only">SAE Level</span></th>';
    stages.forEach(stage => {
        const isCurrent = stage === currentStage;
        html += `<th scope="col" aria-label="${stageLabels[stage]}" style="${isCurrent ? 'background: #d1fae5; color: var(--success);' : ''}">
            <span aria-hidden="true">${stageEmojis[stage]}</span> ${stageLabels[stage]}
        </th>`;
    });
    html += '</tr></thead><tbody>';

    // Data rows — SAE levels as rows
    levels.forEach(level => {
        const isLevelCurrent = level === currentLevel;
        const label = levelLabels[level].replace(/\n/g, '<br>');
        html += `<tr>`;
        html += `<th scope="row" aria-label="${levelAccessible[level]}" style="${isLevelCurrent ? 'background: var(--primary-light); color: var(--primary);' : ''}">${label}</th>`;

        stages.forEach(stage => {
            const isCurrent = level === currentLevel && stage === currentStage;
            const isNext = nextStep &&
                level === nextStep.sae_level &&
                stage === nextStep.epias_stage;

            let classes = 'matrix-cell';
            if (isCurrent) classes += ' current';
            else if (isNext) classes += ' next-step';

            let title = '';
            let ariaLabel = levelAccessible[level] + ', ' + stageLabels[stage];
            if (isCurrent) {
                title = 'You are here';
                ariaLabel += ': Your current position';
            } else if (isNext) {
                title = 'Next step';
                ariaLabel += ': Suggested next step';
            }

            html += `<td class="${classes}" title="${title}" role="cell" aria-label="${ariaLabel}"`;
            if (isCurrent) html += ' aria-current="true"';
            html += '>';
            if (isCurrent) {
                html += '<span style="font-size: 1.2rem;" aria-hidden="true">You</span>';
            } else if (isNext) {
                html += '<span style="font-size: 0.9rem; color: var(--success);" aria-hidden="true">Next</span>';
            }
            html += '</td>';
        });

        html += '</tr>';
    });

    html += '</tbody></table>';

    // Legend
    html += `
        <div style="display: flex; gap: 1.5rem; margin-top: 0.75rem; font-size: 0.8rem; color: var(--text-muted);" role="img" aria-label="Legend: blue highlight is your position, green dashed is suggested next step">
            <span aria-hidden="true"><span style="display: inline-block; width: 12px; height: 12px; background: var(--primary-light); border: 2px solid var(--primary); border-radius: 2px; vertical-align: middle;"></span> Your position</span>
            <span aria-hidden="true"><span style="display: inline-block; width: 12px; height: 12px; background: #d1fae5; border: 2px dashed var(--success); border-radius: 2px; vertical-align: middle;"></span> Suggested next step</span>
        </div>
    `;

    container.innerHTML = html;
}
