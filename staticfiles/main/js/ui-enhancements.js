// UI Enhancements for better user experience
document.addEventListener('DOMContentLoaded', () => {
    // Smooth scrolling for all internal links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId !== '#') {
                e.preventDefault();
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    window.scrollTo({
                        top: targetElement.offsetTop - 20,
                        behavior: 'smooth'
                    });
                }
            }
        });
    });
    
    // Enhance show more/less functionality
    const enhanceShowMoreButtons = () => {
        document.querySelectorAll('.show-more-btn').forEach(btn => {
            if (!btn.hasAttribute('data-enhanced')) {
                btn.setAttribute('data-enhanced', 'true');
                btn.addEventListener('click', function() {
                    const preview = this.previousElementSibling;
                    const fullText = this.nextElementSibling;
                    const showLessBtn = fullText.nextElementSibling;
                    
                    preview.classList.add('d-none');
                    this.classList.add('d-none');
                    fullText.classList.remove('d-none');
                    showLessBtn.classList.remove('d-none');
                });
            }
        });
        
        document.querySelectorAll('.show-less-btn').forEach(btn => {
            if (!btn.hasAttribute('data-enhanced')) {
                btn.setAttribute('data-enhanced', 'true');
                btn.addEventListener('click', function() {
                    const fullText = this.previousElementSibling;
                    const showMoreBtn = fullText.previousElementSibling;
                    const preview = showMoreBtn.previousElementSibling;
                    
                    this.classList.add('d-none');
                    fullText.classList.add('d-none');
                    showMoreBtn.classList.remove('d-none');
                    preview.classList.remove('d-none');
                });
            }
        });
    };
    
    // Call initially
    enhanceShowMoreButtons();
    
    // Enhance card animations
    const enhanceCardAnimations = () => {
        const cards = document.querySelectorAll('.tweet-card, .critique-item');
        cards.forEach((card, index) => {
            if (!card.hasAttribute('data-animated')) {
                card.setAttribute('data-animated', 'true');
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
                card.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                
                setTimeout(() => {
                    card.style.opacity = '1';
                    card.style.transform = 'translateY(0)';
                }, 50 * index); // Staggered animation
            }
        });
    };
    
    // Call initially
    enhanceCardAnimations();
    
    // Enhance form interactions
    const enhanceFormInteractions = () => {
        const textareas = document.querySelectorAll('textarea');
        textareas.forEach(textarea => {
            if (!textarea.hasAttribute('data-enhanced')) {
                textarea.setAttribute('data-enhanced', 'true');
                
                // Auto-resize
                textarea.addEventListener('input', function() {
                    this.style.height = 'auto';
                    this.style.height = `${this.scrollHeight}px`;
                });
                
                // Focus effect
                textarea.addEventListener('focus', function() {
                    this.closest('.form-group')?.classList.add('focused');
                });
                
                textarea.addEventListener('blur', function() {
                    this.closest('.form-group')?.classList.remove('focused');
                });
                
                // Initial height
                textarea.style.height = `${textarea.scrollHeight}px`;
            }
        });
    };
    
    // Call initially
    enhanceFormInteractions();
    
    // Enhance dropdown menus
    const enhanceDropdowns = () => {
        const dropdownMenus = document.querySelectorAll('.dropdown-menu');
        dropdownMenus.forEach(menu => {
            if (!menu.hasAttribute('data-enhanced')) {
                menu.setAttribute('data-enhanced', 'true');
                menu.style.opacity = '0';
                menu.style.transform = 'translateY(-10px)';
                menu.style.transition = 'opacity 0.2s ease, transform 0.2s ease';
                
                const dropdown = menu.closest('.dropdown');
                if (dropdown) {
                    const toggle = dropdown.querySelector('[data-bs-toggle="dropdown"]');
                    if (toggle) {
                        toggle.addEventListener('click', () => {
                            setTimeout(() => {
                                if (menu.classList.contains('show')) {
                                    menu.style.opacity = '1';
                                    menu.style.transform = 'translateY(0)';
                                }
                            }, 0);
                        });
                    }
                }
            }
        });
    };
    
    // Call initially
    enhanceDropdowns();
    
    // Observe DOM changes to enhance dynamically added elements
    const observer = new MutationObserver(() => {
        enhanceShowMoreButtons();
        enhanceCardAnimations();
        enhanceFormInteractions();
        enhanceDropdowns();
    });
    
    observer.observe(document.body, { 
        childList: true, 
        subtree: true 
    });
});