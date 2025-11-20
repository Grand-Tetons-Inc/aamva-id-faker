"""
Exporters Package

Provides comprehensive export functionality for license data in various formats:
- PDF (Avery 28371 layout)
- DOCX (Word documents)
- Images (PNG, JPEG, BMP)
- JSON (structured data)
- CSV (tabular data)

All exporters inherit from common base classes and provide:
- Validation
- Progress tracking
- Error handling
- Resource management
"""

from .base import (
    BaseExporter,
    BatchExporter,
    StreamingExporter,
    ExportFormat,
    ExportOptions,
    ExportResult,
    ExportProgress,
    ExportError,
    ValidationError,
    RenderError,
    EncodingError,
)

# Always available (no external dependencies)
from .json_exporter import (
    JSONExporter,
    CompactJSONExporter,
    JSONExportOptions,
)
from .csv_exporter import CSVExporter, CSVExportOptions

# Optional imports (require external dependencies)
# These will fail gracefully if dependencies are not installed
try:
    from .pdf_exporter import PDFExporter, PDFExportOptions
    _PDF_AVAILABLE = True
except ImportError:
    _PDF_AVAILABLE = False
    PDFExporter = None
    PDFExportOptions = None

try:
    from .docx_exporter import DOCXExporter, DOCXExportOptions
    _DOCX_AVAILABLE = True
except ImportError:
    _DOCX_AVAILABLE = False
    DOCXExporter = None
    DOCXExportOptions = None

try:
    from .image_exporter import (
        BarcodeExporter,
        CardImageExporter,
        ImageExportOptions,
        ImageFormat,
    )
    _IMAGE_AVAILABLE = True
except ImportError:
    _IMAGE_AVAILABLE = False
    BarcodeExporter = None
    CardImageExporter = None
    ImageExportOptions = None
    ImageFormat = None


__all__ = [
    # Base classes
    "BaseExporter",
    "BatchExporter",
    "StreamingExporter",
    # Data types
    "ExportFormat",
    "ExportOptions",
    "ExportResult",
    "ExportProgress",
    # Exceptions
    "ExportError",
    "ValidationError",
    "RenderError",
    "EncodingError",
    # PDF
    "PDFExporter",
    "PDFExportOptions",
    # DOCX
    "DOCXExporter",
    "DOCXExportOptions",
    # Images
    "BarcodeExporter",
    "CardImageExporter",
    "ImageExportOptions",
    "ImageFormat",
    # JSON
    "JSONExporter",
    "CompactJSONExporter",
    "JSONExportOptions",
    # CSV
    "CSVExporter",
    "CSVExportOptions",
]
