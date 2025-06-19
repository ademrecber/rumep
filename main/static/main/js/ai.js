// rumep/main/static/main/js/ai.js

import { getCsrfToken } from './like.js';

export function initAiEnhance() {
    const aiButton = document.getElementById('aiEnhanceButton');
    const aiToast = document.getElementById('aiEnhanceToast');
    const confirmButton = document.getElementById('confirmEnhance');
    const textarea = document.querySelector('textarea[name="text"]');

    if (!aiButton || !aiToast || !confirmButton || !textarea) {
        console.warn('AI enhance için gerekli elementler bulunamadı.');
        return;
    }

    aiButton.addEventListener('click', () => {
        if (!textarea.value.trim()) {
            console.warn('Textarea boş, metin geliştirme iptal edildi.');
            return;
        }
        bootstrap.Toast.getOrCreateInstance(aiToast).show();
    });

    confirmButton.addEventListener('click', async () => {
        const csrfToken = getCsrfToken();
        if (!csrfToken) {
            console.error('CSRF token bulunamadı.');
            return;
        }

        try {
            const response = await fetch('/enhance-text/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: `text=${encodeURIComponent(textarea.value)}`
            });

            if (!response.ok) {
                throw new Error(`Sunucu hatası: ${response.status}`);
            }

            const data = await response.json();
            if (data.success) {
                textarea.value = data.enhanced_text;
                textarea.dispatchEvent(new Event('input')); // Karakter sayısını güncelle
                bootstrap.Toast.getInstance(aiToast).hide();
            } else {
                console.error('Metin geliştirme hatası:', data.error);
            }
        } catch (error) {
            console.error('AI enhance hatası:', error);
        }
    });
}
