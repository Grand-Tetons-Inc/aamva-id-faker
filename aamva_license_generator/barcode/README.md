# AAMVA Barcode Module

A clean, testable, production-ready barcode generation and validation system for AAMVA DL/ID-2020 standard.

## Overview

This module provides comprehensive AAMVA barcode functionality with:

- **Encoding**: Convert structured data to AAMVA barcode strings
- **Decoding**: Parse AAMVA barcode strings back to structured data (NEW)
- **Validation**: Comprehensive compliance validation (NEW)
- **Rendering**: PDF417 barcode image generation
- **Formatting**: Human-readable display and debugging

## Key Improvements Over Original

1. **Decoding Capability**: Full round-trip encode/decode support
2. **Comprehensive Validation**: Field-level and cross-field validation
3. **Better Error Handling**: Specific exceptions with clear error messages
4. **Clean Architecture**: Separation of concerns (encode/decode/validate/render)
5. **Type Safety**: Full type hints and dataclasses
6. **Testability**: Modular design for easy unit testing
7. **Documentation**: Complete docstrings and examples

## Module Structure

```
barcode/
├── __init__.py          # Public API exports
├── aamva_spec.py        # AAMVA field definitions and specifications
├── subfiles.py          # Subfile handling (DL, ZC, etc.)
├── encoder.py           # AAMVA data encoding
├── decoder.py           # AAMVA data decoding (NEW)
├── formatter.py         # Barcode formatting and display
├── validator.py         # AAMVA compliance validation (NEW)
└── renderer.py          # PDF417 image rendering
```

## Quick Start

### Encoding a Barcode

```python
from aamva_license_generator.barcode import encode_license_data, AAMVAVersion

# Prepare DL data
dl_data = {
    'DAQ': 'D1234567',           # License number
    'DCS': 'SMITH',              # Last name
    'DAC': 'JOHN',               # First name
    'DAD': 'MICHAEL',            # Middle name
    'DBB': '01011990',           # DOB (MMDDYYYY)
    'DBD': '01012020',           # Issue date
    'DBA': '01012030',           # Expiration date
    'DBC': '1',                  # Sex (1=Male, 2=Female)
    'DAY': 'BRO',                # Eye color
    'DAU': '070',                # Height (inches)
    'DAW': '180',                # Weight (lbs)
    'DAG': '123 MAIN ST',        # Address
    'DAI': 'ANYTOWN',            # City
    'DAJ': 'CA',                 # State
    'DAK': '12345',              # ZIP
    'DCA': 'D',                  # Vehicle class
    'DCB': '',                   # Restrictions
    'DCD': '',                   # Endorsements
    'DCF': 'DOC12345',           # Document discriminator
    'DCG': 'USA',                # Country
}

# Encode to barcode string
barcode_string = encode_license_data(dl_data, version=AAMVAVersion.VERSION_10)
print(f"Barcode length: {len(barcode_string)} bytes")
```

### Decoding a Barcode

```python
from aamva_license_generator.barcode import decode_license_data

# Decode barcode string
data = decode_license_data(barcode_string)

# Access header info
print(f"IIN: {data['header']['iin']}")
print(f"Version: {data['header']['version']}")
print(f"Jurisdiction: {data['header']['jurisdiction_info']['jurisdiction']}")

# Access DL fields
dl_fields = data['subfiles'][0]['fields']
print(f"Name: {dl_fields['DAC']} {dl_fields['DCS']}")
print(f"License: {dl_fields['DAQ']}")
print(f"DOB: {dl_fields['DBB']}")
```

### Validating Data

```python
from aamva_license_generator.barcode import (
    validate_license_data,
    DLSubfile,
    AAMVAVersion
)

# Create subfile
subfile = DLSubfile(fields=dl_data)

# Validate
result = validate_license_data([subfile], version=AAMVAVersion.VERSION_10)

if result.is_valid:
    print("✓ Validation passed!")
else:
    print("✗ Validation failed:")
    for error in result.errors:
        print(f"  - {error}")
    for warning in result.warnings:
        print(f"  ⚠ {warning}")
```

