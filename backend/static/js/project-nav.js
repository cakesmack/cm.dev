/**
 * Project Detail Page Navigation - v2.0 Rebuilt
 * Handles sidebar active state and mobile collapsible navigation
 */

document.addEventListener('DOMContentLoaded', () => {
  const sidebarToggle = document.getElementById('sidebar-toggle');
  const sidebarMenu = document.getElementById('sidebar-menu');
  const sidebarIcon = document.getElementById('sidebar-icon');
  const navLinks = document.querySelectorAll('.project-nav-link');

  // Mobile sidebar toggle
  if (sidebarToggle) {
    sidebarToggle.addEventListener('click', () => {
      sidebarMenu.classList.toggle('collapsed');
      sidebarIcon.style.transform = sidebarMenu.classList.contains('collapsed')
        ? 'rotate(0deg)'
        : 'rotate(180deg)';
    });
  }

  // Highlight active section on scroll
  const sections = document.querySelectorAll('section[id]');

  function highlightActiveSection() {
    const scrollPos = window.scrollY + 200;

    sections.forEach(section => {
      const sectionTop = section.offsetTop;
      const sectionHeight = section.offsetHeight;
      const sectionId = section.getAttribute('id');

      if (scrollPos >= sectionTop && scrollPos < sectionTop + sectionHeight) {
        navLinks.forEach(link => {
          link.classList.remove('active');
          if (link.getAttribute('href') === `#${sectionId}`) {
            link.classList.add('active');
          }
        });
      }
    });
  }

  window.addEventListener('scroll', highlightActiveSection);
  highlightActiveSection(); // Run on page load

  // Smooth scroll to section on click
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

        // Close mobile menu after click
        if (window.innerWidth < 1024) {
          sidebarMenu.classList.add('collapsed');
          sidebarIcon.style.transform = 'rotate(0deg)';
        }
      }
    });
  });
});
