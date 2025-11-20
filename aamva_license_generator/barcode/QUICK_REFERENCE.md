# AAMVA Barcode Module - Quick Reference

## Installation

```bash
pip install pdf417 pillow
```

## Quick Start

### Encode a Barcode

```python
from aamva_license_generator.barcode import encode_license_data

dl_data = {
    'DAQ': 'D1234567',       # License number *
    'DCS': 'SMITH',          # Last name *
    'DAC': 'JOHN',           # First name *
    'DBB': '01011990',       # DOB (MMDDYYYY) *
    'DBD': '01012020',       # Issue date *
    'DBA': '01012030',       # Expiration *
    'DBC': '1',              # Sex (1=M, 2=F) *
    'DAY': 'BRO',            # Eye color *
    'DAU': '070',            # Height (inches) *
    'DAG': '123 MAIN ST',    # Address *
    'DAI': 'ANYTOWN',        # City *
    'DAJ': 'CA',             # State *
    'DAK': '12345',          # ZIP *
    'DCA': 'D',              # Vehicle class *
    'DCB': '',               # Restrictions *
    'DCD': '',               # Endorsements *
    'DCF': 'DOC123',         # Document ID *
    'DCG': 'USA',            # Country *
}
# * = mandatory fields

barcode = encode_license_data(dl_data)
```

### Decode a Barcode

```python
from aamva_license_generator.barcode import decode_license_data

data = decode_license_data(barcode)
name = f"{data['subfiles'][0]['fields']['DAC']} {data['subfiles'][0]['fields']['DCS']}"
```

### Validate Data

```python
from aamva_license_generator.barcode import validate_license_data, DLSubfile

subfile = DLSubfile(fields=dl_data)
result = validate_license_data([subfile])

if result.is_valid:
    print("Valid!")
```

### Render to Image

```python
from aamva_license_generator.barcode import render_barcode

render_barcode(barcode, 'output.bmp')
```

## Common Field Codes

### Mandatory Fields

| Code | Name | Format | Example |
|------|------|--------|---------|
| DAQ | License Number | Alphanumeric | D1234567 |
| DCS | Last Name | Alpha | SMITH |
| DAC | First Name | Alpha | JOHN |
| DAD | Middle Name | Alpha | MICHAEL |
| DBB | Date of Birth | MMDDYYYY | 01011990 |
| DBD | Issue Date | MMDDYYYY | 01012020 |
| DBA | Expiration Date | MMDDYYYY | 01012030 |
| DBC | Sex | 1/2/9 | 1 |
| DAY | Eye Color | BLK/BLU/BRO/... | BRO |
| DAU | Height | Inches or CM | 070 |
| DAG | Address Line 1 | Alphanumeric | 123 MAIN ST |
| DAI | City | Alphanumeric | PHOENIX |
| DAJ | State | 2-letter code | AZ |
| DAK | ZIP Code | 5 or 9 digits | 85001 |
| DCA | Vehicle Class | Alphanumeric | D |
| DCB | Restrictions | Alphanumeric | A |
| DCD | Endorsements | Alphanumeric | H |
| DCF | Document ID | Alphanumeric | DOC12345 |
| DCG | Country | USA/CAN | USA |

### Optional Fields

| Code | Name | Format | Example |
|------|------|--------|---------|
| DAW | Weight (lbs) | Numeric | 180 |
| DAZ | Hair Color | BLK/BLN/BRO/... | BRO |
| DCL | Race | W/B/A/I/H/O/U | W |
| DDE | Last Name Truncated | N/T/U | N |
| DDF | First Name Truncated | N/T/U | N |
| DDG | Middle Name Truncated | N/T/U | N |
| DDA | Compliance Type | F/N/M | F |
| DDB | Card Revision Date | MMDDYYYY | 01012020 |
| DDC | Hazmat Expiry | MMDDYYYY | 01012030 |
| DDD | Limited Duration | 0/1 | 0 |
| DDK | Organ Donor | 0/1 | 1 |
| DDL | Veteran | 0/1 | 0 |

## Valid Values

### Sex (DBC)
- `1` = Male
- `2` = Female
- `9` = Not specified

