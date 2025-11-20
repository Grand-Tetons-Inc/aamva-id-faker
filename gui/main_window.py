"""
Main Application Window

Combines all components into the main three-panel layout.
"""

import customtkinter as ctk
from typing import Optional, Dict, Any
from gui.components import ConfigurationSidebar, PreviewPanel, StatusBar
from gui.styles import ComponentStyles, Spacing, Typography, get_font_tuple
from gui.theme import get_theme_manager


class MainWindow(ctk.CTk):
    """
    Main application window with three-panel layout

    Layout:
    +------------------+-------------------------+
    |                  |                         |
    |   Sidebar        |    Preview Panel        |
    |   (Config)       |    (License Display)    |
    |                  |                         |
    +------------------+-------------------------+
    |            Status Bar                      |
    +--------------------------------------------+
    """

    def __init__(self):
        """Initialize main window"""
        super().__init__()

        # Get theme manager
        self.theme = get_theme_manager()

        # Window configuration
        self._configure_window()

        # Create main layout
        self._create_layout()

        # Bind events
        self._bind_events()

        # Update status
        self.status_bar.set_info("Ready to generate licenses")

    def _configure_window(self):
        """Configure main window properties"""
        # Window title
        self.title("AAMVA License Generator")

        # Window size
        self.geometry(
            f"{ComponentStyles.WINDOW_DEFAULT_WIDTH}x"
            f"{ComponentStyles.WINDOW_DEFAULT_HEIGHT}"
        )

        # Minimum size
        self.minsize(
            ComponentStyles.WINDOW_MIN_WIDTH,
            ComponentStyles.WINDOW_MIN_HEIGHT
        )

        # Configure grid weights for responsive layout
        self.grid_rowconfigure(0, weight=1)    # Main content area
        self.grid_rowconfigure(1, weight=0)    # Status bar
        self.grid_columnconfigure(0, weight=0)  # Sidebar
        self.grid_columnconfigure(1, weight=1)  # Preview panel

    def _create_layout(self):
        """Create main layout with all components"""
        # Sidebar (left panel)
        self.sidebar = ConfigurationSidebar(
            self,
            generate_callback=self._on_generate_requested
        )
        self.sidebar.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        # Preview panel (right panel)
        self.preview_panel = PreviewPanel(self)
        self.preview_panel.grid(
            row=0,
            column=1,
            sticky="nsew"
        )

        # Status bar (bottom)
        self.status_bar = StatusBar(self)
        self.status_bar.grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="ew"
        )

    def _bind_events(self):
        """Bind keyboard shortcuts and events"""
        # Keyboard shortcuts
        self.bind("<Control-q>", lambda e: self.quit())
        self.bind("<Control-g>", lambda e: self._on_generate_requested())
        self.bind("<F5>", lambda e: self._on_generate_requested())

        # Window close event
        self.protocol("WM_DELETE_WINDOW", self._on_window_close)

    def _on_generate_requested(self, config: Optional[Dict[str, Any]] = None):
        """
        Handle generate button click

        Args:
            config: Configuration dictionary from sidebar (optional)
        """
        if config is None:
            config = self.sidebar.get_configuration()

        # Validate configuration
        validation_error = self._validate_configuration(config)
        if validation_error:
            self.status_bar.set_error(validation_error)
            return

        # Update UI to generating state
        self._set_generating_state(True)

        # Show loading in preview
        self.preview_panel.show_loading()

        # Update status
        self.status_bar.set_generating("Generating licenses...")

        # TODO: Call actual generation logic here
        # For now, just simulate with a timer
        self.after(2000, lambda: self._on_generation_complete(config))

    def _on_generation_complete(self, config: Dict[str, Any]):
        """
        Handle generation completion

        Args:
            config: Configuration that was used
        """
        # Reset UI state
        self._set_generating_state(False)

        # Hide progress
        self.status_bar.hide_progress()

        # Show success status
        count = config.get('count', 0)
        state = config.get('state', 'all states')
        self.status_bar.set_success(
            f"Generated {count} license(s) for {state}"
        )

        # Show sample license in preview
        # TODO: Show actual generated license
        sample_license = self._create_sample_license_data(config)
        self.preview_panel.show_license(sample_license)

    def _on_generation_error(self, error_message: str):
        """
        Handle generation error

        Args:
            error_message: Error message to display
        """
        # Reset UI state
        self._set_generating_state(False)

        # Hide progress
        self.status_bar.hide_progress()

        # Show error status
        self.status_bar.set_error(f"Generation failed: {error_message}")

        # Show error in preview
        self.preview_panel.show_error(error_message)

    def _validate_configuration(self, config: Dict[str, Any]) -> Optional[str]:
        """
        Validate configuration

        Args:
            config: Configuration dictionary

        Returns:
            Error message if validation fails, None if valid
        """
        # Validate count
        count = config.get('count')
        if not count or count < 1:
            return "Number of licenses must be at least 1"
        if count > 1000:
            return "Number of licenses cannot exceed 1000"

        # Validate output directory
        output_dir = config.get('output_dir')
        if not output_dir:
            return "Output directory is required"

        # Validate at least one format is selected
        if not (config.get('generate_pdf') or
                config.get('generate_docx') or
                config.get('generate_odt')):
            return "At least one output format must be selected"

        return None

    def _set_generating_state(self, is_generating: bool):
        """
        Set UI state for generating

        Args:
            is_generating: True if currently generating
        """
        # Update sidebar controls
        self.sidebar.set_generating_state(is_generating)

        # Update cursor
        if is_generating:
            self.configure(cursor="watch")
        else:
            self.configure(cursor="")

    def _create_sample_license_data(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create sample license data for preview

        Args:
            config: Configuration dictionary

        Returns:
            Sample license data dictionary
        """
        state = config.get('state', 'CA')
        if state is None:
            state = 'CA'

        return {
            'name': 'JOHN DOE',
            'first_name': 'JOHN',
            'last_name': 'DOE',
            'dob': '1990-05-15',
            'sex': 'M',
            'license_number': 'A1234567',
            'state': state,
            'issue_date': '2023-01-10',
            'expiration_date': '2028-01-10',
            'license_class': 'C',
            'address': '123 Main Street',
            'city': 'Los Angeles',
            'zip': '90001',
            'height': '5\'10"',
            'weight': '180 lbs',
            'eye_color': 'BRO',
            'hair_color': 'BRO',
            'veteran': False,
            'organ_donor': True,
        }

    def _on_window_close(self):
        """Handle window close event"""
        # TODO: Add confirmation dialog if generation in progress
        # TODO: Save window size and position to config

        # Cleanup and exit
        self.quit()

    def show_about_dialog(self):
        """Show about dialog"""
        about_window = ctk.CTkToplevel(self)
        about_window.title("About")
        about_window.geometry("400x300")
        about_window.transient(self)
        about_window.grab_set()

        # Center on parent
        about_window.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (about_window.winfo_width() // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (about_window.winfo_height() // 2)
        about_window.geometry(f"+{x}+{y}")

        # Content frame
        content = ctk.CTkFrame(about_window, fg_color="transparent")
        content.pack(expand=True, fill="both", padx=Spacing.XL, pady=Spacing.XL)

        # Title
        title = ctk.CTkLabel(
            content,
            text="AAMVA License Generator",
            font=get_font_tuple(size=Typography.SIZE_HEADING, weight=Typography.WEIGHT_BOLD),
            **self.theme.get_label_colors("heading")
        )
        title.pack(pady=(0, Spacing.MD))

        # Version
        version = ctk.CTkLabel(
            content,
            text="Version 2.0.0",
            font=get_font_tuple(size=Typography.SIZE_BODY),
            **self.theme.get_label_colors("secondary")
        )
        version.pack(pady=(0, Spacing.LG))

        # Description
        description = ctk.CTkLabel(
            content,
            text=(
                "Generate test driver's licenses for AAMVA barcode\n"
                "scanner validation, software testing, and training.\n\n"
                "For legitimate testing purposes only."
            ),
            font=get_font_tuple(size=Typography.SIZE_BODY),
            justify="center",
            **self.theme.get_label_colors("default")
        )
        description.pack(pady=(0, Spacing.LG))

        # License
        license_text = ctk.CTkLabel(
            content,
            text="MIT License",
            font=get_font_tuple(size=Typography.SIZE_SMALL),
            **self.theme.get_label_colors("secondary")
        )
        license_text.pack(pady=(0, Spacing.MD))

        # Close button
        close_btn = ctk.CTkButton(
            content,
            text="Close",
            command=about_window.destroy,
            **self.theme.get_button_colors("primary")
        )
        close_btn.pack(pady=(Spacing.LG, 0))

    def toggle_theme(self):
        """Toggle between dark and light themes"""
        self.theme.toggle_theme()
        current_mode = "Dark" if self.theme.is_dark else "Light"
        self.status_bar.set_info(f"Theme changed to {current_mode}")
