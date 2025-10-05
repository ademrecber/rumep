// Home Page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Modal event listeners
    const createTopicModal = document.getElementById('createTopicModal');
    const floatingBtn = document.querySelector('.floating-btn');
    
    if (createTopicModal && floatingBtn) {
        createTopicModal.addEventListener('show.bs.modal', function() {
            floatingBtn.classList.add('hidden');
        });
        
        createTopicModal.addEventListener('hidden.bs.modal', function() {
            floatingBtn.classList.remove('hidden');
        });
    }
    
    // Prevent bottom nav layout shift when modal opens
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
                const body = document.body;
                if (body.style.paddingRight) {
                    // Modal is open, fix bottom nav
                    const bottomNav = document.querySelector('.bottom-nav');
                    if (bottomNav) {
                        bottomNav.style.paddingRight = body.style.paddingRight;
                    }
                } else {
                    // Modal is closed, reset bottom nav
                    const bottomNav = document.querySelector('.bottom-nav');
                    if (bottomNav) {
                        bottomNav.style.paddingRight = '';
                    }
                }
            }
        });
    });
    
    observer.observe(document.body, {
        attributes: true,
        attributeFilter: ['style']
    });
    // Textarea auto-resize and character count
    const textarea = document.querySelector('textarea[name="content"]');
    if (textarea) {
        let isResizing = false;
        
        textarea.addEventListener('input', function() {
            if (isResizing) return;
            isResizing = true;
            
            // Scroll pozisyonunu kaydet
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            
            this.style.height = 'auto';
            this.style.height = `${this.scrollHeight}px`;
            
            const charCount = document.getElementById('charCount');
            if (charCount) {
                charCount.textContent = 10000 - this.value.length;
            }
            
            // Scroll pozisyonunu geri yükle
            setTimeout(() => {
                window.scrollTo(0, scrollTop);
                isResizing = false;
            }, 0);
        });
        
        // Focus olayında da scroll pozisyonunu koru
        textarea.addEventListener('focus', function() {
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            setTimeout(() => {
                window.scrollTo(0, scrollTop);
            }, 0);
        });
    }
    
    // Category selection limit
    document.querySelectorAll('input[name="categories"]').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const checkedBoxes = document.querySelectorAll('input[name="categories"]:checked');
            if (checkedBoxes.length > 3) {
                this.checked = false;
                alert('En fazla 3 kategori seçebilirsiniz.');
            }
        });
    });
    
    // Tab switching functionality
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const tabName = this.dataset.tab;
            
            // Update tab styles
            document.querySelectorAll('.tab-btn').forEach(b => {
                b.classList.remove('border-bottom', 'border-primary', 'border-3', 'fw-bold');
                b.style.color = '#6c757d';
            });
            this.classList.add('border-bottom', 'border-primary', 'border-3', 'fw-bold');
            this.style.color = '#0d6efd';
            
            // Show/hide content
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.add('d-none');
            });
            document.getElementById(tabName + '-tab').classList.remove('d-none');
            
            // Update URL without reload
            const url = new URL(window.location);
            if (tabName === 'home') {
                url.searchParams.delete('tab');
            } else {
                url.searchParams.set('tab', tabName);
            }
            window.history.pushState({}, '', url);
        });
    });
    
    // Vote functionality using event delegation
    document.body.addEventListener('click', function(e) {
        const button = e.target.closest('.vote-btn');
        if (!button) return;

        const topicSlug = button.dataset.topicSlug;
        const voteType = button.dataset.voteType;
        
        fetch(`/topic/${topicSlug}/vote/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `vote_type=${voteType}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.vote_score !== undefined) {
                const card = button.closest('.topic-card, .mb-4'); // .mb-4 for topic_detail
                const scoreElement = card.querySelector('.vote-score');
                const upBtn = card.querySelector('.vote-btn[data-vote-type="up"]');
                const downBtn = card.querySelector('.vote-btn[data-vote-type="down"]');
                
                scoreElement.textContent = data.vote_score;
                
                const upIcon = upBtn.querySelector('i');
                const downIcon = downBtn.querySelector('i');

                // Reset icons first
                upIcon.className = 'bi bi-arrow-up';
                downIcon.className = 'bi bi-arrow-down';

                if (data.voted) {
                    if (voteType === 'up') {
                        upIcon.className = 'bi bi-arrow-up-circle-fill text-success';
                    } else {
                        downIcon.className = 'bi bi-arrow-down-circle-fill text-danger';
                    }
                } 
            }
        })
        .catch(error => console.error('Error:', error));
    });

    // Hata varsa modalı aç (Django template'inden gelen bilgiye göre)
    // Bu bloğun çalışması için home.html'de `data-errors` attribute'u eklenmelidir.
    const topicForm = document.getElementById('topicEntryForm');
    if (topicForm && topicForm.dataset.errors === 'true') {
        const modal = new bootstrap.Modal(document.getElementById('createTopicModal'));
        modal.show();
    }
});

