// Custom Emoji System
document.addEventListener('DOMContentLoaded', function() {
    let currentTextarea = null;
    
    // Custom emoji characters
    const customEmojis = [
        { char: String.fromCharCode(0xE000), name: 'Emoji 1', unicode: 'E000' },
        { char: String.fromCharCode(0xE002), name: 'Emoji 2', unicode: 'E002' },
        { char: String.fromCharCode(0xE003), name: 'Emoji 3', unicode: 'E003' },
        { char: String.fromCharCode(0xE004), name: 'Emoji 4', unicode: 'E004' },
        { char: String.fromCharCode(0xE005), name: 'Emoji 5', unicode: 'E005' },
        { char: String.fromCharCode(0xE006), name: 'Emoji 6', unicode: 'E006' },
        { char: String.fromCharCode(0xE007), name: 'Emoji 7', unicode: 'E007' },
        { char: String.fromCharCode(0xE008), name: 'Emoji 8', unicode: 'E008' },
        { char: String.fromCharCode(0xE009), name: 'Emoji 9', unicode: 'E009' }
    ];
    
    // Create emoji modal
    createEmojiModal();
    
    // Add emoji buttons to textareas
    addEmojiButtons();
    
    function createEmojiModal() {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.id = 'customEmojiModal';
        modal.innerHTML = `
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Emojiler</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="emoji-grid" id="emojiGrid">
                            ${customEmojis.map(emoji => `
                                <button type="button" class="btn btn-outline-secondary emoji-btn m-1" 
                                        style="font-family: RumepLogosSVG; font-size: 24px;" 
                                        data-char="${emoji.char}" title="${emoji.name}">
                                    ${emoji.char}
                                </button>
                            `).join('')}
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Add emoji click handlers
        modal.querySelectorAll('.emoji-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const char = this.dataset.char;
                insertEmojiToTextarea(char);
                
                // Close modal
                const modalInstance = bootstrap.Modal.getInstance(modal);
                modalInstance.hide();
            });
        });
    }
    
    function addEmojiButtons() {
        // Handle existing font buttons (rename to emoji buttons)
        document.querySelectorAll('.font-btn').forEach(fontBtn => {
            fontBtn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                const textareaId = this.getAttribute('data-textarea');
                currentTextarea = document.getElementById(textareaId);
                
                const emojiModal = new bootstrap.Modal(document.getElementById('customEmojiModal'));
                emojiModal.show();
            });
        });
    }
    
    function insertEmojiToTextarea(char) {
        if (currentTextarea) {
            const start = currentTextarea.selectionStart;
            const end = currentTextarea.selectionEnd;
            const text = currentTextarea.value;
            
            // Insert the emoji character
            currentTextarea.value = text.substring(0, start) + char + text.substring(end);
            currentTextarea.setSelectionRange(start + 1, start + 1);
            
            // Apply emoji font to textarea temporarily for display
            if (!currentTextarea.style.fontFamily || currentTextarea.style.fontFamily === '') {
                currentTextarea.style.fontFamily = 'RumepLogosSVG, Inter, system-ui, sans-serif';
            }
            
            currentTextarea.focus();
        }
    }
});