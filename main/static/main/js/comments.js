import { bindReplyEvents } from './reply.js';

function initComments() {
    console.log("initComments başlatıldı");

    document.querySelectorAll('.reply-form form').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            console.log("Yorum formu gönderiliyor");
            const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
            if (!csrfToken) {
                console.error("CSRF token bulunamadı");
                return;
            }
            const formData = new FormData(this);
            fetch(this.action, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            })
            .then(response => {
                console.log("Yorum yanıtı alındı, durum:", response.status);
                if (!response.ok) {
                    throw new Error(`Sunucu hatası: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log("Yorum eklendi, veri:", data);
                if (data.success) {
                    const commentDiv = document.createElement('div');
                    commentDiv.className = `card mb-2 tweet-card ${data.parent_id ? 'ms-4 border-start' : ''}`;
                    commentDiv.id = `comment-${data.comment_id}`;
                    const text = data.text; // text zaten render_emojis ile işlenmiş
                    const lines = text.split('\n').filter(line => line.trim()).length;
                    const showMore = text.length > 400 || lines > 15;
                    commentDiv.innerHTML = `
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-start">
                                <p class="mb-1">
                                    <strong>${data.nickname}</strong> 
                                    <span class="text-muted">@${data.username} · şimdi</span>
                                </p>
                                <div class="dropdown">
                                    <button class="btn btn-link text-muted p-0" type="button" data-bs-toggle="dropdown">
                                        <i class="bi bi-three-dots"></i>
                                    </button>
                                    <ul class="dropdown-menu">
                                        <li>
                                            <form method="post" action="/delete-comment/${data.comment_id}/" onsubmit="return window.deleteComment(event, '${data.comment_id}')">
                                                <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
                                                <button type="submit" class="dropdown-item text-danger">Sil</button>
                                            </form>
                                        </li>
                                    </ul>
                                </div>
                            </div>
                            <div class="post-text">
                                ${showMore ? `
                                    <div class="text-preview"><p>${text}</p></div>
                                    <button class="btn btn-link text-primary p-0 show-more-btn">Devamını gör</button>
                                    <div class="full-text d-none"><p>${text}</p></div>
                                    <button class="btn btn-link text-primary p-0 show-less-btn d-none">Daha az gör</button>
                                ` : `<p>${text}</p>`}
                            </div>
                            <div class="post-actions mt-2">
                                <button class="btn btn-link text-primary p-0 reply-btn" data-comment-id="${data.comment_id}">
                                    <i class="bi bi-reply"></i> Yanıtla
                                </button>
                                <form method="post" action="/vote-comment/${data.comment_id}/" class="vote-form d-inline" data-comment-id="${data.comment_id}">
                                    <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
                                    <input type="hidden" name="vote" value="up">
                                    <button type="submit" class="btn btn-link text-success p-0 upvote-btn">0 ↑</button>
                                </form>
                                <form method="post" action="/vote-comment/${data.comment_id}/" class="vote-form d-inline" data-comment-id="${data.comment_id}">
                                    <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
                                    <input type="hidden" name="vote" value="down">
                                    <button type="submit" class="btn btn-link text-danger p-0 downvote-btn">0 ↓</button>
                                </form>
                            </div>
                            <div class="reply-form mt-2" id="reply-form-${data.comment_id}" style="display:none;">
                                <form method="post">
                                    <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
                                    <input type="hidden" name="parent_id" value="${data.comment_id}">
                                    <div class="input-group">
                                        <textarea name="text" class="form-control auto-resize mb-2" rows="2" placeholder="Yanıtınız..." maxlength="500"></textarea>
                                        <button type="button" class="btn btn-link text-muted p-0 ms-2" id="emojiButton" data-bs-toggle="modal" data-bs-target="#emojiModal">
                                            <i class="bi bi-emoji-smile" style="font-size: 1.5rem;"></i>
                                        </button>
                                    </div>
                                    <button type="submit" class="btn btn-sm btn-primary">Gönder</button>
                                    <button type="button" class="btn btn-sm btn-outline-secondary cancel-reply">İptal</button>
                                </form>
                            </div>
                        </div>
                    `;
                    const commentsSection = document.querySelector('.comments-section');
                    if (data.parent_id) {
                        let parentReplies = document.querySelector(`#comment-${data.parent_id} .replies`);
                        if (!parentReplies) {
                            parentReplies = document.createElement('div');
                            parentReplies.className = 'replies mt-3';
                            document.querySelector(`#comment-${data.parent_id} .card-body`).appendChild(parentReplies);
                        }
                        parentReplies.appendChild(commentDiv);
                    } else if (commentsSection) {
                        commentsSection.prepend(commentDiv);
                    } else {
                        console.error('Comments section bulunamadı');
                    }
                    form.reset();
                    form.style.display = 'none';
                    console.log("Yorum eklendikten sonra bindReplyEvents çağrılıyor");
                    bindReplyEvents(); // Yeni yorum için olay dinleyicilerini bağla
                }
            })
            .catch(error => console.error('Hata:', error));
        });
    });

    window.deleteComment = function(event, commentId) {
        event.preventDefault();
        console.log("deleteComment çağrıldı, commentId:", commentId);

        if (!confirm('Bu yorumu silmek istediğinizden emin misiniz?')) {
            console.log("Silme iptal edildi");
            return false;
        }

        const form = event.target.closest('form');
        const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
        if (!csrfToken) {
            console.error("CSRF token bulunamadı");
            return false;
        }
        if (!form) {
            console.error("Form bulunamadı, event.target:", event.target);
            return false;
        }
        fetch(form.action, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: new FormData(form)
        })
        .then(response => {
            console.log("Silme yanıtı alındı, durum:", response.status);
            if (!response.ok) {
                throw new Error(`Sunucu hatası: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log("deleteComment yanıtı:", data);
            if (data.success) {
                const commentElement = document.getElementById(`comment-${commentId}`);
                if (commentElement) {
                    commentElement.remove();
                    console.log("Yorum DOM’dan silindi, commentId:", commentId);
                } else {
                    console.error("Yorum elementi bulunamadı, commentId:", commentId);
                }
            } else {
                console.error("Silme başarısız, sunucu yanıtı:", data);
            }
        })
        .catch(error => console.error("Silme hatası:", error));
        return false;
    };

    // İlk yüklemede olay dinleyicilerini bağla
    bindReplyEvents();
}

export { initComments };