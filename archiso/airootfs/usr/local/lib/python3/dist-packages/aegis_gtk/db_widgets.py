"""
Database-specific widgets for aegis-dbview.

Provides enhanced UI components:
- SyntaxHighlightedEditor: SQL editor with Pygments syntax highlighting
- VirtualScrollingTable: Efficient display of large result sets
- EditableResultsTable: Inline data editing with confirmation dialogs
"""

import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib, Pango, Gdk
from typing import Any
from collections.abc import Callable
from dataclasses import dataclass

from .theme import COLORS

# SQL syntax highlighting colors (Catppuccin Mocha)
SQL_COLORS = {
    'keyword': COLORS['mauve'],  # SELECT, FROM, WHERE, etc.
    'function': COLORS['blue'],  # COUNT, SUM, MAX, etc.
    'string': COLORS['green'],  # 'string values'
    'number': COLORS['peach'],  # 123, 45.67
    'comment': COLORS['overlay0'],  # -- comments
    'operator': COLORS['sky'],  # =, <, >, AND, OR
    'identifier': COLORS['text'],  # column names
    'type': COLORS['yellow'],  # INTEGER, VARCHAR, etc.
}

# SQL keywords for highlighting
SQL_KEYWORDS = {
    'SELECT',
    'FROM',
    'WHERE',
    'AND',
    'OR',
    'NOT',
    'IN',
    'IS',
    'NULL',
    'LIKE',
    'BETWEEN',
    'JOIN',
    'LEFT',
    'RIGHT',
    'INNER',
    'OUTER',
    'FULL',
    'ON',
    'AS',
    'ORDER',
    'BY',
    'GROUP',
    'HAVING',
    'LIMIT',
    'OFFSET',
    'INSERT',
    'INTO',
    'VALUES',
    'UPDATE',
    'SET',
    'DELETE',
    'CREATE',
    'TABLE',
    'INDEX',
    'VIEW',
    'DROP',
    'ALTER',
    'ADD',
    'COLUMN',
    'PRIMARY',
    'KEY',
    'FOREIGN',
    'REFERENCES',
    'UNIQUE',
    'CHECK',
    'DEFAULT',
    'CONSTRAINT',
    'CASCADE',
    'DISTINCT',
    'ALL',
    'UNION',
    'EXCEPT',
    'INTERSECT',
    'CASE',
    'WHEN',
    'THEN',
    'ELSE',
    'END',
    'EXISTS',
    'ANY',
    'SOME',
    'TRUE',
    'FALSE',
    'ASC',
    'DESC',
    'NULLS',
    'FIRST',
    'LAST',
    'OVER',
    'PARTITION',
    'WINDOW',
    'WITH',
    'RECURSIVE',
    'RETURNING',
    'CONFLICT',
    'DO',
    'NOTHING',
    'EXCLUDED',
}

SQL_FUNCTIONS = {
    'COUNT',
    'SUM',
    'AVG',
    'MIN',
    'MAX',
    'COALESCE',
    'NULLIF',
    'CAST',
    'CONVERT',
    'SUBSTRING',
    'TRIM',
    'UPPER',
    'LOWER',
    'LENGTH',
    'CONCAT',
    'REPLACE',
    'NOW',
    'CURRENT_DATE',
    'CURRENT_TIME',
    'CURRENT_TIMESTAMP',
    'DATE',
    'TIME',
    'EXTRACT',
    'ROUND',
    'FLOOR',
    'CEIL',
    'ABS',
    'MOD',
    'POWER',
    'SQRT',
    'ROW_NUMBER',
    'RANK',
    'DENSE_RANK',
    'LAG',
    'LEAD',
    'FIRST_VALUE',
    'LAST_VALUE',
    'NTH_VALUE',
    'ARRAY_AGG',
    'STRING_AGG',
    'JSON_AGG',
}

SQL_TYPES = {
    'INTEGER',
    'INT',
    'SMALLINT',
    'BIGINT',
    'SERIAL',
    'BIGSERIAL',
    'REAL',
    'DOUBLE',
    'PRECISION',
    'NUMERIC',
    'DECIMAL',
    'FLOAT',
    'BOOLEAN',
    'BOOL',
    'TEXT',
    'VARCHAR',
    'CHAR',
    'CHARACTER',
    'DATE',
    'TIME',
    'TIMESTAMP',
    'TIMESTAMPTZ',
    'INTERVAL',
    'UUID',
    'JSON',
    'JSONB',
    'ARRAY',
    'BYTEA',
    'BLOB',
}

SQL_OPERATORS = {'=', '<', '>', '<=', '>=', '<>', '!=', '+', '-', '*', '/', '%'}


class SyntaxHighlightedEditor(Gtk.Box):
    """SQL editor with syntax highlighting and line numbers."""

    def __init__(self, on_run: Callable[[str], None] | None = None):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)

        self.on_run = on_run
        self._updating = False

        # Line numbers column
        self.line_numbers = Gtk.TextView()
        self.line_numbers.set_editable(False)
        self.line_numbers.set_cursor_visible(False)
        self.line_numbers.set_monospace(True)
        self.line_numbers.set_right_margin(8)
        self.line_numbers.set_left_margin(8)
        self.line_numbers.add_css_class('line-numbers')
        self.line_numbers.set_size_request(50, -1)

        line_scroll = Gtk.ScrolledWindow()
        line_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.EXTERNAL)
        line_scroll.set_child(self.line_numbers)
        self.append(line_scroll)

        # Main editor
        self.editor = Gtk.TextView()
        self.editor.set_monospace(True)
        self.editor.set_wrap_mode(Gtk.WrapMode.NONE)
        self.editor.set_left_margin(12)
        self.editor.set_right_margin(12)
        self.editor.set_top_margin(8)
        self.editor.set_bottom_margin(8)
        self.editor.add_css_class('syntax-editor')

        editor_scroll = Gtk.ScrolledWindow()
        editor_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        editor_scroll.set_child(self.editor)
        editor_scroll.set_hexpand(True)
        editor_scroll.set_vexpand(True)
        self.append(editor_scroll)

        # Sync scrolling
        editor_vadj = editor_scroll.get_vadjustment()
        line_vadj = line_scroll.get_vadjustment()
        editor_vadj.connect('value-changed', lambda a: line_vadj.set_value(a.get_value()))

        # Setup text tags for syntax highlighting
        self.buffer = self.editor.get_buffer()
        self._setup_tags()

        # Connect signals
        self.buffer.connect('changed', self._on_text_changed)

        # Keyboard shortcut for run (Ctrl+Enter)
        key_controller = Gtk.EventControllerKey()
        key_controller.connect('key-pressed', self._on_key_pressed)
        self.editor.add_controller(key_controller)

        # Initial line numbers
        self._update_line_numbers()

    def _setup_tags(self):
        """Create text tags for syntax highlighting."""
        tag_table = self.buffer.get_tag_table()

        # Keyword tag
        tag = Gtk.TextTag(name='keyword')
        tag.set_property('foreground', SQL_COLORS['keyword'])
        tag.set_property('weight', Pango.Weight.BOLD)
        tag_table.add(tag)

        # Function tag
        tag = Gtk.TextTag(name='function')
        tag.set_property('foreground', SQL_COLORS['function'])
        tag_table.add(tag)

        # String tag
        tag = Gtk.TextTag(name='string')
        tag.set_property('foreground', SQL_COLORS['string'])
        tag_table.add(tag)

        # Number tag
        tag = Gtk.TextTag(name='number')
        tag.set_property('foreground', SQL_COLORS['number'])
        tag_table.add(tag)

        # Comment tag
        tag = Gtk.TextTag(name='comment')
        tag.set_property('foreground', SQL_COLORS['comment'])
        tag.set_property('style', Pango.Style.ITALIC)
        tag_table.add(tag)

        # Operator tag
        tag = Gtk.TextTag(name='operator')
        tag.set_property('foreground', SQL_COLORS['operator'])
        tag_table.add(tag)

        # Type tag
        tag = Gtk.TextTag(name='type')
        tag.set_property('foreground', SQL_COLORS['type'])
        tag_table.add(tag)

    def _on_text_changed(self, buffer):
        """Handle text changes - update highlighting and line numbers."""
        if self._updating:
            return

        self._updating = True
        GLib.idle_add(self._apply_highlighting)
        self._update_line_numbers()
        self._updating = False

    def _apply_highlighting(self):
        """Apply syntax highlighting to the buffer."""
        # Remove all existing tags
        start, end = self.buffer.get_bounds()
        self.buffer.remove_all_tags(start, end)

        text = self.buffer.get_text(start, end, False)
        if not text:
            return

        # Tokenize and highlight
        self._highlight_comments(text)
        self._highlight_strings(text)
        self._highlight_numbers(text)
        self._highlight_words(text)

    def _highlight_comments(self, text: str):
        """Highlight SQL comments."""
        import re

        # Single-line comments
        for match in re.finditer(r'--[^\n]*', text):
            start_iter = self.buffer.get_iter_at_offset(match.start())
            end_iter = self.buffer.get_iter_at_offset(match.end())
            self.buffer.apply_tag_by_name('comment', start_iter, end_iter)

        # Multi-line comments
        for match in re.finditer(r'/\*.*?\*/', text, re.DOTALL):
            start_iter = self.buffer.get_iter_at_offset(match.start())
            end_iter = self.buffer.get_iter_at_offset(match.end())
            self.buffer.apply_tag_by_name('comment', start_iter, end_iter)

    def _highlight_strings(self, text: str):
        """Highlight string literals."""
        import re

        for match in re.finditer(r"'(?:[^'\\]|\\.)*'", text):
            start_iter = self.buffer.get_iter_at_offset(match.start())
            end_iter = self.buffer.get_iter_at_offset(match.end())
            self.buffer.apply_tag_by_name('string', start_iter, end_iter)

    def _highlight_numbers(self, text: str):
        """Highlight numeric literals."""
        import re

        for match in re.finditer(r'\b\d+\.?\d*\b', text):
            start_iter = self.buffer.get_iter_at_offset(match.start())
            end_iter = self.buffer.get_iter_at_offset(match.end())
            # Don't highlight if inside a string or comment
            if not start_iter.has_tag(self.buffer.get_tag_table().lookup('string')):
                if not start_iter.has_tag(self.buffer.get_tag_table().lookup('comment')):
                    self.buffer.apply_tag_by_name('number', start_iter, end_iter)

    def _highlight_words(self, text: str):
        """Highlight keywords, functions, and types."""
        import re

        for match in re.finditer(r'\b[A-Za-z_][A-Za-z0-9_]*\b', text):
            word = match.group().upper()
            start_iter = self.buffer.get_iter_at_offset(match.start())
            end_iter = self.buffer.get_iter_at_offset(match.end())

            # Skip if already tagged (string, comment, number)
            if start_iter.has_tag(self.buffer.get_tag_table().lookup('string')):
                continue
            if start_iter.has_tag(self.buffer.get_tag_table().lookup('comment')):
                continue

            if word in SQL_KEYWORDS:
                self.buffer.apply_tag_by_name('keyword', start_iter, end_iter)
            elif word in SQL_FUNCTIONS:
                self.buffer.apply_tag_by_name('function', start_iter, end_iter)
            elif word in SQL_TYPES:
                self.buffer.apply_tag_by_name('type', start_iter, end_iter)

    def _update_line_numbers(self):
        """Update line numbers display."""
        text = self.get_text()
        line_count = max(1, text.count('\n') + 1)
        lines = '\n'.join(str(i) for i in range(1, line_count + 1))

        line_buffer = self.line_numbers.get_buffer()
        line_buffer.set_text(lines)

    def _on_key_pressed(self, controller, keyval, keycode, state):
        """Handle key presses."""
        # Ctrl+Enter to run query
        if keyval == Gdk.KEY_Return and (state & Gdk.ModifierType.CONTROL_MASK):
            if self.on_run:
                self.on_run(self.get_text())
            return True
        return False

    def get_text(self) -> str:
        """Get the editor content."""
        start, end = self.buffer.get_bounds()
        return self.buffer.get_text(start, end, False)

    def set_text(self, text: str):
        """Set the editor content."""
        self.buffer.set_text(text)

    def get_buffer(self) -> Gtk.TextBuffer:
        """Get the underlying text buffer."""
        return self.buffer


