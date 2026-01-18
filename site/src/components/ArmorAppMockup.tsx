import { useState, useEffect } from 'preact/hooks';

type Page = 'overview' | 'apparmor' | 'firewall' | 'hardening';

interface Profile {
  name: string;
  path: string;
  status: 'enforce' | 'complain';
  complaints: number;
}

interface FirewallRule {
  action: 'accept' | 'drop';
  protocol: string;
  port: string | null;
  comment: string;
}

const PROFILES: Profile[] = [
  { name: 'firefox', path: '/usr/lib/firefox/firefox', status: 'enforce', complaints: 0 },
  { name: 'discord', path: '/usr/bin/discord', status: 'complain', complaints: 3 },
  { name: 'steam', path: '/usr/bin/steam', status: 'enforce', complaints: 0 },
  { name: 'obs', path: '/usr/bin/obs', status: 'enforce', complaints: 0 },
  { name: 'code', path: '/usr/bin/code', status: 'complain', complaints: 1 },
];

const FIREWALL_RULES: FirewallRule[] = [
  { action: 'accept', protocol: 'tcp', port: '22', comment: 'SSH access' },
  { action: 'accept', protocol: 'tcp', port: '80,443', comment: 'HTTP/HTTPS' },
  { action: 'accept', protocol: 'udp', port: '5353', comment: 'mDNS (device discovery)' },
  { action: 'drop', protocol: 'any', port: null, comment: 'Default deny' },
];

const HARDENING_SETTINGS = [
  { name: 'ASLR', desc: 'Address Space Layout Randomization', active: true },
  { name: 'PTI', desc: 'Page Table Isolation (Meltdown protection)', active: true },
  { name: 'SMAP/SMEP', desc: 'Supervisor Mode Access Prevention', active: true },
  { name: 'Lockdown', desc: 'Kernel Lockdown Mode', active: true },
];

