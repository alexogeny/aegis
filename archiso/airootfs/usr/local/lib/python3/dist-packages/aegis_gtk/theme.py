"""
Aegis GTK Theme - Catppuccin Mocha color palette and CSS styles.
"""

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

# Catppuccin Mocha Colors
COLORS = {
    # Base colors
    'base': '#1e1e2e',
    'mantle': '#181825',
    'crust': '#11111b',

    # Surface colors
    'surface0': '#313244',
    'surface1': '#45475a',
    'surface2': '#585b70',

    # Text colors
    'text': '#cdd6f4',
    'subtext0': '#a6adc8',
    'subtext1': '#bac2de',

    # Overlay colors
    'overlay0': '#6c7086',
    'overlay1': '#7f849c',
    'overlay2': '#9399b2',

    # Accent colors
    'mauve': '#cba6f7',
    'blue': '#89b4fa',
    'sapphire': '#74c7ec',
    'sky': '#89dceb',
    'teal': '#94e2d5',
    'green': '#a6e3a1',
    'yellow': '#f9e2af',
    'peach': '#fab387',
    'maroon': '#eba0ac',
    'red': '#f38ba8',
    'pink': '#f5c2e7',
    'flamingo': '#f2cdcd',
    'rosewater': '#f5e0dc',
    'lavender': '#b4befe',
}

# All available accent colors for pickers
ACCENT_COLORS = [
    'red', 'mauve', 'blue', 'teal', 'peach', 'green', 'pink', 'sky',
    'yellow', 'lavender', 'sapphire', 'flamingo', 'rosewater', 'maroon', 'surface1'
]

# Light text colors (need dark text on these backgrounds)
LIGHT_COLORS = ['yellow', 'rosewater', 'flamingo', 'lavender', 'pink']


