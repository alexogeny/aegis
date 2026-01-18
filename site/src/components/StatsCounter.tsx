import { useState, useEffect, useRef } from 'preact/hooks';

interface Stat {
  value: number;
  suffix: string;
  label: string;
  color: string;
}

const STATS: Stat[] = [
  { value: 40, suffix: '+', label: 'VSCode Extensions', color: 'blue' },
  { value: 80, suffix: '+', label: 'App Routing Rules', color: 'teal' },
  { value: 6, suffix: '', label: 'Virtual Audio Sinks', color: 'green' },
  { value: 100, suffix: '%', label: 'Open Source', color: 'mauve' },
];

export function StatsCounter() {
  const [isVisible, setIsVisible] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
        }
      },
      { threshold: 0.3 }
    );

    if (containerRef.current) {
      observer.observe(containerRef.current);
    }

    return () => observer.disconnect();
  }, []);

  return (
    <div ref={containerRef} class="grid grid-cols-2 md:grid-cols-4 gap-6">
      {STATS.map((stat, index) => (
        <StatCard
          key={stat.label}
          stat={stat}
          index={index}
          isVisible={isVisible}
        />
      ))}
    </div>
  );
}

function StatCard({ stat, index, isVisible }: { stat: Stat; index: number; isVisible: boolean }) {
  const [count, setCount] = useState(0);

  useEffect(() => {
    if (!isVisible) return;

    const duration = 2000;
    const steps = 60;
    const increment = stat.value / steps;
    let current = 0;

    const timer = setInterval(() => {
      current += increment;
      if (current >= stat.value) {
        setCount(stat.value);
        clearInterval(timer);
      } else {
        setCount(Math.floor(current));
      }
    }, duration / steps);

    return () => clearInterval(timer);
  }, [isVisible, stat.value]);

  return (
    <div
      class={`
        glass-card rounded-2xl p-6 text-center
        transition-all duration-700 ease-out hover-lift
        ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}
      `}
      style={{ transitionDelay: `${index * 150}ms` }}
    >
      {/* Animated number */}
      <div class={`text-4xl md:text-5xl font-bold text-${stat.color} mb-2 tabular-nums`}>
        {count}
        <span class="text-2xl">{stat.suffix}</span>
      </div>

      {/* Label */}
      <div class="text-sm text-subtext0">{stat.label}</div>

      {/* Decorative bar */}
      <div class="mt-4 h-1 bg-surface0 rounded-full overflow-hidden">
        <div
          class={`h-full bg-${stat.color} rounded-full transition-all duration-1000 ease-out`}
          style={{
            width: isVisible ? '100%' : '0%',
            transitionDelay: `${index * 150 + 500}ms`,
          }}
        />
      </div>
    </div>
  );
}
