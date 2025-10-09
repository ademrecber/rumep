export function initDetayEkleForm() {
    const form = document.getElementById('detay-ekle-form');
    const errorDiv = document.getElementById('detay-form-errors');
    if (!form || !errorDiv) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        errorDiv.classList.add('d-none');
        errorDiv.innerHTML = '';

        const formData = new FormData(form);
        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content || document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
        console.log('CSRF Token:', csrfToken);
        console.log('Form Data:', Object.fromEntries(formData));
        try {
            console.log(`Detay ekleme isteği: ${form.action}`);
            const response = await fetch(form.action, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.content || document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
                },
                body: formData
            });
            const data = await response.json();
            console.log('Detay ekleme yanıtı:', data);
            if (data.success) {
                alert(window.i18n?.t('sozluk.detail_added_success') || 'Detay başarıyla eklendi!');
                window.location.reload();
            } else {
                errorDiv.classList.remove('d-none');
                errorDiv.textContent = window.i18n?.t('common.error_try_again') || 'Bir hata oluştu, lütfen tekrar deneyin.';
            }
        } catch (error) {
            console.error('Detay ekleme hatası:', error);
            errorDiv.classList.remove('d-none');
            errorDiv.textContent = window.i18n?.t('common.error_try_again') || 'Bir hata oluştu, lütfen tekrar deneyin.';
        }
    });
}

export function initEditDetayForm() {
    const form = document.getElementById('edit-detay-form');
    const errorDiv = document.getElementById('edit-detay-form-errors');
    if (!form || !errorDiv) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        errorDiv.classList.add('d-none');
        errorDiv.innerHTML = '';

        const formData = new FormData(form);
        try {
            console.log(`Detay düzenleme isteği: ${form.action}`);
            const response = await fetch(form.action, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.content || document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
                },
                body: formData
            });
            const data = await response.json();
            console.log('Detay düzenleme yanıtı:', data);
            if (data.success) {
                alert(window.i18n?.t('sozluk.detail_updated_success') || 'Detay başarıyla güncellendi!');
                window.location.reload();
            } else {
                errorDiv.classList.remove('d-none');
                errorDiv.textContent = window.i18n?.t('common.error_try_again') || 'Bir hata oluştu, lütfen tekrar deneyin.';
            }
        } catch (error) {
            console.error('Detay düzenleme hatası:', error);
            errorDiv.classList.remove('d-none');
            errorDiv.textContent = window.i18n?.t('common.error_try_again') || 'Bir hata oluştu, lütfen tekrar deneyin.';
        }
    });
}