"""
Image Export for Barcodes and License Cards

Handles generation of:
- PDF417 barcode images
- Complete license card images
- Multiple image formats (PNG, JPEG, BMP)
"""

from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum

try:
    import pdf417
    from PIL import Image as PILImage, ImageDraw, ImageFont
except ImportError as e:
    raise ImportError(
        "PDF417 and Pillow are required for image export. "
        "Install with: pip install pdf417gen pillow"
    ) from e

from .base import (
    BatchExporter, ExportFormat, ExportOptions, ExportResult,
    ValidationError, RenderError, EncodingError
)
from ..storage import (
    FileSystemValidator, DirectoryManager, SafeFileOperations,
    StorageError
)


class ImageFormat(Enum):
    """Supported image formats"""
    PNG = "png"
    JPEG = "jpeg"
    JPG = "jpg"
    BMP = "bmp"


class BarcodeExporter(BatchExporter):
    """
    Export license data as PDF417 barcode images

    Generates one barcode image per license with comprehensive
    error handling for encoding failures.
    """

    def __init__(self, options: ExportOptions, image_format: ImageFormat = ImageFormat.BMP):
        super().__init__(options)
        self.image_format = image_format

    @property
    def format(self) -> ExportFormat:
        return ExportFormat.BMP  # Default, but configurable

    @property
    def file_extension(self) -> str:
        return self.image_format.value

    def validate_data(self, data: Any) -> None:
        """
        Validate license data for barcode export

        Args:
            data: List of license data (list of subfiles)

        Raises:
            ValidationError: If data is invalid
        """
        if not isinstance(data, list):
            raise ValidationError("Data must be a list of license records")

        if len(data) == 0:
            raise ValidationError("No license data to export")

        for index, license_data in enumerate(data):
            if not isinstance(license_data, list) or len(license_data) < 1:
                raise ValidationError(
                    f"Item {index}: License data must be list with at least one subfile"
                )

            # Check that we can format barcode data
            try:
                self._format_barcode_data(license_data)
            except Exception as e:
                raise ValidationError(
                    f"Item {index}: Cannot format barcode data: {e}"
                )

    def _export_impl(self, data: List[List[Dict[str, Any]]]) -> ExportResult:
        """
        Export barcodes using batch processing

        Args:
            data: List of license data

        Returns:
            ExportResult with batch statistics
        """
        # Ensure output directory exists
        output_dir = Path(self.options.output_path)
        try:
            DirectoryManager.ensure_directory_tree(output_dir)
        except Exception as e:
            return ExportResult(
                success=False,
                errors=[f"Failed to create output directory: {e}"]
            )

        # Use batch export from parent class
        return super()._export_impl(data)

    def _export_item(self, item: List[Dict[str, Any]], index: int) -> Optional[str]:
        """
        Export a single barcode

        Args:
            item: License data (list of subfiles)
            index: Item index

        Returns:
            Error message if failed, None if successful
        """
        try:
            # Format barcode data
            barcode_data = self._format_barcode_data(item)

            # Encode barcode
            codes = self._encode_barcode(barcode_data)

            # Render image
            image = pdf417.render_image(codes)

            # Save image
            output_path = Path(self.options.output_path) / f"license_{index}.{self.file_extension}"
            image.save(str(output_path))

            # Also save raw data to TXT file
            txt_path = output_path.with_suffix('.txt')
            with SafeFileOperations.atomic_write(txt_path, mode='w') as f:
                f.write(barcode_data)

            return None  # Success

        except EncodingError as e:
            return f"Barcode encoding failed: {e}"
        except Exception as e:
            return f"Unexpected error: {e}"

    def _format_barcode_data(self, license_data: List[Dict[str, Any]]) -> str:
        """
        Format license data for PDF417 barcode

        Args:
            license_data: List of subfiles

        Returns:
            Formatted barcode data string

        Raises:
            EncodingError: If data cannot be formatted
        """
        try:
            # Extract IIN from state code
            dl_data = license_data[0]
            state_code = dl_data.get("DAJ", "AZ")
            iin = self._get_iin_by_state(state_code)

            # Header
            compliance = "@\n\x1E\r"  # @LF RS CR
            file_type = "ANSI "
            version = "10"
            jurisdiction_version = "00"
            number_of_entries = f"{len(license_data):02d}"

            header_base = (
                compliance +
                file_type +
                iin +
                version +
                jurisdiction_version +
                number_of_entries
            )

            # Build subfiles
            subfile_designators = ""
            subfile_data_combined = ""
            current_offset = len(header_base.encode("ascii"))

            # Reserve space for subfile designators
            designator_space = 10 * len(license_data)
            current_offset += designator_space

            for subfile in license_data:
                subfile_type = subfile.get("subfile_type", "DL")

                # Build subfile content
                if subfile_type == "DL":
                    # DL subfile - DAQ comes first
                    daq = subfile.get("DAQ", "")
                    content = f"{subfile_type}DAQ{daq}\n"
                    content += "".join(
                        f"{k}{v}\n"
                        for k, v in subfile.items()
                        if k not in ["DAQ", "subfile_type"]
                    )
                    content += "\r"
                else:
                    # State subfile
                    content = subfile_type
                    content += "".join(
                        f"{k}{v}\n"
                        for k, v in subfile.items()
                        if k != "subfile_type"
                    )
                    content += "\r"

                # Calculate offset and length
                subfile_length = len(content.encode("ascii"))
                subfile_designators += f"{subfile_type}{current_offset:04d}{subfile_length:04d}"
                subfile_data_combined += content
                current_offset += subfile_length

            # Combine all parts
            barcode_data = header_base + subfile_designators + subfile_data_combined

            # Validate length
            if len(barcode_data) > 2710:  # PDF417 limit
                raise EncodingError(
                    f"Barcode data too long ({len(barcode_data)} bytes). "
                    f"Maximum is 2710 bytes."
                )

            return barcode_data

        except Exception as e:
            raise EncodingError(f"Failed to format barcode data: {e}") from e

    def _encode_barcode(self, data: str) -> Any:
        """
        Encode data as PDF417

        Args:
            data: Data to encode

        Returns:
            Encoded barcode

        Raises:
            EncodingError: If encoding fails
        """
        try:
            codes = pdf417.encode(data, columns=13, security_level=5)
            return codes
        except Exception as e:
            raise EncodingError(f"PDF417 encoding failed: {e}") from e

    def _get_iin_by_state(self, state_code: str) -> str:
        """
        Get IIN for a state code

        Args:
            state_code: Two-letter state abbreviation

        Returns:
            Six-digit IIN
        """
        # Simplified IIN lookup - in production, use full IIN_JURISDICTIONS
        iin_map = {
            "CA": "636014",
            "NY": "636001",
            "TX": "636015",
            "FL": "636010",
            "AZ": "636026",
            # Add more as needed...
        }
        return iin_map.get(state_code.upper(), "636026")  # Default to AZ


