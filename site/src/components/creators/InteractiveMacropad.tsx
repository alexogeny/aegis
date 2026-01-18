import { useState, useEffect } from 'preact/hooks';

interface MacroButton {
  icon: string;
  label: string;
  color: string;
  active?: boolean;
}

const initialButtons: MacroButton[] = [
  // Row 1
  { icon: '🔴', label: 'LIVE', color: 'red', active: false },
  { icon: '🎬', label: 'RECORD', color: 'mauve', active: false },
  { icon: '📷', label: 'SCENE 1', color: 'blue', active: true },
  { icon: '🎮', label: 'SCENE 2', color: 'teal', active: false },
  { icon: '💬', label: 'SCENE 3', color: 'peach', active: false },
  // Row 2
  { icon: '🎤', label: 'MIC', color: 'green', active: true },
  { icon: '🔊', label: 'MUSIC', color: 'pink', active: true },
  { icon: '📺', label: 'GAME', color: 'sky', active: false },
  { icon: '💡', label: 'LIGHT', color: 'yellow', active: true },
  { icon: '⚙️', label: 'CONFIG', color: 'surface1', active: false },
  // Row 3
  { icon: '🎵', label: 'SFX 1', color: 'lavender', active: false },
  { icon: '🎶', label: 'SFX 2', color: 'sapphire', active: false },
  { icon: '👏', label: 'SFX 3', color: 'flamingo', active: false },
  { icon: '😂', label: 'SFX 4', color: 'rosewater', active: false },
  { icon: '📱', label: 'PHONE', color: 'maroon', active: false },
];

const lightTextColors = ['yellow', 'rosewater', 'flamingo', 'lavender', 'surface1', 'pink'];

export function InteractiveMacropad() {
  const [buttons, setButtons] = useState<MacroButton[]>(initialButtons);
  const [currentPage, setCurrentPage] = useState(1);
  const [pressedIndex, setPressedIndex] = useState<number | null>(null);
  const [lastAction, setLastAction] = useState<string>('');

  // Handle button press
  const handlePress = (index: number) => {
    const btn = buttons[index];
    setPressedIndex(index);

    // Toggle active state for toggleable buttons
    if (['LIVE', 'RECORD', 'MIC', 'MUSIC', 'GAME', 'LIGHT'].includes(btn.label)) {
      setButtons(prev => prev.map((b, i) =>
        i === index ? { ...b, active: !b.active } : b
      ));
      setLastAction(`${btn.label} ${!btn.active ? 'ON' : 'OFF'}`);
    }
    // Scene buttons - make exclusive
    else if (btn.label.startsWith('SCENE')) {
      setButtons(prev => prev.map((b, i) => ({
        ...b,
        active: b.label.startsWith('SCENE') ? i === index : b.active
      })));
      setLastAction(`Switched to ${btn.label}`);
    }
    // SFX buttons - just flash
    else if (btn.label.startsWith('SFX')) {
      setLastAction(`Playing ${btn.label}`);
    }
    // Other buttons
    else {
      setLastAction(`${btn.label} triggered`);
    }

    // Release animation
    setTimeout(() => setPressedIndex(null), 150);
  };

  return (
    <div class="bg-mantle rounded-2xl border-2 border-surface0 overflow-hidden shadow-2xl">
      {/* Window Title Bar */}
      <div class="bg-crust px-4 py-3 flex items-center justify-between border-b border-surface0">
        <div class="flex items-center gap-3">
          <div class="flex gap-1.5">
            <div class="w-3 h-3 rounded-full bg-red/80"></div>
            <div class="w-3 h-3 rounded-full bg-yellow/80"></div>
            <div class="w-3 h-3 rounded-full bg-green/80"></div>
          </div>
          <div class="flex items-center gap-2 ml-2">
            <span class="text-lg">🎮</span>
            <span class="text-sm font-bold text-text">Aegis Macropad</span>
            <span class="text-xs text-green">● Connected</span>
          </div>
        </div>
        <span class="text-[10px] text-overlay0 bg-surface0 px-2 py-0.5 rounded">Click buttons!</span>
      </div>

      {/* Content */}
      <div class="p-6 bg-base">
        {/* Status bar */}
        <div class="bg-surface0/50 rounded-lg px-3 py-2 mb-4 flex items-center justify-between">
          <span class="text-xs text-overlay0">Last action:</span>
          <span class="text-xs text-text font-mono">{lastAction || 'None'}</span>
        </div>

        {/* 5x3 Button Grid */}
        <div class="grid grid-cols-5 gap-2 mb-6">
          {buttons.map((btn, index) => {
            const isPressed = pressedIndex === index;
            const isLightText = lightTextColors.includes(btn.color);

            return (
              <button
                key={`${btn.label}-${index}`}
                onClick={() => handlePress(index)}
                class={`aspect-square rounded-xl flex flex-col items-center justify-center p-1 cursor-pointer transition-all duration-100 border select-none ${
                  isPressed
                    ? 'scale-90 brightness-125'
                    : 'hover:scale-105 active:scale-95'
                } ${
                  btn.active
                    ? `bg-gradient-to-br from-${btn.color} to-${btn.color}/70 shadow-lg shadow-${btn.color}/30 border-${btn.color}/50`
                    : `bg-gradient-to-br from-surface1 to-surface0 border-surface0 opacity-70 hover:opacity-100`
                }`}
              >
                <span class={`text-2xl ${isPressed ? 'scale-110' : ''} transition-transform`}>
                  {btn.icon}
                </span>
                <span class={`text-[8px] font-bold mt-0.5 ${
                  btn.active
                    ? isLightText ? 'text-crust' : 'text-white'
                    : 'text-subtext0'
                }`}>
                  {btn.label}
                </span>
                {/* Active indicator */}
                {btn.active && (
                  <div class={`absolute -top-0.5 -right-0.5 w-2 h-2 rounded-full bg-white shadow-sm animate-pulse`}></div>
                )}
              </button>
            );
          })}
        </div>

        {/* Page Indicators */}
        <div class="flex justify-center gap-2 mb-4">
          {[1, 2, 3].map(page => (
            <button
              key={page}
              onClick={() => setCurrentPage(page)}
              class={`px-3 py-1 rounded text-xs font-bold transition-all ${
                currentPage === page
                  ? 'bg-mauve text-crust'
                  : 'bg-surface0 text-subtext0 hover:bg-surface1'
              }`}
            >
              {page}
            </button>
          ))}
        </div>

        {/* Category Chips */}
        <div class="flex flex-wrap justify-center gap-2 text-xs">
          <span class="bg-surface0 text-subtext0 px-3 py-1.5 rounded-full hover:bg-surface1 cursor-pointer transition-colors">OBS Scenes</span>
          <span class="bg-surface0 text-subtext0 px-3 py-1.5 rounded-full hover:bg-surface1 cursor-pointer transition-colors">Audio Sources</span>
          <span class="bg-surface0 text-subtext0 px-3 py-1.5 rounded-full hover:bg-surface1 cursor-pointer transition-colors">Sound FX</span>
          <span class="bg-surface0 text-subtext0 px-3 py-1.5 rounded-full hover:bg-surface1 cursor-pointer transition-colors">Lighting</span>
          <span class="bg-surface0 text-subtext0 px-3 py-1.5 rounded-full hover:bg-surface1 cursor-pointer transition-colors">System</span>
        </div>
      </div>
    </div>
  );
}
