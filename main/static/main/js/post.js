function initPost() {
    console.log("initPost çalıştı"); // Debug
    const postForm = document.querySelector('.tweet-form');
    if (postForm) {
        console.log("Post formu bulundu:", postForm); // Debug
        postForm.addEventListener('submit', function(e) {
            e.preventDefault();
            console.log("Post submit tetiklendi"); // Debug
            const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
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
                console.log("Yanıt alındı:", response.status); // Debug
                return response.json();
            })
            .then(data => {
                console.log("Data:", data); // Debug
                if (data.success) {
                    const postsDiv = document.querySelector('.twitter-container');
                    const newPost = document.createElement('div');
                    newPost.className = 'card mb-2 tweet-card';
                    newPost.id = `post-${data.post_id}`;
                    newPost.innerHTML = `
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-start">
                                <p class="mb-1">
                                    <strong>${data.nickname}</strong> 
                                    <span class="text-muted">@${data.username} · ${data.created_at}</span>
                                </p>
                                <div class="dropdown">
                                    <button class="btn btn-link text-muted p-0" type="button" data-bs-toggle="dropdown">
                                        <i class="bi bi-three-dots"></i>
                                    </button>
                                    <ul class="dropdown-menu">
                                        <li>
                                            <form method="post" action="/delete-post/${data.post_id}/" onsubmit="return confirm('Bu postu silmek istediğinizden emin misiniz?');">
                                                <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
                                                <button type="submit" class="dropdown-item text-danger">Sil</button>
                                            </form>
                                        </li>
                                    </ul>
                                </div>
                            </div>
                            <div class="post-text">${data.text}</div>
                        </div>
                    `;
                    postsDiv.insertBefore(newPost, postsDiv.firstChild);
                    this.reset();
                }
            })
            .catch(error => console.error('Hata:', error));
        });
    } else {
        console.log("Post formu bulunamadı"); // Debug
    }
}

export { initPost };