import { initLikes, getCsrfToken } from "./like.js";
import { initVoteButtons } from "./vote.js";
import { initCopyLink } from "./copy-link.js";

async function loadMorePosts() {
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
        if (!csrfToken) throw new Error(gettext('CSRF token bulunamadı'));
        console.log('CSRF Token:', csrfToken);

        const url = `/load-more-topics/?offset=${window.offset}`;
        console.log(`Yükleniyor: url=${url}`);

        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrfToken
            }
        });

        if (!response.ok) throw new Error(gettext('Ağ hatası: %(status)s').replace('%(status)s', response.status));

        const data = await response.json();
        console.log('Gelen veri:', data);

        if (data.posts && Array.isArray(data.posts)) {
            const fragment = document.createDocumentFragment();
            data.posts.forEach(post => {
                const liked = post.liked ? 'liked' : '';
                const bookmarked = post.bookmarked ? 'bookmarked' : '';
                const isOwner = post.is_owner !== undefined ? post.is_owner : false; // is_owner yoksa false varsay
                const postDiv = document.createElement('div');
                postDiv.className = 'card mb-2 tweet-card';
                postDiv.id = `post-${post.id}`;
                const totalLines = post.text.split(/(\n)/).length;
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
                                            <form method="post" action="/delete-post/${post.id}/" class="m-0" onsubmit="return confirm('${gettext('Bu postu silmek istediğinizden emin misiniz?')}');">
                                                <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
                                                <button type="submit" class="dropdown-item text-danger">${gettext('Sil')}</button>
                                            </form>
                                        </li>
                                    ` : ''}
                                    <li>
                                        <form method="post" action="/bookmark-post/${post.id}/?tab=posts" class="bookmark-form m-0" onsubmit="return confirm('${bookmarked ? gettext('Yer işaretinden kaldır') : gettext('Yer işaretine ekle')} istediğinizden emin misiniz?');" data-post-id="${post.id}">
                                            <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
                                            <button type="submit" class="dropdown-item">${bookmarked ? gettext('Yer İşaretinden Kaldır') : gettext('Yer İşaretine Ekle')}</button>
                                        </form>
                                    </li>
                                    <li>
                                        <button class="dropdown-item copy-link-btn" data-post-id="${post.id}">${gettext('Bağlantıyı Kopyala')}</button>
                                    </li>
                                </ul>
                            </div>
                        </div>
                        <h5>${post.title || ''}</h5>
                        <div class="post-text">
                            ${post.text.length > 400 || totalLines > 15 ? `
                                <div class="text-preview">${post.text.substring(0, 100).replace(/\n/g, '<br>')}</div>
                                <button class="btn btn-link text-primary p-0 show-more-btn">${gettext('Daha fazla göster')}</button>
                                <div class="full-text d-none">${post.text.split('\n').map(line => `<p>${line}</p>`).join('')}</div>
                            ` : post.text.split('\n').map(line => `<p>${line}</p>`).join('')}
                        </div>
                        ${post.link ? `<a href="/rmp/${post.link.slice(4)}" target="_blank" class="text-muted mt-2 d-block">${post.link}</a>` : ''}
                        ${post.embed_code ? `<div class="social-embed">${post.embed_code}</div>` : ''}
                        <div class="post-meta text-muted mt-2">
                            <span>${gettext('Beğeni')}: ${post.like_count}</span> | 
                            <span>${gettext('Yorum')}: ${post.comment_count}</span> | 
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
                            ${post.total_score ? `<span class="text-muted ms-2">${gettext('Puan')}: ${post.total_score.toFixed(1)}</span>` : ''}
                        </div>
                    </div>
                `;
                fragment.appendChild(postDiv);
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
            errorMessage.textContent = gettext('Postlar yüklenirken hata oluştu: %(error)s').replace('%(error)s', error.message);
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
                        button.textContent = data.bookmarked ? gettext('Yer İşaretinden Kaldır') : gettext('Yer İşaretine Ekle');
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

// initVoteButtons fonksiyonu vote.js'den import ediliyor

function initializePage() {
    window.offset = window.offset || 10;
    window.hasMore = typeof window.hasMore === 'undefined' ? true : window.hasMore;
    window.loading = window.loading || false;

    const loadMoreBtn = document.getElementById('load-more-btn');
    if (loadMoreBtn) {
        const newBtn = loadMoreBtn.cloneNode(true);
        loadMoreBtn.parentNode.replaceChild(newBtn, loadMoreBtn);
        
        newBtn.addEventListener('click', () => {
            console.log('Load More butonuna tıklandı');
            loadMorePosts();
        });
    } else {
        console.error('Load More butonu bulunamadı');
    }

    const scrollHandler = () => {
        if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 100 && !window.loading) {
            loadMorePosts();
        }
    };
    window.removeEventListener('scroll', scrollHandler);
    window.addEventListener('scroll', scrollHandler);

    const postContainer = document.querySelector('.topic-container');
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
    initCopyLink();
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializePage);
} else {
    initializePage();
}

export { loadMorePosts };