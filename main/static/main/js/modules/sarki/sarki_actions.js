export function initSarkiActions() {
    // Şarkı silme (detay sayfasında)
    document.querySelectorAll('.sarki-sil-btn').forEach(button => {
        button.addEventListener('click', async () => {
            if (!confirm('Ma hûn ji vê stranê jêbirinê piştrast in?')) return;
            const sarkiId = button.getAttribute('data-sarki-id');
            const albumId = button.getAttribute('data-album-id');
            const silUrl = button.getAttribute('data-url-sil');
            try {
                const response = await fetch(silUrl, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                });
                const data = await response.json();
                if (data.success) {
                    // Silme işleminden sonra şarkı listesine yönlendir
                    window.location.href = `/sarki/liste/${albumId}/`;
                } else {
                    alert(data.error || 'Çewtîyek çêbû.');
                }
            } catch (error) {
                console.error('Şarkı silme hatası:', error);
                alert('Çewtîyek çêbû.');
            }
        });
    });

    // Berfirehî ekleme
    const detayEkleButton = document.querySelector('[data-action="detay-ekle"]');
    if (detayEkleButton) {
        detayEkleButton.addEventListener('click', () => {
            const modal = new bootstrap.Modal(document.getElementById('detayEkleModal'));
            document.getElementById('detay-ekle-sarki-id').value = detayEkleButton.getAttribute('data-sarki-id');
            document.getElementById('detay-ekle-text').value = '';
            modal.show();
        });
    }

    // Berfirehî ekleme formu gönderimi
    const detayEkleForm = document.getElementById('detay-ekle-form');
    if (detayEkleForm) {
        detayEkleForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const sarkiId = formData.get('sarki_id');
            try {
                const response = await fetch(`/sarki/detay-ekle/${sarkiId}/`, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                    }
                });
                const data = await response.json();
                if (data.success) {
                    location.reload();
                } else {
                    let errorMessage = 'Çewtîyek çêbû.';
                    if (data.errors) {
                        // Hata mesajlarını ayrıştır
                        if (typeof data.errors === 'string') {
                            errorMessage = data.errors;
                        } else if (data.errors.detay) {
                            const error = data.errors.detay[0];
                            if (error.code === 'min_length') {
                                errorMessage = 'Qada berfireh divê herî kêm 10 tîp be.';
                            } else if (error.code === 'required') {
                                errorMessage = 'Qada berfireh mecbûrî ye.';
                            } else {
                                errorMessage = error.message || 'Çewtiyek nenas çêbû.';
                            }
                        }
                    }
                    alert(errorMessage);
                }
            } catch (error) {
                console.error('Detay ekleme hatası:', error);
                alert('Çewtîyek çêbû.');
            }
        });
    }

    // Berfirehî düzenleme
    document.querySelectorAll('[data-action="detay-duzenle"]').forEach(button => {
        button.addEventListener('click', async () => {
            const detayId = button.getAttribute('data-detay-id');
            const modal = new bootstrap.Modal(document.getElementById('detayDuzenleModal'));
            document.getElementById('detay-duzenle-id').value = detayId;

            try {
                const response = await fetch(`/sarki/detay-veri/${detayId}/`);
                const data = await response.json();
                if (data.success) {
                    document.getElementById('detay-duzenle-text').value = data.data.detay;
                    modal.show();
                } else {
                    alert(data.error || 'Çewtîyek çêbû.');
                }
            } catch (error) {
                console.error('Detay verisi alınamadı:', error);
                alert('Çewtîyek çêbû.');
            }
        });
    });

    // Berfirehî düzenleme formu gönderimi
    const detayDuzenleForm = document.getElementById('detay-duzenle-form');
    if (detayDuzenleForm) {
        detayDuzenleForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const detayId = formData.get('detay_id');
            try {
                const response = await fetch(`/sarki/detay-duzenle/${detayId}/`, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                    }
                });
                const data = await response.json();
                if (data.success) {
                    location.reload();
                } else {
                    let errorMessage = 'Çewtîyek çêbû.';
                    if (data.errors) {
                        // Hata mesajlarını ayrıştır
                        if (typeof data.errors === 'string') {
                            errorMessage = data.errors;
                        } else if (data.errors.detay) {
                            const error = data.errors.detay[0];
                            if (error.code === 'min_length') {
                                errorMessage = 'Qada berfireh divê herî kêm 10 tîp be.';
                            } else if (error.code === 'required') {
                                errorMessage = 'Qada berfireh mecbûrî ye.';
                            } else {
                                errorMessage = error.message || 'Çewtiyek nenas çêbû.';
                            }
                        }
                    }
                    alert(errorMessage);
                }
            } catch (error) {
                console.error('Detay düzenleme hatası:', error);
                alert('Çewtîyek çêbû.');
            }
        });
    }

    // Berfirehî silme
    document.querySelectorAll('[data-action="detay-sil"]').forEach(button => {
        button.addEventListener('click', async () => {
            if (!confirm('Ma hûn ji vê berfirehiyê jêbirinê piştrast in?')) return;
            const detayId = button.getAttribute('data-detay-id');
            try {
                const response = await fetch(`/sarki/detay-sil/${detayId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                });
                const data = await response.json();
                if (data.success) {
                    location.reload();
                } else {
                    alert(data.error || 'Çewtîyek çêbû.');
                }
            } catch (error) {
                console.error('Detay silme hatası:', error);
                alert('Çewtîyek çêbû.');
            }
        });
    });
}