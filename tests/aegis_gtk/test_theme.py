"""
Tests for aegis_gtk.theme module.
"""

import pytest


class TestColors:
    """Tests for the COLORS dictionary."""

    def test_colors_has_required_keys(self):
        """Verify all required Catppuccin Mocha colors are present."""
        from aegis_gtk.theme import COLORS

        required_keys = [
            # Base colors
            'base', 'mantle', 'crust',
            # Surface colors
            'surface0', 'surface1', 'surface2',
            # Text colors
            'text', 'subtext0', 'subtext1',
            # Overlay colors
            'overlay0', 'overlay1',
            # Accent colors
            'mauve', 'blue', 'sapphire', 'sky', 'teal', 'green',
            'yellow', 'peach', 'maroon', 'red', 'pink',
            'flamingo', 'rosewater', 'lavender'
        ]

        for key in required_keys:
            assert key in COLORS, f"Missing color: {key}"

    def test_colors_are_valid_hex(self):
        """Verify all colors are valid hex color codes."""
        from aegis_gtk.theme import COLORS
        import re

        hex_pattern = re.compile(r'^#[0-9a-fA-F]{6}$')

        for name, color in COLORS.items():
            assert hex_pattern.match(color), f"Invalid hex color for {name}: {color}"

    def test_catppuccin_mocha_base_color(self):
        """Verify base color matches Catppuccin Mocha spec."""
        from aegis_gtk.theme import COLORS

        assert COLORS['base'] == '#1e1e2e'
        assert COLORS['mantle'] == '#181825'
        assert COLORS['crust'] == '#11111b'


class TestAccentColors:
    """Tests for accent color utilities."""

    def test_accent_colors_list(self):
        """Verify ACCENT_COLORS contains expected colors."""
        from aegis_gtk.theme import ACCENT_COLORS, COLORS

        assert len(ACCENT_COLORS) > 0

        # All accent colors should exist in COLORS
        for color in ACCENT_COLORS:
            assert color in COLORS, f"Accent color {color} not in COLORS"

    def test_needs_dark_text(self):
        """Test needs_dark_text function for light colors."""
        from aegis_gtk.theme import needs_dark_text

        # These light colors need dark text
        assert needs_dark_text('yellow') is True
        assert needs_dark_text('rosewater') is True
        assert needs_dark_text('flamingo') is True

        # These dark colors don't need dark text
        assert needs_dark_text('blue') is False
        assert needs_dark_text('mauve') is False
        assert needs_dark_text('red') is False


class TestCSSGeneration:
    """Tests for CSS generation functions."""

    def test_get_base_css_returns_string(self):
        """Verify get_base_css returns a non-empty string."""
        from aegis_gtk.theme import get_base_css

        css = get_base_css()

        assert isinstance(css, str)
        assert len(css) > 0

    def test_get_base_css_contains_essential_classes(self):
        """Verify base CSS contains essential class definitions."""
        from aegis_gtk.theme import get_base_css

        css = get_base_css()

        essential_classes = [
            '.card',
            '.panel',
            '.header-bar',
            '.title',
            '.subtitle',
            '.primary-button',
            '.secondary-button',
            '.sidebar',
            '.info-banner',
            '.warning-banner',
            '.status-card',
            '.settings-row',
            '.main-container'
        ]

        for css_class in essential_classes:
            assert css_class in css, f"Missing CSS class: {css_class}"

    def test_get_base_css_uses_colors(self):
        """Verify base CSS uses color variables correctly."""
        from aegis_gtk.theme import get_base_css, COLORS

        css = get_base_css()

        # Check that actual color values appear in CSS
        assert COLORS['base'] in css
        assert COLORS['mantle'] in css
        assert COLORS['text'] in css

    def test_get_app_css_combines_base_and_app(self):
        """Verify get_app_css combines base CSS with app-specific CSS."""
        from aegis_gtk.theme import get_app_css, get_base_css

        app_specific = ".my-custom-class { color: red; }"
        combined = get_app_css(app_specific)

        base = get_base_css()

        assert base in combined
        assert app_specific in combined
        assert combined.index(base) < combined.index(app_specific)

    def test_get_app_css_with_empty_string(self):
        """Verify get_app_css works with empty app CSS."""
        from aegis_gtk.theme import get_app_css, get_base_css

        combined = get_app_css("")
        base = get_base_css()

        assert base in combined


class TestCSSValidity:
    """Tests for CSS syntax validity."""

    def test_css_braces_balanced(self):
        """Verify CSS has balanced braces."""
        from aegis_gtk.theme import get_base_css

        css = get_base_css()

        open_braces = css.count('{')
        close_braces = css.count('}')

        assert open_braces == close_braces, \
            f"Unbalanced braces: {open_braces} open, {close_braces} close"

    def test_css_no_python_fstring_errors(self):
        """Verify no f-string errors (unescaped braces) in CSS."""
        from aegis_gtk.theme import get_base_css

        css = get_base_css()

        # Check for common f-string errors
        assert '{{' not in css, "Found unprocessed double braces in CSS"
        assert '}}' not in css, "Found unprocessed double braces in CSS"
