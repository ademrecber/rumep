// Atasözü ve Deyim Canlı Arama Modülü
export function initAtasozuDeyimLiveSearch() {
    let searchTimeout;
    
    const searchInput = document.getElementById('live-search');
    const searchResults = document.getElementById('search-results');
    const searchSpinner = document.querySelector('.search-spinner');
    const itemList = document.getElementById('item-list');
    
    if (!searchInput) return;
    
    searchInput.addEventListener('input', function() {
        const query = this.value.trim();
        
        clearTimeout(searchTimeout);
        
        if (query.length === 0) {
            searchResults.classList.remove('show');
            if (itemList) itemList.style.display = 'block';
            return;
        }
        
        if (query.length < 2) return;
        
        searchSpinner.classList.remove('d-none');
        
        searchTimeout = setTimeout(() => {
            performSearch(query);
        }, 300);
    });
    
    // Dışarı tıklayınca kapat
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
            searchResults.classList.remove('show');
            if (itemList) itemList.style.display = 'block';
        }
    });
    
    function performSearch(query) {
        // Hem atasözü hem deyim ara
        Promise.all([
            fetch(`/atasozu-deyim/ara/?sekme=atasozu&query=${encodeURIComponent(query)}`, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            }),
            fetch(`/atasozu-deyim/ara/?sekme=deyim&query=${encodeURIComponent(query)}`, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
        ])
        .then(responses => Promise.all(responses.map(r => r.json())))
        .then(([atasozuData, deyimData]) => {
            searchSpinner.classList.add('d-none');
            const allResults = [];
            
            // Atasözleri ekle
            if (atasozuData.success && atasozuData.items) {
                atasozuData.items.forEach(item => {
                    allResults.push({
                        type: 'atasozu',
                        type_display: 'ATASÖZÜ',
                        title: item.kelime,
                        description: item.anlami,
                        url: `/atasozu-deyim/atasozu/${item.id}/`
                    });
                });
            }
            
            // Deyimleri ekle
            if (deyimData.success && deyimData.items) {
                deyimData.items.forEach(item => {
                    allResults.push({
                        type: 'deyim',
                        type_display: 'DEYİM',
                        title: item.kelime,
                        description: item.anlami,
                        url: `/atasozu-deyim/deyim/${item.id}/`
                    });
                });
            }
            
            displaySearchResults(allResults);
        })
        .catch(error => {
            console.error('Arama hatası:', error);
            searchSpinner.classList.add('d-none');
        });
    }
    
    function displaySearchResults(results) {
        if (results.length === 0) {
            searchResults.innerHTML = '<div class="no-results">Sonuç bulunamadı</div>';
        } else {
            const html = results.map(item => `
                <div class="search-result-item" onclick="window.location.href='${item.url}'">
                    <div class="result-type ${item.type}">${item.type_display}</div>
                    <div class="result-title">${item.title}</div>
                    <div class="result-description">${item.description}</div>
                </div>
            `).join('');
            searchResults.innerHTML = html;
        }
        
        searchResults.classList.add('show');
        if (itemList) itemList.style.display = results.length > 0 ? 'none' : 'block';
    }
}