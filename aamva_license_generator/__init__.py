"""
AAMVA License Generator - Core Business Logic Layer

This package provides clean, testable business logic for generating AAMVA-compliant
driver's license data and barcodes, along with comprehensive state management.

Author: Claude Code Agent
License: MIT
"""

from .models import (
    Person,
    Address,
    PhysicalAttributes,
    License,
    LicenseSubfile,
    StateSubfile,
    Sex,
    EyeColor,
    HairColor,
    Race,
    TruncationStatus,
    ComplianceType,
)
from .generators import LicenseGenerator
from .validators import LicenseValidator, ValidationError
from .formatters import AAMVABarcodeFormatter
from .state_formats import StateFormatRegistry

# State Management
from .state import (
    AppState,
    get_app_state,
    GenerationState,
    GenerationStatus,
    LicenseGenerationItem,
    HistoryManager,
    HistoryEntry,
    get_history_manager,
    Settings,
    get_settings,
)

# Event System
from .events import (
    Event,
    EventType,
    EventPriority,
    EventBus,
    get_event_bus,
    emit,
    subscribe,
    unsubscribe,
)

# Command Pattern (Undo/Redo)
from .commands import (
    Command,
    FunctionCommand,
    MacroCommand,
    CommandHistory,
    get_command_history,
    Transaction,
    execute,
    undo,
    redo,
)

# Barcode Module (new refactored implementation)
from .barcode import (
    # Encoding
    AAMVAEncoder,
    encode_license_data,
    # Decoding
    AAMVADecoder,
    decode_license_data,
    extract_dl_fields,
    # Validation
    AAMVAValidator,
    validate_license_data,
    validate_barcode_string,
    ValidationResult,
    # Rendering
    PDF417Renderer,
    BarcodeImageRenderer,
    render_barcode,
    # Subfiles
    Subfile,
    DLSubfile,
    JurisdictionSubfile,
    # Spec
    AAMVAVersion,
    FieldDefinition,
    get_field_definition,
    get_iin_by_state,
    get_state_by_iin,
    # Exceptions
    EncodingError,
    DecodingError,
    RenderingError,
    SubfileError,
)

# File I/O - Storage
from .storage import (
    StorageError as FileStorageError,
    DiskSpaceError,
    PathError,
    ChecksumError,
    FileSystemValidator,
    SafeFileOperations,
    DirectoryManager,
    TemporaryFileManager,
    DiskSpaceInfo,
)

# File I/O - Exporters
from .exporters import (
    BaseExporter,
    BatchExporter,
    StreamingExporter,
    PDFExporter,
    DOCXExporter,
    BarcodeExporter,
    CardImageExporter,
    JSONExporter,
    CompactJSONExporter,
    CSVExporter,
    ExportOptions,
    PDFExportOptions,
    DOCXExportOptions,
    ImageExportOptions,
    JSONExportOptions,
    CSVExportOptions,
    ExportResult,
    ExportProgress,
    ExportFormat,
    ExportError,
    RenderError as ExportRenderError,
)

# File I/O - Importers
from .importers import (
    BaseImporter,
    StreamingImporter as ImportStreamingImporter,
    JSONImporter,
    JSONLinesImporter,
    CSVImporter,
    ImportOptions,
    JSONImportOptions,
    CSVImportOptions,
    ImportResult,
    ImportProgress,
    ImportFormat,
    ImportError,
    ParseError,
    SchemaError,
)

__version__ = "0.1.0"
__all__ = [
    # Models
    "Person",
    "Address",
    "PhysicalAttributes",
    "License",
    "LicenseSubfile",
    "StateSubfile",
    "Sex",
    "EyeColor",
    "HairColor",
    "Race",
    "TruncationStatus",
    "ComplianceType",
    # Core Logic
    "LicenseGenerator",
    "LicenseValidator",
    "ValidationError",
    "AAMVABarcodeFormatter",
    "StateFormatRegistry",
    # State Management
    "AppState",
    "get_app_state",
    "GenerationState",
    "GenerationStatus",
    "LicenseGenerationItem",
    "HistoryManager",
    "HistoryEntry",
    "get_history_manager",
    "Settings",
    "get_settings",
    # Events
    "Event",
    "EventType",
    "EventPriority",
    "EventBus",
    "get_event_bus",
    "emit",
    "subscribe",
    "unsubscribe",
    # Commands
    "Command",
    "FunctionCommand",
    "MacroCommand",
    "CommandHistory",
    "get_command_history",
    "Transaction",
    "execute",
    "undo",
    "redo",
    # Barcode Module
    "AAMVAEncoder",
    "encode_license_data",
    "AAMVADecoder",
    "decode_license_data",
    "extract_dl_fields",
    "AAMVAValidator",
    "validate_license_data",
    "validate_barcode_string",
    "ValidationResult",
    "PDF417Renderer",
    "BarcodeImageRenderer",
    "render_barcode",
    "Subfile",
    "DLSubfile",
    "JurisdictionSubfile",
    "AAMVAVersion",
    "FieldDefinition",
    "get_field_definition",
    "get_iin_by_state",
    "get_state_by_iin",
    "EncodingError",
    "DecodingError",
    "RenderingError",
    "SubfileError",
    # Storage
    "FileStorageError",
    "DiskSpaceError",
    "PathError",
    "ChecksumError",
    "FileSystemValidator",
    "SafeFileOperations",
    "DirectoryManager",
    "TemporaryFileManager",
    "DiskSpaceInfo",
    # Exporters
    "BaseExporter",
    "BatchExporter",
    "StreamingExporter",
    "PDFExporter",
    "DOCXExporter",
    "BarcodeExporter",
    "CardImageExporter",
    "JSONExporter",
    "CompactJSONExporter",
    "CSVExporter",
    "ExportOptions",
    "PDFExportOptions",
    "DOCXExportOptions",
    "ImageExportOptions",
    "JSONExportOptions",
    "CSVExportOptions",
    "ExportResult",
    "ExportProgress",
    "ExportFormat",
    "ExportError",
    "ExportRenderError",
    # Importers
    "BaseImporter",
    "ImportStreamingImporter",
    "JSONImporter",
    "JSONLinesImporter",
    "CSVImporter",
    "ImportOptions",
    "JSONImportOptions",
    "CSVImportOptions",
    "ImportResult",
    "ImportProgress",
    "ImportFormat",
    "ImportError",
    "ParseError",
    "SchemaError",
]
