// sanitizeHTML fonksiyonunu global tanımlıyorum
const sanitizeHTML = (str) => {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
};

export function initSozlukArama() {
    const form = document.getElementById('sozluk-arama-form');
    const aramaInput = document.getElementById('arama-input');
    const turFiltresi = document.getElementById('tur-filtresi');
    const dilFiltresi = document.getElementById('dil-filtresi');
    const sonucListesi = document.getElementById('arama-sonuc-listesi');
    const loadingDiv = document.getElementById('loading');
    const errorDiv = document.getElementById('error-message');

    if (!form || !aramaInput || !turFiltresi || !sonucListesi || !loadingDiv || !errorDiv) {
        console.error('Arama formu elemanları eksik:', { form, aramaInput, turFiltresi, sonucListesi, loadingDiv, errorDiv });
        return;
    }

    let offset = 0;
    let hasMore = true;
    let loading = false;
    let lastQuery = '';

    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    const loadAramaSonuclari = async (reset = false) => {
        if (loading) return;
        
        const query = sanitizeHTML(aramaInput.value.trim());
        
        if (!query) {
            sonucListesi.innerHTML = '<p class="text-muted">Ji bo lêgerînê peyvekê binivîse.</p>';
            return;
        }
        
        if (!reset && query !== lastQuery) {
            reset = true;
        }
        
        lastQuery = query;
        
        if (reset) {
            offset = 0;
            sonucListesi.innerHTML = '';
            hasMore = true;
        }
        
        if (!hasMore && !reset) return;
        
        loading = true;
        loadingDiv.style.display = 'block';
        errorDiv.classList.add('d-none');

        try {
            console.log(`Arama isteği: /sozluk/ara/?q=${encodeURIComponent(query)}&tur=${encodeURIComponent(turFiltresi.value)}&dil=${encodeURIComponent(dilFiltresi?.value || '')}&offset=${offset}`);
            const response = await fetch(`/sozluk/ara/?q=${encodeURIComponent(query)}&tur=${encodeURIComponent(turFiltresi.value)}&dil=${encodeURIComponent(dilFiltresi?.value || '')}&offset=${offset}`, {
                method: 'GET',
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });
            if (!response.ok) throw new Error(`Ağ hatası: ${response.status}`);
            const data = await response.json();
            console.log('Arama yanıtı:', data);
            
            if (data.kelimeler && Array.isArray(data.kelimeler)) {
                if (data.kelimeler.length === 0 && reset) {
                    sonucListesi.innerHTML = '<p class="text-muted">Encam nehat dîtin.</p>';
                } else {
                    const fragment = document.createDocumentFragment();
                    data.kelimeler.forEach(kelime => {
                        const kelimeLi = document.createElement('li');
                        kelimeLi.className = 'kelime-item mb-1';
                        kelimeLi.dataset.kelimeId = kelime.id;
                        kelimeLi.innerHTML = `
                            <div class="d-flex justify-content-between align-items-start">
                                <a href="/sozluk/kelime/${kelime.id}/" class="text-decoration-none">
                                    <strong>${sanitizeHTML(kelime.kelime)}</strong>
                                    <p class="text-muted small">${sanitizeHTML(kelime.detay)}</p>
                                    <p class="text-muted small">Cure: ${sanitizeHTML(kelime.tur || 'Nenaskirî')}</p>
                                </a>
                                ${kelime.is_owner ? `
                                    <div class="dropdown">
                                        <button class="btn btn-link text-muted p-0" type="button" data-bs-toggle="dropdown">
                                            <i class="bi bi-three-dots"></i>
                                        </button>
                                        <ul class="dropdown-menu">
                                            <li>
                                                <button class="dropdown-item edit-kelime-btn" data-kelime-id="${kelime.id}" data-url="/sozluk/kelime-veri/${kelime.id}/" data-bs-toggle="modal" data-bs-target="#editKelimeModal">Sererast bike</button>
                                            </li>
                                            <li>
                                                <button class="dropdown-item text-danger delete-kelime-btn" data-kelime-id="${kelime.id}" data-url="/sozluk/kelime-sil/${kelime.id}/">Jê bibe</button>
                                            </li>
                                        </ul>
                                    </div>
                                ` : ''}
                            </div>
                        `;
                        fragment.appendChild(kelimeLi);
                    });
                    sonucListesi.appendChild(fragment);
                    offset += 20;
                    hasMore = data.has_more;

                    bindKelimeActions();
                }
            } else {
                hasMore = false;
            }
        } catch (error) {
            console.error('Arama hatası:', error);
            errorDiv.classList.remove('d-none');
            errorDiv.textContent = 'Di dema lêgerînê de çewtiyek çêbû, ji kerema xwe dîsa biceribîne.';
        } finally {
            loading = false;
            loadingDiv.style.display = 'none';
        }
    };

    const debouncedArama = debounce(() => loadAramaSonuclari(true), 250);

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        console.log('Arama formu submit edildi');
        loadAramaSonuclari(true);
    });

    turFiltresi.addEventListener('change', () => {
        console.log('Tür filtresi değişti:', turFiltresi.value);
        loadAramaSonuclari(true);
    });

    if (dilFiltresi) {
        dilFiltresi.addEventListener('change', () => {
            console.log('Dil filtresi değişti:', dilFiltresi.value);
            loadAramaSonuclari(true);
        });
    }

    aramaInput.addEventListener('input', (e) => {
        console.log('Arama input tetiklendi:', e.target.value);
        debouncedArama();
    });

    const scrollHandler = () => {
        if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 100 && !loading) {
            loadAramaSonuclari();
        }
    };
    window.addEventListener('scroll', scrollHandler);
}