@dataclass
class VirtualRow:
    """Represents a row in the virtual table."""

    index: int
    data: tuple
    widget: Gtk.Box | None = None


class VirtualScrollingTable(Gtk.Box):
    """
    Efficient table display with virtual scrolling.
    Only renders visible rows for performance with large datasets.
    """

    ROW_HEIGHT = 32
    BUFFER_ROWS = 10  # Extra rows to render above/below viewport

    def __init__(
        self,
        on_cell_edit: Callable[[int, int, Any, Any], None] | None = None,
        on_row_click: Callable[[int, tuple], None] | None = None,
        editable: bool = False,
    ):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        self.columns: list = []
        self.rows: list[tuple] = []
        self.on_cell_edit = on_cell_edit
        self.on_row_click = on_row_click
        self.editable = editable
        self._visible_range = (0, 0)
        self._row_widgets: dict[int, Gtk.Box] = {}
        self._editing_cell: tuple[int, int] | None = None
        self._selected_row: int | None = None

        # Header
        self.header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.header_box.add_css_class('results-header-row')
        self.append(self.header_box)

        # Scrolled content area
        self.scroll = Gtk.ScrolledWindow()
        self.scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.scroll.set_vexpand(True)
        self.append(self.scroll)

        # Container for rows (with fixed height based on data)
        self.rows_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.scroll.set_child(self.rows_container)

        # Viewport for detecting scroll position
        self.scroll.get_vadjustment().connect('value-changed', self._on_scroll)

    def set_data(self, columns: list, rows: list[tuple]):
        """Set the table data."""
        self.columns = columns
        self.rows = rows
        self._row_widgets.clear()

        # Build header
        self._build_header()

        # Set container height
        total_height = len(rows) * self.ROW_HEIGHT
        self.rows_container.set_size_request(-1, total_height)

        # Clear and render visible rows
        self._clear_rows()
        self._update_visible_rows()

    def _build_header(self):
        """Build the header row."""
        # Clear existing
        while True:
            child = self.header_box.get_first_child()
            if child is None:
                break
            self.header_box.remove(child)

        for col in self.columns:
            header = Gtk.Label(label=col.name if hasattr(col, 'name') else str(col))
            header.add_css_class('results-header')
            header.set_halign(Gtk.Align.START)
            header.set_hexpand(True)
            header.set_size_request(120, -1)
            self.header_box.append(header)

    def _clear_rows(self):
        """Clear all row widgets."""
        while True:
            child = self.rows_container.get_first_child()
            if child is None:
                break
            self.rows_container.remove(child)

    def _on_scroll(self, adjustment):
        """Handle scroll events to update visible rows."""
        self._update_visible_rows()

    def _update_visible_rows(self):
        """Update which rows are rendered based on scroll position."""
        if not self.rows:
            return

        # Calculate visible range
        vadj = self.scroll.get_vadjustment()
        scroll_top = vadj.get_value()
        viewport_height = vadj.get_page_size()

        first_visible = max(0, int(scroll_top / self.ROW_HEIGHT) - self.BUFFER_ROWS)
        last_visible = min(len(self.rows), int((scroll_top + viewport_height) / self.ROW_HEIGHT) + self.BUFFER_ROWS)

        new_range = (first_visible, last_visible)

        if new_range == self._visible_range:
            return

        self._visible_range = new_range

        # Remove rows outside visible range
        rows_to_remove = [idx for idx in self._row_widgets if idx < first_visible or idx >= last_visible]
        for idx in rows_to_remove:
            widget = self._row_widgets.pop(idx)
            self.rows_container.remove(widget)

        # Add rows inside visible range
        for idx in range(first_visible, last_visible):
            if idx not in self._row_widgets:
                self._create_row_widget(idx)

        # Re-sort children by index
        self._sort_row_widgets()

    def _create_row_widget(self, row_idx: int):
        """Create a widget for a single row."""
        if row_idx >= len(self.rows):
            return

        row_data = self.rows[row_idx]

        row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        row_box.set_size_request(-1, self.ROW_HEIGHT)
        row_box.add_css_class('results-row')
        if row_idx % 2 == 1:
            row_box.add_css_class('results-row-alt')
        if self._selected_row == row_idx:
            row_box.add_css_class('results-row-selected')

        # Position row absolutely
        row_box.set_margin_top(row_idx * self.ROW_HEIGHT)

        # Add row click handler
        row_click = Gtk.GestureClick()
        row_click.set_button(1)
        row_click.connect('released', self._on_row_clicked, row_idx)
        row_box.add_controller(row_click)

        for col_idx, value in enumerate(row_data):
            cell = self._create_cell(row_idx, col_idx, value)
            row_box.append(cell)

        self._row_widgets[row_idx] = row_box
        self.rows_container.append(row_box)

    def _create_cell(self, row_idx: int, col_idx: int, value: Any) -> Gtk.Widget:
        """Create a cell widget."""
        cell_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        cell_box.set_hexpand(True)
        cell_box.set_size_request(120, -1)
        cell_box.add_css_class('results-cell')

        if value is None:
            label = Gtk.Label(label='NULL')
            label.add_css_class('null')
        else:
            cell_text = str(value)
            if len(cell_text) > 50:
                cell_text = cell_text[:47] + '...'
            label = Gtk.Label(label=cell_text)

        label.set_halign(Gtk.Align.START)
        label.set_selectable(True)
        cell_box.append(label)

        # Make editable if enabled
        if self.editable:
            click = Gtk.GestureClick()
            click.set_button(1)
            click.connect('released', self._on_cell_clicked, row_idx, col_idx, value)
            cell_box.add_controller(click)
            cell_box.add_css_class('editable-cell')

        return cell_box

    def _on_cell_clicked(self, gesture, n_press, x, y, row_idx, col_idx, value):
        """Handle cell click for editing."""
        if n_press == 2 and self.editable:  # Double-click
            self._start_editing(row_idx, col_idx, value)

    def _start_editing(self, row_idx: int, col_idx: int, current_value: Any):
        """Start inline editing of a cell."""
        if self._editing_cell is not None:
            return

        self._editing_cell = (row_idx, col_idx)

        # Find the cell widget
        row_widget = self._row_widgets.get(row_idx)
        if not row_widget:
            return

        cell = row_widget.get_first_child()
        for _ in range(col_idx):
            if cell:
                cell = cell.get_next_sibling()

        if not cell:
            return

        # Replace label with entry
        label = cell.get_first_child()
        if label:
            cell.remove(label)

        entry = Gtk.Entry()
        entry.set_text('' if current_value is None else str(current_value))
        entry.set_hexpand(True)
        entry.add_css_class('cell-edit-entry')

        # Handle focus out and enter key
        entry.connect('activate', self._on_edit_complete, row_idx, col_idx, current_value)

        focus_controller = Gtk.EventControllerFocus()
        focus_controller.connect('leave', self._on_edit_focus_lost, row_idx, col_idx, current_value, entry)
        entry.add_controller(focus_controller)

        cell.append(entry)
        entry.grab_focus()

    def _on_edit_complete(self, entry, row_idx, col_idx, original_value):
        """Handle edit completion."""
        new_value = entry.get_text()
        self._finish_editing(row_idx, col_idx, original_value, new_value)

    def _on_edit_focus_lost(self, controller, row_idx, col_idx, original_value, entry):
        """Handle focus lost during editing."""
        new_value = entry.get_text()
        self._finish_editing(row_idx, col_idx, original_value, new_value)

    def _finish_editing(self, row_idx: int, col_idx: int, original_value: Any, new_value: str):
        """Complete the editing process."""
        if self._editing_cell != (row_idx, col_idx):
            return

        self._editing_cell = None

        # Update the cell display
        row_widget = self._row_widgets.get(row_idx)
        if row_widget:
            cell = row_widget.get_first_child()
            for _ in range(col_idx):
                if cell:
                    cell = cell.get_next_sibling()

            if cell:
                # Remove entry
                entry = cell.get_first_child()
                if entry:
                    cell.remove(entry)

                # Add label back
                display_value = new_value if new_value else 'NULL'
                label = Gtk.Label(label=display_value)
                if not new_value:
                    label.add_css_class('null')
                label.set_halign(Gtk.Align.START)
                label.set_selectable(True)
                cell.append(label)

        # Notify callback if value changed
        str_original = '' if original_value is None else str(original_value)
        if new_value != str_original and self.on_cell_edit:
            self.on_cell_edit(row_idx, col_idx, original_value, new_value)

    def _sort_row_widgets(self):
        """Sort row widgets by their index."""
        # GTK4 doesn't have direct reordering, widgets are already positioned by margin
        pass

    def set_editable(self, editable: bool):
        """Enable or disable inline cell editing."""
        self.editable = editable
        # Refresh visible rows to update cell click handlers
        if self.rows:
            old_range = self._visible_range
            self._visible_range = (0, 0)  # Force refresh
            self._row_widgets.clear()
            self._clear_rows()
            self._visible_range = old_range
            self._update_visible_rows()

    def _on_row_clicked(self, gesture, n_press, x, y, row_idx: int):
        """Handle row click - select row and notify callback."""
        if n_press == 1:
            self.select_row(row_idx)
            if self.on_row_click and row_idx < len(self.rows):
                self.on_row_click(row_idx, self.rows[row_idx])

    def select_row(self, row_idx: int | None):
        """Select a row visually."""
        # Deselect previous row
        if self._selected_row is not None and self._selected_row in self._row_widgets:
            self._row_widgets[self._selected_row].remove_css_class('results-row-selected')

        self._selected_row = row_idx

        # Select new row
        if row_idx is not None and row_idx in self._row_widgets:
            self._row_widgets[row_idx].add_css_class('results-row-selected')

    def get_selected_row(self) -> tuple[int, tuple] | None:
        """Get the currently selected row index and data."""
        if self._selected_row is not None and self._selected_row < len(self.rows):
            return (self._selected_row, self.rows[self._selected_row])
        return None


