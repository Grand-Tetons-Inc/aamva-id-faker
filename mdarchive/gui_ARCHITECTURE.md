# GUI Architecture Documentation

## Overview

The AAMVA License Generator GUI is built with a modern, component-based architecture using CustomTkinter. The design emphasizes separation of concerns, reusability, and maintainability.

## Directory Structure

```
gui/
├── __init__.py              # Package initialization
├── app.py                   # Application entry point (executable)
├── main_window.py           # Main window with three-panel layout
├── theme.py                 # Theme management (dark/light)
├── styles.py                # Color system and styling constants
├── components/              # Reusable UI components
│   ├── __init__.py          # Component package
│   ├── sidebar.py           # Configuration sidebar
│   ├── preview_panel.py     # License preview panel
│   └── status_bar.py        # Status bar with progress
├── README.md                # User documentation
└── ARCHITECTURE.md          # This file
```

## Component Hierarchy

```
MainWindow (CTk)
├── ConfigurationSidebar (CTkScrollableFrame)
│   ├── State Dropdown (CTkOptionMenu)
│   ├── Quantity Entry (CTkEntry)
│   ├── Format Checkboxes (CTkCheckBox)
│   ├── Output Directory (CTkEntry + CTkButton)
│   └── Generate Button (CTkButton)
│
├── PreviewPanel (CTkFrame)
│   ├── Image Container (CTkFrame)
│   │   └── Image Label (CTkLabel)
│   └── Data Textbox (CTkTextbox)
│
└── StatusBar (CTkFrame)
    ├── Status Label (CTkLabel)
    └── Progress Bar (CTkProgressBar)
```

## Core Components

### 1. Theme System (`theme.py`)

**Purpose**: Centralized theme management with dark/light mode support

**Key Features**:
- Singleton `ThemeManager` class
- Theme switching with callbacks
- Color palette management
- Component-specific color helpers

**Usage**:
```python
from gui.theme import get_theme_manager

theme = get_theme_manager()
theme.set_mode("dark")  # or "light"
colors = theme.get_colors()
button_colors = theme.get_button_colors("primary")
```

### 2. Style System (`styles.py`)

**Purpose**: Design system with colors, typography, spacing, and component styles

**Key Classes**:
- `ColorPalette`: Color constants for all UI elements
- `Spacing`: Consistent spacing scale (XS to HUGE)
- `Typography`: Font configurations and sizes
- `ComponentStyles`: Component-specific dimensions
- `Icons`: Unicode icons for UI

**Usage**:
```python
from gui.styles import ColorPalette, Spacing, get_font_tuple

# Colors
primary_color = ColorPalette.PRIMARY

# Spacing
padding = Spacing.LG  # 16px

# Typography
title_font = get_font_tuple(
    size=Typography.SIZE_TITLE,
    weight=Typography.WEIGHT_BOLD
)
```

### 3. Configuration Sidebar (`components/sidebar.py`)

**Purpose**: Left panel with all configuration options

**Features**:
- State selection dropdown
- Quantity input with validation
- Output format checkboxes (PDF, DOCX, ODT)
- Output directory browser
- Generate button
- Automatic enable/disable during generation

**Public Methods**:
```python
sidebar = ConfigurationSidebar(parent, generate_callback=callback)

# Get current configuration
config = sidebar.get_configuration()
# Returns: {
#     'state': 'CA',
#     'count': 10,
#     'output_dir': './output',
#     'generate_pdf': True,
#     'generate_docx': True,
#     'generate_odt': False,
#     'all_states': False
# }

# Set UI state
sidebar.set_generating_state(is_generating=True)
```

### 4. Preview Panel (`components/preview_panel.py`)

**Purpose**: Right panel displaying license preview and data

**Features**:
- Large license image display with auto-scaling
- Scrollable license data textbox
- Placeholder state when empty
- Loading state during generation
- Error state for failures

**Public Methods**:
```python
preview = PreviewPanel(parent)

# Show license
preview.show_license({
    'image_path': '/path/to/image.png',
    'name': 'JOHN DOE',
    'dob': '1990-05-15',
    # ... more fields
})

# Show states
preview.show_loading()
preview.show_error("Error message")
preview.clear_preview()
```

### 5. Status Bar (`components/status_bar.py`)

