"""
Pytest configuration and fixtures for aegis_gtk tests.

This handles mocking GTK/GLib imports so tests can run on systems without GTK.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

# Mock gi module before any imports that might use it
gi_mock = MagicMock()
gi_mock.require_version = MagicMock()

# Mock GTK and related modules
gtk_mock = MagicMock()
adw_mock = MagicMock()
glib_mock = MagicMock()

# Make GLib functions return proper values
glib_mock.idle_add.return_value = 1
glib_mock.timeout_add.return_value = 2
glib_mock.timeout_add_seconds.return_value = 3
glib_mock.source_remove.return_value = True

gi_mock.repository.Gtk = gtk_mock
gi_mock.repository.Adw = adw_mock
gi_mock.repository.GLib = glib_mock
gi_mock.repository.Gdk = MagicMock()
gi_mock.repository.GdkPixbuf = MagicMock()
gi_mock.repository.Pango = MagicMock()

sys.modules['gi'] = gi_mock
sys.modules['gi.repository'] = gi_mock.repository

# Add the library path so we can import aegis_gtk
LIB_PATH = Path(__file__).parent.parent / "archiso" / "airootfs" / "usr" / "local" / "lib" / "python3" / "dist-packages"
sys.path.insert(0, str(LIB_PATH))

import pytest
import tempfile
import json


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_presets_file(temp_dir):
    """Create a mock presets.json file."""
    presets_data = {
        'presets': [
            {
                'id': 'custom-test-1',
                'name': 'Test Preset',
                'icon': '🔆',
                'color': 'blue',
                'temperature': 5000,
                'brightness': 75,
                'power': True,
                'is_builtin': False
            }
        ],
        'active_preset': 'custom-test-1'
    }

    presets_file = temp_dir / "presets.json"
    presets_file.write_text(json.dumps(presets_data, indent=2))
    return presets_file


@pytest.fixture
def mock_devices_file(temp_dir):
    """Create a mock devices.json file."""
    devices_data = {
        'keylights': [
            {'ip': '192.168.1.100', 'name': 'Key Light 1'},
            {'ip': '192.168.1.101', 'name': 'Key Light 2'}
        ]
    }

    devices_file = temp_dir / "devices.json"
    devices_file.write_text(json.dumps(devices_data, indent=2))
    return devices_file
