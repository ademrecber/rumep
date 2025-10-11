

function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
}

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
        if (!csrfToken) throw new Error('CSRF token bulunamadı');
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

        if (!response.ok) throw new Error(`Ağ hatası: ${response.status}`);

        const data = await response.json();
        console.log('Gelen veri:', data);

        if (data.posts && Array.isArray(data.posts)) {
            const fragment = document.createDocumentFragment();
            data.posts.forEach(topic => {
                const isOwner = topic.is_owner !== undefined ? topic.is_owner : false;
                const topicDiv = document.createElement('div');
                topicDiv.className = 'card mb-2 topic-card fade-in border-0';
                topicDiv.id = `topic-${topic.id}`;
                topicDiv.style.boxShadow = 'none !important';
                
                topicDiv.innerHTML = `
                    <div class="card-body">
                        <a href="/topic/${topic.short_id}/" class="text-decoration-none text-dark">
                            <h5 class="card-title mb-2">${topic.title}</h5>
                        </a>
                        
                        ${topic.text ? `
                        <div class="first-entry-preview text-muted mb-2" style="font-size: 0.85rem; color: #6c757d;">
                            ${topic.text.length > 790 ? 
                                topic.text.substring(0, 790) + '<a href="/topic/' + topic.short_id + '/" class="text-primary text-decoration-none">...devamını gör</a>' : 
                                topic.text
                            }
                        </div>
                        ` : ''}
                        
                        <!-- Desktop Layout -->
                        <div class="d-none d-md-flex justify-content-between align-items-end mt-3">
                            <div class="vote-buttons d-flex gap-1 align-items-center">
                                <button class="btn btn-link p-0 vote-btn" data-topic-slug="${topic.short_id}" data-vote-type="up">
                                    <i class="bi bi-arrow-up"></i>
                                </button>
                                <span class="vote-score fw-bold" style="font-size: 0.9rem;">${topic.upvotes - topic.downvotes}</span>
                                <button class="btn btn-link p-0 vote-btn" data-topic-slug="${topic.short_id}" data-vote-type="down">
                                    <i class="bi bi-arrow-down"></i>
                                </button>
                                <small class="text-muted ms-2">${topic.comment_count} entry</small>
                                ${isOwner ? `
                                    <button class="btn btn-link p-0 ms-2 topic-bookmark-btn text-muted" data-topic-slug="${topic.short_id}">
                                        <i class="bi bi-bookmark"></i>
                                    </button>
                                ` : ''}
                            </div>
                            <div class="d-flex align-items-center">
                                <div class="text-end me-2">
                                    <a href="/profile/${topic.username}/" class="username-link">${topic.nickname}</a>
                                    <small class="text-muted d-block">${new Date(topic.created_at).toLocaleDateString('tr-TR')} ${new Date(topic.created_at).toLocaleTimeString('tr-TR', {hour: '2-digit', minute: '2-digit'})}</small>
                                </div>
                                <div class="rounded-circle bg-secondary d-flex align-items-center justify-content-center" style="width: 40px; height: 40px;">
                                    <i class="bi bi-person text-white"></i>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Mobile Layout -->
                        <div class="d-block d-md-none mt-3">
                            <div class="mobile-topic-actions" data-topic-id="${topic.id}">
                                <div class="topic-info-container">
                                    <div class="topic-user-info">
                                        <a href="/profile/${topic.username}/" class="username-link">${topic.nickname}</a>
                                        <small class="text-muted ms-2">${new Date(topic.created_at).toLocaleDateString('tr-TR')} ${new Date(topic.created_at).toLocaleTimeString('tr-TR', {hour: '2-digit', minute: '2-digit'})}</small>
                                        <small class="text-muted ms-2">${topic.comment_count} entry</small>
                                    </div>
                                    <button class="mobile-actions-toggle" data-topic-id="${topic.id}">
                                        <i class="bi bi-three-dots"></i>
                                    </button>
                                </div>
                                <div class="mobile-actions-panel" data-topic-id="${topic.id}">
                                    <div class="actions-content">
                                        <button class="btn btn-link p-0 vote-btn" data-topic-slug="${topic.short_id}" data-vote-type="up">
                                            <i class="bi bi-arrow-up"></i>
                                        </button>
                                        <span class="vote-score fw-bold mx-1" style="font-size: 0.9rem;">${topic.upvotes - topic.downvotes}</span>
                                        <button class="btn btn-link p-0 vote-btn" data-topic-slug="${topic.short_id}" data-vote-type="down">
                                            <i class="bi bi-arrow-down"></i>
                                        </button>
                                        ${isOwner ? `
                                            <button class="btn btn-link p-0 ms-2 topic-bookmark-btn text-muted" data-topic-slug="${topic.short_id}">
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
                
                fragment.appendChild(topicDiv);
                fragment.appendChild(dividerDiv);
            });
            
            const topicContainer = document.querySelector('.topic-container');
            if (topicContainer) {
                topicContainer.appendChild(fragment);
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
            errorMessage.textContent = `Postlar yüklenirken hata oluştu: ${error.message}`;
            errorMessage.style.display = 'block';
        }
        if (loadMoreBtn) loadMoreBtn.style.display = 'block';
    } finally {
        window.loading = false;
        if (loadingDiv) loadingDiv.style.display = 'none';
    }
}



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


}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializePage);
} else {
    initializePage();
}

export { loadMorePosts };