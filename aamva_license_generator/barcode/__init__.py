"""
AAMVA Barcode Module.

This module provides comprehensive AAMVA barcode encoding, decoding,
validation, and rendering functionality.

This is a refactored implementation with:
- Clean separation of concerns (encoding vs decoding vs validation vs rendering)
- Comprehensive field validation
- Full decode capability (NEW)
- Superior error handling
- Better testability

Main components:
    - aamva_spec: AAMVA field definitions and specifications
    - subfiles: Subfile handling (DL, ZX, etc.)
    - encoder: AAMVA data encoding
    - decoder: AAMVA data decoding (NEW)
    - formatter: Barcode formatting and display
    - validator: AAMVA compliance validation (NEW)
    - renderer: PDF417 image rendering

Author: Refactored from generate_licenses.py
License: MIT
"""

from .aamva_spec import (
    AAMVAVersion,
    SubfileType,
    FieldDataType,
    FieldCategory,
    FieldDefinition,
    AAMVA_FIELDS,
    IIN_JURISDICTIONS,
    get_iin_by_state,
    get_state_by_iin,
    get_mandatory_fields,
    get_field_definition,
    COMPLIANCE_INDICATOR,
    FILE_TYPE,
    FIELD_SEPARATOR,
    SEGMENT_TERMINATOR,
    SUBFILE_DESIGNATOR_LENGTH,
)

from .subfiles import (
    Subfile,
    DLSubfile,
    JurisdictionSubfile,
    SubfileError,
    SubfileValidationError,
    create_dl_subfile,
    create_jurisdiction_subfile,
)

from .encoder import (
    AAMVAEncoder,
    AAMVAEncoderBuilder,
    EncodingError,
    encode_license_data,
)

from .decoder import (
    AAMVADecoder,
    AAMVAHeader,
    SubfileDesignator,
    DecodingError,
    decode_license_data,
    extract_dl_fields,
)

from .validator import (
    AAMVAValidator,
    ValidationError,
    ValidationIssue,
    ValidationResult,
    validate_license_data,
    validate_barcode_string,
)

from .formatter import (
    BarcodeFormatter,
    format_license_summary,
)

from .renderer import (
    PDF417Renderer,
    BarcodeImageRenderer,
    RenderingError,
    render_barcode,
    render_barcode_with_metadata,
)

__all__ = [
    # Spec
    'AAMVAVersion',
    'SubfileType',
    'FieldDataType',
    'FieldCategory',
    'FieldDefinition',
    'AAMVA_FIELDS',
    'IIN_JURISDICTIONS',
    'get_iin_by_state',
    'get_state_by_iin',
    'get_mandatory_fields',
    'get_field_definition',
    'COMPLIANCE_INDICATOR',
    'FILE_TYPE',
    'FIELD_SEPARATOR',
    'SEGMENT_TERMINATOR',
    'SUBFILE_DESIGNATOR_LENGTH',

    # Subfiles
    'Subfile',
    'DLSubfile',
    'JurisdictionSubfile',
    'SubfileError',
    'SubfileValidationError',
    'create_dl_subfile',
    'create_jurisdiction_subfile',

    # Encoder
    'AAMVAEncoder',
    'AAMVAEncoderBuilder',
    'EncodingError',
    'encode_license_data',

    # Decoder
    'AAMVADecoder',
    'AAMVAHeader',
    'SubfileDesignator',
    'DecodingError',
    'decode_license_data',
    'extract_dl_fields',

    # Validator
    'AAMVAValidator',
    'ValidationError',
    'ValidationIssue',
    'ValidationResult',
    'validate_license_data',
    'validate_barcode_string',

    # Formatter
    'BarcodeFormatter',
    'format_license_summary',

    # Renderer
    'PDF417Renderer',
    'BarcodeImageRenderer',
    'RenderingError',
    'render_barcode',
    'render_barcode_with_metadata',
]