### Eye Color (DAY)
- `BLK` = Black
- `BLU` = Blue
- `BRO` = Brown
- `GRY` = Gray
- `GRN` = Green
- `HAZ` = Hazel
- `MAR` = Maroon
- `PNK` = Pink
- `DIC` = Dichromatic
- `UNK` = Unknown

### Hair Color (DAZ)
- `BAL` = Bald
- `BLK` = Black
- `BLN` = Blond
- `BRO` = Brown
- `GRY` = Gray
- `RED` = Red
- `SDY` = Sandy
- `WHI` = White
- `UNK` = Unknown

### Race (DCL)
- `W` = White
- `B` = Black
- `A` = Asian
- `I` = American Indian/Alaska Native
- `H` = Hispanic
- `O` = Other
- `U` = Unknown

### Truncation (DDE/DDF/DDG)
- `N` = Not truncated
- `T` = Truncated
- `U` = Unknown

### Compliance Type (DDA)
- `F` = Fully compliant
- `N` = Non-compliant
- `M` = Materially compliant

## API Reference

### Encoding

```python
from aamva_license_generator.barcode import AAMVAEncoder, encode_license_data

# Simple function
barcode = encode_license_data(dl_data, jurisdiction_data=None, version=AAMVAVersion.VERSION_10)

# Full control
encoder = AAMVAEncoder(version=AAMVAVersion.VERSION_10)
barcode = encoder.encode([dl_subfile, juris_subfile], validate=True)
```

### Decoding

```python
from aamva_license_generator.barcode import AAMVADecoder, decode_license_data

# Simple function
data = decode_license_data(barcode_string, strict=False)

# Full control
decoder = AAMVADecoder(strict=False)
header, subfiles = decoder.decode(barcode_string)
```

### Validation

```python
from aamva_license_generator.barcode import AAMVAValidator, validate_license_data

# Simple function
result = validate_license_data(subfiles, version=AAMVAVersion.VERSION_10, strict=False)

# Full control
validator = AAMVAValidator(version=AAMVAVersion.VERSION_10, strict=False)
result = validator.validate(subfiles)

# Check results
if result.is_valid:
    print("Valid!")
else:
    for error in result.errors:
        print(f"Error: {error.message}")
    for warning in result.warnings:
        print(f"Warning: {warning.message}")
```

### Rendering

```python
from aamva_license_generator.barcode import PDF417Renderer, render_barcode

# Simple function
render_barcode(barcode_string, 'output.bmp', columns=13, security_level=5)

# Full control
renderer = PDF417Renderer(columns=13, security_level=5, scale=1, ratio=3)
image = renderer.render(barcode_string, output_path='output.bmp', format='BMP')
```

### Formatting

```python
from aamva_license_generator.barcode import BarcodeFormatter, format_license_summary

# License summary
summary = format_license_summary(dl_fields)

# Table format
table = BarcodeFormatter.format_table(subfile)

# Raw barcode with control characters visible
raw = BarcodeFormatter.format_raw_barcode(barcode_string, show_invisible=True)

# Hex dump for debugging
hex_dump = BarcodeFormatter.format_hex_dump(barcode_string)
```

## Subfiles

### DL Subfile

```python
from aamva_license_generator.barcode import DLSubfile

subfile = DLSubfile(fields=dl_data)
subfile.add_field('DAQ', 'D1234567')
value = subfile.get_field('DAQ')
has_field = subfile.has_field('DAQ')
```

### Jurisdiction Subfile

```python
from aamva_license_generator.barcode import JurisdictionSubfile

subfile = JurisdictionSubfile(
    jurisdiction='AZ',
    fields={
        'ZAW': 'MARICOPA',  # County
        'ZAT': 'TEST',      # Custom field
    }
)
```

## IIN Lookups

```python
from aamva_license_generator.barcode import get_iin_by_state, get_state_by_iin

# State to IIN
iin = get_iin_by_state('CA')  # '636014'

# IIN to state
info = get_state_by_iin('636014')
# {'jurisdiction': 'California', 'abbr': 'CA', 'country': 'USA'}
```

## Field Definitions

```python
from aamva_license_generator.barcode import get_field_definition

field_def = get_field_definition('DAQ')
# field_def.code          -> 'DAQ'
# field_def.name          -> 'Customer ID Number'
# field_def.data_type     -> FieldDataType.ALPHANUMERIC
# field_def.max_length    -> 25
# field_def.category      -> FieldCategory.MANDATORY

is_valid, error = field_def.validate('D1234567')
```

