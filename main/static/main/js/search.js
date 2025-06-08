// Search functionality
document.addEventListener('DOMContentLoaded', function() {
    const searchInputs = document.querySelectorAll('[data-search-input]');
    
    searchInputs.forEach(input => {
        const container = input.closest('.search-container');
        const suggestions = container.querySelector('[data-search-suggestions]');
        let debounceTimer;

        // Handle input changes
        input.addEventListener('input', function(e) {
            clearTimeout(debounceTimer);
            const query = e.target.value.trim();
            
            if (query.length < 2) {
                suggestions.classList.remove('active');
                return;
            }

            debounceTimer = setTimeout(() => {
                fetchSuggestions(query, suggestions);
            }, 300);
        });

        // Close suggestions on click outside
        document.addEventListener('click', function(e) {
            if (!container.contains(e.target)) {
                suggestions.classList.remove('active');
            }
        });

        // Handle keyboard navigation
        input.addEventListener('keydown', function(e) {
            if (!suggestions.classList.contains('active')) return;

            const items = suggestions.querySelectorAll('.search-suggestion-item');
            const activeItem = suggestions.querySelector('.search-suggestion-item.active');
            let index = -1;

            if (activeItem) {
                index = Array.from(items).indexOf(activeItem);
            }

            switch (e.key) {
                case 'ArrowDown':
                    e.preventDefault();
                    if (index < items.length - 1) {
                        if (activeItem) activeItem.classList.remove('active');
                        items[index + 1].classList.add('active');
                        items[index + 1].scrollIntoView({ block: 'nearest' });
                    }
                    break;
                case 'ArrowUp':
                    e.preventDefault();
                    if (index > 0) {
                        if (activeItem) activeItem.classList.remove('active');
                        items[index - 1].classList.add('active');
                        items[index - 1].scrollIntoView({ block: 'nearest' });
                    }
                    break;
                case 'Enter':
                    if (activeItem) {
                        e.preventDefault();
                        window.location.href = activeItem.dataset.url;
                    }
                    break;
                case 'Escape':
                    suggestions.classList.remove('active');
                    break;
            }
        });
    });
});

async function fetchSuggestions(query, suggestionsElement) {
    try {
        const response = await fetch(`/api/search/suggestions/?q=${encodeURIComponent(query)}`);
        if (!response.ok) throw new Error('Network response was not ok');
        
        const data = await response.json();
        
        if (data.suggestions && data.suggestions.length > 0) {
            renderSuggestions(data.suggestions, suggestionsElement);
            suggestionsElement.classList.add('active');
        } else {
            suggestionsElement.classList.remove('active');
        }
    } catch (error) {
        console.error('Error fetching suggestions:', error);
        suggestionsElement.classList.remove('active');
    }
}

function renderSuggestions(suggestions, element) {
    const html = suggestions.map(suggestion => `
        <div class="search-suggestion-item" data-url="${suggestion.url}">
            <div class="d-flex align-items-center">
                <i class="bi ${getIconForType(suggestion.type)} me-2"></i>
                <div>
                    <div class="fw-medium">${highlightMatch(suggestion.title)}</div>
                    ${suggestion.subtitle ? `<small class="text-muted">${suggestion.subtitle}</small>` : ''}
                </div>
            </div>
        </div>
    `).join('');
    
    element.innerHTML = html;

    // Add click handlers
    element.querySelectorAll('.search-suggestion-item').forEach(item => {
        item.addEventListener('click', () => {
            window.location.href = item.dataset.url;
        });
    });
}

function getIconForType(type) {
    const icons = {
        'post': 'bi-file-text',
        'user': 'bi-person',
        'tag': 'bi-tag',
        'category': 'bi-folder',
        'default': 'bi-search'
    };
    return icons[type] || icons.default;
}

function highlightMatch(text) {
    // Implementation can be added to highlight matching text portions
    return text;
}