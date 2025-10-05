// Utility functions
const sanitizeHTML = (str) => {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
};

const createKelimeTemplate = ({ id, kelime, detay, is_owner }) => `
    <div class="d-flex justify-content-between align-items-start">
        <a href="/sozluk/kelime/${id}/" class="text-decoration-none">
            <strong>${sanitizeHTML(kelime)}</strong>
            <p class="text-muted small">${sanitizeHTML(detay)}</p>
        </a>
        ${is_owner ? `
            <div class="dropdown">
                <button class="btn btn-link text-muted p-0" type="button" data-bs-toggle="dropdown">
                    <i class="bi bi-three-dots"></i>
                </button>
                <ul class="dropdown-menu">
                    <li>
                        <button class="dropdown-item edit-kelime-btn" data-kelime-id="${id}" data-bs-toggle="modal" data-bs-target="#editKelimeModal">${window.i18n?.t('common.edit') || 'Düzenle'}</button>
                    </li>
                    <li>
                        <button class="dropdown-item text-danger delete-kelime-btn" data-kelime-id="${id}">${window.i18n?.t('common.delete') || 'Sil'}</button>
                    </li>
                </ul>
            </div>
        ` : ''}
    </div>
`;

// Throttle function for performance optimization
const throttle = (func, limit) => {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
};

// Error handling utility
const handleError = (error, errorDiv, customMessage = '') => {
    console.error(error);
    errorDiv.classList.remove('d-none');
    errorDiv.innerHTML = `<p>${customMessage || (window.i18n?.t('common.error_try_again') || 'Bir hata oluştu, lütfen tekrar deneyin.')}</p>`;
};

// Form submission handler with optimized error handling
export async function initSozlukForm() {
    const form = document.getElementById('sozluk-form');
    const errorDiv = document.getElementById('form-errors');
    if (!form || !errorDiv) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        errorDiv.classList.add('d-none');
        errorDiv.innerHTML = '';

        try {
            const formData = new FormData(form);
            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
            if (!csrfToken) {
                throw new Error('CSRF token bulunamadı. Lütfen sayfayı yenileyin.');
            }
            const response = await fetch(form.action, {
                method: 'POST',
                headers: { 
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken
                },
                body: formData
            });

            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const data = await response.json();

            if (data.success) {
                form.reset();
                try {
                    const module = await import("./sozluk_search.js");
                    await module.initTumKelimeler(true);
                } catch (importError) {
                    handleError(importError, errorDiv, '${window.i18n?.t('sozluk.word_list_update_error') || 'Kelime listesi güncellenemedi.'}');
                }
            } else {
                errorDiv.classList.remove('d-none');
                errorDiv.innerHTML = '<p>${window.i18n?.t('sozluk.word_add_error') || 'Kelime eklenirken hata oluştu, lütfen tekrar deneyin.'}</p>';
            }
        } catch (error) {
            handleError(error, errorDiv);
        }
    });
}

// Optimized infinite scroll implementation
export function initSozlukLoader(harf) {
    const state = {
        offset: 20,
        hasMore: true,
        loading: false,
        cache: new Map() // Cache for loaded items
    };

    const elements = {
        kelimeList: document.getElementById('kelime-list'),
        loadingDiv: document.getElementById('loading'),
        errorDiv: document.getElementById('error-message')
    };

    if (!Object.values(elements).every(Boolean)) return;

    const loadMoreKelimeler = async () => {
        if (state.loading || !state.hasMore) return;
        
        state.loading = true;
        elements.loadingDiv.style.display = 'block';
        elements.errorDiv.classList.add('d-none');

        try {
            const cacheKey = `${harf}-${state.offset}`;
            if (state.cache.has(cacheKey)) {
                const cachedData = state.cache.get(cacheKey);
                renderKelimeler(cachedData);
                return;
            }

            const response = await fetch(`/sozluk/harf-yukle/?harf=${harf}&offset=${state.offset}`, {
                method: 'GET',
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });

            if (!response.ok) throw new Error(`Ağ hatası: ${response.status}`);
            const data = await response.json();

            state.cache.set(cacheKey, data);
            renderKelimeler(data);

        } catch (error) {
            handleError(error, elements.errorDiv, '${window.i18n?.t('sozluk.word_load_error') || 'Kelimeler yüklenirken hata oluştu.'}');
        } finally {
            state.loading = false;
            elements.loadingDiv.style.display = 'none';
        }
    };

    const renderKelimeler = (data) => {
        if (!data.kelimeler?.length) {
            state.hasMore = false;
            return;
        }

        const fragment = document.createDocumentFragment();
        data.kelimeler.forEach(kelime => {
            const kelimeDiv = document.createElement('div');
            kelimeDiv.className = 'kelime-item mb-1';
            kelimeDiv.dataset.kelimeId = kelime.id;
            kelimeDiv.innerHTML = createKelimeTemplate(kelime);
            fragment.appendChild(kelimeDiv);
        });

        elements.kelimeList.appendChild(fragment);
        state.offset += 20;
        state.hasMore = data.has_more;

        import("./sozluk_search.js")
            .then(module => module.bindKelimeActions())
            .catch(error => {
                console.error('Action binding failed:', error);
                handleError(error, elements.errorDiv, '${window.i18n?.t('sozluk.action_binding_error') || 'Eylem bağlama başarısız oldu.'}');
            });
    };

    const scrollHandler = throttle(() => {
        const { scrollY, innerHeight } = window;
        const { scrollHeight } = document.documentElement;
        
        if (scrollHeight - (scrollY + innerHeight) < 200 && !state.loading) {
            loadMoreKelimeler();
        }
    }, 150);

    window.addEventListener('scroll', scrollHandler, { passive: true });

    return () => window.removeEventListener('scroll', scrollHandler);
}