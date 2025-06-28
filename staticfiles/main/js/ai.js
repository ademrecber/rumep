
import { getCsrfToken } from './like.js';

export function initAiEnhance() {
    const aiButton = document.getElementById('aiEnhanceButton');
    const aiToast = document.getElementById('aiEnhanceToast');
    const confirmButton = document.getElementById('confirmEnhance');
    const postInput = document.getElementById('id_text'); // Doğru ID: id_text

    if (aiButton && aiToast && confirmButton && postInput) {
        console.log('AI metin işleme elementleri bulundu:', { aiButton, aiToast, confirmButton, postInput });
        aiButton.addEventListener('click', () => {
            console.log('Sihir değendi tıklandı, metin:', postInput.value);
            if (!postInput.value.trim()) {
                console.warn('Metin boş, işleme iptal edildi.');
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
            bootstrap.Toast.getOrCreateInstance(aiToast).show();
        });

        confirmButton.addEventListener('click', async () => {
            console.log('Metin işleme onaylandı, AJAX isteği gönderiliyor...');
            const csrfToken = getCsrfToken();
            if (!csrfToken) {
                console.error('CSRF token bulunamadı.');
                return;
            }
            try {
                const response = await fetch('/enhance/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'X-Requested-With': 'XMLHttpRequest',
                        'Content-Type': 'application/x-www-form-urlencoded'
                    },
                    body: `text=${encodeURIComponent(postInput.value)}&language=tr`
                });
                console.log('AJAX yanıtı alındı:', response.status);
                const data = await response.json();
                console.log('Sunucu yanıtı:', data);
                if (!response.ok) {
                    throw new Error(`Sunucu hatası: ${response.status} - ${data.error || 'Bilinmeyen hata'}`);
                }
                if (data.success) {
                    console.log('Metin işlendi:', data.enhanced_text);
                    postInput.value = data.enhanced_text;
                    bootstrap.Toast.getInstance(aiToast).hide();
                } else {
                    console.error('Metin işleme hatası:', data.error);
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
                console.error('Metin işleme hatası:', error);
                const errorToast = document.createElement('div');
                errorToast.className = 'toast';
                errorToast.innerHTML = `
                    <div class="toast-header">
                        <strong class="me-auto">Hata</strong>
                        <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
                    </div>
                    <div class="toast-body">
                        Metin işleme başarısız: ${error.message}
                    </div>
                `;
                document.querySelector('.toast-container').appendChild(errorToast);
                bootstrap.Toast.getOrCreateInstance(errorToast).show();
            }
        });
    } else {
        console.error('AI metin işleme için gerekli elementler bulunamadı:', { aiButton: !!aiButton, aiToast: !!aiToast, confirmButton: !!confirmButton, postInput: !!postInput });
    }
}
