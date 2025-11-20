"""
Importers Package

Provides comprehensive import functionality for license data from various formats:
- JSON (structured data)
- JSON Lines (streaming)
- CSV (tabular data)

All importers inherit from common base classes and provide:
- Validation
- Progress tracking
- Error handling
- Schema validation
- Streaming support for large files
"""

from .base import (
    BaseImporter,
    StreamingImporter,
    ImportFormat,
    ImportOptions,
    ImportResult,
    ImportProgress,
    ImportError,
    ParseError,
    SchemaError,
)

from .json_importer import (
    JSONImporter,
    JSONLinesImporter,
    JSONImportOptions,
)

from .csv_importer import (
    CSVImporter,
    CSVImportOptions,
)


__all__ = [
    # Base classes
    "BaseImporter",
    "StreamingImporter",
    # Data types
    "ImportFormat",
    "ImportOptions",
    "ImportResult",
    "ImportProgress",
    # Exceptions
    "ImportError",
    "ParseError",
    "SchemaError",
    # JSON
    "JSONImporter",
    "JSONLinesImporter",
    "JSONImportOptions",
    # CSV
    "CSVImporter",
    "CSVImportOptions",
]
