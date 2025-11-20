"""
Configuration Sidebar Component

Left panel containing all configuration options for license generation.
"""

import customtkinter as ctk
from typing import Callable, Optional, Dict, Any
from tkinter import filedialog
from gui.styles import (
    ComponentStyles, Spacing, Typography,
    get_font_tuple, Icons
)
from gui.theme import get_theme_manager


class ConfigurationSidebar(ctk.CTkScrollableFrame):
    """
    Scrollable sidebar with configuration options

    Features:
    - State selection dropdown
    - Quantity input
    - Output format checkboxes
    - Output directory selection
    - Generate button
    """

    def __init__(self, master, generate_callback: Optional[Callable] = None, **kwargs):
        """
        Initialize sidebar

        Args:
            master: Parent widget
            generate_callback: Function to call when generate button is clicked
        """
        # Get theme colors
        theme = get_theme_manager()
        frame_colors = theme.get_frame_colors("sidebar")

        super().__init__(
            master,
            width=ComponentStyles.SIDEBAR_WIDTH,
            fg_color=frame_colors["fg_color"],
            corner_radius=0,
            **kwargs
        )

        self.generate_callback = generate_callback
        self.theme = theme

        # State variables
        self.state_var = ctk.StringVar(value="CA")
        self.count_var = ctk.IntVar(value=10)
        self.pdf_var = ctk.BooleanVar(value=True)
        self.docx_var = ctk.BooleanVar(value=True)
        self.odt_var = ctk.BooleanVar(value=False)
        self.all_states_var = ctk.BooleanVar(value=False)
        self.output_var = ctk.StringVar(value="./output")

        # Build UI
        self._create_widgets()

        # Register theme callback
        self.theme.register_callback(self._on_theme_change)

    def _create_widgets(self):
        """Create all sidebar widgets"""
        # Title
        self._create_title()

        # State selection section
        self._create_state_section()

        # Quantity section
        self._create_quantity_section()

        # Output formats section
        self._create_formats_section()

        # Output directory section
        self._create_output_section()

        # Generate button
        self._create_generate_button()

    def _create_title(self):
        """Create sidebar title"""
        title_label = ctk.CTkLabel(
            self,
            text="Configuration",
            font=get_font_tuple(
                size=Typography.SIZE_TITLE,
                weight=Typography.WEIGHT_BOLD
            ),
            **self.theme.get_label_colors("heading")
        )
        title_label.pack(pady=(Spacing.LG, Spacing.XL), padx=Spacing.LG, anchor="w")

    def _create_state_section(self):
        """Create state selection section"""
        # Section label
        section_label = ctk.CTkLabel(
            self,
            text="State",
            font=get_font_tuple(
                size=Typography.SIZE_MEDIUM,
                weight=Typography.WEIGHT_BOLD
            ),
            **self.theme.get_label_colors("default")
        )
        section_label.pack(pady=(Spacing.MD, Spacing.XS), padx=Spacing.LG, anchor="w")

        # State dropdown
        self.state_dropdown = ctk.CTkOptionMenu(
            self,
            values=self._get_state_list(),
            variable=self.state_var,
            **self.theme.get_input_colors(),
            button_color=self.theme.get_button_colors("primary")["fg_color"],
            button_hover_color=self.theme.get_button_colors("primary")["hover_color"],
            font=get_font_tuple(size=Typography.SIZE_BODY),
        )
        self.state_dropdown.pack(
            pady=(0, Spacing.SM),
            padx=Spacing.LG,
            fill="x"
        )

        # All states checkbox
        self.all_states_checkbox = ctk.CTkCheckBox(
            self,
            text="Generate all states",
            variable=self.all_states_var,
            command=self._on_all_states_toggle,
            font=get_font_tuple(size=Typography.SIZE_SMALL),
            **self.theme.get_label_colors("secondary")
        )
        self.all_states_checkbox.pack(
            pady=(0, Spacing.LG),
            padx=Spacing.LG,
            anchor="w"
        )

    def _create_quantity_section(self):
        """Create quantity input section"""
        # Section label
        section_label = ctk.CTkLabel(
            self,
            text="Number of Licenses",
            font=get_font_tuple(
                size=Typography.SIZE_MEDIUM,
                weight=Typography.WEIGHT_BOLD
            ),
            **self.theme.get_label_colors("default")
        )
        section_label.pack(pady=(Spacing.MD, Spacing.XS), padx=Spacing.LG, anchor="w")

        # Quantity entry
        self.count_entry = ctk.CTkEntry(
            self,
            textvariable=self.count_var,
            placeholder_text="10",
            height=ComponentStyles.INPUT_HEIGHT,
            font=get_font_tuple(size=Typography.SIZE_BODY),
            **self.theme.get_input_colors()
        )
        self.count_entry.pack(
            pady=(0, Spacing.XS),
            padx=Spacing.LG,
            fill="x"
        )

        # Hint text
        hint_label = ctk.CTkLabel(
            self,
            text="Recommended: 1-100 licenses",
            font=get_font_tuple(size=Typography.SIZE_TINY),
            **self.theme.get_label_colors("secondary")
        )
        hint_label.pack(pady=(0, Spacing.LG), padx=Spacing.LG, anchor="w")

    def _create_formats_section(self):
        """Create output formats section"""
        # Section label
        section_label = ctk.CTkLabel(
            self,
            text="Output Formats",
            font=get_font_tuple(
                size=Typography.SIZE_MEDIUM,
                weight=Typography.WEIGHT_BOLD
            ),
            **self.theme.get_label_colors("default")
        )
        section_label.pack(pady=(Spacing.MD, Spacing.XS), padx=Spacing.LG, anchor="w")

        # PDF checkbox
        pdf_checkbox = ctk.CTkCheckBox(
            self,
            text=f"{Icons.PDF} PDF (Avery template)",
            variable=self.pdf_var,
            font=get_font_tuple(size=Typography.SIZE_BODY),
            **self.theme.get_label_colors("default")
        )
        pdf_checkbox.pack(pady=(0, Spacing.SM), padx=Spacing.LG, anchor="w")

        # DOCX checkbox
        docx_checkbox = ctk.CTkCheckBox(
            self,
            text=f"{Icons.FILE} DOCX (Word document)",
            variable=self.docx_var,
            font=get_font_tuple(size=Typography.SIZE_BODY),
            **self.theme.get_label_colors("default")
        )
        docx_checkbox.pack(pady=(0, Spacing.SM), padx=Spacing.LG, anchor="w")

        # ODT checkbox
        odt_checkbox = ctk.CTkCheckBox(
            self,
            text=f"{Icons.FILE} ODT (OpenDocument)",
            variable=self.odt_var,
            font=get_font_tuple(size=Typography.SIZE_BODY),
            **self.theme.get_label_colors("default")
        )
        odt_checkbox.pack(pady=(0, Spacing.LG), padx=Spacing.LG, anchor="w")

    def _create_output_section(self):
        """Create output directory section"""
        # Section label
        section_label = ctk.CTkLabel(
            self,
            text="Output Directory",
            font=get_font_tuple(
                size=Typography.SIZE_MEDIUM,
                weight=Typography.WEIGHT_BOLD
            ),
            **self.theme.get_label_colors("default")
        )
        section_label.pack(pady=(Spacing.MD, Spacing.XS), padx=Spacing.LG, anchor="w")

        # Container frame for entry and button
        output_frame = ctk.CTkFrame(self, fg_color="transparent")
        output_frame.pack(pady=(0, Spacing.XS), padx=Spacing.LG, fill="x")

        # Configure grid
        output_frame.grid_columnconfigure(0, weight=1)
        output_frame.grid_columnconfigure(1, weight=0)

        # Output directory entry
        self.output_entry = ctk.CTkEntry(
            output_frame,
            textvariable=self.output_var,
            placeholder_text="./output",
            height=ComponentStyles.INPUT_HEIGHT,
            font=get_font_tuple(size=Typography.SIZE_BODY),
            **self.theme.get_input_colors()
        )
        self.output_entry.grid(row=0, column=0, sticky="ew", padx=(0, Spacing.XS))

        # Browse button
        browse_btn = ctk.CTkButton(
            output_frame,
            text=f"{Icons.FOLDER}",
            width=ComponentStyles.INPUT_HEIGHT,
            height=ComponentStyles.INPUT_HEIGHT,
            command=self._browse_directory,
            font=get_font_tuple(size=Typography.SIZE_MEDIUM),
            **self.theme.get_button_colors("secondary")
        )
        browse_btn.grid(row=0, column=1, sticky="e")

        # Hint text
        hint_label = ctk.CTkLabel(
            self,
            text="Click folder icon to browse",
            font=get_font_tuple(size=Typography.SIZE_TINY),
            **self.theme.get_label_colors("secondary")
        )
        hint_label.pack(pady=(0, Spacing.LG), padx=Spacing.LG, anchor="w")

    def _create_generate_button(self):
        """Create generate button"""
        # Add spacer to push button to bottom
        spacer = ctk.CTkFrame(self, height=Spacing.XL, fg_color="transparent")
        spacer.pack(fill="y", expand=True)

        # Generate button
        self.generate_btn = ctk.CTkButton(
            self,
            text=f"{Icons.LICENSE} Generate Licenses",
            height=ComponentStyles.BUTTON_HEIGHT + 8,  # Larger for primary action
            command=self._on_generate_click,
            font=get_font_tuple(
                size=Typography.SIZE_MEDIUM,
                weight=Typography.WEIGHT_BOLD
            ),
            **self.theme.get_button_colors("primary")
        )
        self.generate_btn.pack(
            pady=Spacing.LG,
            padx=Spacing.LG,
            fill="x"
        )

    def _get_state_list(self) -> list:
        """Get list of state abbreviations"""
        # Top 20 most populous states for now
        return [
            "CA", "TX", "FL", "NY", "PA",
            "IL", "OH", "GA", "NC", "MI",
            "NJ", "VA", "WA", "AZ", "MA",
            "TN", "IN", "MD", "MO", "WI",
        ]

    def _on_all_states_toggle(self):
        """Handle all states checkbox toggle"""
        if self.all_states_var.get():
            # Disable state dropdown and count entry
            self.state_dropdown.configure(state="disabled")
            self.count_entry.configure(state="disabled")
        else:
            # Enable state dropdown and count entry
            self.state_dropdown.configure(state="normal")
            self.count_entry.configure(state="normal")

    def _browse_directory(self):
        """Open directory browser dialog"""
        directory = filedialog.askdirectory(
            initialdir=self.output_var.get(),
            title="Select Output Directory"
        )
        if directory:
            self.output_var.set(directory)

    def _on_generate_click(self):
        """Handle generate button click"""
        if self.generate_callback:
            config = self.get_configuration()
            self.generate_callback(config)

    def get_configuration(self) -> Dict[str, Any]:
        """
        Get current configuration values

        Returns:
            Dictionary with all configuration values
        """
        return {
            "state": None if self.all_states_var.get() else self.state_var.get(),
            "count": self.count_var.get(),
            "output_dir": self.output_var.get(),
            "generate_pdf": self.pdf_var.get(),
            "generate_docx": self.docx_var.get(),
            "generate_odt": self.odt_var.get(),
            "all_states": self.all_states_var.get(),
        }

    def set_generating_state(self, is_generating: bool):
        """
        Enable/disable controls during generation

        Args:
            is_generating: True to disable controls, False to enable
        """
        state = "disabled" if is_generating else "normal"

        self.state_dropdown.configure(state=state)
        self.count_entry.configure(state=state)
        self.output_entry.configure(state=state)
        self.all_states_checkbox.configure(state=state)

        if is_generating:
            self.generate_btn.configure(
                text=f"{Icons.LOADING} Generating...",
                state="disabled"
            )
        else:
            self.generate_btn.configure(
                text=f"{Icons.LICENSE} Generate Licenses",
                state="normal"
            )

    def _on_theme_change(self, theme_mode: str):
        """Handle theme change event"""
        # Update colors for all components
        frame_colors = self.theme.get_frame_colors("sidebar")
        self.configure(fg_color=frame_colors["fg_color"])

        # Note: CustomTkinter automatically updates most widget colors
        # This method is here for future custom styling that might need
        # manual updates
