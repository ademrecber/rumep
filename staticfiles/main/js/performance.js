// Performance optimizations for the entire application

// Intersection Observer for lazy loading images
const lazyLoadImages = () => {
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                observer.unobserve(img);
            }
        });
    }, {
        rootMargin: '50px 0px',
        threshold: 0.1
    });

    document.querySelectorAll('img.lazy[data-src]').forEach(img => {
        imageObserver.observe(img);
    });
};

// Debounce utility for performance optimization
const debounce = (func, wait) => {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
};

// Throttle utility for performance optimization
const throttle = (func, limit) => {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
};

// Cache frequently accessed DOM elements
const domCache = new Map();
const getElement = (selector) => {
    if (!domCache.has(selector)) {
        domCache.set(selector, document.querySelector(selector));
    }
    return domCache.get(selector);
};

// Optimize scroll event handlers
const optimizeScrollHandlers = () => {
    const scrollHandlers = new Set();
    let ticking = false;

    const requestTick = () => {
        if (!ticking) {
            requestAnimationFrame(() => {
                scrollHandlers.forEach(handler => handler());
                ticking = false;
            });
        }
        ticking = true;
    };

    return {
        add: (handler) => {
            scrollHandlers.add(handler);
            if (scrollHandlers.size === 1) {
                window.addEventListener('scroll', requestTick, { passive: true });
            }
        },
        remove: (handler) => {
            scrollHandlers.delete(handler);
            if (scrollHandlers.size === 0) {
                window.removeEventListener('scroll', requestTick);
            }
        }
    };
};

// Resource hints for performance
const addResourceHints = () => {
    const hints = [
        { rel: 'dns-prefetch', href: 'https://cdn.jsdelivr.net' },
        { rel: 'dns-prefetch', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: true }
    ];

    const fragment = document.createDocumentFragment();
    hints.forEach(({ rel, href, crossorigin }) => {
        if (!document.querySelector(`link[rel="${rel}"][href="${href}"]`)) {
            const link = document.createElement('link');
            link.rel = rel;
            link.href = href;
            if (crossorigin) link.crossOrigin = 'anonymous';
            fragment.appendChild(link);
        }
    });
    document.head.appendChild(fragment);
};

// Initialize performance optimizations
const initPerformance = () => {
    // Add resource hints
    addResourceHints();

    // Initialize lazy loading
    if ('IntersectionObserver' in window) {
        lazyLoadImages();
    }

    // Initialize scroll optimization
    const scrollOptimizer = optimizeScrollHandlers();

    // Optimize third-party script loading
    const loadThirdPartyScripts = () => {
        // Load non-critical third-party scripts after page load
        const scripts = [
            { src: 'https://www.google-analytics.com/analytics.js', async: true },
            // Add other third-party scripts here
        ];

        scripts.forEach(({ src, async }) => {
            const script = document.createElement('script');
            script.src = src;
            if (async) script.async = true;
            document.body.appendChild(script);
        });
    };

    // Load third-party scripts after critical content
    if (document.readyState === 'complete') {
        loadThirdPartyScripts();
    } else {
        window.addEventListener('load', loadThirdPartyScripts);
    }

    // Export utilities for use in other modules
    window.perfUtils = {
        debounce,
        throttle,
        getElement,
        scrollOptimizer
    };
};

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPerformance);
} else {
    initPerformance();
}

// Export utilities for use in modules
export {
    debounce,
    throttle,
    getElement,
    optimizeScrollHandlers
};