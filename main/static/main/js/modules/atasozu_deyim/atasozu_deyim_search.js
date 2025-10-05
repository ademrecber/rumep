export function initAtasozuDeyimArama() {
    console.log("initAtasozuDeyimArama çalıştı."); // Hata ayıklama için log
    const searchForm = document.getElementById('atasozu-deyim-arama-form');
    const searchInput = document.querySelector('input[name="query"]');
    const searchResults = document.getElementById('search-results');
    const sekmeInput = document.querySelector('input[name="sekme"]');

    if (!searchForm || !searchInput || !searchResults || !sekmeInput) {
        console.error("Gerekli elementler eksik:", { searchForm, searchInput, searchResults, sekmeInput });
        return;
    }

    const sekme = sekmeInput.value;
    console.log("Sekme değeri:", sekme); // Hata ayıklama için log

    // Debounce fonksiyonu: Sık sık arama isteği gönderimini engeller
    const debounce = (func, delay) => {
        let timeoutId;
        return (...args) => {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => func(...args), delay);
        };
    };

    const performSearch = async (query, tarih_baslangic, tarih_bitis, kullanici) => {
        try {
            const response = await fetch(`/atasozu-deyim/ara/?sekme=${sekme}&query=${encodeURIComponent(query)}&tarih_baslangic=${tarih_baslangic}&tarih_bitis=${tarih_bitis}&kullanici=${encodeURIComponent(kullanici)}`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            const data = await response.json();
            if (data.success) {
                searchResults.innerHTML = '';
                if (data.items.length === 0) {
                    searchResults.innerHTML = `<p class="text-muted">${window.i18n?.t('atasozu_deyim.no_results') || 'Sonuç bulunamadı.'}</p>`;
                } else {
                    data.items.forEach(item => {
                        const itemDiv = document.createElement('div');
                        itemDiv.classList.add('item', 'mb-3');
                        itemDiv.innerHTML = `
                            <h5><a href="/atasozu-deyim/${sekme}/${item.id}/" class="text-decoration-none">${item.kelime}</a></h5>
                            <p>${item.anlami.substring(0, 100)}${item.anlami.length > 100 ? '...' : ''}</p>
                            <small class="text-muted">${window.i18n?.t('atasozu_deyim.added_by') || 'Ekleyen'}: ${item.kullanici} - ${new Date(item.eklenme_tarihi).toLocaleDateString('tr-TR')}</small>
                        `;
                        searchResults.appendChild(itemDiv);
                    });
                }
            } else {
                searchResults.innerHTML = `<p class="text-muted">${window.i18n?.t('atasozu_deyim.search_error') || 'Bir hata oluştu, lütfen tekrar deneyin.'}</p>`;
            }
        } catch (error) {
            console.error('Arama hatası:', error);
            searchResults.innerHTML = `<p class="text-muted">${window.i18n?.t('atasozu_deyim.search_error') || 'Bir hata oluştu, lütfen tekrar deneyin.'}</p>`;
        }
    };

    // Debounce ile arama fonksiyonunu optimize et
    const debouncedSearch = debounce((query, tarih_baslangic, tarih_bitis, kullanici) => {
        performSearch(query, tarih_baslangic, tarih_bitis, kullanici);
    }, 300);

    // Input değişikliğini dinle
    searchInput.addEventListener('input', (e) => {
        const formData = new FormData(searchForm);
        const query = formData.get('query');
        const tarih_baslangic = formData.get('tarih_baslangic');
        const tarih_bitis = formData.get('tarih_bitis');
        const kullanici = formData.get('kullanici');

        console.log("Arama parametreleri:", { query, tarih_baslangic, tarih_bitis, kullanici }); // Hata ayıklama için log

        if (query.length > 0) {
            debouncedSearch(query, tarih_baslangic, tarih_bitis, kullanici);
        } else {
            searchResults.innerHTML = ''; // Arama metni boşsa sonuçları temizle
        }
    });

    // Form gönderimini de destekleyelim
    searchForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const formData = new FormData(searchForm);
        const query = formData.get('query');
        const tarih_baslangic = formData.get('tarih_baslangic');
        const tarih_bitis = formData.get('tarih_bitis');
        const kullanici = formData.get('kullanici');

        performSearch(query, tarih_baslangic, tarih_bitis, kullanici);
    });
}