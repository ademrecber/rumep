export function initSarkiAlbumActions() {
    console.log("initSarkiAlbumActions çalıştı."); // Hata ayıklama için log ekledik

    // Albüm silme işlemi
    const forms = document.querySelectorAll('.album-sil-form');
    console.log("Bulunan albüm silme formları:", forms); // Hata ayıklama için log

    forms.forEach(form => {
        const button = form.querySelector('.album-sil-btn');
        console.log("Albüm silme butonu bulundu:", button); // Hata ayıklama için log

        button.addEventListener('click', async (e) => {
            e.preventDefault(); // Formun varsayılan gönderimini engelle
            if (!confirm('Bu albümü silmek istediğinizden emin misiniz?')) return;
            const albumId = form.getAttribute('data-album-id');
            try {
                const response = await fetch(`/sarki/album-sil/${albumId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': form.querySelector('[name=csrfmiddlewaretoken]').value,
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });
                const data = await response.json();
                if (data.success) {
                    location.reload(); // Sayfayı yenile
                } else {
                    alert(data.error || 'Bir hata oluştu.');
                }
            } catch (error) {
                console.error('Albüm silme hatası:', error);
                alert('Bir hata oluştu.');
            }
        });
    });

    // Albüm değiştirme işlemi
    const albumDegistirButtons = document.querySelectorAll('.album-degistir-btn');
    const albumDegistirForm = document.getElementById('album-degistir-form');
    const albumSelect = document.getElementById('album-select');

    albumDegistirButtons.forEach(button => {
        button.addEventListener('click', async (e) => {
            e.preventDefault();
            const sarkiId = button.getAttribute('data-sarki-id');
            document.getElementById('sarki-id').value = sarkiId;

            try {
                const response = await fetch(`/sarki/album-degistir-veri/${sarkiId}/`, {
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });
                const data = await response.json();
                if (data.success) {
                    // Albüm seçeneklerini doldur
                    albumSelect.innerHTML = '';
                    data.data.albumler.forEach(album => {
                        const option = document.createElement('option');
                        option.value = album.id;
                        option.textContent = album.ad;
                        if (album.id === data.data.album_id) {
                            option.selected = true;
                        }
                        albumSelect.appendChild(option);
                    });
                    // Modal'ı göster
                    const modal = new bootstrap.Modal(document.getElementById('albumDegistirModal'));
                    modal.show();
                } else {
                    alert(data.error || 'Albüm bilgileri alınamadı.');
                }
            } catch (error) {
                console.error('Albüm bilgileri alma hatası:', error);
                alert('Bir hata oluştu.');
            }
        });
    });

    albumDegistirForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const sarkiId = document.getElementById('sarki-id').value;
        const albumId = albumSelect.value;

        try {
            const response = await fetch(`/sarki/album-degistir/${sarkiId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': albumDegistirForm.querySelector('[name=csrfmiddlewaretoken]').value,
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: `album=${albumId}`
            });
            const data = await response.json();
            if (data.success) {
                location.reload(); // Sayfayı yenile
            } else {
                alert(data.error || 'Albüm değiştirilemedi.');
            }
        } catch (error) {
            console.error('Albüm değiştirme hatası:', error);
            alert('Bir hata oluştu.');
        }
    });
}