export function initKatkiLoader() {
    // Get all required elements
    const katkiList = document.getElementById('katki-list');
    
    // If we're not on the katki page, exit early
    if (!katkiList) {
        console.log('Katkı sayfasında değiliz, katkı yükleyici başlatılmıyor.');
        return;
    }
    
    const loadMoreBtn = document.getElementById('katki-load-more-btn');
    const katkiLoading = document.getElementById('katki-loading');
    const katkiErrorMessage = document.getElementById('katki-error-message');
    const turFilter = document.getElementById('katki-tur-filter');
    const liderlerList = document.getElementById('liderler-list');
    const katkiLiderlerLoading = document.getElementById('liderler-loading');
    const katkiLiderlerErrorMessage = document.getElementById('liderler-error-message');
    
    // Check for required elements
    const requiredElements = {
        loadMoreBtn,
        katkiLoading,
        katkiErrorMessage,
        turFilter
    };
    
    const missingElements = Object.entries(requiredElements)
        .filter(([_, element]) => !element)
        .map(([name]) => name);
    
    if (missingElements.length > 0) {
        console.error('Katkı için gerekli elementler bulunamadı:', missingElements.join(', '));
        return;
    }
    
    // Initialize state variables
    let katkiOffset = 0; // Start from 0 to load initial data
    let liderlerOffset = 10;
    let katkiHasMore = true;
    let liderlerHasMore = true;
    let katkiLoadingActive = false;
    let liderlerLoadingActive = false;
    let tur = '';
    
    // Safely format time since a given date
    const formatTimeSince = (dateStr) => {
        try {
            const now = new Date();
            const date = new Date(dateStr);
            if (isNaN(date.getTime())) throw new Error('Geçersiz tarih formatı');
            
            const seconds = Math.floor((now - date) / 1000);
            if (seconds < 60) return `${seconds} ${window.i18n?.t('time.seconds_ago') || 'saniye önce'}`;
            
            const minutes = Math.floor(seconds / 60);
            if (minutes < 60) return `${minutes} ${window.i18n?.t('time.minutes_ago') || 'dakika önce'}`;
            
            const hours = Math.floor(minutes / 60);
            if (hours < 24) return `${hours} ${window.i18n?.t('time.hours_ago') || 'saat önce'}`;
            
            const days = Math.floor(hours / 24);
            return `${days} ${window.i18n?.t('time.days_ago') || 'gün önce'}`;
        } catch (error) {
            console.error('Zaman formatlama hatası:', error);
            return window.i18n?.t('time.unknown') || 'Bilinmeyen zaman';
        }
    };
    
    // Sanitize HTML content to prevent XSS
    const sanitizeHTML = (str) => {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    };
    
    // Load katkilar data
    const loadKatkilar = async () => {
        if (!katkiHasMore || katkiLoadingActive) return;
        
        katkiLoadingActive = true;
        katkiLoading.style.display = 'block';
        loadMoreBtn.style.display = 'none';
        katkiErrorMessage.style.display = 'none';
        
        try {
            // Add a cache-busting parameter to prevent caching issues
            const timestamp = new Date().getTime();
            const response = await fetch(`/katki/load-more/?offset=${katkiOffset}&tur=${encodeURIComponent(tur)}&_=${timestamp}`, {
                method: 'GET',
                headers: { 
                    'X-Requested-With': 'XMLHttpRequest',
                    'Cache-Control': 'no-cache'
                },
                credentials: 'same-origin' // Include cookies for authentication
            });
            
            if (!response.ok) {
                throw new Error(`Ağ hatası: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (!data.katkilar || !Array.isArray(data.katkilar)) {
                throw new Error('Katkılar verisi eksik veya geçersiz format');
            }
            
            const container = katkiList.querySelector('.katki-container');
            if (!container) {
                throw new Error('Katkı container bulunamadı.');
            }
            
            // If this is the first load and container is empty, clear any "no contributions" message
            if (katkiOffset === 0 && container.innerHTML.includes(window.i18n?.t('katki.no_contributions') || 'Henüz katkı yok')) {
                container.innerHTML = '';
            }
            
            // Process each contribution
            data.katkilar.forEach(katki => {
                // Validate required fields
                if (!katki || typeof katki !== 'object') return;
                
                const div = document.createElement('div');
                div.className = 'card mb-2 katki-card';
                div.id = `katki-${sanitizeHTML(katki.id)}`;
                
                // Create safe HTML content
                const nickname = sanitizeHTML(katki.nickname || (window.i18n?.t('common.unknown') || 'Bilinmeyen'));
                const username = sanitizeHTML(katki.username || 'bilinmeyen');
                const katki_puani = parseInt(katki.katki_puani) || 0;
                const baslik = sanitizeHTML(katki.baslik || (window.i18n?.t('common.unknown') || 'Bilinmeyen'));
                const detay_url = katki.detay_url || '#';
                const formattedTime = formatTimeSince(katki.eklenme_tarihi);
                
                // Generate appropriate icon and text based on contribution type
                let typeIcon, typeText;
                switch(katki.tur) {
                    case 'sarki':
                        typeIcon = 'bi-music-note';
                        typeText = window.i18n?.t('katki.song_lyrics') || 'şarkı sözü';
                        break;
                    case 'kisi':
                        typeIcon = 'bi-person';
                        typeText = window.i18n?.t('katki.person') || 'kişi';
                        break;
                    case 'sozluk':
                        typeIcon = 'bi-book';
                        typeText = window.i18n?.t('katki.dictionary_word') || 'sözlük kelimesi';
                        break;
                    case 'atasozu':
                        typeIcon = 'bi-quote';
                        typeText = window.i18n?.t('katki.proverb') || 'atasözü';
                        break;
                    case 'deyim':
                        typeIcon = 'bi-quote';
                        typeText = window.i18n?.t('katki.idiom') || 'deyim';
                        break;
                    default:
                        typeIcon = 'bi-info-circle';
                        typeText = window.i18n?.t('katki.content') || 'içerik';
                }
                
                div.innerHTML = `
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start">
                            <p class="mb-1">
                                <strong>${nickname}</strong> 
                                <span class="text-muted">
                                    <a href="/profile/${username}" class="text-muted text-decoration-none">@${username}</a> · 
                                    <span class="badge bg-warning text-dark">⭐ ${katki_puani}</span> · 
                                    ${formattedTime}
                                </span>
                            </p>
                        </div>
                        <div class="katki-text">
                            <p><i class="bi ${typeIcon}"></i> ${window.i18n?.t('katki.user_added', {type: typeText}) || `Bu kullanıcı yeni ${typeText} ekledi`}: <a href="${detay_url}">${baslik}</a></p>
                        </div>
                    </div>
                `;
                
                container.appendChild(div);
            });
            
            // Update state
            katkiOffset += data.katkilar.length;
            katkiHasMore = data.has_more;
            loadMoreBtn.style.display = katkiHasMore ? 'block' : 'none';
            
        } catch (error) {
            console.error('Katkı yükleme hatası:', error);
            katkiErrorMessage.style.display = 'block';
            katkiErrorMessage.textContent = (window.i18n?.t('katki.load_error') || 'Katkılar yüklenemedi') + ': ' + error.message;
        } finally {
            katkiLoadingActive = false;
            katkiLoading.style.display = 'none';
        }
    };
    
    // Load liderler data
    const loadLiderler = async () => {
        // Only proceed if liderlerList exists
        if (!liderlerList || !katkiLiderlerLoading || !katkiLiderlerErrorMessage) {
            return;
        }
        
        if (!liderlerHasMore || liderlerLoadingActive) return;
        
        liderlerLoadingActive = true;
        katkiLiderlerLoading.style.display = 'block';
        katkiLiderlerErrorMessage.style.display = 'none';
        
        try {
            const timestamp = new Date().getTime();
            const response = await fetch(`/katki/load-more-liderler/?offset=${liderlerOffset}&_=${timestamp}`, {
                method: 'GET',
                headers: { 
                    'X-Requested-With': 'XMLHttpRequest',
                    'Cache-Control': 'no-cache'
                },
                credentials: 'same-origin'
            });
            
            if (!response.ok) {
                throw new Error(`Ağ hatası: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (!data.liderler || !Array.isArray(data.liderler)) {
                throw new Error('Liderler verisi eksik veya geçersiz format');
            }
            
            const ul = liderlerList.querySelector('ul');
            if (!ul) {
                throw new Error('Liderler listesi bulunamadı.');
            }
            
            data.liderler.forEach(lider => {
                if (!lider || typeof lider !== 'object') return;
                
                const li = document.createElement('li');
                li.className = 'mb-2';
                
                const nickname = sanitizeHTML(lider.nickname || (window.i18n?.t('common.unknown') || 'Bilinmeyen'));
                const username = sanitizeHTML(lider.username || 'bilinmeyen');
                const katki_puani = parseInt(lider.katki_puani) || 0;
                const profile_url = lider.profile_url || '#';
                
                li.innerHTML = `
                    <a href="${profile_url}" class="text-decoration-none">
                        <strong>${nickname}</strong> 
                        <span class="text-muted">@${username}</span> 
                        <span class="badge bg-warning text-dark">⭐ ${katki_puani}</span>
                    </a>
                `;
                
                ul.appendChild(li);
            });
            
            liderlerOffset += data.liderler.length;
            liderlerHasMore = data.has_more;
            
        } catch (error) {
            console.error('Liderler yükleme hatası:', error);
            katkiLiderlerErrorMessage.style.display = 'block';
            katkiLiderlerErrorMessage.textContent = (window.i18n?.t('katki.leaders_load_error') || 'Liderler yüklenemedi') + ': ' + error.message;
        } finally {
            liderlerLoadingActive = false;
            katkiLiderlerLoading.style.display = 'none';
        }
    };
    
    // Set up event listeners
    loadMoreBtn.addEventListener('click', loadKatkilar);
    
    turFilter.addEventListener('change', () => {
        tur = turFilter.value;
        katkiOffset = 0;
        katkiHasMore = true;
        
        const container = katkiList.querySelector('.katki-container');
        if (container) {
            container.innerHTML = '';
        }
        
        loadKatkilar();
    });
    
    // Implement infinite scroll with throttling
    let scrollTimeout;
    window.addEventListener('scroll', () => {
        if (scrollTimeout) {
            clearTimeout(scrollTimeout);
        }
        
        scrollTimeout = setTimeout(() => {
            const scrollPosition = window.innerHeight + window.scrollY;
            const documentHeight = document.body.offsetHeight;
            const scrollThreshold = documentHeight - 200; // Load earlier for better UX
            
            if (scrollPosition >= scrollThreshold) {
                if (katkiHasMore && !katkiLoadingActive) {
                    loadKatkilar();
                }
                
                if (liderlerHasMore && !liderlerLoadingActive && liderlerList) {
                    loadLiderler();
                }
            }
        }, 100); // Throttle to improve performance
    });
    
    // Format existing timestamps
    document.querySelectorAll('.time-since').forEach(el => {
        const date = el.getAttribute('data-date');
        if (date) {
            el.textContent = formatTimeSince(date);
        }
    });
    
    // Load initial data
    loadKatkilar();
    
    // If liderlerList exists, load initial liderler data
    if (liderlerList && katkiLiderlerLoading && katkiLiderlerErrorMessage) {
        loadLiderler();
    }
}