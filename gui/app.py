#!/usr/bin/env python3
"""
AAMVA License Generator - GUI Application

Modern graphical user interface for generating AAMVA driver's licenses
for testing, scanner validation, and training purposes.

Usage:
    python gui/app.py

Or make executable and run directly:
    chmod +x gui/app.py
    ./gui/app.py
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from gui.main_window import MainWindow
from gui.theme import get_theme_manager


def main():
    """
    Main application entry point
    """
    # Set CustomTkinter appearance defaults
    ctk.set_appearance_mode("dark")  # "dark", "light", or "system"
    ctk.set_default_color_theme("blue")  # "blue", "dark-blue", "green"

    # Initialize theme manager
    theme = get_theme_manager()
    theme.set_mode("dark")

    # Create and run application
    app = MainWindow()

    # Start main event loop
    app.mainloop()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
