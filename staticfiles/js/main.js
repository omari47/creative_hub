// Global variables for mobile navigation
let globalMobileMenuToggle;
let globalMobileNavContainer;
let globalMenuIcon;
let globalCloseIcon;

// Global function for toggling mobile menu (can be called directly from HTML)
function toggleMobileMenu() {
  if (!globalMobileMenuToggle) {
    globalMobileMenuToggle = document.getElementById('mobileMenuToggle');
  }
  if (!globalMobileNavContainer) {
    globalMobileNavContainer = document.getElementById('mobileNavContainer');
  }
  if (!globalMenuIcon) {
    globalMenuIcon = document.querySelector('.icon-menu');
  }
  if (!globalCloseIcon) {
    globalCloseIcon = document.querySelector('.icon-close');
  }

  if (!globalMobileNavContainer) return;

  const isActive = globalMobileNavContainer.classList.contains('active');

  if (!isActive) {
    // Open menu
    globalMobileNavContainer.classList.add('active');
    document.body.style.overflow = 'hidden'; // Prevent scrolling

    // Switch icons
    if (globalMenuIcon && globalCloseIcon) {
      globalMenuIcon.classList.add('d-none');
      globalCloseIcon.classList.remove('d-none');
    }

    // Force all mobile nav items to be visible
    document.querySelectorAll('.mobile-nav-item').forEach(item => {
      item.style.display = 'block';
      item.style.opacity = '1';
      item.style.visibility = 'visible';
    });

    document.querySelectorAll('.mobile-nav-link').forEach(link => {
      link.style.display = 'block';
      link.style.opacity = '1';
      link.style.visibility = 'visible';
    });
  } else {
    // Close menu
    globalMobileNavContainer.classList.remove('active');
    document.body.style.overflow = ''; // Restore scrolling

    // Switch icons
    if (globalMenuIcon && globalCloseIcon) {
      globalMenuIcon.classList.remove('d-none');
      globalCloseIcon.classList.add('d-none');
    }
  }
}

document.addEventListener('DOMContentLoaded', function() {
  // Removed navbar scroll effect as it affects other pages

  // Initialize Mobile Navigation Toggle
  initMobileNavigation();

  // Initialize Auth Modals
  initAuthModals();

  // Initialize Reveal on Scroll
  initRevealOnScroll();

  // Initialize Portfolio Filtering
  initPortfolioFilter();

  // Initialize Trailer Slider Navigation
  initTrailerSlider();

  // Initialize M-Pesa Payment Modal
  initPaymentModal();
});

// Mobile Navigation Toggle
function initMobileNavigation() {
  const mobileMenuToggle = document.getElementById('mobileMenuToggle');
  const mobileNavContainer = document.getElementById('mobileNavContainer');
  const mobileNavLinks = document.querySelectorAll('.mobile-nav-link');
  const menuIcon = document.querySelector('.icon-menu');
  const closeIcon = document.querySelector('.icon-close');

  if (!mobileMenuToggle || !mobileNavContainer) return;

  // Function to toggle menu state
  function toggleMobileMenu(show) {
    if (show) {
      mobileNavContainer.classList.add('active');
      document.body.style.overflow = 'hidden'; // Prevent scrolling when menu is open

      // Switch icons
      if (menuIcon && closeIcon) {
        menuIcon.classList.add('d-none');
        closeIcon.classList.remove('d-none');
      }

      // Make sure all items are visible
      mobileNavLinks.forEach((link, index) => {
        // Clear any previous inline styles
        link.style = '';
        link.style.opacity = '1';
      });
    } else {
      mobileNavContainer.classList.remove('active');
      document.body.style.overflow = ''; // Restore scrolling

      // Switch icons
      if (menuIcon && closeIcon) {
        menuIcon.classList.remove('d-none');
        closeIcon.classList.add('d-none');
      }
    }
  }

  // Set initial state for menu items but keep them visible by default
  mobileNavLinks.forEach(link => {
    link.style.opacity = '1'; // Changed to 1 to make items visible by default
    link.style.transform = 'translateY(0)'; // Reset transform
    link.style.transition = 'all 0.3s ease, opacity 0.3s ease, transform 0.3s ease';
  });

  // Toggle mobile menu on button click
  mobileMenuToggle.addEventListener('click', function(e) {
    e.stopPropagation(); // Prevent triggering document click
    const isActive = mobileNavContainer.classList.contains('active');
    toggleMobileMenu(!isActive);
  });

  // Close mobile menu when a link is clicked
  mobileNavLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      // If it's a button (login/signup), don't navigate away
      if (this.tagName.toLowerCase() !== 'button') {
        e.stopPropagation(); // Prevent triggering document click
      }
      toggleMobileMenu(false);
    });
  });

  // Close mobile menu when clicking outside
  document.addEventListener('click', function(event) {
    const isClickInside = mobileNavContainer.contains(event.target) || mobileMenuToggle.contains(event.target);

    if (!isClickInside && mobileNavContainer.classList.contains('active')) {
      toggleMobileMenu(false);
    }
  });

  // Close menu on escape key
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && mobileNavContainer.classList.contains('active')) {
      toggleMobileMenu(false);
    }
  });
}