class EditConfirmDialog(Adw.Window):
    """Dialog to confirm data edits before execution."""

    def __init__(
        self,
        parent: Gtk.Window,
        changes: list[dict],
        on_confirm: Callable[[], None] | None = None,
        on_cancel: Callable[[], None] | None = None,
        operation: str = 'UPDATE',
        table_name: str = 'data',
    ):
        super().__init__(transient_for=parent, modal=True)
        self.set_title('Confirm Changes')
        self.set_default_size(500, 400)

        self.on_confirm = on_confirm
        self.on_cancel = on_cancel
        self.changes = changes

        self._build_ui(operation, table_name)

    def _build_ui(self, operation: str, table_name: str):
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_content(main_box)

        # Header
        header = Adw.HeaderBar()
        header.add_css_class('header-bar')

        cancel_btn = Gtk.Button(label='Cancel')
        cancel_btn.connect('clicked', self._on_cancel)
        header.pack_start(cancel_btn)

        confirm_btn = Gtk.Button(label='Execute')
        confirm_btn.add_css_class('destructive-action')
        confirm_btn.connect('clicked', self._on_confirm)
        header.pack_end(confirm_btn)

        main_box.append(header)

        # Content
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        content.set_margin_start(24)
        content.set_margin_end(24)
        content.set_margin_top(24)
        content.set_margin_bottom(24)
        main_box.append(content)

        # Warning icon and message
        warning_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        content.append(warning_box)

        warning_icon = Gtk.Label(label='⚠️')
        warning_icon.set_markup('<span size="xx-large">⚠️</span>')
        warning_box.append(warning_icon)

        warning_text = Gtk.Label()
        warning_text.set_markup(
            f'<b>You are about to {operation} {len(self.changes)} cell(s)</b>\n'
            f'<span size="small">in <b>{table_name}</b></span>'
        )
        warning_text.set_halign(Gtk.Align.START)
        warning_box.append(warning_text)

        # Changes preview
        changes_label = Gtk.Label(label='Changes:')
        changes_label.add_css_class('section-title')
        changes_label.set_halign(Gtk.Align.START)
        changes_label.set_margin_top(16)
        content.append(changes_label)

        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_min_content_height(150)
        content.append(scroll)

        changes_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        scroll.set_child(changes_box)

        for change in self.changes[:10]:  # Show max 10 changes
            change_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            change_row.add_css_class('change-row')

            col_label = Gtk.Label(label=change.get('column', ''))
            col_label.add_css_class('change-column')
            col_label.set_size_request(100, -1)
            change_row.append(col_label)

            old_val = Gtk.Label(label=str(change.get('old_value', 'NULL')))
            old_val.add_css_class('change-old')
            change_row.append(old_val)

            arrow = Gtk.Label(label='→')
            change_row.append(arrow)

            new_val = Gtk.Label(label=str(change.get('new_value', 'NULL')))
            new_val.add_css_class('change-new')
            change_row.append(new_val)

            changes_box.append(change_row)

        if len(self.changes) > 10:
            more = Gtk.Label(label=f'... and {len(self.changes) - 10} more changes')
            more.add_css_class('subtitle')
            changes_box.append(more)

        # Warning message
        warning_footer = Gtk.Label(label='This action cannot be undone.')
        warning_footer.add_css_class('warning-text')
        warning_footer.set_margin_top(16)
        content.append(warning_footer)

    def _on_confirm(self, button):
        if self.on_confirm:
            self.on_confirm()
        self.close()

    def _on_cancel(self, button):
        if self.on_cancel:
            self.on_cancel()
        self.close()


@dataclass
class SchemaNode:
    """Represents a node in the schema tree."""

    name: str
    node_type: str  # 'schema', 'table', 'column', 'index', 'view'
    children: list['SchemaNode'] | None = None
    metadata: dict | None = None  # Additional info like data type, nullable, etc.


