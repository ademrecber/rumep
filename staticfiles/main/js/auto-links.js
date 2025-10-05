// Auto-Links Helper JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Add tooltips for auto-link patterns
    const textarea = document.querySelector('textarea[name="content"]');
    if (textarea) {
        // Create help tooltip
        const helpDiv = document.createElement('div');
        helpDiv.className = 'auto-link-help mt-2';
        helpDiv.innerHTML = `
            <small class="text-muted">
                <strong>Otomatik Linkler:</strong>
                Sözlükteki kelimeler otomatik link olur (xweş, amed, vb.)
            </small>
        `;
        
        // Insert after textarea
        textarea.parentNode.insertBefore(helpDiv, textarea.nextSibling);
    }

});