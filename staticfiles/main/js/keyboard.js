export function initializeEmojiPanel() {
    const container = document.getElementById('emoji-container');
    if (!container) {
        console.warn('Emoji container bulunamadı');
        return;
    }
    const EMOJIS = {
        ':smile:': '😊',
        ':star:': '⭐',
        ':heart:': '❤️',
        ':cool:': '😎',
        ':fire:': '🔥'
    };
    for (const [code, symbol] of Object.entries(EMOJIS)) {
        const button = document.createElement('button');
        button.className = 'btn btn-light p-1 m-1';
        button.textContent = symbol;
        button.onclick = () => insertEmoji(code);
        container.appendChild(button);
    }
}

export function openEmojiModal() {
    const modalElement = document.getElementById('emojiModal');
    if (!modalElement) {
        console.warn('Emoji modal bulunamadı');
        return;
    }
    const modal = new bootstrap.Modal(modalElement);
    modal.show();
}

function insertEmoji(emoji) {
    const textarea = document.querySelector('textarea[name="text"]');
    if (!textarea) {
        console.warn('Textarea bulunamadı');
        return;
    }
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    textarea.value = textarea.value.substring(0, start) + emoji + textarea.value.substring(end);
    textarea.selectionStart = textarea.selectionEnd = start + emoji.length;
    textarea.dispatchEvent(new Event('input'));
    textarea.focus();
}

// Global erişim için
window.openEmojiModal = openEmojiModal;