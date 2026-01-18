import { useState } from "react";

interface ClipboardItem {
  id: string;
  content: string;
  type: "text" | "image" | "code";
  time: string;
  pinned: boolean;
  preview?: string;
}

const mockItems: ClipboardItem[] = [
  {
    id: "1",
    content: 'git commit -m "feat: add container manager"',
    type: "code",
    time: "Just now",
    pinned: false,
  },
  {
    id: "2",
    content: "https://github.com/aegis-linux/aegis",
    type: "text",
    time: "2m ago",
    pinned: true,
  },
  {
    id: "3",
    content: "const App = () => {\n  return <div>Hello</div>;\n}",
    type: "code",
    time: "5m ago",
    pinned: false,
  },
  {
    id: "4",
    content: "Screenshot",
    type: "image",
    time: "12m ago",
    pinned: false,
    preview: "📸",
  },
  {
    id: "5",
    content: "export EDITOR=nvim",
    type: "code",
    time: "1h ago",
    pinned: true,
  },
  {
    id: "6",
    content: "Meeting notes from standup...",
    type: "text",
    time: "2h ago",
    pinned: false,
  },
];

export function InteractiveClipboard() {
  const [items, setItems] = useState(mockItems);
  const [filter, setFilter] = useState<"all" | "text" | "code" | "pinned">(
    "all",
  );
  const [searchQuery, setSearchQuery] = useState("");
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const togglePin = (id: string) => {
    setItems(
      items.map((item) =>
        item.id === id ? { ...item, pinned: !item.pinned } : item,
      ),
    );
  };

  const copyItem = (id: string) => {
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 1000);
  };

  const filteredItems = items.filter((item) => {
    if (filter === "pinned") return item.pinned;
    if (filter !== "all" && item.type !== filter) return false;
    if (
      searchQuery &&
      !item.content.toLowerCase().includes(searchQuery.toLowerCase())
    )
      return false;
    return true;
  });

  const pinnedCount = items.filter((i) => i.pinned).length;

  return (
    <div className="bg-mantle rounded-xl border-2 border-surface0 overflow-hidden shadow-2xl">
      {/* Title Bar */}
      <div className="bg-crust px-4 py-3 flex items-center justify-between border-b border-surface0">
        <div className="flex items-center gap-2">
          <div className="flex gap-1.5">
            <div className="w-3 h-3 rounded-full bg-red/80"></div>
            <div className="w-3 h-3 rounded-full bg-yellow/80"></div>
            <div className="w-3 h-3 rounded-full bg-green/80"></div>
          </div>
          <span className="text-sm font-bold text-text ml-2">
            Aegis Clipboard
          </span>
        </div>
        <button className="text-xs text-red hover:bg-red/20 px-2 py-1 rounded transition-colors">
          Clear
        </button>
      </div>

      {/* Search & Stats */}
      <div className="bg-base px-4 py-3 border-b border-surface0">
        <div className="flex items-center gap-3">
          <div className="flex-1 relative">
            <input
              type="text"
              placeholder="Search clipboard..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-surface0 border border-surface1 rounded-lg px-3 py-2 text-sm text-text placeholder:text-overlay0 focus:border-blue focus:outline-none"
            />
            <span className="absolute right-3 top-1/2 -translate-y-1/2 text-overlay0">
              🔍
            </span>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <span className="text-text font-bold">{items.length}</span>
            <span className="text-overlay0">Total</span>
            <span className="text-yellow">⭐</span>
            <span className="text-text font-bold">{pinnedCount}</span>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-base px-4 py-2 flex gap-2 border-b border-surface0">
        {(["all", "text", "code", "pinned"] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-3 py-1 rounded-lg text-xs font-medium transition-colors ${
              filter === f
                ? "bg-blue text-crust"
                : "bg-surface0 text-overlay0 hover:text-text"
            }`}
          >
            {f === "pinned"
              ? "⭐ Pinned"
              : f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        ))}
      </div>

      {/* Items List */}
      <div
        className="bg-base p-3 space-y-2 overflow-y-auto"
        style={{ maxHeight: "320px" }}
      >
        {filteredItems.length === 0 ? (
          <div className="text-center py-8">
            <div className="text-4xl mb-2">📋</div>
            <div className="text-subtext0">No items found</div>
          </div>
        ) : (
          filteredItems.map((item) => (
            <div
              key={item.id}
              className={`bg-mantle rounded-lg p-3 border transition-all ${
                item.pinned
                  ? "border-yellow/40 bg-yellow/5"
                  : "border-surface0 hover:border-surface1"
              } ${copiedId === item.id ? "ring-2 ring-green" : ""}`}
            >
              <div className="flex items-start gap-3">
                {/* Type Badge */}
                <span
                  className={`text-xs px-2 py-0.5 rounded ${
                    item.type === "code"
                      ? "bg-blue/20 text-blue"
                      : item.type === "image"
                        ? "bg-mauve/20 text-mauve"
                        : "bg-surface0 text-overlay0"
                  }`}
                >
                  {item.type}
                </span>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  {item.type === "image" ? (
                    <div className="bg-crust rounded p-2 text-center">
                      <span className="text-2xl">{item.preview}</span>
                      <div className="text-xs text-overlay0 mt-1">Image</div>
                    </div>
                  ) : (
                    <div
                      className={`text-sm text-subtext0 truncate ${item.type === "code" ? "font-mono" : ""}`}
                    >
                      {item.content}
                    </div>
                  )}
                  <div className="text-xs text-overlay0 mt-1">{item.time}</div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => copyItem(item.id)}
                    className={`p-1.5 rounded transition-colors ${
                      copiedId === item.id
                        ? "bg-green text-crust"
                        : "bg-blue/20 text-blue hover:bg-blue hover:text-crust"
                    }`}
                    title="Copy"
                  >
                    {copiedId === item.id ? "✓" : "📋"}
                  </button>
                  <button
                    onClick={() => togglePin(item.id)}
                    className={`p-1.5 rounded transition-colors ${
                      item.pinned
                        ? "text-yellow"
                        : "text-overlay0 hover:text-yellow"
                    }`}
                    title={item.pinned ? "Unpin" : "Pin"}
                  >
                    {item.pinned ? "⭐" : "☆"}
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Footer */}
      <div className="bg-surface0/50 px-4 py-2 text-xs text-overlay0 border-t border-surface0 flex justify-between">
        <span>Watching clipboard...</span>
        <span>Super+V to open</span>
      </div>
    </div>
  );
}