### Rendering to Image

```python
from aamva_license_generator.barcode import render_barcode

# Render barcode to file
render_barcode(
    barcode_string,
    'output/license_barcode.bmp',
    columns=13,
    security_level=5
)
```

## Advanced Usage

### Using the Encoder Class

```python
from aamva_license_generator.barcode import (
    AAMVAEncoder,
    DLSubfile,
    JurisdictionSubfile,
    AAMVAVersion
)

# Create encoder
encoder = AAMVAEncoder(version=AAMVAVersion.VERSION_10)

# Create DL subfile
dl_subfile = DLSubfile(fields=dl_data)

# Create jurisdiction-specific subfile
juris_data = {
    'ZCW': 'BOULDER',      # County (Colorado example)
    'ZCT': 'TEST DATA',    # Test field
}
juris_subfile = JurisdictionSubfile(
    jurisdiction='CO',
    fields=juris_data
)

# Encode with multiple subfiles
barcode_string = encoder.encode([dl_subfile, juris_subfile])
```

### Using the Decoder Class

```python
from aamva_license_generator.barcode import AAMVADecoder

# Create decoder
decoder = AAMVADecoder(strict=False)

# Decode to structured objects
header, subfiles = decoder.decode(barcode_string)

# Access header
print(f"IIN: {header.iin}")
print(f"Version: {header.version}")
print(f"Entries: {header.number_of_entries}")

# Access subfiles
for subfile in subfiles:
    print(f"\nSubfile: {subfile.subfile_type}")
    for code, value in subfile.fields.items():
        print(f"  {code}: {value}")
```

### Using the Validator

```python
from aamva_license_generator.barcode import AAMVAValidator, AAMVAVersion

# Create validator
validator = AAMVAValidator(version=AAMVAVersion.VERSION_10, strict=False)

# Validate subfiles
result = validator.validate([dl_subfile, juris_subfile])

# Print detailed results
print(result)  # Full report

# Check specific issues
print(f"Errors: {len(result.errors)}")
print(f"Warnings: {len(result.warnings)}")

# Access individual issues
for issue in result.errors:
    print(f"ERROR in {issue.field}: {issue.message}")
```

### Formatting and Display

```python
from aamva_license_generator.barcode import (
    BarcodeFormatter,
    format_license_summary
)

# Format subfile for display
formatted = BarcodeFormatter.format_subfile(dl_subfile, include_descriptions=True)
print(formatted)

# Format as table
table = BarcodeFormatter.format_table(dl_subfile)
print(table)

# Format license summary
summary = format_license_summary(dl_data)
print(summary)

# Show raw barcode with control characters
raw = BarcodeFormatter.format_raw_barcode(barcode_string, show_invisible=True)
print(raw)

# Hex dump for debugging
hex_dump = BarcodeFormatter.format_hex_dump(barcode_string)
print(hex_dump)
```

### Advanced Rendering

```python
from aamva_license_generator.barcode import (
    PDF417Renderer,
    BarcodeImageRenderer
)

# Create custom renderer
renderer = PDF417Renderer(
    columns=13,
    security_level=5,
    scale=2,
    ratio=3
)

# Render to image
image = renderer.render(barcode_string)

# Get image size
width, height = renderer.get_image_size(barcode_string)
print(f"Image size: {width}x{height}")

# Use high-level renderer for advanced features
image_renderer = BarcodeImageRenderer(renderer)

# Render with border
bordered = image_renderer.render_with_border(
    barcode_string,
    border_size=20,
    background_color='white',
    output_path='output/barcode_bordered.png'
)

# Render with text label
labeled = image_renderer.render_with_text(
    barcode_string,
    text='License: D1234567',
    output_path='output/barcode_labeled.png',
    font_size=14,
    text_position='bottom'
)

# Resize image
resized = image_renderer.resize(image, width=400, maintain_aspect=True)
```

## Validation Features

The validator checks:

