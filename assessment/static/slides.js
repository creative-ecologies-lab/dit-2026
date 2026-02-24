/**
 * DIT 2026 — Lightweight slide system.
 * Makes any container with [data-slideshow] paginate its .slide children.
 *
 * Modes:
 *   data-slideshow        — expects explicit .slide children
 *   data-slideshow="auto" — splits content at <h2> boundaries into slides
 */
(function () {
    'use strict';

    function initSlideshow(container) {
        if (container.dataset.slideshow === 'scroll') {
            initScrollFrame(container);
            return;
        }
        if (container.dataset.slideshow === 'auto') autoSplit(container);

        var slides = container.querySelectorAll(':scope > .slide');
        if (!slides.length) return;

        // Single slide — show it, no nav needed
        if (slides.length === 1) {
            slides[0].classList.add('active');
            return;
        }

        var current = 0;

        // --- Build navigation ---
        var nav = document.createElement('div');
        nav.className = 'slide-nav';
        nav.setAttribute('role', 'navigation');
        nav.setAttribute('aria-label', 'Page navigation');

        var prevBtn = document.createElement('button');
        prevBtn.className = 'slide-btn slide-prev';
        prevBtn.setAttribute('aria-label', 'Previous page');
        prevBtn.textContent = '\u2190';

        var nextBtn = document.createElement('button');
        nextBtn.className = 'slide-btn slide-next';
        nextBtn.setAttribute('aria-label', 'Next page');
        nextBtn.textContent = '\u2192';

        var dots = document.createElement('div');
        dots.className = 'slide-dots';
        dots.setAttribute('role', 'tablist');
        dots.setAttribute('aria-label', 'Slide selection');
        for (var i = 0; i < slides.length; i++) {
            var dot = document.createElement('button');
            dot.className = 'slide-dot' + (i === 0 ? ' active' : '');
            dot.setAttribute('role', 'tab');
            dot.setAttribute('aria-label', 'Page ' + (i + 1) + ' of ' + slides.length);
            dot.setAttribute('aria-selected', i === 0 ? 'true' : 'false');
            dot.dataset.idx = i;
            dots.appendChild(dot);
        }

        var count = document.createElement('span');
        count.className = 'slide-count';
        count.setAttribute('role', 'status');
        count.setAttribute('aria-live', 'polite');
        count.setAttribute('aria-label', 'Current page');
        count.textContent = '1 / ' + slides.length;

        nav.appendChild(prevBtn);
        nav.appendChild(dots);
        nav.appendChild(count);
        nav.appendChild(nextBtn);
        container.appendChild(nav);

        // --- Navigation logic ---
        function goTo(idx) {
            if (idx < 0 || idx >= slides.length) return;
            slides[current].classList.remove('active');
            slides[current].setAttribute('aria-hidden', 'true');
            dots.children[current].classList.remove('active');
            dots.children[current].setAttribute('aria-selected', 'false');
            slides[idx].classList.add('active');
            slides[idx].setAttribute('aria-hidden', 'false');
            dots.children[idx].classList.add('active');
            dots.children[idx].setAttribute('aria-selected', 'true');
            count.textContent = (idx + 1) + ' / ' + slides.length;
            current = idx;
        }

        // Set initial ARIA state on slides
        for (var j = 0; j < slides.length; j++) {
            slides[j].setAttribute('role', 'tabpanel');
            slides[j].setAttribute('aria-label', 'Page ' + (j + 1) + ' of ' + slides.length);
            slides[j].setAttribute('aria-hidden', j === 0 ? 'false' : 'true');
        }
        slides[0].classList.add('active');

        prevBtn.addEventListener('click', function () { goTo(current - 1); });
        nextBtn.addEventListener('click', function () { goTo(current + 1); });
        dots.addEventListener('click', function (e) {
            if (e.target.classList.contains('slide-dot')) {
                goTo(parseInt(e.target.dataset.idx));
            }
        });

        // Keyboard (only when this container is visible)
        document.addEventListener('keydown', function (e) {
            if (container.offsetParent === null) return;
            var tag = (document.activeElement || {}).tagName;
            if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return;
            if (e.key === 'ArrowRight') { e.preventDefault(); goTo(current + 1); }
            if (e.key === 'ArrowLeft') { e.preventDefault(); goTo(current - 1); }
        });
    }

    /**
     * Split content at <h2> boundaries into .slide containers.
     * Each h2 starts a new slide; content before the first h2 becomes slide 1.
     */
    function autoSplit(container) {
        var children = Array.from(container.children);
        if (!children.length) return;

        var groups = [];
        var currentGroup = [];

        children.forEach(function (child) {
            if (child.tagName === 'H2' && currentGroup.length > 0) {
                groups.push(currentGroup);
                currentGroup = [];
            }
            currentGroup.push(child);
        });
        if (currentGroup.length > 0) groups.push(currentGroup);

        // Rebuild with .slide wrappers
        while (container.firstChild) container.removeChild(container.firstChild);
        groups.forEach(function (group) {
            var slide = document.createElement('div');
            slide.className = 'slide';
            group.forEach(function (el) { slide.appendChild(el); });
            container.appendChild(slide);
        });
    }

    /**
     * Scroll-frame mode: content flows in a two-column grid.
     * Advance button smooth-scrolls by one viewport frame.
     * No manual scrolling — wheel and touch are captured.
     */
    function initScrollFrame(container) {
        // Wrap all content in a grid body
        var body = document.createElement('div');
        body.className = 'scroll-frame-body';
        body.setAttribute('role', 'document');
        body.setAttribute('aria-label', 'Framework content');
        while (container.firstChild) body.appendChild(container.firstChild);
        container.appendChild(body);

        // Build navigation (sticky at bottom of scroll container)
        var nav = document.createElement('div');
        nav.className = 'scroll-frame-nav';
        nav.setAttribute('role', 'navigation');
        nav.setAttribute('aria-label', 'Frame navigation');

        var prevBtn = document.createElement('button');
        prevBtn.className = 'slide-btn';
        prevBtn.textContent = '\u2190';
        prevBtn.setAttribute('aria-label', 'Previous frame');

        var nextBtn = document.createElement('button');
        nextBtn.className = 'slide-btn';
        nextBtn.textContent = '\u2192';
        nextBtn.setAttribute('aria-label', 'Next frame');

        var track = document.createElement('div');
        track.className = 'scroll-frame-track';
        var fill = document.createElement('div');
        fill.className = 'scroll-frame-fill';
        track.appendChild(fill);

        var counter = document.createElement('span');
        counter.className = 'slide-count';
        counter.setAttribute('role', 'status');
        counter.setAttribute('aria-live', 'polite');
        counter.setAttribute('aria-label', 'Current frame');

        nav.appendChild(prevBtn);
        nav.appendChild(track);
        nav.appendChild(counter);
        nav.appendChild(nextBtn);
        container.appendChild(nav);

        // State
        var idx = 0;

        function frameH() {
            return container.clientHeight - nav.offsetHeight;
        }

        function maxFrame() {
            var scrollable = container.scrollHeight - container.clientHeight;
            return scrollable <= 0 ? 0 : Math.ceil(scrollable / frameH());
        }

        function goTo(i) {
            var m = maxFrame();
            i = Math.max(0, Math.min(i, m));
            idx = i;
            container.scrollTo({ top: i * frameH(), behavior: 'smooth' });
            update();
        }

        function update() {
            var m = maxFrame();
            counter.textContent = (idx + 1) + ' / ' + (m + 1);
            fill.style.width = m > 0 ? (idx / m * 100) + '%' : '100%';
            prevBtn.disabled = idx <= 0;
            nextBtn.disabled = idx >= m;
            prevBtn.setAttribute('aria-disabled', idx <= 0 ? 'true' : 'false');
            nextBtn.setAttribute('aria-disabled', idx >= m ? 'true' : 'false');
        }

        prevBtn.addEventListener('click', function () { goTo(idx - 1); });
        nextBtn.addEventListener('click', function () { goTo(idx + 1); });

        // Debounced wheel → frame advance
        var wheelLock = false;
        container.addEventListener('wheel', function (e) {
            e.preventDefault();
            if (wheelLock) return;
            wheelLock = true;
            setTimeout(function () { wheelLock = false; }, 400);
            goTo(idx + (e.deltaY > 0 ? 1 : -1));
        }, { passive: false });

        // Touch swipe
        var touchY = 0;
        container.addEventListener('touchstart', function (e) {
            touchY = e.touches[0].clientY;
        }, { passive: true });
        container.addEventListener('touchmove', function (e) {
            e.preventDefault();
        }, { passive: false });
        container.addEventListener('touchend', function (e) {
            var dy = touchY - e.changedTouches[0].clientY;
            if (Math.abs(dy) > 40) goTo(idx + (dy > 0 ? 1 : -1));
        });

        // Keyboard
        document.addEventListener('keydown', function (e) {
            if (container.offsetParent === null) return;
            var tag = (document.activeElement || {}).tagName;
            if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return;
            var handled = true;
            switch (e.key) {
                case 'ArrowRight': case 'ArrowDown': case ' ': case 'PageDown':
                    goTo(idx + 1); break;
                case 'ArrowLeft': case 'ArrowUp': case 'PageUp':
                    goTo(idx - 1); break;
                case 'Home': goTo(0); break;
                case 'End': goTo(maxFrame()); break;
                default: handled = false;
            }
            if (handled) e.preventDefault();
        });

        // Sync idx from scroll position after smooth animation settles
        var scrollTimer;
        container.addEventListener('scroll', function () {
            clearTimeout(scrollTimer);
            scrollTimer = setTimeout(function () {
                var fh = frameH();
                if (fh > 0) {
                    idx = Math.round(container.scrollTop / fh);
                    update();
                }
            }, 150);
        });

        update();
    }

    // --- Init ---
    function init() {
        var containers = document.querySelectorAll('[data-slideshow]');
        for (var i = 0; i < containers.length; i++) {
            initSlideshow(containers[i]);
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Expose for late-init (results page shows container after JS runs)
    window.initSlideshow = initSlideshow;
})();
