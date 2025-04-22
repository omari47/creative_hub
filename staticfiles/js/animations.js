document.addEventListener('DOMContentLoaded', function() {
  // Hero Section animations
  animateHeroSection();

  // Animate featured movie promo
  animateMoviePromo();

  // Animate counters/statistics on scroll
  initCounterAnimations();

  // Initialize custom hover effects
  initHoverEffects();

  // Initialize section animations
  initSectionAnimations();

  // Initialize smooth scrolling
  initSmoothScrolling();

  // Initialize morphing animations
  initMorphingAnimations();
});

// Hero Section Animation Sequence
function animateHeroSection() {
  const heroTitle = document.querySelector('.hero-title');
  const heroSubtitle = document.querySelector('.hero-subtitle');
  const heroButtons = document.querySelector('.hero-buttons');

  if (!heroTitle || !heroSubtitle || !heroButtons) return;

  // Reset any existing animations
  [heroTitle, heroSubtitle, heroButtons].forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
  });

  // Animation sequence
  setTimeout(() => {
    heroTitle.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
    heroTitle.style.opacity = '1';
    heroTitle.style.transform = 'translateY(0)';
  }, 300);

  setTimeout(() => {
    heroSubtitle.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
    heroSubtitle.style.opacity = '1';
    heroSubtitle.style.transform = 'translateY(0)';
  }, 500);

  setTimeout(() => {
    heroButtons.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
    heroButtons.style.opacity = '1';
    heroButtons.style.transform = 'translateY(0)';
  }, 700);
}

// Counter Animations with Intersection Observer
function initCounterAnimations() {
  const counters = document.querySelectorAll('.stat-number');

  if (counters.length === 0) return;

  const counterObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const counter = entry.target;
        const target = parseInt(counter.getAttribute('data-target'), 10);
        const duration = 2000; // milliseconds
        const interval = 50;
        const increment = target / (duration / interval);

        let current = 0;
        const counterTimer = setInterval(() => {
          current += increment;
          if (current >= target) {
            counter.textContent = target;
            clearInterval(counterTimer);
          } else {
            counter.textContent = Math.floor(current);
          }
        }, interval);

        observer.unobserve(counter);
      }
    });
  }, { threshold: 0.5 });

  counters.forEach(counter => {
    counterObserver.observe(counter);
  });
}

// Custom hover effects for various elements
function initHoverEffects() {
  // Image hover effects
  document.querySelectorAll('.hover-tilt').forEach(element => {
    element.addEventListener('mousemove', e => {
      const rect = element.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      const xPercent = x / rect.width;
      const yPercent = y / rect.height;

      const rotateX = (yPercent - 0.5) * -10;
      const rotateY = (xPercent - 0.5) * 10;

      element.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
    });

    element.addEventListener('mouseleave', () => {
      element.style.transform = 'perspective(1000px) rotateX(0) rotateY(0)';
    });
  });

  // Magnetic button effect
  document.querySelectorAll('.magnetic-btn').forEach(button => {
    button.addEventListener('mousemove', e => {
      const rect = button.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      const centerX = rect.width / 2;
      const centerY = rect.height / 2;

      const distanceX = (x - centerX) / centerX * 10;
      const distanceY = (y - centerY) / centerY * 10;

      button.style.transform = `translate(${distanceX}px, ${distanceY}px)`;
    });

    button.addEventListener('mouseleave', () => {
      button.style.transform = 'translate(0, 0)';
    });
  });
}

// Trailer video player functionality
function playTrailer(trailerUrl, previewContainer) {
  const container = document.querySelector(previewContainer);
  if (!container) return;

  // Create iframe for embedded video
  const videoIframe = document.createElement('iframe');
  videoIframe.src = trailerUrl;
  videoIframe.width = '100%';
  videoIframe.height = '100%';
  videoIframe.frameBorder = '0';
  videoIframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';
  videoIframe.allowFullscreen = true;

  // Replace container content with iframe
  container.innerHTML = '';
  container.appendChild(videoIframe);
}

// Parallax scrolling effect
function initParallaxEffect() {
  const parallaxElements = document.querySelectorAll('.parallax');

  window.addEventListener('scroll', () => {
    const scrollTop = window.pageYOffset;

    parallaxElements.forEach(element => {
      const speed = element.getAttribute('data-speed') || 0.5;
      element.style.transform = `translateY(${scrollTop * speed}px)`;
    });
  });
}

