"""
Tests for aegis_gtk.lighting module.
"""

import pytest
import json
from pathlib import Path
from dataclasses import asdict


class TestLightingPreset:
    """Tests for the LightingPreset dataclass."""

    def test_create_preset(self):
        """Test creating a LightingPreset."""
        from aegis_gtk.lighting import LightingPreset

        preset = LightingPreset(
            id="test-1",
            name="Test Preset",
            icon="🔆",
            color="blue",
            temperature=5000,
            brightness=75,
            power=True,
            is_builtin=False
        )

        assert preset.id == "test-1"
        assert preset.name == "Test Preset"
        assert preset.icon == "🔆"
        assert preset.color == "blue"
        assert preset.temperature == 5000
        assert preset.brightness == 75
        assert preset.power is True
        assert preset.is_builtin is False

    def test_preset_to_dict(self):
        """Test converting preset to dictionary."""
        from aegis_gtk.lighting import LightingPreset

        preset = LightingPreset(
            id="test-1",
            name="Test",
            icon="🔆",
            color="blue",
            temperature=5000,
            brightness=75,
            power=True
        )

        d = preset.to_dict()

        assert isinstance(d, dict)
        assert d['id'] == "test-1"
        assert d['name'] == "Test"
        assert d['temperature'] == 5000

    def test_preset_from_dict(self):
        """Test creating preset from dictionary."""
        from aegis_gtk.lighting import LightingPreset

        data = {
            'id': 'from-dict',
            'name': 'From Dict',
            'icon': '💡',
            'color': 'green',
            'temperature': 4500,
            'brightness': 50,
            'power': False,
            'is_builtin': False
        }

        preset = LightingPreset.from_dict(data)

        assert preset.id == 'from-dict'
        assert preset.name == 'From Dict'
        assert preset.temperature == 4500
        assert preset.power is False

    def test_preset_roundtrip(self):
        """Test that to_dict and from_dict are inverse operations."""
        from aegis_gtk.lighting import LightingPreset

        original = LightingPreset(
            id="roundtrip",
            name="Roundtrip Test",
            icon="🌟",
            color="mauve",
            temperature=6500,
            brightness=100,
            power=True,
            is_builtin=False
        )

        d = original.to_dict()
        restored = LightingPreset.from_dict(d)

        assert original.id == restored.id
        assert original.name == restored.name
        assert original.temperature == restored.temperature
        assert original.brightness == restored.brightness


class TestBuiltinPresets:
    """Tests for builtin presets."""

    def test_builtin_presets_exist(self):
        """Verify builtin presets are defined."""
        from aegis_gtk.lighting import BUILTIN_PRESETS

        assert len(BUILTIN_PRESETS) > 0

    def test_builtin_presets_are_builtin(self):
        """Verify all builtin presets have is_builtin=True."""
        from aegis_gtk.lighting import BUILTIN_PRESETS

        for preset in BUILTIN_PRESETS:
            assert preset.is_builtin is True, f"Preset {preset.name} should be builtin"

    def test_builtin_presets_have_valid_temperatures(self):
        """Verify builtin presets have valid temperature ranges."""
        from aegis_gtk.lighting import BUILTIN_PRESETS

        for preset in BUILTIN_PRESETS:
            assert 2900 <= preset.temperature <= 7000, \
                f"Preset {preset.name} has invalid temperature: {preset.temperature}"

    def test_builtin_presets_have_valid_brightness(self):
        """Verify builtin presets have valid brightness ranges."""
        from aegis_gtk.lighting import BUILTIN_PRESETS

        for preset in BUILTIN_PRESETS:
            assert 0 <= preset.brightness <= 100, \
                f"Preset {preset.name} has invalid brightness: {preset.brightness}"


