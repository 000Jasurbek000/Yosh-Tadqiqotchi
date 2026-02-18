// Header HTML template
const headerTemplate = `
<!-- Top Bar -->
<div class="header-top-bar">
    <div class="contact-links">
        <a href="mailto:u.m.xalikova@buxdu.uz">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>
            <span>u.m.xalikova@buxdu.uz</span>
        </a>
        <a href="tel:+998973056220">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
            <span>(97)305-62-20</span>
        </a>
    </div>
    <div style="display: flex; align-items: center; gap: 8px;" class="text-muted">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>
        <span>Buxoro sh. M.Iqbol ko'chasi 11-uy</span>
    </div>
</div>

<!-- Main Navbar -->
<nav class="header-main-nav">
    <div class="nav-container">
        <a href="index.html" class="logo">
            <img src="./assets/logo.svg" alt="logo"/>
        </a>

        <div class="nav-links">
            <a href="index.html">Bosh Sahifa</a>
            <a href="courses.html">Online Kurslar</a>
            
            <div class="dropdown">
                <button>
                    <span>Iqtidorli Talabamisiz?</span>
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m6 9 6 6 6-6"/></svg>
                </button>
                <div class="dropdown-menu">
                    <a href="iqtidorli-sorovnoma.html">So'rovnoma</a>
                    <a href="iqtidorli-test.html">Saralash testi</a>
                    <a href="iqtidorli-baza.html">Iqtidorli talabalar bazasi</a>
                </div>
            </div>
            
            <div class="dropdown">
                <button>
                    <span>Imtiyozli stipendiyalar</span>
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m6 9 6 6 6-6"/></svg>
                </button>
                <div class="dropdown-menu">
                    <a href="davlat-stipendiyalari.html">Davlat stipendiyalari</a>
                    <a href="buxdu-stipendiyalari.html">BuxDU stipendiyalari</a>
                    <a href="buxdu-stipendiya-bazasi.html">BuxDU stipendiya sovrindorlari bazasi</a>
                </div>
            </div>
            
            <div class="dropdown">
                <button>
                    <span>Xalqaro grant va olimpiadalar</span>
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m6 9 6 6 6-6"/></svg>
                </button>
                <div class="dropdown-menu">
                    <a href="#">Xalqaro grantlar, almashinuv dasturlari</a>
                    <a href="olimpiadalar.html">Xalqaro fan olimpiadalari</a>
                    <a href="buxdu-olimpiada-goliblari.html">BuxDU olimpiada g'oliblari</a>
                    <a href="#">Respublika fan olimpiadalari</a>
                    <a href="#">Nufuzli tanlovlar</a>
                    <a href="#">Onlayn fan olimpiadalari</a>
                    <a href="buxdu-olimpiadalari.html">BuxDU olimpiadalari</a>

                </div>

                
            </div>
            
            <div class="dropdown">
                <button>
                    <span>Ilmiy nashrlar va bazalar</span>
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m6 9 6 6 6-6"/></svg>
                </button>
                <div class="dropdown-menu">
                    <a href="mahalliy-oak-jurnallari.html">Mahalliy OAK jurnallari</a>
                    <a href="xalqaro-oak-jurnallari.html">Xalqaro OAK jurnallari</a>
                    <a href="xalqaro-konferensiyalar.html">Xalqaro konferensiyalar</a>
                    <a href="respublika-konferensiyalar.html">Respublika konferensiyalar</a>
                    <a href="dissertatsiyalar-banki.html">Dissertatsiyalar banki</a>
                    <a href="maqolalar-banki.html">Maqolalar banki</a>
                </div>
            </div>
            
            <div class="dropdown">
                <button>
                    <span>Xizmatlar</span>
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m6 9 6 6 6-6"/></svg>
                </button>
                <div class="dropdown-menu">
                    <a href="service.html">Maqola tahriri va tarjima xizmati</a>
                    <a href="maqola-jurnal-tavsiyasi.html">Maqola mazmuniga mos jurnalni tavsiya etish</a>
                    <a href="ilmiy-nizomlar.html">Ilmiy tadqiqotchilar uchun nizomlar</a>
                </div>
            </div>
        </div>

        <div style="display: flex; align-items: center; gap: 16px;">
            <button id="theme-toggle" class="theme-toggle-btn" title="Rangni o'zgartirish">
                <svg id="theme-icon-sun" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display: none;">
                    <circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
                </svg>
                <svg id="theme-icon-moon" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
                </svg>
            </button>
            <a href="login.html" id="auth-button" class="auth-btn">Tizimga kirish</a>
            <button id="open-menu" class="mobile-menu-btn">
                <svg xmlns="http://www.w3.org/2000/svg" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 5h16"/><path d="M4 12h16"/><path d="M4 19h16"/></svg>
            </button>
        </div>
    </div>
</nav>

<!-- Mobile Menu -->
<div id="mobile-navlinks" class="mobile-menu">
    <a href="index.html">Bosh Sahifa</a>
    <a href="courses.html">Online Kurslar</a>
    <a href="iqtidorli-test.html">Iqtidorli Talabamisiz?</a>
    <a href="davlat-stipendiyalari.html">Davlat stipendiyalari</a>
    <a href="buxdu-stipendiyalari.html">BuxDU stipendiyalari</a>
    <a href="buxdu-stipendiya-bazasi.html">BuxDU stipendiya sovrindorlari</a>
    <a href="#">Xalqaro grant va olimpiadalar</a>
    <a href="buxdu-olimpiada-goliblari.html">BuxDU olimpiada g'oliblari</a>
    <a href="buxdu-olimpiadalari.html">BuxDU olimpiadalari</a>
    <a href="mahalliy-oak-jurnallari.html">Mahalliy OAK jurnallari</a>
    <a href="xalqaro-oak-jurnallari.html">Xalqaro OAK jurnallari</a>
    <a href="xalqaro-konferensiyalar.html">Xalqaro konferensiyalar</a>
    <a href="respublika-konferensiyalar.html">Respublika konferensiyalar</a>
    <a href="dissertatsiyalar-banki.html">Dissertatsiyalar banki</a>
    <a href="maqolalar-banki.html">Maqolalar banki</a>
    <a href="service.html">Xizmatlar</a>
    <a href="maqola-jurnal-tavsiyasi.html">Maqola mazmuniga mos jurnalni tavsiya etish</a>
    <a href="ilmiy-nizomlar.html">Ilmiy tadqiqotchilar uchun nizomlar</a>
    <a href="login.html" id="mobile-auth-button" class="auth-btn" style="margin-top: 16px;">Tizimga kirish</a>
    <button id="close-menu" class="close-btn">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
    </button>
</div>
`;

