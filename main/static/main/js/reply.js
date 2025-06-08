export function initReplies() {
    console.log("initReplies başlatıldı");

    bindReplyEvents();
}

export function bindReplyEvents() {
    console.log("bindReplyEvents çağrıldı");
    const replyButtons = document.querySelectorAll('.reply-btn');
    console.log("bindReplyEvents çalışıyor, reply-btn sayısı:", replyButtons.length);
    replyButtons.forEach(btn => {
        // Mevcut dinleyicileri kaldırmak için butonu klonla
        const newBtn = btn.cloneNode(true);
        btn.parentNode.replaceChild(newBtn, btn);
        
        newBtn.addEventListener('click', function(e) {
            e.preventDefault();
            console.log("Reply butonuna basıldı, commentId:", this.dataset.commentId);
            const commentId = this.dataset.commentId;
            const form = document.getElementById(`reply-form-${commentId}`);
            if (form) {
                document.querySelectorAll('.reply-form').forEach(f => f.style.display = 'none');
                form.style.display = 'block';
                form.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            } else {
                console.error(`reply-form-${commentId} bulunamadı`);
            }
        });
        newBtn.dataset.listenerAdded = 'true';
    });

    const cancelButtons = document.querySelectorAll('.cancel-reply');
    console.log("cancel-reply sayısı:", cancelButtons.length);
    cancelButtons.forEach(btn => {
        // Mevcut dinleyicileri kaldırmak için butonu klonla
        const newBtn = btn.cloneNode(true);
        btn.parentNode.replaceChild(newBtn, btn);
        
        newBtn.addEventListener('click', function() {
            console.log("Cancel butonuna basıldı");
            const replyForm = this.closest('.reply-form');
            if (replyForm) replyForm.style.display = 'none';
        });
        newBtn.dataset.listenerAdded = 'true';
    });
}