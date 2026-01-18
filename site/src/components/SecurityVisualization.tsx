import { useState, useEffect } from 'preact/hooks';

interface SecurityLayer {
  id: string;
  name: string;
  color: string;
  icon: string;
  shortDesc: string;
  longDesc: string;
  examples: string[];
}

const SECURITY_LAYERS: SecurityLayer[] = [
  {
    id: 'apparmor',
    name: 'AppArmor',
    color: 'mauve',
    icon: '',
    shortDesc: 'Application Sandboxing',
    longDesc: 'Each app runs in its own sandbox with strict rules about what files it can read, what network connections it can make, and what other apps it can talk to.',
    examples: ['Firefox can\'t read your SSH keys', 'Discord can\'t access your Documents folder', 'Untrusted apps are automatically restricted'],
  },
  {
    id: 'nftables',
    name: 'Firewall',
    color: 'blue',
    icon: '',
    shortDesc: 'Network Protection',
    longDesc: 'A strict "deny by default" firewall blocks all incoming connections unless you explicitly allow them. Outgoing connections from suspicious apps are also monitored.',
    examples: ['Blocks port scanning attacks', 'Prevents unauthorized remote access', 'Rate-limits connection attempts'],
  },
  {
    id: 'kernel',
    name: 'Kernel Hardening',
    color: 'green',
    icon: '',
    shortDesc: 'Deep System Protection',
    longDesc: 'The Linux kernel itself is hardened with security features that make it much harder for attackers to exploit vulnerabilities, even if they find one.',
    examples: ['Memory addresses are randomized (ASLR)', 'Kernel is locked down from tampering', 'Exploit mitigations are enabled'],
  },
  {
    id: 'clamav',
    name: 'ClamAV',
    color: 'teal',
    icon: '',
    shortDesc: 'Malware Detection',
    longDesc: 'Real-time scanning watches for known malware signatures. Downloaded files are automatically scanned before you can open them.',
    examples: ['Scans downloads automatically', 'Catches known malware signatures', 'Quarantines threats safely'],
  },
  {
    id: 'luks',
    name: 'LUKS2 Encryption',
    color: 'peach',
    icon: '',
    shortDesc: 'Disk Encryption',
    longDesc: 'Your entire disk is encrypted. Even if someone steals your computer, they can\'t read your data without your password.',
    examples: ['Full disk encryption at boot', 'Protected by strong passphrase', 'Data is unreadable without key'],
  },
];