// Load header
function loadHeader() {
    const container = document.getElementById('header-container');
    if (container) {
        container.innerHTML = headerTemplate;
        updateAuthButton();
        initMobileMenu();
    }
}

// Update auth button based on page
function updateAuthButton() {
    const currentPage = window.location.pathname.split('/').pop();
    const authButton = document.getElementById('auth-button');
    const mobileAuthButton = document.getElementById('mobile-auth-button');
    
    if (currentPage === 'login.html') {
        if (authButton) {
            authButton.href = 'register.html';
            authButton.textContent = 'Ro\'yxatdan o\'tish';
        }
        if (mobileAuthButton) {
            mobileAuthButton.href = 'register.html';
            mobileAuthButton.textContent = 'Ro\'yxatdan o\'tish';
        }
    } else if (currentPage === 'register.html') {
        if (authButton) {
            authButton.href = 'login.html';
            authButton.textContent = 'Tizimga kirish';
        }
        if (mobileAuthButton) {
            mobileAuthButton.href = 'login.html';
            mobileAuthButton.textContent = 'Tizimga kirish';
        }
    }
}

// Initialize mobile menu
function initMobileMenu() {
    const openMenu = document.getElementById("open-menu");
    const closeMenu = document.getElementById("close-menu");
    const navlinks = document.getElementById("mobile-navlinks");

    if (openMenu && closeMenu && navlinks) {
        openMenu.addEventListener("click", () => {
            navlinks.classList.add("active");
        });

        closeMenu.addEventListener("click", () => {
            navlinks.classList.remove("active");
        });
    }
}

// Handle scroll effect
function initScrollEffect() {
    const topBar = document.querySelector('.header-top-bar');
    const mainNav = document.querySelector('.header-main-nav');
    
    if (!topBar || !mainNav) return;
    
    window.addEventListener('scroll', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
        
        if (window.scrollY > 50) {
            // Scroll bo'lganda
            topBar.style.transform = 'translateY(-100%)';
            topBar.style.opacity = '0';
            mainNav.style.top = '0';
            
            // Theme-aware background
            if (currentTheme === 'light') {
                mainNav.style.background = 'rgba(255, 255, 255, 0.98)';
                mainNav.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.15)';
            } else {
                mainNav.style.background = 'rgba(15, 23, 42, 0.95)';
                mainNav.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.3)';
            }
            mainNav.style.backdropFilter = 'blur(10px)';
        } else {
            // Yuqorida bo'lganda
            topBar.style.transform = 'translateY(0)';
            topBar.style.opacity = '1';
            mainNav.style.top = '40px';
            
            // Theme-aware background
            if (currentTheme === 'light') {
                mainNav.style.background = 'rgba(255, 255, 255, 0.95)';
                mainNav.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.08)';
            } else {
                mainNav.style.background = 'rgb(30, 41, 59)';
                mainNav.style.boxShadow = 'none';
            }
            mainNav.style.backdropFilter = 'blur(24px)';
        }
    });
}

