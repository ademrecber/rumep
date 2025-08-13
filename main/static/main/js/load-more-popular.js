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
                postDiv.className = 'card mb-2 tweet-card';
                postDiv.id = `post-${post.id}`;
                const totalLines = post.text.split(/(\n)/).length;
                
                // Process emoji shortcodes in post text
                const processedText = renderEmojis(post.text);
                
                postDiv.innerHTML = `
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start">
                            <p class="mb-1">
                                <strong>${post.nickname}</strong>
                                <span class="text-muted"><a href="/profile/${post.username}/" class="text-muted text-decoration-none">@${post.username}</a> · ${post.short_id} · ${new Date(post.created_at).toLocaleString()}</span>
                            </p>
                            <div class="dropdown">
                                <button class="btn btn-link text-muted p-0" type="button" data-bs-toggle="dropdown" aria-expanded="false">
                                    <i class="bi bi-three-dots"></i>
                                </button>
                                <ul class="dropdown-menu">
                                    ${isOwner ? `
                                        <li>
                                            <form method="post" action="/delete-post/${post.id}/" class="m-0" onsubmit="return confirm('Ma tu bawer î ku dixwazî vê postê jê bibî?');">
                                                <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
                                                <button type="submit" class="dropdown-item text-danger">Jê bibe</button>
                                            </form>
                                        </li>
                                    ` : ''}
                                    <li>
                                        <form method="post" action="/bookmark-post/${post.id}/?tab=posts" class="bookmark-form m-0" onsubmit="return confirm('${bookmarked ? 'Ji nîşankirina cîhê derxistin' : 'Têxe nîşankirina cîhê'} istediğinizden emin misiniz?');" data-post-id="${post.id}">
                                            <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
                                            <button type="submit" class="dropdown-item">${bookmarked ? 'Ji Nîşankirina Cîhê Derxîne' : 'Têxe Nîşankirina Cîhê'}</button>
                                        </form>
                                    </li>
                                    <li>
                                        <button class="dropdown-item copy-link-btn" data-post-id="${post.id}">Girêdanê Kopî Bike</button>
                                    </li>
                                </ul>
                            </div>
                        </div>
                        <h5>${post.title || 'Bêsernav'}</h5>
                        <div class="post-text">
                            ${processedText.length > 400 || totalLines > 15 ? `
                                <div class="text-preview"><p>${processedText.substring(0, 100)}</p></div>
                                <button class="btn btn-link text-primary p-0 show-more-btn">Zêdetir bibîne</button>
                                <div class="full-text d-none"><p>${processedText}</p></div>
                            ` : `<p>${processedText}</p>`}
                        </div>
                        ${post.link ? `<a href="${post.link}" target="_blank" class="text-muted mt-2 d-block">${post.link}</a>` : ''}
                        ${post.embed_code ? `<div class="social-embed">${post.embed_code}</div>` : ''}
                        <div class="post-meta text-muted mt-2">
                            <span>Ecibandin: ${post.like_count}</span> | 
                            <span>Şîrove: ${post.comment_count}</span> | 
                            <span><i class="bi bi-list-ul"></i> ${post.critique_count}</span> | 
                            <span><i class="bi bi-bar-chart"></i> ${post.views}</span>
                        </div>
                        <div class="post-actions mt-2">
                            <form method="post" action="/like-post/${post.id}/" class="like-form d-inline">
                                <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
                                <button type="submit" class="btn btn-link like-btn ${liked}" data-post-id="${post.id}">
                                    <i class="bi ${liked ? 'bi-heart-fill' : 'bi-heart'}"></i> ${post.like_count}
                                </button>
                            </form>
                            <form method="post" action="/vote-post/${post.id}/" class="vote-form d-inline" data-post-id="${post.id}">
                                <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
                                <input type="hidden" name="vote" value="up">
                                <button type="submit" class="btn btn-link text-success p-0 upvote-btn">${post.upvotes} ↑</button>
                            </form>
                            <form method="post" action="/vote-post/${post.id}/" class="vote-form d-inline" data-post-id="${post.id}">
                                <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
                                <input type="hidden" name="vote" value="down">
                                <button type="submit" class="btn btn-link text-danger p-0 downvote-btn">${post.downvotes} ↓</button>
                            </form>
                            <a href="/post/${post.id}/" class="btn btn-link text-muted"><i class="bi bi-arrow-right"></i></a>
                            ${post.total_score ? `<span class="text-muted ms-2">Pûan: ${post.total_score.toFixed(1)}</span>` : ''}
                        </div>
                    </div>
                `;
                fragment.appendChild(postDiv);
            });
            
            const postContainer = document.querySelector('.post-container');
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

    const postContainer = document.querySelector('.post-container');
    if (postContainer) {
        const clickHandler = (e) => {
            if (e.target.classList.contains('show-more-btn')) {
                const postDiv = e.target.closest('.tweet-card');
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