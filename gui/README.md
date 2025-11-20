# AAMVA License Generator - GUI

Modern graphical user interface for the AAMVA License Generator, built with CustomTkinter.

## Features

### Three-Panel Layout
- **Configuration Sidebar**: All generation options in one place
- **Preview Panel**: Real-time preview of generated licenses
- **Status Bar**: Progress tracking and status messages

### Professional Design
- Dark and light theme support
- Responsive layout that adapts to window size
- Modern, clean UI following design best practices
- Color-coded status messages and validation

### User-Friendly Controls
- State selection dropdown with popular states
- Quantity input with validation
- Output format checkboxes (PDF, DOCX, ODT)
- Directory browser for output location
- Keyboard shortcuts for common actions

## Installation

### Prerequisites

```bash
# Install required Python packages
pip install customtkinter pillow
```

### Required Dependencies
- Python 3.8+
- customtkinter >= 5.2.0
- pillow >= 9.0.0

## Usage

### Running the GUI

From the project root directory:

```bash
python gui/app.py
```

Or make it executable and run directly:

```bash
chmod +x gui/app.py
./gui/app.py
```

### Keyboard Shortcuts

- `Ctrl+G` or `F5` - Generate licenses
- `Ctrl+Q` - Quit application

### Configuration Options

#### State Selection
- Choose a specific US state or territory
- Or check "Generate all states" to create one license per jurisdiction

#### Number of Licenses
- Enter quantity (1-1000)
- Recommended: 1-100 for best performance

#### Output Formats
- **PDF** - Avery 28371 business card template
- **DOCX** - Microsoft Word document
- **ODT** - OpenDocument format

#### Output Directory
- Specify where generated files will be saved
- Click folder icon to browse
- Default: `./output`

## Architecture

### Component Structure

```
gui/
├── app.py                  # Application entry point
├── main_window.py          # Main window layout
├── theme.py                # Theme management
├── styles.py               # Color system and constants
├── components/             # Reusable UI components
│   ├── sidebar.py          # Configuration sidebar
│   ├── preview_panel.py    # License preview area
│   └── status_bar.py       # Status and progress bar
└── README.md               # This file
```

### Design Principles

1. **Separation of Concerns**
   - UI components separate from business logic
   - Theme management decoupled from components
   - Reusable component architecture

2. **Responsive Design**
   - Grid-based layout
   - Adaptive sizing
   - Minimum window dimensions

3. **Theme Support**
   - Dark and light themes
   - System theme detection (future)
   - Centralized color management

4. **Accessibility**
   - Keyboard navigation
   - Clear visual feedback
   - Color-coded status messages

## Customization

### Changing Colors

Edit `gui/styles.py` to customize the color palette:

```python
class ColorPalette:
    PRIMARY = "#1F6FEB"      # Change accent color
    SUCCESS = "#238636"      # Change success color
    ERROR = "#DA3633"        # Change error color
    # ... more colors
```

### Adjusting Layout

Modify spacing and sizes in `gui/styles.py`:

```python
class ComponentStyles:
    SIDEBAR_WIDTH = 320      # Sidebar width
    WINDOW_DEFAULT_WIDTH = 1200  # Default window width
    # ... more dimensions
```

### Adding Components

1. Create new component in `gui/components/`
2. Extend `ctk.CTkFrame` or similar
3. Use theme manager for colors: `get_theme_manager()`
4. Import and use in `main_window.py`

## Integration with Backend

The GUI is designed to integrate with the existing license generation backend:

```python
# In main_window.py, replace the TODO in _on_generate_requested():

def _on_generate_requested(self, config):
    # ... validation ...

    # Call backend
    from generate_licenses import generate_batch

    try:
        results = generate_batch(
            state=config['state'],
            count=config['count'],
            output_dir=config['output_dir'],
            # ... more parameters
        )

        # Show results
        self._on_generation_complete(results)

    except Exception as e:
        self._on_generation_error(str(e))
```

## Troubleshooting

### CustomTkinter Not Found

```bash
pip install --upgrade customtkinter
```

### Window Too Small

The window has minimum dimensions (1000x700). If your screen is smaller:

```python
# Edit main_window.py
ComponentStyles.WINDOW_MIN_WIDTH = 800
ComponentStyles.WINDOW_MIN_HEIGHT = 600
```

### Theme Issues

Force a specific theme in `app.py`:

```python
ctk.set_appearance_mode("dark")  # or "light"
```

### Import Errors

Ensure you're running from the project root directory:

```bash
cd /path/to/aamva-id-faker
python gui/app.py
```

## Future Enhancements

### Planned Features
- [ ] Real-time validation of inputs
- [ ] Progress bar during generation
- [ ] Batch generation queue
- [ ] Configuration presets/templates
- [ ] Export settings
- [ ] Recent files menu
- [ ] Drag-and-drop file handling
- [ ] Multi-language support

### Potential Improvements
- Advanced configuration options
- License preview with zoom
- Barcode validation tools
- Export to additional formats
- Custom templates
- Plugin system

## Contributing

When contributing to the GUI:

1. Follow the existing code structure
2. Use the theme manager for all colors
3. Add type hints to all functions
4. Document new components
5. Test in both dark and light themes
6. Ensure responsive behavior

## License

MIT License - See LICENSE.md in project root

## Credits

Built with:
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) by Tom Schimansky
- Python 3.8+
- Pillow (PIL Fork)

---

**For legitimate testing purposes only**

This tool is designed for scanner validation, software testing, and training. Do not use for any illegal purposes.
