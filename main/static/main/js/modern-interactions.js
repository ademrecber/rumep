// Modern 2025 Interactions
class ModernInteractions {
    constructor() {
        this.init();
    }

    init() {
        this.setupIntersectionObserver();
        this.setupSmoothScrolling();
        this.setupModernHovers();
        this.setupLoadingStates();
        this.setupFormEnhancements();
    }

    // Intersection Observer for animations
    setupIntersectionObserver() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });

        // Observe fade-in elements
        document.querySelectorAll('.fade-in').forEach(el => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(20px)';
            el.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
            observer.observe(el);
        });
    }

    // Smooth scrolling for internal links
    setupSmoothScrolling() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    // Modern hover effects
    setupModernHovers() {
        // Card hover effects
        document.querySelectorAll('.card').forEach(card => {
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-4px)';
            });
            
            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0)';
            });
        });

        // Button ripple effect
        document.querySelectorAll('.btn').forEach(button => {
            button.addEventListener('click', function(e) {
                const ripple = document.createElement('span');
                const rect = this.getBoundingClientRect();
                const size = Math.max(rect.width, rect.height);
                const x = e.clientX - rect.left - size / 2;
                const y = e.clientY - rect.top - size / 2;
                
                ripple.style.width = ripple.style.height = size + 'px';
                ripple.style.left = x + 'px';
                ripple.style.top = y + 'px';
                ripple.classList.add('ripple');
                
                this.appendChild(ripple);
                
                setTimeout(() => {
                    ripple.remove();
                }, 600);
            });
        });
    }

    // Loading states for forms and buttons
    setupLoadingStates() {
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', function() {
                const submitBtn = this.querySelector('button[type="submit"]');
                if (submitBtn) {
                    const originalText = submitBtn.innerHTML;
                    submitBtn.innerHTML = '<i class="bi bi-arrow-clockwise spin"></i> Tê şandin...';
                    submitBtn.disabled = true;
                    
                    // Reset after 3 seconds if no redirect
                    setTimeout(() => {
                        if (submitBtn) {
                            submitBtn.innerHTML = originalText;
                            submitBtn.disabled = false;
                        }
                    }, 3000);
                }
            });
        });
    }

    // Form enhancements
    setupFormEnhancements() {
        // Auto-resize textareas
        document.querySelectorAll('textarea').forEach(textarea => {
            textarea.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = this.scrollHeight + 'px';
            });
        });

        // Floating labels
        document.querySelectorAll('.form-control').forEach(input => {
            const label = input.previousElementSibling;
            if (label && label.tagName === 'LABEL') {
                input.addEventListener('focus', () => {
                    label.style.transform = 'translateY(-20px) scale(0.8)';
                    label.style.color = 'var(--primary-600)';
                });
                
                input.addEventListener('blur', () => {
                    if (!input.value) {
                        label.style.transform = 'translateY(0) scale(1)';
                        label.style.color = 'var(--gray-500)';
                    }
                });
            }
        });
    }

    // Utility method to add loading skeleton
    static addLoadingSkeleton(container) {
        const skeleton = document.createElement('div');
        skeleton.className = 'loading-skeleton';
        skeleton.style.height = '100px';
        skeleton.style.borderRadius = 'var(--radius-lg)';
        skeleton.style.marginBottom = 'var(--space-4)';
        container.appendChild(skeleton);
        return skeleton;
    }

    // Utility method to remove loading skeleton
    static removeLoadingSkeleton(skeleton) {
        if (skeleton && skeleton.parentNode) {
            skeleton.parentNode.removeChild(skeleton);
        }
    }
}

// CSS for ripple effect and spin animation
const modernStyles = `
.ripple {
    position: absolute;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.6);
    transform: scale(0);
    animation: ripple-animation 0.6s linear;
    pointer-events: none;
}

@keyframes ripple-animation {
    to {
        transform: scale(4);
        opacity: 0;
    }
}

.spin {
    animation: spin 1s linear infinite;
}

@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

.btn {
    position: relative;
    overflow: hidden;
}
`;

// Inject styles
const styleSheet = document.createElement('style');
styleSheet.textContent = modernStyles;
document.head.appendChild(styleSheet);

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ModernInteractions();
});

// Export for use in other modules
export { ModernInteractions };