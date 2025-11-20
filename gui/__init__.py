"""
AAMVA License Generator GUI Package

Modern CustomTkinter-based graphical user interface.
"""

from gui.main_window import MainWindow
from gui.theme import get_theme_manager, ThemeManager

__version__ = "2.0.0"

__all__ = [
    "MainWindow",
    "get_theme_manager",
    "ThemeManager",
]
