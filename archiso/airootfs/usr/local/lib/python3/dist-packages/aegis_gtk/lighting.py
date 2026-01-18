"""
Aegis GTK Lighting - Shared lighting preset API and data structures.
Used by aegis-lighting and aegis-macropad for cross-app integration.
"""

import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any
from datetime import datetime
import urllib.request
import urllib.error


# Configuration paths
LIGHTING_CONFIG_DIR = Path.home() / ".config" / "aegis" / "lighting"
DEVICES_PATH = LIGHTING_CONFIG_DIR / "devices.json"
PRESETS_PATH = LIGHTING_CONFIG_DIR / "presets.json"


@dataclass
class LightingPreset:
    """Represents a lighting preset configuration."""
    id: str
    name: str
    icon: str
    color: str
    temperature: int  # Kelvin (2900-7000)
    brightness: int   # Percentage (0-100)
    power: bool
    is_builtin: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LightingPreset':
        return cls(**data)


# Default builtin presets
BUILTIN_PRESETS = [
    LightingPreset("warm", "Warm", "🌅", "peach", 3200, 30, True, True),
    LightingPreset("studio", "Studio", "🎬", "yellow", 4500, 50, True, True),
    LightingPreset("daylight", "Daylight", "☀️", "sky", 5600, 70, True, True),
    LightingPreset("off", "Off", "🌙", "surface1", 4500, 0, False, True),
]


class PresetManager:
    """Manages lighting presets with CRUD operations."""

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or PRESETS_PATH
        self.presets: List[LightingPreset] = []
        self.active_preset_id: Optional[str] = None
        self.load_presets()

    def load_presets(self) -> None:
        """Load presets from config file."""
        # Start with builtin presets
        self.presets = [LightingPreset(**asdict(p)) for p in BUILTIN_PRESETS]

        try:
            if self.config_path.exists():
                with open(self.config_path) as f:
                    data = json.load(f)
                    for preset_data in data.get('presets', []):
                        if not preset_data.get('is_builtin', False):
                            self.presets.append(LightingPreset.from_dict(preset_data))
                    self.active_preset_id = data.get('active_preset')
        except Exception as e:
            print(f"Error loading presets: {e}")

    def save_presets(self) -> None:
        """Save presets to config file."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            data = {
                'presets': [p.to_dict() for p in self.presets if not p.is_builtin],
                'active_preset': self.active_preset_id
            }
            with open(self.config_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving presets: {e}")

    def add_preset(self, preset: LightingPreset) -> None:
        """Add a new preset."""
        self.presets.append(preset)
        self.save_presets()

    def remove_preset(self, preset_id: str) -> bool:
        """Remove a preset by ID. Returns False if builtin."""
        for preset in self.presets:
            if preset.id == preset_id:
                if preset.is_builtin:
                    return False
                self.presets.remove(preset)
                self.save_presets()
                return True
        return False

    def update_preset(self, preset_id: str, **kwargs) -> bool:
        """Update a preset's properties."""
        for preset in self.presets:
            if preset.id == preset_id:
                if preset.is_builtin:
                    return False
                for key, value in kwargs.items():
                    if hasattr(preset, key):
                        setattr(preset, key, value)
                self.save_presets()
                return True
        return False

    def get_preset(self, preset_id: str) -> Optional[LightingPreset]:
        """Get a preset by ID."""
        for preset in self.presets:
            if preset.id == preset_id:
                return preset
        return None

    def create_from_current(self, name: str, icon: str, color: str,
                            temperature: int, brightness: int, power: bool) -> LightingPreset:
        """Create a new preset from current settings."""
        preset_id = f"custom-{int(datetime.now().timestamp())}"
        preset = LightingPreset(
            id=preset_id,
            name=name,
            icon=icon,
            color=color,
            temperature=temperature,
            brightness=brightness,
            power=power,
            is_builtin=False
        )
        self.add_preset(preset)
        return preset

    def export_presets(self, file_path: Path) -> bool:
        """Export user presets to a file."""
        try:
            user_presets = [p.to_dict() for p in self.presets if not p.is_builtin]
            with open(file_path, 'w') as f:
                json.dump({'presets': user_presets, 'version': 1}, f, indent=2)
            return True
        except Exception:
            return False

    def import_presets(self, file_path: Path) -> int:
        """Import presets from a file. Returns count of imported presets."""
        try:
            with open(file_path) as f:
                data = json.load(f)
            count = 0
            for preset_data in data.get('presets', []):
                preset_data['is_builtin'] = False
                preset_data['id'] = f"imported-{int(datetime.now().timestamp())}-{count}"
                self.presets.append(LightingPreset.from_dict(preset_data))
                count += 1
            if count > 0:
                self.save_presets()
            return count
        except Exception:
            return 0


