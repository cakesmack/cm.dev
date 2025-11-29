# Implementation Plan: Expanding Flow List Portfolio Section

## Overview
Replace the existing card-based portfolio section with an interactive "Expanding Flow List" design featuring 3 static projects. The design will feature a vertical flow line on the left, clickable project headers, and expandable details with smooth accordion behavior.

## Current Architecture

### File Structure
```
backend/
├── app/
│   └── templates/
│       ├── base.html                    # Base template with Tailwind config
│       ├── public/
│       │   └── home.html                # Main homepage (MODIFY THIS)
│       └── components/
│           └── navbar.html
└── static/
    ├── js/
    │   └── main.js                       # Main JS file (ADD PORTFOLIO JS HERE)
    └── css/
        └── main.css
```

### Current Portfolio Section
- **Location**: `backend/app/templates/public/home.html` lines 450-509
- **Current Implementation**: Grid of project cards (`md:grid-cols-2 lg:grid-cols-3`)
- **Data Source**: Dynamic (fetches from `projects` variable passed from Flask backend)
- **Styling**: Dark mode enabled, using Tailwind utility classes
- **Key Classes**: `project-card`, `fade-in`, `bg-perplexity-light`, `text-perplexity-accent`

## Implementation Tasks

### Task 1: Create Portfolio Section HTML Structure
**File**: `backend/app/templates/public/home.html`
**Action**: Replace lines 450-509 (entire Projects Section)

**Implementation Details**:

1. **Section Container** (lines 450-453):
   - Keep the existing `<section id="projects">` wrapper
   - Maintain existing classes: `py-24 bg-gradient-to-b from-light-grey to-warm-grey dark:from-perplexity-light dark:to-perplexity-dark relative`
   - Keep the max-width container: `max-w-6xl mx-auto px-6`

2. **Section Header** (lines 458-460):
   - Keep existing header structure
   - Update title to "Project Portfolio" (already correct)

3. **Create Flow List Container**:
   ```html
   <div class="relative">
     <!-- Vertical Flow Line -->
     <div class="absolute left-0 top-0 bottom-0 w-0.5 bg-gradient-to-b from-perplexity-accent/30 via-perplexity-accent/60 to-perplexity-accent/30"></div>

     <!-- Projects List -->
     <div class="space-y-0" id="portfolio-list">
       <!-- Individual project items go here -->
     </div>
   </div>
   ```

4. **Project Item Structure** (Create 3 instances with placeholder data):
   ```html
   <!-- Project 1: P-001 -->
   <div class="project-item relative" data-project="p-001">
     <!-- Project Header (Clickable) -->
     <div class="project-header cursor-pointer relative pl-12 pr-6 py-6 transition-all duration-300 hover:bg-gray-800">
       <!-- Flow Line Dot -->
       <div class="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-1/2 w-4 h-4 rounded-full bg-perplexity-accent border-4 border-perplexity-dark transition-all duration-300"></div>

       <!-- Header Content -->
       <div class="flex items-center justify-between gap-4">
         <div class="flex-1">
           <div class="flex items-center gap-4 mb-2">
             <span class="font-mono text-sm text-perplexity-accent">P-001</span>
             <h3 class="text-2xl font-display font-semibold text-gray-100">Internal Platform</h3>
           </div>
           <div class="font-mono text-xs text-gray-400">Python / FastAPI / SQL</div>
         </div>

         <!-- Expand/Collapse Icon -->
         <div class="project-icon transition-transform duration-300 text-perplexity-accent">
           <i data-lucide="chevron-down" class="w-6 h-6"></i>
         </div>
       </div>
     </div>

     <!-- Project Detail (Initially Hidden) -->
     <div class="project-detail overflow-hidden transition-all duration-500" style="max-height: 0;">
       <div class="pl-12 pr-6 py-8 border-l-2 border-perplexity-accent/20">
         <!-- Summary -->
         <p class="text-gray-300 leading-relaxed mb-6">
           Automated sales orders, stock tracking, and reporting for a sales administration platform, reducing manual processing by 60%.
         </p>

         <!-- Dashboard Image Placeholder -->
         <div class="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl mb-6 overflow-hidden border border-gray-700">
           <div class="aspect-video flex items-center justify-center">
             <div class="text-center">
               <i data-lucide="layout-dashboard" class="w-16 h-16 text-perplexity-accent/30 mx-auto mb-2"></i>
               <p class="text-gray-500 text-sm">Dashboard Preview</p>
             </div>
           </div>
         </div>

         <!-- CTA Button -->
         <button class="cta-button bg-perplexity-accent text-white px-6 py-3 rounded-xl font-semibold inline-flex items-center gap-2 hover:bg-perplexity-accent/90 transition-all">
           View Full Case Study
           <i data-lucide="arrow-right" class="w-4 h-4"></i>
         </button>
       </div>
     </div>
   </div>
   ```

