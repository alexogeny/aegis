import { useState, useEffect } from "react";

interface QueryResult {
  id: number;
  name: string;
  email: string;
  status: "active" | "pending" | "inactive";
  created: string;
}

const mockData: QueryResult[] = [
  {
    id: 1,
    name: "Alice Johnson",
    email: "alice@example.com",
    status: "active",
    created: "2024-01-15",
  },
  {
    id: 2,
    name: "Bob Smith",
    email: "bob@example.com",
    status: "active",
    created: "2024-01-12",
  },
  {
    id: 3,
    name: "Charlie Davis",
    email: "charlie@example.com",
    status: "pending",
    created: "2024-01-10",
  },
  {
    id: 4,
    name: "Diana Wilson",
    email: "diana@example.com",
    status: "inactive",
    created: "2024-01-08",
  },
  {
    id: 5,
    name: "Eve Martinez",
    email: "eve@example.com",
    status: "active",
    created: "2024-01-05",
  },
];

const connections = [
  { name: "Production DB", type: "postgresql", icon: "🐘", status: "connected" },
  { name: "Dev MySQL", type: "mysql", icon: "🐬", status: "disconnected" },
  { name: "Local SQLite", type: "sqlite", icon: "📁", status: "disconnected" },
];

// SQL syntax highlighting colors
const highlightSQL = (sql: string) => {
  const keywords =
    /\b(SELECT|FROM|WHERE|AND|OR|ORDER|BY|LIMIT|JOIN|LEFT|RIGHT|INNER|ON|AS|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER|INDEX|TABLE|INTO|VALUES|SET|GROUP|HAVING|DISTINCT|COUNT|SUM|AVG|MAX|MIN|NULL|NOT|IN|LIKE|BETWEEN)\b/gi;
  const strings = /'[^']*'/g;
  const numbers = /\b\d+\b/g;
  const comments = /--[^\n]*/g;

  let result = sql;

  // Process in order to avoid conflicts
  const tokens: { start: number; end: number; type: string; text: string }[] =
    [];

  // Find comments
  let match;
  while ((match = comments.exec(sql)) !== null) {
    tokens.push({
      start: match.index,
      end: match.index + match[0].length,
      type: "comment",
      text: match[0],
    });
  }

  // Find strings
  while ((match = strings.exec(sql)) !== null) {
    tokens.push({
      start: match.index,
      end: match.index + match[0].length,
      type: "string",
      text: match[0],
    });
  }

  // Find keywords
  while ((match = keywords.exec(sql)) !== null) {
    tokens.push({
      start: match.index,
      end: match.index + match[0].length,
      type: "keyword",
      text: match[0],
    });
  }

  // Find numbers
  while ((match = numbers.exec(sql)) !== null) {
    tokens.push({
      start: match.index,
      end: match.index + match[0].length,
      type: "number",
      text: match[0],
    });
  }

  // Sort by position and build result
  tokens.sort((a, b) => a.start - b.start);

  // Build highlighted HTML
  let lastEnd = 0;
  const parts: string[] = [];

  for (const token of tokens) {
    // Check for overlaps
    if (token.start < lastEnd) continue;

    if (token.start > lastEnd) {
      parts.push(sql.slice(lastEnd, token.start));
    }

    const colorClass =
      token.type === "keyword"
        ? "text-mauve font-bold"
        : token.type === "string"
          ? "text-green"
          : token.type === "number"
            ? "text-peach"
            : token.type === "comment"
              ? "text-overlay0 italic"
              : "";

    parts.push(`<span class="${colorClass}">${token.text}</span>`);
    lastEnd = token.end;
  }

  if (lastEnd < sql.length) {
    parts.push(sql.slice(lastEnd));
  }

  return parts.join("");
};

