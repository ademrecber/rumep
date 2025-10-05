// Advanced Search JavaScript
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    const suggestionsContainer = document.getElementById('searchSuggestions');
    let searchTimeout;
    
    if (searchInput && suggestionsContainer) {
        // Search suggestions
        searchInput.addEventListener('input', function() {
            const query = this.value.trim();
            
            clearTimeout(searchTimeout);
            
            if (query.length < 2) {
                hideSuggestions();
                return;
            }
            
            searchTimeout = setTimeout(() => {
                fetchSuggestions(query);
            }, 300);
        });
        
        // Hide suggestions when clicking outside
        document.addEventListener('click', function(e) {
            if (!searchInput.contains(e.target) && !suggestionsContainer.contains(e.target)) {
                hideSuggestions();
            }
        });
        
        // Handle keyboard navigation
        searchInput.addEventListener('keydown', function(e) {
            const suggestions = suggestionsContainer.querySelectorAll('.suggestion-item');
            const activeSuggestion = suggestionsContainer.querySelector('.suggestion-item.active');
            
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                if (activeSuggestion) {
                    activeSuggestion.classList.remove('active');
                    const next = activeSuggestion.nextElementSibling;
                    if (next) {
                        next.classList.add('active');
                    } else {
                        suggestions[0]?.classList.add('active');
                    }
                } else {
                    suggestions[0]?.classList.add('active');
                }
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                if (activeSuggestion) {
                    activeSuggestion.classList.remove('active');
                    const prev = activeSuggestion.previousElementSibling;
                    if (prev) {
                        prev.classList.add('active');
                    } else {
                        suggestions[suggestions.length - 1]?.classList.add('active');
                    }
                } else {
                    suggestions[suggestions.length - 1]?.classList.add('active');
                }
            } else if (e.key === 'Enter') {
                if (activeSuggestion) {
                    e.preventDefault();
                    const link = activeSuggestion.querySelector('a');
                    if (link) {
                        window.location.href = link.href;
                    }
                }
            } else if (e.key === 'Escape') {
                hideSuggestions();
            }
        });
    }
    
    function fetchSuggestions(query) {
        fetch(`/search/suggestions/?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                showSuggestions(data.suggestions);
            })
            .catch(error => {
                console.error('Search suggestions error:', error);
                hideSuggestions();
            });
    }
    
    function showSuggestions(suggestions) {
        if (suggestions.length === 0) {
            hideSuggestions();
            return;
        }
        
        const html = suggestions.map(suggestion => `
            <div class="suggestion-item p-2 border-bottom">
                <a href="${suggestion.url}" class="text-decoration-none d-flex align-items-center">
                    <i class="${suggestion.icon} me-2 text-muted"></i>
                    <span>${suggestion.text}</span>
                    <small class="ms-auto text-muted">${suggestion.type}</small>
                </a>
            </div>
        `).join('');
        
        suggestionsContainer.innerHTML = html;
        suggestionsContainer.style.display = 'block';
        
        // Position suggestions below input
        const inputRect = searchInput.getBoundingClientRect();
        suggestionsContainer.style.top = `${inputRect.bottom + window.scrollY}px`;
        suggestionsContainer.style.left = `${inputRect.left}px`;
        suggestionsContainer.style.width = `${inputRect.width}px`;
        
        // Add hover effects
        suggestionsContainer.querySelectorAll('.suggestion-item').forEach(item => {
            item.addEventListener('mouseenter', function() {
                // Remove active from all
                suggestionsContainer.querySelectorAll('.suggestion-item').forEach(i => {
                    i.classList.remove('active');
                });
                // Add active to this
                this.classList.add('active');
            });
        });
    }
    
    function hideSuggestions() {
        suggestionsContainer.style.display = 'none';
        suggestionsContainer.innerHTML = '';
    }
    
    // Auto-submit form when filters change
    document.querySelectorAll('select[name="type"], select[name="date"]').forEach(select => {
        select.addEventListener('change', function() {
            if (searchInput.value.trim()) {
                this.closest('form').submit();
            }
        });
    });
    
    // Search history (localStorage)
    function saveSearchHistory(query) {
        if (!query.trim()) return;
        
        let history = JSON.parse(localStorage.getItem('searchHistory') || '[]');
        
        // Remove if already exists
        history = history.filter(item => item !== query);
        
        // Add to beginning
        history.unshift(query);
        
        // Keep only last 10
        history = history.slice(0, 10);
        
        localStorage.setItem('searchHistory', JSON.stringify(history));
    }
    
    function loadSearchHistory() {
        return JSON.parse(localStorage.getItem('searchHistory') || '[]');
    }
    
    // Save search when form is submitted
    document.querySelector('.search-form')?.addEventListener('submit', function() {
        const query = searchInput.value.trim();
        if (query) {
            saveSearchHistory(query);
        }
    });
    
    // Show search history when input is focused and empty
    searchInput?.addEventListener('focus', function() {
        if (!this.value.trim()) {
            const history = loadSearchHistory();
            if (history.length > 0) {
                const suggestions = history.map(query => ({
                    type: 'history',
                    text: query,
                    url: `?q=${encodeURIComponent(query)}`,
                    icon: 'bi-clock-history'
                }));
                showSuggestions(suggestions);
            }
        }
    });
});