def get_base_css() -> str:
    """Generate base CSS shared by all Aegis applications."""
    c = COLORS
    return f"""
/* === Window & Container Styles === */
window {{
    background-color: {c['base']};
}}

.card {{
    background-color: {c['mantle']};
    border-radius: 12px;
    padding: 16px;
    border: 1px solid {c['surface0']};
}}

.panel {{
    background-color: {c['mantle']};
    border-radius: 16px;
    padding: 24px;
    border: 2px solid {c['surface0']};
}}

/* === Header Bar === */
.header-bar {{
    background-color: {c['crust']};
    border-bottom: 1px solid {c['surface0']};
}}

/* === Typography === */
.title {{
    color: {c['text']};
    font-weight: bold;
    font-size: 18px;
}}

.subtitle {{
    color: {c['subtext0']};
    font-size: 12px;
}}

.section-title {{
    color: {c['text']};
    font-weight: bold;
    font-size: 13px;
}}

.monospace {{
    font-family: monospace;
}}

/* === Status Indicators === */
.status-connected {{
    color: {c['green']};
    font-size: 11px;
}}

.status-disconnected {{
    color: {c['red']};
    font-size: 11px;
}}

.status-warning {{
    color: {c['yellow']};
    font-size: 11px;
}}

/* === Sliders === */
.slider-label {{
    color: {c['subtext0']};
    font-size: 13px;
}}

.slider-value {{
    color: {c['text']};
    font-family: monospace;
    font-size: 13px;
}}

/* === Buttons === */
.primary-button {{
    background-color: {c['blue']};
    color: {c['crust']};
    border-radius: 8px;
    padding: 8px 16px;
}}

.primary-button:hover {{
    background-color: {c['sky']};
}}

.secondary-button {{
    background-color: {c['surface0']};
    color: {c['text']};
    border-radius: 6px;
    padding: 6px 12px;
}}

.secondary-button:hover {{
    background-color: {c['surface1']};
}}

.icon-button {{
    background-color: transparent;
    border: none;
    padding: 4px;
    border-radius: 4px;
    min-width: 24px;
    min-height: 24px;
}}

.icon-button:hover {{
    background-color: {c['surface1']};
}}

.destructive-button:hover {{
    background-color: rgba(243, 139, 168, 0.3);
}}

/* === Color Picker Buttons === */
.color-btn {{
    min-width: 28px;
    min-height: 28px;
    border-radius: 6px;
    border: 2px solid transparent;
}}

.color-btn:checked {{
    border-color: {c['text']};
}}

.color-btn.color-red {{ background-color: {c['red']}; }}
.color-btn.color-mauve {{ background-color: {c['mauve']}; }}
.color-btn.color-blue {{ background-color: {c['blue']}; }}
.color-btn.color-teal {{ background-color: {c['teal']}; }}
.color-btn.color-peach {{ background-color: {c['peach']}; }}
.color-btn.color-green {{ background-color: {c['green']}; }}
.color-btn.color-pink {{ background-color: {c['pink']}; }}
.color-btn.color-sky {{ background-color: {c['sky']}; }}
.color-btn.color-yellow {{ background-color: {c['yellow']}; }}
.color-btn.color-lavender {{ background-color: {c['lavender']}; }}
.color-btn.color-sapphire {{ background-color: {c['sapphire']}; }}
.color-btn.color-flamingo {{ background-color: {c['flamingo']}; }}
.color-btn.color-rosewater {{ background-color: {c['rosewater']}; }}
.color-btn.color-maroon {{ background-color: {c['maroon']}; }}
.color-btn.color-surface1 {{ background-color: {c['surface1']}; }}

/* === Gradient Button Backgrounds === */
.btn-red {{ background: linear-gradient(135deg, {c['red']}, {c['red']}b3); }}
.btn-mauve {{ background: linear-gradient(135deg, {c['mauve']}, {c['mauve']}b3); }}
.btn-blue {{ background: linear-gradient(135deg, {c['blue']}, {c['blue']}b3); }}
.btn-teal {{ background: linear-gradient(135deg, {c['teal']}, {c['teal']}b3); }}
.btn-peach {{ background: linear-gradient(135deg, {c['peach']}, {c['peach']}b3); }}
.btn-green {{ background: linear-gradient(135deg, {c['green']}, {c['green']}b3); }}
.btn-pink {{ background: linear-gradient(135deg, {c['pink']}, {c['pink']}b3); }}
.btn-sky {{ background: linear-gradient(135deg, {c['sky']}, {c['sky']}b3); }}
.btn-yellow {{ background: linear-gradient(135deg, {c['yellow']}, {c['yellow']}b3); }}
.btn-lavender {{ background: linear-gradient(135deg, {c['lavender']}, {c['lavender']}b3); }}
.btn-sapphire {{ background: linear-gradient(135deg, {c['sapphire']}, {c['sapphire']}b3); }}
.btn-flamingo {{ background: linear-gradient(135deg, {c['flamingo']}, {c['flamingo']}b3); }}
.btn-rosewater {{ background: linear-gradient(135deg, {c['rosewater']}, {c['rosewater']}b3); }}
.btn-maroon {{ background: linear-gradient(135deg, {c['maroon']}, {c['maroon']}b3); }}
.btn-surface {{ background: linear-gradient(135deg, {c['surface1']}, {c['surface0']}); }}
.btn-surface1 {{ background: linear-gradient(135deg, {c['surface1']}, {c['surface0']}); }}

/* === Lists & Rows === */
.list-row {{
    background-color: {c['surface0']};
    border-radius: 8px;
    padding: 8px 12px;
    margin: 2px 0;
}}

.list-row:hover {{
    background-color: {c['surface1']};
}}

.list-row.active {{
    background-color: {c['mauve']};
}}

.list-row.active label {{
    color: {c['crust']};
}}

/* === Tags & Chips === */
.chip {{
    background-color: {c['surface0']};
    color: {c['subtext0']};
    border-radius: 16px;
    padding: 6px 12px;
    font-size: 11px;
}}

/* === Page Indicators === */
.page-indicator {{
    background-color: {c['surface0']};
    border-radius: 4px;
    padding: 4px 12px;
    min-width: 24px;
}}

.page-indicator.active {{
    background-color: {c['mauve']};
    color: {c['crust']};
}}

/* === Emoji/Icon Grids === */
.icon-grid button {{
    background-color: {c['surface0']};
    border-radius: 8px;
    min-width: 44px;
    min-height: 44px;
    font-size: 22px;
}}

.icon-grid button:hover {{
    background-color: {c['surface1']};
}}

.icon-grid button:checked {{
    background-color: {c['mauve']};
}}

/* === Dialog Content === */
.dialog-content {{
    padding: 24px;
}}

/* === Action Feedback === */
.action-success {{
    animation: success-flash 0.5s ease;
    box-shadow: 0 0 12px {c['green']};
}}

.action-error {{
    animation: error-flash 0.5s ease;
    box-shadow: 0 0 12px {c['red']};
}}

@keyframes success-flash {{
    0% {{ box-shadow: 0 0 0 {c['green']}; }}
    50% {{ box-shadow: 0 0 16px {c['green']}; }}
    100% {{ box-shadow: 0 0 0 {c['green']}; }}
}}

@keyframes error-flash {{
    0% {{ box-shadow: 0 0 0 {c['red']}; }}
    50% {{ box-shadow: 0 0 16px {c['red']}; }}
    100% {{ box-shadow: 0 0 0 {c['red']}; }}
}}

/* === Light Preview (for lighting apps) === */
.light-preview {{
    background: linear-gradient(135deg, {c['yellow']} 0%, {c['peach']} 100%);
    border-radius: 16px;
    min-width: 120px;
    min-height: 120px;
}}

.light-preview-off {{
    background-color: {c['surface1']};
    border-radius: 16px;
    min-width: 120px;
    min-height: 120px;
}}

/* === Deck Buttons (for macropad) === */
.deck-button {{
    border-radius: 12px;
    min-width: 72px;
    min-height: 72px;
    border: none;
    transition: all 0.15s ease;
}}

.deck-button:hover {{
    transform: scale(1.05);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}}

.deck-button:active {{
    transform: scale(0.95);
}}

.deck-button.edit-mode {{
    border: 2px dashed {c['overlay0']};
}}

.deck-button.edit-mode:hover {{
    border-color: {c['mauve']};
}}

.button-icon {{
    font-size: 28px;
}}

.button-label {{
    font-size: 9px;
    font-weight: bold;
    margin-top: 2px;
}}

/* === Sidebar Navigation === */
.sidebar {{
    background-color: {c['mantle']};
    border-right: 1px solid {c['surface0']};
}}

.sidebar-item {{
    padding: 12px 16px;
    border-radius: 8px;
    margin: 2px 8px;
}}

.sidebar-item:hover {{
    background-color: {c['surface0']};
}}

.sidebar-item.active {{
    background-color: {c['mauve']};
    color: {c['crust']};
}}

/* === Progress & Meters === */
.meter {{
    background-color: {c['surface0']};
    border-radius: 4px;
}}

.meter-fill {{
    background-color: {c['green']};
    border-radius: 4px;
}}

/* === Toggle States === */
.toggle-active {{
    background-color: {c['mauve']};
    color: {c['crust']};
}}

/* === Banners & Alerts === */
.info-banner {{
    background-color: {c['blue']}20;
    border: 1px solid {c['blue']}40;
    border-radius: 12px;
    padding: 16px;
}}

.warning-banner {{
    background-color: {c['yellow']}20;
    border: 1px solid {c['yellow']}40;
    border-radius: 12px;
    padding: 16px;
}}

.success-banner {{
    background-color: {c['green']}20;
    border: 1px solid {c['green']}40;
    border-radius: 12px;
    padding: 16px;
}}

.error-banner {{
    background-color: {c['red']}20;
    border: 1px solid {c['red']}40;
    border-radius: 12px;
    padding: 16px;
}}

/* === Status Cards === */
.status-card {{
    background-color: {c['mantle']};
    border-radius: 16px;
    padding: 24px;
    border: 2px solid {c['surface0']};
}}

.status-icon {{
    font-size: 48px;
}}

.status-title {{
    font-size: 20px;
    font-weight: bold;
    color: {c['text']};
}}

.status-subtitle {{
    font-size: 13px;
    color: {c['subtext0']};
}}

/* === Settings Rows === */
.settings-row {{
    padding: 12px 0;
    border-bottom: 1px solid {c['surface0']};
}}

.settings-row:last-child {{
    border-bottom: none;
}}

.settings-label {{
    color: {c['text']};
    font-weight: bold;
}}

.settings-description {{
    color: {c['overlay0']};
    font-size: 11px;
}}

/* === Action Buttons === */
.add-button {{
    background-color: {c['blue']};
    color: {c['crust']};
    border-radius: 8px;
    padding: 8px 16px;
}}

.add-button:hover {{
    background-color: {c['sapphire']};
}}

.danger-button {{
    background-color: {c['red']};
    color: {c['crust']};
    border-radius: 8px;
    padding: 8px 16px;
}}

.danger-button:hover {{
    background-color: {c['maroon']};
}}

/* === Main Container === */
.main-container {{
    background-color: {c['base']};
    padding: 24px;
}}
"""


def get_app_css(app_specific_css: str = "") -> str:
    """Combine base CSS with app-specific CSS."""
    return get_base_css() + "\n" + app_specific_css


def setup_css(window, app_specific_css: str = ""):
    """Setup CSS for a GTK window.

    Args:
        window: A Gtk.Window or Adw.ApplicationWindow
        app_specific_css: Additional CSS specific to the application
    """
    css_provider = Gtk.CssProvider()
    css = get_app_css(app_specific_css)
    css_provider.load_from_data(css.encode())
    Gtk.StyleContext.add_provider_for_display(
        window.get_display(),
        css_provider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )


def needs_dark_text(color: str) -> bool:
    """Check if a color needs dark text for contrast."""
    return color in LIGHT_COLORS
