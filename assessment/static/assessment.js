/**
 * DIT Assessment — Self-assessment questionnaire logic.
 * Handles two-stage assessment: SAE Level → EPIAS Leadership Stage.
 * Persists progress in sessionStorage so users can navigate away and return.
 *
 * v3: Typeform-style centered one-question-per-page flow.
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
        role: '',  // 'design' or 'uxr'
    };

    let totalSaeQuestions = SAE_QUESTIONS.length;
    const STAGE_NAMES = {E: 'Explorer', P: 'Practitioner', I: 'Integrator', A: 'Architect', S: 'Steward'};

    // Jargon glossary: term → plain-English tooltip
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

    /** Wrap known jargon terms in tooltip spans. */
    function addTooltips(text) {
        let result = text;
        // Sort by length descending so longer phrases match first
        const terms = Object.keys(JARGON).sort((a, b) => b.length - a.length);
        for (const term of terms) {
            const regex = new RegExp(`\\b${term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'gi');
            result = result.replace(regex, (match) =>
                `<span class="jargon" data-tip="${JARGON[term]}" tabindex="0">${match}</span>`
            );
        }
        return result;
    }

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
            state.role = parsed.role || '';
            // Restore correct question set based on saved role
            if (state.role === 'uxr') {
                SAE_QUESTIONS = SAE_QUESTIONS_UXR;
            } else {
                SAE_QUESTIONS = SAE_QUESTIONS_DESIGN;
            }
            totalSaeQuestions = SAE_QUESTIONS.length;
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
        state.role = '';
        SAE_QUESTIONS = SAE_QUESTIONS_DESIGN;
        totalSaeQuestions = SAE_QUESTIONS.length;

        document.getElementById('completedStage').style.display = 'none';
        document.getElementById('saeStage').style.display = 'none';
        document.getElementById('transitionStage').style.display = 'none';
        document.getElementById('epiasStage').style.display = 'none';
        document.getElementById('intakeStage').style.display = '';
        initIntake();
    }

    // ---- Rendering ----

    function renderSaeQuestion(idx) {
        const q = SAE_QUESTIONS[idx];
        const container = document.getElementById('saeQuestions');

        // Update integrated progress counter
        document.getElementById('saeProgress').textContent =
            `Question ${idx + 1} of ${totalSaeQuestions}`;

        container.innerHTML = `
            <div class="q-card" role="group" aria-labelledby="q-heading">
                <h2 id="q-heading" tabindex="-1">${q.question}</h2>
                <div class="q-options" role="radiogroup" aria-labelledby="q-heading">
                    ${q.options.map((opt, i) => `
                        <button class="q-option ${state.saeAnswers[q.id] === opt.level ? 'selected' : ''}"
                                data-qid="${q.id}" data-value="${opt.level}"
                                role="radio" aria-checked="${state.saeAnswers[q.id] === opt.level}"
                                aria-label="Level ${opt.level}: ${opt.text}">
                            <span class="q-option-key">${String.fromCharCode(65 + i)}</span>
                            <span class="q-option-text">${addTooltips(opt.text)}</span>
                        </button>
                    `).join('')}
                </div>
                <div class="q-confirmation" id="confirmationMsg" role="status" aria-live="polite"></div>
            </div>
        `;

        container.querySelectorAll('.q-option').forEach(el => {
            el.addEventListener('click', () => handleSaeSelect(el, idx));
            el.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    handleSaeSelect(el, idx);
                }
            });
        });

        updateNavButtons();
        var heading = container.querySelector('h2');
        if (heading) heading.focus();
    }

    function handleSaeSelect(el, idx) {
        const qid = el.dataset.qid;
        const val = parseInt(el.dataset.value);
        state.saeAnswers[qid] = val;
        saveState();

        // Visual: mark selected, unmark others
        el.closest('.q-options').querySelectorAll('.q-option').forEach(o => {
            o.classList.remove('selected');
            o.setAttribute('aria-checked', 'false');
        });
        el.classList.add('selected');
        el.setAttribute('aria-checked', 'true');

        // Confirmation message
        const conf = document.getElementById('confirmationMsg');
        const answered = Object.keys(state.saeAnswers).length;
        conf.textContent = `Got it! (${answered} of ${totalSaeQuestions} answered)`;
        conf.classList.add('visible');

        updateNavButtons();

        // Auto-advance after 800ms
        setTimeout(() => {
            conf.classList.remove('visible');
            if (idx < totalSaeQuestions - 1) {
                state.currentQuestion = idx + 1;
                saveState();
                renderSaeQuestion(state.currentQuestion);
            } else {
                transitionToEpias();
            }
        }, 800);
    }

    function renderEpiasQuestion(idx) {
        const q = state.epiasQuestions[idx];
        const total = state.epiasQuestions.length;
        const container = document.getElementById('epiasQuestions');

        // Update integrated progress counter
        document.getElementById('epiasProgress').textContent =
            `Question ${idx + 1} of ${total}`;

        container.innerHTML = `
            <div class="q-card" role="group" aria-labelledby="eq-heading">
                <h2 id="eq-heading" tabindex="-1">${q.question}</h2>
                <div class="q-options" role="radiogroup" aria-labelledby="eq-heading">
                    ${q.options.map((opt, i) => `
                        <button class="q-option ${state.epiasAnswers[q.id] === opt.stage ? 'selected' : ''}"
                                data-qid="${q.id}" data-value="${opt.stage}"
                                role="radio" aria-checked="${state.epiasAnswers[q.id] === opt.stage}"
                                aria-label="${opt.text}">
                            <span class="q-option-key">${String.fromCharCode(65 + i)}</span>
                            <span class="q-option-text">${addTooltips(opt.text)}</span>
                        </button>
                    `).join('')}
                </div>
                <div class="q-confirmation" id="confirmationMsg" role="status" aria-live="polite"></div>
            </div>
        `;

        container.querySelectorAll('.q-option').forEach(el => {
            el.addEventListener('click', () => handleEpiasSelect(el, idx));
            el.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    handleEpiasSelect(el, idx);
                }
            });
        });

        updateNavButtons();
        var heading = container.querySelector('h2');
        if (heading) heading.focus();
    }

    function handleEpiasSelect(el, idx) {
        const qid = el.dataset.qid;
        const val = el.dataset.value;
        state.epiasAnswers[qid] = val;
        saveState();

        // Visual: mark selected, unmark others
        el.closest('.q-options').querySelectorAll('.q-option').forEach(o => {
            o.classList.remove('selected');
            o.setAttribute('aria-checked', 'false');
        });
        el.classList.add('selected');
        el.setAttribute('aria-checked', 'true');

        // Confirmation message
        const conf = document.getElementById('confirmationMsg');
        const answered = Object.keys(state.epiasAnswers).length;
        const total = state.epiasQuestions.length;
        conf.textContent = `Got it! (${answered} of ${total} answered)`;
        conf.classList.add('visible');

        updateNavButtons();

        // Auto-advance after 800ms
        setTimeout(() => {
            conf.classList.remove('visible');
            if (idx < total - 1) {
                state.currentQuestion = idx + 1;
                saveState();
                renderEpiasQuestion(state.currentQuestion);
            } else {
                submitAssessment();
            }
        }, 800);
    }

    function updateNavButtons() {
        if (state.stage === 'sae') {
            const prevBtn = document.getElementById('saePrev');
            const nextBtn = document.getElementById('saeNext');

            // Prev always enabled (goes back to intake on first question)
            prevBtn.disabled = false;

            // Intro screen — next is always enabled
            if (state.currentQuestion === -1) {
                nextBtn.textContent = '\u2192';
                nextBtn.disabled = false;
                nextBtn.setAttribute('aria-label', 'Start Part 1 questions');
                return;
            }

            const currentQ = SAE_QUESTIONS[state.currentQuestion];
            const answered = state.saeAnswers[currentQ.id] !== undefined;

            if (state.currentQuestion === totalSaeQuestions - 1) {
                nextBtn.textContent = answered ? 'Continue \u2192' : '\u2192';
                nextBtn.disabled = !answered;
                nextBtn.setAttribute('aria-label', answered ? 'Continue to leadership stage' : 'Next question');
            } else {
                nextBtn.textContent = '\u2192';
                nextBtn.disabled = !answered;
                nextBtn.setAttribute('aria-label', 'Next question');
            }
        } else if (state.stage === 'epias') {
            const prevBtn = document.getElementById('epiasPrev');
            const nextBtn = document.getElementById('epiasNext');

            prevBtn.disabled = false;

            const currentQ = state.epiasQuestions[state.currentQuestion];
            const answered = state.epiasAnswers[currentQ.id] !== undefined;

            if (state.currentQuestion === state.epiasQuestions.length - 1) {
                nextBtn.textContent = answered ? 'See Results \u2192' : '\u2192';
                nextBtn.disabled = !answered;
                nextBtn.setAttribute('aria-label', answered ? 'See your results' : 'Next question');
            } else {
                nextBtn.textContent = '\u2192';
                nextBtn.disabled = !answered;
                nextBtn.setAttribute('aria-label', 'Next question');
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
        0: 'Manual (Level 0)', 1: 'AI-Assisted (Level 1)', 2: 'Partially Automated (Level 2)',
        3: 'Guided Automation (Level 3)', 4: 'Mostly Automated (Level 4)', 5: 'Full Automation (Level 5)'
    };

    const SAE_TRANSITION = {
        0: {
            name: 'Level 0 — Manual',
            description: 'Work produced entirely through traditional methods — no AI tools in the workflow.',
            part2: 'Part 2 measures how deliberate that choice is — whether you are still deciding about AI, have developed a clear personal method for working without it, or have shaped how your team operates.',
        },
        1: {
            name: 'Level 1 — AI-Assisted',
            description: 'AI used for individual tasks, one at a time, with direct oversight at every step.',
            part2: 'Part 2 measures how deep that practice runs — whether you are still experimenting, have built a consistent personal workflow, or have established patterns your team follows.',
        },
        2: {
            name: 'Level 2 — Partially Automated',
            description: 'AI produces usable pieces from a spec — individual, bounded outputs assembled by hand.',
            part2: 'Part 2 measures how deep that practice runs — whether you are still experimenting, have built a consistent personal workflow, or have established patterns your team follows.',
        },
        3: {
            name: 'Level 3 — Guided Automation',
            description: 'Multi-step AI workflows with checkpoints, persisting across sessions.',
            part2: 'Part 2 measures how deep that practice runs — whether you are still experimenting, have built a consistent personal workflow, or have established patterns your team follows.',
        },
        4: {
            name: 'Level 4 — Mostly Automated',
            description: 'Autonomous AI systems execute, evaluate, and self-correct — human review at the outcome level.',
            part2: 'Part 2 measures how deep that practice runs — whether you are still experimenting, have built a consistent personal workflow, or have established patterns your team follows.',
        },
        5: {
            name: 'Level 5 — Full Automation',
            description: 'AI handles the workflow end-to-end — goals and exceptions are the only human touchpoints.',
            part2: 'Part 2 measures how deep that practice runs — whether you are still experimenting, have built a consistent personal workflow, or have established patterns your team follows.',
        },
    };

    function showTransitionStage(level) {
        const data = SAE_TRANSITION[level] || SAE_TRANSITION[1];
        const container = document.getElementById('transitionContent');
        container.innerHTML = `
            <p class="transition-result-label">Part 1 result</p>
            <h2 tabindex="-1">${data.name}</h2>
            <p class="transition-description">${data.description}</p>
            <p class="transition-part2">${data.part2} Choose the single best answer for each question.</p>
        `;
        document.getElementById('transitionStage').style.display = '';
        const heading = container.querySelector('h2');
        if (heading) heading.focus();
    }

    // ---- Stage Transitions ----

    async function transitionToEpias() {
        // All SAE questions must be answered
        if (Object.keys(state.saeAnswers).length < totalSaeQuestions) return;

        state.saeLevel = calculateSaeLevel();

        try {
            const resp = await fetch('/api/epias-questions?' + new URLSearchParams({
                level: state.saeLevel,
                role: state.role || 'design',
            }));
            if (resp.ok) {
                state.epiasQuestions = await resp.json();
            }
        } catch (e) {
            console.warn('Failed to fetch EPIAS questions, using defaults');
        }

        if (!state.epiasQuestions || state.epiasQuestions.length === 0) {
            state.epiasQuestions = generateFallbackEpiasQuestions(state.saeLevel);
        }

        state.stage = 'transition';
        saveState();

        document.getElementById('saeStage').style.display = 'none';
        showTransitionStage(state.saeLevel);
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
        // All EPIAS questions must be answered
        if (Object.keys(state.epiasAnswers).length < state.epiasQuestions.length) return;
        submitting = true;
        document.getElementById('epiasStage').style.display = 'none';
        document.getElementById('loadingStage').style.display = 'block';

        const payload = {
            ...state.saeAnswers,
            ...state.epiasAnswers,
        };
        if (state.cohort) payload.cohort = state.cohort;
        if (state.role) payload.role = state.role;
        // UTM attribution — captured from URL at page load
        const _utmParams = new URLSearchParams(window.location.search);
        const _utm = (k) => _utmParams.get(k) || sessionStorage.getItem('utm_' + k) || null;
        if (_utm('utm_source'))   payload.utm_source   = _utm('utm_source');
        if (_utm('utm_medium'))   payload.utm_medium   = _utm('utm_medium');
        if (_utm('utm_campaign')) payload.utm_campaign = _utm('utm_campaign');

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

    // Bind intake listeners once (never re-bind)
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
            } else {
                SAE_QUESTIONS = SAE_QUESTIONS_DESIGN;
            }
            totalSaeQuestions = SAE_QUESTIONS.length;
            intakeNextBtn.disabled = false;
        });
    });

    intakeNextBtn.addEventListener('click', () => {
        if (!state.role) return;
        state.cohort = (intakeCohortInput.value || '').trim().toLowerCase();
        transitionToSae();
    });

    function initIntake() {
        // Pre-fill cohort from URL param
        if (URL_COHORT) {
            intakeCohortInput.value = URL_COHORT;
        }

        // Restore role selection if returning to intake
        if (state.role) {
            const activeBtn = document.querySelector(`.role-btn[data-role="${state.role}"]`);
            if (activeBtn) {
                activeBtn.classList.add('selected');
                activeBtn.setAttribute('aria-checked', 'true');
            }
            intakeNextBtn.disabled = false;
        }
    }

    function showSaeIntro() {
        const container = document.getElementById('saeQuestions');
        document.getElementById('saeProgress').textContent = 'Part 1 of 2';
        container.innerHTML = `
            <div class="q-card" role="group" aria-labelledby="sae-intro-heading">
                <h2 id="sae-intro-heading" tabindex="-1">How much does AI do in your workflow?</h2>
                <p class="transition-part2" style="border-top:none; padding-top:0;">Part 1 measures your level of automation — from doing everything manually to running autonomous systems. Choose the single best answer that describes where you are today, not where you'd like to be.</p>
            </div>
        `;
        document.getElementById('saePrev').disabled = false;
        document.getElementById('saeNext').disabled = false;
        const heading = container.querySelector('h2');
        if (heading) heading.focus();
    }

    function transitionToSae() {
        // Ensure question set matches current role
        if (state.role === 'uxr') {
            SAE_QUESTIONS = SAE_QUESTIONS_UXR;
        } else {
            SAE_QUESTIONS = SAE_QUESTIONS_DESIGN;
        }
        totalSaeQuestions = SAE_QUESTIONS.length;

        state.stage = 'sae';
        state.currentQuestion = -1; // -1 = intro screen
        saveState();
        document.getElementById('intakeStage').style.display = 'none';
        document.getElementById('saeStage').style.display = '';
        showSaeIntro();
    }

    // ---- Event Handlers ----

    document.getElementById('saePrev').addEventListener('click', () => {
        if (state.currentQuestion > 0) {
            state.currentQuestion--;
            saveState();
            renderSaeQuestion(state.currentQuestion);
        } else if (state.currentQuestion === 0) {
            // Back to intro
            state.currentQuestion = -1;
            saveState();
            showSaeIntro();
        } else {
            // Back to intake from intro
            state.stage = 'intake';
            state.currentQuestion = 0;
            saveState();
            document.getElementById('saeStage').style.display = 'none';
            document.getElementById('intakeStage').style.display = '';
            initIntake();
        }
    });

    document.getElementById('saeNext').addEventListener('click', () => {
        if (state.currentQuestion === -1) {
            // Advance from intro to Q1
            state.currentQuestion = 0;
            saveState();
            renderSaeQuestion(0);
        } else if (state.currentQuestion < totalSaeQuestions - 1) {
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
            state.stage = 'transition';
            saveState();
            document.getElementById('epiasStage').style.display = 'none';
            showTransitionStage(state.saeLevel);
        }
    });

    document.getElementById('transitionBack').addEventListener('click', () => {
        state.stage = 'sae';
        state.currentQuestion = totalSaeQuestions - 1;
        saveState();
        document.getElementById('transitionStage').style.display = 'none';
        document.getElementById('saeStage').style.display = '';
        renderSaeQuestion(state.currentQuestion);
    });

    document.getElementById('transitionContinue').addEventListener('click', () => {
        state.stage = 'epias';
        state.currentQuestion = 0;
        saveState();
        document.getElementById('transitionStage').style.display = 'none';
        document.getElementById('epiasStage').style.display = '';
        renderEpiasQuestion(0);
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

    // All stages start hidden (no FOUC). Show exactly one.
    const hasResults = sessionStorage.getItem('ditResult');
    if (hasResults) {
        document.getElementById('completedStage').style.display = 'block';
    } else if (restoreState()) {
        if (state.stage === 'epias' && state.epiasQuestions.length > 0) {
            document.getElementById('epiasStage').style.display = '';
            renderEpiasQuestion(state.currentQuestion);
        } else if (state.stage === 'transition' && state.epiasQuestions.length > 0) {
            showTransitionStage(state.saeLevel);
        } else if (state.stage === 'sae') {
            document.getElementById('saeStage').style.display = '';
            if (state.currentQuestion === -1) {
                showSaeIntro();
            } else {
                renderSaeQuestion(state.currentQuestion);
            }
        } else {
            document.getElementById('intakeStage').style.display = '';
            initIntake();
        }
    } else {
        document.getElementById('intakeStage').style.display = '';
        initIntake();
    }

})();