export function initTumKelimeler(autoLoad = false) {
    const tumKelimelerBtn = document.getElementById('tum-kelimeler-btn');
    const sonucListesi = document.getElementById('arama-sonuc-listesi');
    const loadingDiv = document.getElementById('loading');
    const errorDiv = document.getElementById('error-message');

    if (!tumKelimelerBtn || !sonucListesi || !loadingDiv || !errorDiv) {
        console.error('Tüm kelimeler elemanları eksik:', { tumKelimelerBtn, sonucListesi, loadingDiv, errorDiv });
        return;
    }

    let offset = 0;
    let hasMore = true;
    let loading = false;
    let seenIds = new Set();

    const loadTumKelimeler = async (reset = false) => {
        if (loading || (!hasMore && !reset)) return;
        loading = true;
        loadingDiv.style.display = 'block';
        errorDiv.classList.add('d-none');

        if (reset) {
            offset = 0;
            hasMore = true;
            seenIds.clear();
            sonucListesi.innerHTML = '<p class="text-muted">Peyv tên barkirin...</p>';
        }

        try {
            console.log(`Tüm kelimeler isteği: /sozluk/tum-kelimeler/?offset=${offset}`);
            const response = await fetch(`/sozluk/tum-kelimeler/?offset=${offset}`, {
                method: 'GET',
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });
            if (!response.ok) throw new Error(`Ağ hatası: ${response.status}`);
            const data = await response.json();
            console.log('Tüm kelimeler yanıtı:', data);
            if (data.kelimeler && Array.isArray(data.kelimeler)) {
                if (data.kelimeler.length === 0 && reset) {
                    sonucListesi.innerHTML = '<p class="text-muted">Peyv nehat dîtin.</p>';
                    hasMore = false;
                    return;
                }

                const fragment = document.createDocumentFragment();
                let addedCount = 0;

                data.kelimeler.forEach(kelime => {
                    if (seenIds.has(kelime.id)) return;

                    seenIds.add(kelime.id);
                    addedCount++;

                    const kelimeLi = document.createElement('li');
                    kelimeLi.className = 'kelime-item mb-1';
                    kelimeLi.dataset.kelimeId = kelime.id;
                    kelimeLi.innerHTML = `
                        <div class="d-flex justify-content-between align-items-start">
                            <a href="/sozluk/kelime/${kelime.id}/" class="text-decoration-none">
                                <strong>${sanitizeHTML(kelime.kelime)}</strong>
                                <p class="text-muted small">${sanitizeHTML(kelime.detay)}</p>
                                <p class="text-muted small">Cure: ${sanitizeHTML(kelime.tur || 'Nenaskirî')}</p>
                            </a>
                            ${kelime.is_owner ? `
                                <div class="dropdown">
                                    <button class="btn btn-link text-muted p-0" type="button" data-bs-toggle="dropdown">
                                        <i class="bi bi-three-dots"></i>
                                    </button>
                                    <ul class="dropdown-menu">
                                        <li>
                                            <button class="dropdown-item edit-kelime-btn" data-kelime-id="${kelime.id}" data-url="/sozluk/kelime-veri/${kelime.id}/" data-bs-toggle="modal" data-bs-target="#editKelimeModal">Sererast bike</button>
                                        </li>
                                        <li>
                                            <button class="dropdown-item text-danger delete-kelime-btn" data-kelime-id="${kelime.id}" data-url="/sozluk/kelime-sil/${kelime.id}/">Jê bibe</button>
                                        </li>
                                    </ul>
                                </div>
                            ` : ''}
                        </div>
                    `;
                    fragment.appendChild(kelimeLi);
                });

                if (reset) sonucListesi.innerHTML = '';
                if (addedCount > 0) {
                    sonucListesi.appendChild(fragment);
                }
                offset += 20;
                hasMore = data.has_more && addedCount > 0;

                bindKelimeActions();
            } else {
                hasMore = false;
            }
        } catch (error) {
            console.error('Tüm kelimeler yükleme hatası:', error);
            errorDiv.classList.remove('d-none');
            errorDiv.textContent = 'Di dema barkirina peyvan de çewtiyek çêbû, ji kerema xwe dîsa biceribîne.';
        } finally {
            loading = false;
            loadingDiv.style.display = 'none';
        }
    };

    tumKelimelerBtn.addEventListener('click', () => {
        loadTumKelimeler(true);
    });

    if (autoLoad) {
        loadTumKelimeler(true);
    }

    const scrollHandler = () => {
        if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 100 && !loading && hasMore) {
            loadTumKelimeler();
        }
    };
    window.addEventListener('scroll', scrollHandler);
}

