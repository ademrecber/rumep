// Takip Et butonu JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Takip Et butonları için event listener
    document.querySelectorAll('.follow-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const username = this.dataset.username;
            if (!username) return;
            
            // CSRF token al
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
                             document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
            
            // Loading state
            const originalText = this.textContent;
            this.disabled = true;
            this.textContent = 'Yükleniyor...';
            
            fetch(`/toggle-follow/${username}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                credentials: 'same-origin'
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                } else {
                    // Buton metnini güncelle
                    if (data.is_following) {
                        this.textContent = 'Takip Ediliyor';
                        this.classList.remove('btn-outline-primary');
                        this.classList.add('btn-primary');
                    } else {
                        this.textContent = 'Takip Et';
                        this.classList.remove('btn-primary');
                        this.classList.add('btn-outline-primary');
                    }
                    
                    // Takipçi sayısını güncelle
                    const followerCountElement = document.querySelector('.follower-count');
                    if (followerCountElement) {
                        followerCountElement.textContent = data.follower_count;
                    }
                }
            })
            .catch(error => {
                console.error('Takip işlemi hatası:', error);
                alert('Bir hata oluştu. Lütfen tekrar deneyin.');
            })
            .finally(() => {
                this.disabled = false;
                if (this.textContent === 'Yükleniyor...') {
                    this.textContent = originalText;
                }
            });
        });
    });
});