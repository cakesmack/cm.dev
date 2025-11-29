// Portfolio Accordion Functionality
document.addEventListener('DOMContentLoaded', () => {
    const portfolioList = document.getElementById('portfolio-list');

    if (portfolioList) {
        const projectItems = portfolioList.querySelectorAll('.project-item');

        projectItems.forEach(item => {
            const header = item.querySelector('.project-header');
            const detail = item.querySelector('.project-detail');
            const icon = item.querySelector('.project-icon');
            const dot = item.querySelector('.project-header > div:first-child');

            header.addEventListener('click', () => {
                const isOpen = detail.style.maxHeight && detail.style.maxHeight !== '0px';

                // Close all other items
                projectItems.forEach(otherItem => {
                    if (otherItem !== item) {
                        const otherDetail = otherItem.querySelector('.project-detail');
                        const otherIcon = otherItem.querySelector('.project-icon');
                        const otherDot = otherItem.querySelector('.project-header > div:first-child');

                        otherDetail.style.maxHeight = '0';
                        otherIcon.style.transform = 'rotate(0deg)';
                        otherItem.classList.remove('expanded');

                        if (otherDot) {
                            otherDot.classList.remove('scale-150', 'bg-perplexity-accent');
                            otherDot.classList.add('bg-perplexity-accent');
                        }
                    }
                });

                // Toggle current item
                if (isOpen) {
                    detail.style.maxHeight = '0';
                    icon.style.transform = 'rotate(0deg)';
                    item.classList.remove('expanded');
                    if (dot) {
                        dot.classList.remove('scale-150');
                    }
                } else {
                    detail.style.maxHeight = detail.scrollHeight + 'px';
                    icon.style.transform = 'rotate(180deg)';
                    item.classList.add('expanded');
                    if (dot) {
                        dot.classList.add('scale-150');
                    }

                    // Re-initialize Lucide icons in the newly opened detail section
                    lucide.createIcons();
                }
            });
        });
    }
});