export function InteractiveDbView() {
  const [query, setQuery] = useState(
    "SELECT id, name, email, status\nFROM users\nWHERE status = 'active'\nORDER BY created DESC\nLIMIT 10;",
  );
  const [results, setResults] = useState<QueryResult[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [executionTime, setExecutionTime] = useState<number | null>(null);
  const [editMode, setEditMode] = useState(false);
  const [editingCell, setEditingCell] = useState<{
    row: number;
    col: string;
  } | null>(null);
  const [pendingEdits, setPendingEdits] = useState<
    { row: number; col: string; oldVal: string; newVal: string }[]
  >([]);
  const [activeConnection, setActiveConnection] = useState(0);

  const runQuery = () => {
    setIsRunning(true);
    setExecutionTime(null);

    // Simulate query execution
    setTimeout(() => {
      const time = Math.random() * 50 + 10;
      setExecutionTime(time);
      setResults(mockData);
      setIsRunning(false);
    }, 500);
  };

  const handleCellEdit = (
    rowIdx: number,
    col: string,
    oldVal: string,
    newVal: string,
  ) => {
    if (oldVal !== newVal) {
      setPendingEdits([...pendingEdits, { row: rowIdx, col, oldVal, newVal }]);
    }
    setEditingCell(null);
  };

  const statusColor = (status: string) => {
    switch (status) {
      case "active":
        return "bg-green/20 text-green";
      case "pending":
        return "bg-yellow/20 text-yellow";
      case "inactive":
        return "bg-red/20 text-red";
      default:
        return "bg-surface0 text-overlay0";
    }
  };

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
            Aegis Database Viewer
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-overlay0">Production DB</span>
          <span className="w-2 h-2 rounded-full bg-green"></span>
        </div>
      </div>

      <div className="flex" style={{ height: "380px" }}>
        {/* Sidebar - Connections */}
        <div className="w-48 bg-mantle border-r border-surface0 flex flex-col">
          <div className="px-3 py-2 text-[10px] text-overlay0 uppercase tracking-wider border-b border-surface0">
            Connections
          </div>
          <div className="p-2 space-y-1 flex-1">
            {connections.map((conn, idx) => (
              <button
                key={idx}
                onClick={() => setActiveConnection(idx)}
                className={`w-full text-left px-2 py-2 rounded-lg text-xs transition-colors ${
                  activeConnection === idx
                    ? "bg-mauve text-crust"
                    : "hover:bg-surface0"
                }`}
              >
                <div className="flex items-center gap-2">
                  <span>{conn.icon}</span>
                  <span className="font-medium truncate">{conn.name}</span>
                  <span
                    className={`w-1.5 h-1.5 rounded-full ml-auto ${
                      conn.status === "connected" ? "bg-green" : "bg-overlay0"
                    }`}
                  ></span>
                </div>
              </button>
            ))}
          </div>
          <div className="p-2 border-t border-surface0">
            <button className="w-full text-center px-2 py-2 rounded-lg text-xs bg-surface0 hover:bg-surface1 text-text transition-colors border border-dashed border-surface1">
              + Add Connection
            </button>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 flex flex-col min-w-0">
          {/* Toolbar */}
          <div className="bg-base px-3 py-2 flex items-center gap-2 border-b border-surface0">
            <button
              onClick={runQuery}
              disabled={isRunning}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-colors ${
                isRunning
                  ? "bg-surface0 text-overlay0"
                  : "bg-green text-crust hover:bg-teal"
              }`}
            >
              {isRunning ? "⏳ Running..." : "▶ Run"}
            </button>
            <button
              onClick={() => {
                setEditMode(!editMode);
                setPendingEdits([]);
              }}
              className={`px-3 py-1.5 rounded-lg text-xs transition-colors ${
                editMode
                  ? "bg-blue text-crust"
                  : "bg-surface0 text-text hover:bg-surface1"
              }`}
            >
              ✏️ Edit Mode
            </button>
            {pendingEdits.length > 0 && (
              <button className="px-3 py-1.5 rounded-lg text-xs font-bold bg-green text-crust hover:bg-teal transition-colors">
                💾 Save ({pendingEdits.length})
              </button>
            )}
            <div className="flex-1"></div>
            {executionTime !== null && (
              <span className="text-xs text-overlay0 font-mono">
                {executionTime.toFixed(1)}ms • {results.length} rows
              </span>
            )}
            <button className="px-2 py-1 text-xs text-overlay0 hover:text-text transition-colors">
              Export
            </button>
          </div>

          {/* Query Editor with Syntax Highlighting */}
          <div className="bg-crust border-b border-surface0">
            <div className="flex">
              {/* Line numbers */}
              <div className="w-8 bg-mantle text-overlay0 text-xs font-mono py-2 text-right pr-2 select-none border-r border-surface0">
                {query.split("\n").map((_, i) => (
                  <div key={i}>{i + 1}</div>
                ))}
              </div>
              {/* Editor */}
              <div className="flex-1 relative">
                {/* Highlighted overlay */}
                <pre className="absolute inset-0 p-2 font-mono text-xs text-text pointer-events-none overflow-hidden whitespace-pre-wrap">
                  <code
                    dangerouslySetInnerHTML={{ __html: highlightSQL(query) }}
                  />
                </pre>
                {/* Actual textarea */}
                <textarea
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  className="w-full h-full p-2 font-mono text-xs bg-transparent text-transparent caret-mauve resize-none focus:outline-none"
                  style={{ minHeight: "80px" }}
                  spellCheck={false}
                />
              </div>
            </div>
            <div className="px-3 py-1 text-[10px] text-overlay0 bg-mantle/50 border-t border-surface0/50">
              Tip: Press <span className="text-mauve">Ctrl+Enter</span> to run
              query
            </div>
          </div>

          {/* Results Table with Virtual Scrolling Preview */}
          <div className="flex-1 overflow-auto bg-base">
            {results.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-overlay0">
                <span className="text-3xl mb-2">📊</span>
                <span className="text-sm">Run a query to see results</span>
              </div>
            ) : (
              <table className="w-full text-xs">
                <thead className="sticky top-0 bg-mantle">
                  <tr>
                    {["id", "name", "email", "status", "created"].map((col) => (
                      <th
                        key={col}
                        className="text-left px-3 py-2 text-text font-bold border-b-2 border-surface0"
                      >
                        {col}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {results.map((row, rowIdx) => (
                    <tr
                      key={row.id}
                      className={`border-b border-surface0/30 ${rowIdx % 2 === 1 ? "bg-surface0/10" : ""} hover:bg-surface0/30`}
                    >
                      <td className="px-3 py-2 font-mono text-overlay0">
                        {row.id}
                      </td>
                      <td
                        className={`px-3 py-2 ${editMode ? "cursor-pointer hover:bg-blue/10" : ""}`}
                        onClick={() =>
                          editMode && setEditingCell({ row: rowIdx, col: "name" })
                        }
                      >
                        {editingCell?.row === rowIdx &&
                        editingCell?.col === "name" ? (
                          <input
                            type="text"
                            defaultValue={row.name}
                            autoFocus
                            onBlur={(e) =>
                              handleCellEdit(
                                rowIdx,
                                "name",
                                row.name,
                                e.target.value,
                              )
                            }
                            onKeyDown={(e) => {
                              if (e.key === "Enter") {
                                handleCellEdit(
                                  rowIdx,
                                  "name",
                                  row.name,
                                  e.currentTarget.value,
                                );
                              }
                            }}
                            className="bg-crust border-2 border-mauve rounded px-1 py-0.5 text-text w-full focus:outline-none"
                          />
                        ) : (
                          <span className="text-text">{row.name}</span>
                        )}
                      </td>
                      <td className="px-3 py-2 font-mono text-subtext0">
                        {row.email}
                      </td>
                      <td className="px-3 py-2">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-medium ${statusColor(row.status)}`}
                        >
                          {row.status}
                        </span>
                      </td>
                      <td className="px-3 py-2 font-mono text-overlay0">
                        {row.created}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </div>

      {/* Status Bar */}
      <div className="bg-surface0/50 px-4 py-2 text-xs text-overlay0 border-t border-surface0 flex justify-between">
        <span>
          Connected to <span className="text-text">Production DB</span>
        </span>
        <span>
          {editMode ? (
            <span className="text-blue">Edit mode: double-click to modify</span>
          ) : (
            "Read-only"
          )}
        </span>
      </div>
    </div>
  );
}
