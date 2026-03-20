/**
 * Forest wind + dice animation.
 *
 * Each tree has a data-ratio (canopy/roots). The user clicks "Roll"
 * to roll two dice (1-9 each) per tree. The product of the dice
 * determines circumstance. effective = ratio × (die1 + die2) / 10.
 * If effective > 2.0, the tree is vulnerable at some wind level.
 *
 * Wind slider then reveals which trees fall at each level.
 * Trees must be rolled before wind has any effect beyond swaying.
 */

(function() {
    'use strict';

    var windSlider = document.getElementById('forestWind');
    var windValue = document.getElementById('forestWindValue');
    var rollBtn = document.getElementById('rollDice');
    var diceResult = document.getElementById('diceResult');
    if (!windSlider || !rollBtn) return;

    var windLabels = [
        'calm', 'light air', 'light breeze', 'gentle breeze',
        'moderate breeze', 'fresh breeze', 'strong breeze', 'near gale',
        'gale', 'strong gale', 'storm', 'severe storm',
        'hurricane cat 1', 'hurricane cat 2', 'hurricane cat 3',
        'hurricane cat 4', 'hurricane cat 5',
    ];

    var trees = [];
    var targetWind = 0;
    var smoothWind = 0;
    var rolled = false;
    var calmSince = 0;

    function bindTrees() {
        var active = document.querySelector('.forest-view.active');
        if (!active) return;
        var els = active.querySelectorAll('.forest-tree-g');
        trees = [];
        els.forEach(function(el, idx) {
            trees.push({
                el: el,
                ratio: parseFloat(el.getAttribute('data-ratio')) || 0,
                x: parseFloat(el.getAttribute('data-x')) || 0,
                y: parseFloat(el.getAttribute('data-y')) || 0,
                isEmpty: el.hasAttribute('data-empty'),
                phase: idx * 1.7,
                die1: 0,
                die2: 0,
                breakAt: 99,
                // Animation state
                fallen: false,
                falling: false,
                fallT: 0,
                queued: false,
                fadeStart: null,
            });
        });
        smoothWind = 0;
        targetWind = 0;
        rolled = false;
        calmSince = 0;
        // Only clear dice result on view toggle, not initial load

    }

    bindTrees();
    doRoll();
    rolled = true;

    document.querySelectorAll('.forest-toggle-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            setTimeout(function() {
                bindTrees();
                doRoll();
                rolled = true;
                windSlider.value = 0;
            }, 20);
        });
    });

    // ── Night overlay ──
    var nightEl = document.getElementById('nightOverlay');
    var starsEl = document.getElementById('starsOverlay');
    var rolling = false;

    var lastVulnerable = 0;

    function doRoll() {
        lastVulnerable = 0;
        trees.forEach(function(t) {
            t.fallen = false;
            t.falling = false;
            t.fallT = 0;
            t.queued = false;
            t.fadeStart = null;
            var showAll = document.getElementById('showAllTrees');
            var hidden = t.isEmpty && showAll && !showAll.checked;
            t.el.style.display = hidden ? 'none' : '';
            t.el.style.opacity = '';
            t.el.setAttribute('transform', '');

            if (t.ratio <= 0) {
                t.die1 = 0; t.die2 = 0; t.breakAt = 99;
                return;
            }

            t.die1 = Math.floor(Math.random() * 9) + 1;
            t.die2 = Math.floor(Math.random() * 9) + 1;
            var circumstance = (t.die1 + t.die2) / 10;
            var effective = t.ratio * circumstance;

            if (effective <= 2.0) {
                t.breakAt = 99;
            } else {
                var s = Math.min(1.0, (effective - 2.0) / 5.0);
                t.breakAt = 0.98 - s * s * 0.60;
                if (!t.isEmpty) lastVulnerable++;
            }
        });

        rolled = true;
        fallQueue = [];
        nextFallTime = 0;

        windSlider.value = 0;
        targetWind = 0;
        smoothWind = 0;
        calmSince = 0;
    }

    // ── Roll button: gentle dim → roll → brighten ──
    rollBtn.addEventListener('click', function() {
        if (rolling) return;
        rolling = true;
        rollBtn.disabled = true;

        diceResult.textContent = '\u00a0';

        starsEl.style.transition = 'opacity 1.5s';
        starsEl.style.opacity = '0.3';

        setTimeout(function() {
            nightEl.style.transition = 'opacity 1.2s';
            nightEl.style.opacity = '0.35';
            starsEl.style.transition = 'opacity 1s';
            starsEl.style.opacity = '1';
        }, 400);

        setTimeout(function() { doRoll(); }, 1500);

        setTimeout(function() {
            nightEl.style.transition = 'opacity 1.2s';
            nightEl.style.opacity = '0';
        }, 1900);

        setTimeout(function() {
            starsEl.style.transition = 'opacity 1s';
            starsEl.style.opacity = '0';
        }, 2200);

        setTimeout(function() {
            diceResult.textContent = lastVulnerable > 0
                ? lastVulnerable + ' at risk'
                : 'all safe';
        }, 2400);

        setTimeout(function() {
            rolling = false;
            rollBtn.disabled = false;
        }, 3200);
    });

    // ── Wind slider ──
    windSlider.addEventListener('input', function() {
        targetWind = parseInt(this.value) / 100;
    });

    // ── Fall queue ──
    var fallQueue = [];
    var nextFallTime = 0;

    function tick() {
        smoothWind += (targetWind - smoothWind) * 0.03;
        if (Math.abs(smoothWind - targetWind) < 0.001) smoothWind = targetWind;

        var f = smoothWind;
        var now = Date.now() * 0.001;

        var li = Math.min(16, Math.floor(targetWind * 16.99));
        windValue.textContent = windLabels[li];

        // Calm reset
        if (f < 0.005) {
            if (!calmSince) calmSince = now;
        } else {
            calmSince = 0;
        }

        if (calmSince && (now - calmSince) > 2) {
            var showAll2 = document.getElementById('showAllTrees');
            trees.forEach(function(t) {
                t.fallen = false;
                t.falling = false;
                t.fallT = 0;
                t.queued = false;
                t.fadeStart = null;
                var hidden2 = t.isEmpty && showAll2 && !showAll2.checked;
                t.el.style.display = hidden2 ? 'none' : '';
                t.el.setAttribute('transform', '');
                t.el.style.opacity = '';
            });
            fallQueue = [];
            nextFallTime = 0;
            calmSince = now;
        }

        // Queue newly eligible trees
        if (rolled) {
            trees.forEach(function(t) {
                if (!t.queued && !t.fallen && !t.falling && t.breakAt < 99 && f >= t.breakAt) {
                    t.queued = true;
                    fallQueue.push(t);
                }
            });

            // Un-queue if wind dropped
            fallQueue = fallQueue.filter(function(t) {
                if (!t.falling && f < t.breakAt) {
                    t.queued = false;
                    return false;
                }
                return true;
            });
        }

        if (fallQueue.length > 0 && nextFallTime === 0) {
            nextFallTime = now + 0.1;
        }

        if (fallQueue.length > 0 && now >= nextFallTime) {
            var t = fallQueue.shift();
            t.falling = true;
            t.fallT = 0;
            nextFallTime = now + 0.15;
        }

        if (fallQueue.length === 0) {
            nextFallTime = 0;
        }

        // Render
        trees.forEach(function(t) {
            if (f < 0.005 && !t.falling && !t.fallen && !t.queued) {
                t.el.setAttribute('transform', '');
                t.el.style.opacity = '';
                return;
            }

            if (t.falling) {
                if (t.fallT < 1) {
                    t.fallT = Math.min(1, t.fallT + 0.008);
                } else {
                    t.fallen = true;
                    t.falling = false;
                    t.fadeStart = now;
                }
                var ease = 1 - (1 - t.fallT) * (1 - t.fallT);
                t.el.setAttribute('transform',
                    'rotate(' + (ease * 88).toFixed(1) + ' ' + t.x + ' ' + t.y + ')');
                t.el.style.opacity = (1 - ease * 0.7).toFixed(2);
            } else if (t.fallen) {
                var fadeElapsed = now - (t.fadeStart || now);
                var fadeT = Math.min(1, fadeElapsed / 2);
                if (fadeT >= 1) {
                    t.el.style.display = 'none';
                } else {
                    t.el.setAttribute('transform',
                        'rotate(88 ' + t.x + ' ' + t.y + ')');
                    t.el.style.opacity = (0.3 * (1 - fadeT)).toFixed(2);
                }
            } else {
                // Sway — L0 (ratio=0) translates side-to-side since they're flat
                var angle = Math.sin(now * 1.2 + t.phase) * f * 20
                          + Math.sin(now * 0.7 + t.phase * 0.6) * f * 8
                          + f * 5;
                if (t.ratio <= 0) {
                    var drift = Math.sin(now * 1.0 + t.phase) * f * 6
                              + Math.sin(now * 0.6 + t.phase * 0.7) * f * 3;
                    t.el.setAttribute('transform',
                        'translate(' + drift.toFixed(1) + ',0)');
                } else {
                    t.el.setAttribute('transform',
                        'rotate(' + angle.toFixed(1) + ' ' + t.x + ' ' + t.y + ')');
                }
                t.el.style.opacity = '';
            }
        });

        requestAnimationFrame(tick);
    }

    tick();
})();