class SchemaTree(Gtk.Box):
    """
    Tree-style browser for database schemas, tables, and columns.
    Supports expanding/collapsing nodes and selection callbacks.
    """

    def __init__(
        self,
        on_select: Callable[[SchemaNode], None] | None = None,
        on_activate: Callable[[SchemaNode], None] | None = None,
    ):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        self.on_select = on_select  # Single click
        self.on_activate = on_activate  # Double click
        self._expanded_nodes: set[str] = set()
        self._selected_path: str | None = None
        self._nodes: dict[str, SchemaNode] = {}

        # Search/filter entry
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text('Filter tables...')
        self.search_entry.add_css_class('schema-search')
        self.search_entry.connect('search-changed', self._on_search_changed)
        self.append(self.search_entry)

        # Scrollable tree area
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.set_vexpand(True)
        self.append(scroll)

        self.tree_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.tree_box.add_css_class('schema-tree')
        scroll.set_child(self.tree_box)

        self._filter_text = ''

    def set_schema(self, schemas: list[SchemaNode]):
        """Set the schema data and rebuild the tree."""
        self._nodes.clear()
        self._clear_tree()

        for schema in schemas:
            self._add_schema_node(schema, '', 0)

    def _add_schema_node(self, node: SchemaNode, parent_path: str, level: int):
        """Recursively add a node to the tree."""
        path = f'{parent_path}/{node.name}' if parent_path else node.name
        self._nodes[path] = node

        # Check filter
        if self._filter_text and not self._matches_filter(node):
            return

        # Create row widget
        row = self._create_tree_row(node, path, level)
        self.tree_box.append(row)

        # Add children if expanded
        if node.children and path in self._expanded_nodes:
            for child in node.children:
                self._add_schema_node(child, path, level + 1)

    def _matches_filter(self, node: SchemaNode) -> bool:
        """Check if a node matches the current filter."""
        if self._filter_text.lower() in node.name.lower():
            return True
        if node.children:
            return any(self._matches_filter(child) for child in node.children)
        return False

    def _create_tree_row(self, node: SchemaNode, path: str, level: int) -> Gtk.Box:
        """Create a single tree row widget."""
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        row.add_css_class('schema-row')
        row.set_margin_start(level * 20 + 8)
        row.set_margin_end(8)
        row.set_margin_top(2)
        row.set_margin_bottom(2)

        if path == self._selected_path:
            row.add_css_class('schema-row-selected')

        # Expand/collapse button for nodes with children
        if node.children:
            expand_btn = Gtk.Button()
            expand_btn.add_css_class('flat')
            expand_btn.add_css_class('expand-btn')
            is_expanded = path in self._expanded_nodes
            expand_btn.set_label('▼' if is_expanded else '▶')
            expand_btn.connect('clicked', self._on_expand_clicked, path)
            row.append(expand_btn)
        else:
            # Spacer
            spacer = Gtk.Label(label='  ')
            row.append(spacer)

        # Icon based on type
        icon = self._get_node_icon(node.node_type)
        icon_label = Gtk.Label(label=icon)
        icon_label.add_css_class(f'schema-icon-{node.node_type}')
        row.append(icon_label)

        # Name label
        name_label = Gtk.Label(label=node.name)
        name_label.set_halign(Gtk.Align.START)
        name_label.set_hexpand(True)
        name_label.add_css_class('schema-name')
        row.append(name_label)

        # Metadata badge (e.g., row count, data type)
        if node.metadata:
            if 'row_count' in node.metadata:
                badge = Gtk.Label(label=f'{node.metadata["row_count"]:,}')
                badge.add_css_class('schema-badge')
                row.append(badge)
            elif 'data_type' in node.metadata:
                type_label = Gtk.Label(label=node.metadata['data_type'])
                type_label.add_css_class('schema-type')
                row.append(type_label)

        # Click handlers
        click = Gtk.GestureClick()
        click.set_button(1)
        click.connect('released', self._on_row_clicked, path, node)
        row.add_controller(click)

        return row

    def _get_node_icon(self, node_type: str) -> str:
        """Get icon for a node type."""
        icons = {
            'schema': '📁',
            'table': '🗃️',
            'view': '👁️',
            'column': '📊',
            'index': '🔑',
            'pk': '🔑',  # Primary key
            'fk': '🔗',  # Foreign key
        }
        return icons.get(node_type, '📄')

    def _on_expand_clicked(self, button, path: str):
        """Handle expand/collapse button click."""
        if path in self._expanded_nodes:
            self._expanded_nodes.remove(path)
        else:
            self._expanded_nodes.add(path)
        self._rebuild_tree()

    def _on_row_clicked(self, gesture, n_press, x, y, path: str, node: SchemaNode):
        """Handle row click."""
        self._selected_path = path
        self._rebuild_tree()

        if n_press == 1 and self.on_select:
            self.on_select(node)
        elif n_press == 2 and self.on_activate:
            self.on_activate(node)

    def _on_search_changed(self, entry):
        """Handle search text change."""
        self._filter_text = entry.get_text()
        self._rebuild_tree()

    def _clear_tree(self):
        """Remove all tree rows."""
        while True:
            child = self.tree_box.get_first_child()
            if child is None:
                break
            self.tree_box.remove(child)

    def _rebuild_tree(self):
        """Rebuild the tree from stored nodes."""
        self._clear_tree()
        # Re-add root nodes
        for path, node in self._nodes.items():
            if '/' not in path:  # Root level
                self._add_schema_node(node, '', 0)

    def expand_all(self):
        """Expand all nodes."""
        for path in self._nodes:
            self._expanded_nodes.add(path)
        self._rebuild_tree()

    def collapse_all(self):
        """Collapse all nodes."""
        self._expanded_nodes.clear()
        self._rebuild_tree()

    def select_node(self, path: str):
        """Programmatically select a node."""
        self._selected_path = path
        self._rebuild_tree()
        if path in self._nodes and self.on_select:
            self.on_select(self._nodes[path])


