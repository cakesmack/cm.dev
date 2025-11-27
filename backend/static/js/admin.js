// Mobile menu toggle
const mobileMenuBtn = document.getElementById('mobile-admin-menu-btn');
const mobileMenu = document.getElementById('mobile-admin-menu');
const mobileMenuPanel = document.getElementById('mobile-admin-menu-panel');

if (mobileMenuBtn && mobileMenu && mobileMenuPanel) {
    // Open menu
    mobileMenuBtn.addEventListener('click', () => {
        mobileMenu.classList.remove('hidden');
        // Small delay for smooth animation
        setTimeout(() => {
            mobileMenuPanel.classList.remove('-translate-x-full');
        }, 10);
        // Re-initialize Lucide icons for mobile menu
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    });

    // Close menu when clicking overlay
    mobileMenu.addEventListener('click', (e) => {
        if (e.target === mobileMenu) {
            mobileMenuPanel.classList.add('-translate-x-full');
            setTimeout(() => {
                mobileMenu.classList.add('hidden');
            }, 300);
        }
    });

    // Close menu when clicking a link
    mobileMenuPanel.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
            mobileMenuPanel.classList.add('-translate-x-full');
            setTimeout(() => {
                mobileMenu.classList.add('hidden');
            }, 300);
        });
    });
}

// Format currency
function formatCurrency(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
    }).format(amount);
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}