// Reveal on Scroll using Intersection Observer
function initRevealOnScroll() {
  const revealElements = document.querySelectorAll('.reveal, .reveal-left, .reveal-right, .reveal-scale');

  if (revealElements.length === 0) return;

  const revealOptions = {
    threshold: 0.15,
    rootMargin: '0px 0px -50px 0px'
  };

  const revealObserver = new IntersectionObserver(function(entries, observer) {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('active');
        observer.unobserve(entry.target);
      }
    });
  }, revealOptions);

  revealElements.forEach(el => {
    revealObserver.observe(el);
  });
}

// Portfolio Filter Functionality
function initPortfolioFilter() {
  const portfolioCategories = document.querySelectorAll('.portfolio-category');
  const portfolioItems = document.querySelectorAll('.portfolio-item');

  if (portfolioCategories.length === 0 || portfolioItems.length === 0) return;

  portfolioCategories.forEach(category => {
    category.addEventListener('click', function() {
      // Remove active class from all categories
      portfolioCategories.forEach(cat => cat.classList.remove('active'));

      // Add active class to clicked category
      this.classList.add('active');

      const filterValue = this.getAttribute('data-filter');

      // Filter portfolio items
      portfolioItems.forEach(item => {
        if (filterValue === 'all') {
          item.style.display = 'block';
        } else if (item.getAttribute('data-category') === filterValue) {
          item.style.display = 'block';
        } else {
          item.style.display = 'none';
        }
      });
    });
  });
}

// Trailer Slider Navigation
function initTrailerSlider() {
  const trailerContainer = document.querySelector('.trailer-scrolling');
  const prevBtn = document.querySelector('.trailer-prev');
  const nextBtn = document.querySelector('.trailer-next');

  if (!trailerContainer || !prevBtn || !nextBtn) return;

  // Calculate scroll amount based on first card width + margin
  let scrollAmount;

  // Initialize scroll amount
  function updateScrollAmount() {
    if (trailerContainer.children.length > 0) {
      const firstCard = trailerContainer.children[0];
      const cardWidth = firstCard.offsetWidth;
      const cardStyle = window.getComputedStyle(firstCard);
      const cardMargin = parseInt(cardStyle.marginRight, 10);
      scrollAmount = cardWidth + cardMargin;
    }
  }

  updateScrollAmount();
  window.addEventListener('resize', updateScrollAmount);

  // Scroll left button
  prevBtn.addEventListener('click', function() {
    trailerContainer.scrollBy({
      left: -scrollAmount,
      behavior: 'smooth'
    });
  });

  // Scroll right button
  nextBtn.addEventListener('click', function() {
    trailerContainer.scrollBy({
      left: scrollAmount,
      behavior: 'smooth'
    });
  });
}

