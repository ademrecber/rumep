export function initProfile() {
    console.log('initProfile başlatıldı');

    const getCsrfToken = () => {
        const token = document.querySelector('meta[name="csrf-token"]')?.content || document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        if (!token) {
            console.error('CSRF token bulunamadı');
            return null;
        }
        return token;
    };

    const initialize = () => {
        console.log('DOM yüklendi, initProfile çalışıyor');

        const visibilityBtn = document.querySelector('.visibility-btn');
        console.log('visibility-btn elementi:', visibilityBtn);
        if (visibilityBtn) {
            visibilityBtn.addEventListener('click', async (e) => {
                e.preventDefault();
                console.log('Görünürlük butonuna tıklandı');
                const csrfToken = getCsrfToken();
                if (!csrfToken) {
                    console.error('CSRF token bulunamadı');
                    alert('Görünürlük ayarları yüklenemedi: CSRF token eksik.');
                    return;
                }

                try {
                    console.log('GET isteği gönderiliyor: /update-visibility/');
                    const response = await fetch('/update-visibility/', {
                        method: 'GET',
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest'
                        }
                    });

                    console.log('GET yanıtı alındı, durum:', response.status);
                    const data = await response.json();
                    if (!response.ok) {
                        console.error(`Sunucu hatası: ${response.status}, Yanıt:`, data);
                        alert(`Görünürlük ayarları yüklenemedi: ${data.errors || 'Sunucu hatası'}`);
                        return;
                    }

                    console.log('Ayarlar yanıtı:', data);

                    const postsVisible = document.getElementById('postsVisible');
                    const critiquesVisible = document.getElementById('critiquesVisible');
                    const commentsVisible = document.getElementById('commentsVisible');
                    console.log('Checkbox elementleri:', { postsVisible, critiquesVisible, commentsVisible });

                    if (postsVisible && critiquesVisible && commentsVisible) {
                        postsVisible.checked = data.posts_visible ?? false;
                        critiquesVisible.checked = data.critiques_visible ?? false;
                        commentsVisible.checked = data.comments_visible ?? false;
                        console.log('Ayarlar yüklendi:', data);
                    } else {
                        console.error('Checkbox elementleri bulunamadı:', { postsVisible, critiquesVisible, commentsVisible });
                        alert('Görünürlük ayarları yüklenemedi: Form elemanları eksik.');
                    }
                } catch (error) {
                    console.error('Ayarlar yükleme hatası:', error.message, 'Tam hata:', error);
                    alert('Görünürlük ayarları yüklenemedi: Sunucu hatası.');
                }
            });
        } else {
            console.warn('visibility-btn bulunamadı, DOM yüklendi mi?');
        }

        const visibilityForm = document.getElementById('visibilityForm');
        console.log('visibilityForm elementi:', visibilityForm);
        if (visibilityForm) {
            visibilityForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                console.log('Görünürlük formu gönderiliyor');
                const csrfToken = getCsrfToken();
                if (!csrfToken) {
                    console.error('CSRF token bulunamadı');
                    alert('Görünürlük ayarları kaydedilemedi: CSRF token eksik.');
                    return;
                }

                const formData = new FormData();
                formData.append('csrfmiddlewaretoken', csrfToken);

                const postsVisible = document.getElementById('postsVisible');
                const critiquesVisible = document.getElementById('critiquesVisible');
                const commentsVisible = document.getElementById('commentsVisible');

                formData.append('posts_visible', postsVisible.checked ? 'on' : 'off');
                formData.append('critiques_visible', critiquesVisible.checked ? 'on' : 'off');
                formData.append('comments_visible', commentsVisible.checked ? 'on' : 'off');

                const formDataObj = Object.fromEntries(formData);
                console.log('Görünürlük kaydediliyor:', formDataObj);

                try {
                    console.log('POST isteği gönderiliyor: /update-visibility/');
                    const response = await fetch('/update-visibility/', {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': csrfToken,
                            'X-Requested-With': 'XMLHttpRequest'
                        },
                        body: formData
                    });

                    console.log('POST yanıtı alındı, durum:', response.status);
                    const data = await response.json();
                    if (!response.ok) {
                        console.error(`Sunucu hatası: ${response.status}, Yanıt:`, data);
                        alert(`Görünürlük ayarları kaydedilemedi: ${data.errors || 'Sunucu hatası'}`);
                        return;
                    }

                    if (data.success) {
                        postsVisible.checked = data.posts_visible ?? false;
                        critiquesVisible.checked = data.critiques_visible ?? false;
                        commentsVisible.checked = data.comments_visible ?? false;
                        console.log('Ayarlar güncellendi:', data);

                        const modal = bootstrap.Modal.getInstance(document.getElementById('visibilityModal'));
                        if (modal) {
                            modal.hide();
                        } else {
                            console.warn('Bootstrap Modal bulunamadı');
                        }
                        alert('Görünürlük ayarları başarıyla kaydedildi.');
                        console.log('Görünürlük güncellendi:', data);
                    } else {
                        console.error('Görünürlük kaydetme hatası:', data.errors || data.error || 'Hata mesajı sağlanmadı');
                        alert(`Görünürlük ayarları kaydedilemedi: ${data.errors || data.error || 'Hata mesajı sağlanmadı'}`);
                    }
                } catch (error) {
                    console.error('Görünürlük kaydetme hatası:', error.message, 'Tam hata:', error);
                    alert('Görünürlük ayarları kaydedilemedi: Sunucu hatası.');
                }
            });
        } else {
            console.warn('visibilityForm bulunamadı, DOM yüklendi mi?');
        }
    };

    const visibilityModal = document.getElementById('visibilityModal');
    if (visibilityModal) {
        visibilityModal.addEventListener('shown.bs.modal', () => {
            initialize();
        });
    } else {
        // Eğer modal yoksa, DOM yüklendiğinde çalıştır
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', initialize);
        } else {
            initialize();
        }
    }
}