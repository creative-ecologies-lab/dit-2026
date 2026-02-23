/**
 * DIT Assessment — Self-assessment questionnaire logic.
 * Handles two-stage assessment: SAE Level → EPIAS Maturity.
 * Persists progress in sessionStorage so users can navigate away and return.
 */

(function() {
    'use strict';

    const STORAGE_KEY = 'ditAssessmentState';

    const state = {
        currentQuestion: 0,
        saeAnswers: {},
        epiasAnswers: {},
        saeLevel: null,
        stage: 'intake', // 'intake', 'sae', or 'epias'
        epiasQuestions: [],
        cohort: '',
        ageRange: '',
        role: '',
    };

    const totalSaeQuestions = SAE_QUESTIONS.length;

    // ---- State Persistence ----

    function saveState() {
        sessionStorage.setItem(STORAGE_KEY, JSON.stringify({
            currentQuestion: state.currentQuestion,
            saeAnswers: state.saeAnswers,
            epiasAnswers: state.epiasAnswers,
            saeLevel: state.saeLevel,
            stage: state.stage,
            epiasQuestions: state.epiasQuestions,
            cohort: state.cohort,
            ageRange: state.ageRange,
            role: state.role,
        }));
    }

    function restoreState() {
        const saved = sessionStorage.getItem(STORAGE_KEY);
        if (!saved) return false;
        try {
            const parsed = JSON.parse(saved);
            state.currentQuestion = parsed.currentQuestion || 0;
            state.saeAnswers = parsed.saeAnswers || {};
            state.epiasAnswers = parsed.epiasAnswers || {};
            state.saeLevel = parsed.saeLevel;
            state.stage = parsed.stage || 'intake';
            state.epiasQuestions = parsed.epiasQuestions || [];
            state.cohort = parsed.cohort || '';
            state.ageRange = parsed.ageRange || '';
            state.role = parsed.role || '';
            return true;
        } catch { return false; }
    }

    function clearState() {
        sessionStorage.removeItem(STORAGE_KEY);
    }

    function startFresh() {
        clearState();
        state.currentQuestion = 0;
        state.saeAnswers = {};
        state.epiasAnswers = {};
        state.saeLevel = null;
        state.stage = 'intake';
        state.epiasQuestions = [];
        state.cohort = '';
        state.ageRange = '';
        state.role = '';

        document.getElementById('completedStage').style.display = 'none';
        document.getElementById('saeStage').style.display = 'none';
        document.getElementById('epiasStage').style.display = 'none';
        document.getElementById('intakeStage').style.display = '';
        document.getElementById('progressBar').style.display = 'none';
        document.getElementById('progressText').style.display = 'none';
        initIntake();
    }

    // ---- Rendering ----

    function renderSaeQuestion(idx) {
        const q = SAE_QUESTIONS[idx];
        const container = document.getElementById('saeQuestions');
        container.innerHTML = `
            <div class="question-card">
                <h3>Question ${idx + 1} of ${totalSaeQuestions}</h3>
                <p style="margin-bottom: 0.75rem; font-weight: 500;">${q.question}</p>
                <div class="option-list">
                    ${q.options.map(opt => `
                        <label class="option-item ${state.saeAnswers[q.id] === opt.level ? 'selected' : ''}"
                               data-qid="${q.id}" data-value="${opt.level}">
                            <input type="radio" name="${q.id}" value="${opt.level}">
                            ${opt.text}
                        </label>
                    `).join('')}
                </div>
            </div>
        `;

        container.querySelectorAll('.option-item').forEach(el => {
            el.addEventListener('click', () => {
                const qid = el.dataset.qid;
                const val = parseInt(el.dataset.value);
                state.saeAnswers[qid] = val;
                saveState();
                renderSaeQuestion(idx);
                updateButtons();
                // Auto-advance after brief visual feedback
                setTimeout(() => {
                    if (idx < totalSaeQuestions - 1) {
                        state.currentQuestion = idx + 1;
                        saveState();
                        renderSaeQuestion(state.currentQuestion);
                    } else {
                        transitionToEpias();
                    }
                }, 300);
            });
        });

        updateProgress();
        updateButtons();
    }

    function renderEpiasQuestion(idx) {
        const q = state.epiasQuestions[idx];
        const container = document.getElementById('epiasQuestions');
        container.innerHTML = `
            <div class="question-card">
                <h3>Question ${idx + 1} of ${state.epiasQuestions.length}</h3>
                <p style="margin-bottom: 0.75rem; font-weight: 500;">${q.question}</p>
                <div class="option-list">
                    ${q.options.map(opt => `
                        <label class="option-item ${state.epiasAnswers[q.id] === opt.stage ? 'selected' : ''}"
                               data-qid="${q.id}" data-value="${opt.stage}">
                            <input type="radio" name="${q.id}" value="${opt.stage}">
                            ${opt.text}
                        </label>
                    `).join('')}
                </div>
            </div>
        `;

        container.querySelectorAll('.option-item').forEach(el => {
            el.addEventListener('click', () => {
                const qid = el.dataset.qid;
                const val = el.dataset.value;
                state.epiasAnswers[qid] = val;
                saveState();
                renderEpiasQuestion(idx);
                updateButtons();
                // Auto-advance after brief visual feedback
                setTimeout(() => {
                    if (idx < state.epiasQuestions.length - 1) {
                        state.currentQuestion = idx + 1;
                        saveState();
                        renderEpiasQuestion(state.currentQuestion);
                    } else {
                        submitAssessment();
                    }
                }, 300);
            });
        });

        updateProgress();
        updateButtons();
    }

    function updateProgress() {
        const fill = document.getElementById('progressFill');
        const text = document.getElementById('progressText');

        if (state.stage === 'sae') {
            const pct = ((state.currentQuestion + 1) / (totalSaeQuestions + state.epiasQuestions.length || 5)) * 100;
            fill.style.width = Math.min(pct, 50) + '%';
            text.textContent = `Step 1 of 2 — Question ${state.currentQuestion + 1} of ${totalSaeQuestions}`;
        } else {
            const baseP = 50;
            const total = state.epiasQuestions.length || 5;
            const pct = baseP + ((state.currentQuestion + 1) / total) * 50;
            fill.style.width = pct + '%';
            text.textContent = `Step 2 of 2 — Question ${state.currentQuestion + 1} of ${total}`;
        }
    }

    function updateButtons() {
        if (state.stage === 'sae') {
            const prevBtn = document.getElementById('saePrev');
            const nextBtn = document.getElementById('saeNext');
            prevBtn.disabled = state.currentQuestion === 0;

            const currentQ = SAE_QUESTIONS[state.currentQuestion];
            const answered = state.saeAnswers[currentQ.id] !== undefined;

            if (state.currentQuestion === totalSaeQuestions - 1) {
                nextBtn.textContent = answered ? 'Continue to Step 2' : 'Select an answer';
                nextBtn.disabled = !answered;
            } else {
                nextBtn.textContent = 'Next';
                nextBtn.disabled = !answered;
            }
        } else {
            const prevBtn = document.getElementById('epiasPrev');
            const nextBtn = document.getElementById('epiasNext');
            prevBtn.disabled = false;

            const currentQ = state.epiasQuestions[state.currentQuestion];
            const answered = state.epiasAnswers[currentQ.id] !== undefined;

            if (state.currentQuestion === state.epiasQuestions.length - 1) {
                nextBtn.textContent = answered ? 'See Results' : 'Select an answer';
                nextBtn.disabled = !answered;
            } else {
                nextBtn.textContent = 'Next';
                nextBtn.disabled = !answered;
            }
        }
    }

    // ---- SAE Level Calculation ----

    function calculateSaeLevel() {
        const values = Object.values(state.saeAnswers).sort((a, b) => a - b);
        if (values.length === 0) return 1;
        return values[Math.floor(values.length / 2)];
    }

    const SAE_NAMES = {
        0: 'L0: Manual', 1: 'L1: AI-Assisted', 2: 'L2: Partially Automated',
        3: 'L3: Guided Automation', 4: 'L4: Mostly Automated', 5: 'L5: Full Automation'
    };

    // ---- Stage Transitions ----

    async function transitionToEpias() {
        state.saeLevel = calculateSaeLevel();
        document.getElementById('identifiedLevel').textContent =
            SAE_NAMES[state.saeLevel] || `SAE L${state.saeLevel}`;

        try {
            const resp = await fetch('/api/epias-questions?' + new URLSearchParams({level: state.saeLevel}));
            if (resp.ok) {
                state.epiasQuestions = await resp.json();
            }
        } catch (e) {
            console.warn('Failed to fetch EPIAS questions, using defaults');
        }

        if (!state.epiasQuestions || state.epiasQuestions.length === 0) {
            state.epiasQuestions = generateFallbackEpiasQuestions(state.saeLevel);
        }

        state.stage = 'epias';
        state.currentQuestion = 0;
        saveState();

        document.getElementById('saeStage').style.display = 'none';
        document.getElementById('epiasStage').style.display = '';
        renderEpiasQuestion(0);
    }

    function generateFallbackEpiasQuestions(level) {
        return [
            {
                id: `epias_fb_consistency_${level}`,
                question: 'How consistent are your outputs at this level?',
                options: [
                    {stage: 'E', text: 'Inconsistent — still experimenting and learning.'},
                    {stage: 'P', text: 'Predictable — I have reliable habits and processes.'},
                    {stage: 'I', text: 'Integrated — fully embedded in my workflow with validation.'},
                    {stage: 'A', text: 'Systematic — I\'ve built reusable systems others adopt.'},
                    {stage: 'S', text: 'Standard-setting — I define and maintain organizational standards.'},
                ]
            },
            {
                id: `epias_fb_sharing_${level}`,
                question: 'How do you share your practices at this level?',
                options: [
                    {stage: 'E', text: 'I mostly learn from others.'},
                    {stage: 'P', text: 'I share tips informally.'},
                    {stage: 'I', text: 'I contribute to team knowledge and reviews.'},
                    {stage: 'A', text: 'Others rely on my reusable assets.'},
                    {stage: 'S', text: 'I run training and set standards for the organization.'},
                ]
            },
            {
                id: `epias_fb_judgment_${level}`,
                question: 'How strong is your judgment at this level?',
                options: [
                    {stage: 'E', text: 'Developing — I\'m still building intuition.'},
                    {stage: 'P', text: 'Solid — I know what works and what doesn\'t.'},
                    {stage: 'I', text: 'Articulate — I can explain my reasoning clearly.'},
                    {stage: 'A', text: 'Transferable — I\'ve codified judgment into guidelines.'},
                    {stage: 'S', text: 'Authoritative — I set the standard for judgment.'},
                ]
            },
            {
                id: `epias_fb_process_${level}`,
                question: 'How structured is your process at this level?',
                options: [
                    {stage: 'E', text: 'Ad-hoc — I figure it out as I go.'},
                    {stage: 'P', text: 'Repeatable — I follow consistent steps.'},
                    {stage: 'I', text: 'Integrated — my process connects end-to-end.'},
                    {stage: 'A', text: 'Designed — I\'ve built processes others follow.'},
                    {stage: 'S', text: 'Governed — I maintain and evolve org processes.'},
                ]
            },
            {
                id: `epias_fb_accountability_${level}`,
                question: 'How do you handle accountability at this level?',
                options: [
                    {stage: 'E', text: 'Informal — accountability is implicit.'},
                    {stage: 'P', text: 'Personal — I take responsibility for my outputs.'},
                    {stage: 'I', text: 'Documented — decisions are traceable and reviewable.'},
                    {stage: 'A', text: 'Systemic — accountability frameworks exist for teams.'},
                    {stage: 'S', text: 'Organizational — I set accountability standards.'},
                ]
            },
        ];
    }

    let submitting = false;

    async function submitAssessment() {
        if (submitting) return;
        submitting = true;
        document.getElementById('epiasStage').style.display = 'none';
        document.getElementById('loadingStage').style.display = 'block';

        const payload = {
            ...state.saeAnswers,
            ...state.epiasAnswers,
        };
        if (state.cohort) payload.cohort = state.cohort;
        if (state.ageRange) payload.age_range = state.ageRange;
        if (state.role) payload.role = state.role;

        try {
            const resp = await fetch('/api/assess', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload),
            });
            const result = await resp.json();

            sessionStorage.setItem('ditResult', JSON.stringify(result));
            clearState();
            window.location.href = '/results';
        } catch (e) {
            console.error('Assessment submission failed:', e);
            submitting = false;
            document.getElementById('loadingStage').style.display = 'none';
            document.getElementById('epiasStage').style.display = '';
            alert('Failed to submit assessment. Please try again.');
        }
    }

    // ---- Intake Stage ----

    function initIntake() {
        const cohortInput = document.getElementById('intakeCohort');
        const ageSelect = document.getElementById('intakeAge');
        const roleInput = document.getElementById('intakeRole');

        // Pre-fill cohort from URL param
        if (URL_COHORT) {
            cohortInput.value = URL_COHORT;
        }

        document.getElementById('intakeStart').addEventListener('click', () => {
            state.cohort = (cohortInput.value || '').trim().toLowerCase();
            state.ageRange = ageSelect.value || '';
            state.role = (roleInput.value || '').trim();
            transitionToSae();
        });

        document.getElementById('intakeSkip').addEventListener('click', () => {
            transitionToSae();
        });
    }

    function transitionToSae() {
        state.stage = 'sae';
        state.currentQuestion = 0;
        saveState();
        document.getElementById('intakeStage').style.display = 'none';
        document.getElementById('saeStage').style.display = '';
        document.getElementById('progressBar').style.display = '';
        document.getElementById('progressText').style.display = '';
        renderSaeQuestion(0);
    }

    // ---- Event Handlers ----

    document.getElementById('saePrev').addEventListener('click', () => {
        if (state.currentQuestion > 0) {
            state.currentQuestion--;
            saveState();
            renderSaeQuestion(state.currentQuestion);
        }
    });

    document.getElementById('saeNext').addEventListener('click', () => {
        if (state.currentQuestion < totalSaeQuestions - 1) {
            state.currentQuestion++;
            saveState();
            renderSaeQuestion(state.currentQuestion);
        } else {
            transitionToEpias();
        }
    });

    document.getElementById('epiasPrev').addEventListener('click', () => {
        if (state.currentQuestion > 0) {
            state.currentQuestion--;
            saveState();
            renderEpiasQuestion(state.currentQuestion);
        } else {
            state.stage = 'sae';
            state.currentQuestion = totalSaeQuestions - 1;
            saveState();
            document.getElementById('epiasStage').style.display = 'none';
            document.getElementById('saeStage').style.display = '';
            renderSaeQuestion(state.currentQuestion);
        }
    });

    document.getElementById('epiasNext').addEventListener('click', () => {
        if (state.currentQuestion < state.epiasQuestions.length - 1) {
            state.currentQuestion++;
            saveState();
            renderEpiasQuestion(state.currentQuestion);
        } else {
            submitAssessment();
        }
    });

    document.getElementById('retakeBtn').addEventListener('click', startFresh);

    // ---- Init ----

    const hasResults = sessionStorage.getItem('ditResult');
    if (hasResults) {
        // Already completed — show prompt
        document.getElementById('intakeStage').style.display = 'none';
        document.getElementById('saeStage').style.display = 'none';
        document.getElementById('completedStage').style.display = 'block';
        document.getElementById('progressBar').style.display = 'none';
        document.getElementById('progressText').style.display = 'none';
    } else if (restoreState()) {
        // Resume in-progress assessment
        if (state.stage === 'epias' && state.epiasQuestions.length > 0) {
            document.getElementById('intakeStage').style.display = 'none';
            document.getElementById('saeStage').style.display = 'none';
            document.getElementById('epiasStage').style.display = '';
            document.getElementById('identifiedLevel').textContent =
                SAE_NAMES[state.saeLevel] || `SAE L${state.saeLevel}`;
            renderEpiasQuestion(state.currentQuestion);
        } else if (state.stage === 'sae') {
            document.getElementById('intakeStage').style.display = 'none';
            document.getElementById('saeStage').style.display = '';
            renderSaeQuestion(state.currentQuestion);
        } else {
            // intake stage — show intake form
            document.getElementById('progressBar').style.display = 'none';
            document.getElementById('progressText').style.display = 'none';
            initIntake();
        }
    } else {
        // Fresh start — show intake
        document.getElementById('progressBar').style.display = 'none';
        document.getElementById('progressText').style.display = 'none';
        initIntake();
    }

})();
