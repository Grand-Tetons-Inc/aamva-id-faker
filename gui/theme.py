"""
Theme Management for AAMVA License Generator

Handles dark/light theme switching and provides theme-aware
color and styling utilities.
"""

import customtkinter as ctk
from typing import Literal, Callable, List
from gui.styles import ThemeColors, ColorPalette


ThemeMode = Literal["dark", "light", "system"]


class ThemeManager:
    """
    Centralized theme management

    Handles theme switching and provides callbacks for components
    to update when theme changes.
    """

    def __init__(self):
        self._current_mode: ThemeMode = "dark"
        self._callbacks: List[Callable[[ThemeMode], None]] = []

        # Set initial CustomTkinter theme
        ctk.set_appearance_mode(self._current_mode)
        ctk.set_default_color_theme("blue")

    @property
    def current_mode(self) -> ThemeMode:
        """Get current theme mode"""
        return self._current_mode

    @property
    def is_dark(self) -> bool:
        """Check if current theme is dark"""
        if self._current_mode == "system":
            # In production, would detect system theme
            return ctk.get_appearance_mode() == "Dark"
        return self._current_mode == "dark"

    def get_colors(self) -> dict:
        """Get current theme colors"""
        if self.is_dark:
            return ThemeColors.get_dark_theme()
        else:
            return ThemeColors.get_light_theme()

    def set_mode(self, mode: ThemeMode):
        """
        Set theme mode and notify all listeners

        Args:
            mode: Theme mode ('dark', 'light', or 'system')
        """
        if mode not in ("dark", "light", "system"):
            raise ValueError(f"Invalid theme mode: {mode}")

        self._current_mode = mode
        ctk.set_appearance_mode(mode)

        # Notify all registered callbacks
        self._notify_callbacks()

    def toggle_theme(self):
        """Toggle between dark and light themes"""
        if self._current_mode == "dark":
            self.set_mode("light")
        else:
            self.set_mode("dark")

    def register_callback(self, callback: Callable[[ThemeMode], None]):
        """
        Register a callback to be notified of theme changes

        Args:
            callback: Function that takes theme mode as parameter
        """
        if callback not in self._callbacks:
            self._callbacks.append(callback)

    def unregister_callback(self, callback: Callable[[ThemeMode], None]):
        """
        Unregister a theme change callback

        Args:
            callback: Previously registered callback function
        """
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def _notify_callbacks(self):
        """Notify all registered callbacks of theme change"""
        for callback in self._callbacks:
            try:
                callback(self._current_mode)
            except Exception as e:
                print(f"Error in theme callback: {e}")

    def get_button_colors(self, variant: str = "primary") -> dict:
        """
        Get button color configuration for current theme

        Args:
            variant: Button variant ('primary', 'secondary', 'danger', 'success')

        Returns:
            Dictionary with fg_color, hover_color, text_color
        """
        colors = self.get_colors()

        variants = {
            "primary": {
                "fg_color": ColorPalette.PRIMARY,
                "hover_color": ColorPalette.PRIMARY_HOVER,
                "text_color": "#FFFFFF",
            },
            "secondary": {
                "fg_color": colors["bg_tertiary"],
                "hover_color": colors["hover"],
                "text_color": colors["text_primary"],
            },
            "danger": {
                "fg_color": ColorPalette.ERROR,
                "hover_color": "#C52A28",
                "text_color": "#FFFFFF",
            },
            "success": {
                "fg_color": ColorPalette.SUCCESS,
                "hover_color": "#1C6E2C",
                "text_color": "#FFFFFF",
            },
        }

        return variants.get(variant, variants["primary"])

    def get_input_colors(self) -> dict:
        """Get input field color configuration"""
        colors = self.get_colors()

        return {
            "fg_color": colors["bg_secondary"],
            "border_color": colors["border"],
            "text_color": colors["text_primary"],
            "placeholder_text_color": colors["text_secondary"],
        }

    def get_frame_colors(self, variant: str = "default") -> dict:
        """
        Get frame color configuration

        Args:
            variant: Frame variant ('default', 'card', 'sidebar')

        Returns:
            Dictionary with fg_color, border_color
        """
        colors = self.get_colors()

        variants = {
            "default": {
                "fg_color": colors["bg_primary"],
                "border_color": "transparent",
            },
            "card": {
                "fg_color": colors["bg_secondary"],
                "border_color": colors["border"],
            },
            "sidebar": {
                "fg_color": colors["bg_secondary"],
                "border_color": colors["border"],
            },
        }

        return variants.get(variant, variants["default"])

    def get_label_colors(self, variant: str = "default") -> dict:
        """
        Get label color configuration

        Args:
            variant: Label variant ('default', 'secondary', 'heading', 'error', 'success')

        Returns:
            Dictionary with text_color
        """
        colors = self.get_colors()

        variants = {
            "default": {
                "text_color": colors["text_primary"],
            },
            "secondary": {
                "text_color": colors["text_secondary"],
            },
            "heading": {
                "text_color": colors["text_primary"],
            },
            "error": {
                "text_color": ColorPalette.ERROR,
            },
            "success": {
                "text_color": ColorPalette.SUCCESS,
            },
            "warning": {
                "text_color": ColorPalette.WARNING,
            },
        }

        return variants.get(variant, variants["default"])


# Global theme manager instance
_theme_manager = None


def get_theme_manager() -> ThemeManager:
    """
    Get the global theme manager instance

    Returns:
        ThemeManager singleton instance
    """
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager
