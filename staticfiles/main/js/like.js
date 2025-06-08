function getCsrfToken() {
    // First try to get token from meta tag
    let token = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
    if (!token) {
        // If not found in meta, try to get from csrf_token input
        token = document.querySelector('input[name="csrfmiddlewaretoken"]')?.value;
    }
    return token ? token.trim() : null;
}

function initLikes() {
    console.log("initLikes çalışıyor");
    // Remove existing event listeners by cloning and replacing elements
    document.querySelectorAll('.like-form').forEach(form => {
        const newForm = form.cloneNode(true);
        form.parentNode.replaceChild(newForm, form);
        
        newForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            console.log("Beğeni butonuna basıldı");
            
            const postId = this.querySelector('.like-btn').dataset.postId;
            const csrfToken = getCsrfToken();
            
            if (!csrfToken) {
                console.error("CSRF token bulunamadı!");
                return;
            }
            
            console.log("Gönderilen CSRF Token:", csrfToken, "Uzunluk:", csrfToken.length);

            try {
                const response = await fetch(this.action, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'X-Requested-With': 'XMLHttpRequest',
                        'Content-Type': 'application/x-www-form-urlencoded'
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
                
                const button = this.querySelector('.like-btn');
                button.innerHTML = `<i class="bi ${data.liked ? 'bi-heart-fill' : 'bi-heart'}"></i> ${data.like_count}`;
                button.classList.toggle('liked', data.liked);
            } catch (error) {
                console.error("Hata:", error);
            }
        });
    });
}

// Only initialize on DOMContentLoaded if not being imported
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initLikes);
} else {
    initLikes();
}

export { initLikes, getCsrfToken };