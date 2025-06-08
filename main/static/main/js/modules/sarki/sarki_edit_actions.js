// Şarkı düzenleme işlemleri
export function initSarkiEditActions() {
    // Şarkı düzenleme
    document.querySelectorAll('.sarki-duzenle-btn').forEach(button => {
        button.addEventListener('click', async () => {
            const sarkiId = button.getAttribute('data-sarki-id');
            const duzenleUrl = button.getAttribute('data-url-duzenle');
            const modal = new bootstrap.Modal(document.getElementById('sarkiDuzenleModal'));
            
            try {
                const response = await fetch(duzenleUrl, {
                    method: 'GET',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });
                const data = await response.json();
                if (data.success) {
                    document.getElementById('sarki-duzenle-ad').value = data.data.ad;
                    document.getElementById('sarki-duzenle-sozler').value = data.data.sozler;
                    document.getElementById('sarki-duzenle-link').value = data.data.link || '';
                    document.getElementById('sarki-duzenle-tur').value = data.data.tur || '';
                    modal.show();
                } else {
                    alert(data.error || 'Veri alınırken bir hata oluştu.');
                }
            } catch (error) {
                console.error('Şarkı verisi alınamadı:', error);
                alert('Bir hata oluştu: ' + error.message);
            }
        });
    });

    // Şarkı düzenleme formu gönderimi
    const sarkiDuzenleForm = document.getElementById('sarki-duzenle-form');
    if (sarkiDuzenleForm) {
        sarkiDuzenleForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const duzenleUrl = document.querySelector('.sarki-duzenle-btn').getAttribute('data-url-duzenle');
            
            try {
                const response = await fetch(duzenleUrl, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });
                const data = await response.json();
                if (data.success) {
                    location.reload();
                } else {
                    let errorMessage = 'Bir hata oluştu.';
                    if (data.error) {
                        errorMessage = data.error;
                    } else if (data.errors) {
                        const errors = JSON.parse(data.errors);
                        errorMessage = 'Hatalar:\n';
                        for (const [field, errorList] of Object.entries(errors)) {
                            errorList.forEach(error => {
                                errorMessage += `${field}: ${error.message}\n`;
                            });
                        }
                    }
                    alert(errorMessage);
                }
            } catch (error) {
                console.error('Şarkı düzenleme hatası:', error);
                alert('Bir hata oluştu: ' + error.message);
            }
        });
    }
}