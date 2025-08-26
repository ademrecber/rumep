export function initCopyLink() {
    console.log("initCopyLink başlatıldı");

    // Post kopyalama butonları
    const postCopyButtons = document.querySelectorAll('.copy-link-btn');
    console.log("Post copy-link-btn sayısı:", postCopyButtons.length);
    postCopyButtons.forEach(btn => {
        if (!btn.dataset.listenerAdded) {
            btn.addEventListener('click', () => {
                const postShortId = btn.dataset.postShortId;
                const postUrl = `${window.location.origin}/rmp/${postShortId}/`;
                navigator.clipboard.writeText(postUrl)
                    .then(() => {
                        console.log("Bağlantı kopyalandı:", postUrl);
                        const toast = new bootstrap.Toast(document.getElementById('copyToast'));
                        toast.show();
                    })
                    .catch(err => {
                        console.error("Kopyalama hatası:", err);
                        alert("Girêdan nehat kopîkirin!");
                    });
            });
            btn.dataset.listenerAdded = 'true';
        }
    });

    // Değerlendirme kopyalama butonları
    const critiqueCopyButtons = document.querySelectorAll('.copy-critique-link-btn');
    console.log("Critique copy-critique-link-btn sayısı:", critiqueCopyButtons.length);
    critiqueCopyButtons.forEach(btn => {
        if (!btn.dataset.listenerAdded) {
            btn.addEventListener('click', () => {
                const postShortId = btn.dataset.postShortId;
                if (!postShortId) {
                    console.error("Eksik veri: postShortId bulunamadı", { postShortId });
                    alert("Girêdan nehat kopîkirin!");
                    return;
                }
                const critiqueUrl = `${window.location.origin}/rmp/${postShortId}/`;
                navigator.clipboard.writeText(critiqueUrl)
                    .then(() => {
                        console.log("Değerlendirme bağlantısı kopyalandı:", critiqueUrl);
                        const toast = new bootstrap.Toast(document.getElementById('copyToast'));
                        toast.show();
                    })
                    .catch(err => {
                        console.error("Değerlendirme kopyalama hatası:", err);
                        alert("Girêdan nehat kopîkirin!");
                    });
            });
            btn.dataset.listenerAdded = 'true';
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    initCopyLink();
});