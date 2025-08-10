import { getCsrfToken } from '../../like.js';

export function initKisiForm() {
    const form = document.getElementById('kisi-form');
    const errorDiv = document.getElementById('form-errors');
    const aiButton = document.getElementById('aiEnhanceBioButton');
    const aiToast = document.getElementById('aiEnhanceBioToast');
    const confirmButton = document.getElementById('confirmEnhanceBio');

    if (!form || !errorDiv) {
        console.warn('Kişi ekleme formu veya hata divi bulunamadı:', { form: !!form, errorDiv: !!errorDiv });
        return;
    }

    console.log('initKisiForm başlatılıyor, form bulundu:', form);

    // Quill düzenleyiciyi başlat
    if (typeof Quill !== 'undefined') {
        console.log('Quill.js bulundu, düzenleyici başlatılıyor...');
        const quill = new Quill('#biyografi-editor', {
            theme: 'snow',
            modules: {
                toolbar: [
                    ['bold', 'italic', 'underline'],
                    ['link'],
                    [{ 'list': 'ordered'}, { 'list': 'bullet' }]
                ]
            },
            placeholder: 'Biyografiyê li vir binivîse...',
            readOnly: false
        });
        console.log('Quill düzenleyici başlatıldı, yazılabilir mod aktif.');

        // Quill içeriği değiştiğinde log
        quill.on('text-change', () => {
            console.log('Quill içeriği değişti:', quill.root.innerHTML);
        });

        // Form gönderilmeden önce Quill içeriğini gizli input’a aktar
        const biyografiHidden = document.getElementById('biyografi-hidden');
        form.addEventListener('submit', () => {
            console.log('Form gönderiliyor, Quill içeriği aktarılıyor...');
            biyografiHidden.value = quill.root.innerHTML;
        });

        // AI Metin İşleme
        if (aiButton && aiToast && confirmButton) {
            console.log('AI metin işleme elementleri bulundu:', { aiButton: !!aiButton, aiToast: !!aiToast, confirmButton: !!confirmButton });
            aiButton.addEventListener('click', () => {
                console.log('Sihir değneği tıklandı, metin:', quill.root.innerHTML);
                if (!quill.root.innerHTML.trim() || quill.root.innerHTML === '<p><br></p>') {
                    console.warn('Metin boş, işleme iptal edildi.');
                    const errorToast = document.createElement('div');
                    errorToast.className = 'toast';
                    errorToast.innerHTML = `
                        <div class="toast-header">
                            <strong class="me-auto">Çewtî</strong>
                            <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
                        </div>
                        <div class="toast-body">
                            Ji kerema xwe pêşî nivîsekê binivîse.
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
                        body: `text=${encodeURIComponent(quill.root.innerHTML)}&language=ku`
                    });
                    console.log('AJAX yanıtı alındı:', response.status);
                    const data = await response.json();
                    console.log('Sunucu yanıtı:', data);
                    if (!response.ok) {
                        throw new Error(`Sunucu hatası: ${response.status} - ${data.error || 'Nenas çewtî'}`);
                    }
                    if (data.success) {
                        console.log('Metin işlendi:', data.enhanced_text);
                        quill.root.innerHTML = data.enhanced_text;
                        biyografiHidden.value = data.enhanced_text;
                        bootstrap.Toast.getInstance(aiToast).hide();
                    } else {
                        console.error('Metin işleme hatası:', data.error);
                        const errorToast = document.createElement('div');
                        errorToast.className = 'toast';
                        errorToast.innerHTML = `
                            <div class="toast-header">
                                <strong class="me-auto">Çewtî</strong>
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
                            <strong class="me-auto">Çewtî</strong>
                            <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
                        </div>
                        <div class="toast-body">
                            Pêvajoya nivîsê bi ser neket: ${error.message}
                        </div>
                    `;
                    document.querySelector('.toast-container').appendChild(errorToast);
                    bootstrap.Toast.getOrCreateInstance(errorToast).show();
                }
            });
        } else {
            console.error('AI metin işleme için gerekli elementler bulunamadı:', { aiButton: !!aiButton, aiToast: !!aiToast, confirmButton: !!confirmButton });
        }
    } else {
        console.error('Quill.js yüklenemedi, düzenleyici başlatılamadı.');
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        console.log('Form gönderimi engellendi, AJAX başlıyor...');
        errorDiv.classList.add('d-none');
        errorDiv.innerHTML = '';

        const formData = new FormData(form);
        try {
            const response = await fetch(form.action, {
                method: 'POST',
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
                body: formData
            });
            console.log('AJAX isteği gönderildi, yanıt bekleniyor...');
            const data = await response.json();
            console.log('AJAX yanıtı alındı:', data);
            if (data.success) {
                form.reset();
                console.log('Form sıfırlandı, alert gösteriliyor...');
                alert('Kes bi serkeftî hate zêdekirin!');
            } else {
                console.warn('Form hataları:', data.errors);
                errorDiv.classList.remove('d-none');
                for (const [field, message] of Object.entries(data.errors)) {
                    errorDiv.innerHTML += `<p>${message}</p>`;
                }
            }
        } catch (error) {
            console.error('Form gönderim hatası:', error);
            errorDiv.classList.remove('d-none');
            errorDiv.innerHTML = '<p>Çewtîyek çêbû, ji kerema xwe dîsa biceribîne.</p>';
        }
    });
    console.log('Form submit dinleyicisi bağlandı.');
}

export function initKisiLoader() {
    let offset = 20;
    let hasMore = true;
    let loading = false;

    const kisiList = document.getElementById('kisi-list');
    const loadingDiv = document.getElementById('loading');
    const errorDiv = document.getElementById('error-message');
    const filterForm = document.getElementById('filter-form');

    const loadMoreKisiler = async () => {
        if (loading || !hasMore) return;
        loading = true;
        loadingDiv.style.display = 'block';
        errorDiv.classList.add('d-none');

        const params = new URLSearchParams();
        params.append('offset', offset);
        if (filterForm) {
            const formData = new FormData(filterForm);
            if (formData.get('q')) params.append('q', formData.get('q'));
            if (formData.get('kategori')) params.append('kategori', formData.get('kategori'));
        }
        const harf = new URLSearchParams(window.location.search).get('harf');
        if (harf) params.append('harf', harf);

        try {
            const response = await fetch(`/kisi/liste-yukle/?${params.toString()}`, {
                method: 'GET',
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });
            if (!response.ok) throw new Error(`Ağ hatası: ${response.status}`);
            const data = await response.json();
            if (data.kisiler && Array.isArray(data.kisiler)) {
                const fragment = document.createDocumentFragment();
                data.kisiler.forEach(kisi => {
                    const kisiDiv = document.createElement('div');
                    kisiDiv.className = 'kisi-item mb-2';
                    kisiDiv.dataset.kisiId = kisi.id;
                    kisiDiv.innerHTML = `
                        <div class="d-flex justify-content-between align-items-start">
                            <a href="/kisi/detay/${kisi.id}/" class="text-decoration-none">
                                <strong>${kisi.ad}</strong>
                                <p class="text-muted small">${kisi.biyografi}</p>
                            </a>
                            ${kisi.is_owner ? `
                                <div class="dropdown">
                                    <button class="btn btn-link text-muted p-0" type="button" data-bs-toggle="dropdown">
                                        <i class="bi bi-three-dots"></i>
                                    </button>
                                    <ul class="dropdown-menu">
                                        <li>
                                            <button class="dropdown-item text-danger delete-kisi-btn" data-kisi-id="${kisi.id}">Jêbirin</button>
                                        </li>
                                    </ul>
                                </div>
                            ` : ''}
                        </div>
                    `;
                    fragment.appendChild(kisiDiv);
                });
                kisiList.appendChild(fragment);
                offset += 20;
                hasMore = data.has_more;

                document.querySelectorAll('.delete-kisi-btn').forEach(btn => {
                    btn.removeEventListener('click', handleDelete);
                    btn.addEventListener('click', handleDelete);
                });
            } else {
                hasMore = false;
            }
        } catch (error) {
            console.error('Kişi yükleme hatası:', error);
            errorDiv.classList.remove('d-none');
            errorDiv.textContent = 'Kes nehatin barkirin: ' + error.message;
        } finally {
            loading = false;
            loadingDiv.style.display = 'none';
        }
    };

    const handleDelete = async (e) => {
        const btn = e.target;
        if (!confirm('Ma hûn ji vê kesê jêbirinê piştrast in?')) return;
        try {
            const response = await fetch(`/kisi/sil/${btn.dataset.kisiId}/`, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
                }
            });
            const data = await response.json();
            if (data.success) {
                document.querySelector(`.kisi-item[data-kisi-id="${btn.dataset.kisiId}"]`).remove();
                alert('Kes bi serkeftî hate jêbirin!');
            } else {
                errorDiv.classList.remove('d-none');
                errorDiv.textContent = data.error || 'Di dema jêbirina kesê de çewtîyek çêbû.';
            }
        } catch (error) {
            console.error('Silme hatası:', error);
            errorDiv.classList.remove('d-none');
            errorDiv.textContent = 'Çewtîyek çêbû, ji kerema xwe dîsa biceribîne.';
        }
    };

    const scrollHandler = () => {
        if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 100 && !loading) {
            loadMoreKisiler();
        }
    };
    window.addEventListener('scroll', scrollHandler);

    if (filterForm) {
        filterForm.addEventListener('submit', (e) => {
            e.preventDefault();
            kisiList.innerHTML = '';
            offset = 0;
            hasMore = true;
            loadMoreKisiler();
        });
    }

    document.querySelectorAll('.delete-kisi-btn').forEach(btn => {
        btn.removeEventListener('click', handleDelete);
        btn.addEventListener('click', handleDelete);
    });
}