/**
 * Loading states ve error handling için JavaScript
 */

class LoadingManager {
    constructor() {
        this.activeRequests = new Set();
        this.init();
    }

    init() {
        // Form submit'lerde loading state
        document.addEventListener('submit', (e) => {
            if (e.target.tagName === 'FORM') {
                this.showFormLoading(e.target);
            }
        });

        // AJAX isteklerde loading state
        this.interceptFetch();
    }

    showFormLoading(form) {
        const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = true;
            const originalText = submitBtn.textContent || submitBtn.value;
            submitBtn.dataset.originalText = originalText;
            submitBtn.textContent = 'Yükleniyor...';
            submitBtn.classList.add('loading');
        }
    }

    hideFormLoading(form) {
        const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
        if (submitBtn && submitBtn.dataset.originalText) {
            submitBtn.disabled = false;
            submitBtn.textContent = submitBtn.dataset.originalText;
            submitBtn.classList.remove('loading');
        }
    }

    showPageLoading() {
        let loader = document.getElementById('page-loader');
        if (!loader) {
            loader = document.createElement('div');
            loader.id = 'page-loader';
            loader.innerHTML = `
                <div class="loader-overlay">
                    <div class="loader-spinner"></div>
                    <div class="loader-text">Yükleniyor...</div>
                </div>
            `;
            document.body.appendChild(loader);
        }
        loader.style.display = 'flex';
    }

    hidePageLoading() {
        const loader = document.getElementById('page-loader');
        if (loader) {
            loader.style.display = 'none';
        }
    }

    interceptFetch() {
        const originalFetch = window.fetch;
        const self = this;

        window.fetch = function(...args) {
            const requestId = Math.random().toString(36);
            self.activeRequests.add(requestId);
            
            if (self.activeRequests.size === 1) {
                self.showPageLoading();
            }

            return originalFetch.apply(this, args)
                .then(response => {
                    self.activeRequests.delete(requestId);
                    if (self.activeRequests.size === 0) {
                        self.hidePageLoading();
                    }
                    return response;
                })
                .catch(error => {
                    self.activeRequests.delete(requestId);
                    if (self.activeRequests.size === 0) {
                        self.hidePageLoading();
                    }
                    self.handleError(error);
                    throw error;
                });
        };
    }

    handleError(error) {
        console.error('Request error:', error);
        this.showErrorMessage('Bir hata oluştu. Lütfen tekrar deneyin.');
    }

    showErrorMessage(message, type = 'error') {
        const errorDiv = document.createElement('div');
        errorDiv.className = `alert alert-${type} alert-dismissible`;
        errorDiv.innerHTML = `
            <span>${message}</span>
            <button type="button" class="close" onclick="this.parentElement.remove()">×</button>
        `;
        
        // Sayfanın üstüne ekle
        const container = document.querySelector('.container') || document.body;
        container.insertBefore(errorDiv, container.firstChild);
        
        // 5 saniye sonra otomatik kapat
        setTimeout(() => {
            if (errorDiv.parentElement) {
                errorDiv.remove();
            }
        }, 5000);
    }

    showSuccessMessage(message) {
        this.showErrorMessage(message, 'success');
    }
}

// Global loading manager
const loadingManager = new LoadingManager();

// Utility functions
window.showLoading = () => loadingManager.showPageLoading();
window.hideLoading = () => loadingManager.hidePageLoading();
window.showError = (msg) => loadingManager.showErrorMessage(msg);
window.showSuccess = (msg) => loadingManager.showSuccessMessage(msg);