export function bindKelimeActions() {
    const errorDiv = document.getElementById('error-message') || document.createElement('div');

    document.querySelectorAll('.delete-kelime-btn').forEach(btn => {
        btn.removeEventListener('click', handleDeleteKelime);
        btn.addEventListener('click', handleDeleteKelime, { once: true });
    });

    document.querySelectorAll('.edit-kelime-btn').forEach(btn => {
        btn.removeEventListener('click', handleEditKelime);
        btn.addEventListener('click', handleEditKelime, { once: true });
    });

    document.querySelectorAll('.delete-detay-btn').forEach(btn => {
        btn.removeEventListener('click', handleDeleteDetay);
        btn.addEventListener('click', handleDeleteDetay, { once: true });
    });

    document.querySelectorAll('.edit-detay-btn').forEach(btn => {
        btn.removeEventListener('click', handleEditDetay);
        btn.addEventListener('click', handleEditDetay, { once: true });
    });

    async function handleDeleteKelime(e) {
        const btn = e.currentTarget;
        const url = btn.getAttribute('data-url');
        if (!url) {
            console.error('Silme URL’si eksik:', btn);
            errorDiv.classList.remove('d-none');
            errorDiv.textContent = 'Ji bo kiryara jêbirinê URL-ya pêwîst nehat dîtin.';
            return;
        }
        if (!confirm(window.i18n?.t('sozluk.confirm_delete_word') || 'Bu kelimeyi silmek istediğinizden emin misiniz?')) return;
        try {
            console.log(`Silme isteği: ${url}`);
            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
            if (!csrfToken) {
                throw new Error('CSRF token bulunamadı. Lütfen sayfayı yenileyin.');
            }
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken
                }
            });
            const data = await response.json();
            console.log('Silme yanıtı:', data);
            if (data.success) {
                alert(window.i18n?.t('sozluk.word_deleted_success') || 'Kelime başarıyla silindi!');
                window.location.href = '/sozluk/';
            } else {
                errorDiv.classList.remove('d-none');
                errorDiv.textContent = 'Di dema jêbirina peyvê de çewtiyek çêbû, ji kerema xwe dîsa biceribîne.';
            }
        } catch (error) {
            console.error('Kelime silme hatası:', error);
            errorDiv.classList.remove('d-none');
            errorDiv.textContent = 'Çewtiyek çêbû, ji kerema xwe dîsa biceribîne.';
        }
    }

    async function handleEditKelime(e) {
        const btn = e.currentTarget;
        const kelimeId = btn.dataset.kelimeId;
        const url = btn.getAttribute('data-url');
        if (!url) {
            console.error('Düzenleme verisi URL’si eksik:', btn);
            alert('Ji bo kiryara sererastkirinê URL-ya pêwîst nehat dîtin.');
            return;
        }
        try {
            console.log(`Düzenleme verisi isteği: ${url}`);
            const response = await fetch(url, {
                method: 'GET',
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });
            const data = await response.json();
            console.log('Düzenleme verisi yanıtı:', data);
            if (data.success) {
                const form = document.getElementById('edit-kelime-form');
                form.action = `/sozluk/kelime-duzenle/${kelimeId}/`;
                form.querySelector('#kelime').value = sanitizeHTML(data.kelime) || '';
                form.querySelector('#detay').value = sanitizeHTML(data.detay) || '';
                form.querySelector('#tur').value = sanitizeHTML(data.tur) || '';
            } else {
                alert('Daneyên peyvê nehatin barkirin.');
            }
        } catch (error) {
            console.error('Kelime verisi yükleme hatası:', error);
            alert('Daneyên peyvê nehatin barkirin.');
        }
    }

    async function handleDeleteDetay(e) {
        const btn = e.currentTarget;
        const url = btn.getAttribute('data-url');
        if (!url) {
            console.error('Detay silme URL’si eksik:', btn);
            errorDiv.classList.remove('d-none');
            errorDiv.textContent = 'Ji bo kiryara jêbirina detayê URL-ya pêwîst nehat dîtin.';
            return;
        }
        if (!confirm(window.i18n?.t('sozluk.confirm_delete_detail') || 'Bu detayı silmek istediğinizden emin misiniz?')) return;
        try {
            console.log(`Detay silme isteği: ${url}`);
            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
            if (!csrfToken) {
                throw new Error('CSRF token bulunamadı. Lütfen sayfayı yenileyin.');
            }
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken
                }
            });
            const data = await response.json();
            console.log('Detay silme yanıtı:', data);
            if (data.success) {
                document.querySelector(`.detay-item[data-detay-id="${btn.dataset.detayId}"]`)?.remove();
                alert(window.i18n?.t('sozluk.detail_deleted_success') || 'Detay başarıyla silindi!');
            } else {
                errorDiv.classList.remove('d-none');
                errorDiv.textContent = 'Di dema jêbirina detayê de çewtiyek çêbû, ji kerema xwe dîsa biceribîne.';
            }
        } catch (error) {
            console.error('Detay silme hatası:', error);
            errorDiv.classList.remove('d-none');
            errorDiv.textContent = 'Çewtiyek çêbû, ji kerema xwe dîsa biceribîne.';
        }
    }

    async function handleEditDetay(e) {
        const btn = e.currentTarget;
        const detayId = btn.dataset.detayId;
        const url = btn.getAttribute('data-url');
        if (!url) {
            console.error('Detay verisi URL’si eksik:', btn);
            alert('Ji bo kiryara sererastkirina detayê URL-ya pêwîst nehat dîtin.');
            return;
        }
        try {
            console.log(`Detay verisi isteği: ${url}`);
            const response = await fetch(url, {
                method: 'GET',
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });
            const data = await response.json();
            console.log('Detay verisi yanıtı:', data);
            if (data.success) {
                const form = document.getElementById('edit-detay-form');
                form.action = `/sozluk/detay-duzenle/${detayId}/`;
                form.querySelector('#detay').value = sanitizeHTML(data.detay) || '';
            } else {
                alert('Daneyên detayê nehatin barkirin.');
            }
        } catch (error) {
            console.error('Detay verisi yükleme hatası:', error);
            alert('Daneyên detayê nehatin barkirin.');
        }
    }
}