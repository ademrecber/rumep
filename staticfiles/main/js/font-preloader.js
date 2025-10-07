// Enhanced Font Preloader - Cross-platform support
document.addEventListener('DOMContentLoaded', function() {
    // Detect platform
    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
    const isAndroid = /Android/.test(navigator.userAgent);
    const isMobile = isIOS || isAndroid;
    
    // Add loading class to body
    document.body.classList.add('font-loading');
    
    // Platform-specific font loading
    const fonts = [];
    
    if (isMobile) {
        // Mobile: Only load TTF for better compatibility
        fonts.push(
            new FontFace('RumepLogosSVG', 'url(/static/fonts/RumepLogosSVG.ttf)', {
                unicodeRange: 'U+E000-E00F, U+F000-F0FF'
            })
        );
        
        // iOS specific handling
        if (isIOS) {
            console.log('iOS detected: Loading TTF only');
        }
    } else {
        // Desktop: Load both WOFF2 and COLR
        fonts.push(
            new FontFace('RumepLogosSVG', 'url(/static/fonts/RumepLogosSVG.woff2)', {
                unicodeRange: 'U+E000-E00F, U+F000-F0FF'
            }),
            new FontFace('RumepLogosSVG', 'url(/static/fonts/RumepLogosSVG.ttf)', {
                unicodeRange: 'U+E000-E00F, U+F000-F0FF'
            }),
            new FontFace('RumepLogosCOLR', 'url(/static/fonts/RumepLogosCOLR.ttf)', {
                unicodeRange: 'U+E000-E00F, U+F000-F0FF'
            })
        );
    }
    
    // Load fonts with mobile-specific timeout
    const timeout = isMobile ? 5000 : 3000; // Longer timeout for mobile
    
    const fontPromises = fonts.map(font => {
        return Promise.race([
            font.load(),
            new Promise((_, reject) => 
                setTimeout(() => reject(new Error('Font load timeout')), timeout)
            )
        ]).then(loadedFont => {
            document.fonts.add(loadedFont);
            console.log(`✓ RumepFont loaded: ${loadedFont.family}`);
            
            // Mobile-specific font validation
            if (isMobile) {
                validateMobileFont(loadedFont);
            }
            
            return loadedFont;
        }).catch(error => {
            console.warn(`✗ RumepFont loading failed: ${font.family}`, error);
            
            // Show debug info on mobile
            if (isMobile && window.location.search.includes('debug=font')) {
                showMobileFontDebug(font.family, error);
            }
            
            return null;
        });
    });
    
    // Wait for fonts or timeout
    Promise.allSettled(fontPromises).then(() => {
        document.body.classList.remove('font-loading');
        document.body.classList.add('font-loaded');
        
        // Apply fonts to elements
        applyFontsToElements();
        
        // Check font support after loading
        setTimeout(checkFontSupport, 500);
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
    
    // Fallback for very slow connections
    setTimeout(() => {
        if (document.body.classList.contains('font-loading')) {
            document.body.classList.remove('font-loading');
            document.body.classList.add('font-loaded');
            console.warn('Font loading timeout, using fallback');
        }
    }, 5000);
    
    function checkFontSupport() {
        // Test multiple RumepLogosSVG characters
        const testChars = [0xE000, 0xE001, 0xE002, 0xE003];
        let fontsWorking = 0;
        
        testChars.forEach((charCode, index) => {
            const testElement = document.createElement('span');
            testElement.style.fontFamily = 'RumepLogosSVG';
            testElement.style.fontSize = '24px';
            testElement.textContent = String.fromCharCode(charCode);
            testElement.style.position = 'absolute';
            testElement.style.visibility = 'hidden';
            testElement.style.left = '-9999px';
            
            document.body.appendChild(testElement);
            
            setTimeout(() => {
                const computedStyle = window.getComputedStyle(testElement);
                const actualFont = computedStyle.fontFamily;
                
                if (actualFont.includes('RumepLogosSVG')) {
                    fontsWorking++;
                    console.log(`✓ RumepFont char ${charCode.toString(16)} working`);
                } else {
                    console.warn(`✗ RumepFont char ${charCode.toString(16)} not working`);
                }
                
                document.body.removeChild(testElement);
                
                // Final check after all characters tested
                if (index === testChars.length - 1) {
                    if (fontsWorking === 0) {
                        console.error('RumepLogosSVG fonts completely failed');
                        if (window.location.search.includes('debug=font')) {
                            showMobileFontDebug('RumepLogosSVG', 'No characters rendering');
                        }
                    } else if (fontsWorking < testChars.length) {
                        console.warn(`RumepLogosSVG partially working: ${fontsWorking}/${testChars.length}`);
                    } else {
                        console.log('✓ All RumepLogosSVG characters working!');
                    }
                }
            }, 200 + (index * 50));
        });
    }
    
    function validateMobileFont(font) {
        // Mobile-specific font validation
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        
        ctx.font = '20px ' + font.family;
        const testChar = String.fromCharCode(0xE000);
        const metrics = ctx.measureText(testChar);
        
        if (metrics.width > 0) {
            console.log(`✓ Mobile font validation passed for ${font.family}`);
        } else {
            console.warn(`✗ Mobile font validation failed for ${font.family}`);
        }
    }
    
    function showMobileFontDebug(fontName, error) {
        const debug = document.createElement('div');
        debug.className = 'debug-font';
        debug.innerHTML = `
            <strong>Font Debug:</strong><br>
            Font: ${fontName}<br>
            Error: ${error}<br>
            UA: ${navigator.userAgent.substring(0, 50)}...
        `;
        document.body.appendChild(debug);
        
        setTimeout(() => debug.remove(), 10000);
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