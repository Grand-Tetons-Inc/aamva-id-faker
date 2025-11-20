"""
GUI Styling Constants and Color System
Based on visual design specification from GUI_FRAMEWORK_ANALYSIS.md

This module defines the complete color palette, typography, spacing,
and visual styling for the AAMVA License Generator GUI.
"""

from typing import Dict, Tuple


class ColorPalette:
    """Modern color palette for light and dark themes"""

    # Primary Colors (Blue accent)
    PRIMARY = "#1F6FEB"
    PRIMARY_HOVER = "#1A5FD7"
    PRIMARY_ACTIVE = "#0D4CA0"
    PRIMARY_LIGHT = "#388BFD"

    # Secondary Colors
    SECONDARY = "#8B949E"
    SECONDARY_HOVER = "#6E7681"
    SECONDARY_ACTIVE = "#57606A"

    # Success Colors
    SUCCESS = "#238636"
    SUCCESS_BG = "#DFF6DD"
    SUCCESS_BORDER = "#2EA043"

    # Warning Colors
    WARNING = "#9A6700"
    WARNING_BG = "#FFF8C5"
    WARNING_BORDER = "#D29922"

    # Error Colors
    ERROR = "#DA3633"
    ERROR_BG = "#FFE8E6"
    ERROR_BORDER = "#F85149"

    # Info Colors
    INFO = "#0969DA"
    INFO_BG = "#DDF4FF"
    INFO_BORDER = "#54A3FF"

    # Dark Theme Colors
    DARK_BG = "#0D1117"
    DARK_BG_SECONDARY = "#161B22"
    DARK_BG_TERTIARY = "#21262D"
    DARK_BORDER = "#30363D"
    DARK_TEXT = "#C9D1D9"
    DARK_TEXT_SECONDARY = "#8B949E"

    # Light Theme Colors
    LIGHT_BG = "#FFFFFF"
    LIGHT_BG_SECONDARY = "#F6F8FA"
    LIGHT_BG_TERTIARY = "#EAEEF2"
    LIGHT_BORDER = "#D0D7DE"
    LIGHT_TEXT = "#24292F"
    LIGHT_TEXT_SECONDARY = "#57606A"


class Spacing:
    """Consistent spacing scale"""
    XS = 4
    SM = 8
    MD = 12
    LG = 16
    XL = 20
    XXL = 24
    XXXL = 32
    HUGE = 48


class Typography:
    """Font configurations"""

    # Font Families
    FONT_FAMILY = "Segoe UI"
    FONT_FAMILY_MONO = "Consolas"

    # Font Sizes
    SIZE_TINY = 10
    SIZE_SMALL = 11
    SIZE_BODY = 13
    SIZE_MEDIUM = 14
    SIZE_LARGE = 16
    SIZE_TITLE = 18
    SIZE_HEADING = 20
    SIZE_DISPLAY = 24

    # Font Weights
    WEIGHT_NORMAL = "normal"
    WEIGHT_MEDIUM = "normal"  # CustomTkinter limitation
    WEIGHT_BOLD = "bold"


class BorderRadius:
    """Border radius scale"""
    NONE = 0
    SMALL = 4
    MEDIUM = 6
    LARGE = 8
    XLARGE = 12
    PILL = 999


class Shadow:
    """Shadow definitions (for future enhancement)"""
    SMALL = "0 1px 3px rgba(0,0,0,0.12)"
    MEDIUM = "0 4px 6px rgba(0,0,0,0.1)"
    LARGE = "0 10px 24px rgba(0,0,0,0.15)"
    XLARGE = "0 20px 40px rgba(0,0,0,0.2)"


class ThemeColors:
    """Theme-specific color configurations"""

    @staticmethod
    def get_dark_theme() -> Dict[str, str]:
        """Get dark theme color configuration"""
        return {
            # Backgrounds
            "bg_primary": ColorPalette.DARK_BG,
            "bg_secondary": ColorPalette.DARK_BG_SECONDARY,
            "bg_tertiary": ColorPalette.DARK_BG_TERTIARY,

            # Text
            "text_primary": ColorPalette.DARK_TEXT,
            "text_secondary": ColorPalette.DARK_TEXT_SECONDARY,
            "text_disabled": "#484F58",

            # Borders
            "border": ColorPalette.DARK_BORDER,
            "border_hover": "#525964",

            # Interactive
            "hover": "#1C2128",
            "active": "#262C36",
            "selected": ColorPalette.PRIMARY,

            # Status
            "success": ColorPalette.SUCCESS,
            "warning": ColorPalette.WARNING,
            "error": ColorPalette.ERROR,
            "info": ColorPalette.INFO,
        }

    @staticmethod
    def get_light_theme() -> Dict[str, str]:
        """Get light theme color configuration"""
        return {
            # Backgrounds
            "bg_primary": ColorPalette.LIGHT_BG,
            "bg_secondary": ColorPalette.LIGHT_BG_SECONDARY,
            "bg_tertiary": ColorPalette.LIGHT_BG_TERTIARY,

            # Text
            "text_primary": ColorPalette.LIGHT_TEXT,
            "text_secondary": ColorPalette.LIGHT_TEXT_SECONDARY,
            "text_disabled": "#8C959F",

            # Borders
            "border": ColorPalette.LIGHT_BORDER,
            "border_hover": "#8C959F",

            # Interactive
            "hover": "#F3F4F6",
            "active": "#E5E7EB",
            "selected": ColorPalette.PRIMARY,

            # Status
            "success": ColorPalette.SUCCESS,
            "warning": ColorPalette.WARNING,
            "error": ColorPalette.ERROR,
            "info": ColorPalette.INFO,
        }


