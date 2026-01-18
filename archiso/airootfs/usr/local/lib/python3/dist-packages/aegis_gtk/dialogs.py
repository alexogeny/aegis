"""
Aegis GTK Dialogs - Common dialog patterns for Aegis applications.
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio
from pathlib import Path
from typing import Optional, Callable, List


class ConfirmDialog:
    """A confirmation dialog with customizable actions."""

    def __init__(self, parent: Gtk.Window,
                 heading: str,
                 body: str,
                 confirm_label: str = "Confirm",
                 cancel_label: str = "Cancel",
                 destructive: bool = False,
                 on_confirm: Optional[Callable[[], None]] = None):
        self.on_confirm = on_confirm

        self.dialog = Adw.MessageDialog(
            transient_for=parent,
            heading=heading,
            body=body
        )
        self.dialog.add_response("cancel", cancel_label)
        self.dialog.add_response("confirm", confirm_label)

        if destructive:
            self.dialog.set_response_appearance(
                "confirm", Adw.ResponseAppearance.DESTRUCTIVE
            )
        else:
            self.dialog.set_response_appearance(
                "confirm", Adw.ResponseAppearance.SUGGESTED
            )

        self.dialog.connect('response', self._on_response)

    def _on_response(self, dialog: Adw.MessageDialog, response: str):
        if response == "confirm" and self.on_confirm:
            self.on_confirm()

    def present(self):
        self.dialog.present()


class InputDialog:
    """A dialog with a text input field."""

    def __init__(self, parent: Gtk.Window,
                 heading: str,
                 body: str = "",
                 placeholder: str = "",
                 initial_value: str = "",
                 confirm_label: str = "OK",
                 on_confirm: Optional[Callable[[str], None]] = None):
        self.on_confirm = on_confirm

        self.dialog = Adw.MessageDialog(
            transient_for=parent,
            heading=heading,
            body=body
        )

        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text(placeholder)
        self.entry.set_text(initial_value)
        self.dialog.set_extra_child(self.entry)

        self.dialog.add_response("cancel", "Cancel")
        self.dialog.add_response("confirm", confirm_label)
        self.dialog.set_response_appearance(
            "confirm", Adw.ResponseAppearance.SUGGESTED
        )

        self.dialog.connect('response', self._on_response)

    def _on_response(self, dialog: Adw.MessageDialog, response: str):
        if response == "confirm" and self.on_confirm:
            self.on_confirm(self.entry.get_text())

    def present(self):
        self.dialog.present()


class FileImportDialog:
    """A file chooser dialog for importing files."""

    def __init__(self, parent: Gtk.Window,
                 title: str = "Import",
                 patterns: Optional[List[str]] = None,
                 filter_name: str = "Files",
                 on_file_selected: Optional[Callable[[Path], None]] = None):
        self.on_file_selected = on_file_selected
        self.parent = parent

        self.dialog = Gtk.FileDialog()
        self.dialog.set_title(title)

        if patterns:
            file_filter = Gtk.FileFilter()
            for pattern in patterns:
                file_filter.add_pattern(pattern)
            file_filter.set_name(filter_name)

            filters = Gio.ListStore.new(Gtk.FileFilter)
            filters.append(file_filter)
            self.dialog.set_filters(filters)

    def present(self):
        self.dialog.open(self.parent, None, self._on_response)

    def _on_response(self, dialog: Gtk.FileDialog, result):
        try:
            file = dialog.open_finish(result)
            if file and self.on_file_selected:
                self.on_file_selected(Path(file.get_path()))
        except Exception:
            pass


class FileExportDialog:
    """A file chooser dialog for exporting files."""

    def __init__(self, parent: Gtk.Window,
                 title: str = "Export",
                 initial_name: str = "export.json",
                 on_file_selected: Optional[Callable[[Path], None]] = None):
        self.on_file_selected = on_file_selected
        self.parent = parent

        self.dialog = Gtk.FileDialog()
        self.dialog.set_title(title)
        self.dialog.set_initial_name(initial_name)

    def present(self):
        self.dialog.save(self.parent, None, self._on_response)

    def _on_response(self, dialog: Gtk.FileDialog, result):
        try:
            file = dialog.save_finish(result)
            if file and self.on_file_selected:
                self.on_file_selected(Path(file.get_path()))
        except Exception:
            pass


class IconPickerDialog(Adw.Window):
    """A dialog for selecting icons (emoji, system, or custom file)."""

    from .widgets import EmojiPicker, IconPicker

    def __init__(self, parent: Gtk.Window,
                 current_icon: str = "",
                 current_type: str = "emoji",
                 on_select: Optional[Callable[[str, str], None]] = None):
        super().__init__(transient_for=parent, modal=True)
        self.set_title("Choose Icon")
        self.set_default_size(450, 500)

        self.selected_icon = current_icon
        self.selected_type = current_type
        self.on_select = on_select

        self._build_ui()

    def _build_ui(self):
        from .widgets import EmojiPicker, IconPicker
        from .theme import COLORS, setup_css

        setup_css(self)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_content(main_box)

        # Header
        header = Adw.HeaderBar()
        header.add_css_class('header-bar')

        cancel_btn = Gtk.Button(label="Cancel")
        cancel_btn.connect('clicked', lambda b: self.close())
        header.pack_start(cancel_btn)

        select_btn = Gtk.Button(label="Select")
        select_btn.add_css_class('primary-button')
        select_btn.connect('clicked', self._on_select_clicked)
        header.pack_end(select_btn)

        main_box.append(header)

        # Notebook for tabs
        notebook = Gtk.Notebook()
        notebook.set_margin_top(16)
        notebook.set_margin_bottom(16)
        notebook.set_margin_start(16)
        notebook.set_margin_end(16)
        main_box.append(notebook)

        # Emoji tab
        emoji_scroll = Gtk.ScrolledWindow()
        emoji_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        emoji_scroll.set_vexpand(True)

        self.emoji_picker = EmojiPicker(
            selected_emoji=self.selected_icon if self.selected_type == "emoji" else "",
            on_change=self._on_emoji_change
        )
        self.emoji_picker.set_margin_all(12)
        emoji_scroll.set_child(self.emoji_picker)

        notebook.append_page(emoji_scroll, Gtk.Label(label="Emoji"))

        # System Icons tab
        icons_scroll = Gtk.ScrolledWindow()
        icons_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        icons_scroll.set_vexpand(True)

        self.icon_picker = IconPicker(
            selected_icon=self.selected_icon if self.selected_type == "icon_name" else "",
            on_change=self._on_icon_change
        )
        self.icon_picker.set_margin_all(12)
        icons_scroll.set_child(self.icon_picker)

        notebook.append_page(icons_scroll, Gtk.Label(label="System"))

        # Custom file tab
        file_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        file_box.set_margin_all(16)

        file_label = Gtk.Label(label="Custom Image")
        file_label.add_css_class('section-title')
        file_label.set_halign(Gtk.Align.START)
        file_box.append(file_label)

        file_hint = Gtk.Label(label="Select a PNG or SVG file from your computer")
        file_hint.add_css_class('subtitle')
        file_hint.set_halign(Gtk.Align.START)
        file_box.append(file_hint)

        self.file_path_label = Gtk.Label(label="No file selected")
        self.file_path_label.add_css_class('subtitle')
        self.file_path_label.set_margin_top(8)
        file_box.append(self.file_path_label)

        browse_btn = Gtk.Button(label="Browse...")
        browse_btn.add_css_class('primary-button')
        browse_btn.set_halign(Gtk.Align.START)
        browse_btn.connect('clicked', self._on_browse_file)
        file_box.append(browse_btn)

        # Preview
        self.file_preview = Gtk.Image()
        self.file_preview.set_pixel_size(48)
        self.file_preview.set_margin_top(16)
        file_box.append(self.file_preview)

        notebook.append_page(file_box, Gtk.Label(label="Custom"))

    def _on_emoji_change(self, emoji: str):
        self.selected_icon = emoji
        self.selected_type = "emoji"
        self.icon_picker.clear_selection()

    def _on_icon_change(self, icon_name: str):
        self.selected_icon = icon_name
        self.selected_type = "icon_name"
        self.emoji_picker.clear_selection()

    def _on_browse_file(self, button: Gtk.Button):
        dialog = Gtk.FileDialog()
        dialog.set_title("Select Icon Image")

        filter_images = Gtk.FileFilter()
        filter_images.add_mime_type("image/png")
        filter_images.add_mime_type("image/svg+xml")
        filter_images.set_name("Image files")

        filters = Gio.ListStore.new(Gtk.FileFilter)
        filters.append(filter_images)
        dialog.set_filters(filters)

        dialog.open(self, None, self._on_file_selected)

    def _on_file_selected(self, dialog: Gtk.FileDialog, result):
        try:
            from gi.repository import GdkPixbuf

            file = dialog.open_finish(result)
            if file:
                path = file.get_path()
                self.selected_icon = path
                self.selected_type = "file_path"
                self.file_path_label.set_text(Path(path).name)

                # Show preview
                try:
                    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(path, 48, 48, True)
                    self.file_preview.set_from_pixbuf(pixbuf)
                except Exception:
                    pass

                # Deselect other selections
                self.emoji_picker.clear_selection()
                self.icon_picker.clear_selection()
        except Exception:
            pass

    def _on_select_clicked(self, button: Gtk.Button):
        if self.selected_icon and self.on_select:
            self.on_select(self.selected_icon, self.selected_type)
        self.close()
