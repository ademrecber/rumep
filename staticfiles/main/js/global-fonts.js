// Global Font System - Works on all pages automatically
document.addEventListener('DOMContentLoaded', function() {
    // Apply fonts to all elements with font-family style
    applyGlobalFonts();
    
    // Watch for dynamic content changes
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === 1) { // Element node
                        applyFontsToElement(node);
                    }
                });
            }
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    
    function applyGlobalFonts() {
        // Find all elements with font-family in style attribute
        const elementsWithFonts = document.querySelectorAll('[style*="font-family"]');
        
        elementsWithFonts.forEach(element => {
            applyFontsToElement(element);
        });
    }
    
    function applyFontsToElement(element) {
        const style = element.getAttribute('style');
        if (!style) return;
        
        // Check if element uses custom fonts
        if (style.includes('RumepLogosSVG') || style.includes('RumepLogosCOLR')) {
            // Ensure font is properly applied
            const computedStyle = window.getComputedStyle(element);
            const currentFont = computedStyle.fontFamily;
            
            // Force font application if needed
            if (!currentFont.includes('RumepLogos')) {
                element.style.fontFamily = style.match(/font-family:\s*([^;]+)/)?.[1] || '';
            }
        }
    }
    
    // Global font utility functions
    window.applyCustomFont = function(element, fontFamily) {
        if (element && fontFamily) {
            element.style.fontFamily = fontFamily;
            
            // Apply to all child elements that might need it
            const children = element.querySelectorAll('*');
            children.forEach(child => {
                if (!child.style.fontFamily) {
                    child.style.fontFamily = 'inherit';
                }
            });
        }
    };
    
    // Auto-detect and apply fonts from data attributes
    document.querySelectorAll('[data-font-family]').forEach(element => {
        const fontFamily = element.getAttribute('data-font-family');
        if (fontFamily) {
            element.style.fontFamily = fontFamily;
        }
    });
});