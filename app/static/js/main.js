/**
 * Veltrix – main.js
 * Minimal, focused JavaScript for UI enhancements.
 * No frameworks required – vanilla JS only.
 */

/* ── Run after DOM is fully loaded ─────────────────────────────── */
document.addEventListener("DOMContentLoaded", () => {
  initNavbarScroll();
  initFlashAutoDismiss();
  initActiveNavLink();
  initFadeInCards();
  initPageLoadAnimations();
});


/* ================================================================
   1. Navbar – add "scrolled" class after user scrolls down
      (changes background opacity, adds shadow – see style.css)
   ================================================================ */
function initNavbarScroll() {
  const navbar = document.getElementById("mainNavbar");
  if (!navbar) return;

  const onScroll = () => {
    if (window.scrollY > 20) {
      navbar.classList.add("scrolled");
    } else {
      navbar.classList.remove("scrolled");
    }
  };

  // Set initial state and listen
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });
}


/* ================================================================
   2. Flash Messages – auto-dismiss after 5 seconds
   ================================================================ */
function initFlashAutoDismiss() {
  const alerts = document.querySelectorAll(".vx-alert");
  alerts.forEach((alert) => {
    setTimeout(() => {
      // Bootstrap's dismiss API with safe fallback
      if (typeof bootstrap !== "undefined") {
        const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
        bsAlert.close();
      } else {
        // Fallback: fade out and remove natively
        alert.style.transition = "opacity 0.5s ease";
        alert.style.opacity = "0";
        setTimeout(() => alert.remove(), 500);
      }
    }, 5000);
  });
}


/* ================================================================
   3. Active nav-link – highlight based on current URL path
      (Jinja already sets the "active" class server-side, but this
       acts as a client-side fallback / enhancement)
   ================================================================ */
function initActiveNavLink() {
  const currentPath = window.location.pathname;
  const navLinks    = document.querySelectorAll(".navbar-nav .nav-link");

  navLinks.forEach((link) => {
    // Exact match for home; prefix match for other pages
    const href = link.getAttribute("href");
    if (!href) return;
    if (href === currentPath || (href !== "/" && currentPath.startsWith(href))) {
      link.classList.add("active");
    }
  });
}


/* ================================================================
   4. Fade-in stagger for feature / stat cards
      Adds a tiny delay per card for a cascading entrance effect.
   ================================================================ */
function initFadeInCards() {
  const cards = document.querySelectorAll(
    ".vx-feature-card, .vx-stat-card, .vx-card"
  );

  if (!("IntersectionObserver" in window)) {
    // Fallback: make all cards visible immediately if IntersectionObserver is not supported
    cards.forEach((card) => card.classList.add("vx-visible"));
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      // Filter entries that are actually intersecting to stagger them properly
      const intersectingEntries = entries.filter(entry => entry.isIntersecting);
      intersectingEntries.forEach((entry, i) => {
        // Stagger each card by 80ms
        const delay = i * 80;
        entry.target.style.transitionDelay = `${delay}ms`;
        entry.target.classList.add("vx-visible");
        observer.unobserve(entry.target);

        // Remove the inline transition delay after the animation completes
        // so that hover styles react instantly without delay.
        setTimeout(() => {
          entry.target.style.transitionDelay = "";
        }, delay + 800);
      });
    },
    { threshold: 0.1 }
  );

  cards.forEach((card) => observer.observe(card));
}

/* ================================================================
   5. Page-load Animations
      Triggers page-load transition classes after DOM has loaded.
   ================================================================ */
function initPageLoadAnimations() {
  const loadElements = document.querySelectorAll(
    ".vx-animate-fade-in-up, .vx-animate-fade-in-down, .vx-animate-fade-in-left, .vx-animate-fade-in-right, .vx-animate-scale-in"
  );
  
  // Stagger or execute page-load animation classes
  setTimeout(() => {
    loadElements.forEach((el) => {
      el.classList.add("vx-visible");
    });
  }, 50);
}
