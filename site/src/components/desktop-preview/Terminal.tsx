interface TerminalProps {
  lines: TerminalLine[];
  currentInput: string;
  showCursor?: boolean;
}

interface TerminalLine {
  type: 'prompt' | 'output';
  content: string;
}

function PromptSegment({ bg, fg, children }: { bg: string; fg: string; children: string }) {
  return (
    <span
      class="inline-block px-2 py-0.5 text-xs font-semibold"
      style={{ backgroundColor: bg, color: fg }}
    >
      {children}
    </span>
  );
}

function Prompt() {
  return (
    <div class="flex items-center mb-1">
      <PromptSegment bg="#cba6f7" fg="#11111b">  aegis </PromptSegment>
      <span style={{ color: '#cba6f7', fontSize: '12px' }}></span>
      <PromptSegment bg="#fab387" fg="#11111b">  ~ </PromptSegment>
      <span style={{ color: '#fab387', fontSize: '12px' }}></span>
      <PromptSegment bg="#f9e2af" fg="#11111b">  main </PromptSegment>
      <span style={{ color: '#f9e2af', fontSize: '12px' }}></span>
      <PromptSegment bg="#94e2d5" fg="#11111b">  </PromptSegment>
      <span style={{ color: '#94e2d5', fontSize: '12px' }}></span>
      <PromptSegment bg="#89b4fa" fg="#11111b">  12:34 </PromptSegment>
      <span style={{ color: '#89b4fa', fontSize: '12px' }}> </span>
    </div>
  );
}

function NeofetchOutput() {
  return (
    <div class="text-xs leading-relaxed mt-2 flex gap-4">
      {/* ASCII Art */}
      <pre class="text-blue whitespace-pre" style={{ fontSize: '10px', lineHeight: 1.2 }}>
{`      /\\
     /  \\
    /\\   \\
   /      \\
  /   ,,   \\
 /   |  |  -\\
/_-''    ''-_\\`}
      </pre>

      {/* System Info */}
      <div class="text-xs space-y-0.5">
        <div><span class="text-mauve font-bold">aegis</span>@<span class="text-mauve font-bold">aegis</span></div>
        <div class="text-overlay0">---------------</div>
        <div><span class="text-mauve font-bold">OS</span>: Aegis Linux x86_64</div>
        <div><span class="text-mauve font-bold">Kernel</span>: 6.12.8-arch1-1</div>
        <div><span class="text-mauve font-bold">WM</span>: Hyprland</div>
        <div><span class="text-mauve font-bold">Theme</span>: Catppuccin Mocha</div>
        <div><span class="text-mauve font-bold">Terminal</span>: kitty</div>
        <div><span class="text-mauve font-bold">Shell</span>: fish 3.7.1</div>
        <div class="pt-1 flex gap-1">
          {['#f38ba8', '#fab387', '#f9e2af', '#a6e3a1', '#94e2d5', '#89b4fa', '#cba6f7', '#f5c2e7'].map((c) => (
            <span key={c} class="w-3 h-3 rounded-sm" style={{ backgroundColor: c }} />
          ))}
        </div>
      </div>
    </div>
  );
}

export function Terminal({ lines, currentInput, showCursor = true }: TerminalProps) {
  return (
    <div class="h-full bg-base p-3 font-mono text-text overflow-hidden" style={{ fontSize: '12px' }}>
      {lines.map((line, i) => (
        <div key={i}>
          {line.type === 'prompt' ? (
            <>
              <Prompt />
              <div class="text-text ml-1">{line.content}</div>
            </>
          ) : line.content === 'neofetch' ? (
            <NeofetchOutput />
          ) : (
            <div class="text-subtext1">{line.content}</div>
          )}
        </div>
      ))}

      {/* Current input line */}
      <div class="mt-2">
        <Prompt />
        <div class="ml-1 inline">
          <span class="text-text">{currentInput}</span>
          {showCursor && (
            <span class="inline-block w-0.5 h-4 bg-rosewater ml-0.5 animate-pulse" />
          )}
        </div>
      </div>
    </div>
  );
}
