import { useState, useEffect, useRef } from 'preact/hooks';

type Page = 'welcome' | 'features' | 'shortcuts' | 'apps' | 'finish';

const FEATURES = [
  { icon: '🔒', name: 'AppArmor', desc: 'App sandboxing', color: 'mauve' },
  { icon: '🛡️', name: 'Firewall', desc: 'nftables protection', color: 'blue' },
  { icon: '🦠', name: 'ClamAV', desc: 'Antivirus scanning', color: 'teal' },
  { icon: '💾', name: 'Encryption', desc: 'LUKS2 support', color: 'green' },
  { icon: '🎨', name: 'Hyprland', desc: 'Wayland compositor', color: 'pink' },
  { icon: '⚡', name: 'Catppuccin', desc: 'Dark theme', color: 'peach' },
];

const SHORTCUTS = [
  { key: 'Super + Return', action: 'Terminal' },
  { key: 'Super + Space', action: 'App launcher' },
  { key: 'Super + Q', action: 'Close window' },
  { key: 'Super + 1-9', action: 'Switch workspace' },
  { key: 'Super + E', action: 'File manager' },
  { key: 'Super + L', action: 'Lock screen' },
];

const APPS = [
  { icon: '🛡️', name: 'Aegis Armor', desc: 'Security settings' },
  { icon: '🎚️', name: 'Aegis Mixer', desc: 'Audio mixer' },
  { icon: '📦', name: 'Aegis Updates', desc: 'System updates' },
  { icon: '💾', name: 'Aegis Backup', desc: 'Backup & restore' },
];