class ComponentStyles:
    """Component-specific styling configurations"""

    # Window
    WINDOW_MIN_WIDTH = 1000
    WINDOW_MIN_HEIGHT = 700
    WINDOW_DEFAULT_WIDTH = 1200
    WINDOW_DEFAULT_HEIGHT = 800

    # Sidebar
    SIDEBAR_WIDTH = 320
    SIDEBAR_MIN_WIDTH = 280
    SIDEBAR_MAX_WIDTH = 400

    # Preview Panel
    PREVIEW_MIN_WIDTH = 400
    PREVIEW_PADDING = Spacing.LG

    # Status Bar
    STATUS_BAR_HEIGHT = 32

    # Buttons
    BUTTON_HEIGHT = 36
    BUTTON_PADDING_X = Spacing.LG
    BUTTON_PADDING_Y = Spacing.SM
    BUTTON_BORDER_WIDTH = 2

    # Input Fields
    INPUT_HEIGHT = 36
    INPUT_PADDING_X = Spacing.MD
    INPUT_BORDER_WIDTH = 1

    # Cards
    CARD_PADDING = Spacing.LG
    CARD_BORDER_WIDTH = 1
    CARD_CORNER_RADIUS = BorderRadius.MEDIUM

    # Progress Bar
    PROGRESS_BAR_HEIGHT = 6
    PROGRESS_BAR_CORNER_RADIUS = BorderRadius.SMALL

    # Scrollbar
    SCROLLBAR_WIDTH = 12


class AnimationTiming:
    """Animation duration constants (for future enhancement)"""
    INSTANT = 0
    FAST = 150
    NORMAL = 300
    SLOW = 500


class Icons:
    """Unicode icons for UI elements"""
    # Status
    SUCCESS = "✓"
    ERROR = "✗"
    WARNING = "⚠"
    INFO = "ℹ"

    # Actions
    LOADING = "⟳"
    SETTINGS = "⚙"
    HELP = "?"
    SEARCH = "🔍"

    # Navigation
    ARROW_DOWN = "▼"
    ARROW_UP = "▲"
    ARROW_LEFT = "◀"
    ARROW_RIGHT = "▶"

    # File
    FILE = "📄"
    FOLDER = "📁"
    IMAGE = "🖼"
    PDF = "📕"

    # License specific
    LICENSE = "🪪"
    BARCODE = "⚊⚊"
    PERSON = "👤"


def get_font_tuple(size: int = Typography.SIZE_BODY,
                   weight: str = Typography.WEIGHT_NORMAL,
                   family: str = Typography.FONT_FAMILY) -> Tuple[str, int, str]:
    """
    Get CustomTkinter font tuple

    Args:
        size: Font size in pixels
        weight: Font weight ('normal' or 'bold')
        family: Font family name

    Returns:
        Tuple of (family, size, weight)
    """
    return (family, size, weight)


def get_state_colors(state: str, theme: str = "dark") -> Dict[str, str]:
    """
    Get colors for validation states

    Args:
        state: One of 'untouched', 'typing', 'validating', 'valid', 'invalid', 'warning'
        theme: 'dark' or 'light'

    Returns:
        Dictionary with fg_color, border_color, text_color
    """
    theme_colors = ThemeColors.get_dark_theme() if theme == "dark" else ThemeColors.get_light_theme()

    state_configs = {
        "untouched": {
            "fg_color": theme_colors["bg_secondary"],
            "border_color": theme_colors["border"],
            "text_color": theme_colors["text_secondary"],
        },
        "typing": {
            "fg_color": theme_colors["bg_primary"],
            "border_color": ColorPalette.PRIMARY,
            "text_color": theme_colors["text_primary"],
        },
        "validating": {
            "fg_color": theme_colors["bg_primary"],
            "border_color": ColorPalette.WARNING,
            "text_color": theme_colors["text_primary"],
        },
        "valid": {
            "fg_color": theme_colors["bg_primary"],
            "border_color": ColorPalette.SUCCESS,
            "text_color": theme_colors["text_primary"],
        },
        "invalid": {
            "fg_color": theme_colors["bg_primary"],
            "border_color": ColorPalette.ERROR,
            "text_color": theme_colors["text_primary"],
        },
        "warning": {
            "fg_color": theme_colors["bg_primary"],
            "border_color": ColorPalette.WARNING,
            "text_color": theme_colors["text_primary"],
        },
    }

    return state_configs.get(state, state_configs["untouched"])
