# GUI Installation Guide

## Quick Start

### Prerequisites

1. **Python 3.8 or higher**
   ```bash
   python --version
   ```

2. **tkinter** (usually included with Python)
   ```bash
   python -m tkinter  # Should open a small test window
   ```

   If tkinter is not installed:
   - **Ubuntu/Debian**: `sudo apt-get install python3-tk`
   - **Fedora/RedHat**: `sudo dnf install python3-tkinter`
   - **macOS**: Included with Python from python.org
   - **Windows**: Included with Python from python.org

3. **pip** (Python package installer)
   ```bash
   pip --version
   ```

### Installation Steps

#### Option 1: Using pip (Recommended)

```bash
# Navigate to project directory
cd /path/to/aamva-id-faker

# Install required packages
pip install customtkinter pillow

# Run the GUI
python gui/app.py
```

#### Option 2: Using virtual environment (Best Practice)

```bash
# Navigate to project directory
cd /path/to/aamva-id-faker

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Linux/Mac:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
pip install customtkinter pillow

# Run the GUI
python gui/app.py
```

#### Option 3: Using requirements file

Create `requirements-gui.txt`:
```
customtkinter>=5.2.0
pillow>=9.0.0
```

Then install:
```bash
pip install -r requirements-gui.txt
python gui/app.py
```

## Verification

### Test Imports

Before running the full GUI, verify all imports work:

```bash
python gui/test_imports.py
```

Expected output:
```
Testing GUI module imports...

✓ Importing customtkinter
✓ Importing PIL (Pillow)
✓ Importing gui.theme
  - ThemeManager class loaded
  - Theme manager initialized: dark mode
✓ Importing gui.styles
  - ColorPalette.PRIMARY = #1F6FEB
  - Spacing.LG = 16px
  - Typography.SIZE_BODY = 13pt
✓ Importing gui.components
  - ConfigurationSidebar loaded
  - PreviewPanel loaded
  - StatusBar loaded
✓ Importing gui.main_window
  - MainWindow class loaded
✓ Importing gui package
  - GUI package version: 2.0.0
✓ Testing theme functionality
  - Current theme: dark
  - Is dark: True
  - Theme colors: 10 defined
  - Primary button color: #1F6FEB

==================================================
SUCCESS: All imports working correctly!

The GUI is ready to run:
  python gui/app.py
```

### Manual Test

Run the application:
```bash
python gui/app.py
```

You should see:
- Window titled "AAMVA License Generator"
- Left sidebar with configuration options
- Right preview panel
- Bottom status bar
- Dark theme by default

## Troubleshooting

### ImportError: No module named 'tkinter'

**Problem**: tkinter is not installed

**Solution**:
- **Linux**: `sudo apt-get install python3-tk`
- **Mac**: Reinstall Python from python.org (not Homebrew)
- **Windows**: Reinstall Python and check "tcl/tk" option

### ImportError: No module named 'customtkinter'

**Problem**: customtkinter package not installed

**Solution**:
```bash
pip install customtkinter
```

### ImportError: No module named 'PIL'

**Problem**: Pillow (PIL) not installed

**Solution**:
```bash
pip install pillow
```

### Module 'gui' not found

**Problem**: Running from wrong directory

**Solution**: Run from project root:
```bash
cd /path/to/aamva-id-faker
python gui/app.py
```

### Window appears but crashes immediately

**Problem**: Missing dependencies or Python version too old

**Solution**:
1. Check Python version: `python --version` (need 3.8+)
2. Reinstall dependencies: `pip install --upgrade customtkinter pillow`
3. Check error messages in terminal

### Display Error on Linux

**Problem**: No display server (headless environment)

**Solution**:
- GUI requires a display server (X11, Wayland)
- Cannot run in purely headless environments (SSH without X forwarding)
- Use SSH with X forwarding: `ssh -X user@host`
- Or use the CLI version: `python generate_licenses.py`

### Permission Errors

**Problem**: Cannot create window or access display

**Solution**:
```bash
# On Linux, ensure DISPLAY is set
echo $DISPLAY  # Should show something like :0 or :1

# Grant display access if needed
xhost +local:
```

## Platform-Specific Notes

### Linux

- Requires X11 or Wayland display server
- May need to install additional font packages for best appearance
- Tested on Ubuntu 20.04+, Debian 11+, Fedora 35+

### macOS

- Works on macOS 10.14 (Mojave) and later
- Python from python.org recommended over Homebrew
- May show permission dialog on first run

### Windows

- Works on Windows 10 and later
- Python from python.org recommended
- High DPI displays automatically handled

## Development Setup

For GUI development:

```bash
# Install development dependencies
pip install customtkinter pillow pytest pytest-cov black mypy

# Run tests
python gui/test_imports.py

# Format code
black gui/

# Type checking
mypy gui/
```

## Performance Tips

### Faster Startup

The GUI starts almost instantly. If slow:
1. Check antivirus isn't scanning Python
2. Ensure running from SSD, not network drive
3. Use virtual environment for isolated dependencies

### Smoother Preview

For better image preview performance:
1. Ensure graphics drivers are up to date
2. Close other graphics-intensive applications
3. Use smaller batch sizes (<100) for generation

## Uninstallation

To remove the GUI (keeps generated files):

```bash
# Uninstall Python packages
pip uninstall customtkinter pillow

# Delete GUI directory (optional)
rm -rf gui/
```

To completely remove everything:

```bash
# Deactivate virtual environment if active
deactivate

# Remove project directory
cd ..
rm -rf aamva-id-faker/
```

## Next Steps

Once installed:

1. **Read the README**: `gui/README.md` for usage instructions
2. **Explore Architecture**: `gui/ARCHITECTURE.md` for technical details
3. **Run the GUI**: `python gui/app.py`
4. **Generate Licenses**: Configure and click "Generate Licenses"

## Support

### Common Questions

**Q: Can I run this without a graphical interface?**
A: Yes, use the CLI: `python generate_licenses.py --help`

**Q: Does this work on Raspberry Pi?**
A: Yes, but may be slow. Use Raspberry Pi OS with desktop environment.

**Q: Can I customize the appearance?**
A: Yes! Edit `gui/styles.py` to change colors, fonts, and spacing.

**Q: Is there a web version?**
A: Not yet. The GUI is desktop-only. Web version is planned for future.

**Q: Can I use this in Docker?**
A: Difficult. Docker containers are typically headless. Use CLI version instead.

### Getting Help

If you encounter issues:

1. Check this guide's troubleshooting section
2. Run `python gui/test_imports.py` to diagnose
3. Check terminal output for error messages
4. Ensure Python 3.8+ and dependencies installed
5. Try running CLI version to isolate GUI issues

---

**Version**: 2.0.0
**Last Updated**: 2025-11-20
**Minimum Python**: 3.8
**Tested Platforms**: Windows 10+, macOS 10.14+, Ubuntu 20.04+
