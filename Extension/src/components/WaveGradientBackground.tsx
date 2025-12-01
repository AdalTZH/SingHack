import { useEffect, useRef } from 'react';

interface WaveGradientBackgroundProps {
  speedMultiplier?: number;
}

export function WaveGradientBackground({ speedMultiplier = 1 }: WaveGradientBackgroundProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const currentSpeedRef = useRef(speedMultiplier);
  const targetSpeedRef = useRef(speedMultiplier);

  useEffect(() => {
    targetSpeedRef.current = speedMultiplier;
  }, [speedMultiplier]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d', { alpha: false });
    if (!ctx) return;
    
    // Enable image smoothing for better quality when scaled
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = 'high';

    let w: number = 0, h: number = 0;
    let renderW: number = 0, renderH: number = 0;
    let time = 0;
    let animationFrameId: number;
    let resizeTimeout: NodeJS.Timeout;
    let lastFrameTime = 0;
    const FPS_LIMIT = 20; // Reduced to 20fps for better performance
    const FRAME_INTERVAL = 1000 / FPS_LIMIT;

    // Render at 1/5 resolution for much better performance, then scale up
    const SCALE_FACTOR = 5;

    function resize() {
      clearTimeout(resizeTimeout);
      resizeTimeout = setTimeout(() => {
        if (!canvas || !canvas.parentElement) return;
        const parent = canvas.parentElement;
        w = parent.offsetWidth || 400;
        h = parent.scrollHeight || 800; // Use scrollHeight to get full content height
        
        // Set display size
        canvas.style.width = w + 'px';
        canvas.style.height = h + 'px';
        
        // Set render size (much lower resolution)
        renderW = Math.floor(w / SCALE_FACTOR);
        renderH = Math.floor(h / SCALE_FACTOR);
        canvas.width = renderW;
        canvas.height = renderH;
      }, 100);
    }

    // Observe parent element size changes (including content height changes)
    let resizeObserver: ResizeObserver | null = null;
    if (canvas.parentElement) {
      resizeObserver = new ResizeObserver(() => {
        resize();
      });
      resizeObserver.observe(canvas.parentElement);
    }

    function draw(currentTime: number) {
      if (!ctx || !canvas || !renderW || !renderH || renderW <= 0 || renderH <= 0) {
        animationFrameId = requestAnimationFrame(draw);
        return;
      }

      // Throttle to target FPS
      const elapsed = currentTime - lastFrameTime;
      if (elapsed < FRAME_INTERVAL) {
        animationFrameId = requestAnimationFrame(draw);
        return;
      }
      lastFrameTime = currentTime - (elapsed % FRAME_INTERVAL);

      // Smoothly interpolate current speed towards target speed
      const lerpFactor = 0.05;
      currentSpeedRef.current += (targetSpeedRef.current - currentSpeedRef.current) * lerpFactor;

      const colors = [
        { r: 39, g: 39, b: 96 },      // #272760 - dark blue
        { r: 225, g: 31, b: 38 },     // #E11F26 - red
        { r: 255, g: 255, b: 255 }    // #FFFFFF - white
      ];

      try {
        const imageData = ctx.createImageData(renderW, renderH);
        const data = imageData.data;

        // Pre-calculate time-based values (huge performance boost!)
        const t1 = time * 0.001 * currentSpeedRef.current;
        const t2 = time * 0.0008 * currentSpeedRef.current;
        const t3 = time * 0.0012 * currentSpeedRef.current;
        
        const cosT1 = Math.cos(t1);
        const sinT2 = Math.sin(t2);
        const sinT3 = Math.sin(t3);
        const cosT1Half = Math.cos(t1 * 0.5);
        const sinT2Half = Math.sin(t2 * 0.5);

        for (let y = 0; y < renderH; y++) {
          for (let x = 0; x < renderW; x++) {
            // Reduced to 4 waves instead of 6 for better performance
            const wave1 = Math.sin(x * 0.008 + cosT1 * 100 + y * 0.006);
            const wave2 = Math.cos(y * 0.009 + sinT2 * 80 - x * 0.005);
            const wave3 = Math.sin((x * cosT1Half * 0.01) + (y * sinT2Half * 0.01));
            const wave4 = Math.cos((x * 0.007) + (y * 0.008) + sinT3 * 50);

            const combined = (wave1 + wave2 + wave3 + wave4) / 4;
            const normalized = (combined + 1) / 2;

            let r: number, g: number, b: number;

            // Blue 0-0.35, Red 0.35-0.70, White 0.70-1.0
            if (normalized < 0.35) {
              // Blue zone - 35%
              r = colors[0].r;
              g = colors[0].g;
              b = colors[0].b;
            } else if (normalized < 0.70) {
              // Red zone - 35%
              const t = (normalized - 0.35) / 0.35;
              r = colors[0].r + (colors[1].r - colors[0].r) * t;
              g = colors[0].g + (colors[1].g - colors[0].g) * t;
              b = colors[0].b + (colors[1].b - colors[0].b) * t;
            } else {
              // White - 30%
              const t = (normalized - 0.70) / 0.30;
              r = colors[1].r + (colors[2].r - colors[1].r) * t;
              g = colors[1].g + (colors[2].g - colors[1].g) * t;
              b = colors[1].b + (colors[2].b - colors[1].b) * t;
            }

            const index = (y * renderW + x) * 4;
            data[index] = Math.round(r);
            data[index + 1] = Math.round(g);
            data[index + 2] = Math.round(b);
            data[index + 3] = 255;
          }
        }

        ctx.putImageData(imageData, 0, 0);
      } catch (e) {
        console.error('Draw error:', e);
      }

      // Increment time and use modulo to prevent it from growing too large
      // This prevents floating-point precision issues and freezing
      time = (time + 1) % 100000;
      animationFrameId = requestAnimationFrame(draw);
    }

    window.addEventListener('resize', resize);
    resize();
    animationFrameId = requestAnimationFrame(draw);

    return () => {
      window.removeEventListener('resize', resize);
      clearTimeout(resizeTimeout);
      if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
      }
      if (resizeObserver) {
        resizeObserver.disconnect();
      }
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="absolute top-0 left-0 w-full min-h-full"
      style={{ display: 'block', height: '100%', zIndex: 0 }}
    />
  );
}