class EntityView(Gtk.Box):
    """
    Detailed view of a database entity (table, view, column).
    Shows metadata, structure, and quick actions.
    """

    def __init__(
        self,
        on_query: Callable[[str], None] | None = None,
    ):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add_css_class('entity-view')

        self.on_query = on_query
        self._current_node: SchemaNode | None = None

        # Header
        self.header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.header_box.add_css_class('entity-header')
        self.header_box.set_margin_start(16)
        self.header_box.set_margin_end(16)
        self.header_box.set_margin_top(16)
        self.header_box.set_margin_bottom(8)
        self.append(self.header_box)

        self.icon_label = Gtk.Label(label='🗃️')
        self.icon_label.add_css_class('entity-icon')
        self.header_box.append(self.icon_label)

        self.title_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        self.header_box.append(self.title_box)

        self.title_label = Gtk.Label(label='Select an entity')
        self.title_label.set_halign(Gtk.Align.START)
        self.title_label.add_css_class('entity-title')
        self.title_box.append(self.title_label)

        self.subtitle_label = Gtk.Label(label='')
        self.subtitle_label.set_halign(Gtk.Align.START)
        self.subtitle_label.add_css_class('entity-subtitle')
        self.title_box.append(self.subtitle_label)

        # Quick actions
        self.actions_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.actions_box.set_halign(Gtk.Align.END)
        self.actions_box.set_hexpand(True)
        self.header_box.append(self.actions_box)

        # Content area
        self.content_scroll = Gtk.ScrolledWindow()
        self.content_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.content_scroll.set_vexpand(True)
        self.append(self.content_scroll)

        self.content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.content_box.set_margin_start(16)
        self.content_box.set_margin_end(16)
        self.content_box.set_margin_top(8)
        self.content_box.set_margin_bottom(16)
        self.content_scroll.set_child(self.content_box)

    def show_entity(self, node: SchemaNode):
        """Display information about an entity."""
        self._current_node = node

        # Update header
        icons = {
            'schema': '📁',
            'table': '🗃️',
            'view': '👁️',
            'column': '📊',
            'index': '🔑',
        }
        self.icon_label.set_label(icons.get(node.node_type, '📄'))
        self.title_label.set_label(node.name)
        self.subtitle_label.set_label(node.node_type.title())

        # Clear actions
        while True:
            child = self.actions_box.get_first_child()
            if child is None:
                break
            self.actions_box.remove(child)

        # Clear content
        while True:
            child = self.content_box.get_first_child()
            if child is None:
                break
            self.content_box.remove(child)

        # Build view based on type
        if node.node_type == 'table':
            self._build_table_view(node)
        elif node.node_type == 'view':
            self._build_view_view(node)
        elif node.node_type == 'column':
            self._build_column_view(node)
        elif node.node_type == 'schema':
            self._build_schema_view(node)

    def _build_table_view(self, node: SchemaNode):
        """Build the view for a table."""
        # Quick actions
        select_btn = Gtk.Button(label='SELECT *')
        select_btn.add_css_class('suggested-action')
        select_btn.connect('clicked', self._on_select_all, node.name)
        self.actions_box.append(select_btn)

        count_btn = Gtk.Button(label='COUNT')
        count_btn.connect('clicked', self._on_count, node.name)
        self.actions_box.append(count_btn)

        # Metadata section
        if node.metadata:
            meta_group = self._create_info_group('Table Info')
            self.content_box.append(meta_group)

            if 'row_count' in node.metadata:
                self._add_info_row(meta_group, 'Rows', f'{node.metadata["row_count"]:,}')
            if 'size' in node.metadata:
                self._add_info_row(meta_group, 'Size', node.metadata['size'])
            if 'schema' in node.metadata:
                self._add_info_row(meta_group, 'Schema', node.metadata['schema'])

        # Columns section
        if node.children:
            columns = [c for c in node.children if c.node_type == 'column']
            if columns:
                col_group = self._create_info_group(f'Columns ({len(columns)})')
                self.content_box.append(col_group)

                for col in columns:
                    col_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
                    col_row.add_css_class('entity-column-row')

                    # Icon for keys
                    if col.metadata and col.metadata.get('is_pk'):
                        icon = Gtk.Label(label='🔑')
                    elif col.metadata and col.metadata.get('is_fk'):
                        icon = Gtk.Label(label='🔗')
                    else:
                        icon = Gtk.Label(label='  ')
                    col_row.append(icon)

                    name = Gtk.Label(label=col.name)
                    name.set_halign(Gtk.Align.START)
                    name.set_hexpand(True)
                    name.add_css_class('entity-column-name')
                    col_row.append(name)

                    if col.metadata and 'data_type' in col.metadata:
                        dtype = Gtk.Label(label=col.metadata['data_type'])
                        dtype.add_css_class('entity-column-type')
                        col_row.append(dtype)

                    if col.metadata and col.metadata.get('nullable') is False:
                        not_null = Gtk.Label(label='NOT NULL')
                        not_null.add_css_class('entity-column-constraint')
                        col_row.append(not_null)

                    col_group.append(col_row)

            # Indexes
            indexes = [c for c in node.children if c.node_type == 'index']
            if indexes:
                idx_group = self._create_info_group(f'Indexes ({len(indexes)})')
                self.content_box.append(idx_group)

                for idx in indexes:
                    idx_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
                    idx_row.add_css_class('entity-index-row')

                    name = Gtk.Label(label=idx.name)
                    name.set_halign(Gtk.Align.START)
                    name.set_hexpand(True)
                    idx_row.append(name)

                    if idx.metadata and 'columns' in idx.metadata:
                        cols = Gtk.Label(label=', '.join(idx.metadata['columns']))
                        cols.add_css_class('entity-index-cols')
                        idx_row.append(cols)

                    idx_group.append(idx_row)

    def _build_view_view(self, node: SchemaNode):
        """Build the view for a database view."""
        # Quick action
        select_btn = Gtk.Button(label='SELECT *')
        select_btn.add_css_class('suggested-action')
        select_btn.connect('clicked', self._on_select_all, node.name)
        self.actions_box.append(select_btn)

        # Definition
        if node.metadata and 'definition' in node.metadata:
            def_group = self._create_info_group('Definition')
            self.content_box.append(def_group)

            def_label = Gtk.Label(label=node.metadata['definition'])
            def_label.set_wrap(True)
            def_label.set_selectable(True)
            def_label.add_css_class('entity-definition')
            def_group.append(def_label)

    def _build_column_view(self, node: SchemaNode):
        """Build the view for a column."""
        if node.metadata:
            info_group = self._create_info_group('Column Info')
            self.content_box.append(info_group)

            if 'data_type' in node.metadata:
                self._add_info_row(info_group, 'Type', node.metadata['data_type'])
            if 'nullable' in node.metadata:
                self._add_info_row(info_group, 'Nullable', 'Yes' if node.metadata['nullable'] else 'No')
            if 'default' in node.metadata:
                self._add_info_row(info_group, 'Default', str(node.metadata['default']))
            if 'is_pk' in node.metadata and node.metadata['is_pk']:
                self._add_info_row(info_group, 'Primary Key', 'Yes')
            if 'is_fk' in node.metadata and node.metadata['is_fk']:
                self._add_info_row(info_group, 'Foreign Key', 'Yes')
                if 'references' in node.metadata:
                    self._add_info_row(info_group, 'References', node.metadata['references'])

    def _build_schema_view(self, node: SchemaNode):
        """Build the view for a schema."""
        if node.children:
            tables = [c for c in node.children if c.node_type == 'table']
            views = [c for c in node.children if c.node_type == 'view']

            info_group = self._create_info_group('Schema Info')
            self.content_box.append(info_group)

            self._add_info_row(info_group, 'Tables', str(len(tables)))
            self._add_info_row(info_group, 'Views', str(len(views)))

    def _create_info_group(self, title: str) -> Gtk.Box:
        """Create a titled info group."""
        group = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        group.add_css_class('entity-group')

        label = Gtk.Label(label=title)
        label.set_halign(Gtk.Align.START)
        label.add_css_class('entity-group-title')
        group.append(label)

        return group

    def _add_info_row(self, group: Gtk.Box, label: str, value: str):
        """Add an info row to a group."""
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        row.add_css_class('entity-info-row')

        lbl = Gtk.Label(label=label)
        lbl.set_halign(Gtk.Align.START)
        lbl.set_size_request(100, -1)
        lbl.add_css_class('entity-info-label')
        row.append(lbl)

        val = Gtk.Label(label=value)
        val.set_halign(Gtk.Align.START)
        val.set_selectable(True)
        val.add_css_class('entity-info-value')
        row.append(val)

        group.append(row)

    def _on_select_all(self, button, table_name: str):
        """Generate SELECT * query."""
        if self.on_query:
            self.on_query(f'SELECT * FROM {table_name} LIMIT 100;')

    def _on_count(self, button, table_name: str):
        """Generate COUNT query."""
        if self.on_query:
            self.on_query(f'SELECT COUNT(*) FROM {table_name};')