5. **Repeat for P-002 and P-003**:
   - P-002: Title: "Data Migration Tool", Tech: `Python / Pandas / Flask`, Summary: "Designed and built a utility to clean, validate, and migrate complex legacy data between disparate SQL databases with 99.9% accuracy."
   - P-003: Title: "Logistics Tracker", Tech: `JS / HTML / CSS`, Summary: "A simple, custom front-end tool for tracking and reporting on logistics movements, giving operations teams real-time status updates."

**Complete HTML Code**:
```html
<!-- Projects Section -->
<section id="projects"
    class="py-24 bg-gradient-to-b from-light-grey to-warm-grey dark:from-perplexity-light dark:to-perplexity-dark relative">
    <div class="max-w-6xl mx-auto px-6">
        <div class="fade-in mb-12 text-center">
            <h2 class="text-3xl font-display font-semibold text-charcoal dark:text-white mb-12">Project Portfolio</h2>
        </div>

        <!-- Flow List Container -->
        <div class="relative max-w-4xl mx-auto">
            <!-- Vertical Flow Line -->
            <div class="absolute left-0 top-0 bottom-0 w-0.5 bg-gradient-to-b from-perplexity-accent/30 via-perplexity-accent/60 to-perplexity-accent/30 hidden md:block"></div>

            <!-- Projects List -->
            <div class="space-y-0" id="portfolio-list">

                <!-- Project 1: P-001 Internal Platform -->
                <div class="project-item relative" data-project="p-001">
                    <!-- Project Header -->
                    <div class="project-header cursor-pointer relative md:pl-12 pl-0 pr-6 py-6 transition-all duration-300 hover:bg-gray-800 rounded-lg">
                        <!-- Flow Line Dot -->
                        <div class="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-1/2 w-4 h-4 rounded-full bg-perplexity-accent border-4 border-perplexity-dark transition-all duration-300 hidden md:block"></div>

                        <!-- Header Content -->
                        <div class="flex items-center justify-between gap-4">
                            <div class="flex-1">
                                <div class="flex flex-col md:flex-row md:items-center gap-2 md:gap-4 mb-2">
                                    <span class="font-mono text-sm text-perplexity-accent">P-001</span>
                                    <h3 class="text-2xl font-display font-semibold text-gray-100">Internal Platform</h3>
                                </div>
                                <div class="font-mono text-xs text-gray-400">Python / FastAPI / SQL</div>
                            </div>

                            <!-- Expand Icon -->
                            <div class="project-icon transition-transform duration-300 text-perplexity-accent">
                                <i data-lucide="chevron-down" class="w-6 h-6"></i>
                            </div>
                        </div>
                    </div>

                    <!-- Project Detail -->
                    <div class="project-detail overflow-hidden transition-all duration-500" style="max-height: 0;">
                        <div class="md:pl-12 pl-0 pr-6 py-8 md:border-l-2 border-perplexity-accent/20">
                            <p class="text-gray-300 leading-relaxed mb-6">
                                Automated sales orders, stock tracking, and reporting for a sales administration platform, reducing manual processing by 60%.
                            </p>

                            <!-- Dashboard Placeholder -->
                            <div class="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl mb-6 overflow-hidden border border-gray-700">
                                <div class="aspect-video flex items-center justify-center">
                                    <div class="text-center">
                                        <i data-lucide="layout-dashboard" class="w-16 h-16 text-perplexity-accent/30 mx-auto mb-2"></i>
                                        <p class="text-gray-500 text-sm">Dashboard Preview</p>
                                    </div>
                                </div>
                            </div>

                            <button class="cta-button bg-perplexity-accent text-white px-6 py-3 rounded-xl font-semibold inline-flex items-center gap-2 hover:bg-perplexity-accent/90 transition-all">
                                View Full Case Study
                                <i data-lucide="arrow-right" class="w-4 h-4"></i>
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Project 2: P-002 Data Migration Tool -->
                <div class="project-item relative" data-project="p-002">
                    <div class="project-header cursor-pointer relative md:pl-12 pl-0 pr-6 py-6 transition-all duration-300 hover:bg-gray-800 rounded-lg">
                        <div class="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-1/2 w-4 h-4 rounded-full bg-perplexity-accent border-4 border-perplexity-dark transition-all duration-300 hidden md:block"></div>

                        <div class="flex items-center justify-between gap-4">
                            <div class="flex-1">
                                <div class="flex flex-col md:flex-row md:items-center gap-2 md:gap-4 mb-2">
                                    <span class="font-mono text-sm text-perplexity-accent">P-002</span>
                                    <h3 class="text-2xl font-display font-semibold text-gray-100">Data Migration Tool</h3>
                                </div>
                                <div class="font-mono text-xs text-gray-400">Python / Pandas / Flask</div>
                            </div>

                            <div class="project-icon transition-transform duration-300 text-perplexity-accent">
                                <i data-lucide="chevron-down" class="w-6 h-6"></i>
                            </div>
                        </div>
                    </div>

                    <div class="project-detail overflow-hidden transition-all duration-500" style="max-height: 0;">
                        <div class="md:pl-12 pl-0 pr-6 py-8 md:border-l-2 border-perplexity-accent/20">
                            <p class="text-gray-300 leading-relaxed mb-6">
                                Designed and built a utility to clean, validate, and migrate complex legacy data between disparate SQL databases with 99.9% accuracy.
                            </p>

                            <div class="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl mb-6 overflow-hidden border border-gray-700">
                                <div class="aspect-video flex items-center justify-center">
                                    <div class="text-center">
                                        <i data-lucide="database" class="w-16 h-16 text-perplexity-accent/30 mx-auto mb-2"></i>
                                        <p class="text-gray-500 text-sm">Dashboard Preview</p>
                                    </div>
                                </div>
                            </div>

                            <button class="cta-button bg-perplexity-accent text-white px-6 py-3 rounded-xl font-semibold inline-flex items-center gap-2 hover:bg-perplexity-accent/90 transition-all">
                                View Full Case Study
                                <i data-lucide="arrow-right" class="w-4 h-4"></i>
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Project 3: P-003 Logistics Tracker -->
                <div class="project-item relative" data-project="p-003">
                    <div class="project-header cursor-pointer relative md:pl-12 pl-0 pr-6 py-6 transition-all duration-300 hover:bg-gray-800 rounded-lg">
                        <div class="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-1/2 w-4 h-4 rounded-full bg-perplexity-accent border-4 border-perplexity-dark transition-all duration-300 hidden md:block"></div>

                        <div class="flex items-center justify-between gap-4">
                            <div class="flex-1">
                                <div class="flex flex-col md:flex-row md:items-center gap-2 md:gap-4 mb-2">
                                    <span class="font-mono text-sm text-perplexity-accent">P-003</span>
                                    <h3 class="text-2xl font-display font-semibold text-gray-100">Logistics Tracker</h3>
                                </div>
                                <div class="font-mono text-xs text-gray-400">JS / HTML / CSS</div>
                            </div>

                            <div class="project-icon transition-transform duration-300 text-perplexity-accent">
                                <i data-lucide="chevron-down" class="w-6 h-6"></i>
                            </div>
                        </div>
                    </div>

                    <div class="project-detail overflow-hidden transition-all duration-500" style="max-height: 0;">
                        <div class="md:pl-12 pl-0 pr-6 py-8 md:border-l-2 border-perplexity-accent/20">
                            <p class="text-gray-300 leading-relaxed mb-6">
                                A simple, custom front-end tool for tracking and reporting on logistics movements, giving operations teams real-time status updates.
                            </p>

                            <div class="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl mb-6 overflow-hidden border border-gray-700">
                                <div class="aspect-video flex items-center justify-center">
                                    <div class="text-center">
                                        <i data-lucide="truck" class="w-16 h-16 text-perplexity-accent/30 mx-auto mb-2"></i>
                                        <p class="text-gray-500 text-sm">Dashboard Preview</p>
                                    </div>
                                </div>
                            </div>

                            <button class="cta-button bg-perplexity-accent text-white px-6 py-3 rounded-xl font-semibold inline-flex items-center gap-2 hover:bg-perplexity-accent/90 transition-all">
                                View Full Case Study
                                <i data-lucide="arrow-right" class="w-4 h-4"></i>
                            </button>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    </div>
</section>
```

