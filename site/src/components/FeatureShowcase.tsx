import { useState, useEffect, useRef } from "preact/hooks";

interface Feature {
  icon: string;
  title: string;
  description: string;
  color: string;
  details: string[];
}

const FEATURES: Feature[] = [
  {
    icon: "🔒",
    title: "AppArmor",
    description: "Mandatory Access Control",
    color: "mauve",
    details: ["Profile enforcement", "App sandboxing", "Zero-day protection"],
  },
  {
    icon: "🛡️",
    title: "nftables Firewall",
    description: "Network Protection",
    color: "blue",
    details: ["Default deny policy", "Rate limiting", "Port knocking ready"],
  },
  {
    icon: "🦠",
    title: "ClamAV",
    description: "Antivirus Scanning",
    color: "teal",
    details: ["On-access scanning", "Auto-updates", "Low overhead"],
  },
  {
    icon: "🔐",
    title: "LUKS2",
    description: "Full Disk Encryption",
    color: "green",
    details: ["AES-256 encryption", "TPM support", "Secure boot ready"],
  },
  {
    icon: "🧅",
    title: "Kernel Hardening",
    description: "Exploit Mitigations",
    color: "peach",
    details: ["ASLR/SMEP/SMAP", "Lockdown mode", "PTI enabled"],
  },
  {
    icon: "🔍",
    title: "Audit Framework",
    description: "Security Monitoring",
    color: "pink",
    details: ["System auditing", "Log analysis", "Intrusion detection"],
  },
];

export function FeatureShowcase() {
  const [activeFeature, setActiveFeature] = useState<number | null>(null);
  const [isVisible, setIsVisible] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
        }
      },
      { threshold: 0.1 },
    );

    if (containerRef.current) {
      observer.observe(containerRef.current);
    }

    return () => observer.disconnect();
  }, []);

  return (
    <div ref={containerRef} class="relative">
      {/* Animated background orbs */}
      <div class="absolute inset-0 overflow-hidden pointer-events-none">
        <div class="absolute top-1/4 left-1/4 w-96 h-96 bg-mauve/10 rounded-full blur-[100px] animate-pulse-glow" />
        <div
          class="absolute bottom-1/4 right-1/4 w-80 h-80 bg-blue/10 rounded-full blur-[80px] animate-pulse-glow"
          style={{ animationDelay: "1s" }}
        />
      </div>

      {/* Feature grid */}
      <div class="grid grid-cols-2 md:grid-cols-3 gap-4 relative z-10">
        {FEATURES.map((feature, index) => (
          <FeatureCard
            key={feature.title}
            feature={feature}
            index={index}
            isActive={activeFeature === index}
            isVisible={isVisible}
            onHover={() => setActiveFeature(index)}
            onLeave={() => setActiveFeature(null)}
          />
        ))}
      </div>

      {/* Central security visualization */}
      <div class="mt-12 flex justify-center">
        <div class="relative">
          {/* Orbiting dots */}
          <div class="absolute inset-0 animate-spin-slow">
            {[0, 1, 2, 3, 4, 5].map((i) => (
              <div
                key={i}
                class="absolute w-2 h-2 bg-mauve rounded-full"
                style={{
                  top: "50%",
                  left: "50%",
                  transform: `rotate(${i * 60}deg) translateX(60px) translateY(-50%)`,
                }}
              />
            ))}
          </div>

          {/* Shield icon */}
          <div class="w-32 h-32 rounded-full bg-gradient-to-br from-surface0 to-mantle border-2 border-mauve/30 flex items-center justify-center animate-float-slow glow-mauve">
            <span class="text-5xl">🛡️</span>
          </div>

          {/* Pulse rings */}
          <div
            class="absolute inset-0 animate-ping rounded-full border border-mauve/20"
            style={{ animationDuration: "3s" }}
          />
          <div
            class="absolute inset-[-10px] animate-ping rounded-full border border-mauve/10"
            style={{ animationDuration: "3s", animationDelay: "1s" }}
          />
        </div>
      </div>
    </div>
  );
}

function FeatureCard({
  feature,
  index,
  isActive,
  isVisible,
  onHover,
  onLeave,
}: {
  feature: Feature;
  index: number;
  isActive: boolean;
  isVisible: boolean;
  onHover: () => void;
  onLeave: () => void;
}) {
  return (
    <div
      onMouseEnter={onHover}
      onMouseLeave={onLeave}
      class={`
        glass-card rounded-2xl p-5 cursor-pointer
        transition-all duration-500 ease-out
        ${isActive ? `glow-${feature.color} scale-105` : "hover:scale-102"}
        ${isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"}
      `}
      style={{ transitionDelay: `${index * 100}ms` }}
    >
      {/* Icon with glow */}
      <div class="relative mb-3">
        <div
          class={`absolute inset-0 bg-${feature.color}/20 rounded-xl blur-xl transition-opacity duration-300 ${isActive ? "opacity-100" : "opacity-0"}`}
        />
        <div
          class={`relative w-12 h-12 rounded-xl bg-${feature.color}/20 flex items-center justify-center text-2xl transition-transform duration-300 ${isActive ? "scale-110" : ""}`}
        >
          {feature.icon}
        </div>
      </div>

      {/* Title */}
      <h3 class={`font-bold text-${feature.color} mb-1 transition-colors`}>
        {feature.title}
      </h3>

      {/* Description */}
      <p class="text-sm text-subtext0 mb-3">{feature.description}</p>

      {/* Expandable details */}
      <div
        class={`space-y-1 overflow-hidden transition-all duration-300 ${isActive ? "max-h-32 opacity-100" : "max-h-0 opacity-0"}`}
      >
        {feature.details.map((detail) => (
          <div
            key={detail}
            class="flex items-center gap-2 text-xs text-overlay0"
          >
            <span class={`text-${feature.color}`}>✓</span>
            <span>{detail}</span>
          </div>
        ))}
      </div>

      {/* Shine effect overlay */}
      <div class="absolute inset-0 rounded-2xl overflow-hidden pointer-events-none">
        <div
          class={`absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent transform -skew-x-12 transition-transform duration-700 ${isActive ? "translate-x-full" : "-translate-x-full"}`}
        />
      </div>
    </div>
  );
}