class RowDetailView(Gtk.Box):
    """
    Expanded detail view for a single database row.
    Shows data in multiple formats: field list, JSON, and raw values.
    """

    def __init__(
        self,
        on_close: Callable[[], None] | None = None,
        on_edit: Callable[[str, Any, Any], None] | None = None,
    ):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add_css_class('row-detail-view')

        self.on_close = on_close
        self.on_edit = on_edit
        self._columns: list[str] = []
        self._row_data: dict = {}
        self._view_mode = 'fields'  # 'fields', 'json', 'raw'

        # Header with close button
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        header.add_css_class('row-detail-header')
        header.set_margin_start(12)
        header.set_margin_end(12)
        header.set_margin_top(8)
        header.set_margin_bottom(8)
        self.append(header)

        self.title_label = Gtk.Label(label='Row Details')
        self.title_label.set_halign(Gtk.Align.START)
        self.title_label.set_hexpand(True)
        self.title_label.add_css_class('row-detail-title')
        header.append(self.title_label)

        # View mode toggle buttons
        mode_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        mode_box.add_css_class('linked')
        header.append(mode_box)

        self.fields_btn = Gtk.ToggleButton(label='Fields')
        self.fields_btn.set_active(True)
        self.fields_btn.connect('toggled', self._on_mode_changed, 'fields')
        mode_box.append(self.fields_btn)

        self.json_btn = Gtk.ToggleButton(label='JSON')
        self.json_btn.connect('toggled', self._on_mode_changed, 'json')
        mode_box.append(self.json_btn)

        self.raw_btn = Gtk.ToggleButton(label='Raw')
        self.raw_btn.connect('toggled', self._on_mode_changed, 'raw')
        mode_box.append(self.raw_btn)

        # Close button
        close_btn = Gtk.Button()
        close_btn.set_icon_name('window-close-symbolic')
        close_btn.add_css_class('flat')
        close_btn.connect('clicked', self._on_close_clicked)
        header.append(close_btn)

        # Content area
        self.content_scroll = Gtk.ScrolledWindow()
        self.content_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.content_scroll.set_vexpand(True)
        self.append(self.content_scroll)

        self.content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.content_box.set_margin_start(12)
        self.content_box.set_margin_end(12)
        self.content_box.set_margin_top(8)
        self.content_box.set_margin_bottom(12)
        self.content_scroll.set_child(self.content_box)

    def show_row(self, columns: list[str], row_data: tuple | dict, row_index: int | None = None):
        """Display a row's data in the detail view."""
        self._columns = columns

        # Convert tuple to dict if needed
        if isinstance(row_data, tuple):
            self._row_data = dict(zip(columns, row_data, strict=False))
        else:
            self._row_data = dict(row_data)

        # Update title
        if row_index is not None:
            self.title_label.set_label(f'Row {row_index + 1}')
        else:
            self.title_label.set_label('Row Details')

        self._rebuild_content()

    def _on_mode_changed(self, button, mode: str):
        """Handle view mode toggle."""
        if not button.get_active():
            return

        self._view_mode = mode

        # Update toggle states
        if mode != 'fields':
            self.fields_btn.set_active(False)
        if mode != 'json':
            self.json_btn.set_active(False)
        if mode != 'raw':
            self.raw_btn.set_active(False)

        self._rebuild_content()

    def _rebuild_content(self):
        """Rebuild the content based on current view mode."""
        # Clear existing content
        while True:
            child = self.content_box.get_first_child()
            if child is None:
                break
            self.content_box.remove(child)

        if self._view_mode == 'fields':
            self._build_fields_view()
        elif self._view_mode == 'json':
            self._build_json_view()
        elif self._view_mode == 'raw':
            self._build_raw_view()

    def _build_fields_view(self):
        """Build field-by-field view with type indicators."""
        for col in self._columns:
            value = self._row_data.get(col)

            field_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            field_row.add_css_class('row-detail-field')
            field_row.set_margin_top(4)
            field_row.set_margin_bottom(4)

            # Field name
            name_label = Gtk.Label(label=col)
            name_label.set_halign(Gtk.Align.START)
            name_label.set_size_request(120, -1)
            name_label.add_css_class('row-detail-field-name')
            field_row.append(name_label)

            # Type indicator
            type_str = self._get_type_string(value)
            type_label = Gtk.Label(label=type_str)
            type_label.set_size_request(60, -1)
            type_label.add_css_class('row-detail-field-type')
            field_row.append(type_label)

            # Value display
            value_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            value_container.set_hexpand(True)
            field_row.append(value_container)

            if self._is_complex_value(value):
                # Show expandable view for complex values (JSON, arrays)
                self._build_complex_value_view(value_container, value)
            else:
                # Simple value display
                value_label = Gtk.Label(label=self._format_value(value))
                value_label.set_halign(Gtk.Align.START)
                value_label.set_selectable(True)
                value_label.set_wrap(True)
                value_label.add_css_class('row-detail-field-value')
                if value is None:
                    value_label.add_css_class('row-detail-null')
                value_container.append(value_label)

            self.content_box.append(field_row)

    def _build_json_view(self):
        """Build JSON representation view."""
        import json

        try:
            json_str = json.dumps(self._row_data, indent=2, default=str)
        except (TypeError, ValueError):
            json_str = str(self._row_data)

        # Use a text view for JSON with syntax highlighting style
        json_frame = Gtk.Frame()
        json_frame.add_css_class('row-detail-json-frame')

        text_view = Gtk.TextView()
        text_view.set_editable(False)
        text_view.set_monospace(True)
        text_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        text_view.add_css_class('row-detail-json')
        text_view.get_buffer().set_text(json_str)

        json_frame.set_child(text_view)
        self.content_box.append(json_frame)

        # Copy button
        copy_btn = Gtk.Button(label='Copy JSON')
        copy_btn.set_halign(Gtk.Align.START)
        copy_btn.set_margin_top(8)
        copy_btn.connect('clicked', self._on_copy_json, json_str)
        self.content_box.append(copy_btn)

    def _build_raw_view(self):
        """Build raw values view (comma-separated)."""
        raw_values = []
        for col in self._columns:
            value = self._row_data.get(col)
            raw_values.append(repr(value))

        raw_str = ', '.join(raw_values)

        text_view = Gtk.TextView()
        text_view.set_editable(False)
        text_view.set_monospace(True)
        text_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        text_view.add_css_class('row-detail-raw')
        text_view.get_buffer().set_text(f'({raw_str})')

        self.content_box.append(text_view)

    def _build_complex_value_view(self, container: Gtk.Box, value: Any):
        """Build an expandable view for complex values like JSON objects."""
        import json

        # Try to format as JSON
        try:
            if isinstance(value, str):
                # Try to parse as JSON string
                parsed = json.loads(value)
                formatted = json.dumps(parsed, indent=2)
            else:
                formatted = json.dumps(value, indent=2, default=str)
        except (json.JSONDecodeError, TypeError):
            formatted = str(value)

        # Expandable text view
        expander = Gtk.Expander(label='View data...')
        expander.add_css_class('row-detail-expander')

        text_view = Gtk.TextView()
        text_view.set_editable(False)
        text_view.set_monospace(True)
        text_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        text_view.add_css_class('row-detail-complex-value')
        text_view.get_buffer().set_text(formatted)

        expander.set_child(text_view)
        container.append(expander)

    def _get_type_string(self, value: Any) -> str:
        """Get a short type indicator string."""
        if value is None:
            return 'null'
        elif isinstance(value, bool):
            return 'bool'
        elif isinstance(value, int):
            return 'int'
        elif isinstance(value, float):
            return 'float'
        elif isinstance(value, str):
            # Check if it looks like JSON
            if value.startswith(('{', '[')):
                return 'json?'
            return 'str'
        elif isinstance(value, (list, tuple)):
            return 'array'
        elif isinstance(value, dict):
            return 'object'
        else:
            return type(value).__name__[:6]

    def _is_complex_value(self, value: Any) -> bool:
        """Check if a value should be shown in expandable view."""
        if isinstance(value, (dict, list, tuple)):
            return True
        if isinstance(value, str):
            # Long strings or JSON-like strings
            if len(value) > 100:
                return True
            if value.startswith(('{', '[')):
                return True
        return False

    def _format_value(self, value: Any) -> str:
        """Format a value for display."""
        if value is None:
            return 'NULL'
        elif isinstance(value, bool):
            return 'true' if value else 'false'
        elif isinstance(value, str):
            return value
        else:
            return str(value)

    def _on_copy_json(self, button, json_str: str):
        """Copy JSON to clipboard."""
        clipboard = Gdk.Display.get_default().get_clipboard()
        clipboard.set(json_str)

        # Show feedback
        button.set_label('Copied!')
        GLib.timeout_add(1500, lambda: button.set_label('Copy JSON') or False)

    def _on_close_clicked(self, button):
        """Handle close button click."""
        if self.on_close:
            self.on_close()


