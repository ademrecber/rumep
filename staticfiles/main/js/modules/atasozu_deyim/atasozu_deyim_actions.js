export function initAtasozuDeyimActions() {
    // Tüm silme formlarını seç (id'si sil-form ile başlayanlar)
    const silForms = document.querySelectorAll('[id^="sil-form"]');
    silForms.forEach(form => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const tur = form.getAttribute('data-tur');
            const mesaj = `Bu ${tur === 'atasozu' ? 'atasözünü' : 'deyimi'} silmek istediğinizden emin misiniz?`;
            if (!confirm(mesaj)) {
                return;
            }

            try {
                const response = await fetch(form.action, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': form.querySelector('[name=csrfmiddlewaretoken]').value,
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });
                const data = await response.json();
                if (data.success) {
                    // Silme işlemi başarılı, liste sayfasına yönlendir
                    window.location.href = `/atasozu-deyim/?sekme=${tur}`;
                } else {
                    alert(data.error || 'Silme işlemi sırasında bir hata oluştu.');
                }
            } catch (error) {
                console.error('Silme hatası:', error);
                alert('Bir hata oluştu, lütfen tekrar deneyin.');
            }
        });
    });

    // Detay ekleme
    const detayEkleButton = document.querySelector('[data-action="detay-ekle"]');
    if (detayEkleButton) {
        detayEkleButton.addEventListener('click', () => {
            const modal = new bootstrap.Modal(document.getElementById('detayEkleModal'));
            document.getElementById('detay-ekle-tur').value = detayEkleButton.getAttribute('data-tur');
            document.getElementById('detay-ekle-id').value = detayEkleButton.getAttribute('data-id');
            document.getElementById('detay-ekle-text').value = '';
            modal.show();
        });
    }

    // Detay ekleme formu gönderimi
    const detayEkleForm = document.getElementById('detay-ekle-form');
    if (detayEkleForm) {
        detayEkleForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const tur = formData.get('tur');
            const id = formData.get('id');
            try {
                const response = await fetch(`/atasozu-deyim/${tur}/${id}/detay-ekle/`, {
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
                    // Hata mesajını konsola yazdır
                    console.error('Detay ekleme hatası (tam yanıt):', data);
                    let errorMessage = 'Detay eklenemedi. Hata: ';
                    if (data.error) {
                        console.log('Hata (error):', data.error);
                        errorMessage += data.error;
                    } else if (data.errors) {
                        // Hataları JSON string olarak konsola yazdır
                        console.log('Hata (errors):', JSON.stringify(data.errors, null, 2));
                        errorMessage += '\n';
                        for (const [field, errors] of Object.entries(data.errors)) {
                            errors.forEach(error => {
                                errorMessage += `${field}: ${error.message || error}\n`;
                            });
                        }
                    } else {
                        errorMessage += 'Bilinmeyen bir hata oluştu.';
                    }
                    alert(errorMessage);
                }
            } catch (error) {
                // Catch bloğuna düşerse, hatayı konsola yazdır
                console.error('Fetch hatası:', error);
                alert('Bir hata oluştu: ' + error.message);
            }
        });
    }

    // Detay düzenleme
    document.querySelectorAll('[data-action="detay-duzenle"]').forEach(button => {
        button.addEventListener('click', async () => {
            const detayId = button.getAttribute('data-detay-id');
            const modal = new bootstrap.Modal(document.getElementById('detayDuzenleModal'));
            document.getElementById('detay-duzenle-id').value = detayId;

            try {
                const response = await fetch(`/atasozu-deyim/detay/${detayId}/veri/`);
                const data = await response.json();
                if (data.success) {
                    document.getElementById('detay-duzenle-text').value = data.data.detay;
                    modal.show();
                } else {
                    alert(data.error || 'Bir hata oluştu.');
                }
            } catch (error) {
                console.error('Detay verisi alınamadı:', error);
                alert('Bir hata oluştu.');
            }
        });
    });

    // Detay düzenleme formu gönderimi
    const detayDuzenleForm = document.getElementById('detay-duzenle-form');
    if (detayDuzenleForm) {
        detayDuzenleForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const detayId = formData.get('detay_id');
            try {
                const response = await fetch(`/atasozu-deyim/detay/${detayId}/duzenle/`, {
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
                    let errorMessage = 'Bir hata oluştu.';
                    if (data.errors) {
                        errorMessage = 'Hatalar:\n';
                        for (const [field, errors] of Object.entries(data.errors)) {
                            errors.forEach(error => {
                                errorMessage += `${field}: ${error}\n`;
                            });
                        }
                    }
                    alert(errorMessage);
                }
            } catch (error) {
                console.error('Detay düzenleme hatası:', error);
                alert('Bir hata oluştu.');
            }
        });
    }

    // Detay silme
    document.querySelectorAll('[data-action="detay-sil"]').forEach(button => {
        button.addEventListener('click', async () => {
            if (!confirm('Bu detayı silmek istediğinizden emin misiniz?')) return;
            const detayId = button.getAttribute('data-detay-id');
            try {
                const response = await fetch(`/atasozu-deyim/detay/${detayId}/sil/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                });
                const data = await response.json();
                if (data.success) {
                    location.reload();
                } else {
                    alert(data.error || 'Bir hata oluştu.');
                }
            } catch (error) {
                console.error('Detay silme hatası:', error);
                alert('Bir hata oluştu.');
            }
        });
    });

    // Atasözü/Deyim düzenleme
    document.querySelectorAll('[data-action="duzenle"]').forEach(button => {
        button.addEventListener('click', async () => {
            const tur = button.getAttribute('data-tur');
            const id = button.getAttribute('data-id');
            const modal = new bootstrap.Modal(document.getElementById('duzenleModal'));
            document.getElementById('duzenle-tur').value = tur;
            document.getElementById('duzenle-id').value = id;

            try {
                const response = await fetch(`/atasozu-deyim/${tur}/${id}/duzenle/`);
                const data = await response.json();
                if (data.success) {
                    document.getElementById('duzenle-kelime').value = data.form.kelime;
                    document.getElementById('duzenle-anlami').value = data.form.anlami;
                    document.getElementById('duzenle-ornek').value = data.form.ornek;
                    modal.show();
                } else {
                    alert(data.error || 'Bir hata oluştu.');
                }
            } catch (error) {
                console.error('Düzenleme verisi alınamadı:', error);
                alert('Bir hata oluştu.');
            }
        });
    });

    // Atasözü/Deyim düzenleme formu gönderimi
    const duzenleForm = document.getElementById('duzenle-form');
    if (duzenleForm) {
        duzenleForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const tur = formData.get('tur');
            const id = formData.get('id');
            try {
                const response = await fetch(`/atasozu-deyim/${tur}/${id}/duzenle/`, {
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
                    let errorMessage = 'Bir hata oluştu.';
                    if (data.errors) {
                        errorMessage = 'Hatalar:\n';
                        for (const [field, errors] of Object.entries(data.errors)) {
                            errors.forEach(error => {
                                errorMessage += `${field}: ${error}\n`;
                            });
                        }
                    }
                    alert(errorMessage);
                }
            } catch (error) {
                console.error('Düzenleme hatası:', error);
                alert('Bir hata oluştu.');
            }
        });
    }
}