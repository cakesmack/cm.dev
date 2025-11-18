// Particle Murmuration Animation (like flocking birds)
class ParticleWave {
    constructor() {
        this.canvas = document.createElement('canvas');
        this.ctx = this.canvas.getContext('2d');
        this.particles = [];
        this.animationId = null;
        this.time = 0;

        // Enhanced brand colors with opacity - sophisticated palette
        this.colors = [
            'rgba(26, 32, 44, 0.12)',      // charcoal - very subtle
            'rgba(91, 142, 179, 0.18)',    // muted-blue - subtle
            'rgba(44, 82, 130, 0.15)',     // deep-blue - medium
            'rgba(217, 119, 6, 0.08)',     // accent-amber - very light
            'rgba(26, 32, 44, 0.08)',      // charcoal - lighter
            'rgba(91, 142, 179, 0.22)',    // muted-blue - slightly stronger
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
        // Responsive particle count - massive murmuration
        const isMobile = window.innerWidth < 768;
        const particleCount = isMobile ? 1000 : 2500;

        this.particles = [];

        // Start particles spread across entire viewport (and beyond)
        const centerX = this.canvas.width / 2;
        const centerY = this.canvas.height / 2;
        const spreadX = this.canvas.width * 1.1;   // Spread across 110% of width
        const spreadY = this.canvas.height * 1.0;  // Spread across 100% of height

        for (let i = 0; i < particleCount; i++) {
            this.particles.push({
                // Current position - much more spread out
                x: centerX + (Math.random() - 0.5) * spreadX,
                y: centerY + (Math.random() - 0.5) * spreadY,

                // Velocity
                vx: (Math.random() - 0.5) * 2,
                vy: (Math.random() - 0.5) * 2,

                // Particle properties
                size: Math.random() * 1.2 + 0.8,  // 0.8-2px
                color: this.colors[Math.floor(Math.random() * this.colors.length)],

                // Unique offset for flow field
                noiseOffsetX: Math.random() * 1000,
                noiseOffsetY: Math.random() * 1000,
            });
        }
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
        const centerX = this.canvas.width / 2;
        const centerY = this.canvas.height / 2;

        this.particles.forEach((particle, i) => {
            // Get flow direction from flow field
            const flowAngle = this.getFlowAngle(particle.x, particle.y, this.time);
            const flowForceX = Math.cos(flowAngle) * 0.15;
            const flowForceY = Math.sin(flowAngle) * 0.15;

            // Cohesion: gentle pull towards center to keep flock together
            const toCenterX = (centerX - particle.x) * 0.0003;
            const toCenterY = (centerY - particle.y) * 0.0003;

            // Simple alignment with nearby particles (check a few neighbors)
            let avgVx = 0, avgVy = 0, neighborCount = 0;
            for (let j = i - 5; j < i + 5; j++) {
                if (j >= 0 && j < this.particles.length && j !== i) {
                    avgVx += this.particles[j].vx;
                    avgVy += this.particles[j].vy;
                    neighborCount++;
                }
            }
            if (neighborCount > 0) {
                avgVx /= neighborCount;
                avgVy /= neighborCount;
            }
            const alignmentX = (avgVx - particle.vx) * 0.05;
            const alignmentY = (avgVy - particle.vy) * 0.05;

            // Apply forces
            particle.vx += flowForceX + toCenterX + alignmentX;
            particle.vy += flowForceY + toCenterY + alignmentY;

            // Limit speed
            const speed = Math.sqrt(particle.vx * particle.vx + particle.vy * particle.vy);
            const maxSpeed = 2;
            if (speed > maxSpeed) {
                particle.vx = (particle.vx / speed) * maxSpeed;
                particle.vy = (particle.vy / speed) * maxSpeed;
            }

            // Update position
            particle.x += particle.vx;
            particle.y += particle.vy;

            // Soft boundary wrapping
            if (particle.x < -50) particle.x = this.canvas.width + 50;
            if (particle.x > this.canvas.width + 50) particle.x = -50;
            if (particle.y < -50) particle.y = this.canvas.height + 50;
            if (particle.y > this.canvas.height + 50) particle.y = -50;
        });
    }

    drawParticles() {
        // Clear canvas cleanly (minimal trail)
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw each particle
        this.particles.forEach(particle => {
            this.ctx.fillStyle = particle.color;
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

// Initialize particle wave when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Check for reduced motion preference
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (!prefersReducedMotion) {
        window.particleWave = new ParticleWave();
    }
});
