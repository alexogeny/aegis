import { useRef, useState, useEffect } from 'preact/hooks';

interface TiltCardProps {
  href: string;
  title: string;
  description: string;
  icon: string;
  color: string;
  tags: { icon: string; label: string; color: string }[];
  cta: string;
}

export function TiltCard({ href, title, description, icon, color, tags, cta }: TiltCardProps) {
  const cardRef = useRef<HTMLAnchorElement>(null);
  const [transform, setTransform] = useState('');
  const [glowPosition, setGlowPosition] = useState({ x: 0, y: 0 });
  const [isHovered, setIsHovered] = useState(false);

  const handleMouseMove = (e: MouseEvent) => {
    if (!cardRef.current) return;

    const rect = cardRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;

    const rotateX = (y - centerY) / 20;
    const rotateY = (centerX - x) / 20;

    setTransform(`perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`);
    setGlowPosition({ x, y });
  };

  const handleMouseLeave = () => {
    setTransform('');
    setIsHovered(false);
  };

  const handleMouseEnter = () => {
    setIsHovered(true);
  };

  return (
    <a
      ref={cardRef}
      href={href}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      onMouseEnter={handleMouseEnter}
      class={`
        group relative block overflow-hidden
        glass-card rounded-2xl p-8
        transition-all duration-200 ease-out
        border-2 border-surface1 hover:border-${color}
      `}
      style={{ transform }}
    >
      {/* Dynamic spotlight effect */}
      <div
        class="absolute pointer-events-none transition-opacity duration-300"
        style={{
          width: '300px',
          height: '300px',
          left: glowPosition.x - 150,
          top: glowPosition.y - 150,
          background: `radial-gradient(circle, var(--color-${color}) 0%, transparent 70%)`,
          opacity: isHovered ? 0.1 : 0,
          filter: 'blur(40px)',
        }}
      />

      {/* Background gradient on hover */}
      <div class={`absolute inset-0 bg-gradient-to-br from-${color}/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500`} />

      {/* Floating icon background */}
      <div class={`absolute -right-8 -top-8 text-[120px] opacity-5 group-hover:opacity-10 transition-all duration-500 group-hover:scale-110`}>
        {icon}
      </div>

      <div class="relative">
        {/* Icon with glow */}
        <div class="relative inline-block mb-6">
          <div class={`absolute inset-0 bg-${color}/20 rounded-xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500`} />
          <div class={`relative w-16 h-16 rounded-xl bg-${color}/20 flex items-center justify-center text-3xl group-hover:scale-110 transition-transform duration-300`}>
            {icon}
          </div>
        </div>

        <h3 class={`text-2xl font-bold text-text group-hover:text-${color} transition-colors duration-300 mb-3`}>
          {title}
        </h3>
        <p class="text-subtext0 mb-6">
          {description}
        </p>

        {/* Tech tags with stagger animation */}
        <div class="flex flex-wrap gap-2 mb-6">
          {tags.map((tag, i) => (
            <span
              key={tag.label}
              class={`text-xs bg-${tag.color}/20 text-${tag.color} px-3 py-1.5 rounded-full font-medium flex items-center gap-1 transition-all duration-300 group-hover:scale-105`}
              style={{ transitionDelay: `${i * 50}ms` }}
            >
              <span class="text-[10px]">{tag.icon}</span>
              {tag.label}
            </span>
          ))}
        </div>

        {/* CTA with arrow animation */}
        <div class={`flex items-center gap-2 text-${color} font-semibold group-hover:gap-3 transition-all duration-300`}>
          <span>{cta}</span>
          <svg class="w-5 h-5 transition-transform group-hover:translate-x-1" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6"/>
          </svg>
        </div>
      </div>

      {/* Bottom gradient line */}
      <div class={`absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-${color} to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500`} />
    </a>
  );
}
