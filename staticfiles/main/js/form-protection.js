// Form Protection - Prevent double submission
document.addEventListener('DOMContentLoaded', function() {
    // Track submitted forms to prevent double submission
    const submittedForms = new Set();
    
    // Handle all forms with protection
    document.querySelectorAll('form').forEach(form => {
        // Skip if already protected
        if (form.hasAttribute('data-protected')) return;
        form.setAttribute('data-protected', 'true');
        
        form.addEventListener('submit', function(e) {
            const formId = this.id || this.action || 'default';
            const submitButton = this.querySelector('button[type="submit"]');
            
            // Check if already submitted
            if (submittedForms.has(formId)) {
                e.preventDefault();
                showToast(gettext('Form zaten gönderiliyor, lütfen bekleyin...'), 'warning');
                return false;
            }
            
            // Mark as submitted
            submittedForms.add(formId);
            
            // Disable submit button
            if (submitButton) {
                submitButton.disabled = true;
                const originalText = submitButton.textContent;
                submitButton.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span>${gettext('Gönderiliyor...')}`;
                
                // Re-enable after 5 seconds (fallback)
                setTimeout(() => {
                    submitButton.disabled = false;
                    submitButton.textContent = originalText;
                    submittedForms.delete(formId);
                }, 5000);
            }
            
            // Remove from submitted set after page navigation
            setTimeout(() => {
                submittedForms.delete(formId);
            }, 1000);
        });
    });
    
    // Handle AJAX forms separately
    document.addEventListener('click', function(e) {
        if (e.target.matches('.ajax-submit')) {
            const button = e.target;
            if (button.disabled) {
                e.preventDefault();
                return false;
            }
            
            button.disabled = true;
            const originalText = button.textContent;
            button.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span>${gettext('İşleniyor...')}`;
            
            setTimeout(() => {
                button.disabled = false;
                button.textContent = originalText;
            }, 3000);
        }
    });
    
    // Rate limit warning
    function showRateLimitWarning(remainingTime) {
        showToast(gettext('Çok hızlı işlem yapıyorsunuz. %(time)s saniye bekleyin.').replace('%(time)s', remainingTime), 'warning');
    }
    
    // Toast function
    function showToast(message, type = 'info') {
        // Remove existing toast
        const existingToast = document.querySelector('.protection-toast');
        if (existingToast) {
            existingToast.remove();
        }
        
        const toast = document.createElement('div');
        toast.className = `toast protection-toast show position-fixed`;
        toast.style.cssText = 'bottom: 20px; right: 20px; z-index: 9999;';
        
        const bgClass = type === 'warning' ? 'bg-warning' : type === 'error' ? 'bg-danger' : 'bg-info';
        
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
        
        // Auto hide after 4 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 4000);
    }
    
    // Global error handler for rate limiting
    window.addEventListener('unhandledrejection', function(e) {
        if (e.reason && e.reason.status === 429) {
            showToast(gettext('Çok fazla istek gönderiyorsunuz. Lütfen bekleyin.'), 'warning');
        }
    });
});