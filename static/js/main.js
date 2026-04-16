document.addEventListener('DOMContentLoaded', () => {

    // Hamburger menu
    const hamburgerBtn = document.getElementById('hamburgerBtn');
    const navMenu = document.getElementById('navMenu');

    if (hamburgerBtn && navMenu) {
        hamburgerBtn.addEventListener('click', () => {
            navMenu.classList.toggle('open');
        });
    }

    // User dropdown
    const userDropdownToggle = document.getElementById('userDropdownToggle');

    if (userDropdownToggle) {
        userDropdownToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            userDropdownToggle.classList.toggle('open');
        });

        document.addEventListener('click', () => {
            userDropdownToggle.classList.remove('open');
        });
    }

    const flashes = document.querySelectorAll('.auth__alert');
    flashes.forEach(flash => {
        setTimeout(() => {
            flash.style.opacity = '0';
            flash.style.transform = 'translateX(20px)';
            flash.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
            setTimeout(() => flash.remove(), 300);
        }, 5000);
    });

});