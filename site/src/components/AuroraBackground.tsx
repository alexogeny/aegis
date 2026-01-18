import { useEffect, useRef } from 'preact/hooks';

export function AuroraBackground() {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    let animationFrame: number;
    let time = 0;

    const animate = () => {
      time += 0.002;

      const blobs = container.querySelectorAll('.aurora-blob');
      blobs.forEach((blob, i) => {
        const el = blob as HTMLElement;
        const offset = i * 1.5;
        const x = Math.sin(time + offset) * 20;
        const y = Math.cos(time * 0.7 + offset) * 15;
        const scale = 1 + Math.sin(time * 0.5 + offset) * 0.1;
        el.style.transform = `translate(${x}%, ${y}%) scale(${scale})`;
      });

      animationFrame = requestAnimationFrame(animate);
    };

    animate();

    return () => cancelAnimationFrame(animationFrame);
  }, []);

  return (
    <div ref={containerRef} class="fixed inset-0 overflow-hidden pointer-events-none z-0">
      {/* Large morphing gradient blobs */}
      <div
        class="aurora-blob absolute w-[800px] h-[800px] rounded-full opacity-20 blur-[100px] morph-blob"
        style={{
          background: 'radial-gradient(circle, rgba(203, 166, 247, 0.4) 0%, transparent 70%)',
          top: '-20%',
          left: '-10%',
        }}
      />
      <div
        class="aurora-blob absolute w-[600px] h-[600px] rounded-full opacity-15 blur-[80px] morph-blob"
        style={{
          background: 'radial-gradient(circle, rgba(137, 180, 250, 0.4) 0%, transparent 70%)',
          top: '30%',
          right: '-15%',
          animationDelay: '-2s',
        }}
      />
      <div
        class="aurora-blob absolute w-[700px] h-[700px] rounded-full opacity-10 blur-[90px] morph-blob"
        style={{
          background: 'radial-gradient(circle, rgba(245, 194, 231, 0.4) 0%, transparent 70%)',
          bottom: '-10%',
          left: '20%',
          animationDelay: '-4s',
        }}
      />
      <div
        class="aurora-blob absolute w-[500px] h-[500px] rounded-full opacity-15 blur-[70px] morph-blob"
        style={{
          background: 'radial-gradient(circle, rgba(148, 226, 213, 0.3) 0%, transparent 70%)',
          top: '50%',
          left: '50%',
          animationDelay: '-6s',
        }}
      />

      {/* Subtle grid overlay */}
      <div
        class="absolute inset-0 opacity-[0.02]"
        style={{
          backgroundImage: `
            linear-gradient(rgba(203, 166, 247, 0.5) 1px, transparent 1px),
            linear-gradient(90deg, rgba(203, 166, 247, 0.5) 1px, transparent 1px)
          `,
          backgroundSize: '100px 100px',
        }}
      />

      {/* Noise texture */}
      <div
        class="absolute inset-0 opacity-[0.015]"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E")`,
        }}
      />
    </div>
  );
}
