/* ============================================
   js/section-loader.js — Venkatesh Babu Portfolio
   Dynamic HTML section loader using IntersectionObserver
============================================ */

(function () {
    'use strict';

    // Store loaded status to prevent duplicate fetches
    const loadedSections = new Set();

    /**
     * Post-load initializers for section-specific interactive logic
     */
    function triggerSectionHooks(sectionId) {
        // Refresh scroll reveal observer for newly injected DOM nodes
        if (typeof window.initScrollAnimations === 'function') {
            window.initScrollAnimations();
        }

        switch (sectionId) {
            case 'about':
                if (typeof window.initStatsCounter === 'function') {
                    window.initStatsCounter();
                }
                break;

            case 'skills':
                if (typeof window.renderRadarChart === 'function') {
                    window.renderRadarChart();
                }
                break;

            case 'projects':
                if (typeof window.renderProjects === 'function') {
                    window.renderProjects('all');
                }
                break;

            case 'footer':
                var yrEl = document.getElementById('current-year');
                if (yrEl) {
                    yrEl.innerText = new Date().getFullYear();
                }
                break;
        }
    }

    /**
     * Fetch and inject HTML section partial
     */
    async function loadSection(element) {
        const src = element.getAttribute('data-src');
        const sectionId = element.id;

        if (!src || loadedSections.has(sectionId)) return;

        try {
            const response = await fetch(src);
            if (!response.ok) throw new Error(`HTTP ${response.status} loading ${src}`);
            const html = await response.text();

            // Inject section HTML
            element.innerHTML = html;
            element.classList.remove('lazy-section-placeholder');
            element.removeAttribute('data-src');
            loadedSections.add(sectionId);

            // Execute hooks for newly loaded section
            triggerSectionHooks(sectionId);
        } catch (error) {
            console.error(`Failed to load section [${sectionId}]:`, error);
        }
    }

    /**
     * Intersection Observer for scroll-triggered section loading
     */
    function initSectionObserver() {
        const placeholders = document.querySelectorAll('[data-src]');
        if (!placeholders.length) return;

        // Fallback for browsers without IntersectionObserver
        if (!('IntersectionObserver' in window)) {
            placeholders.forEach(el => loadSection(el));
            return;
        }

        const observer = new IntersectionObserver((entries, obs) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    loadSection(entry.target);
                    obs.unobserve(entry.target);
                }
            });
        }, {
            rootMargin: '300px 0px 300px 0px', // Preload 300px before reaching viewport
            threshold: 0.01
        });

        placeholders.forEach(el => observer.observe(el));
    }

    // Initialize when DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initSectionObserver);
    } else {
        initSectionObserver();
    }
})();
