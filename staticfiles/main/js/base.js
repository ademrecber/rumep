// Global Font Auto-Apply
document.addEventListener('DOMContentLoaded', function() {
    // Auto-apply fonts from inline styles
    document.querySelectorAll('[style*="font-family"]').forEach(el => {
        const style = el.getAttribute('style');
        if (style && (style.includes('RumepLogosSVG') || style.includes('RumepLogosCOLR'))) {
            el.style.fontFamily = style.match(/font-family:\s*([^;]+)/)?.[1] || '';
        }
    });
    
    // Watch for new content
    const observer = new MutationObserver(mutations => {
        mutations.forEach(mutation => {
            mutation.addedNodes.forEach(node => {
                if (node.nodeType === 1 && node.hasAttribute && node.hasAttribute('style')) {
                    const style = node.getAttribute('style');
                    if (style && (style.includes('RumepLogosSVG') || style.includes('RumepLogosCOLR'))) {
                        node.style.fontFamily = style.match(/font-family:\s*([^;]+)/)?.[1] || '';
                    }
                }
            });
        });
    });
    observer.observe(document.body, { childList: true, subtree: true });
});

function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.querySelector('.sidebar-overlay');
    
    if (sidebar) {
        sidebar.classList.toggle('active');
    }
    if (overlay) {
        overlay.classList.toggle('active');
    }
    
    // Prevent body scroll when sidebar is open
    if (sidebar && sidebar.classList.contains('active')) {
        document.body.style.overflow = 'hidden';
    } else {
        document.body.style.overflow = '';
    }
}

// Prevent page jumping on bottom nav clicks
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.bottom-nav a').forEach(link => {
        link.addEventListener('click', function(e) {
            // Allow navigation but prevent any jumping
            const currentScroll = window.pageYOffset;
            setTimeout(() => {
                window.scrollTo(0, currentScroll);
            }, 0);
        });
    });
    
    // Yeni sekme sistemi için JavaScript
    initializeTabSystem();
});

// Sekme sistemi fonksiyonu
function initializeTabSystem() {
    // Sayfa sekmelerini yönet
    document.querySelectorAll('.tab-link').forEach(tabLink => {
        tabLink.addEventListener('click', function(e) {
            e.preventDefault();
            
            const tabName = this.dataset.tab;
            if (!tabName) return;
            
            // Aktif sekmeyi güncelle
            document.querySelectorAll('.tab-link').forEach(link => {
                link.classList.remove('active');
            });
            this.classList.add('active');
            
            // İçeriği göster/gizle
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.add('d-none');
            });
            
            const targetContent = document.getElementById(tabName + '-tab');
            if (targetContent) {
                targetContent.classList.remove('d-none');
            }
            
            // URL'yi güncelle (isteğe bağlı)
            const url = new URL(window.location);
            if (tabName === 'home') {
                url.searchParams.delete('tab');
            } else {
                url.searchParams.set('tab', tabName);
            }
            window.history.pushState({}, '', url);
        });
    });
    
    // Eski tab-btn sistemi ile uyumluluk
    document.querySelectorAll('.tab-btn').forEach(tabBtn => {
        tabBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            const tabName = this.dataset.tab;
            if (!tabName) return;
            
            // Aktif tab-btn'i güncelle
            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.classList.remove('border-bottom', 'border-primary', 'border-3', 'fw-bold');
                btn.style.color = '#6c757d';
            });
            this.classList.add('border-bottom', 'border-primary', 'border-3', 'fw-bold');
            this.style.color = '#0d6efd';
            
            // İçeriği göster/gizle
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.add('d-none');
            });
            
            const targetContent = document.getElementById(tabName + '-tab');
            if (targetContent) {
                targetContent.classList.remove('d-none');
            }
        });
    });
}