export function initEditKelimeForm() {
    const form = document.getElementById('edit-kelime-form');
    const errorDiv = document.getElementById('edit-form-errors');
    if (!form || !errorDiv) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        errorDiv.classList.add('d-none');
        errorDiv.innerHTML = '';

        const formData = new FormData(form);
        try {
            console.log(`Kelime düzenleme isteği: ${form.action}`);
            const response = await fetch(form.action, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content || ''
                },
                body: formData
            });
            const data = await response.json();
            console.log('Kelime düzenleme yanıtı:', data);
            if (data.success) {
                alert(window.i18n?.t('sozluk.word_updated_success') || 'Kelime başarıyla güncellendi!');
                window.location.reload();
            } else {
                errorDiv.classList.remove('d-none');
                errorDiv.textContent = window.i18n?.t('common.error_try_again') || 'Bir hata oluştu, lütfen tekrar deneyin.';
            }
        } catch (error) {
            console.error('Düzenleme hatası:', error);
            errorDiv.classList.remove('d-none');
            errorDiv.textContent = window.i18n?.t('common.error_try_again') || 'Bir hata oluştu, lütfen tekrar deneyin.';
        }
    });
}