**Purpose**: Bottom bar showing status and progress

**Features**:
- Color-coded status messages (info, success, warning, error)
- Progress bar (shown/hidden as needed)
- Icon indicators

**Public Methods**:
```python
status_bar = StatusBar(parent)

# Set status
status_bar.set_info("Ready")
status_bar.set_success("Generation complete")
status_bar.set_warning("Large batch may be slow")
status_bar.set_error("Generation failed")

# Progress
status_bar.set_generating("Generating...")
status_bar.set_progress(0.5)  # 50%
status_bar.hide_progress()
```

### 6. Main Window (`main_window.py`)

**Purpose**: Main application window coordinating all components

**Features**:
- Three-panel layout (sidebar, preview, status bar)
- Keyboard shortcuts (Ctrl+G, Ctrl+Q, F5)
- Configuration validation
- Generation workflow orchestration
- Theme toggle
- About dialog

**Key Methods**:
```python
app = MainWindow()

# Internal workflow
app._on_generate_requested(config)
app._on_generation_complete(config)
app._on_generation_error(error_message)

# Public methods
app.toggle_theme()
app.show_about_dialog()
```

## Data Flow

### Generation Workflow

```
User clicks Generate Button
    ↓
Sidebar.generate_callback()
    ↓
MainWindow._on_generate_requested()
    ↓
1. Get configuration from sidebar
2. Validate configuration
3. Set generating state (disable UI)
4. Show loading in preview
5. Update status bar
6. Call backend generation
    ↓
Backend generates licenses
    ↓
MainWindow._on_generation_complete()
    ↓
1. Reset generating state (enable UI)
2. Update status bar with success
3. Show first license in preview
4. Hide progress bar
```

### Theme Change Workflow

```
User toggles theme
    ↓
ThemeManager.toggle_theme()
    ↓
ThemeManager._notify_callbacks()
    ↓
Each component's _on_theme_change()
    ↓
Components update their colors
```

## Design Patterns

### 1. Component Pattern

Each UI component is a self-contained class extending CustomTkinter widgets:

```python
class MyComponent(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._create_widgets()

    def _create_widgets(self):
        # Build UI
        pass
```

### 2. Callback Pattern

Components communicate via callbacks rather than direct references:

```python
sidebar = ConfigurationSidebar(
    parent,
    generate_callback=self._on_generate_requested
)
```

### 3. Observer Pattern (Theme)

Theme changes notify all registered observers:

```python
theme.register_callback(self._on_theme_change)
```

### 4. Singleton Pattern (Theme Manager)

Single global theme manager instance:

```python
_theme_manager = None

def get_theme_manager():
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager
```

## Styling Guidelines

### Colors

Always use theme manager for colors:

```python
# Good
theme = get_theme_manager()
colors = theme.get_colors()
widget.configure(fg_color=colors["bg_primary"])

# Bad
widget.configure(fg_color="#0D1117")  # Hardcoded
```

### Spacing

Use spacing constants from `styles.py`:

```python
# Good
widget.pack(pady=Spacing.LG, padx=Spacing.MD)

# Bad
widget.pack(pady=16, padx=12)  # Magic numbers
```

### Typography

Use `get_font_tuple()` helper:

```python
# Good
font = get_font_tuple(
    size=Typography.SIZE_TITLE,
    weight=Typography.WEIGHT_BOLD
)

# Bad
font = ("Segoe UI", 18, "bold")  # Hardcoded
```

## Responsive Behavior

### Grid Weights

Configure grid weights for responsive resizing:

```python
self.grid_rowconfigure(0, weight=1)     # Expands
self.grid_rowconfigure(1, weight=0)     # Fixed size
self.grid_columnconfigure(0, weight=1)  # Expands
```

### Minimum Sizes

Set minimum window dimensions:

```python
self.minsize(
    ComponentStyles.WINDOW_MIN_WIDTH,
    ComponentStyles.WINDOW_MIN_HEIGHT
)
```

## Error Handling

### Validation

Validate inputs before processing:

```python
error = self._validate_configuration(config)
if error:
    self.status_bar.set_error(error)
    return
```

### Try-Catch

Wrap risky operations:

```python
try:
    result = risky_operation()
except Exception as e:
    self._on_generation_error(str(e))
```

