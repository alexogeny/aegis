export function VSCodeWindow() {
  return (
    <div class="h-full bg-base flex flex-col">
      {/* Title bar */}
      <div class="h-8 bg-crust flex items-center px-3 gap-2 border-b border-surface0">
        <div class="flex gap-1.5">
          <div class="w-3 h-3 rounded-full bg-red/80" />
          <div class="w-3 h-3 rounded-full bg-yellow/80" />
          <div class="w-3 h-3 rounded-full bg-green/80" />
        </div>
        <span class="text-xs text-subtext0 ml-2">aegis-project - Visual Studio Code</span>
      </div>

      <div class="flex-1 flex">
        {/* Sidebar */}
        <div class="w-12 bg-mantle flex flex-col items-center py-2 gap-3 border-r border-surface0">
          <div class="text-mauve text-lg"></div>
          <div class="text-overlay0 text-lg hover:text-text"></div>
          <div class="text-overlay0 text-lg hover:text-text"></div>
          <div class="text-overlay0 text-lg hover:text-text"></div>
        </div>

        {/* Explorer */}
        <div class="w-40 bg-mantle border-r border-surface0 text-xs">
          <div class="px-3 py-2 text-overlay0 uppercase font-semibold text-[10px]">Explorer</div>
          <div class="px-2">
            <div class="text-subtext0 py-1"> AEGIS-PROJECT</div>
            <div class="ml-3 space-y-0.5">
              <div class="text-overlay1 py-0.5 hover:bg-surface0 px-1 rounded"> src</div>
              <div class="ml-3 text-text py-0.5 px-1 bg-surface0 rounded border-l-2 border-mauve"> main.rs</div>
              <div class="text-overlay1 py-0.5 hover:bg-surface0 px-1 rounded"> Cargo.toml</div>
              <div class="text-overlay1 py-0.5 hover:bg-surface0 px-1 rounded"> README.md</div>
            </div>
          </div>
        </div>

        {/* Editor */}
        <div class="flex-1 flex flex-col">
          {/* Tabs */}
          <div class="h-8 bg-mantle flex items-center border-b border-surface0">
            <div class="px-3 py-1.5 bg-base text-text text-xs flex items-center gap-2 border-r border-surface0">
              <span class="text-peach"></span>
              main.rs
              <span class="text-overlay0 hover:text-text text-[10px]"></span>
            </div>
          </div>

          {/* Code */}
          <div class="flex-1 bg-base p-2 font-mono text-xs overflow-hidden">
            <div class="flex">
              <div class="w-8 text-right pr-3 text-overlay0 select-none">1</div>
              <div>
                <span class="text-mauve">use</span>
                <span class="text-text"> std::io;</span>
              </div>
            </div>
            <div class="flex">
              <div class="w-8 text-right pr-3 text-overlay0 select-none">2</div>
              <div></div>
            </div>
            <div class="flex">
              <div class="w-8 text-right pr-3 text-overlay0 select-none">3</div>
              <div>
                <span class="text-mauve">fn</span>
                <span class="text-blue"> main</span>
                <span class="text-text">() {'{'}</span>
              </div>
            </div>
            <div class="flex">
              <div class="w-8 text-right pr-3 text-overlay0 select-none">4</div>
              <div>
                <span class="text-text">    </span>
                <span class="text-teal">println!</span>
                <span class="text-text">(</span>
                <span class="text-green">"Hello, Aegis!"</span>
                <span class="text-text">);</span>
              </div>
            </div>
            <div class="flex">
              <div class="w-8 text-right pr-3 text-overlay0 select-none">5</div>
              <div>
                <span class="text-text">{'}'}</span>
              </div>
            </div>
          </div>

          {/* Status bar */}
          <div class="h-5 bg-mauve flex items-center justify-between px-2 text-crust text-[10px]">
            <div class="flex items-center gap-2">
              <span> main</span>
              <span>0 0</span>
            </div>
            <div class="flex items-center gap-3">
              <span>Rust</span>
              <span>UTF-8</span>
              <span>LF</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
