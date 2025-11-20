"""
AAMVA Barcode Rendering Module.

This module provides functionality for rendering AAMVA barcode data
as PDF417 barcode images.

This separates rendering concerns from encoding logic, allowing for
different rendering backends and configurations.

Author: Refactored from generate_licenses.py
License: MIT
"""

from typing import Optional, Tuple, Any
from pathlib import Path
import tempfile

try:
    import pdf417
    PDF417_AVAILABLE = True
except ImportError:
    PDF417_AVAILABLE = False

try:
    from PIL import Image as PILImage
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class RenderingError(Exception):
    """Base exception for rendering errors."""
    pass


class PDF417Renderer:
    """PDF417 barcode renderer.

    This class handles rendering AAMVA barcode strings as PDF417
    barcode images using the pdf417 library.
    """

    def __init__(
        self,
        columns: int = 13,
        security_level: int = 5,
        scale: int = 1,
        ratio: int = 3
    ):
        """Initialize renderer.

        Args:
            columns: Number of data columns (1-30)
            security_level: Error correction level (0-8)
            scale: Scaling factor for barcode
            ratio: Module width to height ratio

        Raises:
            RenderingError: If pdf417 library not available
        """
        if not PDF417_AVAILABLE:
            raise RenderingError(
                "pdf417 library not available. Install with: pip install pdf417"
            )

        self.columns = columns
        self.security_level = security_level
        self.scale = scale
        self.ratio = ratio

        # Validate parameters
        if not 1 <= columns <= 30:
            raise RenderingError(f"Columns must be 1-30, got {columns}")
        if not 0 <= security_level <= 8:
            raise RenderingError(f"Security level must be 0-8, got {security_level}")

    def render(
        self,
        barcode_data: str,
        output_path: Optional[str] = None,
        format: str = 'BMP'
    ) -> Any:
        """Render barcode data as PDF417 image.

        Args:
            barcode_data: AAMVA barcode string to render
            output_path: Optional path to save image
            format: Image format (BMP, PNG, JPEG, etc.)

        Returns:
            PIL Image object

        Raises:
            RenderingError: If rendering fails
        """
        try:
            # Encode to PDF417
            codes = pdf417.encode(
                barcode_data,
                columns=self.columns,
                security_level=self.security_level
            )

            # Render as image
            image = pdf417.render_image(
                codes,
                scale=self.scale,
                ratio=self.ratio
            )

            # Save if path provided
            if output_path:
                image.save(output_path, format=format)

            return image

        except Exception as e:
            raise RenderingError(f"Failed to render barcode: {str(e)}") from e

    def render_to_bytes(
        self,
        barcode_data: str,
        format: str = 'PNG'
    ) -> bytes:
        """Render barcode and return as bytes.

        Args:
            barcode_data: AAMVA barcode string to render
            format: Image format (BMP, PNG, JPEG, etc.)

        Returns:
            Image data as bytes

        Raises:
            RenderingError: If rendering fails
        """
        if not PIL_AVAILABLE:
            raise RenderingError(
                "PIL library not available. Install with: pip install pillow"
            )

        from io import BytesIO

        image = self.render(barcode_data)

        # Convert to bytes
        buffer = BytesIO()
        image.save(buffer, format=format)
        return buffer.getvalue()

    def get_image_size(self, barcode_data: str) -> Tuple[int, int]:
        """Get the dimensions of the rendered barcode.

        Args:
            barcode_data: AAMVA barcode string

        Returns:
            Tuple of (width, height) in pixels

        Raises:
            RenderingError: If rendering fails
        """
        image = self.render(barcode_data)
        return image.size


