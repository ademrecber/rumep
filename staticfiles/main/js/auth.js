/**
 * Google Sign-In işlemleri için yardımcı fonksiyonlar
 */

// Google Sign-In butonuna tıklandığında yükleniyor göstergesi ekler
function initGoogleSignIn() {
    const googleSignInBtn = document.querySelector('.google-btn');
    
    if (googleSignInBtn) {
        googleSignInBtn.addEventListener('click', function(e) {
            // Butonun içeriğini yükleniyor göstergesiyle değiştir
            const originalContent = this.innerHTML;
            this.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Giriş yapılıyor...';
            this.disabled = true;
            
            // Yönlendirmeyi geciktir (kullanıcı yükleniyor göstergesini görebilsin)
            setTimeout(() => {
                // Orijinal href'e yönlendir
                window.location.href = this.getAttribute('href');
            }, 500);
            
            e.preventDefault();
        });
    }
}

// Profil tamamlama formunda kullanıcı adı doğrulama
function initProfileCompletion() {
    const usernameInput = document.getElementById('username');
    const nicknameInput = document.getElementById('nickname');
    const submitButton = document.querySelector('button[type="submit"]');
    
    if (usernameInput && submitButton) {
        // Kullanıcı adı doğrulama
        usernameInput.addEventListener('input', function() {
            validateUsername(this);
        });
        
        // Form gönderilmeden önce doğrulama
        submitButton.closest('form').addEventListener('submit', function(e) {
            if (!validateUsername(usernameInput) || !validateNickname(nicknameInput)) {
                e.preventDefault();
            }
        });
    }
}

// Kullanıcı adı doğrulama
function validateUsername(input) {
    const value = input.value.trim();
    const regex = /^[a-zA-Z0-9_]{3,30}$/;
    const isValid = regex.test(value);
    
    if (!isValid) {
        input.classList.add('is-invalid');
        
        // Hata mesajı ekle veya güncelle
        let errorElement = input.nextElementSibling;
        if (!errorElement || !errorElement.classList.contains('invalid-feedback')) {
            errorElement = document.createElement('div');
            errorElement.className = 'invalid-feedback';
            input.parentNode.insertBefore(errorElement, input.nextSibling);
        }
        
        if (value.length < 3) {
            errorElement.textContent = 'Kullanıcı adı en az 3 karakter olmalıdır.';
        } else {
            errorElement.textContent = 'Kullanıcı adı sadece harf, rakam ve alt çizgi içerebilir.';
        }
    } else {
        input.classList.remove('is-invalid');
        input.classList.add('is-valid');
        
        // Hata mesajını kaldır
        const errorElement = input.nextElementSibling;
        if (errorElement && errorElement.classList.contains('invalid-feedback')) {
            errorElement.remove();
        }
    }
    
    return isValid;
}

// Takma ad doğrulama
function validateNickname(input) {
    const value = input.value.trim();
    const isValid = value.length >= 2 && value.length <= 50;
    
    if (!isValid) {
        input.classList.add('is-invalid');
        
        // Hata mesajı ekle veya güncelle
        let errorElement = input.nextElementSibling;
        if (!errorElement || !errorElement.classList.contains('invalid-feedback')) {
            errorElement = document.createElement('div');
            errorElement.className = 'invalid-feedback';
            input.parentNode.insertBefore(errorElement, input.nextSibling);
        }
        
        errorElement.textContent = 'Takma ad 2-50 karakter arasında olmalıdır.';
    } else {
        input.classList.remove('is-invalid');
        input.classList.add('is-valid');
        
        // Hata mesajını kaldır
        const errorElement = input.nextElementSibling;
        if (errorElement && errorElement.classList.contains('invalid-feedback')) {
            errorElement.remove();
        }
    }
    
    return isValid;
}

// Sayfa yüklendiğinde çalıştır
document.addEventListener('DOMContentLoaded', function() {
    initGoogleSignIn();
    initProfileCompletion();
});

export { initGoogleSignIn, initProfileCompletion };