import { initLikes, getCsrfToken } from "./like.js";
import { initCopyLink } from "./copy-link.js";

// Client-side function to render emoji shortcodes to img tags
function renderEmojis(text) {
    if (!text) return text;
    
    // Replace emoji shortcodes with img tags
    // This mimics the server-side render_emojis function
    return text.replace(/:emoji\d+:/g, function(match) {
        const name = match.replace(/:/g, '');
        return `<img src="/static/emojis/${name}.svg" alt="${name}" width="20">`;
    });
}

async function loadMorePopularPosts() {
    if (window.loading || !window.hasMore) return;

    window.loading = true;
    const loadingDiv = document.getElementById('loading');
    const loadMoreBtn = document.getElementById('load-more-btn');
    const errorMessage = document.getElementById('error-message');
    
    if (loadingDiv) loadingDiv.style.display = 'block';
    if (loadMoreBtn) loadMoreBtn.style.display = 'none';
    if (errorMessage) errorMessage.style.display = 'none';

    try {
        const csrfToken = getCsrfToken();
        if (!csrfToken) throw new Error('CSRF token bulunamadı');
        console.log('CSRF Token:', csrfToken);

        const url = `/load-more-popular/?period=${window.currentPeriod}&offset=${window.offset}`;
        console.log(`Yükleniyor: url=${url}`);

        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrfToken
            }
        });

        if (!response.ok) throw new Error(`Ağ hatası: ${response.status}`);

        const data = await response.json();
        console.log('Gelen veri:', data);

        if (data.posts && Array.isArray(data.posts)) {
            const fragment = document.createDocumentFragment();
            data.posts.forEach(post => {
                const liked = post.liked ? 'liked' : '';
                const bookmarked = post.bookmarked ? 'bookmarked' : '';
                const isOwner = post.is_owner !== undefined ? post.is_owner : false;
                const postDiv = document.createElement('div');
                postDiv.className = 'card mb-2 topic-card fade-in border-0';
                postDiv.style.boxShadow = 'none !important';
                postDiv.id = `post-${post.id}`;
                const totalLines = post.text.split(/(\n)/).length;
                
                // Process emoji shortcodes in post text
                const processedText = renderEmojis(post.text);
                
                postDiv.innerHTML = `
                    <div class="card-body">
                        <a href="/topic/${post.short_id}/" class="text-decoration-none text-dark">
                            <h5 class="card-title mb-2">${post.title}</h5>
                        </a>
                        <!-- Kategori Badges -->
                        <div class="mb-2">
                            ${post.categories ? post.categories.map(cat => `<span class="badge rounded-pill bg-primary me-1 mb-1" style="font-size: 0.7rem;">${cat.name}</span>`).join('') : ''}
                        </div>

                        ${post.text ? `
                        <div class="first-entry-preview text-muted mb-2" style="font-size: 0.85rem; color: #6c757d;">
                            ${processedText.length > 790 ? 
                                processedText.substring(0, 790) + '<a href="/topic/' + post.short_id + '/" class="text-primary text-decoration-none">...devamını gör</a>' : 
                                processedText
                            }
                        </div>
                        ` : ''}

                        <!-- Desktop Layout -->
                        <div class="d-none d-md-flex justify-content-between align-items-end mt-3">
                            <div class="vote-buttons d-flex gap-1 align-items-center">
                                <button class="btn btn-link p-0 vote-btn" data-topic-slug="${post.short_id}" data-vote-type="up">
                                    <i class="bi bi-arrow-up"></i>
                                </button>
                                <span class="vote-score fw-bold" style="font-size: 0.9rem;">${post.upvotes - post.downvotes}</span>
                                <button class="btn btn-link p-0 vote-btn" data-topic-slug="${post.short_id}" data-vote-type="down">
                                    <i class="bi bi-arrow-down"></i>
                                </button>
                                <small class="text-muted ms-2">${post.comment_count} entry</small>
                                ${isOwner ? `
                                    <button class="btn btn-link p-0 ms-2 topic-bookmark-btn text-muted" data-topic-slug="${post.short_id}">
                                        <i class="bi bi-bookmark"></i>
                                    </button>
                                ` : ''}
                                <div class="dropdown d-inline ms-2">
                                    <button class="btn btn-link p-0 text-muted" type="button" data-bs-toggle="dropdown">
                                        <i class="bi bi-share"></i>
                                    </button>
                                    <ul class="dropdown-menu share-dropdown">
                                        <li>
                                            <button class="dropdown-item share-btn share-twitter twitter" data-topic-code="${post.short_id}">
                                                <i class="bi bi-twitter share-icon"></i>
                                                Twitter'da Paylaş
                                            </button>
                                        </li>
                                        <li>
                                            <button class="dropdown-item share-btn share-whatsapp whatsapp" data-topic-code="${post.short_id}">
                                                <i class="bi bi-whatsapp share-icon"></i>
                                                WhatsApp'ta Paylaş
                                            </button>
                                        </li>
                                        <li>
                                            <button class="dropdown-item share-btn share-telegram telegram" data-topic-code="${post.short_id}">
                                                <i class="bi bi-telegram share-icon"></i>
                                                Telegram'da Paylaş
                                            </button>
                                        </li>
                                        <li><hr class="dropdown-divider"></li>
                                        <li>
                                            <button class="dropdown-item share-btn share-copy copy-link" data-topic-code="${post.short_id}">
                                                <i class="bi bi-link-45deg share-icon"></i>
                                                Linki Kopyala
                                            </button>
                                        </li>
                                        <li>
                                            <button class="dropdown-item share-btn share-copy-code copy-code" data-topic-code="${post.short_id}">
                                                <i class="bi bi-hash share-icon"></i>
                                                Kodu Kopyala
                                            </button>
                                        </li>
                                        <li>
                                            <button class="dropdown-item share-btn share-qr qr-code" data-topic-code="${post.short_id}">
                                                <i class="bi bi-qr-code share-icon"></i>
                                                QR Kod
                                            </button>
                                        </li>
                                    </ul>
                                </div>
                            </div>
                            <div class="d-flex align-items-center">
                                <div class="text-end me-2">
                                    <a href="/profile/${post.username}/" class="username-link">${post.nickname}</a>
                                    <small class="text-muted d-block">${new Date(post.created_at).toLocaleDateString('tr-TR')} ${new Date(post.created_at).toLocaleTimeString('tr-TR', {hour: '2-digit', minute: '2-digit'})}</small>
                                </div>
                                <div class="rounded-circle bg-secondary d-flex align-items-center justify-content-center" style="width: 40px; height: 40px;">
                                    <i class="bi bi-person text-white"></i>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Mobile Layout -->
                        <div class="d-block d-md-none mt-3">
                            <div class="mobile-topic-actions" data-topic-id="${post.id}">
                                <div class="topic-info-container">
                                    <div class="topic-user-info">
                                        <a href="/profile/${post.username}/" class="username-link">${post.nickname}</a>
                                        <small class="text-muted ms-2">${new Date(post.created_at).toLocaleDateString('tr-TR')} ${new Date(post.created_at).toLocaleTimeString('tr-TR', {hour: '2-digit', minute: '2-digit'})}</small>
                                        <small class="text-muted ms-2">${post.comment_count} entry</small>
                                    </div>
                                    <button class="mobile-actions-toggle" data-topic-id="${post.id}">
                                        <i class="bi bi-three-dots"></i>
                                    </button>
                                </div>
                                <div class="mobile-actions-panel" data-topic-id="${post.id}">
                                    <div class="actions-content">
                                        <button class="btn btn-link p-0 vote-btn" data-topic-slug="${post.short_id}" data-vote-type="up">
                                            <i class="bi bi-arrow-up"></i>
                                        </button>
                                        <span class="vote-score fw-bold mx-1" style="font-size: 0.9rem;">${post.upvotes - post.downvotes}</span>
                                        <button class="btn btn-link p-0 vote-btn" data-topic-slug="${post.short_id}" data-vote-type="down">
                                            <i class="bi bi-arrow-down"></i>
                                        </button>
                                        ${isOwner ? `
                                            <button class="btn btn-link p-0 ms-2 topic-bookmark-btn text-muted" data-topic-slug="${post.short_id}">
                                                <i class="bi bi-bookmark"></i>
                                            </button>
                                        ` : ''}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                // Divider ekle
                const dividerDiv = document.createElement('div');
                dividerDiv.className = 'text-center mb-3';
                dividerDiv.innerHTML = '<hr class="topic-divider">';
                
                fragment.appendChild(postDiv);
                fragment.appendChild(dividerDiv);
            });
            
            const postContainer = document.querySelector('.topic-container');
            if (postContainer) {
                postContainer.appendChild(fragment);
                initLikes();
                initVoteButtons();
                initBookmarks();
                initCopyLink(); // Dinamik yüklenen postlar için kopyalama olayını bağla
            }

            window.offset += 10;
            window.hasMore = data.has_more;
            console.log(`Yeni offset: ${window.offset}, Daha fazla var mı: ${window.hasMore}`);
        } else {
            window.hasMore = false;
            console.log('Post bulunamadı, yükleme durduruldu');
        }

        if (loadMoreBtn) {
            loadMoreBtn.style.display = window.hasMore ? 'block' : 'none';
        }
    } catch (error) {
        console.error('Hata:', error);
        if (errorMessage) {
            errorMessage.textContent = 'Di dema barkirina postan de çewtiyek çêbû: ' + error.message;
            errorMessage.style.display = 'block';
        }
        if (loadMoreBtn) loadMoreBtn.style.display = 'block';
    } finally {
        window.loading = false;
        if (loadingDiv) loadingDiv.style.display = 'none';
    }
}

function initBookmarks() {
    console.log("initBookmarks başlatıldı");
    
    document.querySelectorAll('.bookmark-form').forEach(form => {
        if (!form.dataset.listenerAdded) {
            console.log("Yeni bookmark formu bulundu, ID:", form.dataset.postId);
            form.addEventListener('submit', async function(e) {
                e.preventDefault();
                const postId = this.dataset.postId;
                console.log("Yer işareti formu gönderildi, post ID:", postId);
                
                if (!postId || postId === 'undefined') {
                    console.error("Post ID tanımlı değil, action:", this.action);
                    return;
                }

                const csrfToken = getCsrfToken();
                if (!csrfToken) {
                    console.error('CSRF token bulunamadı');
                    return;
                }
                console.log("Gönderilen CSRF Token:", csrfToken);

                try {
                    const isBookmarksTab = window.location.href.includes('tab=bookmarks');
                    const url = isBookmarksTab ? `/remove-bookmark/${postId}/` : `/bookmark-post/${postId}/`;
                    console.log("İstek gönderiliyor, url:", url);

                    const response = await fetch(url, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': csrfToken,
                            'X-Requested-With': 'XMLHttpRequest'
                        },
                        body: new FormData(this)
                    });

                    console.log("Sunucu yanıtı, durum:", response.status);
                    if (!response.ok) {
                        const text = await response.text();
                        throw new Error(`Sunucu hatası: ${response.status} - ${text}`);
                    }

                    const data = await response.json();
                    console.log("Gelen veri:", data);
                    
                    const button = this.querySelector('.bookmark-btn');
                    if (button) {
                        button.textContent = data.bookmarked ? 'Ji Nîşankirina Cîhê Derxîne' : 'Têxe Nîşankirina Cîhê';
                        button.dataset.bookmarked = data.bookmarked ? 'true' : 'false';
                        console.log("Yer işareti butonu güncellendi:", button.textContent, "Bookmarked:", data.bookmarked);
                        if (isBookmarksTab) {
                            const postCard = this.closest('.card');
                            if (postCard) {
                                console.log("Post listeden kaldırılıyor:", postCard.id);
                                postCard.remove();
                            }
                        }
                    } else {
                        console.error("Bookmark butonu bulunamadı, form:", this);
                    }
                } catch (error) {
                    console.error('Yer işareti hatası:', error);
                }
            });
            form.dataset.listenerAdded = 'true';
        } else {
            console.log("Zaten dinleyici eklenmiş, form ID:", form.dataset.postId);
        }
    });
}

function initVoteButtons() {
    console.log("initVoteButtons çalışıyor");
    
    document.querySelectorAll('.vote-form').forEach(form => {
        if (!form.dataset.listenerAdded) {
            form.addEventListener('submit', async function(e) {
                e.preventDefault();
                console.log("Oylama butonuna basıldı");
                const id = this.dataset.postId || this.dataset.commentId;
                const csrfToken = getCsrfToken();
                if (!csrfToken) {
                    console.error('CSRF token bulunamadı');
                    return;
                }
                console.log("Gönderilen CSRF Token:", csrfToken, "Uzunluk:", csrfToken.length);

                try {
                    const url = this.dataset.postId ? `/vote-post/${id}/` : `/vote-comment/${id}/`;
                    console.log("İstek gönderiliyor, url:", url);
                    const response = await fetch(url, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': csrfToken,
                            'X-Requested-With': 'XMLHttpRequest'
                        },
                        body: new FormData(this)
                    });

                    console.log("Sunucu yanıtı:", response.status);
                    if (!response.ok) {
                        const text = await response.text();
                        throw new Error(`Sunucu hatası: ${response.status} - ${text}`);
                    }

                    const data = await response.json();
                    console.log("Gelen veri:", data);
                    
                    const upBtn = this.querySelector('.upvote-btn');
                    const downBtn = this.querySelector('.downvote-btn');
                    if (upBtn) {
                        upBtn.textContent = `${data.upvotes} ↑`;
                        console.log("Up butonu güncellendi:", upBtn.textContent);
                    } else {
                        console.error("Up butonu bulunamadı, form:", this);
                    }
                    if (downBtn) {
                        downBtn.textContent = `${data.downvotes} ↓`;
                        console.log("Down butonu güncellendi:", downBtn.textContent);
                    } else {
                        console.error("Down butonu bulunamadı, form:", this);
                    }
                } catch (error) {
                    console.error('Hata:', error);
                }
            });
            form.dataset.listenerAdded = 'true';
        }
    });
}

function initializePage() {
    window.offset = 10;
    window.hasMore = true;
    window.loading = false;

    const loadMoreBtn = document.getElementById('load-more-btn');
    if (loadMoreBtn) {
        const newBtn = loadMoreBtn.cloneNode(true);
        loadMoreBtn.parentNode.replaceChild(newBtn, loadMoreBtn);
        
        newBtn.addEventListener('click', () => {
            console.log('Load More butonuna tıklandı');
            loadMorePopularPosts();
        });
    } else {
        console.error('Load More butonu bulunamadı');
    }

    const scrollHandler = () => {
        if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 100 && !window.loading) {
            loadMorePopularPosts();
        }
    };
    window.removeEventListener('scroll', scrollHandler);
    window.addEventListener('scroll', scrollHandler);

    const postContainer = document.querySelector('.topic-container');
    if (postContainer) {
        const clickHandler = (e) => {
            if (e.target.classList.contains('show-more-btn')) {
                const postDiv = e.target.closest('.topic-card');
                const preview = postDiv.querySelector('.text-preview');
                const fullText = postDiv.querySelector('.full-text');
                if (preview) preview.classList.add('d-none');
                if (fullText) fullText.classList.remove('d-none');
                e.target.classList.add('d-none');
            }
        };
        postContainer.removeEventListener('click', clickHandler);
        postContainer.addEventListener('click', clickHandler);
    } else {
        console.error('Post container bulunamadı');
    }

    initLikes();
    initVoteButtons();
    initBookmarks();
    initCopyLink(); // İlk yüklemede kopyalama olayını bağla
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializePage);
} else {
    initializePage();
}

export { loadMorePopularPosts };