import { useState, useEffect, useRef } from 'preact/hooks';

interface Preset {
  name: string;
  brightness: number;
  temperature: number;
  color: string;
}

const presets: Preset[] = [
  { name: 'Warm', brightness: 60, temperature: 15, color: 'peach' },
  { name: 'Studio', brightness: 80, temperature: 40, color: 'yellow' },
  { name: 'Daylight', brightness: 100, temperature: 75, color: 'sky' },
  { name: 'Off', brightness: 0, temperature: 50, color: 'surface0' },
];

export function InteractiveLighting() {
  const [power, setPower] = useState(true);
  const [brightness, setBrightness] = useState(20);
  const [temperature, setTemperature] = useState(40);
  const [activePreset, setActivePreset] = useState<string>('Studio');
  const [dragging, setDragging] = useState<'brightness' | 'temperature' | null>(null);

  const brightnessRef = useRef<HTMLDivElement | null>(null);
  const temperatureRef = useRef<HTMLDivElement | null>(null);

  // Calculate color based on temperature (2900K-7000K)
  const getTemperatureColor = () => {
    if (temperature < 30) return 'from-peach to-yellow';
    if (temperature < 50) return 'from-yellow to-yellow';
    if (temperature < 70) return 'from-yellow to-sky';
    return 'from-sky to-blue';
  };

  const getKelvin = () => {
    return Math.round(2900 + (temperature / 100) * 4100);
  };

  const handlePreset = (preset: Preset) => {
    setActivePreset(preset.name);
    if (preset.name === 'Off') {
      setPower(false);
    } else {
      setPower(true);
      setBrightness(preset.brightness);
      setTemperature(preset.temperature);
    }
  };

  const updateSliderValue = (
    e: MouseEvent | Touch,
    type: 'brightness' | 'temperature'
  ) => {
    const ref = type === 'brightness' ? brightnessRef : temperatureRef;
    if (!ref.current) return;

    const rect = ref.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const percent = Math.max(0, Math.min(100, (x / rect.width) * 100));

    if (type === 'brightness') {
      setBrightness(Math.round(percent));
      if (percent > 0 && !power) setPower(true);
      if (percent === 0) setPower(false);
    } else {
      setTemperature(Math.round(percent));
    }
    setActivePreset('');
  };

  const handleMouseDown = (type: 'brightness' | 'temperature', e: MouseEvent) => {
    e.preventDefault();
    setDragging(type);
    updateSliderValue(e, type);
  };

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (dragging) {
        updateSliderValue(e, dragging);
      }
    };

    const handleMouseUp = () => {
      setDragging(null);
    };

    if (dragging) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
      return () => {
        window.removeEventListener('mousemove', handleMouseMove);
        window.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [dragging]);

  // Touch support
  useEffect(() => {
    const handleTouchMove = (e: TouchEvent) => {
      if (dragging && e.touches[0]) {
        updateSliderValue(e.touches[0], dragging);
      }
    };

    const handleTouchEnd = () => {
      setDragging(null);
    };

    if (dragging) {
      window.addEventListener('touchmove', handleTouchMove, { passive: false });
      window.addEventListener('touchend', handleTouchEnd);
      return () => {
        window.removeEventListener('touchmove', handleTouchMove);
        window.removeEventListener('touchend', handleTouchEnd);
      };
    }
  }, [dragging]);

  const togglePower = () => {
    setPower(!power);
    if (!power) {
      setActivePreset('');
    } else {
      setActivePreset('Off');
    }
  };

  // Glow effect intensity based on brightness
  const glowIntensity = power ? brightness / 100 : 0;
  const glowColor = temperature < 40 ? 'rgba(250, 179, 135,' : temperature < 60 ? 'rgba(249, 226, 175,' : 'rgba(137, 220, 235,';

  return (
    <div class="bg-mantle rounded-2xl border-2 border-surface0 overflow-hidden shadow-2xl select-none">
      {/* Window Title Bar */}
      <div class="bg-crust px-4 py-3 flex items-center justify-between border-b border-surface0">
        <div class="flex items-center gap-3">
          <div class="flex gap-1.5">
            <div class="w-3 h-3 rounded-full bg-red/80"></div>
            <div class="w-3 h-3 rounded-full bg-yellow/80"></div>
            <div class="w-3 h-3 rounded-full bg-green/80"></div>
          </div>
          <div class="flex items-center gap-2 ml-2">
            <span class="text-lg">💡</span>
            <span class="text-sm font-bold text-text">Aegis Lighting</span>
            <span class="text-xs text-green">● 192.168.1.42</span>
          </div>
        </div>
        <span class="text-xs text-overlay0 bg-surface0 px-2 py-0.5 rounded">Super + F10</span>
      </div>

      {/* Content */}
      <div class="p-6 bg-base">
        {/* Power Toggle */}
        <div class="flex items-center justify-between mb-6">
          <span class="text-sm text-subtext0">Power</span>
          <button
            onClick={togglePower}
            class={`w-14 h-7 rounded-full flex items-center px-1 cursor-pointer transition-colors duration-200 ${
              power ? 'bg-green' : 'bg-surface1'
            }`}
          >
            <div
              class={`w-5 h-5 bg-white rounded-full shadow transition-transform duration-200 ${
                power ? 'translate-x-7' : 'translate-x-0'
              }`}
            ></div>
          </button>
        </div>

        {/* Light Preview */}
        <div class="bg-mantle rounded-xl p-6 flex flex-col items-center border border-surface0 mb-6 relative overflow-hidden">
          {/* Glow effect */}
          <div
            class="absolute inset-0 transition-all duration-300"
            style={{
              background: `radial-gradient(circle at center, ${glowColor} ${glowIntensity * 0.4}) 0%, transparent 70%)`,
            }}
          ></div>

          <div class="relative">
            <div
              class={`absolute inset-0 w-20 h-20 rounded-full blur-2xl transition-all duration-200 ${
                power ? `bg-gradient-to-br ${getTemperatureColor()}` : 'bg-surface0'
              }`}
              style={{ opacity: power ? brightness / 100 : 0.1 }}
            ></div>
            <div
              class={`relative w-20 h-20 rounded-xl flex items-center justify-center shadow-2xl border-4 transition-all duration-200 ${
                power
                  ? `bg-gradient-to-br ${getTemperatureColor()} border-white/20`
                  : 'bg-surface1 border-surface0'
              }`}
            >
              <span class="text-4xl">{power ? '💡' : '🔌'}</span>
            </div>
          </div>
          <div class="mt-3 text-center relative z-10">
            <div class={`text-xl font-bold transition-colors duration-150 ${power ? 'text-text' : 'text-overlay0'}`}>
              {power ? 'ON' : 'OFF'}
            </div>
            <div class="text-sm text-overlay0">
              {power ? `${getKelvin()}K · ${brightness}%` : 'Powered off'}
            </div>
          </div>
        </div>

        {/* Brightness Slider */}
        <div class="mb-5">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm text-subtext0">Brightness</span>
            <span class="text-sm font-mono text-text">{brightness}%</span>
          </div>
          <div
            ref={brightnessRef}
            class={`relative h-3 bg-surface0 rounded-full overflow-visible ${
              dragging === 'brightness' ? 'cursor-grabbing' : 'cursor-pointer'
            }`}
            onMouseDown={(e) => handleMouseDown('brightness', e)}
            onTouchStart={(e) => {
              e.preventDefault();
              setDragging('brightness');
              if (e.touches[0]) updateSliderValue(e.touches[0], 'brightness');
            }}
          >
            <div
              class="absolute inset-y-0 left-0 bg-gradient-to-r from-surface1 to-yellow rounded-full pointer-events-none"
              style={{
                width: `${brightness}%`,
                transition: dragging === 'brightness' ? 'none' : 'width 50ms ease-out'
              }}
            ></div>
            <div
              class={`absolute top-1/2 -translate-y-1/2 w-5 h-5 bg-white rounded-full shadow-lg border-2 border-yellow pointer-events-none ${
                dragging === 'brightness' ? 'scale-110' : ''
              }`}
              style={{
                left: `calc(${brightness}% - 10px)`,
                transition: dragging === 'brightness' ? 'none' : 'left 50ms ease-out, transform 150ms'
              }}
            ></div>
          </div>
        </div>

        {/* Temperature Slider */}
        <div class="mb-5">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm text-subtext0">Temperature</span>
            <span class="text-sm font-mono text-text">{getKelvin()}K</span>
          </div>
          <div
            ref={temperatureRef}
            class={`relative h-3 bg-gradient-to-r from-peach via-yellow to-sky rounded-full overflow-visible ${
              dragging === 'temperature' ? 'cursor-grabbing' : 'cursor-pointer'
            }`}
            onMouseDown={(e) => handleMouseDown('temperature', e)}
            onTouchStart={(e) => {
              e.preventDefault();
              setDragging('temperature');
              if (e.touches[0]) updateSliderValue(e.touches[0], 'temperature');
            }}
          >
            <div
              class={`absolute top-1/2 -translate-y-1/2 w-5 h-5 bg-white rounded-full shadow-lg border-2 border-text pointer-events-none ${
                dragging === 'temperature' ? 'scale-110' : ''
              }`}
              style={{
                left: `calc(${temperature}% - 10px)`,
                transition: dragging === 'temperature' ? 'none' : 'left 50ms ease-out, transform 150ms'
              }}
            ></div>
          </div>
          <div class="flex justify-between mt-1 text-[10px] text-overlay0">
            <span>2900K Warm</span>
            <span>7000K Cool</span>
          </div>
        </div>

        {/* Presets */}
        <div class="grid grid-cols-4 gap-2">
          {presets.map((preset) => (
            <button
              key={preset.name}
              onClick={() => handlePreset(preset)}
              class={`py-2 px-3 rounded-lg text-xs font-medium transition-all duration-150 ${
                activePreset === preset.name
                  ? `bg-${preset.color}/30 text-${preset.color} border-2 border-${preset.color}`
                  : `bg-${preset.color}/20 hover:bg-${preset.color}/30 text-${preset.color === 'surface0' ? 'text' : preset.color} border-2 border-transparent`
              }`}
            >
              {preset.name}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
