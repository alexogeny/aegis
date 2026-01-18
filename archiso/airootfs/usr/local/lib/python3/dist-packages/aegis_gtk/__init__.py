"""
Aegis GTK - Shared library for Aegis GTK4/Libadwaita applications.
Provides consistent theming, common widgets, and utility functions.
"""

from .theme import (
    COLORS,
    ACCENT_COLORS,
    LIGHT_COLORS,
    get_base_css,
    get_app_css,
    setup_css,
    needs_dark_text,
)
from .widgets import (
    ActionRow,
    ColorPickerRow,
    EmojiPicker,
    IconPicker,
    PreviewButton,
    SectionLabel,
    SliderRow,
    StatusLabel,
)
from .dialogs import (
    ConfirmDialog,
    FileExportDialog,
    FileImportDialog,
    IconPickerDialog,
    InputDialog,
)
from .utils import (
    AsyncResult,
    debounce,
    idle_add,
    run_async,
    run_in_thread,
    show_toast,
    throttle,
    timeout_add,
    timeout_add_seconds,
)
from .lighting import (
    BUILTIN_PRESETS,
    LightingPreset,
    LightingPresetAPI,
    PresetManager,
    SmartLight,
    DEVICES_PATH,
    PRESETS_PATH,
    LIGHTING_CONFIG_DIR,
)
from .db_widgets import (
    EditConfirmDialog,
    EntityView,
    RowDetailView,
    RowDetailWindow,
    SchemaNode,
    SchemaTree,
    SyntaxHighlightedEditor,
    VirtualScrollingTable,
    get_db_widgets_css,
)

__version__ = '1.0.0'
__all__ = [
    # Theme
    'COLORS',
    'ACCENT_COLORS',
    'LIGHT_COLORS',
    'get_base_css',
    'get_app_css',
    'setup_css',
    'needs_dark_text',
    # Widgets
    'ActionRow',
    'ColorPickerRow',
    'EmojiPicker',
    'IconPicker',
    'PreviewButton',
    'SectionLabel',
    'SliderRow',
    'StatusLabel',
    # Dialogs
    'ConfirmDialog',
    'FileExportDialog',
    'FileImportDialog',
    'IconPickerDialog',
    'InputDialog',
    # Utils
    'AsyncResult',
    'debounce',
    'idle_add',
    'run_async',
    'run_in_thread',
    'show_toast',
    'throttle',
    'timeout_add',
    'timeout_add_seconds',
    # Lighting
    'BUILTIN_PRESETS',
    'DEVICES_PATH',
    'LIGHTING_CONFIG_DIR',
    'LightingPreset',
    'LightingPresetAPI',
    'PRESETS_PATH',
    'PresetManager',
    'SmartLight',
    # Database widgets
    'EditConfirmDialog',
    'EntityView',
    'RowDetailView',
    'RowDetailWindow',
    'SchemaNode',
    'SchemaTree',
    'SyntaxHighlightedEditor',
    'VirtualScrollingTable',
    'get_db_widgets_css',
]