export function SecurityVisualization() {
  const [activeLayer, setActiveLayer] = useState<string | null>(null);
  const [animationPhase, setAnimationPhase] = useState(0);
  const [pulsingLayer, setPulsingLayer] = useState(0);

  // Subtle animation cycling through layers
  useEffect(() => {
    const interval = setInterval(() => {
      setPulsingLayer((prev) => (prev + 1) % SECURITY_LAYERS.length);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  // Initial animation
  useEffect(() => {
    const phases = [0, 1, 2, 3, 4, 5];
    let i = 0;
    const interval = setInterval(() => {
      if (i < phases.length) {
        setAnimationPhase(phases[i]);
        i++;
      } else {
        clearInterval(interval);
      }
    }, 200);
    return () => clearInterval(interval);
  }, []);

  const activeLayerData = activeLayer ? SECURITY_LAYERS.find((l) => l.id === activeLayer) : null;

  return (
    <div class="bg-base rounded-2xl border-2 border-surface0 overflow-hidden">
      {/* Header */}
      <div class="bg-crust px-4 py-3 border-b border-surface0 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="flex gap-1.5">
            <div class="w-3 h-3 rounded-full bg-red/80"></div>
            <div class="w-3 h-3 rounded-full bg-yellow/80"></div>
            <div class="w-3 h-3 rounded-full bg-green/80"></div>
          </div>
          <span class="text-sm font-bold text-text ml-2">Aegis Security Layers</span>
        </div>
        <span class="text-xs text-overlay0 bg-surface0 px-2 py-1 rounded">Hover to explore</span>
      </div>

      <div class="p-6 md:p-8">
        <div class="grid md:grid-cols-2 gap-6">
          {/* Layer Stack Visualization */}
          <div class="relative">
            {/* Shield icon behind layers */}
            <div class="absolute inset-0 flex items-center justify-center pointer-events-none opacity-10">
              <span class="text-[120px]"></span>
            </div>

            {/* Stacked layers */}
            <div class="space-y-2 relative z-10">
              {SECURITY_LAYERS.map((layer, index) => {
                const isActive = activeLayer === layer.id;
                const isPulsing = pulsingLayer === index && !activeLayer;
                const isVisible = animationPhase > index;

                return (
                  <div
                    key={layer.id}
                    class={`
                      transform transition-all duration-300 cursor-pointer
                      ${isVisible ? 'translate-x-0 opacity-100' : 'translate-x-8 opacity-0'}
                      ${isActive ? 'scale-105 -translate-x-1' : ''}
                    `}
                    style={{ transitionDelay: `${index * 50}ms` }}
                    onMouseEnter={() => setActiveLayer(layer.id)}
                    onMouseLeave={() => setActiveLayer(null)}
                  >
                    <div
                      class={`
                        rounded-xl p-4 border-2 transition-all duration-300
                        bg-${layer.color}/20 border-${layer.color}/40
                        ${isActive ? `border-${layer.color} shadow-lg shadow-${layer.color}/20` : ''}
                        ${isPulsing ? 'animate-pulse' : ''}
                      `}
                      style={{
                        backgroundColor: isActive ? `var(--${layer.color}-bg)` : undefined,
                      }}
                    >
                      <div class="flex items-center gap-3">
                        <span class="text-2xl">{layer.icon}</span>
                        <div class="flex-1 min-w-0">
                          <div class={`font-bold text-${layer.color}`}>{layer.name}</div>
                          <div class="text-subtext0 text-sm truncate">{layer.shortDesc}</div>
                        </div>
                        <div
                          class={`
                            w-2 h-2 rounded-full transition-all duration-300
                            bg-${layer.color} ${isActive || isPulsing ? 'animate-ping' : 'opacity-50'}
                          `}
                        />
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Connecting lines animation */}
            <div class="absolute left-6 top-8 bottom-8 w-0.5 bg-surface0 opacity-30 rounded" />
          </div>

          {/* Detail Panel */}
          <div class="bg-mantle rounded-xl p-6 border border-surface0 min-h-[300px] flex flex-col">
            {activeLayerData ? (
              <div class="animate-fadeIn">
                <div class="flex items-center gap-3 mb-4">
                  <span class="text-3xl">{activeLayerData.icon}</span>
                  <div>
                    <h3 class={`text-xl font-bold text-${activeLayerData.color}`}>
                      {activeLayerData.name}
                    </h3>
                    <div class="text-sm text-overlay0">{activeLayerData.shortDesc}</div>
                  </div>
                </div>

                <p class="text-subtext0 mb-6 leading-relaxed">{activeLayerData.longDesc}</p>

                <div class="space-y-2">
                  <div class="text-xs font-bold text-overlay0 uppercase tracking-wider mb-2">
                    What this means for you:
                  </div>
                  {activeLayerData.examples.map((example, i) => (
                    <div key={i} class="flex items-center gap-2 text-sm text-subtext0">
                      <span class={`text-${activeLayerData.color}`}></span>
                      {example}
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div class="flex-1 flex flex-col items-center justify-center text-center">
                <div class="text-5xl mb-4 opacity-50"></div>
                <div class="text-text font-semibold mb-2">5 Layers of Protection</div>
                <div class="text-subtext0 text-sm max-w-xs">
                  Hover over each layer to learn how it protects you. All layers work together automatically.
                </div>

                {/* Mini status indicators */}
                <div class="flex gap-2 mt-6">
                  {SECURITY_LAYERS.map((layer) => (
                    <div
                      key={layer.id}
                      class={`w-3 h-3 rounded-full bg-${layer.color} opacity-60`}
                      title={layer.name}
                    />
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Bottom status bar */}
        <div class="mt-6 bg-surface0/30 rounded-lg p-3 flex flex-wrap items-center justify-between gap-4">
          <div class="flex items-center gap-2 text-sm">
            <span class="text-green"></span>
            <span class="text-green font-semibold">All protections active</span>
          </div>
          <div class="flex flex-wrap gap-3 text-xs text-overlay0">
            <span class="bg-surface0 px-2 py-1 rounded">1500+ AppArmor profiles</span>
            <span class="bg-surface0 px-2 py-1 rounded">Firewall: deny by default</span>
            <span class="bg-surface0 px-2 py-1 rounded">ClamAV signatures: up to date</span>
          </div>
        </div>
      </div>

      {/* Add CSS animation */}
      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(8px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fadeIn {
          animation: fadeIn 0.3s ease-out;
        }
      `}</style>
    </div>
  );
}
