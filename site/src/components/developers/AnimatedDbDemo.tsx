import { useState, useEffect, useRef } from "react";

// Click indicator component - shows a ripple effect at click position
// x and y are percentages of the container dimensions
function ClickIndicator({
  x,
  y,
  visible,
}: {
  x: number;
  y: number;
  visible: boolean;
}) {
  if (!visible) return null;

  return (
    <div
      className="absolute pointer-events-none z-50"
      style={{
        left: `${x}%`,
        top: `${y}%`,
        transform: "translate(-50%, -50%)",
      }}
    >
      {/* Outer ripple - expanding ring */}
      <div className="absolute w-10 h-10 -ml-5 -mt-5 rounded-full border-2 border-mauve/60 animate-ping" />
      {/* Inner glow */}
      <div className="absolute w-6 h-6 -ml-3 -mt-3 rounded-full bg-mauve/40 animate-pulse" />
      {/* Center dot */}
      <div className="absolute w-3 h-3 -ml-1.5 -mt-1.5 rounded-full bg-mauve shadow-lg shadow-mauve/50" />
    </div>
  );
}

// Schema tree data structure
interface SchemaNode {
  name: string;
  type: "schema" | "table" | "view" | "column";
  children?: SchemaNode[];
  metadata?: {
    dataType?: string;
    rowCount?: number;
    isPK?: boolean;
    isFK?: boolean;
    nullable?: boolean;
  };
}

// Mock schema data
const mockSchema: SchemaNode[] = [
  {
    name: "public",
    type: "schema",
    children: [
      {
        name: "users",
        type: "table",
        metadata: { rowCount: 42847 },
        children: [
          {
            name: "id",
            type: "column",
            metadata: { dataType: "bigint", isPK: true },
          },
          {
            name: "email",
            type: "column",
            metadata: { dataType: "varchar(255)", nullable: false },
          },
          {
            name: "name",
            type: "column",
            metadata: { dataType: "varchar(100)" },
          },
          {
            name: "created_at",
            type: "column",
            metadata: { dataType: "timestamptz" },
          },
          {
            name: "status",
            type: "column",
            metadata: { dataType: "varchar(20)" },
          },
        ],
      },
      {
        name: "orders",
        type: "table",
        metadata: { rowCount: 128453 },
        children: [
          {
            name: "id",
            type: "column",
            metadata: { dataType: "bigint", isPK: true },
          },
          {
            name: "user_id",
            type: "column",
            metadata: { dataType: "bigint", isFK: true },
          },
          {
            name: "total",
            type: "column",
            metadata: { dataType: "decimal(10,2)" },
          },
          {
            name: "status",
            type: "column",
            metadata: { dataType: "varchar(20)" },
          },
          {
            name: "created_at",
            type: "column",
            metadata: { dataType: "timestamptz" },
          },
        ],
      },
      {
        name: "products",
        type: "table",
        metadata: { rowCount: 1523 },
        children: [
          {
            name: "id",
            type: "column",
            metadata: { dataType: "bigint", isPK: true },
          },
          {
            name: "name",
            type: "column",
            metadata: { dataType: "varchar(200)" },
          },
          {
            name: "price",
            type: "column",
            metadata: { dataType: "decimal(10,2)" },
          },
          {
            name: "category_id",
            type: "column",
            metadata: { dataType: "integer", isFK: true },
          },
        ],
      },
      {
        name: "active_users",
        type: "view",
        children: [
          { name: "id", type: "column", metadata: { dataType: "bigint" } },
          {
            name: "email",
            type: "column",
            metadata: { dataType: "varchar(255)" },
          },
          {
            name: "name",
            type: "column",
            metadata: { dataType: "varchar(100)" },
          },
        ],
      },
    ],
  },
];

// Animation sequence for the demo
interface AnimationStep {
  action:
    | "expand"
    | "select"
    | "type"
    | "run"
    | "showResults"
    | "selectTable"
    | "click"
    | "expandRow"
    | "wait";
  target?: string;
  delay: number;
  // Click position as percentage of container (for click action)
  clickX?: number;
  clickY?: number;
}

