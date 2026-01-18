import { useState, useEffect, useRef } from "preact/hooks";

type State = "checking" | "updates" | "updating" | "done";

interface Package {
  name: string;
  current: string;
  new: string;
  source: "official" | "aur";
}

const PACKAGES: Package[] = [
  { name: "linux", current: "6.7.1", new: "6.7.2", source: "official" },
  { name: "firefox", current: "121.0", new: "122.0", source: "official" },
  { name: "mesa", current: "23.3.3", new: "23.3.4", source: "official" },
  { name: "hyprland", current: "0.34.0", new: "0.35.0", source: "official" },
  {
    name: "visual-studio-code-bin",
    current: "1.85.1",
    new: "1.85.2",
    source: "aur",
  },
  { name: "spotify", current: "1.2.28", new: "1.2.30", source: "aur" },
];

export function UpdatesAppMockup() {
  const [state, setState] = useState<State>("updates");
  const [progress, setProgress] = useState(0);
  const [animateIn, setAnimateIn] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setAnimateIn(true);
  }, []);

  const handleUpdate = () => {
    setState("updating");
    setProgress(0);

    // Simulate update progress
    const interval = setInterval(() => {
      setProgress((p) => {
        if (p >= 100) {
          clearInterval(interval);
          setState("done");
          return 100;
        }
        return p + Math.random() * 15;
      });
    }, 300);
  };

  const handleRefresh = () => {
    setState("checking");
    setTimeout(() => setState("updates"), 1500);
  };

  const officialPkgs = PACKAGES.filter((p) => p.source === "official");
  const aurPkgs = PACKAGES.filter((p) => p.source === "aur");

  return (
    <div
      ref={containerRef}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      class={`relative bg-base rounded-2xl border-2 overflow-hidden shadow-2xl transition-all duration-300 ${animateIn ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"} ${isHovered ? "shadow-green/30 border-green/50" : "border-surface0"}`}
    >
      {/* GTK Header Bar */}
      <div class="bg-crust px-4 py-2.5 flex items-center justify-between border-b border-surface0">
        <div class="flex items-center gap-3">
          <div class="flex gap-1.5">
            <div class="w-3 h-3 rounded-full bg-red/80 hover:bg-red transition-colors cursor-pointer"></div>
            <div class="w-3 h-3 rounded-full bg-yellow/80 hover:bg-yellow transition-colors cursor-pointer"></div>
            <div class="w-3 h-3 rounded-full bg-green/80 hover:bg-green transition-colors cursor-pointer"></div>
          </div>
          <span class="text-sm font-bold text-green ml-2">Aegis Updates</span>
        </div>
        <button
          onClick={handleRefresh}
          class="text-overlay0 hover:text-text transition-colors p-1 rounded hover:bg-surface0"
        >
          <span class="text-sm">↻</span>
        </button>
      </div>

      {/* Main Content */}
      <div style={{ height: "300px" }} class="overflow-y-auto p-4">
        {state === "checking" && (
          <div class="animate-fadeIn flex flex-col items-center justify-center h-full">
            <div class="w-10 h-10 border-3 border-mauve border-t-transparent rounded-full animate-spin mb-4"></div>
            <div class="text-lg font-bold text-text">
              Checking for updates...
            </div>
            <div class="text-xs text-subtext0">This may take a moment</div>
          </div>
        )}

        {state === "updates" && (
          <div class="animate-fadeIn">
            {/* Header */}
            <div class="flex items-center justify-between mb-4">
              <div class="flex items-center gap-3">
                <span class="text-xl font-bold text-text">
                  Updates Available
                </span>
                <span class="bg-mauve text-crust text-xs font-bold px-2 py-0.5 rounded-full">
                  {PACKAGES.length}
                </span>
              </div>
              <button
                onClick={handleUpdate}
                class="bg-green text-crust text-xs font-bold px-4 py-2 rounded-lg hover:bg-teal transition-colors"
              >
                Update All
              </button>
            </div>

            {/* Info banner */}
            <div class="bg-blue/10 border border-blue/30 rounded-lg p-3 mb-4 flex items-center gap-2">
              <span class="text-blue">ℹ</span>
              <span class="text-[10px] text-subtext0">
                Review packages below, then click Update All to install.
              </span>
            </div>

            {/* Official packages */}
            <div class="bg-mantle rounded-xl border border-surface0 p-3 mb-3">
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-bold text-text">
                  Official Repositories
                </span>
                <span class="text-[10px] text-overlay0">
                  {officialPkgs.length} packages
                </span>
              </div>
              <div class="space-y-1">
                {officialPkgs.map((pkg) => (
                  <PackageRow key={pkg.name} pkg={pkg} />
                ))}
              </div>
            </div>

            {/* AUR packages */}
            <div class="bg-mantle rounded-xl border border-surface0 p-3">
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-bold text-text">AUR Packages</span>
                <span class="text-[10px] text-overlay0">
                  {aurPkgs.length} packages
                </span>
              </div>
              <div class="space-y-1">
                {aurPkgs.map((pkg) => (
                  <PackageRow key={pkg.name} pkg={pkg} />
                ))}
              </div>
            </div>
          </div>
        )}

        {state === "updating" && (
          <div class="animate-fadeIn">
            <div class="flex items-center gap-3 mb-4">
              <div class="w-5 h-5 border-2 border-green border-t-transparent rounded-full animate-spin"></div>
              <span class="text-lg font-bold text-text">
                Updating system...
              </span>
            </div>

            {/* Progress bar */}
            <div class="bg-surface0 rounded-lg h-3 mb-4 overflow-hidden">
              <div
                class="bg-gradient-to-r from-green to-teal h-full rounded-lg transition-all duration-300"
                style={{ width: `${Math.min(progress, 100)}%` }}
              />
            </div>

            {/* Terminal output */}
            <div class="bg-crust rounded-lg p-3 font-mono text-[10px] text-text h-44 overflow-y-auto">
              <div class="text-green">
                :: Synchronizing package databases...
              </div>
              <div class="text-subtext0">downloading core.db...</div>
              <div class="text-subtext0">downloading extra.db...</div>
              <div class="text-green mt-2">
                :: Starting full system upgrade...
              </div>
              {progress > 20 && (
                <div class="text-subtext0">
                  ( 1/{PACKAGES.length}) upgrading linux...
                </div>
              )}
              {progress > 35 && (
                <div class="text-subtext0">
                  ( 2/{PACKAGES.length}) upgrading firefox...
                </div>
              )}
              {progress > 50 && (
                <div class="text-subtext0">
                  ( 3/{PACKAGES.length}) upgrading mesa...
                </div>
              )}
              {progress > 65 && (
                <div class="text-subtext0">
                  ( 4/{PACKAGES.length}) upgrading hyprland...
                </div>
              )}
              {progress > 80 && (
                <div class="text-subtext0">
                  ( 5/{PACKAGES.length}) building visual-studio-code-bin...
                </div>
              )}
              {progress > 95 && (
                <div class="text-subtext0">
                  ( 6/{PACKAGES.length}) building spotify...
                </div>
              )}
            </div>
          </div>
        )}

        {state === "done" && (
          <div class="animate-fadeIn flex flex-col items-center justify-center h-full">
            <div class="text-5xl mb-4 text-green">✓</div>
            <div class="text-xl font-bold text-text mb-2">Update Complete!</div>
            <div class="text-xs text-subtext0 mb-4">
              All packages updated successfully
            </div>
            <button
              onClick={handleRefresh}
              class="bg-surface0 text-text text-xs font-semibold px-4 py-2 rounded-lg hover:bg-surface1 transition-colors"
            >
              Check Again
            </button>
          </div>
        )}
      </div>

      {/* Bottom hints */}
      <div class="bg-surface0/30 px-4 py-2 flex items-center justify-between text-[10px] text-overlay0 border-t border-surface0">
        <span>Click Update All to install</span>
        <div class="flex gap-2">
          <span class="bg-surface0 px-2 py-0.5 rounded">pacman + yay</span>
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
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
        .animate-spin {
          animation: spin 1s linear infinite;
        }
      `}</style>
    </div>
  );
}

function PackageRow({ pkg }: { pkg: Package }) {
  return (
    <div class="bg-base rounded-lg p-2 flex items-center gap-2">
      <div class="flex-1 min-w-0">
        <div class="flex items-center gap-2">
          <span class="text-text font-semibold text-xs">{pkg.name}</span>
          <span
            class={`text-[8px] font-bold px-1.5 py-0.5 rounded ${
              pkg.source === "official"
                ? "bg-blue/20 text-blue"
                : "bg-peach/20 text-peach"
            }`}
          >
            {pkg.source.toUpperCase()}
          </span>
        </div>
        <div class="text-[9px] font-mono text-overlay0">
          {pkg.current} → <span class="text-green">{pkg.new}</span>
        </div>
      </div>
    </div>
  );
}