class CardImageExporter(BatchExporter):
    """
    Export complete license card images

    Generates images containing:
    - Barcode
    - License data text
    - Proper formatting
    """

    def __init__(self, options: ExportOptions,
                 image_format: ImageFormat = ImageFormat.PNG,
                 width_inches: float = 3.5,
                 dpi: int = 300):
        super().__init__(options)
        self.image_format = image_format
        self.width_inches = width_inches
        self.dpi = dpi

    @property
    def format(self) -> ExportFormat:
        return ExportFormat.PNG

    @property
    def file_extension(self) -> str:
        return self.image_format.value

    def validate_data(self, data: Any) -> None:
        """Validate data for card image export"""
        if not isinstance(data, list):
            raise ValidationError("Data must be a list")

        for index, item in enumerate(data):
            if not isinstance(item, (tuple, list)) or len(item) != 2:
                raise ValidationError(
                    f"Item {index}: Must be (barcode_path, license_data) tuple"
                )

    def _export_impl(self, data: List[Tuple[Path, List[Dict[str, Any]]]]) -> ExportResult:
        """Export card images using batch processing"""
        # Ensure output directory
        output_dir = Path(self.options.output_path)
        try:
            DirectoryManager.ensure_directory_tree(output_dir)
        except Exception as e:
            return ExportResult(
                success=False,
                errors=[f"Failed to create output directory: {e}"]
            )

        return super()._export_impl(data)

    def _export_item(self, item: Tuple[Path, List[Dict[str, Any]]],
                    index: int) -> Optional[str]:
        """
        Export a single card image

        Args:
            item: (barcode_path, license_data) tuple
            index: Item index

        Returns:
            Error message if failed, None if successful
        """
        try:
            barcode_path, license_data = item

            # Generate card image
            card_image = self._generate_card_image(barcode_path, license_data)

            # Save image
            output_path = Path(self.options.output_path) / f"card_{index}.{self.file_extension}"

            # Save with appropriate format
            if self.image_format == ImageFormat.JPEG or self.image_format == ImageFormat.JPG:
                card_image.save(
                    str(output_path),
                    quality=self.options.quality,
                    dpi=(self.dpi, self.dpi)
                )
            else:
                card_image.save(str(output_path), dpi=(self.dpi, self.dpi))

            return None  # Success

        except Exception as e:
            return f"Failed to generate card image: {e}"

    def _generate_card_image(self, barcode_path: Path,
                            license_data: List[Dict[str, Any]]) -> PILImage.Image:
        """
        Generate a complete card image

        Args:
            barcode_path: Path to barcode image
            license_data: License data

        Returns:
            PIL Image object
        """
        # Calculate dimensions
        card_width = int(self.width_inches * self.dpi)
        card_height = int(2.0 * self.dpi)

        # Create card
        card = PILImage.new("RGB", (card_width, card_height), "white")
        draw = ImageDraw.Draw(card)

        # Font sizes scaled by DPI
        base_font_size = int(50 * (self.dpi / 300))
        small_font_size = int(40 * (self.dpi / 300))

        # Load fonts
        try:
            font = ImageFont.truetype("LiberationMono-Bold.ttf", base_font_size)
            small_font = ImageFont.truetype("LiberationMono-Bold.ttf", small_font_size)
        except Exception:
            font = ImageFont.load_default()
            small_font = font

        # Add barcode if exists
        if barcode_path.exists():
            try:
                barcode_img = PILImage.open(barcode_path).convert("L")
                barcode_width = int(card_width * 0.55)
                barcode_height = int(barcode_width * 0.25)

                barcode_img = barcode_img.resize(
                    (barcode_width, barcode_height),
                    PILImage.Resampling.LANCZOS
                )

                barcode_x = int(card_width * 0.03)
                barcode_y = int(card_height * 0.05)
                card.paste(barcode_img, (barcode_x, barcode_y))

                text_y = barcode_y + barcode_height + int(card_height * 0.02)
            except Exception as e:
                print(f"Warning: Failed to add barcode: {e}")
                text_y = int(card_height * 0.1)
        else:
            text_y = int(card_height * 0.1)

        # Add license data text
        text_x = int(card_width * 0.03)
        dl_data = license_data[0]
        state_data = license_data[1] if len(license_data) > 1 else {}

        # Format state line
        state_line = "|".join([
            f"{key} {value}"
            for key, value in state_data.items()
            if key != "subfile_type"
        ])

        # Build text
        lines = (
            f"{dl_data.get('DAC', '')} {dl_data.get('DAD', '')} {dl_data.get('DCS', '')}\n"
            f"DOB: {dl_data.get('DBB', '')} | EXP: {dl_data.get('DBA', '')}\n"
            f"DL#: {dl_data.get('DAQ', '')}\n"
            f"Class: {dl_data.get('DCA', '')} | {dl_data.get('DAI', '')}, {dl_data.get('DAJ', '')}\n"
            f"{'M' if dl_data.get('DBC')=='1' else 'F'} | {dl_data.get('DAY', '')} | "
            f"{dl_data.get('DAZ', '')} | {dl_data.get('DAU', '')}\" | {dl_data.get('DAW', '')}lbs\n"
            f"Organ Donor: {dl_data.get('DDK', '')} | Veteran: {dl_data.get('DDL', '')}\n"
            f"{state_line}"
        )

        draw.text((text_x, text_y), lines, fill="black", font=small_font, spacing=10)

        return card


class ImageExportOptions(ExportOptions):
    """Extended options for image export"""

    def __init__(self, output_path: str, **kwargs):
        super().__init__(output_path, **kwargs)
        self.image_format: ImageFormat = ImageFormat.PNG
        self.width_inches: float = 3.5
        self.height_inches: float = 2.0
        self.include_barcode: bool = True
        self.include_text: bool = True
        self.background_color: Tuple[int, int, int] = (255, 255, 255)
        self.text_color: Tuple[int, int, int] = (0, 0, 0)
