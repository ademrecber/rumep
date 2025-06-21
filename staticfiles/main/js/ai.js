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
            const errorToast = document.createElement('div');
            errorToast.className = 'toast';
            errorToast.innerHTML = `
                <div class="toast-header">
                    <strong class="me-auto">Hata</strong>
                    <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
                </div>
                <div class="toast-body">
                    Lütfen önce bir metin yazın.
                </div>
            `;
            document.querySelector('.toast-container').appendChild(errorToast);
            bootstrap.Toast.getOrCreateInstance(errorToast).show();
            return;
        }
        console.log('Sihir değneği tıklandı, metin:', textarea.value);
        bootstrap.Toast.getOrCreateInstance(aiToast).show();
    });

    confirmButton.addEventListener('click', async () => {
        const csrfToken = getCsrfToken();
        if (!csrfToken) {
            console.error('CSRF token bulunamadı.');
            return;
        }

        console.log('Gönderilen metin:', textarea.value);
        console.log('CSRF Token:', csrfToken);

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

            const data = await response.json();
            console.log('Sunucu yanıtı:', data);

            if (!response.ok) {
                throw new Error(`Sunucu hatası: ${response.status} - ${data.error || 'Bilinmeyen hata'}`);
            }

            if (data.success) {
                textarea.value = data.enhanced_text;
                textarea.dispatchEvent(new Event('input')); // Karakter sayısını güncelle
                bootstrap.Toast.getInstance(aiToast).hide();
            } else {
                console.error('Metin geliştirme hatası:', data.error);
                const errorToast = document.createElement('div');
                errorToast.className = 'toast';
                errorToast.innerHTML = `
                    <div class="toast-header">
                        <strong class="me-auto">Hata</strong>
                        <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
                    </div>
                    <div class="toast-body">
                        ${data.error}
                    </div>
                `;
                document.querySelector('.toast-container').appendChild(errorToast);
                bootstrap.Toast.getOrCreateInstance(errorToast).show();
            }
        } catch (error) {
            console.error('AI enhance hatası:', error);
            const errorToast = document.createElement('div');
            errorToast.className = 'toast';
            errorToast.innerHTML = `
                <div class="toast-header">
                    <strong class="me-auto">Hata</strong>
                    <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
                </div>
                <div class="toast-body">
                    Metin geliştirme başarısız: ${error.message}
                </div>
            `;
            document.querySelector('.toast-container').appendChild(errorToast);
            bootstrap.Toast.getOrCreateInstance(errorToast).show();
        }
    });
}
