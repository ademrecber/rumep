// Bootstrap Özellikleri JavaScript

// Progress Bar
function showProgressBar() {
    const progressBar = document.getElementById('pageProgressBar');
    if (progressBar) {
        progressBar.style.width = '30%';
        setTimeout(() => progressBar.style.width = '70%', 200);
        setTimeout(() => progressBar.style.width = '100%', 500);
        setTimeout(() => progressBar.style.width = '0%', 1000);
    }
}

// Toast Notifications
function showToast(type, message) {
    const toastElement = document.getElementById(type + 'Toast');
    const messageElement = document.getElementById(type + 'Message');
    
    if (toastElement && messageElement) {
        messageElement.textContent = message;
        const toast = new bootstrap.Toast(toastElement);
        toast.show();
    }
}

// Sayfa yüklendiğinde progress bar göster
document.addEventListener('DOMContentLoaded', function() {
    showProgressBar();
});

// AJAX istekleri için progress bar
document.addEventListener('click', function(e) {
    if (e.target.matches('a[href]:not([href^="#"]):not([data-bs-toggle])')) {
        showProgressBar();
    }
});

// Form gönderimlerinde success toast
document.addEventListener('submit', function(e) {
    if (e.target.matches('form')) {
        setTimeout(() => {
            showToast('success', 'İşlem başarıyla tamamlandı!');
        }, 500);
    }
});

// Copy işlemleri için toast
document.addEventListener('click', function(e) {
    if (e.target.matches('.copy-link, .copy-code')) {
        showToast('info', 'Kopyalandı!');
    }
});

// Vote işlemleri için toast
document.addEventListener('click', function(e) {
    if (e.target.matches('.vote-btn')) {
        showToast('success', 'Oyunuz kaydedildi!');
    }
});