class TestPresetManager:
    """Tests for PresetManager class."""

    def test_create_manager(self, temp_dir):
        """Test creating a PresetManager."""
        from aegis_gtk.lighting import PresetManager

        config_path = temp_dir / "presets.json"
        manager = PresetManager(config_path=config_path)

        assert manager.config_path == config_path
        assert len(manager.presets) > 0  # Should have builtin presets

    def test_manager_loads_builtins(self, temp_dir):
        """Verify manager loads builtin presets."""
        from aegis_gtk.lighting import PresetManager, BUILTIN_PRESETS

        config_path = temp_dir / "presets.json"
        manager = PresetManager(config_path=config_path)

        builtin_ids = {p.id for p in BUILTIN_PRESETS}
        manager_builtin_ids = {p.id for p in manager.presets if p.is_builtin}

        assert builtin_ids == manager_builtin_ids

    def test_manager_loads_custom_presets(self, mock_presets_file):
        """Verify manager loads custom presets from file."""
        from aegis_gtk.lighting import PresetManager

        manager = PresetManager(config_path=mock_presets_file)

        custom_preset = manager.get_preset('custom-test-1')
        assert custom_preset is not None
        assert custom_preset.name == 'Test Preset'
        assert custom_preset.is_builtin is False

    def test_add_preset(self, temp_dir):
        """Test adding a new preset."""
        from aegis_gtk.lighting import PresetManager, LightingPreset

        config_path = temp_dir / "presets.json"
        manager = PresetManager(config_path=config_path)

        initial_count = len(manager.presets)

        new_preset = LightingPreset(
            id="new-preset",
            name="New Preset",
            icon="✨",
            color="pink",
            temperature=4000,
            brightness=60,
            power=True
        )

        manager.add_preset(new_preset)

        assert len(manager.presets) == initial_count + 1
        assert manager.get_preset("new-preset") is not None

    def test_remove_preset(self, temp_dir):
        """Test removing a preset."""
        from aegis_gtk.lighting import PresetManager, LightingPreset

        config_path = temp_dir / "presets.json"
        manager = PresetManager(config_path=config_path)

        # Add a preset first
        preset = LightingPreset(
            id="to-remove",
            name="To Remove",
            icon="🗑️",
            color="red",
            temperature=5000,
            brightness=50,
            power=True
        )
        manager.add_preset(preset)

        # Now remove it
        result = manager.remove_preset("to-remove")

        assert result is True
        assert manager.get_preset("to-remove") is None

    def test_cannot_remove_builtin_preset(self, temp_dir):
        """Verify builtin presets cannot be removed."""
        from aegis_gtk.lighting import PresetManager, BUILTIN_PRESETS

        config_path = temp_dir / "presets.json"
        manager = PresetManager(config_path=config_path)

        builtin_id = BUILTIN_PRESETS[0].id
        result = manager.remove_preset(builtin_id)

        assert result is False
        assert manager.get_preset(builtin_id) is not None

    def test_update_preset(self, temp_dir):
        """Test updating a preset."""
        from aegis_gtk.lighting import PresetManager, LightingPreset

        config_path = temp_dir / "presets.json"
        manager = PresetManager(config_path=config_path)

        # Add a preset first
        preset = LightingPreset(
            id="to-update",
            name="Original Name",
            icon="📝",
            color="blue",
            temperature=5000,
            brightness=50,
            power=True
        )
        manager.add_preset(preset)

        # Update it
        result = manager.update_preset("to-update", name="Updated Name", brightness=75)

        assert result is True
        updated = manager.get_preset("to-update")
        assert updated.name == "Updated Name"
        assert updated.brightness == 75

    def test_cannot_update_builtin_preset(self, temp_dir):
        """Verify builtin presets cannot be updated."""
        from aegis_gtk.lighting import PresetManager, BUILTIN_PRESETS

        config_path = temp_dir / "presets.json"
        manager = PresetManager(config_path=config_path)

        builtin_id = BUILTIN_PRESETS[0].id
        original_name = BUILTIN_PRESETS[0].name

        result = manager.update_preset(builtin_id, name="Hacked Name")

        assert result is False
        assert manager.get_preset(builtin_id).name == original_name

    def test_create_from_current(self, temp_dir):
        """Test creating a preset from current settings."""
        from aegis_gtk.lighting import PresetManager

        config_path = temp_dir / "presets.json"
        manager = PresetManager(config_path=config_path)

        preset = manager.create_from_current(
            name="My Preset",
            icon="🎨",
            color="teal",
            temperature=5500,
            brightness=80,
            power=True
        )

        assert preset.name == "My Preset"
        assert preset.is_builtin is False
        assert preset.id.startswith("custom-")
        assert manager.get_preset(preset.id) is not None

    def test_export_presets(self, temp_dir):
        """Test exporting presets to file."""
        from aegis_gtk.lighting import PresetManager, LightingPreset

        config_path = temp_dir / "presets.json"
        export_path = temp_dir / "export.json"
        manager = PresetManager(config_path=config_path)

        # Add some custom presets
        manager.add_preset(LightingPreset(
            id="export-1", name="Export 1", icon="📤", color="blue",
            temperature=5000, brightness=50, power=True
        ))

        result = manager.export_presets(export_path)

        assert result is True
        assert export_path.exists()

        # Verify export content
        with open(export_path) as f:
            data = json.load(f)
        assert 'presets' in data
        assert 'version' in data

    def test_import_presets(self, temp_dir):
        """Test importing presets from file."""
        from aegis_gtk.lighting import PresetManager

        config_path = temp_dir / "presets.json"
        import_path = temp_dir / "import.json"

        # Create import file
        import_data = {
            'presets': [
                {
                    'id': 'imported-1',
                    'name': 'Imported Preset',
                    'icon': '📥',
                    'color': 'green',
                    'temperature': 4500,
                    'brightness': 60,
                    'power': True,
                    'is_builtin': False
                }
            ],
            'version': 1
        }
        import_path.write_text(json.dumps(import_data))

        manager = PresetManager(config_path=config_path)
        initial_count = len([p for p in manager.presets if not p.is_builtin])

        count = manager.import_presets(import_path)

        assert count == 1
        # Should have one more custom preset
        final_count = len([p for p in manager.presets if not p.is_builtin])
        assert final_count == initial_count + 1


