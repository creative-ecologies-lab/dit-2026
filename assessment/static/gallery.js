/**
 * Tree Gallery — 3 forms, arrows to navigate, wind interaction.
 */
(function() {
    'use strict';

    var container = document.getElementById('xpTreeContainer');
    var codeEl = document.getElementById('xpCode');
    var descEl = document.getElementById('xpDesc');
    var windSlider = document.getElementById('xpWind');
    var windValue = document.getElementById('xpWindValue');
    var prevBtn = document.getElementById('xpPrev');
    var nextBtn = document.getElementById('xpNext');
    var windLabels = [
        'calm','light air','light breeze','gentle breeze','moderate breeze',
        'fresh breeze','strong breeze','near gale','gale','strong gale',
        'storm','severe storm','hurricane','cat 2','cat 3','cat 4','cat 5'
    ];
    var rollBtn = document.getElementById('xpRollDice');
    var diceResult = document.getElementById('xpDiceResult');
    var chanceInfo = document.getElementById('xpChanceInfo');
    var chancePopup = document.getElementById('xpChancePopup');

    var currentIdx = 0;
    var currentStep = STEPS[0];
    var state = 'calm';
    var animId = null;
    var breakTime = 0;
    var CX = 250, GY_PIVOT = 285;
    var currentRoll = 5; // default dice roll (neutral)

    function loadStep(idx) {
        currentIdx = idx;
        currentStep = STEPS[idx];
        windSlider.value = 0;
        windValue.textContent = 'calm';
        windValue.style.color = '';
        state = 'calm';
        if (animId) { cancelAnimationFrame(animId); animId = null; }

        container.innerHTML = TreeViz.generateTreeSVG(currentStep.viz, currentStep.meta);
        document.querySelector('.xp-below-tree').classList.add('loaded');
        codeEl.textContent = currentStep.code;
        descEl.textContent = currentStep.desc;

        prevBtn.style.visibility = idx === 0 ? 'hidden' : '';
        nextBtn.style.visibility = idx === STEPS.length - 1 ? 'hidden' : '';
    }

    prevBtn.addEventListener('click', function() { if (currentIdx > 0) loadStep(currentIdx - 1); });
    nextBtn.addEventListener('click', function() { if (currentIdx < STEPS.length - 1) loadStep(currentIdx + 1); });
    document.addEventListener('keydown', function(e) {
        if (e.key === 'ArrowRight' && currentIdx < STEPS.length - 1) loadStep(currentIdx + 1);
        if (e.key === 'ArrowLeft' && currentIdx > 0) loadStep(currentIdx - 1);
    });

    // Wind engine
    function getEls() {
        var svg = container.querySelector('svg');
        if (!svg) return null;
        if (!svg.querySelector('#windWarp')) {
            var defs = svg.querySelector('defs');
            if (!defs) { defs = document.createElementNS('http://www.w3.org/2000/svg','defs'); svg.prepend(defs); }
            defs.insertAdjacentHTML('beforeend',
                '<filter id="windWarp" x="-20%" y="-10%" width="140%" height="120%">' +
                '<feTurbulence id="wTurb" type="fractalNoise" baseFrequency="0.005 0.003" numOctaves="3" seed="1" result="noise"/>' +
                '<feDisplacementMap id="wDisp" in="SourceGraphic" in2="noise" scale="0" xChannelSelector="R" yChannelSelector="G"/>' +
                '</filter>');
        }
        return {
            svg: svg, whole: svg.querySelector('.tree-whole'),
            canopy: svg.querySelector('.tree-canopy'),
            leaves: svg.querySelector('.tree-leaves'), roots: svg.querySelector('.tree-roots'),
            turb: svg.querySelector('#wTurb'), disp: svg.querySelector('#wDisp'),
        };
    }

    function tick(ts) {
        var el = getEls();
        if (!el || !el.canopy) { animId = null; return; }
        var t = ts * 0.001;
        var f = parseInt(windSlider.value) / 100;

        var whole = el.whole || el.canopy;

        if (state === 'calm') {
            whole.removeAttribute('transform');
            if (el.canopy) el.canopy.removeAttribute('filter');
            if (el.leaves) { el.leaves.removeAttribute('filter'); el.leaves.style.opacity = ''; }
            animId = null; return;
        }
        if (state === 'swaying') {
            // Displacement filter on canopy only (roots are underground)
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
            var phase = Math.min(breakTime / 1.5, 1);
            // Tree blows away — lifts off ground, tumbles, flies off to the right
            var shiftX = Math.pow(phase, 1.5) * 600; // flies off screen
            var liftY = -Math.sin(phase * Math.PI) * 80; // arcs up then down
            var tumble = phase * 360; // full rotation tumble
            var scale = 1 - phase * 0.6; // shrinks as it flies away
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
            // Gone. Off screen.
            whole.setAttribute('transform', 'translate(800 -200) scale(0.1)');
            if (el.canopy) el.canopy.removeAttribute('filter');
            animId = null; return;
        }
        animId = requestAnimationFrame(tick);
    }

    function getEffectiveBreakAt() {
        // Apply dice roll to breakAt like the forest does
        var ratio = currentStep.ratio || 0;
        var effective = ratio * (currentRoll / 5);
        if (effective > 2.0) return 0.20;
        if (effective <= 0.6) return 99;
        return 0.20 + (2.0 - effective) / (2.0 - 0.6) * 0.80;
    }

    windSlider.addEventListener('input', function() {
        var f = parseInt(this.value) / 100;
        var effectiveBreakAt = getEffectiveBreakAt();
        if (f <= 0) { state = 'calm'; breakTime = 0; if (animId) { cancelAnimationFrame(animId); animId = null; } tick(0); return; }
        if (f >= effectiveBreakAt && state === 'swaying') { state = 'breaking'; breakTime = 0; }
        else if (state !== 'breaking' && state !== 'fallen') { state = 'swaying'; }
        if (!animId) animId = requestAnimationFrame(tick);
        var li = Math.min(windLabels.length - 1, Math.floor(f * windLabels.length * 0.99));
        windValue.textContent = windLabels[li];
        windValue.style.color = (state === 'breaking' || state === 'fallen') ? '#f87171' : f > 0.7 ? '#fbbf24' : '';
    });

    // Dice roll
    if (rollBtn) {
        rollBtn.addEventListener('click', function() {
            currentRoll = Math.floor(Math.random() * 9) + 1;
            var effectiveBreakAt = getEffectiveBreakAt();
            var status = effectiveBreakAt >= 99 ? 'safe' : 'at risk';
            diceResult.textContent = status;
            diceResult.style.color = status === 'safe' ? '#4ade80' : '#f87171';
            // Reset fallen state so wind can re-test
            if (state === 'fallen' || state === 'breaking') {
                state = 'calm';
                breakTime = 0;
                windSlider.value = 0;
                windValue.textContent = 'calm';
                windValue.style.color = '';
                tick(0);
            }
        });
    }

    // Info popup toggle
    if (chanceInfo && chancePopup) {
        chanceInfo.addEventListener('click', function(e) {
            e.stopPropagation();
            chancePopup.classList.toggle('show');
        });
        document.addEventListener('click', function() { chancePopup.classList.remove('show'); });
    }

    loadStep(0);
})();
