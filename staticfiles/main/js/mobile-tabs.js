// Mobil sekme sistemi için JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Sekme geçişleri
    const tabLinks = document.querySelectorAll('.tab-link');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetTab = this.dataset.tab;
            
            // Aktif sekmeyi güncelle
            tabLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
            
            // İçerikleri göster/gizle
            tabContents.forEach(content => {
                content.classList.add('d-none');
            });
            
            const targetContent = document.getElementById(targetTab + '-tab');
            if (targetContent) {
                targetContent.classList.remove('d-none');
            }
        });
    });
    
    // Mobilde sekme kaydırma
    const tabsContainer = document.querySelector('.page-tabs');
    if (tabsContainer) {
        let isScrolling = false;
        
        tabsContainer.addEventListener('touchstart', function() {
            isScrolling = false;
        });
        
        tabsContainer.addEventListener('touchmove', function() {
            isScrolling = true;
        });
        
        tabsContainer.addEventListener('touchend', function() {
            if (!isScrolling) {
                // Tıklama işlemi
            }
        });
    }
    
    // Aktif sekmeyi ortala (mobilde)
    function centerActiveTab() {
        const activeTab = document.querySelector('.tab-link.active');
        const tabsContainer = document.querySelector('.page-tabs');
        
        if (activeTab && tabsContainer && window.innerWidth <= 768) {
            const containerWidth = tabsContainer.offsetWidth;
            const tabWidth = activeTab.offsetWidth;
            const tabOffset = activeTab.offsetLeft;
            
            const scrollLeft = tabOffset - (containerWidth / 2) + (tabWidth / 2);
            
            tabsContainer.scrollTo({
                left: scrollLeft,
                behavior: 'smooth'
            });
        }
    }
    
    // Sayfa yüklendiğinde aktif sekmeyi ortala
    centerActiveTab();
    
    // Sekme değiştiğinde ortala
    tabLinks.forEach(link => {
        link.addEventListener('click', function() {
            setTimeout(centerActiveTab, 100);
        });
    });
});