// Preloader init
function initPreloader() {
    if (document.getElementById('global-preloader')) return;
    const preloader = document.createElement('div');
    preloader.id = 'global-preloader';
    preloader.className = 'preloader-overlay';
    preloader.innerHTML = `
        <div class="preloader-inner">
            <div class="preloader-spinner">
                <span></span><span></span><span></span><span></span>
            </div>
            <p class="preloader-text">Yuklanmoqda...</p>
        </div>
    `;
    document.body.appendChild(preloader);

    function hidePreloader() {
        if (!preloader.classList.contains('preloader-hidden')) {
            preloader.classList.add('preloader-hidden');
            setTimeout(() => {
                preloader.remove();
            }, 500);
        }
    }

    if (document.readyState === 'complete') {
        hidePreloader();
    } else {
        window.addEventListener('load', hidePreloader);
        // Fallback: maksimal 5 soniyadan keyin ham yashirish
        setTimeout(hidePreloader, 5000);
    }
}

// Load when DOM ready
document.addEventListener('DOMContentLoaded', () => {
    initPreloader();
    loadHeader();
    // Scroll effektni headerdan keyin ishga tushirish
    setTimeout(initScrollEffect, 100);
    setTimeout(initThemeToggle, 100);
});

// Theme toggle functionality
function initThemeToggle() {
    const toggleBtn = document.getElementById('theme-toggle');
    const sunIcon = document.getElementById('theme-icon-sun');
    const moonIcon = document.getElementById('theme-icon-moon');
    
    if (!toggleBtn || !sunIcon || !moonIcon) return;
    
    // LocalStorage dan themeni yuklash
    const currentTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', currentTheme);
    
    // Icon ko'rsatish
    if (currentTheme === 'light') {
        sunIcon.style.display = 'none';
        moonIcon.style.display = 'block';
    } else {
        sunIcon.style.display = 'block';
        moonIcon.style.display = 'none';
    }
    
    // Update scroll effect when theme changes
    function updateScrollStyles() {
        const mainNav = document.querySelector('.header-main-nav');
        if (!mainNav) return;
        
        const isScrolled = window.scrollY > 50;
        const theme = document.documentElement.getAttribute('data-theme');
        
        if (isScrolled) {
            if (theme === 'light') {
                mainNav.style.background = 'rgba(255, 255, 255, 0.98)';
                mainNav.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.15)';
            } else {
                mainNav.style.background = 'rgba(15, 23, 42, 0.95)';
                mainNav.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.3)';
            }
        } else {
            if (theme === 'light') {
                mainNav.style.background = 'rgba(255, 255, 255, 0.95)';
                mainNav.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.08)';
            } else {
                mainNav.style.background = 'rgb(30, 41, 59)';
                mainNav.style.boxShadow = 'none';
            }
        }
    }
    
    // Toggle button click
    toggleBtn.addEventListener('click', () => {
        const theme = document.documentElement.getAttribute('data-theme');
        const newTheme = theme === 'dark' ? 'light' : 'dark';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        
        // Icon almashtirish
        if (newTheme === 'light') {
            sunIcon.style.display = 'none';
            moonIcon.style.display = 'block';
        } else {
            sunIcon.style.display = 'block';
            moonIcon.style.display = 'none';
        }
        
        // Update scroll styles immediately
        updateScrollStyles();
    });
}

// User menu dropdown functionality
function initUserMenu() {
    const userMenuTrigger = document.getElementById('user-menu-trigger');
    const userDropdownMenu = document.getElementById('user-dropdown-menu');
    
    if (!userMenuTrigger || !userDropdownMenu) return;
    
    userMenuTrigger.addEventListener('click', (e) => {
        e.stopPropagation();
        userDropdownMenu.classList.toggle('active');
    });
    
    // Close when clicking outside
    document.addEventListener('click', (e) => {
        if (!userMenuTrigger.contains(e.target) && !userDropdownMenu.contains(e.target)) {
            userDropdownMenu.classList.remove('active');
        }
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initUserMenu();
});

