/**
 * Project Detail Page Navigation
 * Handles sidebar active state and mobile dropdown
 */

document.addEventListener('DOMContentLoaded', () => {
  const navLinks = document.querySelectorAll('.project-nav-link');
  const sections = document.querySelectorAll('.project-section');
  const mobileSelect = document.getElementById('project-mobile-nav-select');

  // Update active link on scroll
  function updateActiveLink() {
    let currentSection = '';

    sections.forEach(section => {
      const sectionTop = section.offsetTop;
      const sectionHeight = section.clientHeight;
      const scrollPosition = window.scrollY + 200; // Offset for header

      if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
        currentSection = section.getAttribute('id');
      }
    });

    navLinks.forEach(link => {
      link.classList.remove('active');
      if (link.getAttribute('href') === `#${currentSection}`) {
        link.classList.add('active');
      }
    });

    // Update mobile select
    if (mobileSelect && currentSection) {
      mobileSelect.value = currentSection;
    }
  }

  // Smooth scroll to section
  navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const targetId = link.getAttribute('href').substring(1);
      const targetSection = document.getElementById(targetId);

      if (targetSection) {
        const offsetTop = targetSection.offsetTop - 100;
        window.scrollTo({
          top: offsetTop,
          behavior: 'smooth'
        });
      }
    });
  });

  // Mobile dropdown navigation
  if (mobileSelect) {
    mobileSelect.addEventListener('change', (e) => {
      const targetId = e.target.value;
      const targetSection = document.getElementById(targetId);

      if (targetSection) {
        const offsetTop = targetSection.offsetTop - 100;
        window.scrollTo({
          top: offsetTop,
          behavior: 'smooth'
        });
      }
    });
  }

  // Listen to scroll events
  window.addEventListener('scroll', updateActiveLink);

  // Initial call
  updateActiveLink();
});
