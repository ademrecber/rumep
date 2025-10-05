// Font Keyboard System
document.addEventListener('DOMContentLoaded', function() {
    let currentTextarea = null;
    
    // Font definitions with character ranges
    const fonts = [
        {
            name: 'RumepLogosSVG',
            family: 'RumepLogosSVG',
            preview: String.fromCharCode(0xE000) + String.fromCharCode(0xE002) + String.fromCharCode(0xE005),
            type: 'symbol',
            characters: [
                { char: String.fromCharCode(0xE000), name: 'Logo 1', unicode: 'E000' },
                { char: String.fromCharCode(0xE002), name: 'Logo 2', unicode: 'E002' },
                { char: String.fromCharCode(0xE003), name: 'Logo 3', unicode: 'E003' },
                { char: String.fromCharCode(0xE004), name: 'Logo 4', unicode: 'E004' },
                { char: String.fromCharCode(0xE005), name: 'Logo 5', unicode: 'E005' },
                { char: String.fromCharCode(0xE006), name: 'Logo 6', unicode: 'E006' },
                { char: String.fromCharCode(0xE007), name: 'Logo 7', unicode: 'E007' },
                { char: String.fromCharCode(0xE008), name: 'Logo 8', unicode: 'E008' },
                { char: String.fromCharCode(0xE009), name: 'Logo 9', unicode: 'E009' }
            ]
        },
        {
            name: 'RumepLogosCOLR', 
            family: 'RumepLogosCOLR',
            preview: String.fromCharCode(0xE000) + String.fromCharCode(0xE002) + String.fromCharCode(0xE005),
            type: 'color',
            characters: [
                { char: String.fromCharCode(0xE000), name: 'Logo 1', unicode: 'E000' },
                { char: String.fromCharCode(0xE002), name: 'Logo 2', unicode: 'E002' },
                { char: String.fromCharCode(0xE003), name: 'Logo 3', unicode: 'E003' },
                { char: String.fromCharCode(0xE004), name: 'Logo 4', unicode: 'E004' },
                { char: String.fromCharCode(0xE005), name: 'Logo 5', unicode: 'E005' },
                { char: String.fromCharCode(0xE006), name: 'Logo 6', unicode: 'E006' },
                { char: String.fromCharCode(0xE007), name: 'Logo 7', unicode: 'E007' },
                { char: String.fromCharCode(0xE008), name: 'Logo 8', unicode: 'E008' },
                { char: String.fromCharCode(0xE009), name: 'Logo 9', unicode: 'E009' }
            ]
        },
        {
            name: 'Varsayılan',
            family: 'Inter, system-ui, sans-serif',
            preview: 'Merhaba Dünya',
            type: 'default',
            characters: []
        }
    ];
    
    // Generate character range
    function generateCharacterRange(start, end) {
        const chars = [];
        for (let i = start; i <= end; i++) {
            chars.push(String.fromCharCode(i));
        }
        return chars;
    }
    
    // Create font keyboard modal
    createFontModal();
    
    // Add font button to textareas
    addFontButtons();
    
    // Load saved font preference
    loadSavedFont();
    
    function createFontModal() {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.id = 'fontModal';
        modal.innerHTML = `
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Font Seç</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <!-- Font Selection -->
                        <div class="font-selection mb-3">
                            <label class="form-label">Font Seç:</label>
                            <div class="btn-group w-100" role="group">
                                ${fonts.map((font, index) => `
                                    <button type="button" class="btn btn-outline-primary font-selector ${index === 0 ? 'active' : ''}" 
                                            data-font="${font.family}" data-font-index="${index}">
                                        ${font.name}
                                    </button>
                                `).join('')}
                            </div>
                        </div>
                        
                        <!-- Character Keyboard -->
                        <div class="character-keyboard mb-3">
                            <label class="form-label">Karakterler:</label>
                            <div class="character-grid" id="characterGrid">
                                <!-- Karakterler burada yüklenecek -->
                            </div>
                        </div>
                        
                        <!-- Test Area -->
                        <div class="mt-3">
                            <label class="form-label">Test Alanı:</label>
                            <textarea class="form-control" id="fontTestArea" rows="3" 
                                placeholder="Karakterlere tıklayarak test edin..."></textarea>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">İptal</button>
                        <button type="button" class="btn btn-primary" id="applyFont">Uygula</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Font selector click handlers
        modal.querySelectorAll('.font-selector').forEach(selector => {
            selector.addEventListener('click', function() {
                // Remove active class from all
                modal.querySelectorAll('.font-selector').forEach(sel => {
                    sel.classList.remove('active');
                });
                
                // Add active class to clicked
                this.classList.add('active');
                
                // Load characters for selected font
                const fontIndex = parseInt(this.dataset.fontIndex);
                const fontFamily = this.dataset.font;
                loadCharacters(fontIndex, fontFamily);
                
                // Apply to test area
                const testArea = modal.querySelector('#fontTestArea');
                testArea.style.fontFamily = fontFamily;
            });
        });
        
        // Load initial characters
        loadCharacters(0, fonts[0].family);
        
        function loadCharacters(fontIndex, fontFamily) {
            const characterGrid = modal.querySelector('#characterGrid');
            const font = fonts[fontIndex];
            
            if (font.characters.length === 0) {
                characterGrid.innerHTML = `<p class="text-muted">Bu font için karakter klavyesi mevcut değil.</p>`;
                return;
            }
            
            characterGrid.innerHTML = font.characters.map(charObj => {
                const char = typeof charObj === 'string' ? charObj : charObj.char;
                const name = typeof charObj === 'string' ? char : charObj.name;
                const unicode = typeof charObj === 'string' ? '' : charObj.unicode;
                
                return `
                    <div class="character-item">
                        <button type="button" class="btn btn-outline-secondary character-btn" 
                                style="font-family: ${fontFamily};" data-char="${char}" title="${name} (${unicode})">
                            ${char}
                        </button>
                        <small class="character-label">${name}</small>
                    </div>
                `;
            }).join('');
            
            // Add character click handlers
            characterGrid.querySelectorAll('.character-btn').forEach(btn => {
                btn.addEventListener('click', function() {
                    const char = this.dataset.char;
                    const testArea = modal.querySelector('#fontTestArea');
                    
                    // Insert character at cursor position
                    const start = testArea.selectionStart;
                    const end = testArea.selectionEnd;
                    const text = testArea.value;
                    
                    testArea.value = text.substring(0, start) + char + text.substring(end);
                    testArea.setSelectionRange(start + 1, start + 1);
                    testArea.focus();
                });
            });
        }
        
        // Apply button handler
        modal.querySelector('#applyFont').addEventListener('click', function() {
            const activeFont = modal.querySelector('.font-selector.active');
            const testArea = modal.querySelector('#fontTestArea');
            
            if (activeFont && currentTextarea) {
                const fontFamily = activeFont.dataset.font;
                
                // Apply font to textarea
                applyFontToTextarea(fontFamily);
                
                // Copy test area content to textarea if there's content
                if (testArea.value.trim()) {
                    const start = currentTextarea.selectionStart;
                    const end = currentTextarea.selectionEnd;
                    const currentText = currentTextarea.value;
                    
                    currentTextarea.value = currentText.substring(0, start) + testArea.value + currentText.substring(end);
                    currentTextarea.setSelectionRange(start + testArea.value.length, start + testArea.value.length);
                }
                
                // Close modal
                const modalInstance = bootstrap.Modal.getInstance(modal);
                modalInstance.hide();
            }
        });
    }
    
    function addFontButtons() {
        // Handle existing font buttons and add to emoji buttons
        document.querySelectorAll('.font-btn').forEach(fontBtn => {
            fontBtn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                const textareaId = this.getAttribute('data-textarea');
                currentTextarea = document.getElementById(textareaId);
                
                const fontModal = new bootstrap.Modal(document.getElementById('fontModal'));
                fontModal.show();
            });
        });
        
        // Add font button next to emoji buttons that don't have one
        document.querySelectorAll('.emoji-btn').forEach(emojiBtn => {
            // Check if font button already exists
            const existingFontBtn = emojiBtn.parentNode.querySelector('.font-btn');
            if (existingFontBtn) return;
            
            const fontBtn = document.createElement('button');
            fontBtn.type = 'button';
            fontBtn.className = 'btn btn-outline-secondary btn-sm ms-1 font-btn';
            fontBtn.innerHTML = '<i class="bi bi-fonts"></i>';
            fontBtn.title = 'Font Seç';
            
            const textareaId = emojiBtn.getAttribute('data-textarea');
            fontBtn.setAttribute('data-textarea', textareaId);
            
            fontBtn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                currentTextarea = document.getElementById(textareaId);
                
                const fontModal = new bootstrap.Modal(document.getElementById('fontModal'));
                fontModal.show();
            });
            
            emojiBtn.parentNode.insertBefore(fontBtn, emojiBtn.nextSibling);
        });
    }
    
    function applyFontToTextarea(fontFamily) {
        if (currentTextarea) {
            currentTextarea.style.fontFamily = fontFamily;
            
            // Add data attribute to preserve font info
            currentTextarea.setAttribute('data-font-family', fontFamily);
            
            // Save to hidden input for form submission
            const form = currentTextarea.closest('form');
            if (form) {
                let fontInput = form.querySelector('input[name="font_family"]');
                if (!fontInput) {
                    fontInput = document.createElement('input');
                    fontInput.type = 'hidden';
                    fontInput.name = 'font_family';
                    form.appendChild(fontInput);
                }
                fontInput.value = fontFamily;
            }
            
            // Save preference
            localStorage.setItem('selectedFont', fontFamily);
            
            // Show success message
            showFontToast('Font uygulandı!', 'success');
        }
    }
    
    function loadSavedFont() {
        const savedFont = localStorage.getItem('selectedFont');
        if (savedFont) {
            // Apply to all textareas
            document.querySelectorAll('textarea').forEach(textarea => {
                if (!textarea.style.fontFamily) {
                    textarea.style.fontFamily = savedFont;
                    textarea.setAttribute('data-font-family', savedFont);
                }
            });
        }
        
        // Apply fonts to existing entry content
        document.querySelectorAll('.entry-content, .first-entry-preview').forEach(element => {
            const fontFamily = element.getAttribute('data-font-family');
            if (fontFamily) {
                element.style.fontFamily = fontFamily;
            }
        });
    }
    
    function showFontToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = 'toast position-fixed';
        toast.style.cssText = 'bottom: 20px; right: 20px; z-index: 9999;';
        
        const bgClass = type === 'success' ? 'bg-success' : 'bg-info';
        
        toast.innerHTML = `
            <div class="toast-header ${bgClass} text-white">
                <strong class="me-auto">Font</strong>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        `;
        
        document.body.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 3000);
    }
});