// Featured Movie Promo animations
function animateMoviePromo() {
  const promoSection = document.querySelector('.promo-section');
  if (!promoSection) return;

  const promoElements = {
    label: promoSection.querySelector('.promo-label'),
    title: promoSection.querySelector('.promo-title'),
    description: promoSection.querySelector('.promo-description'),
    meta: promoSection.querySelector('.promo-meta'),
    price: promoSection.querySelector('.promo-price'),
    actions: promoSection.querySelector('.promo-actions'),
    poster: promoSection.querySelector('.promo-poster')
  };

  // Use standard JavaScript for animations instead of GSAP
  // Get all promo elements to animate
  const elementsToAnimate = [
    promoElements.poster,
    promoElements.label,
    promoElements.title,
    promoElements.description,
    promoElements.meta,
    promoElements.price,
    promoElements.actions
  ].filter(el => el); // Filter out null elements

  // Apply initial styles
  elementsToAnimate.forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(30px)';
    el.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
  });

  // Animate each element with a delay
  elementsToAnimate.forEach((el, index) => {
    setTimeout(() => {
      el.style.opacity = '1';
      el.style.transform = 'translateY(0)';
    }, 300 + (index * 200));
  });

  // Animate play button pulse with CSS
  const playButton = promoSection.querySelector('.play-button');
  if (playButton) {
    playButton.classList.add('pulse-animation');
  }
}

// Section animations with Intersection Observer
function initSectionAnimations() {
  // Select all elements that should be animated on scroll
  const sections = document.querySelectorAll('.featured-section, .workshops-section, .movies-section, .cta-section');

  if (sections.length === 0) return;

  const sectionObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        // Add animation class when section becomes visible
        entry.target.classList.add('animate-section');

        // Animate child elements with staggered delay
        const childElements = entry.target.querySelectorAll('.section-title, .featured-card, .cta-title, .cta-text, .btn');
        childElements.forEach((el, index) => {
          setTimeout(() => {
            el.classList.add('animate-element');
          }, 100 * index);
        });

        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.2 });

  sections.forEach(section => {
    sectionObserver.observe(section);

    // Add animation classes for CSS transitions
    section.classList.add('section-animation');

    const childElements = section.querySelectorAll('.section-title, .featured-card, .cta-title, .cta-text, .btn');
    childElements.forEach(el => {
      el.classList.add('element-animation');
    });
  });
}

// Smooth scrolling for navigation links
function initSmoothScrolling() {
  // Get all navigation links that should trigger smooth scrolling
  const navLinks = document.querySelectorAll('.nav-link, .mobile-nav-link');

  navLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      // Only apply smooth scrolling to links pointing to the same page with hash
      const href = this.getAttribute('href');

      // If it's a same-page link with a hash (like #section-id)
      if (href.startsWith('#') || (href.includes('#') && window.location.pathname === href.split('#')[0])) {
        e.preventDefault();

        const targetId = href.includes('#') ? href.split('#')[1] : href.substring(1);
        const targetElement = document.getElementById(targetId);

        if (targetElement) {
          // Close mobile menu if it's open
          const mobileNavContainer = document.getElementById('mobileNavContainer');
          if (mobileNavContainer && mobileNavContainer.classList.contains('active')) {
            mobileNavContainer.classList.remove('active');
            const menuIcon = document.querySelector('.icon-menu');
            const closeIcon = document.querySelector('.icon-close');
            if (menuIcon) menuIcon.classList.remove('d-none');
            if (closeIcon) closeIcon.classList.add('d-none');
            document.body.style.overflow = '';
          }

          // Calculate navbar height for offset
          const navbar = document.querySelector('.navbar');
          const navbarHeight = navbar ? navbar.offsetHeight : 0;

          // Calculate target position with offset
          const targetPosition = targetElement.getBoundingClientRect().top + window.pageYOffset - navbarHeight;

          // Smooth scroll to target
          window.scrollTo({
            top: targetPosition,
            behavior: 'smooth'
          });
        }
      }
    });
  });

  // Handle scroll to top for logo click
  const logoLink = document.querySelector('.navbar-brand');
  if (logoLink && window.location.pathname === '/') {
    logoLink.addEventListener('click', function(e) {
      e.preventDefault();
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
    });
  }
}

// Enhanced morphing animations for buttons and UI elements
function initMorphingAnimations() {
  // Apply morphing effect to navigation links
  const navMorphElements = document.querySelectorAll('.nav-morph');

  // Add subtle hover animations to buttons
  const morphingButtons = document.querySelectorAll('.btn-signup, .auth-submit, .watch-btn');
  morphingButtons.forEach(btn => {
    btn.classList.add('morphing-btn');
  });

  // Add special effect to the brand/logo
  const brandLogo = document.querySelector('.navbar-brand');
  if (brandLogo) {
    brandLogo.addEventListener('mouseenter', () => {
      brandLogo.style.transition = 'all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1)';
      brandLogo.style.textShadow = '0 0 10px rgba(255, 255, 255, 0.5)';
      brandLogo.style.letterSpacing = '0.5px';
    });

    brandLogo.addEventListener('mouseleave', () => {
      brandLogo.style.textShadow = 'none';
      brandLogo.style.letterSpacing = 'normal';
    });
  }

  // Add gradient hover effect to hero buttons
  const heroButtons = document.querySelectorAll('.hero-button');
  heroButtons.forEach(btn => {
    btn.addEventListener('mouseenter', () => {
      btn.style.backgroundSize = '200% 200%';
      btn.style.backgroundPosition = 'right center';
    });

    btn.addEventListener('mouseleave', () => {
      btn.style.backgroundSize = '100% 100%';
      btn.style.backgroundPosition = 'left center';
    });
  });
}