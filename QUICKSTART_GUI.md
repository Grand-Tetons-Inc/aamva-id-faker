# GUI Quick Start Guide

## Installation (2 minutes)

```bash
# Install dependencies
pip install customtkinter pillow

# Verify installation
python gui/test_imports.py
```

Expected output: ✅ "SUCCESS: All imports working correctly!"

## Running the GUI (10 seconds)

```bash
python gui/app.py
```

## Using the GUI (1 minute)

### Three-Panel Layout

```
┌────────────────────┬─────────────────────────┐
│                    │                         │
│  CONFIGURATION     │    PREVIEW PANEL        │
│  SIDEBAR           │    (License Display)    │
│                    │                         │
│  - State: [CA ▼]   │  [License Image]        │
│  - Count: [10]     │                         │
│  - Formats:        │  License Data:          │
│    ☑ PDF          │  Name: JOHN DOE         │
│    ☑ DOCX         │  DOB: 1990-05-15        │
│    ☐ ODT          │  ...                    │
│  - Output: [...]   │                         │
│                    │                         │
│  [Generate]        │                         │
│                    │                         │
├────────────────────┴─────────────────────────┤
│  Status: Ready                    [Progress] │
└──────────────────────────────────────────────┘
```

### Quick Workflow

1. **Select State**: Choose from dropdown (default: CA)
2. **Set Quantity**: Enter number 1-1000 (default: 10)
3. **Choose Formats**: Check PDF, DOCX, or ODT
4. **Set Output**: Browse for directory (default: ./output)
5. **Generate**: Click button or press F5
6. **View Results**: See preview in right panel

### Keyboard Shortcuts

- `F5` or `Ctrl+G` - Generate licenses
- `Ctrl+Q` - Quit application

## Features

### Visual Design
- Modern dark theme (default)
- Light theme available
- Professional color palette
- Responsive layout

### Configuration Options
- 20+ US states in dropdown
- "All states" checkbox for batch generation
- Quantity: 1-1000 licenses
- Multiple output formats: PDF, DOCX, ODT
- Directory browser for output location

### Preview Panel
- Auto-scaled license image
- Complete license data display
- Loading indicators
- Error messages

### Status Bar
- Color-coded status messages
- Progress bar during generation
- Clear visual feedback

## File Structure

```
gui/
├── app.py                   # ← Run this file
├── main_window.py           # Main window
├── theme.py                 # Theme system
├── styles.py                # Design system
├── components/              # UI components
│   ├── sidebar.py
│   ├── preview_panel.py
│   └── status_bar.py
├── README.md                # Full documentation
├── ARCHITECTURE.md          # Technical details
├── INSTALLATION.md          # Setup guide
└── test_imports.py          # Verify installation
```

## Troubleshooting

### "No module named 'customtkinter'"
```bash
pip install customtkinter
```

### "No module named 'tkinter'"
- **Ubuntu/Debian**: `sudo apt-get install python3-tk`
- **macOS**: Install Python from python.org
- **Windows**: Reinstall Python with tcl/tk option

### Window doesn't appear
- Requires display server (X11/Wayland)
- Cannot run in headless SSH
- Use `ssh -X` for X forwarding

### Import errors
```bash
# Run from project root, not gui directory
cd /path/to/aamva-id-faker
python gui/app.py
```

## Next Steps

Once the GUI is running:

1. **Read full docs**: `gui/README.md`
2. **Explore architecture**: `gui/ARCHITECTURE.md`
3. **Customize appearance**: Edit `gui/styles.py`
4. **Connect backend**: Modify `gui/main_window.py`

## Support

- **User Guide**: `gui/README.md`
- **Setup Help**: `gui/INSTALLATION.md`
- **Developer Docs**: `gui/ARCHITECTURE.md`
- **Test Installation**: `python gui/test_imports.py`

## Quick Stats

- **Files**: 13 (9 Python, 4 Markdown)
- **Lines**: 3,302 total
- **Components**: 3 reusable
- **Themes**: Dark + Light
- **Dependencies**: 2 (customtkinter, pillow)

---

**Version**: 2.0.0
**Platform**: Windows, macOS, Linux
**Python**: 3.8+
**License**: MIT
