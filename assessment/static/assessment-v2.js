/**
 * DIT Assessment v2 — Tree-Shaped Designer
 *
 * Three-stage assessment:
 *   Part 1: Root questions (craft foundation depth) — always 5 questions
 *   Part 2: SAE questions (AI automation level) — always 6 questions
 *   Part 3: Canopy questions (AI practice depth at detected SAE level) — 5 questions
 *           Skipped if SAE = 0 (no AI practice to measure)
 *
 * Result: dual code (L0-P / L2-I) + tree silhouette
 */

(function() {
    'use strict';

    const STORAGE_KEY = 'ditAssessmentV2State';
    const STAGE_NAMES = {E: 'Explorer', P: 'Practitioner', I: 'Integrator', A: 'Architect', S: 'Steward'};

    // Jargon glossary (same as v1)
    const JARGON = {
        'agent harnesses': 'Automated systems that run AI tasks, check results, and retry if needed',
        'harness configs': 'Settings files that control how automated AI pipelines run',
        'harnesses': 'Automated systems that run AI tasks, check results, and retry if needed',
        'eval suites': 'Automated tests that check if AI output meets quality standards',
        'evals': 'Automated tests that check AI output quality',
        'context engineering': 'Designing the instructions, examples, and rules given to an AI',
        'context blocks': 'Structured sections of instructions given to an AI system',
        'context libraries': 'Reusable collections of AI instructions and rules',
        'MCP tools': 'Plugins that let AI connect to external data and services',
        'IDE': 'Code editor or design tool (like VS Code, Figma, or Cursor)',
        'agent infrastructure': 'Production systems that run AI tasks automatically for a team',
        'agent pipelines': 'Multi-step automated AI workflows',
        'leadership stage': 'How you lead with AI \u2014 from experimenting to setting standards',
        'flagged exceptions': 'Problems the AI found but couldn\'t fix on its own',
        'self-improving harnesses': 'AI systems that get better automatically based on past results',
        'run-loop template': 'A reusable script that runs AI steps in order',
        'RACI': 'A chart showing who is Responsible, Accountable, Consulted, and Informed',
        'audit trail': 'A record showing what AI did and what decisions you made',
        'eval gates': 'Automated checkpoints that test whether AI output meets standards',
        'context systems': 'Structured instructions, rules, and examples that guide AI workflows',
    };

    function addTooltips(text) {
        let result = text;
        const terms = Object.keys(JARGON).sort((a, b) => b.length - a.length);
        for (const term of terms) {
            const regex = new RegExp(`\\b${term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'gi');
            result = result.replace(regex, (match) =>
                `<span class="jargon" data-tip="${JARGON[term]}" tabindex="0">${match}</span>`
            );
        }
        return result;
    }

    const state = {
        currentQuestion: 0,
        rootAnswers: {},
        saeAnswers: {},
        canopyAnswers: {},
        saeLevel: null,
        stage: 'intake', // intake, root_intro, root, root_transition, sae_intro, sae, sae_transition, canopy, completed
        canopyQuestions: [],
        cohort: '',
        role: '',
        treeId: null,
    };

    // ---- State Persistence ----

    function saveState() {
        sessionStorage.setItem(STORAGE_KEY, JSON.stringify({
            currentQuestion: state.currentQuestion,
            rootAnswers: state.rootAnswers,
            saeAnswers: state.saeAnswers,
            canopyAnswers: state.canopyAnswers,
            saeLevel: state.saeLevel,
            stage: state.stage,
            canopyQuestions: state.canopyQuestions,
            cohort: state.cohort,
            role: state.role,
            treeId: state.treeId,
        }));
    }

    /** Save progress to server at stage boundaries. */
    function saveProgressToServer(stageName) {
        var allAnswers = {};
        Object.keys(state.rootAnswers).forEach(function(k) { allAnswers[k] = state.rootAnswers[k]; });
        Object.keys(state.saeAnswers).forEach(function(k) { allAnswers[k] = state.saeAnswers[k]; });
        Object.keys(state.canopyAnswers).forEach(function(k) { allAnswers[k] = state.canopyAnswers[k]; });

        var body = JSON.stringify({
            tree_id: state.treeId || '',
            stage: stageName,
            answers: allAnswers,
            role: state.role,
            cohort: state.cohort,
        });

        fetch('/api/tree-progress', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: body,
        }).then(function(resp) {
            return resp.json();
        }).then(function(data) {
            if (data.tree_id && !state.treeId) {
                state.treeId = data.tree_id;
                saveState();
            }
            if (state.treeId) {
                try { showTreeIdBar(state.treeId); } catch(e) {}
            }
        }).catch(function(e) {
            console.warn('Failed to save progress:', e);
        });
    }

    /** No-op — tree ID only shown on results page */
    function showTreeIdBar(id) {}

    function restoreState() {
        const saved = sessionStorage.getItem(STORAGE_KEY);
        if (!saved) return false;
        try {
            const p = JSON.parse(saved);
            Object.assign(state, {
                currentQuestion: p.currentQuestion || 0,
                rootAnswers: p.rootAnswers || {},
                saeAnswers: p.saeAnswers || {},
                canopyAnswers: p.canopyAnswers || {},
                saeLevel: p.saeLevel,
                stage: p.stage || 'intake',
                canopyQuestions: p.canopyQuestions || [],
                cohort: p.cohort || '',
                role: p.role || '',
                treeId: p.treeId || null,
            });
            if (state.treeId) showTreeIdBar(state.treeId);
            if (state.role === 'uxr') {
                SAE_QUESTIONS = SAE_QUESTIONS_UXR;
                ROOT_QUESTIONS = ROOT_QUESTIONS_UXR;
            } else {
                SAE_QUESTIONS = SAE_QUESTIONS_DESIGN;
                ROOT_QUESTIONS = ROOT_QUESTIONS_DESIGN;
            }
            return true;
        } catch { return false; }
    }

    function clearState() { sessionStorage.removeItem(STORAGE_KEY); }

    function startFresh() {
        clearState();
        Object.assign(state, {
            currentQuestion: 0,
            rootAnswers: {},
            saeAnswers: {},
            canopyAnswers: {},
            saeLevel: null,
            stage: 'intake',
            canopyQuestions: [],
            cohort: '',
            role: '',
        });
        SAE_QUESTIONS = SAE_QUESTIONS_DESIGN;
        ROOT_QUESTIONS = ROOT_QUESTIONS_DESIGN;
        hideAllStages();
        document.getElementById('intakeStage').style.display = '';
        initIntake();
    }

    function hideAllStages() {
        ['intakeStage', 'rootStage', 'rootTransition', 'saeStage',
         'saeTransition', 'canopyStage', 'completedStage', 'loadingStage'
        ].forEach(id => { document.getElementById(id).style.display = 'none'; });
    }

    // ---- Generic Question Rendering ----

    function renderQuestion(containerId, progressId, questions, answers, idx, onSelect) {
        const q = questions[idx];
        const total = questions.length;
        const container = document.getElementById(containerId);
        document.getElementById(progressId).textContent = `Question ${idx + 1} of ${total}`;

        const isStageAnswer = typeof q.options[0].stage === 'string';
        container.innerHTML = `
            <div class="q-card" role="group" aria-labelledby="q-heading-${containerId}">
                <h2 id="q-heading-${containerId}" tabindex="-1">${q.question}</h2>
                <div class="q-options" role="radiogroup" aria-labelledby="q-heading-${containerId}">
                    ${q.options.map((opt, i) => {
                        const val = isStageAnswer ? opt.stage : opt.level;
                        const selected = answers[q.id] === val;
                        return `
                        <button class="q-option ${selected ? 'selected' : ''}"
                                data-qid="${q.id}" data-value="${val}"
                                role="radio" aria-checked="${selected}"
                                aria-label="${opt.text}">
                            <span class="q-option-key">${String.fromCharCode(65 + i)}</span>
                            <span class="q-option-text">${addTooltips(opt.text)}</span>
                        </button>`;
                    }).join('')}
                </div>
                <div class="q-confirmation" id="confirm-${containerId}" role="status" aria-live="polite"></div>
            </div>
        `;

        container.querySelectorAll('.q-option').forEach(el => {
            el.addEventListener('click', () => onSelect(el, idx));
            el.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onSelect(el, idx); }
            });
        });

        var heading = container.querySelector('h2');
        if (heading) heading.focus();
    }

    function handleSelect(el, answers, questions, containerId) {
        const qid = el.dataset.qid;
        let val = el.dataset.value;
        // Convert numeric strings to int for SAE answers
        if (!isNaN(val) && val !== '') val = parseInt(val);
        answers[qid] = val;
        saveState();

        el.closest('.q-options').querySelectorAll('.q-option').forEach(o => {
            o.classList.remove('selected');
            o.setAttribute('aria-checked', 'false');
        });
        el.classList.add('selected');
        el.setAttribute('aria-checked', 'true');

        const conf = document.getElementById(`confirm-${containerId}`);
        const answered = Object.keys(answers).length;
        conf.textContent = `Got it! (${answered} of ${questions.length} answered)`;
        conf.classList.add('visible');
    }

    // ---- Stage: Root Questions ----

    function showRootIntro() {
        const container = document.getElementById('rootQuestions');
        document.getElementById('rootProgress').textContent = 'Part 1 of 3';
        container.innerHTML = `
            <div class="q-card" role="group" aria-labelledby="root-intro-heading">
                <h2 id="root-intro-heading" tabindex="-1">Your Craft Foundation</h2>
                <p class="transition-part2" style="border-top:none; padding-top:0;">
                    Part 1 measures the depth of your traditional craft skills — your roots.
                    Think about your core abilities <strong>independent of any AI tools</strong>.
                    Choose the single best answer for each question.
                </p>
            </div>
        `;
        document.getElementById('rootPrev').disabled = false;
        document.getElementById('rootNext').disabled = false;
        var heading = container.querySelector('h2');
        if (heading) heading.focus();
    }

    function renderRootQuestion(idx) {
        renderQuestion('rootQuestions', 'rootProgress', ROOT_QUESTIONS, state.rootAnswers, idx,
            (el, i) => {
                handleSelect(el, state.rootAnswers, ROOT_QUESTIONS, 'rootQuestions');
                if (window.dit) dit.track('root_answer', {question: i + 1, stage: el.dataset.value});
                updateRootNav();
            }
        );
        updateRootNav();
    }

    function updateRootNav() {
        const prevBtn = document.getElementById('rootPrev');
        const nextBtn = document.getElementById('rootNext');
        prevBtn.disabled = false;

        if (state.currentQuestion === -1) {
            nextBtn.textContent = '\u2192';
            nextBtn.disabled = false;
            return;
        }

        const q = ROOT_QUESTIONS[state.currentQuestion];
        const answered = state.rootAnswers[q.id] !== undefined;
        if (state.currentQuestion === ROOT_QUESTIONS.length - 1) {
            nextBtn.textContent = answered ? 'Continue \u2192' : '\u2192';
            nextBtn.disabled = !answered;
        } else {
            nextBtn.textContent = '\u2192';
            nextBtn.disabled = !answered;
        }
    }

    function calculateRootStage() {
        const values = Object.values(state.rootAnswers).map(v => ({E:1,P:2,I:3,A:4,S:5}[v] || 1));
        if (values.length === 0) return 'E';
        const sorted = values.sort((a,b) => a - b);
        const median = sorted[Math.floor(sorted.length / 2)];
        return {1:'E',2:'P',3:'I',4:'A',5:'S'}[median] || 'E';
    }

    function showRootTransition() {
        saveProgressToServer('root');
        const rootStage = calculateRootStage();
        const container = document.getElementById('rootTransitionContent');
        container.innerHTML = `
            <p class="transition-result-label">Part 1 result</p>
            <h2 tabindex="-1">Root Depth: ${STAGE_NAMES[rootStage]}</h2>
            <p class="transition-description">Your craft foundation is at the <strong>${STAGE_NAMES[rootStage]}</strong> level — this determines how deep your roots grow.</p>
            <p class="transition-part2">Part 2 measures your AI automation level — how far your branches spread. Choose the single best answer for each question.</p>
        `;
        hideAllStages();
        document.getElementById('rootTransition').style.display = '';
        var heading = container.querySelector('h2');
        if (heading) heading.focus();
    }

    // ---- Stage: SAE Questions ----

    function showSaeIntro() {
        const container = document.getElementById('saeQuestions');
        document.getElementById('saeProgress').textContent = 'Part 2 of 3';
        container.innerHTML = `
            <div class="q-card" role="group" aria-labelledby="sae-intro-heading">
                <h2 id="sae-intro-heading" tabindex="-1">Your AI Practice</h2>
                <p class="transition-part2" style="border-top:none; padding-top:0;">
                    Part 2 measures your level of AI automation — how far your branches spread.
                    Choose the single best answer that describes where you are <strong>today</strong>, not where you'd like to be.
                </p>
            </div>
        `;
        document.getElementById('saePrev').disabled = false;
        document.getElementById('saeNext').disabled = false;
        var heading = container.querySelector('h2');
        if (heading) heading.focus();
    }

    function renderSaeQuestion(idx) {
        renderQuestion('saeQuestions', 'saeProgress', SAE_QUESTIONS, state.saeAnswers, idx,
            (el, i) => {
                handleSelect(el, state.saeAnswers, SAE_QUESTIONS, 'saeQuestions');
                if (window.dit) dit.track('sae_answer', {question: i + 1, level: el.dataset.value});
                updateSaeNav();
            }
        );
        updateSaeNav();
    }

    function updateSaeNav() {
        const prevBtn = document.getElementById('saePrev');
        const nextBtn = document.getElementById('saeNext');
        prevBtn.disabled = false;

        if (state.currentQuestion === -1) {
            nextBtn.textContent = '\u2192';
            nextBtn.disabled = false;
            return;
        }

        const q = SAE_QUESTIONS[state.currentQuestion];
        const answered = state.saeAnswers[q.id] !== undefined;
        if (state.currentQuestion === SAE_QUESTIONS.length - 1) {
            nextBtn.textContent = answered ? 'Continue \u2192' : '\u2192';
            nextBtn.disabled = !answered;
        } else {
            nextBtn.textContent = '\u2192';
            nextBtn.disabled = !answered;
        }
    }

    function calculateSaeLevel() {
        const values = Object.values(state.saeAnswers).map(v => parseInt(v)).filter(v => !isNaN(v));
        if (values.length === 0) return 0;
        const sorted = values.sort((a,b) => a - b);
        return sorted[Math.floor(sorted.length / 2)];
    }

    const SAE_LEVEL_NAMES = {
        0: 'Level 0 \u2014 Manual', 1: 'Level 1 \u2014 AI-Assisted',
        2: 'Level 2 \u2014 Partially Automated', 3: 'Level 3 \u2014 Guided Automation',
        4: 'Level 4 \u2014 Mostly Automated', 5: 'Level 5 \u2014 Full Automation',
    };

    async function showSaeTransition() {
        state.saeLevel = calculateSaeLevel();
        saveProgressToServer('sae');
        if (window.dit) dit.track('sae_complete', {level: state.saeLevel});

        // If SAE = 0, skip canopy — go straight to results
        if (state.saeLevel === 0) {
            state.stage = 'sae_transition';
            saveState();
            const container = document.getElementById('saeTransitionContent');
            container.innerHTML = `
                <p class="transition-result-label">Part 2 result</p>
                <h2 tabindex="-1">${SAE_LEVEL_NAMES[0]}</h2>
                <p class="transition-description">You don't currently use AI tools in your workflow. Your tree is all roots \u2014 a strong craft foundation with no AI canopy.</p>
                <p class="transition-part2">This is a valid and valuable form. Deep roots hold the soil together.</p>
            `;
            hideAllStages();
            document.getElementById('saeTransition').style.display = '';
            document.getElementById('saeTransitionContinue').textContent = 'See Results \u2192';
            var heading = container.querySelector('h2');
            if (heading) heading.focus();
            return;
        }

        // Fetch canopy EPIAS questions for detected SAE level
        try {
            const resp = await fetch('/api/epias-questions?' + new URLSearchParams({
                level: state.saeLevel,
                role: state.role || 'design',
            }));
            if (resp.ok) {
                state.canopyQuestions = await resp.json();
            }
        } catch (e) {
            console.warn('Failed to fetch canopy questions');
        }

        if (!state.canopyQuestions || state.canopyQuestions.length === 0) {
            state.canopyQuestions = []; // Will use fallback
        }

        state.stage = 'sae_transition';
        saveState();

        const container = document.getElementById('saeTransitionContent');
        container.innerHTML = `
            <p class="transition-result-label">Part 2 result</p>
            <h2 tabindex="-1">${SAE_LEVEL_NAMES[state.saeLevel]}</h2>
            <p class="transition-description">This determines how far your branches spread \u2014 your AI canopy width.</p>
            <p class="transition-part2">Part 3 measures how deep your AI practice runs at this level \u2014 your canopy height. Choose the single best answer for each question.</p>
        `;
        hideAllStages();
        document.getElementById('saeTransition').style.display = '';
        document.getElementById('saeTransitionContinue').textContent = '\u2192';
        var heading = container.querySelector('h2');
        if (heading) heading.focus();
    }

    // ---- Stage: Canopy Questions ----

    function renderCanopyQuestion(idx) {
        renderQuestion('canopyQuestions', 'canopyProgress', state.canopyQuestions, state.canopyAnswers, idx,
            (el, i) => {
                handleSelect(el, state.canopyAnswers, state.canopyQuestions, 'canopyQuestions');
                if (window.dit) dit.track('canopy_answer', {question: i + 1, stage: el.dataset.value});
                updateCanopyNav();
            }
        );
        updateCanopyNav();
    }

    function updateCanopyNav() {
        const prevBtn = document.getElementById('canopyPrev');
        const nextBtn = document.getElementById('canopyNext');
        prevBtn.disabled = false;

        const q = state.canopyQuestions[state.currentQuestion];
        const answered = state.canopyAnswers[q.id] !== undefined;
        if (state.currentQuestion === state.canopyQuestions.length - 1) {
            nextBtn.textContent = answered ? 'See Results \u2192' : '\u2192';
            nextBtn.disabled = !answered;
        } else {
            nextBtn.textContent = '\u2192';
            nextBtn.disabled = !answered;
        }
    }

    // ---- Submit ----

    let submitting = false;

    async function submitAssessment() {
        if (submitting) return;
        submitting = true;
        if (window.dit) dit.track('v2_complete');

        hideAllStages();
        document.getElementById('loadingStage').style.display = 'block';

        const payload = {
            ...state.rootAnswers,
            ...state.saeAnswers,
            ...state.canopyAnswers,
        };
        if (state.cohort) payload.cohort = state.cohort;
        if (state.role) payload.role = state.role;
        if (state.treeId) payload.tree_id = state.treeId;

        // UTM attribution
        const _utmParams = new URLSearchParams(window.location.search);
        const _utm = (k) => _utmParams.get(k) || sessionStorage.getItem('utm_' + k) || null;
        if (_utm('utm_source'))   payload.utm_source   = _utm('utm_source');
        if (_utm('utm_medium'))   payload.utm_medium   = _utm('utm_medium');
        if (_utm('utm_campaign')) payload.utm_campaign = _utm('utm_campaign');

        try {
            const resp = await fetch('/api/assess-v2', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload),
            });
            const result = await resp.json();

            sessionStorage.setItem('ditResultV2', JSON.stringify(result));
            clearState();
            if (window.dit) dit.track('v2_submit', {
                root_stage: result.root_stage,
                sae_level: result.sae_level,
                canopy_stage: result.canopy_stage,
                species: result.tree_species,
                balance: result.balance,
            });
            window.location.href = '/tree/v2/results';
        } catch (e) {
            console.error('Assessment submission failed:', e);
            submitting = false;
            document.getElementById('loadingStage').style.display = 'none';
            // Show last active stage
            if (state.saeLevel === 0) {
                document.getElementById('saeTransition').style.display = '';
            } else {
                document.getElementById('canopyStage').style.display = '';
            }
            alert('Failed to submit assessment. Please try again.');
        }
    }

    // ---- Intake ----

    const intakeCohortInput = document.getElementById('intakeCohort');
    const intakeNextBtn = document.getElementById('intakeNext');
    const intakeRoleBtns = document.querySelectorAll('.role-btn');

    intakeRoleBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            intakeRoleBtns.forEach(b => {
                b.classList.remove('selected');
                b.setAttribute('aria-checked', 'false');
            });
            btn.classList.add('selected');
            btn.setAttribute('aria-checked', 'true');
            state.role = btn.dataset.role;
            if (state.role === 'uxr') {
                SAE_QUESTIONS = SAE_QUESTIONS_UXR;
                ROOT_QUESTIONS = ROOT_QUESTIONS_UXR;
            } else {
                SAE_QUESTIONS = SAE_QUESTIONS_DESIGN;
                ROOT_QUESTIONS = ROOT_QUESTIONS_DESIGN;
            }
            intakeNextBtn.disabled = false;
        });
    });

    const intakeTreeIdInput = document.getElementById('intakeTreeId');
    const treeIdError = document.getElementById('treeIdError');

    // Enable → button when tree ID is entered (even without role selection)
    if (intakeTreeIdInput) {
        intakeTreeIdInput.addEventListener('input', function() {
            var val = (intakeTreeIdInput.value || '').trim();
            if (val.length >= 6) {
                intakeNextBtn.disabled = false;
            } else if (!state.role) {
                intakeNextBtn.disabled = true;
            }
        });
    }

    intakeNextBtn.addEventListener('click', async () => {
        state.cohort = (intakeCohortInput.value || '').trim().toLowerCase();

        // Check for tree ID — resume or retake
        const enteredId = (intakeTreeIdInput ? intakeTreeIdInput.value : '').trim().toUpperCase();
        if (enteredId) {
            intakeNextBtn.disabled = true;
            treeIdError.style.display = 'none';
            try {
                const resp = await fetch('/api/tree-progress/' + encodeURIComponent(enteredId));
                if (!resp.ok) {
                    treeIdError.style.display = '';
                    intakeNextBtn.disabled = false;
                    return;
                }
                const progress = await resp.json();
                state.treeId = progress.tree_id;

                if (progress.status === 'complete') {
                    // Already completed — load results and redirect
                    sessionStorage.setItem('ditResultV2', JSON.stringify(progress));
                    window.location.href = '/tree/v2/results';
                    return;
                }

                // Partial — restore answers and advance to next stage
                const answers = progress.answers || {};
                const stages = progress.completed_stages || [];
                // Restore role from saved progress if available
                if (progress.role && !state.role) {
                    state.role = progress.role;
                    if (state.role === 'uxr') {
                        SAE_QUESTIONS = SAE_QUESTIONS_UXR;
                        ROOT_QUESTIONS = ROOT_QUESTIONS_UXR;
                    } else {
                        SAE_QUESTIONS = SAE_QUESTIONS_DESIGN;
                        ROOT_QUESTIONS = ROOT_QUESTIONS_DESIGN;
                    }
                }

                // Pre-fill answers
                Object.keys(answers).forEach(k => {
                    if (k.startsWith('root_')) state.rootAnswers[k] = answers[k];
                    else if (k.startsWith('sae_')) state.saeAnswers[k] = answers[k];
                    else state.canopyAnswers[k] = answers[k];
                });

                hideAllStages();
                if (!stages.includes('root')) {
                    // Start at roots
                    state.stage = 'root_intro';
                    state.currentQuestion = -1;
                    saveState();
                    document.getElementById('rootStage').style.display = '';
                    showRootIntro();
                } else if (!stages.includes('sae')) {
                    // Skip to SAE
                    showRootTransition();
                } else if (!stages.includes('canopy')) {
                    // Skip to canopy
                    showSaeTransition();
                }
                intakeNextBtn.disabled = false;
                return;
            } catch (e) {
                treeIdError.style.display = '';
                intakeNextBtn.disabled = false;
                return;
            }
        }

        // Without a tree ID, role is required
        if (!state.role) return;

        if (window.dit) dit.track('v2_intake_complete', {role: state.role, cohort: state.cohort || 'none'});

        // Generate tree ID immediately at start
        if (!state.treeId) {
            try {
                const resp = await fetch('/api/tree-progress', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        tree_id: '',
                        stage: 'intake',
                        answers: {},
                        role: state.role,
                        cohort: state.cohort,
                    }),
                });
                const d = await resp.json();
                if (d.tree_id) {
                    state.treeId = d.tree_id;
                    saveState();
                    showTreeIdBar(state.treeId);
                }
            } catch (e) {
                console.warn('Failed to generate tree ID:', e);
            }
        }

        // Start root stage
        state.stage = 'root_intro';
        state.currentQuestion = -1;
        saveState();
        hideAllStages();
        document.getElementById('rootStage').style.display = '';
        showRootIntro();
    });

    function initIntake() {
        if (URL_COHORT) intakeCohortInput.value = URL_COHORT;
        if (state.role) {
            const activeBtn = document.querySelector(`.role-btn[data-role="${state.role}"]`);
            if (activeBtn) {
                activeBtn.classList.add('selected');
                activeBtn.setAttribute('aria-checked', 'true');
            }
            intakeNextBtn.disabled = false;
        }
    }

    // ---- Navigation Event Handlers ----

    // Root nav
    document.getElementById('rootPrev').addEventListener('click', () => {
        if (state.currentQuestion > 0) {
            state.currentQuestion--;
            saveState();
            renderRootQuestion(state.currentQuestion);
        } else if (state.currentQuestion === 0) {
            state.currentQuestion = -1;
            state.stage = 'root_intro';
            saveState();
            showRootIntro();
        } else {
            // Back to intake
            state.stage = 'intake';
            saveState();
            hideAllStages();
            document.getElementById('intakeStage').style.display = '';
            initIntake();
        }
    });

    document.getElementById('rootNext').addEventListener('click', () => {
        if (state.currentQuestion === -1) {
            state.currentQuestion = 0;
            state.stage = 'root';
            saveState();
            renderRootQuestion(0);
        } else if (state.currentQuestion < ROOT_QUESTIONS.length - 1) {
            state.currentQuestion++;
            saveState();
            renderRootQuestion(state.currentQuestion);
        } else {
            // All root questions answered → transition
            if (Object.keys(state.rootAnswers).length < ROOT_QUESTIONS.length) return;
            showRootTransition();
        }
    });

    // Root transition nav
    document.getElementById('rootTransitionBack').addEventListener('click', () => {
        state.stage = 'root';
        state.currentQuestion = ROOT_QUESTIONS.length - 1;
        saveState();
        hideAllStages();
        document.getElementById('rootStage').style.display = '';
        renderRootQuestion(state.currentQuestion);
    });

    document.getElementById('rootTransitionContinue').addEventListener('click', () => {
        // Skip SAE intro — root transition already explained Part 2
        state.stage = 'sae';
        state.currentQuestion = 0;
        saveState();
        hideAllStages();
        document.getElementById('saeStage').style.display = '';
        renderSaeQuestion(0);
    });

    // SAE nav
    document.getElementById('saePrev').addEventListener('click', () => {
        if (state.currentQuestion > 0) {
            state.currentQuestion--;
            saveState();
            renderSaeQuestion(state.currentQuestion);
        } else if (state.currentQuestion === 0) {
            state.currentQuestion = -1;
            state.stage = 'sae_intro';
            saveState();
            showSaeIntro();
        } else {
            // Back to root transition
            state.stage = 'root_transition';
            saveState();
            hideAllStages();
            showRootTransition();
        }
    });

    document.getElementById('saeNext').addEventListener('click', () => {
        if (state.currentQuestion === -1) {
            state.currentQuestion = 0;
            state.stage = 'sae';
            saveState();
            renderSaeQuestion(0);
        } else if (state.currentQuestion < SAE_QUESTIONS.length - 1) {
            state.currentQuestion++;
            saveState();
            renderSaeQuestion(state.currentQuestion);
        } else {
            if (Object.keys(state.saeAnswers).length < SAE_QUESTIONS.length) return;
            showSaeTransition();
        }
    });

    // SAE transition nav
    document.getElementById('saeTransitionBack').addEventListener('click', () => {
        state.stage = 'sae';
        state.currentQuestion = SAE_QUESTIONS.length - 1;
        saveState();
        hideAllStages();
        document.getElementById('saeStage').style.display = '';
        renderSaeQuestion(state.currentQuestion);
    });

    document.getElementById('saeTransitionContinue').addEventListener('click', () => {
        if (state.saeLevel === 0) {
            // No canopy stage — submit directly
            submitAssessment();
        } else {
            state.stage = 'canopy';
            state.currentQuestion = 0;
            saveState();
            hideAllStages();
            document.getElementById('canopyStage').style.display = '';
            renderCanopyQuestion(0);
        }
    });

    // Canopy nav
    document.getElementById('canopyPrev').addEventListener('click', () => {
        if (state.currentQuestion > 0) {
            state.currentQuestion--;
            saveState();
            renderCanopyQuestion(state.currentQuestion);
        } else {
            state.stage = 'sae_transition';
            saveState();
            hideAllStages();
            document.getElementById('saeTransition').style.display = '';
        }
    });

    document.getElementById('canopyNext').addEventListener('click', () => {
        if (state.currentQuestion < state.canopyQuestions.length - 1) {
            state.currentQuestion++;
            saveState();
            renderCanopyQuestion(state.currentQuestion);
        } else {
            submitAssessment();
        }
    });

    // Retake
    document.getElementById('retakeBtn').addEventListener('click', startFresh);

    // ---- Init ----

    const hasResults = sessionStorage.getItem('ditResultV2');
    if (!hasResults && window.dit) dit.track('v2_assess_start');

    if (hasResults) {
        document.getElementById('completedStage').style.display = 'block';
    } else if (restoreState()) {
        // Resume from saved state
        if (state.stage === 'canopy' && state.canopyQuestions.length > 0) {
            document.getElementById('canopyStage').style.display = '';
            renderCanopyQuestion(state.currentQuestion);
        } else if (state.stage === 'sae_transition') {
            document.getElementById('saeTransition').style.display = '';
        } else if (state.stage === 'sae') {
            document.getElementById('saeStage').style.display = '';
            if (state.currentQuestion === -1) showSaeIntro();
            else renderSaeQuestion(state.currentQuestion);
        } else if (state.stage === 'sae_intro') {
            document.getElementById('saeStage').style.display = '';
            showSaeIntro();
        } else if (state.stage === 'root_transition') {
            showRootTransition();
        } else if (state.stage === 'root') {
            document.getElementById('rootStage').style.display = '';
            renderRootQuestion(state.currentQuestion);
        } else if (state.stage === 'root_intro') {
            document.getElementById('rootStage').style.display = '';
            showRootIntro();
        } else {
            document.getElementById('intakeStage').style.display = '';
            initIntake();
        }
    } else {
        document.getElementById('intakeStage').style.display = '';
        initIntake();
    }

})();