// Click positions are percentages of container dimensions
// Layout at typical width (~900px) and height (~496px):
// - Title bar: 0-9% height (~44px)
// - Left panel (w-56=224px): 0-25% width
// - Middle panel (w-52=208px): 25-48% width
// - Right panel (flex-1): 48-100% width
// - Status bar: 93-100% height (~32px)
//
// Left panel internal layout:
// - Header "Schema Browser": 9-13% height
// - Search input: 13-17% height
// - Tree starts: ~18% height, each item ~5% height
const animationSequence: AnimationStep[] = [
  { action: "wait", delay: 500 },
  // Click on public schema to expand (left panel, first tree item at ~20%)
  { action: "click", clickX: 10, clickY: 20, delay: 400 },
  { action: "expand", target: "public", delay: 300 },
  { action: "wait", delay: 200 },
  // Click on users table (indented, second item at ~25%)
  { action: "click", clickX: 12, clickY: 25, delay: 400 },
  { action: "selectTable", target: "users", delay: 400 },
  { action: "wait", delay: 600 },
  // Click to expand users (click the arrow area at left edge)
  { action: "click", clickX: 5, clickY: 25, delay: 400 },
  { action: "expand", target: "users", delay: 300 },
  { action: "wait", delay: 400 },
  // Click on email column (indented more, ~35% down)
  { action: "click", clickX: 14, clickY: 35, delay: 400 },
  { action: "select", target: "users/email", delay: 300 },
  { action: "wait", delay: 800 },
  { action: "type", delay: 50 }, // Type query character by character
  { action: "wait", delay: 300 },
  // Click Run button (right panel starts at 48%, button in toolbar ~12% height)
  { action: "click", clickX: 52, clickY: 12, delay: 400 },
  { action: "run", delay: 500 },
  { action: "showResults", delay: 100 },
  { action: "wait", delay: 1500 },
  // Click on third result row (Carol White) - right panel ~65%, third data row ~60% height
  // Results area starts at ~40% height, header row ~45%, each data row is ~5% tall
  // Row 0 (Alice): ~50%, Row 1 (Bob): ~55%, Row 2 (Carol): ~60%
  { action: "click", clickX: 65, clickY: 60, delay: 400 },
  { action: "expandRow", target: "2", delay: 100 },
  { action: "wait", delay: 3000 },
];

const targetQuery = `SELECT id, name, email, status
FROM users
WHERE status = 'active'
ORDER BY created_at DESC
LIMIT 10;`;

const mockResults = [
  {
    id: 1,
    name: "Alice Johnson",
    email: "alice@example.com",
    status: "active",
  },
  { id: 2, name: "Bob Smith", email: "bob@example.com", status: "active" },
  { id: 3, name: "Carol White", email: "carol@example.com", status: "active" },
  { id: 4, name: "David Brown", email: "david@example.com", status: "active" },
  { id: 5, name: "Eve Davis", email: "eve@example.com", status: "active" },
];

// SQL syntax highlighting
const highlightSQL = (sql: string) => {
  const keywords =
    /\b(SELECT|FROM|WHERE|AND|OR|ORDER|BY|LIMIT|JOIN|LEFT|RIGHT|INNER|ON|AS|DESC|ASC)\b/gi;
  const strings = /'[^']*'/g;
  const numbers = /\b\d+\b/g;

  const tokens: { start: number; end: number; type: string; text: string }[] =
    [];

  let match;
  const keywordsRegex = new RegExp(keywords.source, "gi");
  while ((match = keywordsRegex.exec(sql)) !== null) {
    tokens.push({
      start: match.index,
      end: match.index + match[0].length,
      type: "keyword",
      text: match[0],
    });
  }

  const stringsRegex = new RegExp(strings.source, "g");
  while ((match = stringsRegex.exec(sql)) !== null) {
    tokens.push({
      start: match.index,
      end: match.index + match[0].length,
      type: "string",
      text: match[0],
    });
  }

  const numbersRegex = new RegExp(numbers.source, "g");
  while ((match = numbersRegex.exec(sql)) !== null) {
    tokens.push({
      start: match.index,
      end: match.index + match[0].length,
      type: "number",
      text: match[0],
    });
  }

  tokens.sort((a, b) => a.start - b.start);

  let lastEnd = 0;
  const parts: string[] = [];

  for (const token of tokens) {
    if (token.start < lastEnd) continue;
    if (token.start > lastEnd) {
      parts.push(
        `<span class="text-text">${sql.slice(lastEnd, token.start)}</span>`,
      );
    }

    const colorClass =
      token.type === "keyword"
        ? "text-mauve font-bold"
        : token.type === "string"
          ? "text-green"
          : token.type === "number"
            ? "text-peach"
            : "text-text";

    parts.push(`<span class="${colorClass}">${token.text}</span>`);
    lastEnd = token.end;
  }

  if (lastEnd < sql.length) {
    parts.push(`<span class="text-text">${sql.slice(lastEnd)}</span>`);
  }

  return parts.join("");
};

