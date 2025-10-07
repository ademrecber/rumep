// Font Preloader - Ensure fonts are loaded before use
document.addEventListener('DOMContentLoaded', function() {
    // Preload custom fonts
    const fonts = [
        new FontFace('RumepLogosSVG', 'url(/static/fonts/RumepLogosSVG.woff2)'),
        new FontFace('RumepLogosSVG', 'url(/static/fonts/RumepLogosSVG.ttf)'),
        new FontFace('RumepLogosCOLR', 'url(/static/fonts/RumepLogosCOLR.ttf)')
    ];
    
    // Load fonts
    fonts.forEach(font => {
        font.load().then(loadedFont => {
            document.fonts.add(loadedFont);
            console.log(`Font loaded: ${loadedFont.family}`);
        }).catch(error => {
            console.warn(`Font loading failed: ${font.family}`, error);
        });
    });
    
    // Check if fonts are ready
    document.fonts.ready.then(() => {
        console.log('All fonts loaded');
        
        // Apply fonts to elements that need them
        applyFontsToElements();
    });
    
    function applyFontsToElements() {
        // Apply fonts to textareas with data-font-family
        document.querySelectorAll('textarea[data-font-family]').forEach(textarea => {
            const fontFamily = textarea.getAttribute('data-font-family');
            textarea.style.fontFamily = fontFamily;
        });
        
        // Apply fonts to entry content
        document.querySelectorAll('.entry-content[data-font-family]').forEach(element => {
            const fontFamily = element.getAttribute('data-font-family');
            element.style.fontFamily = fontFamily;
        });
        
        // Apply fonts to preview content
        document.querySelectorAll('.first-entry-preview[data-font-family]').forEach(element => {
            const fontFamily = element.getAttribute('data-font-family');
            element.style.fontFamily = fontFamily;
        });
    }
    
    // Font fallback check
    setTimeout(() => {
        checkFontFallback();
    }, 2000);
    
    function checkFontFallback() {
        const testElement = document.createElement('span');
        testElement.style.fontFamily = 'RumepLogosSVG';
        testElement.style.fontSize = '20px';
        testElement.textContent = String.fromCharCode(0xE000);
        testElement.style.position = 'absolute';
        testElement.style.visibility = 'hidden';
        
        document.body.appendChild(testElement);
        
        // Check if font is actually loaded
        const computedStyle = window.getComputedStyle(testElement);
        const actualFont = computedStyle.fontFamily;
        
        if (!actualFont.includes('RumepLogosSVG')) {
            console.warn('Custom fonts not loaded properly, using fallback');
            showFontWarning();
        }
        
        document.body.removeChild(testElement);
    }
    
    function showFontWarning() {
        const warning = document.createElement('div');
        warning.className = 'alert alert-warning position-fixed';
        warning.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 300px;';
        warning.innerHTML = `
            <strong>${gettext('Font Uyarısı:')}</strong><br>
            ${gettext('Özel fontlar yüklenemedi. Karakterler düzgün görünmeyebilir.')}
            <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
        `;
        
        document.body.appendChild(warning);
        
        setTimeout(() => {
            if (warning.parentNode) {
                warning.remove();
            }
        }, 5000);
    }
});