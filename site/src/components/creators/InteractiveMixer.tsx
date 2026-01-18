import { useState, useEffect, useRef, useCallback } from 'preact/hooks';

interface Channel {
  name: string;
  icon: string;
  color: string;
  apps: string;
  volume: number;
  muted: boolean;
  solo: boolean;
  level: number;
}

const initialChannels: Channel[] = [
  { name: 'Music', icon: '🎵', color: 'green', apps: 'Spotify, VLC', volume: 75, muted: false, solo: false, level: 65 },
  { name: 'Voice Chat', icon: '🎧', color: 'teal', apps: 'Discord, Slack', volume: 80, muted: false, solo: false, level: 45 },
  { name: 'Games', icon: '🎮', color: 'mauve', apps: 'Steam, Lutris', volume: 60, muted: false, solo: false, level: 70 },
  { name: 'Browser', icon: '🌐', color: 'blue', apps: 'Firefox, Chrome', volume: 50, muted: false, solo: false, level: 30 },
  { name: 'System', icon: '🔔', color: 'yellow', apps: 'Notifications', volume: 40, muted: false, solo: false, level: 15 },
  { name: 'Stream Mix', icon: '📺', color: 'red', apps: 'OBS capture', volume: 85, muted: false, solo: false, level: 55 },
];

const dspEffects = [
  { name: 'Noise Gate', enabled: true },
  { name: 'Compressor', enabled: true },
  { name: '5-Band EQ', enabled: false },
  { name: 'Limiter', enabled: true },
];