class TestLightingPresetAPI:
    """Tests for LightingPresetAPI static methods."""

    def test_get_presets_returns_list(self):
        """Verify get_presets returns a list."""
        from aegis_gtk.lighting import LightingPresetAPI

        presets = LightingPresetAPI.get_presets()

        assert isinstance(presets, list)
        # Should at least have builtin presets
        assert len(presets) > 0

    def test_get_presets_includes_builtins(self):
        """Verify get_presets includes builtin presets."""
        from aegis_gtk.lighting import LightingPresetAPI, BUILTIN_PRESETS

        presets = LightingPresetAPI.get_presets()
        preset_ids = {p['id'] for p in presets}
        builtin_ids = {p.id for p in BUILTIN_PRESETS}

        assert builtin_ids.issubset(preset_ids)

    def test_get_devices_returns_list(self):
        """Verify get_devices returns a list."""
        from aegis_gtk.lighting import LightingPresetAPI

        devices = LightingPresetAPI.get_devices()

        assert isinstance(devices, list)


class TestSmartLight:
    """Tests for SmartLight class."""

    def test_create_smart_light(self):
        """Test creating a SmartLight instance."""
        from aegis_gtk.lighting import SmartLight

        light = SmartLight(ip="192.168.1.100", name="Test Light")

        assert light.ip == "192.168.1.100"
        assert light.name == "Test Light"
        assert light.port == 9123
        assert light.connected is False

    def test_smart_light_url(self):
        """Test SmartLight URL property."""
        from aegis_gtk.lighting import SmartLight

        light = SmartLight(ip="192.168.1.100")

        assert light.url == "http://192.168.1.100:9123/elgato/lights"

    def test_smart_light_default_values(self):
        """Test SmartLight default values."""
        from aegis_gtk.lighting import SmartLight

        light = SmartLight(ip="192.168.1.100")

        assert light.on is False
        assert light.brightness == 50
        assert light.temperature == 4500
