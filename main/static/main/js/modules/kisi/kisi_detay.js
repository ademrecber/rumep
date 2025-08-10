import { getCsrfToken } from '../../like.js';

export function initDetayEkleForm() {
    const form = document.getElementById('detay-ekle-form');
    const errorDiv = document.getElementById('detay-form-errors');
    if (!form || !errorDiv) {
        console.warn('Detay ekleme formu veya hata divi bulunamadı:', { form: !!form, errorDiv: !!errorDiv });
        return;
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        errorDiv.classList.add('d-none');
        errorDiv.innerHTML = '';

        const formData = new FormData(form);
        try {
            console.log(`Detay ekleme isteği: ${form.action}`);
            const response = await fetch(form.action, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCsrfToken() || ''
                },
                body: formData
            });
            const data = await response.json();
            console.log('Detay ekleme yanıtı:', data);
            if (data.success) {
                alert('Berfirehî bi serkeftî hate zêdekirin!');
                window.location.reload();
            } else {
                errorDiv.classList.remove('d-none');
                errorDiv.textContent = 'Çewtîyek çêbû, ji kerema xwe dîsa biceribîne.';
                if (data.errors) {
                    for (const [field, message] of Object.entries(data.errors)) {
                        errorDiv.innerHTML += `<p>${message}</p>`;
                    }
                }
            }
        } catch (error) {
            console.error('Detay ekleme hatası:', error);
            errorDiv.classList.remove('d-none');
            errorDiv.textContent = 'Çewtîyek çêbû, ji kerema xwe dîsa biceribîne.';
        }
    });
}

export function initEditDetayForm() {
    const form = document.getElementById('edit-detay-form');
    const errorDiv = document.getElementById('edit-detay-form-errors');
    if (!form || !errorDiv) {
        console.warn('Detay düzenleme formu veya hata divi bulunamadı:', { form: !!form, errorDiv: !!errorDiv });
        return;
    }

    document.querySelectorAll('.edit-detay-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            const detayId = btn.dataset.detayId;
            const url = btn.dataset.url;
            try {
                const response = await fetch(url, {
                    method: 'GET',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': getCsrfToken() || ''
                    }
                });
                const data = await response.json();
                console.log('Detay verisi alındı:', data);
                if (data.success) {
                    form.action = `/kisi/detay-duzenle/${detayId}/`;
                    form.querySelector('#detay').value = data.detay;
                } else {
                    alert(data.error || 'Di dema wergirtina daneyên berfirehiyê de çewtîyek çêbû.');
                }
            } catch (error) {
                console.error('Detay verisi alma hatası:', error);
                alert('Çewtîyek çêbû, ji kerema xwe dîsa biceribîne.');
            }
        });
    });

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
                    'X-CSRFToken': getCsrfToken() || ''
                },
                body: formData
            });
            const data = await response.json();
            console.log('Detay düzenleme yanıtı:', data);
            if (data.success) {
                alert('Berfirehî bi serkeftî hate guherandin!');
                window.location.reload();
            } else {
                errorDiv.classList.remove('d-none');
                errorDiv.textContent = 'Çewtîyek çêbû, ji kerema xwe dîsa biceribîne.';
                if (data.errors) {
                    for (const [field, message] of Object.entries(data.errors)) {
                        errorDiv.innerHTML += `<p>${message}</p>`;
                    }
                }
            }
        } catch (error) {
            console.error('Detay düzenleme hatası:', error);
            errorDiv.classList.remove('d-none');
            errorDiv.textContent = 'Çewtîyek çêbû, ji kerema xwe dîsa biceribîne.';
        }
    });
}

export function initDetaySil() {
    document.querySelectorAll('.delete-detay-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            if (!confirm('Ma hûn ji vê berfirehiyê jêbirinê piştrast in?')) return;
            const detayId = btn.dataset.detayId;
            const url = btn.dataset.url;
            try {
                console.log(`Detay silme isteği: ${url}`);
                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': getCsrfToken() || ''
                    }
                });
                const data = await response.json();
                console.log('Detay silme yanıtı:', data);
                if (data.success) {
                    document.querySelector(`.detay-item[data-detay-id="${detayId}"]`).remove();
                    alert('Berfirehî bi serkeftî hate jêbirin!');
                } else {
                    alert(data.error || 'Di dema jêbirina berfirehiyê de çewtîyek çêbû.');
                }
            } catch (error) {
                console.error('Detay silme hatası:', error);
                alert('Çewtîyek çêbû, ji kerema xwe dîsa biceribîne.');
            }
        });
    });
}