class BarcodeImageRenderer:
    """High-level barcode image renderer with additional features.

    This renderer provides additional functionality like:
    - Automatic sizing
    - Image manipulation
    - Multiple format support
    """

    def __init__(self, pdf417_renderer: Optional[PDF417Renderer] = None):
        """Initialize image renderer.

        Args:
            pdf417_renderer: Optional PDF417Renderer instance
        """
        if pdf417_renderer is None:
            pdf417_renderer = PDF417Renderer()

        self.pdf417_renderer = pdf417_renderer

    def render_with_border(
        self,
        barcode_data: str,
        border_size: int = 10,
        background_color: str = 'white',
        output_path: Optional[str] = None
    ) -> Any:
        """Render barcode with border.

        Args:
            barcode_data: AAMVA barcode string
            border_size: Border size in pixels
            background_color: Border/background color
            output_path: Optional path to save image

        Returns:
            PIL Image object with border

        Raises:
            RenderingError: If rendering fails
        """
        if not PIL_AVAILABLE:
            raise RenderingError(
                "PIL library not available. Install with: pip install pillow"
            )

        # Render base barcode
        barcode_image = self.pdf417_renderer.render(barcode_data)

        # Get dimensions
        width, height = barcode_image.size
        new_width = width + (2 * border_size)
        new_height = height + (2 * border_size)

        # Create new image with border
        bordered_image = PILImage.new(
            'RGB',
            (new_width, new_height),
            background_color
        )

        # Paste barcode in center
        bordered_image.paste(barcode_image, (border_size, border_size))

        # Save if path provided
        if output_path:
            bordered_image.save(output_path)

        return bordered_image

    def render_with_text(
        self,
        barcode_data: str,
        text: str,
        output_path: Optional[str] = None,
        font_size: int = 12,
        text_position: str = 'bottom'
    ) -> Any:
        """Render barcode with text label.

        Args:
            barcode_data: AAMVA barcode string
            text: Text to display
            output_path: Optional path to save image
            font_size: Font size for text
            text_position: Position of text ('top' or 'bottom')

        Returns:
            PIL Image object with text

        Raises:
            RenderingError: If rendering fails
        """
        if not PIL_AVAILABLE:
            raise RenderingError(
                "PIL library not available. Install with: pip install pillow"
            )

        from PIL import ImageDraw, ImageFont

        # Render base barcode
        barcode_image = self.pdf417_renderer.render(barcode_data)

        # Calculate new size
        width, height = barcode_image.size
        text_height = font_size + 10
        new_height = height + text_height

        # Create new image
        combined_image = PILImage.new('RGB', (width, new_height), 'white')

        # Position barcode
        if text_position == 'bottom':
            combined_image.paste(barcode_image, (0, 0))
            text_y = height + 5
        else:  # top
            combined_image.paste(barcode_image, (0, text_height))
            text_y = 5

        # Add text
        draw = ImageDraw.Draw(combined_image)

        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()

        # Center text
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_x = (width - text_width) // 2

        draw.text((text_x, text_y), text, fill='black', font=font)

        # Save if path provided
        if output_path:
            combined_image.save(output_path)

        return combined_image

    def resize(
        self,
        image: Any,
        width: Optional[int] = None,
        height: Optional[int] = None,
        maintain_aspect: bool = True
    ) -> Any:
        """Resize barcode image.

        Args:
            image: PIL Image object
            width: Target width (None to calculate from height)
            height: Target height (None to calculate from width)
            maintain_aspect: Maintain aspect ratio

        Returns:
            Resized PIL Image object

        Raises:
            RenderingError: If both width and height are None
        """
        if not PIL_AVAILABLE:
            raise RenderingError(
                "PIL library not available. Install with: pip install pillow"
            )

        if width is None and height is None:
            raise RenderingError("Must specify at least width or height")

        current_width, current_height = image.size

        if maintain_aspect:
            if width and not height:
                # Calculate height from width
                ratio = width / current_width
                height = int(current_height * ratio)
            elif height and not width:
                # Calculate width from height
                ratio = height / current_height
                width = int(current_width * ratio)

        return image.resize((width, height), PILImage.Resampling.LANCZOS)


def render_barcode(
    barcode_data: str,
    output_path: str,
    columns: int = 13,
    security_level: int = 5,
    format: str = 'BMP'
) -> str:
    """Convenience function to render barcode to file.

    Args:
        barcode_data: AAMVA barcode string
        output_path: Path to save image
        columns: Number of data columns
        security_level: Error correction level
        format: Image format

    Returns:
        Output file path

    Raises:
        RenderingError: If rendering fails

    Example:
        render_barcode(barcode_string, 'license_001.bmp')
    """
    renderer = PDF417Renderer(
        columns=columns,
        security_level=security_level
    )

    renderer.render(barcode_data, output_path, format)
    return output_path


def render_barcode_with_metadata(
    barcode_data: str,
    output_path: str,
    license_number: Optional[str] = None,
    **kwargs
) -> str:
    """Render barcode with metadata text.

    Args:
        barcode_data: AAMVA barcode string
        output_path: Path to save image
        license_number: Optional license number to display
        **kwargs: Additional arguments for renderer

    Returns:
        Output file path

    Raises:
        RenderingError: If rendering fails

    Example:
        render_barcode_with_metadata(
            barcode_string,
            'license_001.png',
            license_number='D1234567'
        )
    """
    renderer = BarcodeImageRenderer()

    if license_number:
        image = renderer.render_with_text(
            barcode_data,
            f"License: {license_number}",
            **kwargs
        )
        image.save(output_path)
    else:
        image = renderer.render_with_border(
            barcode_data,
            output_path=output_path,
            **kwargs
        )

    return output_path