## Exception Handling

```python
from aamva_license_generator.barcode import (
    EncodingError,
    DecodingError,
    ValidationError,
    RenderingError,
    SubfileError
)

try:
    barcode = encode_license_data(dl_data)
except EncodingError as e:
    print(f"Encoding error: {e}")

try:
    data = decode_license_data(barcode)
except DecodingError as e:
    print(f"Decoding error: {e}")
```

## Common Patterns

### Round-trip Encode/Decode

```python
# Encode
barcode = encode_license_data(original_data)

# Decode
decoded = decode_license_data(barcode)

# Extract DL fields
dl_fields = decoded['subfiles'][0]['fields']

# Verify
assert dl_fields['DAQ'] == original_data['DAQ']
```

### Validation Before Encoding

```python
# Create subfile
subfile = DLSubfile(fields=dl_data)

# Validate first
result = validate_license_data([subfile])

if result.is_valid:
    # Encode
    barcode = encode_license_data(dl_data)
else:
    # Handle errors
    for error in result.errors:
        print(f"Fix: {error}")
```

### Multiple Subfiles

```python
from aamva_license_generator.barcode import AAMVAEncoder, DLSubfile, JurisdictionSubfile

encoder = AAMVAEncoder()

# DL subfile
dl = DLSubfile(fields=dl_data)

# Jurisdiction subfile
juris = JurisdictionSubfile(
    jurisdiction='AZ',
    fields={'ZAW': 'MARICOPA'}
)

# Encode both
barcode = encoder.encode([dl, juris])
```

### Custom Rendering

```python
from aamva_license_generator.barcode import BarcodeImageRenderer, PDF417Renderer

# Create renderer
pdf417 = PDF417Renderer(columns=13, security_level=5)
renderer = BarcodeImageRenderer(pdf417)

# Render with border
bordered = renderer.render_with_border(
    barcode,
    border_size=20,
    background_color='white',
    output_path='output.png'
)

# Render with text
labeled = renderer.render_with_text(
    barcode,
    text='License: D1234567',
    output_path='output.png'
)
```

## Tips & Best Practices

### 1. Always Validate Before Encoding

```python
result = validate_license_data([subfile])
if result.is_valid:
    barcode = encoder.encode([subfile])
```

### 2. Use Specific Exceptions

```python
try:
    barcode = encode_license_data(data)
except EncodingError as e:
    # Handle encoding error
    pass
except ValidationError as e:
    # Handle validation error
    pass
```

### 3. Check IIN Consistency

```python
state = dl_data['DAJ']
iin = get_iin_by_state(state)
if not iin:
    print(f"Warning: Unknown state {state}")
```

### 4. Validate Dates

```python
# Ensure dates are in correct format
dob = '01011990'  # MMDDYYYY
assert len(dob) == 8
assert dob.isdigit()
```

### 5. Handle Optional Fields

```python
# Use .get() for optional fields
middle_name = dl_fields.get('DAD', '')  # Default to empty string
```

## Debugging

### View Raw Barcode

```python
from aamva_license_generator.barcode import BarcodeFormatter

# Show control characters
raw = BarcodeFormatter.format_raw_barcode(barcode, show_invisible=True)
print(raw)
```

### Hex Dump

```python
hex_dump = BarcodeFormatter.format_hex_dump(barcode)
print(hex_dump)
```

### Validation Details

```python
result = validate_license_data([subfile])
print(result)  # Full report

for issue in result.issues:
    print(f"[{issue.severity}] {issue.field}: {issue.message} ({issue.code})")
```

## Version Support

```python
from aamva_license_generator.barcode import AAMVAVersion

# Encode for specific version
barcode = encode_license_data(dl_data, version=AAMVAVersion.VERSION_09)

# Get mandatory fields for version
from aamva_license_generator.barcode import get_mandatory_fields
mandatory = get_mandatory_fields(AAMVAVersion.VERSION_10)
```

## Further Reading

- [Full Documentation](README.md)
- [Complete Examples](EXAMPLE.py)
- [AAMVA DL/ID Standard](https://www.aamva.org/)