// Emoji functionality
let currentTextarea = null;

// Emoji modal event listeners
document.getElementById('emojiModal').addEventListener('show.bs.modal', function(e) {
    currentTextarea = document.querySelector('#createTopicModal textarea[name="content"]') || 
                     document.querySelector('textarea[name="content"]');
    loadEmojis();
});

// Emoji button click handler
document.addEventListener('click', function(e) {
    if (e.target.matches('.emoji-trigger') || e.target.closest('.emoji-trigger')) {
        e.preventDefault();
        e.stopPropagation();
        
        const button = e.target.matches('.emoji-trigger') ? e.target : e.target.closest('.emoji-trigger');
        const textareaId = button.getAttribute('data-textarea');
        currentTextarea = document.getElementById(textareaId);
        
        // Emoji modal'ını aç
        const emojiModalElement = document.getElementById('emojiModal');
        let emojiModal = bootstrap.Modal.getInstance(emojiModalElement);
        if (!emojiModal) {
            emojiModal = new bootstrap.Modal(emojiModalElement, {
                backdrop: false,  // Parent modal'ın kapanmasını önle
                keyboard: true
            });
        }
        emojiModal.show();
    }
});

function loadEmojis() {
    const emojiKeyboard = document.getElementById('emojiKeyboard');
    if (emojiKeyboard.children.length === 0) {
        fetch('/emojis/')
            .then(response => response.json())
            .then(emojis => {
                emojis.forEach(emoji => {
                    const emojiBtn = document.createElement('button');
                    emojiBtn.type = 'button';
                    emojiBtn.className = 'btn btn-light m-1';
                    emojiBtn.innerHTML = `<img src="/static/emojis/${emoji.name}.svg" alt="${emoji.name}" width="24">`;
                    emojiBtn.onclick = () => insertEmoji(emoji.shortcode);
                    emojiKeyboard.appendChild(emojiBtn);
                });
            })
            .catch(error => {
                console.error('Emoji yükleme hatası:', error);
            });
    }
}

function insertEmoji(emoji) {
    if (currentTextarea) {
        const start = currentTextarea.selectionStart;
        const end = currentTextarea.selectionEnd;
        currentTextarea.value = currentTextarea.value.substring(0, start) + emoji + currentTextarea.value.substring(end);
        
        // Parent modal'ı tespit et
        const parentModal = currentTextarea.closest('.modal');
        const parentModalInstance = parentModal ? bootstrap.Modal.getInstance(parentModal) : null;
        
        // Emoji modal'ını kapat
        const emojiModalElement = document.getElementById('emojiModal');
        const emojiModal = bootstrap.Modal.getInstance(emojiModalElement);
        if (emojiModal) {
            emojiModal.hide();
        }
        
        // Parent modal'ın açık kalmasını sağla
        setTimeout(() => {
            if (parentModal && parentModalInstance) {
                // Modal kapalıysa tekrar aç
                if (!parentModal.classList.contains('show')) {
                    parentModalInstance.show();
                }
                
                // Backdrop sorununu çöz
                const backdrop = document.querySelector('.modal-backdrop');
                if (!backdrop) {
                    const newBackdrop = document.createElement('div');
                    newBackdrop.className = 'modal-backdrop fade show';
                    document.body.appendChild(newBackdrop);
                }
                
                // Body class'ını koru
                document.body.classList.add('modal-open');
            }
            
            // Textarea'ya focus ve cursor pozisyonu
            if (currentTextarea) {
                currentTextarea.focus();
                currentTextarea.setSelectionRange(start + emoji.length, start + emoji.length);
                
                // Mobilde scroll sorununu önle
                if (window.innerWidth <= 768) {
                    currentTextarea.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }
        }, 150);
    }
}

// Global function for emoji insertion
window.insertEmoji = insertEmoji;