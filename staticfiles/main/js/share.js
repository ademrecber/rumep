// Share functionality - Simplified
document.addEventListener('DOMContentLoaded', function() {
    
    // Share button handlers
    document.addEventListener('click', function(e) {
        const btn = e.target.closest('.share-btn');
        if (!btn) return;
        
        e.preventDefault();
        e.stopPropagation();
        
        if (btn.classList.contains('share-twitter')) {
            shareToTwitter(btn);
        } else if (btn.classList.contains('share-whatsapp')) {
            shareToWhatsApp(btn);
        } else if (btn.classList.contains('share-telegram')) {
            shareToTelegram(btn);
        } else if (btn.classList.contains('copy-link')) {
            copyLink(btn);
        } else if (btn.classList.contains('copy-code')) {
            copyCode(btn);
        } else if (btn.classList.contains('share-qr')) {
            showQRCode(btn);
        }
    });
    
    function getShareData(button) {
        const card = button.closest('.topic-card') || button.closest('.entry-item') || button.closest('.card');
        const title = card.querySelector('.card-title')?.textContent?.trim() || 'Rumep';
        const content = card.querySelector('.first-entry-preview')?.textContent?.trim() || '';
        const url = window.location.href;
        
        const topicCode = button.getAttribute('data-topic-code');
        const entryCode = button.getAttribute('data-entry-code');
        const code = topicCode || entryCode;
        
        return {
            title: title,
            content: content.substring(0, 100) + (content.length > 100 ? '...' : ''),
            url: url,
            code: code ? ` #${code}` : ''
        };
    }
    
    function shareToTwitter(button) {
        const data = getShareData(button);
        const text = `${data.title}\n\n${data.content}${data.code}`;
        const url = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(data.url)}`;
        window.open(url, '_blank', 'width=600,height=400');
    }
    
    function shareToWhatsApp(button) {
        const data = getShareData(button);
        const text = `*${data.title}*\n\n${data.content}${data.code}\n\n${data.url}`;
        const url = `https://wa.me/?text=${encodeURIComponent(text)}`;
        window.open(url, '_blank');
    }
    
    function shareToTelegram(button) {
        const data = getShareData(button);
        const text = `${data.title}\n\n${data.content}${data.code}`;
        const url = `https://t.me/share/url?url=${encodeURIComponent(data.url)}&text=${encodeURIComponent(text)}`;
        window.open(url, '_blank');
    }
    
    function copyLink(button) {
        const data = getShareData(button);
        copyToClipboard(data.url);
    }
    
    function copyCode(button) {
        const topicCode = button.getAttribute('data-topic-code');
        const entryCode = button.getAttribute('data-entry-code');
        const code = topicCode || entryCode;
        if (code) {
            copyToClipboard(`#${code}`);
        }
    }
    
    function copyToClipboard(text) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text).then(() => {
                showToast('Kopyalandı');
            }).catch(() => {
                fallbackCopy(text);
            });
        } else {
            fallbackCopy(text);
        }
    }
    
    function fallbackCopy(text) {
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        try {
            document.execCommand('copy');
            showToast('Kopyalandı');
        } catch (err) {
            showToast('Kopyalama başarısız');
        }
        document.body.removeChild(textarea);
    }
    
    function showQRCode(button) {
        const data = getShareData(button);
        
        // Remove existing QR modal
        const existingModal = document.getElementById('qrModal');
        if (existingModal) {
            existingModal.remove();
        }
        
        const modal = document.createElement('div');
        modal.id = 'qrModal';
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">QR Kod</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body text-center">
                        <img src="https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(data.url)}" 
                             alt="QR Code" class="img-fluid" style="max-width: 200px;">
                        <p class="mt-3 text-muted">QR kodu tarayarak bu sayfaya ulaşabilirsiniz</p>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
        
        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
        });
    }
    
    function showToast(message) {
        // Remove existing toast
        const existingToast = document.querySelector('.custom-toast');
        if (existingToast) {
            existingToast.remove();
        }
        
        const toast = document.createElement('div');
        toast.className = 'custom-toast';
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #28a745;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            z-index: 9999;
            font-size: 14px;
        `;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 2000);
    }
});