class RowDetailWindow(Adw.Window):
    """
    Dedicated window for viewing row details with plenty of space.
    Shows data in multiple formats: fields, JSON, and raw values.
    Supports navigation between rows and inline editing.
    """

    def __init__(
        self,
        parent: Gtk.Window,
        columns: list[str],
        rows: list[tuple],
        current_index: int = 0,
        table_name: str = '',
        on_edit: Callable[[int, str, Any, Any], None] | None = None,
    ):
        super().__init__()
        self.set_transient_for(parent)
        self.set_modal(False)  # Allow interaction with main window
        self.set_default_size(700, 600)
        self.set_title(f'Row Details - {table_name}' if table_name else 'Row Details')
        self.add_css_class('row-detail-window')

        self._columns = columns
        self._rows = rows
        self._current_index = current_index
        self._table_name = table_name
        self.on_edit = on_edit
        self._view_mode = 'fields'

        # Build UI
        self._build_ui()
        self._update_content()

    def _build_ui(self):
        """Build the window UI."""
        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_content(main_box)

        # Header bar
        header = Adw.HeaderBar()
        header.add_css_class('flat')
        main_box.append(header)

        # Navigation buttons in header
        nav_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        nav_box.add_css_class('linked')
        header.pack_start(nav_box)

        self.prev_btn = Gtk.Button()
        self.prev_btn.set_icon_name('go-previous-symbolic')
        self.prev_btn.set_tooltip_text('Previous row (←)')
        self.prev_btn.connect('clicked', self._on_prev)
        nav_box.append(self.prev_btn)

        self.next_btn = Gtk.Button()
        self.next_btn.set_icon_name('go-next-symbolic')
        self.next_btn.set_tooltip_text('Next row (→)')
        self.next_btn.connect('clicked', self._on_next)
        nav_box.append(self.next_btn)

        # Row counter
        self.row_counter = Gtk.Label()
        self.row_counter.add_css_class('dim-label')
        self.row_counter.set_margin_start(12)
        header.pack_start(self.row_counter)

        # View mode toggle in header
        mode_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        mode_box.add_css_class('linked')
        header.pack_end(mode_box)

        self.raw_btn = Gtk.ToggleButton(label='Raw')
        self.raw_btn.connect('toggled', self._on_mode_changed, 'raw')
        mode_box.append(self.raw_btn)

        self.json_btn = Gtk.ToggleButton(label='JSON')
        self.json_btn.connect('toggled', self._on_mode_changed, 'json')
        mode_box.append(self.json_btn)

        self.fields_btn = Gtk.ToggleButton(label='Fields')
        self.fields_btn.set_active(True)
        self.fields_btn.connect('toggled', self._on_mode_changed, 'fields')
        mode_box.append(self.fields_btn)

        # Content area with horizontal paned for fields + JSON preview
        self.content_paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        self.content_paned.set_vexpand(True)
        main_box.append(self.content_paned)

        # Left side: Fields view (main content)
        left_scroll = Gtk.ScrolledWindow()
        left_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        left_scroll.set_hexpand(True)
        self.content_paned.set_start_child(left_scroll)
        self.content_paned.set_shrink_start_child(False)

        self.fields_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.fields_box.set_margin_start(16)
        self.fields_box.set_margin_end(16)
        self.fields_box.set_margin_top(12)
        self.fields_box.set_margin_bottom(16)
        left_scroll.set_child(self.fields_box)

        # Right side: JSON preview panel
        right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        right_box.set_size_request(280, -1)
        right_box.add_css_class('row-detail-json-panel')
        self.content_paned.set_end_child(right_box)
        self.content_paned.set_shrink_end_child(False)
        self.content_paned.set_resize_end_child(False)

        # JSON panel header
        json_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        json_header.set_margin_start(12)
        json_header.set_margin_end(12)
        json_header.set_margin_top(8)
        json_header.set_margin_bottom(8)
        right_box.append(json_header)

        json_title = Gtk.Label(label='JSON Preview')
        json_title.set_halign(Gtk.Align.START)
        json_title.set_hexpand(True)
        json_title.add_css_class('heading')
        json_header.append(json_title)

        copy_btn = Gtk.Button()
        copy_btn.set_icon_name('edit-copy-symbolic')
        copy_btn.set_tooltip_text('Copy JSON')
        copy_btn.add_css_class('flat')
        copy_btn.connect('clicked', self._on_copy_json)
        json_header.append(copy_btn)

        # JSON content
        json_scroll = Gtk.ScrolledWindow()
        json_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        json_scroll.set_vexpand(True)
        right_box.append(json_scroll)

        self.json_view = Gtk.TextView()
        self.json_view.set_editable(False)
        self.json_view.set_monospace(True)
        self.json_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.json_view.add_css_class('row-detail-json-preview')
        self.json_view.set_left_margin(12)
        self.json_view.set_right_margin(12)
        self.json_view.set_top_margin(8)
        self.json_view.set_bottom_margin(8)
        json_scroll.set_child(self.json_view)

        # Set initial paned position
        self.content_paned.set_position(400)

        # Keyboard shortcuts
        key_controller = Gtk.EventControllerKey()
        key_controller.connect('key-pressed', self._on_key_pressed)
        self.add_controller(key_controller)

    def _on_key_pressed(self, controller, keyval, keycode, state):
        """Handle keyboard navigation."""
        if keyval == Gdk.KEY_Left or keyval == Gdk.KEY_Up:
            self._on_prev(None)
            return True
        elif keyval == Gdk.KEY_Right or keyval == Gdk.KEY_Down:
            self._on_next(None)
            return True
        elif keyval == Gdk.KEY_Escape:
            self.close()
            return True
        return False

    def _on_prev(self, button):
        """Navigate to previous row."""
        if self._current_index > 0:
            self._current_index -= 1
            self._update_content()

    def _on_next(self, button):
        """Navigate to next row."""
        if self._current_index < len(self._rows) - 1:
            self._current_index += 1
            self._update_content()

    def _on_mode_changed(self, button, mode: str):
        """Handle view mode toggle."""
        if not button.get_active():
            return

        self._view_mode = mode

        # Update toggle states
        if mode != 'fields':
            self.fields_btn.set_active(False)
        if mode != 'json':
            self.json_btn.set_active(False)
        if mode != 'raw':
            self.raw_btn.set_active(False)

        self._update_content()

    def _update_content(self):
        """Update display for current row."""
        # Update navigation state
        self.prev_btn.set_sensitive(self._current_index > 0)
        self.next_btn.set_sensitive(self._current_index < len(self._rows) - 1)
        self.row_counter.set_label(f'Row {self._current_index + 1} of {len(self._rows)}')

        # Get current row data
        row_data = self._rows[self._current_index]
        row_dict = dict(zip(self._columns, row_data, strict=False))

        # Update JSON preview
        import json

        try:
            json_str = json.dumps(row_dict, indent=2, default=str)
        except (TypeError, ValueError):
            json_str = str(row_dict)
        self.json_view.get_buffer().set_text(json_str)

        # Clear fields box
        while True:
            child = self.fields_box.get_first_child()
            if child is None:
                break
            self.fields_box.remove(child)

        # Build content based on view mode
        if self._view_mode == 'fields':
            self._build_fields_view(row_dict)
            self.content_paned.get_end_child().set_visible(True)
        elif self._view_mode == 'json':
            self._build_full_json_view(json_str)
            self.content_paned.get_end_child().set_visible(False)
        elif self._view_mode == 'raw':
            self._build_raw_view(row_data)
            self.content_paned.get_end_child().set_visible(False)

    def _build_fields_view(self, row_dict: dict):
        """Build field-by-field view with card-style layout."""
        for col in self._columns:
            value = row_dict.get(col)

            # Field card
            card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            card.add_css_class('row-detail-field-card')
            card.set_margin_bottom(8)

            # Field header (name + type)
            header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            card.append(header)

            name_label = Gtk.Label(label=col)
            name_label.set_halign(Gtk.Align.START)
            name_label.add_css_class('row-detail-field-name')
            header.append(name_label)

            type_str = self._get_type_string(value)
            type_badge = Gtk.Label(label=type_str)
            type_badge.add_css_class('row-detail-type-badge')
            header.append(type_badge)

            # Spacer
            spacer = Gtk.Box()
            spacer.set_hexpand(True)
            header.append(spacer)

            # Edit button (if editable)
            if self.on_edit:
                edit_btn = Gtk.Button()
                edit_btn.set_icon_name('document-edit-symbolic')
                edit_btn.add_css_class('flat')
                edit_btn.add_css_class('circular')
                edit_btn.set_tooltip_text('Edit value')
                edit_btn.connect('clicked', self._on_edit_field, col, value)
                header.append(edit_btn)

            # Value display
            if self._is_complex_value(value):
                self._build_complex_value_card(card, value)
            else:
                value_label = Gtk.Label(label=self._format_value(value))
                value_label.set_halign(Gtk.Align.START)
                value_label.set_selectable(True)
                value_label.set_wrap(True)
                value_label.set_xalign(0)
                value_label.add_css_class('row-detail-field-value')
                if value is None:
                    value_label.add_css_class('row-detail-null')
                card.append(value_label)

            self.fields_box.append(card)

    def _build_complex_value_card(self, card: Gtk.Box, value: Any):
        """Build expandable view for complex values."""
        import json

        try:
            if isinstance(value, str):
                parsed = json.loads(value)
                formatted = json.dumps(parsed, indent=2)
            else:
                formatted = json.dumps(value, indent=2, default=str)
        except (json.JSONDecodeError, TypeError):
            formatted = str(value)

        # Use expander for complex values
        expander = Gtk.Expander(label=f'{len(formatted)} chars')
        expander.set_expanded(len(formatted) < 500)
        expander.add_css_class('row-detail-expander')

        text_view = Gtk.TextView()
        text_view.set_editable(False)
        text_view.set_monospace(True)
        text_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        text_view.add_css_class('row-detail-complex-value')
        text_view.get_buffer().set_text(formatted)

        expander.set_child(text_view)
        card.append(expander)

    def _build_full_json_view(self, json_str: str):
        """Build full-width JSON view."""
        frame = Gtk.Frame()
        frame.add_css_class('row-detail-json-frame')

        text_view = Gtk.TextView()
        text_view.set_editable(False)
        text_view.set_monospace(True)
        text_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        text_view.add_css_class('row-detail-json')
        text_view.set_left_margin(16)
        text_view.set_right_margin(16)
        text_view.set_top_margin(12)
        text_view.set_bottom_margin(12)
        text_view.get_buffer().set_text(json_str)

        frame.set_child(text_view)
        self.fields_box.append(frame)

    def _build_raw_view(self, row_data: tuple):
        """Build raw tuple view."""
        raw_values = [repr(v) for v in row_data]
        raw_str = f'({", ".join(raw_values)})'

        text_view = Gtk.TextView()
        text_view.set_editable(False)
        text_view.set_monospace(True)
        text_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        text_view.add_css_class('row-detail-raw')
        text_view.set_left_margin(16)
        text_view.set_right_margin(16)
        text_view.set_top_margin(12)
        text_view.set_bottom_margin(12)
        text_view.get_buffer().set_text(raw_str)

        self.fields_box.append(text_view)

    def _on_edit_field(self, button, column: str, old_value: Any):
        """Handle edit button click for a field."""
        # Create edit dialog
        dialog = Adw.MessageDialog(
            transient_for=self,
            heading=f'Edit {column}',
            body='Enter new value:',
        )
        dialog.add_response('cancel', 'Cancel')
        dialog.add_response('save', 'Save')
        dialog.set_response_appearance('save', Adw.ResponseAppearance.SUGGESTED)

        # Entry for new value
        entry = Gtk.Entry()
        entry.set_text(str(old_value) if old_value is not None else '')
        entry.set_margin_start(24)
        entry.set_margin_end(24)
        dialog.set_extra_child(entry)

        def on_response(dialog, response):
            if response == 'save' and self.on_edit:
                new_value = entry.get_text()
                self.on_edit(self._current_index, column, old_value, new_value)
            dialog.close()

        dialog.connect('response', on_response)
        dialog.present()

    def _on_copy_json(self, button):
        """Copy JSON to clipboard."""
        clipboard = Gdk.Display.get_default().get_clipboard()
        buffer = self.json_view.get_buffer()
        start, end = buffer.get_bounds()
        json_str = buffer.get_text(start, end, False)
        clipboard.set(json_str)

        # Show feedback toast
        toast = Adw.Toast(title='JSON copied to clipboard')
        toast.set_timeout(2)
        # Find the toast overlay (if we had one - for now just change button temporarily)
        button.set_icon_name('emblem-ok-symbolic')
        GLib.timeout_add(1500, lambda: button.set_icon_name('edit-copy-symbolic') or False)

    def _get_type_string(self, value: Any) -> str:
        """Get a short type indicator string."""
        if value is None:
            return 'null'
        elif isinstance(value, bool):
            return 'bool'
        elif isinstance(value, int):
            return 'int'
        elif isinstance(value, float):
            return 'float'
        elif isinstance(value, str):
            if value.startswith(('{', '[')):
                return 'json'
            return 'str'
        elif isinstance(value, (list, tuple)):
            return 'array'
        elif isinstance(value, dict):
            return 'object'
        else:
            return type(value).__name__[:6]

    def _is_complex_value(self, value: Any) -> bool:
        """Check if a value should be shown in expandable view."""
        if isinstance(value, (dict, list, tuple)):
            return True
        if isinstance(value, str):
            if len(value) > 100 or value.startswith(('{', '[')):
                return True
        return False

    def _format_value(self, value: Any) -> str:
        """Format a value for display."""
        if value is None:
            return 'NULL'
        elif isinstance(value, bool):
            return 'true' if value else 'false'
        elif isinstance(value, str):
            return value
        else:
            return str(value)

    def navigate_to_row(self, index: int):
        """Navigate to a specific row index."""
        if 0 <= index < len(self._rows):
            self._current_index = index
            self._update_content()


