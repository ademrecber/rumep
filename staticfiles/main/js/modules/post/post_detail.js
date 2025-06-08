export function initPostDetail() {
    // Buton toggle mantığı
    const toggleFunction = () => {
        console.log('Toggle butonuna basıldı');
        const critiqueSection = document.getElementById('critique-section');
        if (critiqueSection) {
            critiqueSection.style.display = critiqueSection.style.display === 'none' ? 'block' : 'none';
            console.log('critique-section görünürlüğü:', critiqueSection.style.display);
        } else {
            console.error('critique-section bulunamadı');
        }
    };

    // İptal butonu mantığı
    const handleCancel = () => {
        console.log('İptal butonuna basıldı');
        const critiqueSection = document.getElementById('critique-section');
        const form = document.getElementById('critique-form');
        if (critiqueSection) critiqueSection.style.display = 'none';
        if (form) form.reset();
    };

    // Olay dinleyicilerini bağla
    const bindToggleEvents = () => {
        const toggleBtn = document.getElementById('toggle-critique-btn');
        const mobileToggleBtn = document.getElementById('mobile-toggle-critique-btn');
        if (toggleBtn) {
            toggleBtn.removeEventListener('click', toggleFunction);
            toggleBtn.addEventListener('click', toggleFunction);
            toggleBtn.style.display = 'block'; // Görünürlüğü garanti et
            console.log('toggle-critique-btn olay dinleyicisi eklendi');
        } else {
            console.warn('toggle-critique-btn bulunamadı');
        }
        if (mobileToggleBtn) {
            mobileToggleBtn.removeEventListener('click', toggleFunction);
            mobileToggleBtn.addEventListener('click', toggleFunction);
            mobileToggleBtn.style.display = 'block'; // Görünürlüğü garanti et
            console.log('mobile-toggle-critique-btn olay dinleyicisi eklendi');
        } else {
            console.warn('mobile-toggle-critique-btn bulunamadı');
        }
    };

    // İptal butonu olay dinleyicisi
    const bindCancelEvent = () => {
        const cancelBtn = document.getElementById('cancel-critique-btn');
        if (cancelBtn) {
            cancelBtn.removeEventListener('click', handleCancel);
            cancelBtn.addEventListener('click', handleCancel);
            console.log('cancel-critique-btn olay dinleyicisi eklendi');
        } else {
            console.warn('cancel-critique-btn bulunamadı');
        }
    };

    // İlk yüklemede bağla
    bindToggleEvents();
    bindCancelEvent();

    // Dinamik yüklemelerde tekrar bağla
    document.addEventListener('critiquesLoaded', () => {
        bindToggleEvents();
        bindCancelEvent();
    });
}