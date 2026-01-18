interface WaybarProps {
  activeWorkspace: number;
  time: string;
}

export function Waybar({ activeWorkspace, time }: WaybarProps) {
  const workspaces = [1, 2, 3, 4, 5];

  return (
    <div class="absolute top-2 left-3 right-3 h-10 bg-base/85 backdrop-blur-sm rounded-xl border-2 border-surface0 flex items-center justify-between px-3 font-mono text-sm font-semibold z-20">
      {/* Left - Launcher & Workspaces */}
      <div class="flex items-center gap-2">
        {/* Launcher */}
        <button class="text-mauve text-lg px-3 py-1 rounded-lg bg-surface0 hover:bg-surface1 transition-colors">

        </button>

        {/* Workspaces */}
        <div class="flex items-center gap-1 bg-surface0 rounded-lg px-2 py-1">
          {workspaces.map((ws) => (
            <button
              key={ws}
              class={`w-6 h-6 flex items-center justify-center rounded text-xs transition-all ${
                ws === activeWorkspace
                  ? 'text-mauve bg-surface1'
                  : 'text-overlay0 hover:text-text hover:bg-surface1'
              }`}
            >
              {ws}
            </button>
          ))}
        </div>
      </div>

      {/* Center - Window Title */}
      <div class="text-subtext1 text-xs hidden sm:block">
        kitty
      </div>

      {/* Right - System Tray */}
      <div class="flex items-center gap-1">
        <div class="px-3 py-1 rounded-lg bg-surface0 text-sky">

        </div>
        <div class="px-3 py-1 rounded-lg bg-surface0 text-teal">

        </div>
        <div class="px-3 py-1 rounded-lg bg-surface0 text-green">

        </div>
        <div class="px-3 py-1 rounded-lg bg-surface0 text-rosewater">
          {time}
        </div>
        <button class="px-3 py-1 rounded-lg bg-surface0 text-red hover:bg-red hover:text-base transition-colors">

        </button>
      </div>
    </div>
  );
}
