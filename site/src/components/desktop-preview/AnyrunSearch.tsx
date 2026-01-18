interface AnyrunSearchProps {
  visible: boolean;
  query: string;
  selectedIndex: number;
}

const results = [
  {
    icon: "",
    name: "Visual Studio Code",
    description: "Code editing. Redefined.",
  },
  { icon: "", name: "Codium", description: "Free/Libre VSCode" },
  { icon: "", name: "Code - OSS", description: "Open Source build of VSCode" },
];

export function AnyrunSearch({
  visible,
  query,
  selectedIndex,
}: AnyrunSearchProps) {
  const filteredResults = query
    ? results.filter((r) => r.name.toLowerCase().includes(query.toLowerCase()))
    : [];

  if (!visible) return null;

  return (
    <>
      {/* Backdrop */}
      <div class="absolute inset-0 bg-black/50 z-30 animate-fade-in" />

      {/* Search Container */}
      <div class="absolute left-1/2 top-[20%] -translate-x-1/2 w-[400px] bg-base/90 backdrop-blur-md border-2 border-surface1 rounded-2xl shadow-2xl z-40 overflow-hidden animate-slide-up">
        {/* Search Input */}
        <div class="p-4">
          <div class="bg-surface0 rounded-xl px-4 py-3 flex items-center gap-3">
            <span class="text-overlay0"></span>
            <span class="text-text font-mono text-lg flex-1">
              {query}
              <span class="inline-block w-0.5 h-5 bg-mauve ml-0.5 animate-pulse" />
            </span>
          </div>
        </div>

        {/* Results */}
        {filteredResults.length > 0 && (
          <div class="px-2 pb-3 space-y-1">
            {filteredResults.map((result, i) => (
              <div
                key={result.name}
                class={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                  i === selectedIndex
                    ? "bg-surface1 border-l-[3px] border-mauve"
                    : "hover:bg-surface0"
                }`}
              >
                <span class="text-xl w-6 text-center">{result.icon}</span>
                <div>
                  <div
                    class={`font-medium ${i === selectedIndex ? "text-mauve" : "text-text"}`}
                  >
                    {result.name}
                  </div>
                  <div class="text-xs text-overlay0">{result.description}</div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </>
  );
}
