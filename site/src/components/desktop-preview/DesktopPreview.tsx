import { useState, useEffect, useRef } from "preact/hooks";
import { Waybar } from "./Waybar";
import { Window } from "./Window";
import { Terminal } from "./Terminal";
import { AnyrunSearch } from "./AnyrunSearch";
import { Notification } from "./Notification";
import { VSCodeWindow } from "./VSCodeWindow";

interface DemoState {
  phase: number;
  terminalLines: Array<{ type: "prompt" | "output"; content: string }>;
  terminalInput: string;
  showTerminal: boolean;
  showVSCode: boolean;
  showAnyrun: boolean;
  anyrunQuery: string;
  anyrunSelected: number;
  showNotification: boolean;
  activeWorkspace: number;
}

const INITIAL_STATE: DemoState = {
  phase: 0,
  terminalLines: [],
  terminalInput: "",
  showTerminal: false,
  showVSCode: false,
  showAnyrun: false,
  anyrunQuery: "",
  anyrunSelected: 0,
  showNotification: false,
  activeWorkspace: 1,
};

export function DesktopPreview() {
  const [state, setState] = useState<DemoState>(INITIAL_STATE);
  const [time, setTime] = useState("12:34");
  const timeoutRef = useRef<number | null>(null);

  // Update time
  useEffect(() => {
    const now = new Date();
    setTime(
      now.toLocaleTimeString("en-US", {
        hour: "2-digit",
        minute: "2-digit",
        hour12: false,
      }),
    );

    const interval = setInterval(() => {
      const now = new Date();
      setTime(
        now.toLocaleTimeString("en-US", {
          hour: "2-digit",
          minute: "2-digit",
          hour12: false,
        }),
      );
    }, 60000);

    return () => clearInterval(interval);
  }, []);

  // Demo sequence
  useEffect(() => {
    const runDemo = async () => {
      const delay = (ms: number) =>
        new Promise((r) => {
          timeoutRef.current = setTimeout(r, ms) as unknown as number;
        });

      const typeText = async (text: string, setter: (t: string) => void) => {
        for (let i = 0; i <= text.length; i++) {
          setter(text.slice(0, i));
          await delay(80);
        }
      };

      // Reset
      setState(INITIAL_STATE);
      await delay(500);

      // Phase 1: Show terminal with pop-in
      setState((s) => ({ ...s, showTerminal: true, phase: 1 }));
      await delay(800);

      // Phase 2: Type neofetch command
      await typeText("neofetch", (t) =>
        setState((s) => ({ ...s, terminalInput: t })),
      );
      await delay(300);

      // Phase 3: Show neofetch output
      setState((s) => ({
        ...s,
        terminalLines: [
          { type: "prompt", content: "neofetch" },
          { type: "output", content: "neofetch" },
        ],
        terminalInput: "",
        phase: 3,
      }));
      await delay(2500);

      // Phase 4: Show Anyrun (Ctrl+Space)
      setState((s) => ({ ...s, showAnyrun: true, phase: 4 }));
      await delay(400);

      // Phase 5: Type "code" in Anyrun
      await typeText("code", (t) =>
        setState((s) => ({ ...s, anyrunQuery: t })),
      );
      await delay(600);

      // Phase 6: Select VSCode and close Anyrun
      setState((s) => ({ ...s, anyrunSelected: 0 }));
      await delay(400);
      setState((s) => ({ ...s, showAnyrun: false, phase: 6 }));
      await delay(200);

      // Phase 7: Open VSCode window
      setState((s) => ({ ...s, showVSCode: true, phase: 7 }));
      await delay(2000);

      // Phase 8: Switch to workspace 2 (slide animation simulated by changing active workspace)
      setState((s) => ({ ...s, activeWorkspace: 2, phase: 8 }));
      await delay(1500);

      // Phase 9: Show notification
      setState((s) => ({ ...s, showNotification: true, phase: 9 }));
      await delay(4000);

      // Pause before reset
      setState((s) => ({ ...s, showNotification: false }));
      await delay(2000);

      // Loop - fade out and restart
      setState(INITIAL_STATE);
      await delay(1000);
      runDemo();
    };

    runDemo();

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  return (
    <div class="relative w-full aspect-video bg-crust rounded-xl overflow-hidden border border-surface0 shadow-2xl">
      {/* Wallpaper gradient */}
      <div
        class="absolute inset-0"
        style={{
          background:
            "linear-gradient(135deg, #1e1e2e 0%, #181825 50%, #11111b 100%)",
        }}
      />

      {/* Subtle pattern overlay */}
      <div
        class="absolute inset-0 opacity-5"
        style={{
          backgroundImage: `radial-gradient(circle at 25% 25%, #cba6f7 1px, transparent 1px),
                           radial-gradient(circle at 75% 75%, #f5c2e7 1px, transparent 1px)`,
          backgroundSize: "60px 60px",
        }}
      />

      {/* Waybar */}
      <Waybar activeWorkspace={state.activeWorkspace} time={time} />

      {/* Terminal Window */}
      {state.showTerminal && (
        <Window
          title="kitty"
          icon=""
          x={40}
          y={60}
          width={500}
          height={320}
          active={!state.showVSCode}
          visible={state.showTerminal}
        >
          <Terminal
            lines={state.terminalLines}
            currentInput={state.terminalInput}
            showCursor={!state.showAnyrun}
          />
        </Window>
      )}

      {/* VSCode Window */}
      {state.showVSCode && (
        <Window
          title="Visual Studio Code"
          icon=""
          x={120}
          y={100}
          width={550}
          height={340}
          active={true}
          visible={state.showVSCode}
        >
          <VSCodeWindow />
        </Window>
      )}

      {/* Anyrun Search */}
      <AnyrunSearch
        visible={state.showAnyrun}
        query={state.anyrunQuery}
        selectedIndex={state.anyrunSelected}
      />

      {/* Notification */}
      <Notification
        visible={state.showNotification}
        title="ClamAV"
        body="Scan complete. No threats detected."
        icon=""
      />

      {/* Keyboard hints */}
      <div class="absolute bottom-4 left-4 flex gap-2">
        <div class="bg-surface0/80 backdrop-blur-sm text-overlay0 text-xs px-2 py-1 rounded font-mono">
          Super + Return = Terminal
        </div>
        <div class="bg-surface0/80 backdrop-blur-sm text-overlay0 text-xs px-2 py-1 rounded font-mono">
          Ctrl + Space = Search
        </div>
      </div>
    </div>
  );
}