export function WelcomeAppMockup() {
  const [currentPage, setCurrentPage] = useState<Page>('welcome');
  const [animateIn, setAnimateIn] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setAnimateIn(true);
  }, []);

  const pages: Page[] = ['welcome', 'features', 'shortcuts', 'apps', 'finish'];
  const currentIndex = pages.indexOf(currentPage);

  const goNext = () => {
    if (currentIndex < pages.length - 1) {
      setCurrentPage(pages[currentIndex + 1]);
    }
  };

  const goBack = () => {
    if (currentIndex > 0) {
      setCurrentPage(pages[currentIndex - 1]);
    }
  };

  return (
    <div
      ref={containerRef}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      class={`relative bg-base rounded-2xl border-2 overflow-hidden shadow-2xl transition-all duration-300 ${animateIn ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'} ${isHovered ? 'shadow-teal/30 border-teal/50' : 'border-surface0'}`}
    >
      {/* GTK Header Bar */}
      <div class="bg-crust px-4 py-2.5 flex items-center justify-between border-b border-surface0">
        <div class="flex items-center gap-3">
          <div class="flex gap-1.5">
            <div class="w-3 h-3 rounded-full bg-red/80 hover:bg-red transition-colors cursor-pointer"></div>
            <div class="w-3 h-3 rounded-full bg-yellow/80 hover:bg-yellow transition-colors cursor-pointer"></div>
            <div class="w-3 h-3 rounded-full bg-green/80 hover:bg-green transition-colors cursor-pointer"></div>
          </div>
          <span class="text-sm font-bold text-teal ml-2">Welcome to Aegis Linux</span>
        </div>
      </div>

      {/* Main Content */}
      <div style={{ height: '300px' }} class="flex flex-col">
        <div class="flex-1 overflow-y-auto">
          {currentPage === 'welcome' && (
            <div class="animate-fadeIn flex flex-col items-center justify-center h-full p-8 text-center">
              <div class="bg-gradient-to-br from-mauve/10 to-blue/10 rounded-2xl p-8">
                <div class="text-5xl mb-4">🛡️</div>
                <h2 class="text-xl font-bold text-text mb-2">Welcome to Aegis Linux</h2>
                <p class="text-xs text-subtext0 max-w-xs">
                  Security by Default. Beauty by Design.
                </p>
                <p class="text-[10px] text-overlay0 mt-3">
                  Let's get you set up in just a few steps.
                </p>
              </div>
            </div>
          )}

          {currentPage === 'features' && (
            <div class="animate-fadeIn p-4">
              <h2 class="text-lg font-bold text-text mb-1">What Makes Aegis Special</h2>
              <p class="text-[10px] text-subtext0 mb-3">Security and productivity out of the box.</p>
              <div class="grid grid-cols-3 gap-2">
                {FEATURES.map((f) => (
                  <div key={f.name} class="bg-mantle rounded-lg p-2.5 border border-surface0">
                    <div class="text-lg mb-1">{f.icon}</div>
                    <div class={`text-xs font-bold text-${f.color}`}>{f.name}</div>
                    <div class="text-[9px] text-overlay0">{f.desc}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {currentPage === 'shortcuts' && (
            <div class="animate-fadeIn p-4">
              <h2 class="text-lg font-bold text-text mb-1">Essential Shortcuts</h2>
              <p class="text-[10px] text-subtext0 mb-3">Super key (⊞) for most actions.</p>
              <div class="bg-mantle rounded-lg border border-surface0 p-2 space-y-1">
                {SHORTCUTS.map((s) => (
                  <div key={s.key} class="flex items-center gap-3 py-1">
                    <span class="text-[10px] font-mono bg-surface0 px-2 py-0.5 rounded text-text w-28">{s.key}</span>
                    <span class="text-xs text-subtext0">{s.action}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {currentPage === 'apps' && (
            <div class="animate-fadeIn p-4">
              <h2 class="text-lg font-bold text-text mb-1">Aegis Tools</h2>
              <p class="text-[10px] text-subtext0 mb-3">Custom apps to manage your system.</p>
              <div class="space-y-2">
                {APPS.map((app) => (
                  <div key={app.name} class="bg-mantle rounded-lg border border-surface0 p-3 flex items-center gap-3">
                    <span class="text-xl">{app.icon}</span>
                    <div class="flex-1">
                      <div class="text-sm font-bold text-text">{app.name}</div>
                      <div class="text-[10px] text-overlay0">{app.desc}</div>
                    </div>
                    <button class="text-[10px] bg-surface0 hover:bg-blue hover:text-crust px-2 py-1 rounded transition-colors">
                      Launch
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {currentPage === 'finish' && (
            <div class="animate-fadeIn flex flex-col items-center justify-center h-full p-8 text-center">
              <div class="bg-gradient-to-br from-green/10 to-teal/10 rounded-2xl p-8">
                <div class="text-5xl mb-4 text-green">✓</div>
                <h2 class="text-xl font-bold text-text mb-2">You're All Set!</h2>
                <p class="text-xs text-subtext0 max-w-xs">
                  Aegis Linux is ready to use.
                </p>
                <div class="text-[10px] text-overlay0 mt-3 space-y-1">
                  <div><span class="text-text font-bold">Super + Space</span> to launch apps</div>
                  <div><span class="text-text font-bold">Super + Return</span> for terminal</div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Bottom Navigation */}
        <div class="bg-mantle border-t border-surface0 px-4 py-3 flex items-center justify-between">
          <button
            onClick={goBack}
            disabled={currentIndex === 0}
            class={`text-xs font-semibold px-4 py-2 rounded-lg transition-colors ${
              currentIndex === 0
                ? 'text-overlay0 bg-surface0/50 cursor-not-allowed'
                : 'text-text bg-surface0 hover:bg-surface1'
            }`}
          >
            Back
          </button>

          {/* Progress dots */}
          <div class="flex gap-2">
            {pages.map((p, i) => (
              <div
                key={p}
                class={`w-2 h-2 rounded-full transition-colors ${
                  i === currentIndex
                    ? 'bg-mauve'
                    : i < currentIndex
                      ? 'bg-green'
                      : 'bg-surface0'
                }`}
              />
            ))}
          </div>

          <button
            onClick={goNext}
            class={`text-xs font-semibold px-4 py-2 rounded-lg transition-colors ${
              currentIndex === pages.length - 1
                ? 'bg-green text-crust hover:bg-teal'
                : 'bg-mauve text-crust hover:bg-pink'
            }`}
          >
            {currentIndex === pages.length - 1 ? 'Get Started' : 'Next'}
          </button>
        </div>
      </div>

      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(8px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fadeIn {
          animation: fadeIn 0.25s ease-out;
        }
      `}</style>
    </div>
  );
}
