"""
Aegis GTK Widgets - Reusable UI components for Aegis applications.
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib, Gio, GdkPixbuf
from pathlib import Path
from typing import Optional, List, Dict, Callable, Any

from .theme import COLORS, ACCENT_COLORS, needs_dark_text


class SectionLabel(Gtk.Label):
    """A styled section header label."""

    def __init__(self, text: str):
        super().__init__(label=text)
        self.add_css_class('section-title')
        self.set_halign(Gtk.Align.START)


class StatusLabel(Gtk.Label):
    """A status indicator label with connected/disconnected/warning states."""

    def __init__(self, text: str = "", status: str = "connected"):
        super().__init__(label=text)
        self.set_halign(Gtk.Align.START)
        self.set_status(status)

    def set_status(self, status: str):
        """Set the status type: 'connected', 'disconnected', or 'warning'."""
        self.remove_css_class('status-connected')
        self.remove_css_class('status-disconnected')
        self.remove_css_class('status-warning')
        self.add_css_class(f'status-{status}')

    def set_connected(self, text: str = "● Connected"):
        self.set_text(text)
        self.set_status('connected')

    def set_disconnected(self, text: str = "● Disconnected"):
        self.set_text(text)
        self.set_status('disconnected')

    def set_warning(self, text: str = "● Warning"):
        self.set_text(text)
        self.set_status('warning')


class ColorPickerRow(Gtk.Box):
    """A horizontal row of color picker toggle buttons."""

    def __init__(self, selected_color: str = "blue",
                 colors: Optional[List[str]] = None,
                 on_change: Optional[Callable[[str], None]] = None):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        self.colors = colors or ACCENT_COLORS
        self.selected_color = selected_color
        self.on_change = on_change
        self.buttons: List[Gtk.ToggleButton] = []

        self._build_ui()

    def _build_ui(self):
        for color in self.colors:
            btn = Gtk.ToggleButton()
            btn.add_css_class('color-btn')
            btn.add_css_class(f'color-{color}')
            if color == self.selected_color:
                btn.set_active(True)
            btn.connect('toggled', self._on_color_selected, color)
            self.append(btn)
            self.buttons.append(btn)

    def _on_color_selected(self, button: Gtk.ToggleButton, color: str):
        if button.get_active():
            self.selected_color = color
            for btn in self.buttons:
                if btn != button:
                    btn.set_active(False)
            if self.on_change:
                self.on_change(color)

    def get_selected(self) -> str:
        return self.selected_color

    def set_selected(self, color: str):
        self.selected_color = color
        for i, c in enumerate(self.colors):
            self.buttons[i].set_active(c == color)


class EmojiPicker(Gtk.Box):
    """An emoji picker with categories."""

    DEFAULT_CATEGORIES = {
        "Media": ["🔴", "🎬", "📷", "🎥", "📺", "🎮", "🎧", "🎤", "🔊", "🔇"],
        "Lighting": ["💡", "🔆", "🌅", "☀️", "🌙", "✨", "🌟", "⚡", "🔥", "❄️"],
        "Actions": ["▶️", "⏸️", "⏹️", "⏺️", "⏭️", "⏮️", "🔄", "⬆️", "⬇️", "↩️"],
        "Symbols": ["⚙️", "🔧", "📁", "📂", "💾", "🗑️", "📋", "✏️", "🔍", "🔒"],
        "Misc": ["💬", "📱", "💻", "🖥️", "⌨️", "🖱️", "📡", "🎵", "🎶", "👏"],
    }

    def __init__(self, selected_emoji: str = "",
                 categories: Optional[Dict[str, List[str]]] = None,
                 on_change: Optional[Callable[[str], None]] = None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=16)

        self.categories = categories or self.DEFAULT_CATEGORIES
        self.selected_emoji = selected_emoji
        self.on_change = on_change
        self.buttons: List[Gtk.ToggleButton] = []

        self._build_ui()

    def _build_ui(self):
        for category, emojis in self.categories.items():
            cat_label = SectionLabel(category)
            self.append(cat_label)

            grid = Gtk.FlowBox()
            grid.set_max_children_per_line(10)
            grid.set_selection_mode(Gtk.SelectionMode.SINGLE)
            grid.add_css_class('icon-grid')
            self.append(grid)

            for emoji in emojis:
                btn = Gtk.ToggleButton(label=emoji)
                if emoji == self.selected_emoji:
                    btn.set_active(True)
                btn.connect('toggled', self._on_emoji_selected, emoji)
                grid.append(btn)
                self.buttons.append(btn)

    def _on_emoji_selected(self, button: Gtk.ToggleButton, emoji: str):
        if button.get_active():
            self.selected_emoji = emoji
            for btn in self.buttons:
                if btn != button:
                    btn.set_active(False)
            if self.on_change:
                self.on_change(emoji)

    def get_selected(self) -> str:
        return self.selected_emoji

    def clear_selection(self):
        """Deselect all emojis."""
        self.selected_emoji = ""
        for btn in self.buttons:
            btn.set_active(False)


class IconPicker(Gtk.Box):
    """A system icon picker with search."""

    DEFAULT_ICONS = [
        "camera-video-symbolic", "microphone-sensitivity-high-symbolic",
        "microphone-sensitivity-muted-symbolic", "audio-speakers-symbolic",
        "audio-volume-high-symbolic", "audio-volume-muted-symbolic",
        "video-display-symbolic", "preferences-desktop-display-symbolic",
        "weather-clear-symbolic", "weather-clear-night-symbolic",
        "media-playback-start-symbolic", "media-playback-pause-symbolic",
        "media-playback-stop-symbolic", "media-record-symbolic",
        "media-skip-forward-symbolic", "media-skip-backward-symbolic",
        "document-save-symbolic", "folder-symbolic",
        "applications-system-symbolic", "preferences-system-symbolic",
        "emblem-system-symbolic", "system-run-symbolic",
    ]

    def __init__(self, selected_icon: str = "",
                 icons: Optional[List[str]] = None,
                 on_change: Optional[Callable[[str], None]] = None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=12)

        self.icons = icons or self.DEFAULT_ICONS
        self.selected_icon = selected_icon
        self.on_change = on_change
        self.buttons: List[Gtk.ToggleButton] = []

        self._build_ui()

    def _build_ui(self):
        label = SectionLabel("System Icons")
        self.append(label)

        grid = Gtk.FlowBox()
        grid.set_max_children_per_line(8)
        grid.set_selection_mode(Gtk.SelectionMode.SINGLE)
        grid.add_css_class('icon-grid')
        self.append(grid)

        for icon_name in self.icons:
            btn = Gtk.ToggleButton()
            image = Gtk.Image.new_from_icon_name(icon_name)
            image.set_pixel_size(24)
            btn.set_child(image)
            btn.set_tooltip_text(icon_name)
            if icon_name == self.selected_icon:
                btn.set_active(True)
            btn.connect('toggled', self._on_icon_selected, icon_name)
            grid.append(btn)
            self.buttons.append(btn)

    def _on_icon_selected(self, button: Gtk.ToggleButton, icon_name: str):
        if button.get_active():
            self.selected_icon = icon_name
            for btn in self.buttons:
                if btn != button:
                    btn.set_active(False)
            if self.on_change:
                self.on_change(icon_name)

    def get_selected(self) -> str:
        return self.selected_icon

    def clear_selection(self):
        """Deselect all icons."""
        self.selected_icon = ""
        for btn in self.buttons:
            btn.set_active(False)


class PreviewButton(Gtk.Button):
    """A preview button that shows icon and label with color styling."""

    def __init__(self, icon: str = "", icon_type: str = "emoji",
                 label: str = "LABEL", color: str = "surface"):
        super().__init__()
        self.icon = icon
        self.icon_type = icon_type
        self.label_text = label
        self.color = color

        self.add_css_class('deck-button')
        self.add_css_class(f'btn-{color}')
        self.set_size_request(72, 72)
        self.set_sensitive(False)

        self._update_content()

    def _update_content(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        box.set_halign(Gtk.Align.CENTER)
        box.set_valign(Gtk.Align.CENTER)

        # Icon
        if self.icon_type == "emoji" or not self.icon_type:
            icon_widget = Gtk.Label(label=self.icon or "?")
            icon_widget.add_css_class('button-icon')
        elif self.icon_type == "icon_name":
            icon_widget = Gtk.Image.new_from_icon_name(
                self.icon or "dialog-question-symbolic"
            )
            icon_widget.set_pixel_size(28)
        else:  # file_path
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                    self.icon, 28, 28, True
                )
                icon_widget = Gtk.Image.new_from_pixbuf(pixbuf)
            except Exception:
                icon_widget = Gtk.Image.new_from_icon_name("dialog-question-symbolic")
                icon_widget.set_pixel_size(28)

        box.append(icon_widget)

        # Label
        label = Gtk.Label(label=self.label_text or "LABEL")
        label.add_css_class('button-label')
        text_color = COLORS['crust'] if needs_dark_text(self.color) else 'white'
        label.set_markup(f'<span foreground="{text_color}">{self.label_text or "LABEL"}</span>')
        box.append(label)

        self.set_child(box)

    def update(self, icon: Optional[str] = None, icon_type: Optional[str] = None,
               label: Optional[str] = None, color: Optional[str] = None):
        """Update the preview button properties."""
        if icon is not None:
            self.icon = icon
        if icon_type is not None:
            self.icon_type = icon_type
        if label is not None:
            self.label_text = label
        if color is not None:
            self.remove_css_class(f'btn-{self.color}')
            self.color = color
            self.add_css_class(f'btn-{color}')

        self._update_content()


class SliderRow(Gtk.Box):
    """A labeled slider with value display."""

    def __init__(self, label: str, min_val: float = 0, max_val: float = 100,
                 step: float = 1, value: float = 50,
                 format_func: Optional[Callable[[float], str]] = None,
                 on_change: Optional[Callable[[float], None]] = None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)

        self.format_func = format_func or (lambda v: f"{int(v)}")
        self.on_change = on_change

        # Header with label and value
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.append(header)

        label_widget = Gtk.Label(label=label)
        label_widget.add_css_class('slider-label')
        label_widget.set_hexpand(True)
        label_widget.set_halign(Gtk.Align.START)
        header.append(label_widget)

        self.value_label = Gtk.Label(label=self.format_func(value))
        self.value_label.add_css_class('slider-value')
        header.append(self.value_label)

        # Slider
        self.scale = Gtk.Scale.new_with_range(
            Gtk.Orientation.HORIZONTAL, min_val, max_val, step
        )
        self.scale.set_value(value)
        self.scale.set_draw_value(False)
        self.scale.connect('value-changed', self._on_value_changed)
        self.append(self.scale)

    def _on_value_changed(self, scale: Gtk.Scale):
        value = scale.get_value()
        self.value_label.set_text(self.format_func(value))
        if self.on_change:
            self.on_change(value)

    def get_value(self) -> float:
        return self.scale.get_value()

    def set_value(self, value: float, emit_signal: bool = True):
        if not emit_signal:
            self.scale.handler_block_by_func(self._on_value_changed)
        self.scale.set_value(value)
        self.value_label.set_text(self.format_func(value))
        if not emit_signal:
            self.scale.handler_unblock_by_func(self._on_value_changed)


class ActionRow(Gtk.Box):
    """A row with icon, title, subtitle, and action widget."""

    def __init__(self, icon: Optional[str] = None,
                 title: str = "",
                 subtitle: str = "",
                 action_widget: Optional[Gtk.Widget] = None):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.add_css_class('list-row')

        # Icon (optional)
        if icon:
            icon_label = Gtk.Label(label=icon)
            icon_label.set_size_request(24, -1)
            self.append(icon_label)

        # Title and subtitle
        text_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        text_box.set_hexpand(True)
        self.append(text_box)

        title_label = Gtk.Label(label=title)
        title_label.add_css_class('title')
        title_label.set_halign(Gtk.Align.START)
        text_box.append(title_label)

        if subtitle:
            subtitle_label = Gtk.Label(label=subtitle)
            subtitle_label.add_css_class('subtitle')
            subtitle_label.set_halign(Gtk.Align.START)
            text_box.append(subtitle_label)

        # Action widget (optional)
        if action_widget:
            self.append(action_widget)
