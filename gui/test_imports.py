#!/usr/bin/env python3
"""
Test GUI Module Imports

Verifies that all GUI modules can be imported successfully
without launching the actual GUI window.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_imports():
    """Test all GUI module imports"""
    print("Testing GUI module imports...\n")

    errors = []

    # Test 1: Core modules
    try:
        print("✓ Importing customtkinter")
        import customtkinter as ctk
    except ImportError as e:
        errors.append(f"✗ customtkinter: {e}")
        print(f"✗ customtkinter: {e}")

    try:
        print("✓ Importing PIL (Pillow)")
        from PIL import Image
    except ImportError as e:
        errors.append(f"✗ PIL: {e}")
        print(f"✗ PIL: {e}")

    # Test 2: Theme system
    try:
        print("✓ Importing gui.theme")
        from gui.theme import get_theme_manager, ThemeManager
        print("  - ThemeManager class loaded")
        theme = get_theme_manager()
        print(f"  - Theme manager initialized: {theme.current_mode} mode")
    except Exception as e:
        errors.append(f"✗ gui.theme: {e}")
        print(f"✗ gui.theme: {e}")

    # Test 3: Style system
    try:
        print("✓ Importing gui.styles")
        from gui.styles import (
            ColorPalette, Spacing, Typography,
            ComponentStyles, get_font_tuple
        )
        print(f"  - ColorPalette.PRIMARY = {ColorPalette.PRIMARY}")
        print(f"  - Spacing.LG = {Spacing.LG}px")
        print(f"  - Typography.SIZE_BODY = {Typography.SIZE_BODY}pt")
    except Exception as e:
        errors.append(f"✗ gui.styles: {e}")
        print(f"✗ gui.styles: {e}")

    # Test 4: Components
    try:
        print("✓ Importing gui.components")
        from gui.components import (
            ConfigurationSidebar,
            PreviewPanel,
            StatusBar
        )
        print("  - ConfigurationSidebar loaded")
        print("  - PreviewPanel loaded")
        print("  - StatusBar loaded")
    except Exception as e:
        errors.append(f"✗ gui.components: {e}")
        print(f"✗ gui.components: {e}")

    # Test 5: Main window
    try:
        print("✓ Importing gui.main_window")
        from gui.main_window import MainWindow
        print("  - MainWindow class loaded")
    except Exception as e:
        errors.append(f"✗ gui.main_window: {e}")
        print(f"✗ gui.main_window: {e}")

    # Test 6: GUI package
    try:
        print("✓ Importing gui package")
        import gui
        print(f"  - GUI package version: {gui.__version__}")
    except Exception as e:
        errors.append(f"✗ gui package: {e}")
        print(f"✗ gui package: {e}")

    # Test 7: Theme functionality
    try:
        print("✓ Testing theme functionality")
        from gui.theme import get_theme_manager

        theme = get_theme_manager()
        print(f"  - Current theme: {theme.current_mode}")
        print(f"  - Is dark: {theme.is_dark}")

        # Test color retrieval
        colors = theme.get_colors()
        print(f"  - Theme colors: {len(colors)} defined")

        # Test button colors
        button_colors = theme.get_button_colors("primary")
        print(f"  - Primary button color: {button_colors['fg_color']}")

    except Exception as e:
        errors.append(f"✗ Theme functionality: {e}")
        print(f"✗ Theme functionality: {e}")

    # Summary
    print("\n" + "="*50)
    if errors:
        print(f"FAILED: {len(errors)} error(s) found")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("SUCCESS: All imports working correctly!")
        print("\nThe GUI is ready to run:")
        print("  python gui/app.py")
        return True


if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
