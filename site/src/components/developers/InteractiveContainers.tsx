import { useState } from "react";

interface Container {
  id: string;
  name: string;
  image: string;
  status: "running" | "stopped" | "paused";
  cpu: number;
  memory: string;
  icon: string;
}

const mockContainers: Container[] = [
  {
    id: "a1b2c3",
    name: "postgres-db",
    image: "postgres:15",
    status: "running",
    cpu: 2.3,
    memory: "256MB",
    icon: "🐘",
  },
  {
    id: "d4e5f6",
    name: "redis-cache",
    image: "redis:7-alpine",
    status: "running",
    cpu: 0.5,
    memory: "64MB",
    icon: "🔴",
  },
  {
    id: "g7h8i9",
    name: "nginx-proxy",
    image: "nginx:latest",
    status: "running",
    cpu: 0.8,
    memory: "32MB",
    icon: "🌐",
  },
  {
    id: "j0k1l2",
    name: "node-api",
    image: "node:20-slim",
    status: "stopped",
    cpu: 0,
    memory: "0MB",
    icon: "📗",
  },
];

const mockImages = [
  { repo: "postgres", tag: "15", size: "412MB" },
  { repo: "redis", tag: "7-alpine", size: "32MB" },
  { repo: "nginx", tag: "latest", size: "187MB" },
  { repo: "node", tag: "20-slim", size: "245MB" },
];

export function InteractiveContainers() {
  const [containers, setContainers] = useState(mockContainers);
  const [activeTab, setActiveTab] = useState<"containers" | "images">(
    "containers",
  );
  const [selectedContainer, setSelectedContainer] = useState<string | null>(
    null,
  );

  const toggleContainer = (id: string) => {
    setContainers(
      containers.map((c) => {
        if (c.id === id) {
          return {
            ...c,
            status: c.status === "running" ? "stopped" : "running",
            cpu: c.status === "running" ? 0 : Math.random() * 5,
            memory:
              c.status === "running"
                ? "0MB"
                : `${Math.floor(Math.random() * 200 + 32)}MB`,
          };
        }
        return c;
      }),
    );
  };

  const runningCount = containers.filter((c) => c.status === "running").length;
  const stoppedCount = containers.filter((c) => c.status !== "running").length;

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
            Aegis Containers
          </span>
        </div>
        <span className="text-xs text-overlay0">Podman</span>
      </div>

      {/* Stats Header */}
      <div className="bg-base px-4 py-3 flex items-center gap-4 border-b border-surface0">
        <div className="flex items-center gap-2 bg-green/20 text-green px-3 py-1 rounded-lg">
          <span className="text-lg font-bold">{runningCount}</span>
          <span className="text-xs">Running</span>
        </div>
        <div className="flex items-center gap-2 bg-surface0 text-overlay0 px-3 py-1 rounded-lg">
          <span className="text-lg font-bold">{stoppedCount}</span>
          <span className="text-xs">Stopped</span>
        </div>
        <div className="flex items-center gap-2 bg-surface0 text-overlay0 px-3 py-1 rounded-lg">
          <span className="text-lg font-bold">{mockImages.length}</span>
          <span className="text-xs">Images</span>
        </div>
      </div>

      {/* Tab Switcher */}
      <div className="bg-base px-4 py-2 flex gap-2 border-b border-surface0">
        <button
          onClick={() => setActiveTab("containers")}
          className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-colors ${
            activeTab === "containers"
              ? "bg-blue text-crust"
              : "text-overlay0 hover:text-text hover:bg-surface0"
          }`}
        >
          Containers
        </button>
        <button
          onClick={() => setActiveTab("images")}
          className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-colors ${
            activeTab === "images"
              ? "bg-blue text-crust"
              : "text-overlay0 hover:text-text hover:bg-surface0"
          }`}
        >
          Images
        </button>
      </div>

      {/* Content */}
      <div className="bg-base p-4 space-y-3" style={{ minHeight: "280px" }}>
        {activeTab === "containers"
          ? containers.map((container) => (
              <div
                key={container.id}
                className={`bg-mantle rounded-lg p-3 border transition-all cursor-pointer ${
                  selectedContainer === container.id
                    ? "border-blue"
                    : "border-surface0 hover:border-surface1"
                }`}
                onClick={() =>
                  setSelectedContainer(
                    selectedContainer === container.id ? null : container.id,
                  )
                }
              >
                <div className="flex items-center gap-3">
                  {/* Icon */}
                  <span className="text-2xl">{container.icon}</span>

                  {/* Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-text truncate">
                        {container.name}
                      </span>
                      <span
                        className={`text-[10px] px-2 py-0.5 rounded ${
                          container.status === "running"
                            ? "bg-green/20 text-green"
                            : "bg-surface0 text-overlay0"
                        }`}
                      >
                        {container.status}
                      </span>
                    </div>
                    <div className="text-xs text-overlay0 font-mono truncate">
                      {container.image}
                    </div>
                  </div>

                  {/* Stats (if running) */}
                  {container.status === "running" && (
                    <div className="flex gap-4 text-xs">
                      <div className="text-center">
                        <div className="text-text font-mono">
                          {container.cpu.toFixed(1)}%
                        </div>
                        <div className="text-overlay0">CPU</div>
                      </div>
                      <div className="text-center">
                        <div className="text-text font-mono">
                          {container.memory}
                        </div>
                        <div className="text-overlay0">MEM</div>
                      </div>
                    </div>
                  )}

                  {/* Action Button */}
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      toggleContainer(container.id);
                    }}
                    className={`px-3 py-1.5 rounded text-xs font-medium transition-colors ${
                      container.status === "running"
                        ? "bg-red/20 text-red hover:bg-red hover:text-crust"
                        : "bg-green/20 text-green hover:bg-green hover:text-crust"
                    }`}
                  >
                    {container.status === "running" ? "Stop" : "Start"}
                  </button>
                </div>

                {/* Expanded Details */}
                {selectedContainer === container.id && (
                  <div className="mt-3 pt-3 border-t border-surface0 flex gap-2">
                    <button className="flex-1 bg-surface0 text-overlay0 hover:text-text px-2 py-1.5 rounded text-xs transition-colors">
                      📋 Logs
                    </button>
                    <button className="flex-1 bg-surface0 text-overlay0 hover:text-text px-2 py-1.5 rounded text-xs transition-colors">
                      🔄 Restart
                    </button>
                    <button className="flex-1 bg-surface0 text-overlay0 hover:text-red px-2 py-1.5 rounded text-xs transition-colors">
                      🗑️ Remove
                    </button>
                  </div>
                )}
              </div>
            ))
          : mockImages.map((image, i) => (
              <div
                key={i}
                className="bg-mantle rounded-lg p-3 border border-surface0 hover:border-surface1 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <span className="text-xl">🖼️</span>
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-text font-mono">
                        {image.repo}
                      </span>
                      <span className="text-xs bg-blue/20 text-blue px-2 py-0.5 rounded">
                        {image.tag}
                      </span>
                    </div>
                  </div>
                  <span className="text-xs text-overlay0">{image.size}</span>
                  <button className="text-overlay0 hover:text-red transition-colors">
                    🗑️
                  </button>
                </div>
              </div>
            ))}
      </div>
    </div>
  );
}
