// Mobile Specific Functions
document.addEventListener('DOMContentLoaded', function() {
    // Active navigation highlighting
    highlightActiveNav();
    
    // Handle mobile navigation
    handleMobileNavigation();
});

function highlightActiveNav() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.mobile-bottom-nav a');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
}

function handleMobileNavigation() {
    // Smooth scrolling for mobile
    const mobileMain = document.querySelector('.mobile-main');
    if (mobileMain) {
        mobileMain.style.scrollBehavior = 'smooth';
    }
    
    // Handle back button
    window.addEventListener('popstate', function() {
        const sidebar = document.getElementById('mobileSidebar');
        const overlay = document.querySelector('.mobile-overlay');
        
        if (sidebar && sidebar.classList.contains('active')) {
            sidebar.classList.remove('active');
            overlay.classList.remove('active');
            document.body.style.overflow = '';
        }
    });
}