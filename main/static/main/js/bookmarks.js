// Bookmark functionality
document.addEventListener('DOMContentLoaded', function() {
    // Entry bookmark button click handler
    document.addEventListener('click', function(e) {
        if (e.target.closest('.bookmark-btn[data-entry-id]')) {
            e.preventDefault();
            const button = e.target.closest('.bookmark-btn[data-entry-id]');
            const entryId = button.dataset.entryId;
            const icon = button.querySelector('i');
            
            if (!entryId || entryId === 'undefined') {
                console.error('Entry ID is undefined');
                return;
            }
            
            fetch(`/bookmark/${entryId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    'Content-Type': 'application/json',
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.is_bookmarked) {
                    icon.className = 'bi bi-bookmark-fill';
                    button.classList.remove('text-muted');
                    button.classList.add('text-warning');
                } else {
                    icon.className = 'bi bi-bookmark';
                    button.classList.remove('text-warning');
                    button.classList.add('text-muted');
                    
                    // Remove from profile page if unbookmarked
                    if (window.location.pathname.includes('/profile/') && window.location.search.includes('tab=bookmarks')) {
                        const card = button.closest('.card');
                        if (card) {
                            card.style.transition = 'opacity 0.3s';
                            card.style.opacity = '0';
                            setTimeout(() => card.remove(), 300);
                        }
                    }
                }
            })
            .catch(error => console.error('Error:', error));
        }
    });
    
    // Topic bookmark button click handler
    document.addEventListener('click', function(e) {
        if (e.target.closest('.topic-bookmark-btn')) {
            e.preventDefault();
            const button = e.target.closest('.topic-bookmark-btn');
            const topicSlug = button.dataset.topicSlug;
            const icon = button.querySelector('i');
            
            if (!topicSlug || topicSlug === 'undefined') {
                console.error('Topic slug is undefined');
                return;
            }
            
            fetch(`/bookmark-topic/${topicSlug}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    'Content-Type': 'application/json',
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.is_bookmarked) {
                    icon.className = 'bi bi-bookmark-fill';
                    button.classList.remove('text-muted');
                    button.classList.add('text-warning');
                } else {
                    icon.className = 'bi bi-bookmark';
                    button.classList.remove('text-warning');
                    button.classList.add('text-muted');
                    
                    // Remove from profile page if unbookmarked
                    if (window.location.pathname.includes('/profile/') && window.location.search.includes('tab=bookmarks')) {
                        const card = button.closest('.card');
                        if (card) {
                            card.style.transition = 'opacity 0.3s';
                            card.style.opacity = '0';
                            setTimeout(() => card.remove(), 300);
                        }
                    }
                }
            })
            .catch(error => console.error('Error:', error));
        }
    });
});