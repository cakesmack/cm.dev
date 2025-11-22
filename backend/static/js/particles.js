// Massive Particle Wave Background Animation
class ParticleWave {
    constructor() {
        this.canvas = document.createElement('canvas');
        this.ctx = this.canvas.getContext('2d');
        this.particles = [];
        this.animationId = null;
        this.time = 0;

        // Enhanced brand colors with opacity - sophisticated palette
        this.colors = [
            'rgba(91, 142, 179, 0.25)',    // muted-blue
            'rgba(44, 82, 130, 0.20)',     // deep-blue
            'rgba(26, 32, 44, 0.15)',      // charcoal
            'rgba(91, 142, 179, 0.30)',    // muted-blue - stronger
            'rgba(217, 119, 6, 0.12)',     // accent-amber
            'rgba(26, 32, 44, 0.10)',      // charcoal - lighter
        ];

        this.init();
    }

    init() {
        // Setup canvas
        this.canvas.id = 'particle-canvas';
        this.canvas.style.position = 'fixed';
        this.canvas.style.top = '0';
        this.canvas.style.left = '0';
        this.canvas.style.width = '100%';
        this.canvas.style.height = '100%';
        this.canvas.style.zIndex = '-1';
        this.canvas.style.pointerEvents = 'none';
        this.canvas.style.filter = 'blur(1px)';
        this.canvas.style.opacity = '0.6';

        document.body.prepend(this.canvas);

        // Set canvas size
        this.resize();
        window.addEventListener('resize', () => {
            this.resize();
            this.createParticles();
        });

        // Create particle flock
        this.createParticles();

        // Start animation
        this.animate();
    }

    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }

    createParticles() {
        // DENSE particle grid covering entire screen
        const isMobile = window.innerWidth < 768;

        // Calculate grid density - particles every X pixels
        const spacing = isMobile ? 15 : 10; // Closer spacing = more particles
        const cols = Math.ceil(this.canvas.width / spacing);
        const rows = Math.ceil(this.canvas.height / spacing);

        this.particles = [];

        // Create a dense grid of particles across entire screen
        for (let row = 0; row < rows; row++) {
            for (let col = 0; col < cols; col++) {
                // Add slight randomness to grid position for organic feel
                const x = col * spacing + (Math.random() - 0.5) * spacing * 0.5;
                const y = row * spacing + (Math.random() - 0.5) * spacing * 0.5;

                this.particles.push({
                    x: x,
                    y: y,
                    baseX: x,  // Remember original position
                    baseY: y,
                    // Random initial velocity
                    vx: (Math.random() - 0.5) * 0.5,
                    vy: (Math.random() - 0.5) * 0.5,
                    // Particle properties
                    size: Math.random() * 2 + 1,  // 1-3px
                    color: this.colors[Math.floor(Math.random() * this.colors.length)],
                    // Phase offset for wave movement
                    phase: Math.random() * Math.PI * 2,
                });
            }
        }

        console.log(`Created ${this.particles.length} particles in ${cols}x${rows} grid`);
    }

    // Create a flow field using layered sine waves (simplified Perlin noise)
    getFlowAngle(x, y, time) {
        // Layer multiple sine waves to create organic, flowing patterns
        const angle = Math.sin(x * 0.003 + time * 0.3) * 2 +
                     Math.sin(y * 0.002 + time * 0.2) * 2 +
                     Math.sin((x + y) * 0.002 + time * 0.25) * 1.5 +
                     Math.cos(x * 0.004 - time * 0.15) * 1 +
                     Math.cos(y * 0.003 - time * 0.1) * 1;

        return angle;
    }

    updateParticles() {
        this.particles.forEach((particle) => {
            // Diagonal wave traveling across screen (top-left to bottom-right)
            const diagonalPosition = particle.baseX + particle.baseY;
            const waveProgress = (diagonalPosition * 0.002) - (this.time * 0.5);

            // Primary wave - moves particles in sweeping motion
            const waveOffset = Math.sin(waveProgress) * 80;
            const wave2 = Math.sin(waveProgress * 2 + this.time * 0.3) * 40;

            // Perpendicular movement for flowing effect
            const flowX = Math.sin(particle.baseY * 0.004 + this.time * 0.7) * 50;
            const flowY = Math.cos(particle.baseX * 0.004 + this.time * 0.7) * 50;

            // Combine movements - creates flowing wave across screen
            particle.x = particle.baseX + waveOffset + wave2 + flowX * 0.5;
            particle.y = particle.baseY + waveOffset + wave2 + flowY * 0.5;
        });
    }

    drawParticles() {
        // Clear canvas cleanly (minimal trail)
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw each particle with vertical fade
        this.particles.forEach(particle => {
            // Calculate opacity based on vertical position (fade out towards bottom)
            const fadeStart = this.canvas.height * 0.3; // Start fading at 30% down
            const fadeEnd = this.canvas.height * 0.8;   // Fully faded at 80% down

            let verticalOpacity = 1;
            if (particle.y > fadeStart) {
                verticalOpacity = Math.max(0, 1 - (particle.y - fadeStart) / (fadeEnd - fadeStart));
            }

            // Apply vertical fade to particle color
            const baseColor = particle.color.match(/rgba?\((\d+),\s*(\d+),\s*(\d+),\s*([\d.]+)\)/);
            if (baseColor) {
                const [, r, g, b, a] = baseColor;
                const finalOpacity = parseFloat(a) * verticalOpacity;
                this.ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${finalOpacity})`;
            } else {
                this.ctx.fillStyle = particle.color;
            }

            this.ctx.beginPath();
            this.ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
            this.ctx.fill();
        });
    }

    animate() {
        this.time += 0.016; // Increment time (~60fps)
        this.updateParticles();
        this.drawParticles();
        this.animationId = requestAnimationFrame(() => this.animate());
    }

    destroy() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
        if (this.canvas && this.canvas.parentNode) {
            this.canvas.parentNode.removeChild(this.canvas);
        }
    }
}

// Initialize particle wave when DOM is ready (only on home page)
document.addEventListener('DOMContentLoaded', () => {
    // Check for reduced motion preference
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // Only run particle animation on home page
    const isHomePage = window.location.pathname === '/' || window.location.pathname === '';

    if (!prefersReducedMotion && isHomePage) {
        window.particleWave = new ParticleWave();
    }
});
