// Initialize AOS
AOS.init({
    duration: 800,
    easing: 'ease-in-out',
    once: true
});

// Script para el menú móvil
document.addEventListener('DOMContentLoaded', function() {
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const mobileMenu = document.getElementById('mobileMenu');
    const overlay = document.getElementById('overlay');
    
    // Toggle del menú móvil
    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', function() {
            this.classList.toggle('active');
            mobileMenu.classList.toggle('active');
            overlay.classList.toggle('active');
            document.body.style.overflow = mobileMenu.classList.contains('active') ? 'hidden' : '';
        });
    }
    
    // Cerrar menú al hacer clic en overlay
    if (overlay) {
        overlay.addEventListener('click', function() {
            if (mobileMenuToggle) mobileMenuToggle.classList.remove('active');
            if (mobileMenu) mobileMenu.classList.remove('active');
            this.classList.remove('active');
            document.body.style.overflow = '';
        });
    }
    
    // Dropdowns en móvil
    const mobileDropdownToggles = document.querySelectorAll('.mobile-dropdown-toggle');
    
    mobileDropdownToggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            const targetMenu = document.getElementById(targetId);
            
            // Cerrar otros dropdowns abiertos
            document.querySelectorAll('.mobile-dropdown-menu.active').forEach(menu => {
                if (menu.id !== targetId) {
                    menu.classList.remove('active');
                }
            });
            
            // Toggle el dropdown actual
            if (targetMenu) {
                targetMenu.classList.toggle('active');
                
                // Rotar la flecha
                const arrow = this.querySelector('span');
                if (arrow) {
                    arrow.style.transform = targetMenu.classList.contains('active') ? 'rotate(180deg)' : 'rotate(0)';
                }
            }
        });
    });
    
    // Cerrar menú al hacer clic en un enlace
    const mobileLinks = document.querySelectorAll('.mobile-nav-link, .mobile-dropdown-item');
    
    mobileLinks.forEach(link => {
        link.addEventListener('click', function() {
            if (mobileMenuToggle) mobileMenuToggle.classList.remove('active');
            if (mobileMenu) mobileMenu.classList.remove('active');
            if (overlay) overlay.classList.remove('active');
            document.body.style.overflow = '';
        });
    });

    // Smooth scrolling para enlaces internos
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');
            if (!targetId || targetId === '#') return;

            const targetElement = document.querySelector(targetId);
            if (!targetElement) return;

            e.preventDefault();
            window.scrollTo({
                top: targetElement.offsetTop - 80,
                behavior: 'smooth'
            });
        });
    });
});