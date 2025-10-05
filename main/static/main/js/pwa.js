// PWA Installation and Management
let deferredPrompt;
let isInstalled = false;

document.addEventListener('DOMContentLoaded', function() {
    // Register service worker
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/static/main/sw.js')
            .then(registration => {
                console.log('SW registered successfully');
                
                // Check for updates
                registration.addEventListener('updatefound', () => {
                    const newWorker = registration.installing;
                    newWorker.addEventListener('statechange', () => {
                        if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                            showUpdateNotification();
                        }
                    });
                });
            })
            .catch(error => {
                console.log('SW registration failed:', error);
            });
    }
    
    // Check if already installed
    if (window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone) {
        isInstalled = true;
        document.body.classList.add('pwa-installed');
    }
    
    // Listen for install prompt
    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredPrompt = e;
        
        if (!isInstalled) {
            showInstallButton();
        }
    });
    
    // Listen for app installed
    window.addEventListener('appinstalled', () => {
        isInstalled = true;
        hideInstallButton();
        showToast(gettext('Rumep başarıyla yüklendi!'), 'success');
    });
    
    // Create install button
    function showInstallButton() {
        // Check if button already exists
        if (document.getElementById('pwa-install-btn')) return;
        
        const installBtn = document.createElement('button');
        installBtn.id = 'pwa-install-btn';
        installBtn.className = 'btn btn-primary btn-sm position-fixed';
        installBtn.style.cssText = `
            bottom: 80px;
            left: 20px;
            z-index: 1000;
            border-radius: 25px;
            padding: 8px 16px;
            font-size: 0.85rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        `;
        installBtn.innerHTML = `<i class="bi bi-download me-1"></i>${gettext('Yükle')}`;
        installBtn.title = gettext('Rumep\'i telefonunuza yükleyin');
        
        installBtn.addEventListener('click', installApp);
        document.body.appendChild(installBtn);
        
        // Auto hide after 10 seconds
        setTimeout(() => {
            if (installBtn.parentNode) {
                installBtn.style.opacity = '0.7';
            }
        }, 10000);
    }
    
    function hideInstallButton() {
        const installBtn = document.getElementById('pwa-install-btn');
        if (installBtn) {
            installBtn.remove();
        }
    }
    
    async function installApp() {
        if (!deferredPrompt) return;
        
        const installBtn = document.getElementById('pwa-install-btn');
        if (installBtn) {
            installBtn.disabled = true;
            installBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-1"></span>${gettext('Yükleniyor...')}`;
        }
        
        deferredPrompt.prompt();
        const { outcome } = await deferredPrompt.userChoice;
        
        if (outcome === 'accepted') {
            console.log('User accepted the install prompt');
        } else {
            console.log('User dismissed the install prompt');
            if (installBtn) {
                installBtn.disabled = false;
                installBtn.innerHTML = `<i class="bi bi-download me-1"></i>${gettext('Yükle')}`;
            }
        }
        
        deferredPrompt = null;
    }
    
    function showUpdateNotification() {
        const updateToast = document.createElement('div');
        updateToast.className = 'toast position-fixed';
        updateToast.style.cssText = 'bottom: 20px; right: 20px; z-index: 9999;';
        updateToast.innerHTML = `
            <div class="toast-header bg-info text-white">
                <strong class="me-auto">${gettext('Güncelleme Mevcut')}</strong>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                ${gettext('Yeni bir sürüm mevcut. Sayfayı yenileyin.')}
                <div class="mt-2">
                    <button class="btn btn-primary btn-sm" onclick="window.location.reload()">${gettext('Yenile')}</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(updateToast);
        const toast = new bootstrap.Toast(updateToast);
        toast.show();
    }
    
    function showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = 'toast position-fixed';
        toast.style.cssText = 'bottom: 20px; right: 20px; z-index: 9999;';
        
        const bgClass = type === 'success' ? 'bg-success' : type === 'error' ? 'bg-danger' : 'bg-info';
        
        toast.innerHTML = `
            <div class="toast-header ${bgClass} text-white">
                <strong class="me-auto">${gettext('Bilgi')}</strong>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        `;
        
        document.body.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 5000);
    }
    
    // Enhanced mobile experience
    if (isMobile()) {
        document.body.classList.add('mobile-device');
        
        // Prevent zoom on input focus (iOS)
        const inputs = document.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('focus', () => {
                const viewport = document.querySelector('meta[name="viewport"]');
                if (viewport) {
                    viewport.setAttribute('content', 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no');
                }
            });
            
            input.addEventListener('blur', () => {
                const viewport = document.querySelector('meta[name="viewport"]');
                if (viewport) {
                    viewport.setAttribute('content', 'width=device-width, initial-scale=1.0');
                }
            });
        });
        
        // Add touch feedback
        document.addEventListener('touchstart', function(e) {
            if (e.target.matches('button, .btn, a, .clickable')) {
                e.target.style.opacity = '0.7';
            }
        });
        
        document.addEventListener('touchend', function(e) {
            if (e.target.matches('button, .btn, a, .clickable')) {
                setTimeout(() => {
                    e.target.style.opacity = '';
                }, 150);
            }
        });
    }
    
    function isMobile() {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    }
});