class LightingPresetAPI:
    """API for accessing lighting presets from any application."""

    @staticmethod
    def get_presets() -> List[Dict]:
        """Load all available presets as dictionaries."""
        presets = [p.to_dict() for p in BUILTIN_PRESETS]
        try:
            if PRESETS_PATH.exists():
                with open(PRESETS_PATH) as f:
                    data = json.load(f)
                    for preset in data.get('presets', []):
                        if not preset.get('is_builtin', False):
                            presets.append(preset)
        except Exception:
            pass
        return presets

    @staticmethod
    def get_devices() -> List[Dict]:
        """Load configured light devices."""
        try:
            if DEVICES_PATH.exists():
                with open(DEVICES_PATH) as f:
                    data = json.load(f)
                    return data.get('keylights', [])
        except Exception:
            pass
        return []

    @staticmethod
    def apply_preset(preset_id: str) -> bool:
        """Apply a lighting preset to all configured devices.

        Args:
            preset_id: The ID of the preset to apply

        Returns:
            True if at least one device was successfully updated
        """
        # Find preset
        preset = None
        for p in LightingPresetAPI.get_presets():
            if p['id'] == preset_id:
                preset = p
                break

        if not preset:
            return False

        # Get devices
        devices = LightingPresetAPI.get_devices()
        if not devices:
            return False

        success = False
        for device in devices:
            ip = device.get('ip')
            if ip:
                try:
                    url = f"http://{ip}:9123/elgato/lights"
                    # Convert Kelvin to mired
                    temp_kelvin = preset.get('temperature', 4500)
                    temp_mired = int(1000000 / max(2900, min(7000, temp_kelvin)))

                    light_data = {
                        'on': 1 if preset.get('power', True) else 0,
                        'brightness': preset.get('brightness', 50),
                        'temperature': temp_mired
                    }
                    payload = json.dumps({'lights': [light_data]}).encode()
                    req = urllib.request.Request(url, data=payload, method='PUT')
                    req.add_header('Content-Type', 'application/json')
                    with urllib.request.urlopen(req, timeout=2) as response:
                        if response.status == 200:
                            success = True
                except Exception:
                    pass

        return success

    @staticmethod
    def get_current_state(device_ip: Optional[str] = None) -> Optional[Dict]:
        """Get current lighting state from a device.

        Args:
            device_ip: IP address of device, or None to use first configured device

        Returns:
            Dict with 'on', 'brightness', 'temperature' or None on error
        """
        if device_ip is None:
            devices = LightingPresetAPI.get_devices()
            if not devices:
                return None
            device_ip = devices[0].get('ip')

        if not device_ip:
            return None

        try:
            url = f"http://{device_ip}:9123/elgato/lights"
            req = urllib.request.Request(url, method='GET')
            with urllib.request.urlopen(req, timeout=2) as response:
                data = json.loads(response.read().decode())
                light = data['lights'][0]
                return {
                    'on': light['on'] == 1,
                    'brightness': light['brightness'],
                    'temperature': int(1000000 / light['temperature'])  # mired to Kelvin
                }
        except Exception:
            return None


class SmartLight:
    """Represents a network-connected smart light device."""

    def __init__(self, ip: str, name: str = "Smart Light"):
        self.ip = ip
        self.name = name
        self.port = 9123
        self.on = False
        self.brightness = 50
        self.temperature = 4500  # Kelvin
        self.connected = False

    @property
    def url(self) -> str:
        return f"http://{self.ip}:{self.port}/elgato/lights"

    def fetch_status(self) -> bool:
        """Fetch current status from the device."""
        try:
            req = urllib.request.Request(self.url, method='GET')
            with urllib.request.urlopen(req, timeout=2) as response:
                data = json.loads(response.read().decode())
                light = data['lights'][0]
                self.on = light['on'] == 1
                self.brightness = light['brightness']
                self.temperature = int(1000000 / light['temperature'])
                self.connected = True
                return True
        except Exception:
            self.connected = False
            return False

    def set_state(self, on: Optional[bool] = None, brightness: Optional[int] = None,
                  temperature: Optional[int] = None) -> bool:
        """Update the light state."""
        try:
            light_data = {}
            if on is not None:
                light_data['on'] = 1 if on else 0
                self.on = on
            if brightness is not None:
                light_data['brightness'] = max(0, min(100, brightness))
                self.brightness = brightness
            if temperature is not None:
                light_data['temperature'] = int(1000000 / max(2900, min(7000, temperature)))
                self.temperature = temperature

            payload = json.dumps({'lights': [light_data]}).encode()
            req = urllib.request.Request(self.url, data=payload, method='PUT')
            req.add_header('Content-Type', 'application/json')
            with urllib.request.urlopen(req, timeout=2) as response:
                return response.status == 200
        except Exception:
            return False

    def apply_preset(self, preset: LightingPreset) -> bool:
        """Apply a preset to this light."""
        return self.set_state(
            on=preset.power,
            brightness=preset.brightness,
            temperature=preset.temperature
        )
