import { useState, useEffect, useRef } from "preact/hooks";

interface Command {
  cmd: string;
  output: string[];
}

const DEMO_COMMANDS: Command[] = [
  {
    cmd: "eza -la",
    output: [
      "drwxr-xr-x  src/",
      "-rw-r--r--  Cargo.toml",
      "-rw-r--r--  README.md",
      "-rw-r--r--  .gitignore",
    ],
  },
  {
    cmd: "bat Cargo.toml",
    output: [
      "[package]",
      'name = "aegis-project"',
      'version = "0.1.0"',
      'edition = "2024"',
    ],
  },
  {
    cmd: 'rg "fn main"',
    output: ["src/main.rs:4:fn main() {"],
  },
  {
    cmd: "fd .rs",
    output: ["src/main.rs", "src/lib.rs", "src/utils.rs"],
  },
  {
    cmd: "cargo build",
    output: [
      "   Compiling aegis-project v0.1.0",
      "    Finished dev [unoptimized + debuginfo]",
    ],
  },
];

type Phase =
  | { type: "typing"; cmdIndex: number; charIndex: number }
  | { type: "executing"; cmdIndex: number; outputIndex: number }
  | { type: "waiting"; cmdIndex: number }
  | { type: "resetting" };

export function InteractiveTerminal() {
  const [phase, setPhase] = useState<Phase>({
    type: "typing",
    cmdIndex: 0,
    charIndex: 0,
  });
  const [history, setHistory] = useState<
    Array<{ type: "cmd" | "output"; content: string }>
  >([]);
  const [currentInput, setCurrentInput] = useState("");
  const terminalRef = useRef<HTMLDivElement>(null);

  // Auto-scroll
  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [history, currentInput]);

  // State machine
  useEffect(() => {
    let timer: number;

    if (phase.type === "typing") {
      const cmd = DEMO_COMMANDS[phase.cmdIndex];
      if (phase.charIndex <= cmd.cmd.length) {
        setCurrentInput(cmd.cmd.slice(0, phase.charIndex));
        timer = window.setTimeout(
          () => {
            setPhase({
              type: "typing",
              cmdIndex: phase.cmdIndex,
              charIndex: phase.charIndex + 1,
            });
          },
          50 + Math.random() * 50,
        );
      } else {
        // Done typing, execute
        timer = window.setTimeout(() => {
          setHistory((h) => [...h, { type: "cmd", content: cmd.cmd }]);
          setCurrentInput("");
          setPhase({
            type: "executing",
            cmdIndex: phase.cmdIndex,
            outputIndex: 0,
          });
        }, 300);
      }
    } else if (phase.type === "executing") {
      const cmd = DEMO_COMMANDS[phase.cmdIndex];
      if (phase.outputIndex < cmd.output.length) {
        timer = window.setTimeout(() => {
          setHistory((h) => [
            ...h,
            { type: "output", content: cmd.output[phase.outputIndex] },
          ]);
          setPhase({
            type: "executing",
            cmdIndex: phase.cmdIndex,
            outputIndex: phase.outputIndex + 1,
          });
        }, 80);
      } else {
        // Done with output
        setPhase({ type: "waiting", cmdIndex: phase.cmdIndex });
      }
    } else if (phase.type === "waiting") {
      timer = window.setTimeout(() => {
        const nextIndex = phase.cmdIndex + 1;
        if (nextIndex < DEMO_COMMANDS.length) {
          setPhase({ type: "typing", cmdIndex: nextIndex, charIndex: 0 });
        } else {
          setPhase({ type: "resetting" });
        }
      }, 1200);
    } else if (phase.type === "resetting") {
      timer = window.setTimeout(() => {
        setHistory([]);
        setCurrentInput("");
        setPhase({ type: "typing", cmdIndex: 0, charIndex: 0 });
      }, 2000);
    }

    return () => clearTimeout(timer);
  }, [phase]);

  const renderOutput = (content: string) => {
    if (content.includes("src/") || content.includes(".rs")) {
      return <span class="text-blue">{content}</span>;
    }
    if (content.includes("Compiling")) {
      return <span class="text-yellow">{content}</span>;
    }
    if (content.includes("Finished")) {
      return <span class="text-green">{content}</span>;
    }
    if (content.includes(":") && content.includes("fn")) {
      const parts = content.split(":");
      return (
        <>
          <span class="text-mauve">{parts[0]}</span>
          <span class="text-overlay0">:</span>
          <span class="text-peach">{parts[1]}</span>
          <span class="text-overlay0">:</span>
          <span class="text-text">{parts.slice(2).join(":")}</span>
        </>
      );
    }
    return <span class="text-subtext1">{content}</span>;
  };

  return (
    <div class="bg-base rounded-xl border-2 border-surface0 overflow-hidden shadow-2xl">
      {/* Title bar */}
      <div class="bg-crust px-4 py-2 flex items-center justify-between">
        <div class="flex items-center gap-2">
          <div class="w-3 h-3 rounded-full bg-red/80"></div>
          <div class="w-3 h-3 rounded-full bg-yellow/80"></div>
          <div class="w-3 h-3 rounded-full bg-green/80"></div>
          <span class="text-xs text-subtext0 ml-2">kitty</span>
        </div>
        <span class="text-[10px] text-overlay0 bg-surface0 px-2 py-0.5 rounded">
          Demo
        </span>
      </div>

      {/* Terminal content */}
      <div ref={terminalRef} class="p-4 font-mono text-sm h-64 overflow-y-auto">
        {/* Starship prompt header */}
        <div class="flex items-center flex-wrap mb-2">
          <span class="bg-mauve text-crust px-2 py-0.5 text-xs font-bold">
            {" "}
            aegis
          </span>
          <span class="text-mauve text-xs"></span>
          <span class="bg-peach text-crust px-2 py-0.5 text-xs font-bold">
            {" "}
            ~/dev
          </span>
          <span class="text-peach text-xs"></span>
          <span class="bg-yellow text-crust px-2 py-0.5 text-xs font-bold">
            {" "}
            main
          </span>
          <span class="text-yellow text-xs"></span>
          <span class="bg-teal text-crust px-2 py-0.5 text-xs font-bold">
            {" "}
          </span>
        </div>

        {/* History */}
        {history.map((entry, i) => (
          <div key={i} class={entry.type === "cmd" ? "mt-3" : "text-xs ml-2"}>
            {entry.type === "cmd" ? (
              <div class="text-text">
                <span class="text-overlay0">$</span>{" "}
                <span class="text-green">{entry.content.split(" ")[0]}</span>
                <span class="text-blue">
                  {" "}
                  {entry.content.split(" ").slice(1).join(" ")}
                </span>
              </div>
            ) : (
              renderOutput(entry.content)
            )}
          </div>
        ))}

        {/* Current input line */}
        <div class="text-text mt-3">
          <span class="text-overlay0">$</span>{" "}
          <span class="text-green">{currentInput.split(" ")[0]}</span>
          <span class="text-blue">
            {" "}
            {currentInput.split(" ").slice(1).join(" ")}
          </span>
          <span class="inline-block w-2 h-4 bg-mauve ml-0.5 animate-pulse align-middle"></span>
        </div>
      </div>

      {/* Tool hints */}
      <div class="bg-surface0/30 px-4 py-2 flex flex-wrap gap-2 text-[10px] text-overlay0 border-t border-surface0">
        <span class="bg-surface0 px-2 py-0.5 rounded">eza = modern ls</span>
        <span class="bg-surface0 px-2 py-0.5 rounded">bat = cat + syntax</span>
        <span class="bg-surface0 px-2 py-0.5 rounded">rg = fast grep</span>
        <span class="bg-surface0 px-2 py-0.5 rounded">fd = better find</span>
      </div>
    </div>
  );
}
