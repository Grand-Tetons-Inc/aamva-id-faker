"""
Status Bar Component

Bottom status bar showing current status and progress.
"""

import customtkinter as ctk
from typing import Literal
from gui.styles import (
    ComponentStyles, Spacing, Typography,
    get_font_tuple, Icons, ColorPalette
)
from gui.theme import get_theme_manager


StatusLevel = Literal["info", "success", "warning", "error"]


class StatusBar(ctk.CTkFrame):
    """
    Status bar with status message and progress bar

    Features:
    - Status icon and message
    - Progress bar
    - Color-coded by status level
    """

    def __init__(self, master, **kwargs):
        """
        Initialize status bar

        Args:
            master: Parent widget
        """
        # Get theme colors
        theme = get_theme_manager()
        frame_colors = theme.get_frame_colors("card")

        super().__init__(
            master,
            height=ComponentStyles.STATUS_BAR_HEIGHT,
            fg_color=frame_colors["fg_color"],
            corner_radius=0,
            border_width=1,
            border_color=frame_colors["border_color"],
            **kwargs
        )

        self.theme = theme

        # Configure grid
        self.grid_columnconfigure(0, weight=1)  # Status message
        self.grid_columnconfigure(1, weight=2)  # Progress bar
        self.grid_rowconfigure(0, weight=1)

        # Build UI
        self._create_widgets()

        # Register theme callback
        self.theme.register_callback(self._on_theme_change)

    def _create_widgets(self):
        """Create status bar widgets"""
        # Status message label
        self.status_label = ctk.CTkLabel(
            self,
            text=f"{Icons.INFO} Ready",
            font=get_font_tuple(size=Typography.SIZE_SMALL),
            anchor="w",
            **self.theme.get_label_colors("default")
        )
        self.status_label.grid(
            row=0,
            column=0,
            padx=(Spacing.LG, Spacing.MD),
            sticky="ew"
        )

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            self,
            height=ComponentStyles.PROGRESS_BAR_HEIGHT,
            corner_radius=ComponentStyles.PROGRESS_BAR_CORNER_RADIUS,
            mode="determinate"
        )
        self.progress_bar.grid(
            row=0,
            column=1,
            padx=(Spacing.MD, Spacing.LG),
            sticky="ew"
        )
        self.progress_bar.set(0)

        # Hide progress bar initially
        self.progress_bar.grid_remove()

    def set_status(self,
                   message: str,
                   level: StatusLevel = "info",
                   show_progress: bool = False):
        """
        Set status message

        Args:
            message: Status message to display
            level: Status level (info, success, warning, error)
            show_progress: Whether to show progress bar
        """
        # Get icon for level
        icon = self._get_icon_for_level(level)

        # Get color for level
        color = self._get_color_for_level(level)

        # Update label
        self.status_label.configure(
            text=f"{icon} {message}",
            text_color=color
        )

        # Show/hide progress bar
        if show_progress:
            self.progress_bar.grid()
        else:
            self.progress_bar.grid_remove()

    def set_progress(self, value: float):
        """
        Set progress bar value

        Args:
            value: Progress value between 0.0 and 1.0
        """
        if 0.0 <= value <= 1.0:
            self.progress_bar.set(value)

    def show_progress(self):
        """Show progress bar"""
        self.progress_bar.grid()

    def hide_progress(self):
        """Hide progress bar"""
        self.progress_bar.grid_remove()

    def reset(self):
        """Reset status bar to default state"""
        self.set_status("Ready", "info", show_progress=False)
        self.set_progress(0)

    def set_info(self, message: str):
        """Set info status"""
        self.set_status(message, "info", show_progress=False)

    def set_success(self, message: str):
        """Set success status"""
        self.set_status(message, "success", show_progress=False)

    def set_warning(self, message: str):
        """Set warning status"""
        self.set_status(message, "warning", show_progress=False)

    def set_error(self, message: str):
        """Set error status"""
        self.set_status(message, "error", show_progress=False)

    def set_generating(self, message: str = "Generating licenses..."):
        """Set generating status with progress bar"""
        self.set_status(message, "info", show_progress=True)
        self.set_progress(0)

    def _get_icon_for_level(self, level: StatusLevel) -> str:
        """Get icon for status level"""
        icons = {
            "info": Icons.INFO,
            "success": Icons.SUCCESS,
            "warning": Icons.WARNING,
            "error": Icons.ERROR,
        }
        return icons.get(level, Icons.INFO)

    def _get_color_for_level(self, level: StatusLevel) -> str:
        """Get color for status level"""
        colors = {
            "info": self.theme.get_colors()["text_primary"],
            "success": ColorPalette.SUCCESS,
            "warning": ColorPalette.WARNING,
            "error": ColorPalette.ERROR,
        }
        return colors.get(level, self.theme.get_colors()["text_primary"])

    def _on_theme_change(self, theme_mode: str):
        """Handle theme change event"""
        # Update frame colors
        card_colors = self.theme.get_frame_colors("card")
        self.configure(
            fg_color=card_colors["fg_color"],
            border_color=card_colors["border_color"]
        )