---

### Task 2: Create Accordion JavaScript Functionality
**File**: `backend/static/js/main.js`
**Action**: Add after line 26 (after existing intersection observer code)

**Implementation Details**:

1. **Accordion Logic**:
   - Single active item at a time
   - Click header to expand/collapse
   - Smooth height transition using max-height
   - Icon rotation animation

2. **JavaScript Code**:
```javascript
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
                    if (dot) {
                        dot.classList.remove('scale-150');
                    }
                } else {
                    detail.style.maxHeight = detail.scrollHeight + 'px';
                    icon.style.transform = 'rotate(180deg)';
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
```

**Code Explanation**:
- **Lines 1-4**: Wait for DOM to load, select portfolio container
- **Lines 6-9**: Get all project items and their child elements (header, detail, icon, dot)
- **Lines 11-13**: Add click listener to each header, check if currently open
- **Lines 15-27**: Close all other items when one is clicked (accordion behavior)
- **Lines 30-44**: Toggle current item - if open, close it; if closed, open it and rotate icon
- **Line 43**: Re-initialize Lucide icons for newly visible SVG elements

---

### Task 3: Add Custom CSS Transitions (Optional Enhancement)
**File**: `backend/app/templates/base.html`
**Action**: Add to `<style>` block after line 344 (after section scroll-margin-top)

**Implementation Details**:

```css
/* Portfolio Flow List Styling */
.project-item .project-header {
    transition: background-color 0.3s ease, transform 0.2s ease;
}

.project-item .project-header:hover {
    transform: translateX(4px);
}

.project-detail {
    transition: max-height 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.project-icon {
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Flow line dot animation */
.project-header > div:first-child {
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1),
                background-color 0.3s ease;
}

/* Active state glow */
.project-item.active .project-header > div:first-child {
    box-shadow: 0 0 20px rgba(34, 179, 193, 0.5);
}
```

---

## File Changes Summary

### Modified Files

1. **`backend/app/templates/public/home.html`**
   - **Lines to replace**: 450-509 (entire Projects Section)
   - **New content**: Expanding Flow List HTML (see Task 1)
   - **Breaking changes**: None (section ID remains `#projects`)

2. **`backend/static/js/main.js`**
   - **Add after line**: 26
   - **New content**: Accordion JavaScript (see Task 2)
   - **Dependencies**: Requires Lucide icons (already loaded in base.html)

3. **`backend/app/templates/base.html`** (Optional)
   - **Add after line**: 344
   - **New content**: Custom CSS transitions (see Task 3)
   - **Purpose**: Enhanced animations

---

## Design Specifications

### Color Palette (Dark Mode)
- **Background**: `bg-gray-900` (#191A1A - perplexity-dark)
- **Card Background**: `bg-gray-800` (#202222 - perplexity-light)
- **Text Primary**: `text-gray-100` (#E2E8F0)
- **Text Secondary**: `text-gray-300`, `text-gray-400`
- **Accent Color**: `text-perplexity-accent` (#22B3C1)
- **Flow Line**: `bg-perplexity-accent` with opacity variations
- **Border**: `border-gray-700`, `border-perplexity-accent/20`

### Typography
- **Project ID**: `font-mono text-sm` (monospace, small)
- **Project Title**: `text-2xl font-display font-semibold` (Plus Jakarta Sans)
- **Tech Tags**: `font-mono text-xs` (monospace, extra small)
- **Summary**: `text-gray-300 leading-relaxed` (DM Sans)

### Spacing & Layout
- **Section Padding**: `py-24` (6rem top/bottom)
- **Container Max Width**: `max-w-4xl` (56rem)
- **Project Item Spacing**: `space-y-0` (no gap, continuous flow)
- **Header Padding**: `py-6` (1.5rem)
- **Detail Padding**: `py-8` (2rem)
- **Left Offset**: `pl-12` (3rem) on desktop, `pl-0` on mobile

### Responsive Behavior
- **Desktop** (`md:` breakpoint and above):
  - Flow line visible on left
  - Flow dots visible
  - Header padding left: 3rem
  - Title and ID on same row

- **Mobile** (< `md:` breakpoint):
  - Flow line hidden
  - Flow dots hidden
  - Header padding left: 0
  - Title and ID stacked vertically

### Animations & Transitions
- **Header Hover**: `bg-gray-800` (0.3s)
- **Detail Expand**: `max-height` transition (0.5s cubic-bezier)
- **Icon Rotation**: `rotate(180deg)` when expanded (0.3s)
- **Dot Scale**: `scale-150` when active (0.3s)

---

## Testing Checklist

### Functional Tests
- [ ] Click any project header - detail expands smoothly
- [ ] Click same header again - detail collapses smoothly
- [ ] Click different header - previous detail closes, new one opens
- [ ] Only one detail section open at a time (accordion behavior)
- [ ] Chevron icon rotates 180° when expanded
- [ ] Flow line dot scales when project is active

### Visual Tests
- [ ] Flow line appears as vertical gradient on left (desktop only)
- [ ] Project IDs appear in monospace font
- [ ] Tech tags appear in monospace, smaller than IDs
- [ ] Dashboard placeholder has gradient background
- [ ] CTA buttons have accent color background
- [ ] Hover states work on project headers
- [ ] All Lucide icons render correctly

### Responsive Tests
- [ ] Desktop (≥768px): Flow line and dots visible, left padding applied
- [ ] Mobile (<768px): Flow line and dots hidden, no left padding
- [ ] Title and ID stack vertically on mobile
- [ ] All content readable on small screens

### Performance Tests
- [ ] Smooth transitions with no janky animations
- [ ] Icons re-initialize when detail sections open
- [ ] No console errors in browser DevTools

---

## Deployment Steps

1. **Backup current version**:
   ```bash
   git checkout -b backup-portfolio-cards
   git add backend/app/templates/public/home.html
   git commit -m "Backup current portfolio card layout"
   git checkout main
   ```

2. **Implement changes**:
   - Replace HTML in `home.html` (Task 1)
   - Add JavaScript to `main.js` (Task 2)
   - Add CSS to `base.html` (Task 3 - optional)

3. **Test locally**:
   ```bash
   cd backend
   python app.py
   # Visit http://127.0.0.1:8000
   ```

4. **Verify**:
   - Click through all 3 projects
   - Test on mobile viewport (DevTools)
   - Check browser console for errors

5. **Commit and deploy**:
   ```bash
   git add .
   git commit -m "Implement expanding flow list portfolio section"
   git push origin main
   ```

---

## Rollback Plan

If issues arise, restore the previous card layout:

```bash
git checkout backup-portfolio-cards backend/app/templates/public/home.html
git checkout HEAD~1 backend/static/js/main.js
git commit -m "Rollback to card-based portfolio layout"
```

---

## Future Enhancements

1. **Connect to Database**: Replace placeholder data with dynamic `projects` from Flask backend
2. **Add Filtering**: Allow filtering by tech stack (Python, JS, etc.)
3. **Add Search**: Search projects by title or description
4. **Add Images**: Replace placeholders with actual project screenshots
5. **Add Links**: Make CTA buttons link to actual project detail pages
6. **Add Analytics**: Track which projects are most viewed/expanded
7. **Add Animations**: Add entrance animations for flow line and dots
8. **Add Keyboard Nav**: Allow arrow keys to navigate between projects

---

## Dependencies

### Already Available
- ✅ Tailwind CSS (loaded via CDN in base.html)
- ✅ Lucide Icons (loaded via CDN in base.html)
- ✅ Dark mode enabled (forced in base.html line 89)
- ✅ Custom color palette configured (base.html lines 64-78)

### Not Required
- No new npm packages
- No new Python packages
- No database migrations
- No API endpoints

---

## Notes for Developer

1. **Do not modify**: Keep the Featured Project section (lines 41-150) unchanged
2. **Do not modify**: Keep the About section (lines 152-448) unchanged
3. **Only replace**: Projects section (lines 450-509)
4. **Placeholder images**: Currently using Lucide icons, can be replaced with real images later
5. **CTA buttons**: Currently non-functional, can link to `/projects/{slug}` when integrated with backend
6. **Mobile-first**: Design is fully responsive using Tailwind's `md:` breakpoints
7. **Accessibility**: All interactive elements are keyboard-accessible (native `<button>` and clickable `<div>`)

---

## Acceptance Criteria

✅ **Visual Design**:
- Dark background with light text
- Vertical flow line on the left (desktop)
- Monospace font for IDs and tech tags
- Hover state on project headers

✅ **Functionality**:
- Accordion behavior (one open at a time)
- Smooth expand/collapse transitions
- Icon rotation animation
- No JavaScript errors

✅ **Content**:
- 3 projects displayed (P-001, P-002, P-003)
- Each has title, tech tag, summary, image placeholder, and CTA
- All placeholder data matches requirements

✅ **Responsive**:
- Works on desktop (≥768px)
- Works on mobile (<768px)
- Flow line hidden on mobile
- Content readable on all screen sizes

---

## Conclusion

This plan provides step-by-step instructions to replace the current card-based portfolio section with an interactive Expanding Flow List. The implementation uses only Tailwind CSS and vanilla JavaScript (no frameworks), maintains the existing dark mode aesthetic, and is fully responsive. All code examples are complete and ready to copy-paste into the specified files.
