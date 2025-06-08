function initShowMore() {
    function bindShowMoreEvents() {
        document.querySelectorAll('.show-more-btn').forEach(button => {
            if (!button.classList.contains('bound')) {
                button.addEventListener('click', function() {
                    const parent = this.closest('.post-text');
                    const preview = parent.querySelector('.text-preview');
                    const fullText = parent.querySelector('.full-text');
                    if (preview && fullText) {
                        preview.classList.add('d-none');
                        fullText.classList.remove('d-none');
                        this.classList.add('d-none'); // "Devamını gör" gizle
                        const lessBtn = parent.querySelector('.show-less-btn');
                        if (lessBtn) lessBtn.classList.remove('d-none');
                    }
                });
                button.classList.add('bound');
            }
        });

        document.querySelectorAll('.show-less-btn').forEach(button => {
            if (!button.classList.contains('bound')) {
                button.addEventListener('click', function() {
                    const parent = this.closest('.post-text');
                    const preview = parent.querySelector('.text-preview');
                    const fullText = parent.querySelector('.full-text');
                    if (preview && fullText) {
                        preview.classList.remove('d-none');
                        fullText.classList.add('d-none');
                        this.classList.add('d-none'); // "Daha az gör" gizle
                        const moreBtn = parent.querySelector('.show-more-btn');
                        if (moreBtn) moreBtn.classList.remove('d-none');
                    }
                });
                button.classList.add('bound');
            }
        });
    }

    bindShowMoreEvents();
    const observer = new MutationObserver(() => bindShowMoreEvents());
    observer.observe(document.body, { childList: true, subtree: true });
}

export { initShowMore };