export function ArmorAppMockup() {
  const [currentPage, setCurrentPage] = useState<Page>('overview');
  const [hoveredProfile, setHoveredProfile] = useState<string | null>(null);
  const [animateIn, setAnimateIn] = useState(false);

  useEffect(() => {
    setAnimateIn(true);
  }, []);

  const sidebarItems: { id: Page; icon: string; label: string }[] = [
    { id: 'overview', icon: '', label: 'Overview' },
    { id: 'apparmor', icon: '', label: 'AppArmor' },
    { id: 'firewall', icon: '', label: 'Firewall' },
    { id: 'hardening', icon: '', label: 'Hardening' },
  ];

  const complainingProfiles = PROFILES.filter((p) => p.status === 'complain');
  const totalComplaints = complainingProfiles.reduce((sum, p) => sum + p.complaints, 0);

  return (
    <div class={`bg-base rounded-2xl border-2 border-surface0 overflow-hidden shadow-2xl transition-all duration-500 ${animateIn ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
      {/* GTK Header Bar */}
      <div class="bg-crust px-4 py-2.5 flex items-center justify-between border-b border-surface0">
        <div class="flex items-center gap-3">
          <div class="flex gap-1.5">
            <div class="w-3 h-3 rounded-full bg-red/80 hover:bg-red transition-colors cursor-pointer"></div>
            <div class="w-3 h-3 rounded-full bg-yellow/80 hover:bg-yellow transition-colors cursor-pointer"></div>
            <div class="w-3 h-3 rounded-full bg-green/80 hover:bg-green transition-colors cursor-pointer"></div>
          </div>
          <span class="text-sm font-bold text-mauve ml-2">Aegis Armor</span>
        </div>
        <button class="text-overlay0 hover:text-text transition-colors p-1 rounded hover:bg-surface0">
          <span class="text-sm"></span>
        </button>
      </div>

      <div class="flex" style={{ height: '340px' }}>
        {/* Sidebar */}
        <div class="w-44 bg-mantle border-r border-surface0 p-2 shrink-0">
          {sidebarItems.map((item) => (
            <button
              key={item.id}
              onClick={() => setCurrentPage(item.id)}
              class={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg mb-1 transition-all duration-200 ${
                currentPage === item.id
                  ? 'bg-mauve text-crust font-semibold'
                  : 'text-subtext0 hover:bg-surface0 hover:text-text'
              }`}
            >
              <span class="text-lg">{item.icon}</span>
              <span class="text-sm">{item.label}</span>
            </button>
          ))}
        </div>

        {/* Main Content */}
        <div class="flex-1 overflow-y-auto p-4">
          {currentPage === 'overview' && (
            <div class="animate-fadeIn">
              <div class="mb-4">
                <h2 class="text-xl font-bold text-mauve mb-1">Aegis Armor</h2>
                <p class="text-xs text-subtext0">Security configuration center</p>
              </div>

              {/* Status Grid */}
              <div class="grid grid-cols-2 gap-3">
                <StatusCard
                  icon=""
                  title="AppArmor"
                  status={complainingProfiles.length > 0 ? `${PROFILES.filter((p) => p.status === 'enforce').length} enforcing, ${complainingProfiles.length} complaining` : `${PROFILES.length} profiles enforcing`}
                  statusColor={complainingProfiles.length > 0 ? 'yellow' : 'green'}
                  color="mauve"
                />
                <StatusCard
                  icon=""
                  title="Firewall"
                  status={`${FIREWALL_RULES.length} rules active`}
                  statusColor="green"
                  color="blue"
                />
                <StatusCard
                  icon=""
                  title="ClamAV"
                  status="Definitions up to date"
                  statusColor="green"
                  color="teal"
                />
                <StatusCard
                  icon=""
                  title="Kernel"
                  status="All mitigations active"
                  statusColor="green"
                  color="green"
                />
              </div>

              {/* Quick Actions */}
              <div class="mt-4">
                <div class="text-xs font-bold text-text mb-2">Quick Actions</div>
                <div class="flex gap-2">
                  <button class="bg-blue text-crust text-xs font-semibold px-3 py-1.5 rounded-lg hover:bg-sapphire transition-colors">
                    Run ClamAV Scan
                  </button>
                  <button class="bg-blue text-crust text-xs font-semibold px-3 py-1.5 rounded-lg hover:bg-sapphire transition-colors">
                    Update Definitions
                  </button>
                </div>
              </div>
            </div>
          )}

          {currentPage === 'apparmor' && (
            <div class="animate-fadeIn">
              <h2 class="text-lg font-bold text-mauve mb-3">AppArmor Profiles</h2>

              {/* Complaints Banner */}
              {complainingProfiles.length > 0 && (
                <div class="bg-yellow/10 border border-yellow/30 rounded-lg p-3 mb-3 flex items-center gap-2">
                  <span class="text-yellow"></span>
                  <span class="text-xs text-subtext0 flex-1">
                    {complainingProfiles.length} profiles in complain mode with {totalComplaints} logged denials.
                  </span>
                  <button class="bg-green text-crust text-[10px] font-bold px-2 py-1 rounded">Enforce All</button>
                </div>
              )}

              {/* Profiles List */}
              <div class="bg-mantle rounded-xl border border-surface0 p-2 space-y-1">
                {PROFILES.map((profile) => (
                  <div
                    key={profile.name}
                    onMouseEnter={() => setHoveredProfile(profile.name)}
                    onMouseLeave={() => setHoveredProfile(null)}
                    class={`bg-base rounded-lg p-2.5 border border-surface0 flex items-center gap-3 transition-all ${
                      hoveredProfile === profile.name ? 'border-surface1' : ''
                    }`}
                  >
                    <div class="flex-1 min-w-0">
                      <div class="text-text font-semibold text-sm">{profile.name}</div>
                      <div class="text-overlay0 text-[10px] font-mono truncate">{profile.path}</div>
                    </div>
                    <span
                      class={`text-[10px] font-bold ${
                        profile.status === 'enforce' ? 'text-green' : 'text-yellow'
                      }`}
                    >
                      {profile.status === 'enforce' ? ' Enforcing' : ` Complain (${profile.complaints})`}
                    </span>
                    {profile.status === 'complain' && (
                      <button class="bg-green text-crust text-[10px] font-bold px-2 py-1 rounded">Enforce</button>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {currentPage === 'firewall' && (
            <div class="animate-fadeIn">
              <div class="flex items-center justify-between mb-3">
                <h2 class="text-lg font-bold text-blue">Firewall Rules</h2>
                <button class="bg-blue text-crust text-[10px] font-bold px-2 py-1 rounded">Add Rule</button>
              </div>

              {/* Policy Info */}
              <div class="bg-blue/10 border border-blue/30 rounded-lg p-3 mb-3 flex items-center gap-2">
                <span class="text-blue"></span>
                <span class="text-xs text-subtext0">Default policy: DROP all incoming connections.</span>
              </div>

              {/* Rules List */}
              <div class="bg-mantle rounded-xl border border-surface0 p-2 space-y-1">
                {FIREWALL_RULES.map((rule, i) => (
                  <div
                    key={i}
                    class={`bg-base rounded-lg p-2.5 border-l-4 flex items-center gap-3 ${
                      rule.action === 'accept' ? 'border-green' : 'border-red'
                    }`}
                  >
                    <div class="flex-1">
                      <div class="text-text font-semibold text-sm">
                        {rule.action.toUpperCase()} {rule.protocol.toUpperCase()}
                        {rule.port ? ` port ${rule.port}` : ' all'}
                      </div>
                      <div class="text-overlay0 text-[10px]">{rule.comment}</div>
                    </div>
                    {rule.action !== 'drop' && (
                      <button class="text-overlay0 hover:text-red text-sm transition-colors"></button>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {currentPage === 'hardening' && (
            <div class="animate-fadeIn">
              <h2 class="text-lg font-bold text-green mb-1">System Hardening</h2>
              <p class="text-xs text-subtext0 mb-3">Kernel security settings and exploit mitigations.</p>

              {/* Settings List */}
              <div class="bg-mantle rounded-xl border border-surface0 p-2 space-y-1">
                {HARDENING_SETTINGS.map((setting) => (
                  <div key={setting.name} class="bg-base rounded-lg p-2.5 flex items-center gap-3">
                    <div class="flex-1">
                      <div class="text-text font-semibold text-sm">
                        {setting.name}
                        <span class="text-overlay0 font-normal"> - {setting.desc}</span>
                      </div>
                    </div>
                    <span class={`text-[10px] font-bold ${setting.active ? 'text-green' : 'text-red'}`}>
                      {setting.active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Bottom hints */}
      <div class="bg-surface0/30 px-4 py-2 flex flex-wrap items-center justify-between gap-2 text-[10px] text-overlay0 border-t border-surface0">
        <span>Click sidebar to explore</span>
        <div class="flex gap-2">
          <span class="bg-surface0 px-2 py-0.5 rounded">GTK4/Libadwaita</span>
          <span class="bg-surface0 px-2 py-0.5 rounded">Catppuccin Mocha</span>
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

function StatusCard({
  icon,
  title,
  status,
  statusColor,
  color,
}: {
  icon: string;
  title: string;
  status: string;
  statusColor: string;
  color: string;
}) {
  return (
    <div class="bg-mantle rounded-xl border border-surface0 p-3">
      <div class="flex items-center gap-2 mb-1">
        <span class="text-lg">{icon}</span>
        <span class={`font-bold text-sm text-${color}`}>{title}</span>
      </div>
      <div class={`text-[10px] font-semibold text-${statusColor}`}>{status}</div>
    </div>
  );
}
