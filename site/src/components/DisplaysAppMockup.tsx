import { useState, useEffect, useRef } from "preact/hooks";

interface Monitor {
  id: string;
  name: string;
  width: number;
  height: number;
  refresh: number;
  x: number;
  y: number;
  scale: number;
  primary: boolean;
}

const MONITORS: Monitor[] = [
  {
    id: "1",
    name: "DP-1",
    width: 3840,
    height: 2160,
    refresh: 60,
    x: 0,
    y: 0,
    scale: 1.5,
    primary: true,
  },
  {
    id: "2",
    name: "HDMI-A-1",
    width: 2560,
    height: 1440,
    refresh: 144,
    x: 3840,
    y: 0,
    scale: 1.0,
    primary: false,
  },
];

const RESOLUTIONS = ["3840x2160", "2560x1440", "1920x1080"];
const REFRESH_RATES = ["144 Hz", "120 Hz", "60 Hz", "30 Hz"];
const SCALES = [
  "1.0 (100%)",
  "1.25 (125%)",
  "1.5 (150%)",
  "1.75 (175%)",
  "2.0 (200%)",
];

export function DisplaysAppMockup() {
  const [selected, setSelected] = useState<Monitor>(MONITORS[0]);
  const [animateIn, setAnimateIn] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setAnimateIn(true);
  }, []);

  const handleApply = () => {
    setHasChanges(false);
  };

  return (
    <div
      ref={containerRef}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      class={`relative bg-base rounded-2xl border-2 overflow-hidden shadow-2xl transition-all duration-300 ${animateIn ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"} ${isHovered ? "shadow-blue/30 border-blue/50" : "border-surface0"}`}
    >
      {/* GTK Header Bar */}
      <div class="bg-crust px-4 py-2.5 flex items-center justify-between border-b border-surface0">
        <div class="flex items-center gap-3">
          <div class="flex gap-1.5">
            <div class="w-3 h-3 rounded-full bg-red/80 hover:bg-red transition-colors cursor-pointer"></div>
            <div class="w-3 h-3 rounded-full bg-yellow/80 hover:bg-yellow transition-colors cursor-pointer"></div>
            <div class="w-3 h-3 rounded-full bg-green/80 hover:bg-green transition-colors cursor-pointer"></div>
          </div>
          <span class="text-sm font-bold text-blue ml-2">Aegis Displays</span>
        </div>
        <div class="flex items-center gap-2">
          <button class="text-xs bg-blue text-crust font-semibold px-3 py-1.5 rounded-lg hover:bg-sapphire transition-colors">
            Detect
          </button>
          <button
            onClick={handleApply}
            class={`text-xs font-semibold px-3 py-1.5 rounded-lg transition-colors ${
              hasChanges
                ? "bg-green text-crust hover:bg-teal"
                : "bg-surface1 text-overlay0 cursor-not-allowed"
            }`}
          >
            Apply
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div style={{ height: "320px" }} class="overflow-y-auto p-4">
        {/* Display arrangement preview */}
        <div class="bg-mantle rounded-xl border border-surface0 p-4 mb-4">
          <div class="flex items-center justify-between mb-3">
            <span class="text-sm font-bold text-text">Display Arrangement</span>
            <span class="text-[10px] text-overlay0">
              Click to select, drag to arrange
            </span>
          </div>

          {/* Monitor preview area */}
          <div class="bg-base rounded-lg border border-surface0 p-4 h-28 relative">
            {MONITORS.map((mon) => {
              const previewScale = 0.03;
              const width = mon.width * previewScale;
              const height = mon.height * previewScale;

              return (
                <button
                  key={mon.id}
                  onClick={() => {
                    setSelected(mon);
                    setHasChanges(true);
                  }}
                  class={`absolute rounded-lg border-2 flex flex-col items-center justify-center transition-all cursor-pointer hover:scale-105 ${
                    selected.id === mon.id
                      ? "bg-surface1 border-mauve shadow-lg"
                      : mon.primary
                        ? "bg-surface0 border-green"
                        : "bg-surface0 border-surface1 hover:border-surface2"
                  }`}
                  style={{
                    width: `${width}px`,
                    height: `${height}px`,
                    left: `${mon.x * previewScale + 20}px`,
                    top: `${mon.y * previewScale + 10}px`,
                  }}
                >
                  <span class="text-[10px] font-bold text-text">
                    {mon.name}
                  </span>
                  <span class="text-[8px] text-overlay0">
                    {mon.width}x{mon.height}
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Monitor settings */}
        <div class="bg-mantle rounded-xl border border-surface0 p-4">
          <div class="flex items-center gap-3 mb-4">
            <span class="text-sm font-bold text-text">{selected.name}</span>
            {selected.primary && (
              <span class="text-[9px] bg-green text-crust font-bold px-2 py-0.5 rounded">
                PRIMARY
              </span>
            )}
          </div>

          <div class="space-y-3">
            {/* Resolution */}
            <SettingRow
              label="Resolution"
              description="Display resolution in pixels"
            >
              <select
                class="bg-surface0 text-text text-xs rounded-lg px-3 py-1.5 border border-surface1 focus:outline-none focus:border-mauve"
                onChange={() => setHasChanges(true)}
              >
                {RESOLUTIONS.map((r) => (
                  <option
                    key={r}
                    selected={r === `${selected.width}x${selected.height}`}
                  >
                    {r}
                  </option>
                ))}
              </select>
            </SettingRow>

            {/* Refresh Rate */}
            <SettingRow label="Refresh Rate" description="Screen refresh rate">
              <select
                class="bg-surface0 text-text text-xs rounded-lg px-3 py-1.5 border border-surface1 focus:outline-none focus:border-mauve"
                onChange={() => setHasChanges(true)}
              >
                {REFRESH_RATES.map((r) => (
                  <option key={r} selected={r === `${selected.refresh} Hz`}>
                    {r}
                  </option>
                ))}
              </select>
            </SettingRow>

            {/* Scale */}
            <SettingRow label="Scale" description="UI scaling factor">
              <select
                class="bg-surface0 text-text text-xs rounded-lg px-3 py-1.5 border border-surface1 focus:outline-none focus:border-mauve"
                onChange={() => setHasChanges(true)}
              >
                {SCALES.map((s) => (
                  <option
                    key={s}
                    selected={s.startsWith(selected.scale.toString())}
                  >
                    {s}
                  </option>
                ))}
              </select>
            </SettingRow>

            {/* VRR */}
            <SettingRow
              label="Variable Refresh Rate"
              description="FreeSync / G-Sync"
            >
              <ToggleSwitch
                defaultChecked={selected.refresh > 60}
                onChange={() => setHasChanges(true)}
              />
            </SettingRow>

            {/* Primary */}
            <SettingRow label="Set as Primary" description="Main display">
              <ToggleSwitch
                defaultChecked={selected.primary}
                onChange={() => setHasChanges(true)}
              />
            </SettingRow>
          </div>
        </div>
      </div>

      {/* Bottom hints */}
      <div class="bg-surface0/30 px-4 py-2 flex items-center justify-between text-[10px] text-overlay0 border-t border-surface0">
        <span>Changes persist via Hyprland config</span>
        <div class="flex gap-2">
          <span class="bg-surface0 px-2 py-0.5 rounded">hyprctl</span>
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

function SettingRow({
  label,
  description,
  children,
}: {
  label: string;
  description: string;
  children: preact.ComponentChildren;
}) {
  return (
    <div class="flex items-center justify-between py-2 border-b border-surface0 last:border-0">
      <div>
        <div class="text-xs font-semibold text-text">{label}</div>
        <div class="text-[10px] text-overlay0">{description}</div>
      </div>
      {children}
    </div>
  );
}

function ToggleSwitch({
  defaultChecked = false,
  onChange,
}: {
  defaultChecked?: boolean;
  onChange?: () => void;
}) {
  const [checked, setChecked] = useState(defaultChecked);

  return (
    <button
      onClick={() => {
        setChecked(!checked);
        onChange?.();
      }}
      class={`w-10 h-5 rounded-full transition-colors relative ${
        checked ? "bg-mauve" : "bg-surface1"
      }`}
    >
      <div
        class={`w-4 h-4 bg-text rounded-full absolute top-0.5 transition-all ${
          checked ? "left-5" : "left-0.5"
        }`}
      />
    </button>
  );
}
