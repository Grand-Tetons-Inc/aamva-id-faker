"""
PDF Export using ReportLab

Generates PDF documents with Avery 28371 business card layout (10 cards per page).
Extracted and improved from generate_licenses.py with:
- Better error handling
- Progress tracking
- Resource management
- Validation
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Tuple
from contextlib import contextmanager

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch
    from reportlab.lib.colors import black, lightgrey
except ImportError as e:
    raise ImportError(
        "ReportLab is required for PDF export. Install with: pip install reportlab"
    ) from e

from .base import (
    BaseExporter, ExportFormat, ExportOptions, ExportResult,
    ValidationError, RenderError
)
from ..storage import (
    FileSystemValidator, SafeFileOperations, StorageError
)


class PDFExporter(BaseExporter):
    """
    Export license data to PDF using Avery 28371 layout

    Layout specifications:
    - Page: 8.5" x 11" (US Letter)
    - Cards per page: 10 (2 columns x 5 rows)
    - Card size: 3.5" x 2" (business card)
    - Margins: 0.75" left, 0.5" top
    - Spacing: 0.25" horizontal, 0" vertical
    """

    # Avery 28371 specifications
    PAGE_WIDTH, PAGE_HEIGHT = letter  # 8.5" x 11"
    CARD_WIDTH = 3.5 * inch
    CARD_HEIGHT = 2 * inch
    LEFT_MARGIN = 0.75 * inch
    TOP_MARGIN = 0.5 * inch
    HORIZONTAL_SPACING = 0.25 * inch
    VERTICAL_SPACING = 0 * inch
    CARDS_PER_PAGE = 10

    @property
    def format(self) -> ExportFormat:
        return ExportFormat.PDF

    @property
    def file_extension(self) -> str:
        return "pdf"

    def validate_data(self, data: Any) -> None:
        """
        Validate license data for PDF export

        Args:
            data: List of (barcode_path, license_data) tuples

        Raises:
            ValidationError: If data is invalid
        """
        if not isinstance(data, list):
            raise ValidationError("Data must be a list of license records")

        if len(data) == 0:
            raise ValidationError("No license data to export")

        for index, item in enumerate(data):
            if not isinstance(item, (tuple, list)) or len(item) != 2:
                raise ValidationError(
                    f"Item {index}: Must be (barcode_path, license_data) tuple"
                )

            barcode_path, license_data = item

            # Validate barcode path
            if not isinstance(barcode_path, (str, Path)):
                raise ValidationError(
                    f"Item {index}: Barcode path must be string or Path"
                )

            barcode_path_obj = Path(barcode_path)
            if not barcode_path_obj.exists():
                raise ValidationError(
                    f"Item {index}: Barcode image not found: {barcode_path}"
                )

            # Validate license data
            if not isinstance(license_data, list) or len(license_data) < 1:
                raise ValidationError(
                    f"Item {index}: License data must be list with at least one subfile"
                )

            # Check required fields in DL subfile
            dl_data = license_data[0]
            required_fields = [
                'DAC', 'DAD', 'DCS', 'DBB', 'DBA', 'DAQ',
                'DCA', 'DAI', 'DAJ', 'DBC', 'DAY', 'DAZ',
                'DAU', 'DAW', 'DDK', 'DDL'
            ]

            for field in required_fields:
                if field not in dl_data:
                    raise ValidationError(
                        f"Item {index}: Missing required field '{field}' in DL data"
                    )

    def _export_impl(self, data: List[Tuple[Path, List[Dict[str, Any]]]]) -> ExportResult:
        """
        Export licenses to PDF

        Args:
            data: List of (barcode_path, license_data) tuples

        Returns:
            ExportResult with operation details
        """
        result = ExportResult(success=True)
        output_path = Path(self.options.output_path)

        try:
            # Ensure output directory exists
            if not output_path.parent.exists():
                raise RenderError(f"Output directory does not exist: {output_path.parent}")

            # Check writable
            if not FileSystemValidator.check_writable(output_path.parent):
                raise RenderError(f"Cannot write to directory: {output_path.parent}")

            # Estimate size and check disk space
            estimated_size = self._estimate_pdf_size(len(data))
            FileSystemValidator.ensure_space(output_path, estimated_size)

            # Generate PDF using atomic write
            with SafeFileOperations.atomic_write(output_path, mode='wb') as f:
                self._generate_pdf(f.name, data)

            result.output_path = output_path
            result.items_processed = len(data)

        except (StorageError, RenderError) as e:
            result.success = False
            result.errors.append(str(e))
        except Exception as e:
            result.success = False
            result.errors.append(f"Unexpected error: {e}")

        return result

    def _estimate_pdf_size(self, num_licenses: int) -> int:
        """
        Estimate PDF file size

        Args:
            num_licenses: Number of licenses

        Returns:
            Estimated size in bytes
        """
        # Rough estimate: 50KB base + 10KB per license
        return 50 * 1024 + (num_licenses * 10 * 1024)

    def _generate_pdf(self, filepath: str, data: List[Tuple[Path, List[Dict[str, Any]]]]):
        """
        Generate the actual PDF file

        Args:
            filepath: Output file path
            data: License data
        """
        total = len(data)
        c = None

        try:
            # Create PDF canvas
            c = canvas.Canvas(filepath, pagesize=letter)

            # Add metadata
            metadata = self._add_metadata({
                "Title": "AAMVA License Cards",
                "Subject": "Generated License Cards (Avery 28371 Layout)",
                "Creator": "AAMVA License Generator"
            })

            c.setTitle(metadata.get("Title", ""))
            c.setAuthor(metadata.get("Creator", ""))

            # Process cards in pages
            for page_num in range(0, total, self.CARDS_PER_PAGE):
                self._update_progress(
                    page_num,
                    total,
                    "rendering",
                    f"Rendering page {page_num // self.CARDS_PER_PAGE + 1}..."
                )

                page_cards = data[page_num:page_num + self.CARDS_PER_PAGE]
                self._render_page(c, page_cards)

                # Start new page if there are more cards
                if page_num + self.CARDS_PER_PAGE < total:
                    c.showPage()

            # Save PDF
            self._update_progress(total, total, "saving", "Saving PDF...")
            c.save()

        except Exception as e:
            # Clean up canvas if error
            if c:
                try:
                    c.save()  # Try to save partial PDF
                except Exception:
                    pass
            raise RenderError(f"Failed to generate PDF: {e}") from e

    def _render_page(self, c: canvas.Canvas,
                     page_cards: List[Tuple[Path, List[Dict[str, Any]]]]):
        """
        Render a single page of cards

        Args:
            c: ReportLab canvas
            page_cards: Cards for this page (up to 10)
        """
        for card_index, (img_path, license_data) in enumerate(page_cards):
            # Calculate position on page (2 columns, 5 rows)
            row = card_index // 2
            col = card_index % 2

            x = self.LEFT_MARGIN + col * (self.CARD_WIDTH + self.HORIZONTAL_SPACING)
            y = self.PAGE_HEIGHT - self.TOP_MARGIN - (row + 1) * (
                self.CARD_HEIGHT + self.VERTICAL_SPACING
            )

            # Render single card
            try:
                self._render_card(c, x, y, img_path, license_data)
            except Exception as e:
                # Log error but continue with other cards
                print(f"Warning: Failed to render card {card_index}: {e}")

                # Draw error placeholder
                self._render_error_card(c, x, y, str(e))

    def _render_card(self, c: canvas.Canvas, x: float, y: float,
                     barcode_path: Path, license_data: List[Dict[str, Any]]):
        """
        Render a single card

        Args:
            c: ReportLab canvas
            x: X position
            y: Y position
            barcode_path: Path to barcode image
            license_data: License data (list of subfiles)
        """
        # Draw card border (optional)
        c.setStrokeColorRGB(0.8, 0.8, 0.8)
        c.setLineWidth(0.5)
        c.rect(x, y, self.CARD_WIDTH, self.CARD_HEIGHT, stroke=1, fill=0)

        # Add barcode image
        barcode_width = 1.8 * inch
        barcode_height = 0.6 * inch
        barcode_x = x + 0.1 * inch
        barcode_y = y + self.CARD_HEIGHT - barcode_height - 0.1 * inch

        try:
            c.drawImage(
                str(barcode_path),
                barcode_x,
                barcode_y,
                width=barcode_width,
                height=barcode_height,
                preserveAspectRatio=True
            )
        except Exception as e:
            # If image fails, show placeholder
            c.setFillColorRGB(0.9, 0.9, 0.9)
            c.rect(barcode_x, barcode_y, barcode_width, barcode_height, fill=1)
            c.setFillColorRGB(0, 0, 0)
            c.setFont("Helvetica", 6)
            c.drawString(barcode_x + 5, barcode_y + barcode_height / 2,
                        f"Barcode error: {e}")

        # Add text information
        text_x = x + 0.1 * inch
        text_y = y + self.CARD_HEIGHT - barcode_height - 0.25 * inch

        c.setFont("Helvetica", 8)
        c.setFillColorRGB(0, 0, 0)

        dl_data = license_data[0]
        state_data = license_data[1] if len(license_data) > 1 else {}

        # Format state subfile data
        state_line = "|".join([
            f"{key} {value}"
            for key, value in state_data.items()
            if key != "subfile_type"
        ])

        # Format text lines
        lines = [
            f"{dl_data['DAC']} {dl_data['DAD']} {dl_data['DCS']}",
            f"DOB: {dl_data['DBB']} | EXP: {dl_data['DBA']}",
            f"DL#: {dl_data['DAQ']}",
            f"Class: {dl_data['DCA']} | {dl_data['DAI']}, {dl_data['DAJ']}",
            f"{'M' if dl_data['DBC']=='1' else 'F'} | {dl_data['DAY']} | "
            f"{dl_data['DAZ']} | {dl_data['DAU']}\" | {dl_data['DAW']}lbs",
            f"Organ Donor: {dl_data['DDK']} | Veteran: {dl_data['DDL']}",
            state_line
        ]

        # Draw text lines
        line_height = 0.15 * inch
        for i, line in enumerate(lines):
            # Truncate if line is too long
            if len(line) > 60:
                line = line[:57] + "..."

            c.drawString(text_x, text_y - i * line_height, line)

    def _render_error_card(self, c: canvas.Canvas, x: float, y: float, error: str):
        """
        Render an error placeholder card

        Args:
            c: ReportLab canvas
            x: X position
            y: Y position
            error: Error message
        """
        # Draw border
        c.setStrokeColorRGB(0.9, 0.5, 0.5)
        c.setLineWidth(1)
        c.rect(x, y, self.CARD_WIDTH, self.CARD_HEIGHT, stroke=1, fill=0)

        # Draw error text
        c.setFillColorRGB(0.9, 0, 0)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x + 0.1 * inch, y + self.CARD_HEIGHT / 2, "ERROR")

        # Draw error message
        c.setFont("Helvetica", 7)
        c.setFillColorRGB(0, 0, 0)

        # Wrap error message if too long
        max_width = int(self.CARD_WIDTH / inch * 45)  # Rough chars per line
        if len(error) > max_width:
            error = error[:max_width - 3] + "..."

        c.drawString(x + 0.1 * inch, y + self.CARD_HEIGHT / 2 - 15, error)


class PDFExportOptions(ExportOptions):
    """Extended options specific to PDF export"""

    def __init__(self, output_path: str, **kwargs):
        super().__init__(output_path, **kwargs)
        self.page_size: Tuple[float, float] = letter
        self.draw_borders: bool = True
        self.border_color: Tuple[float, float, float] = (0.8, 0.8, 0.8)
        self.border_width: float = 0.5
        self.font_name: str = "Helvetica"
        self.font_size: int = 8