// Auth Modals Functionality
function initAuthModals() {
  // Get modal elements
  const loginModal = document.getElementById('loginModal');
  const signupModal = document.getElementById('signupModal');

  // Get trigger buttons
  const loginBtn = document.getElementById('loginModalBtn');
  const signupBtn = document.getElementById('signupModalBtn');
  const mobileLoginBtn = document.getElementById('mobileLoginBtn');
  const mobileSignupBtn = document.getElementById('mobileSignupBtn');

  // Get close buttons
  const closeLoginBtn = document.getElementById('closeLoginModal');
  const closeSignupBtn = document.getElementById('closeSignupModal');

  // Get switch buttons
  const switchToSignup = document.getElementById('switchToSignup');
  const switchToLogin = document.getElementById('switchToLogin');

  // Mobile menu elements
  const mobileNavContainer = document.getElementById('mobileNavContainer');
  const menuIcon = document.querySelector('.icon-menu');
  const closeIcon = document.querySelector('.icon-close');

  // Helper function to close mobile menu
  function closeMobileMenu() {
    if (mobileNavContainer && mobileNavContainer.classList.contains('active')) {
      mobileNavContainer.classList.remove('active');
      if (menuIcon) menuIcon.classList.remove('d-none');
      if (closeIcon) closeIcon.classList.add('d-none');
    }
  }

  // Open login modal
  if (loginBtn) {
    loginBtn.addEventListener('click', function() {
      loginModal.classList.add('active');
      document.body.style.overflow = 'hidden'; // Prevent scrolling
    });
  }

  if (mobileLoginBtn) {
    mobileLoginBtn.addEventListener('click', function() {
      loginModal.classList.add('active');
      document.body.style.overflow = 'hidden';
      closeMobileMenu();
    });
  }

  // Close login modal
  if (closeLoginBtn) {
    closeLoginBtn.addEventListener('click', function() {
      loginModal.classList.remove('active');
      document.body.style.overflow = '';
    });
  }

  // Open signup modal
  if (signupBtn) {
    signupBtn.addEventListener('click', function() {
      signupModal.classList.add('active');
      document.body.style.overflow = 'hidden';
    });
  }

  if (mobileSignupBtn) {
    mobileSignupBtn.addEventListener('click', function() {
      signupModal.classList.add('active');
      document.body.style.overflow = 'hidden';
      closeMobileMenu();
    });
  }

  // Close signup modal
  if (closeSignupBtn) {
    closeSignupBtn.addEventListener('click', function() {
      signupModal.classList.remove('active');
      document.body.style.overflow = '';
    });
  }

  // Switch between modals
  if (switchToSignup) {
    switchToSignup.addEventListener('click', function() {
      loginModal.classList.remove('active');
      signupModal.classList.add('active');
    });
  }

  if (switchToLogin) {
    switchToLogin.addEventListener('click', function() {
      signupModal.classList.remove('active');
      loginModal.classList.add('active');
    });
  }

  // Close modals when clicking outside
  if (loginModal) {
    loginModal.addEventListener('click', function(event) {
      if (event.target === this) {
        this.classList.remove('active');
        document.body.style.overflow = '';
      }
    });
  }

  if (signupModal) {
    signupModal.addEventListener('click', function(event) {
      if (event.target === this) {
        this.classList.remove('active');
        document.body.style.overflow = '';
      }
    });
  }

  // Close modals with Escape key
  document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
      if (loginModal) loginModal.classList.remove('active');
      if (signupModal) signupModal.classList.remove('active');
      document.body.style.overflow = '';
    }
  });
}

// M-Pesa Payment Modal
function initPaymentModal() {
  const watchButtons = document.querySelectorAll('.watch-btn');
  const mpesaModal = document.querySelector('.mpesa-payment-modal');
  const mpesaCloseBtn = document.querySelector('.mpesa-close-btn');
  const mpesaForm = document.querySelector('.mpesa-payment-form');
  const mpesaLoading = document.querySelector('.mpesa-loading');

  if (!watchButtons.length || !mpesaModal) return;

  // Open modal when watch button is clicked
  watchButtons.forEach(btn => {
    btn.addEventListener('click', function(e) {
      e.preventDefault();

      // Update modal with movie details if data attributes are available
      const movieTitle = this.getAttribute('data-title');
      const moviePrice = this.getAttribute('data-price');
      const movieImage = this.getAttribute('data-image');

      const modalTitle = mpesaModal.querySelector('.mpesa-movie-title');
      const modalPrice = mpesaModal.querySelector('.mpesa-movie-price');
      const modalImage = mpesaModal.querySelector('.mpesa-movie-thumb');

      if (modalTitle && movieTitle) modalTitle.textContent = movieTitle;
      if (modalPrice && moviePrice) modalPrice.textContent = 'KES ' + moviePrice;
      if (modalImage && movieImage) modalImage.src = movieImage;

      // Show modal
      mpesaModal.classList.add('active');
      document.body.style.overflow = 'hidden'; // Prevent background scrolling
    });
  });

  // Close modal
  if (mpesaCloseBtn) {
    mpesaCloseBtn.addEventListener('click', function() {
      mpesaModal.classList.remove('active');
      document.body.style.overflow = '';
    });
  }

  // Close modal when clicking outside
  mpesaModal.addEventListener('click', function(e) {
    if (e.target === mpesaModal) {
      mpesaModal.classList.remove('active');
      document.body.style.overflow = '';
    }
  });

  // Handle payment form submission
  if (mpesaForm) {
    mpesaForm.addEventListener('submit', function(e) {
      e.preventDefault();

      const phoneInput = this.querySelector('input[name="phone_number"]');
      if (!phoneInput || !phoneInput.value) {
        alert('Please enter a valid phone number');
        return;
      }

      // Show loading state
      if (mpesaLoading) {
        mpesaForm.style.display = 'none';
        mpesaLoading.classList.add('active');
      }

      // Simulate a payment request (replace with actual implementation)
      setTimeout(function() {
        // In a real implementation, you would send an AJAX request to your backend
        // and handle the M-Pesa integration there.

        // For demo purposes, just show success and close modal
        alert('Payment request sent! Check your phone for the M-Pesa prompt.');

        if (mpesaLoading) mpesaLoading.classList.remove('active');
        if (mpesaForm) mpesaForm.style.display = '';

        mpesaModal.classList.remove('active');
        document.body.style.overflow = '';
      }, 2000);
    });
  }
}