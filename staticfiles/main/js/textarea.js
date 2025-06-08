function initTextarea() {
    document.querySelectorAll('.auto-resize').forEach(textArea => {
        textArea.style.height = 'auto';
        textArea.style.height = `${textArea.scrollHeight}px`;
        textArea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = `${this.scrollHeight}px`;
        });
    });
}
export { initTextarea };