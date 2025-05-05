<script lang="ts">
  import { onMount, onDestroy } from 'svelte';

  let canvasElement: HTMLCanvasElement;
  let ctx: CanvasRenderingContext2D; // We will ensure this is set before drawing
  let animationFrameId: number;

  interface Particle {
    x: number;
    y: number;
    vx: number;
    vy: number;
    radius: number;
    color: string;
  }

  let particles: Particle[] = [];
  const particleCount = 80; // Adjust density
  const maxConnectionDist = 120; // Adjust connection distance
  const particleSpeed = 0.5; // Adjust speed
  const colors = ['#00ccff', '#00aaff', '#0088ff', '#4d4dff', '#ffffff']; // Techy colors

  function resizeCanvas() {
    if (!canvasElement) return;
    canvasElement.width = window.innerWidth;
    canvasElement.height = window.innerHeight;
    // Re-initialize particles on resize if needed, or adjust existing
    // For simplicity, we'll let them continue from current position
  }

  function initParticles() {
    particles = [];
    const width = window.innerWidth;
    const height = window.innerHeight;
    for (let i = 0; i < particleCount; i++) {
      particles.push({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * particleSpeed * 2,
        vy: (Math.random() - 0.5) * particleSpeed * 2,
        radius: Math.random() * 2 + 1,
        color: colors[Math.floor(Math.random() * colors.length)]
      });
    }
  }

  function draw() {
    // Now we assume ctx and canvasElement are valid because draw() is only called when they are.

    const width = canvasElement.width;
    const height = canvasElement.height;
    
    // Fill background
    ctx.fillStyle = '#0a192f'; // Dark blue tech background
    ctx.fillRect(0, 0, width, height);

    // Update and draw particles
    particles.forEach(p => {
      p.x += p.vx;
      p.y += p.vy;

      // Boundary checks (wrap around)
      if (p.x < 0) p.x = width;
      if (p.x > width) p.x = 0;
      if (p.y < 0) p.y = height;
      if (p.y > height) p.y = 0;

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
      ctx.fillStyle = p.color;
      ctx.fill();
    });

    // Draw connecting lines (branches)
    ctx.lineWidth = 0.5;
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < maxConnectionDist) {
            const opacity = 1 - dist / maxConnectionDist;
            // Use a mix of particle colors or a standard line color
            ctx.strokeStyle = `rgba(0, 170, 255, ${opacity * 0.6})`; // Semi-transparent cyan lines
            ctx.beginPath();
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.stroke();
        }
      }
    }

    animationFrameId = requestAnimationFrame(draw);
  }

  onMount(() => {
    const context = canvasElement.getContext('2d'); // Try to get context
    if (!context) {
      console.error("Failed to get 2D context");
      return; // Do not proceed if context failed
    }
    ctx = context; // Assign to component variable only if successful

    window.addEventListener('resize', resizeCanvas);
    resizeCanvas(); // Initial size
    initParticles(); // Create particles
    animationFrameId = requestAnimationFrame(draw); // Start animation *only if context is valid*
  });

  onDestroy(() => {
    cancelAnimationFrame(animationFrameId);
    window.removeEventListener('resize', resizeCanvas);
  });

</script>

<canvas bind:this={canvasElement} class="animated-background"></canvas>

<style>
  .animated-background {
    position: fixed; /* Position behind everything */
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: -1; /* Place it behind other content */
    display: block; /* Prevent extra space */
  }
</style> 