1. **Field Presence**: All mandatory fields present
2. **Field Format**: Data types, lengths, patterns
3. **Valid Values**: Enumerated field values (sex, eye color, etc.)
4. **Date Validation**: Format and logical relationships
5. **Cross-Field Consistency**: Height, weight, age reasonableness
6. **IIN Consistency**: IIN matches jurisdiction

Example validation issues:

```python
# Missing mandatory field
result.add_error("Missing mandatory field: DAQ", "MISSING_MANDATORY_FIELD")

# Invalid field format
result.add_error("Date must be in MMDDYYYY format", "INVALID_DATE_FORMAT")

# Invalid date sequence
result.add_error("Expiration date must be after issue date", "INVALID_DATE_SEQUENCE")

# Unusual value
result.add_warning("Age seems unusual: 150 years", "UNUSUAL_AGE")
```

## Error Handling

All modules use specific exceptions:

- `EncodingError`: Encoding failures
- `DecodingError`: Decoding/parsing failures
- `ValidationError`: Validation failures
- `RenderingError`: Image rendering failures
- `SubfileError`: Subfile-related errors

```python
from aamva_license_generator.barcode import (
    EncodingError,
    DecodingError,
    ValidationError,
    RenderingError
)

try:
    barcode_string = encode_license_data(dl_data)
except EncodingError as e:
    print(f"Encoding failed: {e}")

try:
    data = decode_license_data(barcode_string)
except DecodingError as e:
    print(f"Decoding failed: {e}")
```

## Field Definitions

Access field metadata:

```python
from aamva_license_generator.barcode import get_field_definition

# Get field definition
field_def = get_field_definition('DAQ')
print(f"Code: {field_def.code}")
print(f"Name: {field_def.name}")
print(f"Type: {field_def.data_type}")
print(f"Max Length: {field_def.max_length}")
print(f"Category: {field_def.category}")

# Validate value
is_valid, error = field_def.validate('D1234567')
if not is_valid:
    print(f"Validation error: {error}")
```

## IIN Lookups

```python
from aamva_license_generator.barcode import (
    get_iin_by_state,
    get_state_by_iin
)

# Get IIN by state
iin = get_iin_by_state('CA')  # Returns '636014'

# Get state info by IIN
info = get_state_by_iin('636014')
print(f"Jurisdiction: {info['jurisdiction']}")  # California
print(f"Abbreviation: {info['abbr']}")  # CA
print(f"Country: {info['country']}")  # USA
```

## Testing

The modular design makes testing easy:

```python
def test_encode_decode_roundtrip():
    """Test encoding and decoding produce same data."""
    # Encode
    barcode = encode_license_data(dl_data)

    # Decode
    decoded = decode_license_data(barcode)

    # Verify
    assert decoded['subfiles'][0]['fields']['DAQ'] == dl_data['DAQ']
    assert decoded['subfiles'][0]['fields']['DCS'] == dl_data['DCS']

def test_validation():
    """Test validation catches errors."""
    invalid_data = dl_data.copy()
    invalid_data['DBC'] = '9'  # Invalid sex code

    subfile = DLSubfile(fields=invalid_data)
    result = validate_license_data([subfile])

    assert not result.is_valid
    assert len(result.errors) > 0
```

## Performance

The module is optimized for performance:

- Efficient string building for encoding
- Single-pass parsing for decoding
- Lazy validation (only when requested)
- Reusable encoder/decoder instances

## Dependencies

Required:
- `pdf417`: PDF417 barcode encoding
- `Pillow` (PIL): Image manipulation

Optional:
- `faker`: Random data generation (for testing)

## Migration from Original

Migrating from `generate_licenses.py`:

**Old:**
```python
barcode_data = format_barcode_data(subfile_data)
```

**New:**
```python
from aamva_license_generator.barcode import encode_license_data

barcode_data = encode_license_data(dl_data, jurisdiction_data)
```

**Benefits:**
- Type safety
- Validation
- Better error messages
- Decode capability
- Testability

## License

MIT License - See project LICENSE file
