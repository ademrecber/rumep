// Theme toggle functionality
document.addEventListener('DOMContentLoaded', () => {
    // Check for saved theme preference or respect OS preference
    const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
    const storedTheme = localStorage.getItem('theme');
    
    // Function to set theme
    const setTheme = (isDark) => {
        if (isDark) {
            document.documentElement.classList.add('dark-theme');
            localStorage.setItem('theme', 'dark');
        } else {
            document.documentElement.classList.remove('dark-theme');
            localStorage.setItem('theme', 'light');
        }
    };
    
    // Set initial theme based on stored preference or OS preference
    if (storedTheme === 'dark' || (storedTheme === null && prefersDarkScheme.matches)) {
        setTheme(true);
    } else {
        setTheme(false);
    }
    
    // Add theme toggle button to sidebar
    const sidebarNav = document.querySelector('.sidebar .nav');
    if (sidebarNav) {
        const themeToggleItem = document.createElement('li');
        themeToggleItem.className = 'nav-item';
        
        const themeToggleBtn = document.createElement('button');
        themeToggleBtn.className = 'nav-link text-start';
        themeToggleBtn.style.border = 'none';
        themeToggleBtn.style.background = 'none';
        themeToggleBtn.style.padding = '10px';
        themeToggleBtn.style.width = '100%';
        
        const updateButtonText = () => {
            const isDarkTheme = document.documentElement.classList.contains('dark-theme');
            themeToggleBtn.innerHTML = isDarkTheme ? 
                '<i class="bi bi-sun me-2"></i> Light' : 
                '<i class="bi bi-moon me-2"></i> Dark';
        };
        
        updateButtonText();
        
        themeToggleBtn.addEventListener('click', () => {
            const isDarkTheme = document.documentElement.classList.contains('dark-theme');
            setTheme(!isDarkTheme);
            updateButtonText();
        });
        
        themeToggleItem.appendChild(themeToggleBtn);
        sidebarNav.appendChild(themeToggleItem);
    }
    
    // Listen for OS theme changes
    prefersDarkScheme.addEventListener('change', (e) => {
        if (!localStorage.getItem('theme')) {
            setTheme(e.matches);
        }
    });
});