function TreeNode({
  node,
  level,
  expandedNodes,
  selectedNode,
  onToggle,
  onSelect,
}: {
  node: SchemaNode;
  level: number;
  expandedNodes: Set<string>;
  selectedNode: string | null;
  onToggle: (name: string) => void;
  onSelect: (name: string) => void;
}) {
  const isExpanded = expandedNodes.has(node.name);
  const isSelected =
    selectedNode === node.name || selectedNode?.startsWith(node.name + "/");
  const hasChildren = node.children && node.children.length > 0;

  const getIcon = () => {
    switch (node.type) {
      case "schema":
        return "📁";
      case "table":
        return "🗃️";
      case "view":
        return "👁️";
      case "column":
        return node.metadata?.isPK ? "🔑" : node.metadata?.isFK ? "🔗" : "📊";
    }
  };

  return (
    <div>
      <div
        className={`flex items-center gap-1.5 px-2 py-1 rounded cursor-pointer text-xs transition-all duration-200 ${
          isSelected
            ? "bg-mauve/20 text-text"
            : "hover:bg-surface0/50 text-subtext0"
        }`}
        style={{ paddingLeft: `${level * 12 + 8}px` }}
        onClick={() => {
          if (hasChildren) onToggle(node.name);
          onSelect(node.name);
        }}
      >
        {hasChildren ? (
          <span
            className={`text-[10px] text-overlay0 transition-transform duration-200 ${isExpanded ? "rotate-90" : ""}`}
          >
            ▶
          </span>
        ) : (
          <span className="w-2.5"></span>
        )}
        <span>{getIcon()}</span>
        <span className="font-medium">{node.name}</span>
        {node.metadata?.rowCount !== undefined && (
          <span className="text-[10px] text-overlay0 ml-auto font-mono">
            {node.metadata.rowCount.toLocaleString()}
          </span>
        )}
        {node.metadata?.dataType && (
          <span className="text-[10px] text-yellow ml-auto font-mono">
            {node.metadata.dataType}
          </span>
        )}
      </div>
      {hasChildren && isExpanded && (
        <div className="animate-fadeIn">
          {node.children!.map((child, idx) => (
            <TreeNode
              key={idx}
              node={child}
              level={level + 1}
              expandedNodes={expandedNodes}
              selectedNode={selectedNode}
              onToggle={onToggle}
              onSelect={onSelect}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export function AnimatedDbDemo() {
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [selectedTable, setSelectedTable] = useState<SchemaNode | null>(null);
  const [query, setQuery] = useState("");
  const [isRunning, setIsRunning] = useState(false);
  const [results, setResults] = useState<typeof mockResults>([]);
  const [executionTime, setExecutionTime] = useState<number | null>(null);
  const [animationStep, setAnimationStep] = useState(0);
  const [isAnimating, setIsAnimating] = useState(true);
  const [clickIndicator, setClickIndicator] = useState<{
    x: number;
    y: number;
    visible: boolean;
  }>({ x: 0, y: 0, visible: false });
  const [expandedRowIndex, setExpandedRowIndex] = useState<number | null>(null);
  const animationRef = useRef<NodeJS.Timeout | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);

  // Run animation sequence
  useEffect(() => {
    if (!isAnimating) return;

    const runAnimation = async () => {
      for (let i = 0; i < animationSequence.length; i++) {
        if (!isAnimating) break;

        const step = animationSequence[i];
        setAnimationStep(i);

        await new Promise((resolve) => setTimeout(resolve, step.delay));

        switch (step.action) {
          case "click":
            // Show click indicator at the specified position
            if (step.clickX !== undefined && step.clickY !== undefined) {
              setClickIndicator({
                x: step.clickX,
                y: step.clickY,
                visible: true,
              });
              // Hide after animation completes
              setTimeout(() => {
                setClickIndicator(
                  (prev: { x: number; y: number; visible: boolean }) => ({
                    ...prev,
                    visible: false,
                  }),
                );
              }, 600);
            }
            break;

          case "expand":
            setExpandedNodes((prev) => new Set([...prev, step.target!]));
            break;

          case "selectTable":
            const table = mockSchema[0].children?.find(
              (t) => t.name === step.target,
            );
            if (table) {
              setSelectedTable(table);
              setSelectedNode(step.target!);
            }
            break;

          case "select":
            setSelectedNode(step.target!);
            break;

          case "type":
            // Type query character by character
            for (let j = 0; j <= targetQuery.length; j++) {
              if (!isAnimating) break;
              setQuery(targetQuery.slice(0, j));
              await new Promise((resolve) => setTimeout(resolve, step.delay));
            }
            break;

          case "run":
            setIsRunning(true);
            break;

          case "showResults":
            setIsRunning(false);
            setExecutionTime(23.4);
            setResults(mockResults);
            break;

          case "expandRow":
            if (step.target !== undefined) {
              setExpandedRowIndex(parseInt(step.target, 10));
            }
            break;

          case "wait":
            break;
        }
      }

      // Reset and loop
      if (isAnimating) {
        await new Promise((resolve) => setTimeout(resolve, 2000));
        setExpandedNodes(new Set());
        setSelectedNode(null);
        setSelectedTable(null);
        setQuery("");
        setResults([]);
        setExecutionTime(null);
        setIsRunning(false);
        setClickIndicator({ x: 0, y: 0, visible: false });
        setExpandedRowIndex(null);
        runAnimation();
      }
    };

    runAnimation();

    return () => {
      setIsAnimating(false);
    };
  }, []);

  const handleToggle = (name: string) => {
    setIsAnimating(false);
    setExpandedNodes((prev) => {
      const next = new Set(prev);
      if (next.has(name)) {
        next.delete(name);
      } else {
        next.add(name);
      }
      return next;
    });
  };

  const handleSelect = (name: string) => {
    setIsAnimating(false);
    setSelectedNode(name);
    // Find the table if selecting a table node
    const table = mockSchema[0].children?.find((t) => t.name === name);
    if (table && (table.type === "table" || table.type === "view")) {
      setSelectedTable(table);
    }
  };

  return (
    <div
      ref={containerRef}
      className="bg-mantle rounded-xl border-2 border-surface0 overflow-hidden shadow-2xl relative"
    >
      {/* Click Indicator */}
      <ClickIndicator
        x={clickIndicator.x}
        y={clickIndicator.y}
        visible={clickIndicator.visible}
      />

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
          <span className="w-2 h-2 rounded-full bg-green animate-pulse"></span>
          <span className="text-xs text-green font-medium">Connected</span>
        </div>
      </div>

      <div className="flex" style={{ height: "420px" }}>
        {/* Left Panel: Schema Tree */}
        <div className="w-56 bg-mantle border-r border-surface0 flex flex-col">
          <div className="px-3 py-2 text-[10px] text-overlay0 uppercase tracking-wider border-b border-surface0 flex items-center justify-between">
            <span>Schema Browser</span>
            <span className="text-mauve">▼ public</span>
          </div>
          {/* Search */}
          <div className="px-2 py-2 border-b border-surface0">
            <input
              type="text"
              placeholder="Filter tables..."
              className="w-full px-2 py-1.5 text-xs bg-surface0/50 border border-surface1 rounded-lg text-text placeholder-overlay0 focus:outline-none focus:border-mauve"
            />
          </div>
          {/* Tree */}
          <div className="flex-1 overflow-auto p-1">
            {mockSchema.map((schema, idx) => (
              <TreeNode
                key={idx}
                node={schema}
                level={0}
                expandedNodes={expandedNodes}
                selectedNode={selectedNode}
                onToggle={handleToggle}
                onSelect={handleSelect}
              />
            ))}
          </div>
        </div>

        {/* Middle Panel: Entity View */}
        <div className="w-52 bg-base border-r border-surface0 flex flex-col">
          <div className="px-3 py-2 text-[10px] text-overlay0 uppercase tracking-wider border-b border-surface0">
            Entity Details
          </div>
          {selectedTable ? (
            <div className="flex-1 overflow-auto p-3">
              {/* Header */}
              <div className="flex items-center gap-2 mb-3">
                <span className="text-xl">
                  {selectedTable.type === "view" ? "👁️" : "🗃️"}
                </span>
                <div>
                  <div className="text-sm font-bold text-text">
                    {selectedTable.name}
                  </div>
                  <div className="text-[10px] text-overlay0 uppercase">
                    {selectedTable.type}
                  </div>
                </div>
              </div>

              {/* Quick Actions */}
              <div className="flex gap-2 mb-3">
                <button
                  className="flex-1 px-2 py-1.5 bg-mauve text-crust text-xs font-medium rounded-lg hover:bg-pink transition-colors"
                  onClick={() => {
                    setIsAnimating(false);
                    setQuery(`SELECT * FROM ${selectedTable.name} LIMIT 100;`);
                  }}
                >
                  SELECT *
                </button>
                <button className="flex-1 px-2 py-1.5 bg-surface0 text-text text-xs rounded-lg hover:bg-surface1 transition-colors">
                  COUNT
                </button>
              </div>

              {/* Columns */}
              <div className="text-[10px] text-overlay0 uppercase tracking-wider mb-2">
                Columns ({selectedTable.children?.length || 0})
              </div>
              <div className="space-y-1">
                {selectedTable.children?.map((col, idx) => (
                  <div
                    key={idx}
                    className="flex items-center gap-2 px-2 py-1.5 bg-surface0/30 rounded text-xs"
                  >
                    <span>
                      {col.metadata?.isPK
                        ? "🔑"
                        : col.metadata?.isFK
                          ? "🔗"
                          : "📊"}
                    </span>
                    <span className="text-text flex-1">{col.name}</span>
                    <span className="text-yellow font-mono text-[10px]">
                      {col.metadata?.dataType}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="flex-1 flex items-center justify-center text-overlay0 text-xs">
              Select a table to view details
            </div>
          )}
        </div>

        {/* Right Panel: Query & Results */}
        <div className="flex-1 flex flex-col min-w-0">
          {/* Toolbar */}
          <div className="bg-base/50 px-3 py-2 flex items-center gap-2 border-b border-surface0">
            <button
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-colors ${
                isRunning
                  ? "bg-surface0 text-overlay0"
                  : "bg-green text-crust hover:bg-teal"
              }`}
              onClick={() => {
                setIsAnimating(false);
                setIsRunning(true);
                setTimeout(() => {
                  setIsRunning(false);
                  setExecutionTime(Math.random() * 50 + 10);
                  setResults(mockResults);
                }, 500);
              }}
            >
              {isRunning ? "⏳ Running..." : "▶ Run"}
            </button>
            <div className="flex-1"></div>
            {executionTime !== null && (
              <span className="text-xs text-overlay0 font-mono">
                {executionTime.toFixed(1)}ms • {results.length} rows
              </span>
            )}
          </div>

          {/* Query Editor */}
          <div className="bg-crust border-b border-surface0">
            <div className="flex">
              <div className="w-6 bg-mantle text-overlay0 text-[10px] font-mono py-2 text-right pr-1 select-none border-r border-surface0">
                {query.split("\n").map((_, i) => (
                  <div key={i}>{i + 1}</div>
                ))}
              </div>
              <div className="flex-1 p-2">
                <pre className="font-mono text-xs text-text whitespace-pre-wrap min-h-[70px]">
                  <code
                    dangerouslySetInnerHTML={{ __html: highlightSQL(query) }}
                  />
                  {isAnimating && (
                    <span className="animate-pulse text-mauve">|</span>
                  )}
                </pre>
              </div>
            </div>
          </div>

          {/* Results Table */}
          <div className="flex-1 overflow-auto bg-base">
            {results.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-overlay0">
                <span className="text-2xl mb-2">📊</span>
                <span className="text-xs">Run a query to see results</span>
              </div>
            ) : (
              <table className="w-full text-xs">
                <thead className="sticky top-0 bg-mantle">
                  <tr>
                    {["id", "name", "email", "status"].map((col) => (
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
                  {results.map(
                    (row: (typeof mockResults)[number], idx: number) => (
                      <tr
                        key={row.id}
                        className={`border-b border-surface0/30 animate-fadeIn cursor-pointer transition-colors ${
                          expandedRowIndex === idx
                            ? "bg-mauve/20 border-l-2 border-l-mauve"
                            : idx % 2 === 1
                              ? "bg-surface0/10 hover:bg-surface0/30"
                              : "hover:bg-surface0/30"
                        }`}
                        style={{ animationDelay: `${idx * 50}ms` }}
                        onClick={() => {
                          setIsAnimating(false);
                          setExpandedRowIndex(
                            expandedRowIndex === idx ? null : idx,
                          );
                        }}
                      >
                        <td className="px-3 py-2 font-mono text-overlay0">
                          {row.id}
                        </td>
                        <td className="px-3 py-2 text-text">{row.name}</td>
                        <td className="px-3 py-2 font-mono text-subtext0">
                          {row.email}
                        </td>
                        <td className="px-3 py-2">
                          <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-green/20 text-green">
                            {row.status}
                          </span>
                        </td>
                      </tr>
                    ),
                  )}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </div>

      {/* Row Detail Window (floating overlay) */}
      {expandedRowIndex !== null && results[expandedRowIndex] && (
        <div className="absolute inset-0 flex items-center justify-center bg-crust/60 backdrop-blur-sm z-40 animate-fadeIn">
          <div className="w-[340px] bg-mantle rounded-xl border-2 border-surface0 shadow-2xl overflow-hidden animate-scale-in">
            {/* Window Title Bar */}
            <div className="bg-crust px-3 py-2 flex items-center justify-between border-b border-surface0">
              <div className="flex items-center gap-2">
                <div className="flex gap-1.5">
                  <div className="w-2.5 h-2.5 rounded-full bg-red/80"></div>
                  <div className="w-2.5 h-2.5 rounded-full bg-yellow/80"></div>
                  <div className="w-2.5 h-2.5 rounded-full bg-green/80"></div>
                </div>
                <span className="text-xs font-bold text-text ml-2">
                  Row Details
                </span>
              </div>
              <button
                className="text-xs text-overlay0 hover:text-text transition-colors"
                onClick={() => setExpandedRowIndex(null)}
              >
                ✕
              </button>
            </div>

            {/* Window Header with Navigation */}
            <div className="px-3 py-2 border-b border-surface0 flex items-center justify-between bg-base/50">
              <div className="flex items-center gap-2">
                <button className="px-2 py-1 text-xs bg-surface0 text-overlay0 rounded hover:text-text transition-colors">
                  ◀ Prev
                </button>
                <span className="text-[10px] text-overlay0 font-mono">
                  Row {expandedRowIndex + 1} of {results.length}
                </span>
                <button className="px-2 py-1 text-xs bg-surface0 text-overlay0 rounded hover:text-text transition-colors">
                  Next ▶
                </button>
              </div>
              {/* View mode toggle */}
              <div className="flex items-center gap-1">
                <button className="px-2 py-1 text-[10px] bg-mauve text-crust rounded font-medium">
                  Fields
                </button>
                <button className="px-2 py-1 text-[10px] bg-surface0 text-overlay0 rounded hover:text-text transition-colors">
                  JSON
                </button>
              </div>
            </div>

            {/* Fields View */}
            <div className="p-3 space-y-2 max-h-[200px] overflow-auto">
              {Object.entries(results[expandedRowIndex]).map(([key, value]) => (
                <div
                  key={key}
                  className="bg-surface0/30 rounded-lg p-2.5 border border-surface0"
                >
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-[10px]">
                      {key === "id"
                        ? "🔑"
                        : key === "email"
                          ? "📧"
                          : key === "status"
                            ? "🏷️"
                            : "📊"}
                    </span>
                    <span className="text-[10px] text-overlay0 uppercase tracking-wide font-medium">
                      {key}
                    </span>
                    <span className="text-[10px] text-yellow font-mono ml-auto">
                      {typeof value === "number" ? "integer" : typeof value}
                    </span>
                  </div>
                  <div className="text-xs text-text font-mono pl-5">
                    {key === "status" ? (
                      <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-green/20 text-green">
                        {String(value)}
                      </span>
                    ) : (
                      String(value)
                    )}
                  </div>
                </div>
              ))}
            </div>

            {/* JSON Preview Panel */}
            <div className="px-3 py-2 border-t border-surface0 bg-crust/50">
              <div className="flex items-center justify-between mb-1">
                <span className="text-[10px] text-overlay0 uppercase">
                  JSON Preview
                </span>
                <button className="text-[10px] text-mauve hover:text-pink transition-colors">
                  📋 Copy
                </button>
              </div>
              <pre className="text-[10px] text-subtext0 font-mono whitespace-pre-wrap bg-crust rounded p-2 max-h-[60px] overflow-auto">
                {JSON.stringify(results[expandedRowIndex], null, 2)}
              </pre>
            </div>
          </div>
        </div>
      )}

      {/* Status Bar */}
      <div className="bg-surface0/50 px-4 py-2 text-xs text-overlay0 border-t border-surface0 flex justify-between items-center">
        <span>
          Connected to <span className="text-text">Production DB</span> •{" "}
          <span className="text-mauve">PostgreSQL 16</span>
        </span>
        {isAnimating && (
          <span className="flex items-center gap-1.5 text-mauve">
            <span className="w-1.5 h-1.5 rounded-full bg-mauve animate-pulse"></span>
            Demo playing
          </span>
        )}
      </div>
    </div>
  );
}
