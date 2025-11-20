"""
License Preview Panel Component

Right panel displaying generated license preview and data.
"""

import customtkinter as ctk
from typing import Optional, Dict, Any
from PIL import Image
from gui.styles import (
    ComponentStyles, Spacing, Typography,
    get_font_tuple, Icons
)
from gui.theme import get_theme_manager


class PreviewPanel(ctk.CTkFrame):
    """
    Preview panel showing license image and data

    Features:
    - Large license image display
    - Scrollable license data textbox
    - Placeholder state when no license generated
    """

    def __init__(self, master, **kwargs):
        """
        Initialize preview panel

        Args:
            master: Parent widget
        """
        # Get theme colors
        theme = get_theme_manager()
        frame_colors = theme.get_frame_colors("default")

        super().__init__(
            master,
            fg_color=frame_colors["fg_color"],
            corner_radius=0,
            **kwargs
        )

        self.theme = theme
        self._current_image = None

        # Configure grid
        self.grid_rowconfigure(0, weight=0)  # Title
        self.grid_rowconfigure(1, weight=1)  # Image
        self.grid_rowconfigure(2, weight=0)  # Data label
        self.grid_rowconfigure(3, weight=1)  # Data text
        self.grid_columnconfigure(0, weight=1)

        # Build UI
        self._create_widgets()

        # Register theme callback
        self.theme.register_callback(self._on_theme_change)

    def _create_widgets(self):
        """Create all preview panel widgets"""
        # Title
        self._create_title()

        # Image preview area
        self._create_image_preview()

        # License data section
        self._create_data_section()

    def _create_title(self):
        """Create panel title"""
        title_label = ctk.CTkLabel(
            self,
            text="Preview",
            font=get_font_tuple(
                size=Typography.SIZE_TITLE,
                weight=Typography.WEIGHT_BOLD
            ),
            **self.theme.get_label_colors("heading")
        )
        title_label.grid(
            row=0,
            column=0,
            pady=(Spacing.LG, Spacing.MD),
            padx=Spacing.LG,
            sticky="w"
        )

    def _create_image_preview(self):
        """Create image preview area"""
        # Container frame for image
        self.image_container = ctk.CTkFrame(
            self,
            **self.theme.get_frame_colors("card"),
            corner_radius=ComponentStyles.CARD_CORNER_RADIUS,
            border_width=ComponentStyles.CARD_BORDER_WIDTH
        )
        self.image_container.grid(
            row=1,
            column=0,
            pady=(0, Spacing.LG),
            padx=Spacing.LG,
            sticky="nsew"
        )

        # Image label (will hold the license image)
        self.image_label = ctk.CTkLabel(
            self.image_container,
            text="",
            **self.theme.get_label_colors("default")
        )
        self.image_label.pack(expand=True, fill="both", padx=Spacing.MD, pady=Spacing.MD)

        # Show placeholder
        self._show_placeholder()

    def _create_data_section(self):
        """Create license data display section"""
        # Section label
        data_label = ctk.CTkLabel(
            self,
            text=f"{Icons.FILE} License Data",
            font=get_font_tuple(
                size=Typography.SIZE_MEDIUM,
                weight=Typography.WEIGHT_BOLD
            ),
            **self.theme.get_label_colors("default")
        )
        data_label.grid(
            row=2,
            column=0,
            pady=(0, Spacing.SM),
            padx=Spacing.LG,
            sticky="w"
        )

        # Data textbox
        self.data_textbox = ctk.CTkTextbox(
            self,
            height=200,
            font=get_font_tuple(
                size=Typography.SIZE_SMALL,
                family=Typography.FONT_FAMILY_MONO
            ),
            **self.theme.get_input_colors(),
            wrap="word"
        )
        self.data_textbox.grid(
            row=3,
            column=0,
            pady=(0, Spacing.LG),
            padx=Spacing.LG,
            sticky="nsew"
        )

        # Insert placeholder text
        self.data_textbox.insert(
            "1.0",
            "No license generated yet.\n\n"
            "Configure options in the sidebar and click 'Generate Licenses' to begin."
        )
        self.data_textbox.configure(state="disabled")

    def _show_placeholder(self):
        """Show placeholder when no license is displayed"""
        placeholder_text = (
            f"{Icons.LICENSE}\n\n"
            "No Preview Available\n\n"
            "Generate a license to see preview"
        )

        self.image_label.configure(
            text=placeholder_text,
            font=get_font_tuple(size=Typography.SIZE_LARGE),
            **self.theme.get_label_colors("secondary")
        )
        self._current_image = None

    def show_license(self, license_data: Dict[str, Any]):
        """
        Display license preview

        Args:
            license_data: Dictionary containing license information
                Expected keys: image_path, name, dob, license_number,
                              state, address, etc.
        """
        # Load and display image if available
        image_path = license_data.get("image_path")
        if image_path:
            try:
                self._display_image(image_path)
            except Exception as e:
                print(f"Error loading image: {e}")
                self._show_placeholder()
        else:
            self._show_placeholder()

        # Update data display
        self._update_data_display(license_data)

    def _display_image(self, image_path: str):
        """
        Load and display license image

        Args:
            image_path: Path to license image file
        """
        try:
            # Load image
            pil_image = Image.open(image_path)

            # Calculate scaled size to fit container
            # Maintain aspect ratio
            container_width = self.image_container.winfo_width()
            container_height = self.image_container.winfo_height()

            # Use default size if container not yet sized
            if container_width <= 1:
                container_width = 600
            if container_height <= 1:
                container_height = 400

            # Calculate scaling
            width_ratio = (container_width - 2 * Spacing.MD) / pil_image.width
            height_ratio = (container_height - 2 * Spacing.MD) / pil_image.height
            scale_ratio = min(width_ratio, height_ratio, 1.0)  # Don't upscale

            new_width = int(pil_image.width * scale_ratio)
            new_height = int(pil_image.height * scale_ratio)

            # Resize image
            pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Convert to CTkImage
            ctk_image = ctk.CTkImage(
                light_image=pil_image,
                dark_image=pil_image,
                size=(new_width, new_height)
            )

            # Update label
            self.image_label.configure(
                image=ctk_image,
                text=""
            )

            # Keep reference to prevent garbage collection
            self._current_image = ctk_image

        except Exception as e:
            print(f"Error displaying image: {e}")
            self._show_placeholder()

    def _update_data_display(self, license_data: Dict[str, Any]):
        """
        Update license data display

        Args:
            license_data: Dictionary containing license information
        """
        # Format license data for display
        data_text = self._format_license_data(license_data)

        # Update textbox
        self.data_textbox.configure(state="normal")
        self.data_textbox.delete("1.0", "end")
        self.data_textbox.insert("1.0", data_text)
        self.data_textbox.configure(state="disabled")

    def _format_license_data(self, data: Dict[str, Any]) -> str:
        """
        Format license data as readable text

        Args:
            data: License data dictionary

        Returns:
            Formatted string for display
        """
        lines = []

        # Personal Information
        lines.append("=== PERSONAL INFORMATION ===\n")
        lines.append(f"Name:           {data.get('name', 'N/A')}")
        lines.append(f"First Name:     {data.get('first_name', 'N/A')}")
        lines.append(f"Last Name:      {data.get('last_name', 'N/A')}")
        lines.append(f"Date of Birth:  {data.get('dob', 'N/A')}")
        lines.append(f"Sex:            {data.get('sex', 'N/A')}")
        lines.append("")

        # License Information
        lines.append("=== LICENSE INFORMATION ===\n")
        lines.append(f"License Number: {data.get('license_number', 'N/A')}")
        lines.append(f"State:          {data.get('state', 'N/A')}")
        lines.append(f"Issue Date:     {data.get('issue_date', 'N/A')}")
        lines.append(f"Expiration:     {data.get('expiration_date', 'N/A')}")
        lines.append(f"Class:          {data.get('license_class', 'N/A')}")
        lines.append("")

        # Address
        lines.append("=== ADDRESS ===\n")
        lines.append(f"Street:         {data.get('address', 'N/A')}")
        lines.append(f"City:           {data.get('city', 'N/A')}")
        lines.append(f"State:          {data.get('state', 'N/A')}")
        lines.append(f"ZIP Code:       {data.get('zip', 'N/A')}")
        lines.append("")

        # Physical Description
        lines.append("=== PHYSICAL DESCRIPTION ===\n")
        lines.append(f"Height:         {data.get('height', 'N/A')}")
        lines.append(f"Weight:         {data.get('weight', 'N/A')}")
        lines.append(f"Eye Color:      {data.get('eye_color', 'N/A')}")
        lines.append(f"Hair Color:     {data.get('hair_color', 'N/A')}")
        lines.append("")

        # Additional Information
        if data.get('veteran') or data.get('organ_donor'):
            lines.append("=== ADDITIONAL ===\n")
            if data.get('veteran'):
                lines.append(f"Veteran:        Yes")
            if data.get('organ_donor'):
                lines.append(f"Organ Donor:    Yes")
            lines.append("")

        # File paths
        if data.get('image_path') or data.get('barcode_path'):
            lines.append("=== FILES ===\n")
            if data.get('image_path'):
                lines.append(f"Image:          {data.get('image_path')}")
            if data.get('barcode_path'):
                lines.append(f"Barcode:        {data.get('barcode_path')}")

        return "\n".join(lines)

    def clear_preview(self):
        """Clear preview and show placeholder"""
        self._show_placeholder()

        self.data_textbox.configure(state="normal")
        self.data_textbox.delete("1.0", "end")
        self.data_textbox.insert(
            "1.0",
            "No license generated yet.\n\n"
            "Configure options in the sidebar and click 'Generate Licenses' to begin."
        )
        self.data_textbox.configure(state="disabled")

    def show_loading(self):
        """Show loading state"""
        loading_text = f"{Icons.LOADING}\n\nGenerating...\n\nPlease wait"

        self.image_label.configure(
            text=loading_text,
            font=get_font_tuple(size=Typography.SIZE_LARGE),
            **self.theme.get_label_colors("default")
        )
        self._current_image = None

        self.data_textbox.configure(state="normal")
        self.data_textbox.delete("1.0", "end")
        self.data_textbox.insert("1.0", "Generating license data...\n\nPlease wait.")
        self.data_textbox.configure(state="disabled")

    def show_error(self, error_message: str):
        """
        Show error state

        Args:
            error_message: Error message to display
        """
        error_text = f"{Icons.ERROR}\n\nGeneration Failed\n\nSee status bar for details"

        self.image_label.configure(
            text=error_text,
            font=get_font_tuple(size=Typography.SIZE_LARGE),
            **self.theme.get_label_colors("error")
        )
        self._current_image = None

        self.data_textbox.configure(state="normal")
        self.data_textbox.delete("1.0", "end")
        self.data_textbox.insert("1.0", f"Error:\n\n{error_message}")
        self.data_textbox.configure(state="disabled")

    def _on_theme_change(self, theme_mode: str):
        """Handle theme change event"""
        # Update frame colors
        frame_colors = self.theme.get_frame_colors("default")
        self.configure(fg_color=frame_colors["fg_color"])

        # Update image container
        card_colors = self.theme.get_frame_colors("card")
        self.image_container.configure(
            fg_color=card_colors["fg_color"],
            border_color=card_colors["border_color"]
        )