## Future Extensions

### Adding a New Component

1. Create file in `gui/components/`
2. Extend appropriate CustomTkinter class
3. Use theme manager for colors
4. Add to `components/__init__.py`
5. Import and use in `main_window.py`

Example:

```python
# gui/components/settings_panel.py
import customtkinter as ctk
from gui.theme import get_theme_manager

class SettingsPanel(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        theme = get_theme_manager()
        super().__init__(
            master,
            **theme.get_frame_colors("card"),
            **kwargs
        )
        self.theme = theme
        self._create_widgets()
        theme.register_callback(self._on_theme_change)

    def _create_widgets(self):
        # Build settings UI
        pass

    def _on_theme_change(self, theme_mode):
        # Update colors
        pass
```

### Adding a New Theme

1. Add colors to `ThemeColors` in `styles.py`
2. Update `ThemeManager.get_colors()`
3. Test all components in new theme

## Testing

### Manual Testing

Run the application:

```bash
python gui/app.py
```

Test checklist:
- [ ] All components render correctly
- [ ] Theme toggle works
- [ ] Sidebar controls function
- [ ] Preview displays correctly
- [ ] Status bar updates
- [ ] Window resizes properly
- [ ] Keyboard shortcuts work

### Unit Testing (Future)

```python
# tests/test_gui_components.py
import unittest
from gui.components import ConfigurationSidebar

class TestSidebar(unittest.TestCase):
    def test_get_configuration(self):
        # Test configuration extraction
        pass
```

## Performance Considerations

### Image Loading

Images are scaled to fit container:

```python
# Calculate scale ratio
scale_ratio = min(width_ratio, height_ratio, 1.0)
new_size = (int(width * scale_ratio), int(height * scale_ratio))
image = image.resize(new_size, Image.Resampling.LANCZOS)
```

### Memory Management

- Images are references stored to prevent garbage collection
- Textboxes use `state="disabled"` when not editable
- Progress bars hidden when not needed

## Accessibility

### Keyboard Navigation

- Tab order follows logical flow
- Keyboard shortcuts for common actions
- Enter key on inputs triggers actions

### Visual Feedback

- Color-coded status messages
- Icons supplement text
- Clear focus indicators

### Future Improvements

- Screen reader support (ARIA labels)
- High contrast mode
- Keyboard-only operation
- Tooltips for all controls

## Integration Points

### Backend Integration

The GUI is designed to call the existing backend:

```python
# In main_window.py
from generate_licenses import generate_batch

results = generate_batch(
    state=config['state'],
    count=config['count'],
    output_dir=config['output_dir'],
    progress_callback=self._update_progress
)
```

### Progress Callbacks

Backend should support progress callbacks:

```python
def generate_batch(..., progress_callback=None):
    for i, license in enumerate(licenses):
        # Generate license
        if progress_callback:
            progress_callback(i / total)
```

## Dependencies

### Required Packages

```
customtkinter >= 5.2.0
pillow >= 9.0.0
darkdetect >= 0.8.0 (installed with customtkinter)
```

### Optional Packages

```
# For future enhancements
pytest  # Unit testing
pytest-cov  # Coverage reporting
```

## Best Practices

### Do's

- ✅ Use theme manager for all colors
- ✅ Use spacing constants for consistency
- ✅ Register theme callbacks
- ✅ Validate inputs before processing
- ✅ Provide clear error messages
- ✅ Use type hints
- ✅ Document public methods

### Don'ts

- ❌ Hardcode colors
- ❌ Use magic numbers for spacing
- ❌ Mix business logic with UI code
- ❌ Create circular dependencies
- ❌ Ignore exceptions
- ❌ Use global variables (except theme manager)
- ❌ Block the UI thread with long operations

## Maintenance

### Code Style

Follow PEP 8 with these specifics:
- Line length: 100 characters
- Indentation: 4 spaces
- Quotes: Double quotes for strings
- Docstrings: Google style

### Version Control

- Commit atomic changes
- Write descriptive commit messages
- Test before committing

### Documentation

- Update this file when architecture changes
- Update README.md for user-facing changes
- Add docstrings to all public methods

---

**Last Updated**: 2025-11-20
**Version**: 2.0.0
