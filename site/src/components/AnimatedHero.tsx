import { useState, useEffect, useRef } from "preact/hooks";

const WORDS = ["Security", "Privacy", "Beauty", "Power"];
const COLORS = ["mauve", "pink", "blue", "green"];

export function AnimatedHero() {
  const [wordIndex, setWordIndex] = useState(0);
  const [isVisible, setIsVisible] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setIsVisible(true);

    const interval = setInterval(() => {
      setWordIndex((i) => (i + 1) % WORDS.length);
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div ref={containerRef} class="relative">
      {/* Animated tagline */}
      <h1
        class={`text-5xl md:text-7xl font-bold text-text mb-6 transition-all duration-1000 ${isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"}`}
      >
        <span class="relative inline-block">
          <span
            key={wordIndex}
            class={`animate-gradient-text inline-block`}
            style={{
              animation: "slideInUp 0.5s ease-out forwards",
            }}
          >
            {WORDS[wordIndex]}
          </span>
        </span>
        <span class="text-subtext0"> by Default.</span>
        <br />
        <span class="text-pink text-glow-pink">Beauty</span>
        <span class="text-subtext0"> by Design.</span>
      </h1>

      {/* Subtitle with typing effect look */}
      <p
        class={`text-lg md:text-xl text-subtext0 max-w-2xl mx-auto mb-8 transition-all duration-1000 delay-300 ${isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"}`}
      >
        A hardened Arch Linux distribution with a stunning Hyprland desktop.
        <br class="hidden md:block" />
        Perfect for developers and content creators who care about privacy.
      </p>

      {/* Animated CTA buttons */}
      <div
        class={`flex flex-col sm:flex-row items-center justify-center gap-4 transition-all duration-1000 delay-500 ${isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"}`}
      >
        <a
          href="/download"
          class="group relative bg-mauve hover:bg-pink text-crust font-semibold px-8 py-4 rounded-xl transition-all duration-300 text-lg overflow-hidden glow-mauve hover:glow-pink shine-effect"
        >
          <span class="relative z-10 flex items-center gap-2">
            <span>Download ISO</span>
            <svg
              class="w-5 h-5 group-hover:translate-x-1 transition-transform"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="2"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M13 7l5 5m0 0l-5 5m5-5H6"
              />
            </svg>
          </span>
        </a>
        <a
          href="https://github.com/alexogeny/aegis"
          target="_blank"
          rel="noopener noreferrer"
          class="group glass-card text-text hover:text-mauve font-semibold px-8 py-4 rounded-xl transition-all duration-300 text-lg flex items-center gap-2 hover-lift"
        >
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
          </svg>
          <span>View on GitHub</span>
          <svg
            class="w-4 h-4 opacity-50 group-hover:opacity-100 group-hover:translate-x-1 transition-all"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            stroke-width="2"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
            />
          </svg>
        </a>
      </div>

      {/* Floating badges */}
      <div
        class={`mt-12 flex flex-wrap items-center justify-center gap-4 transition-all duration-1000 delay-700 ${isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"}`}
      >
        <Badge icon="🔒" text="AppArmor" color="mauve" delay={0} />
        <Badge icon="🛡️" text="Firewall" color="blue" delay={100} />
        <Badge icon="🎨" text="Hyprland" color="pink" delay={200} />
        <Badge icon="⚡" text="Catppuccin" color="peach" delay={300} />
        <Badge icon="🖥️" text="NVIDIA Ready" color="green" delay={400} />
      </div>

      <style>{`
        @keyframes slideInUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  );
}

function Badge({
  icon,
  text,
  color,
  delay,
}: {
  icon: string;
  text: string;
  color: string;
  delay: number;
}) {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setIsVisible(true), delay + 800);
    return () => clearTimeout(timer);
  }, [delay]);

  return (
    <div
      class={`glass-light px-4 py-2 rounded-full flex items-center gap-2 hover-lift cursor-default transition-all duration-500 ${isVisible ? "opacity-100 scale-100" : "opacity-0 scale-90"}`}
      style={{ transitionDelay: `${delay}ms` }}
    >
      <span class="text-base">{icon}</span>
      <span class={`text-sm font-medium text-${color}`}>{text}</span>
    </div>
  );
}
