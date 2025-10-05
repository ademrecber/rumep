// Mobile Sidebar Functions
function toggleMobileSidebar() {
    const sidebar = document.getElementById('mobileSidebar');
    const overlay = document.querySelector('.mobile-overlay');
    
    if (sidebar && overlay) {
        sidebar.classList.toggle('active');
        overlay.classList.toggle('active');
        
        // Prevent body scroll when sidebar is open
        if (sidebar.classList.contains('active')) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = '';
        }
    }
}

// Close sidebar when clicking on overlay
document.addEventListener('DOMContentLoaded', function() {
    const overlay = document.querySelector('.mobile-overlay');
    if (overlay) {
        overlay.addEventListener('click', toggleMobileSidebar);
    }
});