# Additional CSS for the new widgets
DB_WIDGETS_CSS = f"""
/* === Syntax Editor === */
.syntax-editor {{
    background-color: {COLORS['crust']};
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    font-size: 13px;
}}

.syntax-editor text {{
    color: {COLORS['text']};
    caret-color: {COLORS['mauve']};
    background-color: {COLORS['crust']};
}}

.line-numbers {{
    background-color: {COLORS['mantle']};
    color: {COLORS['overlay0']};
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    border-right: 1px solid {COLORS['surface0']};
}}

.line-numbers text {{
    color: {COLORS['overlay0']};
    background-color: {COLORS['mantle']};
}}

/* === Virtual Scrolling Table === */
.results-header-row {{
    background-color: {COLORS['mantle']};
    border-bottom: 2px solid {COLORS['surface0']};
    min-height: 36px;
}}

.results-row {{
    border-bottom: 1px solid {COLORS['surface0']}30;
}}

.results-row-alt {{
    background-color: {COLORS['surface0']}15;
}}

.results-row:hover {{
    background-color: {COLORS['surface0']}40;
    cursor: pointer;
}}

.results-row-selected {{
    background-color: {COLORS['mauve']}30;
    border-left: 3px solid {COLORS['mauve']};
}}

.results-row-selected:hover {{
    background-color: {COLORS['mauve']}40;
}}

.editable-cell {{
    cursor: pointer;
}}

.editable-cell:hover {{
    background-color: {COLORS['blue']}20;
}}

.cell-edit-entry {{
    background-color: {COLORS['crust']};
    border: 2px solid {COLORS['mauve']};
    border-radius: 4px;
    padding: 4px 8px;
    font-family: monospace;
}}

/* === Edit Confirmation Dialog === */
.change-row {{
    background-color: {COLORS['surface0']};
    border-radius: 6px;
    padding: 8px 12px;
}}

.change-column {{
    color: {COLORS['blue']};
    font-weight: bold;
    font-family: monospace;
}}

.change-old {{
    color: {COLORS['red']};
    font-family: monospace;
    text-decoration: line-through;
}}

.change-new {{
    color: {COLORS['green']};
    font-weight: bold;
    font-family: monospace;
}}

.warning-text {{
    color: {COLORS['peach']};
    font-weight: bold;
}}

/* === Schema Tree === */
.schema-search {{
    margin: 8px;
    border-radius: 8px;
}}

.schema-tree {{
    background-color: {COLORS['base']};
}}

.schema-row {{
    padding: 6px 8px;
    border-radius: 6px;
    transition: background-color 150ms;
}}

.schema-row:hover {{
    background-color: {COLORS['surface0']};
}}

.schema-row-selected {{
    background-color: {COLORS['mauve']}30;
}}

.schema-row-selected:hover {{
    background-color: {COLORS['mauve']}40;
}}

.expand-btn {{
    min-width: 24px;
    min-height: 24px;
    padding: 2px;
    font-size: 10px;
    color: {COLORS['overlay0']};
}}

.expand-btn:hover {{
    color: {COLORS['text']};
}}

.schema-name {{
    color: {COLORS['text']};
}}

.schema-badge {{
    background-color: {COLORS['surface1']};
    color: {COLORS['subtext0']};
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 11px;
    font-family: monospace;
}}

.schema-type {{
    color: {COLORS['yellow']};
    font-size: 11px;
    font-family: monospace;
}}

.schema-icon-schema {{
    color: {COLORS['blue']};
}}

.schema-icon-table {{
    color: {COLORS['mauve']};
}}

.schema-icon-view {{
    color: {COLORS['teal']};
}}

.schema-icon-column {{
    color: {COLORS['green']};
}}

.schema-icon-index {{
    color: {COLORS['peach']};
}}

/* === Entity View === */
.entity-view {{
    background-color: {COLORS['mantle']};
    border-left: 1px solid {COLORS['surface0']};
}}

.entity-header {{
    background-color: {COLORS['base']};
    border-bottom: 1px solid {COLORS['surface0']};
    padding-bottom: 12px;
}}

.entity-icon {{
    font-size: 32px;
}}

.entity-title {{
    font-size: 18px;
    font-weight: bold;
    color: {COLORS['text']};
}}

.entity-subtitle {{
    font-size: 12px;
    color: {COLORS['subtext0']};
    text-transform: uppercase;
    letter-spacing: 1px;
}}

.entity-group {{
    background-color: {COLORS['base']};
    padding: 12px;
    border-radius: 8px;
    border: 1px solid {COLORS['surface0']};
}}

.entity-group-title {{
    font-size: 12px;
    font-weight: bold;
    color: {COLORS['subtext0']};
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 8px;
}}

.entity-info-row {{
    padding: 4px 0;
}}

.entity-info-label {{
    color: {COLORS['overlay0']};
    font-size: 13px;
}}

.entity-info-value {{
    color: {COLORS['text']};
    font-size: 13px;
}}

.entity-column-row {{
    padding: 6px 8px;
    border-radius: 4px;
    transition: background-color 150ms;
}}

.entity-column-row:hover {{
    background-color: {COLORS['surface0']};
}}

.entity-column-name {{
    color: {COLORS['text']};
    font-weight: 500;
}}

.entity-column-type {{
    color: {COLORS['yellow']};
    font-family: monospace;
    font-size: 12px;
}}

.entity-column-constraint {{
    color: {COLORS['red']};
    font-size: 11px;
    font-weight: bold;
}}

.entity-index-row {{
    padding: 4px 8px;
    color: {COLORS['subtext0']};
}}

.entity-index-cols {{
    font-family: monospace;
    font-size: 11px;
    color: {COLORS['overlay0']};
}}

.entity-definition {{
    font-family: monospace;
    font-size: 12px;
    padding: 8px;
    background-color: {COLORS['crust']};
    border-radius: 4px;
}}

/* === Row Detail View === */
.row-detail-view {{
    background-color: {COLORS['base']};
    border-left: 1px solid {COLORS['surface0']};
}}

.row-detail-header {{
    background-color: {COLORS['mantle']};
    border-bottom: 1px solid {COLORS['surface0']};
    padding: 8px 12px;
}}

.row-detail-title {{
    font-size: 14px;
    font-weight: bold;
    color: {COLORS['text']};
}}

.row-detail-field {{
    padding: 8px 12px;
    border-radius: 6px;
    background-color: {COLORS['surface0']}20;
}}

.row-detail-field:hover {{
    background-color: {COLORS['surface0']}40;
}}

.row-detail-field-name {{
    font-weight: bold;
    color: {COLORS['blue']};
    font-family: monospace;
}}

.row-detail-field-type {{
    color: {COLORS['overlay0']};
    font-size: 11px;
    font-family: monospace;
    background-color: {COLORS['surface0']};
    padding: 2px 6px;
    border-radius: 4px;
}}

.row-detail-field-value {{
    color: {COLORS['text']};
    font-family: monospace;
}}

.row-detail-null {{
    color: {COLORS['overlay0']};
    font-style: italic;
}}

.row-detail-json-frame {{
    background-color: {COLORS['crust']};
    border-radius: 8px;
    padding: 12px;
}}

.row-detail-json text {{
    color: {COLORS['text']};
    background-color: {COLORS['crust']};
    font-size: 12px;
}}

.row-detail-raw text {{
    color: {COLORS['subtext0']};
    background-color: {COLORS['mantle']};
    font-size: 12px;
    padding: 12px;
}}

.row-detail-expander {{
    color: {COLORS['mauve']};
}}

.row-detail-complex-value text {{
    color: {COLORS['text']};
    background-color: {COLORS['crust']};
    font-size: 11px;
    padding: 8px;
}}

/* === Row Detail Window === */
.row-detail-window {{
    background-color: {COLORS['base']};
}}

.row-detail-json-panel {{
    background-color: {COLORS['mantle']};
    border-left: 1px solid {COLORS['surface0']};
}}

.row-detail-json-preview text {{
    color: {COLORS['text']};
    background-color: {COLORS['mantle']};
    font-size: 12px;
}}

.row-detail-field-card {{
    background-color: {COLORS['surface0']}20;
    padding: 12px 16px;
    border-radius: 8px;
    border: 1px solid {COLORS['surface0']}40;
}}

.row-detail-field-card:hover {{
    background-color: {COLORS['surface0']}40;
    border-color: {COLORS['surface0']};
}}

.row-detail-type-badge {{
    background-color: {COLORS['surface1']};
    color: {COLORS['subtext0']};
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-family: monospace;
}}
"""


def get_db_widgets_css() -> str:
    """Get the CSS for database widgets."""
    return DB_WIDGETS_CSS
