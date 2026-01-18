import { useState, useEffect, useRef } from 'preact/hooks';

type Page = 'snapshots' | 'schedule' | 'settings';
type SnapshotType = 'manual' | 'scheduled' | 'boot';

interface Snapshot {
  id: string;
  name: string;
  date: string;
  type: SnapshotType;
  size: string;
}

const SNAPSHOTS: Snapshot[] = [
  { id: '1', name: 'Before system update', date: '2024-01-15 10:30', type: 'manual', size: '1.2 GB' },
  { id: '2', name: 'Boot snapshot', date: '2024-01-14 08:00', type: 'boot', size: '856 MB' },
  { id: '3', name: 'Daily backup', date: '2024-01-13 03:00', type: 'scheduled', size: '1.1 GB' },
];

export function BackupAppMockup() {
  const [currentPage, setCurrentPage] = useState<Page>('snapshots');
  const [animateIn, setAnimateIn] = useState(false);
  const [creating, setCreating] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setAnimateIn(true);
  }, []);

  const handleCreate = () => {
    setCreating(true);
    setTimeout(() => setCreating(false), 2000);
  };

  const sidebarItems: { id: Page; icon: string; label: string }[] = [
    { id: 'snapshots', icon: '💾', label: 'Snapshots' },
    { id: 'schedule', icon: '📅', label: 'Schedule' },
    { id: 'settings', icon: '⚙️', label: 'Settings' },
  ];

  return (
    <div
      ref={containerRef}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      class={`relative bg-base rounded-2xl border-2 overflow-hidden shadow-2xl transition-all duration-300 ${animateIn ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'} ${isHovered ? 'shadow-peach/30 border-peach/50' : 'border-surface0'}`}
    >
      {/* GTK Header Bar */}
      <div class="bg-crust px-4 py-2.5 flex items-center justify-between border-b border-surface0">
        <div class="flex items-center gap-3">
          <div class="flex gap-1.5">
            <div class="w-3 h-3 rounded-full bg-red/80 hover:bg-red transition-colors cursor-pointer"></div>
            <div class="w-3 h-3 rounded-full bg-yellow/80 hover:bg-yellow transition-colors cursor-pointer"></div>
            <div class="w-3 h-3 rounded-full bg-green/80 hover:bg-green transition-colors cursor-pointer"></div>
          </div>
          <span class="text-sm font-bold text-peach ml-2">Aegis Backup</span>
        </div>
        <button
          onClick={handleCreate}
          disabled={creating}
          class={`text-xs font-semibold px-3 py-1.5 rounded-lg transition-colors ${
            creating
              ? 'bg-surface1 text-overlay0 cursor-wait'
              : 'bg-green text-crust hover:bg-teal'
          }`}
        >
          {creating ? 'Creating...' : 'Create Snapshot'}
        </button>
      </div>

      <div class="flex" style={{ height: '320px' }}>
        {/* Sidebar */}
        <div class="w-36 bg-mantle border-r border-surface0 p-2 shrink-0">
          {sidebarItems.map((item) => (
            <button
              key={item.id}
              onClick={() => setCurrentPage(item.id)}
              class={`w-full flex items-center gap-2 px-3 py-2 rounded-lg mb-1 transition-all duration-200 ${
                currentPage === item.id
                  ? 'bg-mauve text-crust font-semibold'
                  : 'text-subtext0 hover:bg-surface0 hover:text-text'
              }`}
            >
              <span class="text-base">{item.icon}</span>
              <span class="text-xs">{item.label}</span>
            </button>
          ))}
        </div>

        {/* Main Content */}
        <div class="flex-1 overflow-y-auto p-4">
          {currentPage === 'snapshots' && (
            <div class="animate-fadeIn">
              {/* Status card */}
              <div class="bg-mantle rounded-xl border border-surface0 p-4 mb-4 flex items-center gap-4">
                <span class="text-3xl text-green">✓</span>
                <div class="flex-1">
                  <div class="text-sm font-bold text-text">System Protected</div>
                  <div class="text-[10px] text-subtext0">Last snapshot: {SNAPSHOTS[0].date}</div>
                </div>
                <span class="text-[10px] text-overlay0 bg-surface0 px-2 py-1 rounded">Timeshift</span>
              </div>

              {/* Info banner */}
              <div class="bg-blue/10 border border-blue/30 rounded-lg p-2.5 mb-4 flex items-center gap-2">
                <span class="text-blue text-sm">ℹ</span>
                <span class="text-[10px] text-subtext0">
                  Snapshots let you restore your system to a previous state.
                </span>
              </div>

              {/* Snapshots list */}
              <div class="bg-mantle rounded-xl border border-surface0 p-3">
                <div class="flex items-center justify-between mb-2">
                  <span class="text-sm font-bold text-text">Available Snapshots</span>
                  <span class="text-[10px] text-overlay0">{SNAPSHOTS.length} snapshots</span>
                </div>
                <div class="space-y-2">
                  {SNAPSHOTS.map((snapshot) => (
                    <SnapshotRow key={snapshot.id} snapshot={snapshot} />
                  ))}
                </div>
              </div>
            </div>
          )}

          {currentPage === 'schedule' && (
            <div class="animate-fadeIn">
              <h2 class="text-lg font-bold text-text mb-1">Automatic Snapshots</h2>
              <p class="text-[10px] text-subtext0 mb-4">Configure automatic snapshot schedule.</p>

              <div class="bg-mantle rounded-xl border border-surface0 p-3 space-y-2">
                <ScheduleRow label="Boot Snapshots" description="Snapshot on every boot" defaultChecked />
                <ScheduleRow label="Hourly" description="Keep up to 5 hourly snapshots" />
                <ScheduleRow label="Daily" description="Keep up to 7 daily snapshots" defaultChecked />
                <ScheduleRow label="Weekly" description="Keep up to 4 weekly snapshots" defaultChecked />
                <ScheduleRow label="Monthly" description="Keep up to 3 monthly snapshots" />
              </div>
            </div>
          )}

          {currentPage === 'settings' && (
            <div class="animate-fadeIn">
              <h2 class="text-lg font-bold text-text mb-1">Backup Settings</h2>
              <p class="text-[10px] text-subtext0 mb-4">Configure backup behavior.</p>

              <div class="bg-mantle rounded-xl border border-surface0 p-3 space-y-3">
                <div class="flex items-center justify-between py-2 border-b border-surface0">
                  <div>
                    <div class="text-xs font-semibold text-text">Backup Location</div>
                    <div class="text-[10px] text-overlay0">Where to store snapshots</div>
                  </div>
                  <select class="bg-surface0 text-text text-[10px] rounded-lg px-2 py-1 border border-surface1">
                    <option>Local disk</option>
                    <option>External drive</option>
                  </select>
                </div>

                <div class="flex items-center justify-between py-2 border-b border-surface0">
                  <div>
                    <div class="text-xs font-semibold text-text">Include Home</div>
                    <div class="text-[10px] text-overlay0">Back up user files</div>
                  </div>
                  <ToggleSwitch />
                </div>

                <div class="flex items-center justify-between py-2">
                  <div>
                    <div class="text-xs font-semibold text-text">Compression</div>
                    <div class="text-[10px] text-overlay0">Compress snapshots</div>
                  </div>
                  <select class="bg-surface0 text-text text-[10px] rounded-lg px-2 py-1 border border-surface1">
                    <option>Fast (zstd)</option>
                    <option>None</option>
                    <option>Maximum</option>
                  </select>
                </div>
              </div>

              {/* Warning */}
              <div class="bg-yellow/10 border border-yellow/30 rounded-lg p-2.5 mt-4 flex items-center gap-2">
                <span class="text-yellow text-sm">⚠</span>
                <span class="text-[10px] text-subtext0">
                  System snapshots do not back up personal files. Use a separate backup for important data.
                </span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Bottom hints */}
      <div class="bg-surface0/30 px-4 py-2 flex items-center justify-between text-[10px] text-overlay0 border-t border-surface0">
        <span>Click sidebar to explore</span>
        <div class="flex gap-2">
          <span class="bg-surface0 px-2 py-0.5 rounded">Timeshift / Snapper</span>
        </div>
      </div>

      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(8px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fadeIn {
          animation: fadeIn 0.25s ease-out;
        }
      `}</style>
    </div>
  );
}

function SnapshotRow({ snapshot }: { snapshot: Snapshot }) {
  const typeColors: Record<SnapshotType, string> = {
    manual: 'blue',
    scheduled: 'green',
    boot: 'peach',
  };

  return (
    <div class="bg-base rounded-lg p-3 border border-surface0 flex items-center gap-3">
      <div class="flex-1 min-w-0">
        <div class="flex items-center gap-2">
          <span class="text-xs font-bold text-text">{snapshot.name}</span>
          <span class={`text-[8px] font-bold px-1.5 py-0.5 rounded bg-${typeColors[snapshot.type]}/20 text-${typeColors[snapshot.type]}`}>
            {snapshot.type.toUpperCase()}
          </span>
        </div>
        <div class="text-[10px] text-overlay0 flex gap-3">
          <span>{snapshot.date}</span>
          <span>{snapshot.size}</span>
        </div>
      </div>
      <button class="text-[10px] bg-blue text-crust font-semibold px-2 py-1 rounded hover:bg-sapphire transition-colors">
        Restore
      </button>
      <button class="text-[10px] text-overlay0 hover:text-red transition-colors">
        🗑
      </button>
    </div>
  );
}

function ScheduleRow({
  label,
  description,
  defaultChecked = false,
}: {
  label: string;
  description: string;
  defaultChecked?: boolean;
}) {
  return (
    <div class="flex items-center justify-between py-2 border-b border-surface0 last:border-0">
      <div>
        <div class="text-xs font-semibold text-text">{label}</div>
        <div class="text-[10px] text-overlay0">{description}</div>
      </div>
      <ToggleSwitch defaultChecked={defaultChecked} />
    </div>
  );
}

function ToggleSwitch({ defaultChecked = false }: { defaultChecked?: boolean }) {
  const [checked, setChecked] = useState(defaultChecked);

  return (
    <button
      onClick={() => setChecked(!checked)}
      class={`w-9 h-5 rounded-full transition-colors relative ${
        checked ? 'bg-mauve' : 'bg-surface1'
      }`}
    >
      <div
        class={`w-3.5 h-3.5 bg-text rounded-full absolute top-0.5 transition-all ${
          checked ? 'left-5' : 'left-0.5'
        }`}
      />
    </button>
  );
}