export function InteractiveMixer() {
  const [channels, setChannels] = useState<Channel[]>(initialChannels);
  const [micMuted, setMicMuted] = useState(false);
  const [micLevel, setMicLevel] = useState(55);
  const [dsp, setDsp] = useState(dspEffects);
  const [masterVolume, setMasterVolume] = useState(70);
  const [draggingFader, setDraggingFader] = useState<number | null>(null);
  const [draggingMaster, setDraggingMaster] = useState(false);

  const faderRefs = useRef<(HTMLDivElement | null)[]>([]);
  const masterRef = useRef<HTMLDivElement | null>(null);

  // Animate levels
  useEffect(() => {
    const interval = setInterval(() => {
      setChannels(prev => prev.map(ch => ({
        ...ch,
        level: ch.muted ? 0 : Math.max(5, Math.min(95, ch.level + (Math.random() - 0.5) * 15))
      })));
      if (!micMuted) {
        setMicLevel(prev => Math.max(10, Math.min(90, prev + (Math.random() - 0.5) * 20)));
      }
    }, 100);
    return () => clearInterval(interval);
  }, [micMuted]);

  const toggleMute = (index: number) => {
    setChannels(prev => prev.map((ch, i) =>
      i === index ? { ...ch, muted: !ch.muted } : ch
    ));
  };

  const toggleSolo = (index: number) => {
    setChannels(prev => prev.map((ch, i) =>
      i === index ? { ...ch, solo: !ch.solo } : ch
    ));
  };

  const setVolume = useCallback((index: number, volume: number) => {
    setChannels(prev => prev.map((ch, i) =>
      i === index ? { ...ch, volume: Math.max(0, Math.min(100, volume)) } : ch
    ));
  }, []);

  const toggleDsp = (index: number) => {
    setDsp(prev => prev.map((effect, i) =>
      i === index ? { ...effect, enabled: !effect.enabled } : effect
    ));
  };

  const volumeToDb = (vol: number) => {
    if (vol === 0) return '-∞';
    const db = Math.round((vol - 75) * 0.4);
    return db >= 0 ? `+${db}` : `${db}`;
  };

  // Fader drag handlers
  const handleFaderMouseDown = (index: number, e: MouseEvent) => {
    e.preventDefault();
    setDraggingFader(index);
  };

  const handleMasterMouseDown = (e: MouseEvent) => {
    e.preventDefault();
    setDraggingMaster(true);
    // Also update on initial click
    if (masterRef.current) {
      const rect = masterRef.current.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const percent = Math.max(0, Math.min(100, (x / rect.width) * 100));
      setMasterVolume(Math.round(percent));
    }
  };

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (draggingFader !== null && faderRefs.current[draggingFader]) {
        const rect = faderRefs.current[draggingFader]!.getBoundingClientRect();
        const y = e.clientY - rect.top;
        const percent = Math.max(0, Math.min(100, 100 - (y / rect.height) * 100));
        setVolume(draggingFader, Math.round(percent));
      }

      if (draggingMaster && masterRef.current) {
        const rect = masterRef.current.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const percent = Math.max(0, Math.min(100, (x / rect.width) * 100));
        setMasterVolume(Math.round(percent));
      }
    };

    const handleMouseUp = () => {
      setDraggingFader(null);
      setDraggingMaster(false);
    };

    if (draggingFader !== null || draggingMaster) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
      return () => {
        window.removeEventListener('mousemove', handleMouseMove);
        window.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [draggingFader, draggingMaster, setVolume]);

  // Touch support
  const handleFaderTouchStart = (index: number, e: TouchEvent) => {
    e.preventDefault();
    setDraggingFader(index);
  };

  useEffect(() => {
    const handleTouchMove = (e: TouchEvent) => {
      if (draggingFader !== null && faderRefs.current[draggingFader]) {
        const touch = e.touches[0];
        const rect = faderRefs.current[draggingFader]!.getBoundingClientRect();
        const y = touch.clientY - rect.top;
        const percent = Math.max(0, Math.min(100, 100 - (y / rect.height) * 100));
        setVolume(draggingFader, Math.round(percent));
      }

      if (draggingMaster && masterRef.current) {
        const touch = e.touches[0];
        const rect = masterRef.current.getBoundingClientRect();
        const x = touch.clientX - rect.left;
        const percent = Math.max(0, Math.min(100, (x / rect.width) * 100));
        setMasterVolume(Math.round(percent));
      }
    };

    const handleTouchEnd = () => {
      setDraggingFader(null);
      setDraggingMaster(false);
    };

    if (draggingFader !== null || draggingMaster) {
      window.addEventListener('touchmove', handleTouchMove, { passive: false });
      window.addEventListener('touchend', handleTouchEnd);
      return () => {
        window.removeEventListener('touchmove', handleTouchMove);
        window.removeEventListener('touchend', handleTouchEnd);
      };
    }
  }, [draggingFader, draggingMaster, setVolume]);

  return (
    <div class="bg-mantle rounded-2xl border-2 border-surface0 overflow-hidden shadow-2xl select-none">
      {/* Window Title Bar */}
      <div class="bg-crust px-4 py-3 flex items-center justify-between border-b border-surface0">
        <div class="flex items-center gap-3">
          <div class="flex gap-1.5">
            <div class="w-3 h-3 rounded-full bg-red/80 hover:bg-red cursor-pointer"></div>
            <div class="w-3 h-3 rounded-full bg-yellow/80 hover:bg-yellow cursor-pointer"></div>
            <div class="w-3 h-3 rounded-full bg-green/80 hover:bg-green cursor-pointer"></div>
          </div>
          <span class="text-sm font-bold text-text ml-2">Aegis Audio Mixer</span>
        </div>
        <div class="flex items-center gap-2">
          <span class="text-[10px] text-overlay0 bg-surface0 px-2 py-0.5 rounded">Drag the faders!</span>
        </div>
      </div>

      {/* Mixer Content */}
      <div class="p-6 md:p-8 bg-base">
        {/* Mic Input Section */}
        <div class="bg-surface0/30 rounded-xl p-4 mb-6 border border-surface0">
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center gap-3">
              <span class="text-2xl">🎤</span>
              <div>
                <div class="text-peach font-bold">Microphone</div>
                <div class="text-[10px] text-overlay0">Built-in Audio / USB Microphone</div>
              </div>
            </div>
            <button
              onClick={() => setMicMuted(!micMuted)}
              class={`px-3 py-1.5 rounded-lg text-sm font-bold transition-all duration-150 ${
                micMuted
                  ? 'bg-red text-crust'
                  : 'bg-surface1 text-text hover:bg-red hover:text-crust'
              }`}
            >
              {micMuted ? '🔇 Muted' : '🔊 Mute'}
            </button>
          </div>
          <div class="grid md:grid-cols-2 gap-4">
            {/* Input Level */}
            <div class="bg-base rounded-lg p-3">
              <div class="flex justify-between text-xs mb-2">
                <span class="text-overlay0 font-bold uppercase tracking-wider">Input Level</span>
                <span class="text-text font-mono">{volumeToDb(micMuted ? 0 : micLevel)} dB</span>
              </div>
              <div class="h-3 bg-surface0 rounded-full overflow-hidden">
                <div
                  class={`h-full rounded-full ${
                    micMuted ? 'bg-surface1' :
                    micLevel > 80 ? 'bg-gradient-to-r from-green via-yellow to-red' :
                    micLevel > 60 ? 'bg-gradient-to-r from-green to-yellow' :
                    'bg-green'
                  }`}
                  style={{
                    width: `${micMuted ? 0 : micLevel}%`,
                    transition: 'width 80ms ease-out'
                  }}
                ></div>
              </div>
            </div>
            {/* DSP Chain */}
            <div class="bg-base rounded-lg p-3">
              <div class="text-xs text-overlay0 font-bold uppercase tracking-wider mb-2">DSP Processing</div>
              <div class="flex flex-wrap gap-2">
                {dsp.map((effect, i) => (
                  <button
                    key={effect.name}
                    onClick={() => toggleDsp(i)}
                    class={`px-2 py-1 rounded text-[10px] font-bold transition-all duration-150 cursor-pointer ${
                      effect.enabled
                        ? 'bg-sky text-crust hover:bg-sky/80'
                        : 'bg-surface0 text-subtext0 hover:bg-surface1'
                    }`}
                  >
                    {effect.name}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Channel Strips */}
        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
          {channels.map((channel, index) => (
            <div
              key={channel.name}
              class={`bg-mantle rounded-xl p-4 border transition-all duration-150 ${
                channel.solo ? 'border-yellow shadow-lg shadow-yellow/20' :
                channel.muted ? 'border-surface0 opacity-60' :
                'border-surface0 hover:border-surface1'
              }`}
            >
              {/* Channel Label */}
              <div class="text-center mb-3">
                <div class="text-2xl mb-1">{channel.icon}</div>
                <div class={`font-bold text-${channel.color}`}>{channel.name}</div>
                <div class="text-[10px] text-overlay0 truncate">{channel.apps}</div>
              </div>

              {/* Fader Track */}
              <div
                ref={(el) => { faderRefs.current[index] = el; }}
                class={`relative h-32 w-4 mx-auto bg-surface0 rounded-full mb-3 cursor-pointer ${
                  draggingFader === index ? 'cursor-grabbing' : ''
                }`}
                onMouseDown={(e) => handleFaderMouseDown(index, e)}
                onTouchStart={(e) => handleFaderTouchStart(index, e)}
              >
                {/* Level Meter */}
                <div
                  class={`absolute bottom-0 left-0.5 w-1.5 rounded-full pointer-events-none ${
                    channel.muted ? 'bg-surface1' : `bg-gradient-to-t from-${channel.color} to-${channel.color}/50`
                  }`}
                  style={{
                    height: `${channel.muted ? 0 : channel.level}%`,
                    transition: 'height 80ms ease-out'
                  }}
                ></div>
                {/* Fader Knob */}
                <div
                  class={`absolute w-6 h-3 bg-surface2 rounded -left-1 border border-overlay0 pointer-events-none ${
                    draggingFader === index ? 'bg-overlay0 scale-110' : 'hover:bg-overlay0'
                  }`}
                  style={{
                    bottom: `calc(${channel.volume}% - 6px)`,
                    transition: draggingFader === index ? 'none' : 'bottom 50ms ease-out, background-color 150ms, transform 150ms'
                  }}
                ></div>
              </div>

              {/* Volume */}
              <div class="text-center text-xs text-subtext0 font-mono mb-2">
                {volumeToDb(channel.muted ? 0 : channel.volume)} dB
              </div>

              {/* Mute/Solo */}
              <div class="flex justify-center gap-2">
                <button
                  onClick={() => toggleMute(index)}
                  class={`w-7 h-7 rounded text-xs font-bold transition-all duration-150 ${
                    channel.muted
                      ? 'bg-red text-crust'
                      : 'bg-surface0 text-overlay0 hover:bg-red hover:text-crust'
                  }`}
                >
                  M
                </button>
                <button
                  onClick={() => toggleSolo(index)}
                  class={`w-7 h-7 rounded text-xs font-bold transition-all duration-150 ${
                    channel.solo
                      ? 'bg-yellow text-crust'
                      : 'bg-surface0 text-overlay0 hover:bg-yellow hover:text-crust'
                  }`}
                >
                  S
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Master Section */}
        <div class="bg-surface0/40 rounded-xl p-4 border-t border-surface0">
          <div class="flex flex-col md:flex-row items-center justify-between gap-6">
            {/* Routing Info */}
            <div class="flex flex-wrap gap-3 text-sm">
              <div class="bg-surface0 rounded-lg px-3 py-2 flex items-center gap-2">
                <span class="text-green">✓</span>
                <span class="text-subtext0">Apps auto-route</span>
              </div>
              <div class="bg-surface0 rounded-lg px-3 py-2 flex items-center gap-2">
                <span class="text-blue">📋</span>
                <span class="text-subtext0">80+ app rules</span>
              </div>
              <div class="bg-surface0 rounded-lg px-3 py-2 flex items-center gap-2">
                <span class="text-mauve">🔀</span>
                <span class="text-subtext0">qpwgraph for routing</span>
              </div>
            </div>

            {/* Master Output */}
            <div class="flex items-center gap-4 bg-surface0/50 rounded-xl px-6 py-3">
              <span class="text-overlay0 font-bold text-xs">MASTER</span>
              <div
                ref={masterRef}
                class={`w-32 h-3 bg-mantle rounded-full overflow-hidden relative ${
                  draggingMaster ? 'cursor-grabbing' : 'cursor-pointer'
                }`}
                onMouseDown={handleMasterMouseDown}
              >
                <div
                  class="h-full bg-gradient-to-r from-green via-yellow to-red pointer-events-none"
                  style={{
                    width: `${masterVolume}%`,
                    transition: draggingMaster ? 'none' : 'width 50ms ease-out'
                  }}
                ></div>
                {/* Knob indicator */}
                <div
                  class="absolute top-1/2 -translate-y-1/2 w-1 h-5 bg-white rounded-full shadow pointer-events-none"
                  style={{
                    left: `calc(${masterVolume}% - 2px)`,
                    transition: draggingMaster ? 'none' : 'left 50ms ease-out'
                  }}
                ></div>
              </div>
              <span class="text-text font-mono text-sm w-12">{volumeToDb(masterVolume)} dB</span>
              <span class="text-2xl">🔊</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
