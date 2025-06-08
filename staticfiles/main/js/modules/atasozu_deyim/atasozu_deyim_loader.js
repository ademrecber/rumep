export function initAtasozuDeyimEkle() {
    const form = document.getElementById('atasozu-deyim-ekle-form');
    const errorDiv = document.getElementById('form-errors');
    if (!form || !errorDiv) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        errorDiv.classList.add('d-none');
        errorDiv.innerHTML = '';

        const formData = new FormData(form);
        try {
            const response = await fetch(form.action, {
                method: 'POST',
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
                body: formData
            });
            const data = await response.json();
            if (data.success) {
                form.reset();
                alert('Atasözü veya deyim başarıyla eklendi!');
                window.location.href = '/atasozu-deyim/';
            } else {
                errorDiv.classList.remove('d-none');
                errorDiv.innerHTML = '<p>Ekleme başarısız. Aşağıdaki hataları kontrol edin:</p><ul>';
                for (const [field, errors] of Object.entries(data.errors)) {
                    errors.forEach(error => {
                        errorDiv.innerHTML += `<li>${field}: ${error}</li>`;
                    });
                }
                errorDiv.innerHTML += '</ul>';
            }
        } catch (error) {
            console.error('Ekleme hatası:', error);
            errorDiv.classList.remove('d-none');
            errorDiv.innerHTML = '<p>Bir hata oluştu, lütfen tekrar deneyin.</p>';
        }
    });
}