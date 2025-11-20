#!/usr/bin/env python3
"""
AAMVA Barcode Module - Comprehensive Example

This example demonstrates all major features of the refactored
AAMVA barcode module including encoding, decoding, validation,
and rendering.

Run this file to see the barcode module in action!
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from aamva_license_generator.barcode import (
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

    # Rendering
    PDF417Renderer,
    render_barcode,

    # Subfiles
    DLSubfile,
    JurisdictionSubfile,

    # Spec
    AAMVAVersion,
    get_field_definition,
    get_iin_by_state,

    # Formatting
    BarcodeFormatter,
    format_license_summary,
)


def example_1_basic_encoding():
    """Example 1: Basic encoding of license data."""
    print("="*70)
    print("EXAMPLE 1: Basic Encoding")
    print("="*70)

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
        'DAU': '070',                # Height (70 inches = 5'10")
        'DAW': '180',                # Weight (lbs)
        'DAZ': 'BRO',                # Hair color
        'DAG': '123 MAIN STREET',    # Address
        'DAI': 'PHOENIX',            # City
        'DAJ': 'AZ',                 # State
        'DAK': '85001',              # ZIP
        'DCA': 'D',                  # Vehicle class
        'DCB': '',                   # Restrictions
        'DCD': '',                   # Endorsements
        'DCF': 'DOC12345',           # Document discriminator
        'DCG': 'USA',                # Country
        'DDE': 'N',                  # Family name truncation
        'DDF': 'N',                  # First name truncation
        'DDG': 'N',                  # Middle name truncation
        'DDA': 'F',                  # Compliance type
        'DDB': '01012020',           # Card revision date
        'DDC': '01012030',           # Hazmat expiry
        'DDD': '0',                  # Limited duration
        'DDK': '1',                  # Organ donor
        'DDL': '0',                  # Veteran
        'DCL': 'W',                  # Race
    }

    # Encode to barcode string
    barcode_string = encode_license_data(dl_data, version=AAMVAVersion.VERSION_10)

    print(f"\n✓ Encoded barcode successfully!")
    print(f"  Barcode length: {len(barcode_string)} bytes")
    print(f"  First 50 chars: {repr(barcode_string[:50])}")

    return barcode_string, dl_data


def example_2_decoding(barcode_string):
    """Example 2: Decoding a barcode string."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Decoding")
    print("="*70)

    # Decode barcode string
    data = decode_license_data(barcode_string)

    # Access header info
    header = data['header']
    print(f"\nHeader Information:")
    print(f"  IIN: {header['iin']}")
    print(f"  Version: {header['version']}")
    print(f"  Jurisdiction Version: {header['jurisdiction_version']}")
    print(f"  Number of Subfiles: {header['number_of_entries']}")

    if header['jurisdiction_info']:
        juris = header['jurisdiction_info']
        print(f"  Jurisdiction: {juris['jurisdiction']} ({juris['abbr']})")

    # Access DL fields
    print(f"\nDL Subfile Fields:")
    dl_fields = data['subfiles'][0]['fields']

    # Show selected fields
    print(f"  License Number: {dl_fields.get('DAQ')}")
    print(f"  Name: {dl_fields.get('DAC')} {dl_fields.get('DAD')} {dl_fields.get('DCS')}")
    print(f"  DOB: {dl_fields.get('DBB')}")
    print(f"  Address: {dl_fields.get('DAG')}, {dl_fields.get('DAI')}, {dl_fields.get('DAJ')}")

    print(f"\n✓ Decoded {len(dl_fields)} fields successfully!")

    return data


def example_3_validation(dl_data):
    """Example 3: Validating license data."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Validation")
    print("="*70)

    # Create subfile
    subfile = DLSubfile(fields=dl_data)

    # Validate
    result = validate_license_data([subfile], version=AAMVAVersion.VERSION_10)

    print(f"\nValidation Result:")
    print(f"  Valid: {result.is_valid}")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Warnings: {len(result.warnings)}")
    print(f"  Info: {len(result.info)}")

    if result.errors:
        print(f"\nErrors:")
        for error in result.errors:
            print(f"  ✗ {error}")

    if result.warnings:
        print(f"\nWarnings:")
        for warning in result.warnings:
            print(f"  ⚠ {warning}")

    if result.is_valid:
        print(f"\n✓ All validation checks passed!")

    return result


def example_4_validation_with_errors():
    """Example 4: Validation catching errors."""
    print("\n" + "="*70)
    print("EXAMPLE 4: Validation with Errors")
    print("="*70)

    # Create invalid data (missing mandatory fields, invalid values)
    invalid_data = {
        'DAQ': 'D1234567',
        'DCS': 'SMITH',
        'DAC': 'JOHN',
        'DBB': '99999999',  # Invalid date
        'DBC': '9',         # Invalid sex code (must be 1, 2, or 9)
        'DAY': 'XXX',       # Invalid eye color
        # Missing many mandatory fields...
    }

    subfile = DLSubfile(fields=invalid_data)
    result = validate_license_data([subfile], version=AAMVAVersion.VERSION_10)

    print(f"\nValidation Result (intentionally invalid):")
    print(f"  Valid: {result.is_valid}")
    print(f"  Errors: {len(result.errors)}")

    print(f"\nFirst 5 errors:")
    for error in result.errors[:5]:
        print(f"  ✗ {error}")

    print(f"\n✓ Validation correctly caught {len(result.errors)} errors!")

    return result


def example_5_encoding_with_jurisdiction_subfile(dl_data):
    """Example 5: Encoding with jurisdiction-specific subfile."""
    print("\n" + "="*70)
    print("EXAMPLE 5: Multiple Subfiles")
    print("="*70)

    # Create encoder
    encoder = AAMVAEncoder(version=AAMVAVersion.VERSION_10)

    # Create DL subfile
    dl_subfile = DLSubfile(fields=dl_data)

    # Create Arizona jurisdiction-specific subfile
    juris_data = {
        'ZAW': 'MARICOPA',          # County
        'ZAT': 'ADDITIONAL DATA',   # Additional field
        'ZAX': '12345',             # Custom field
    }
    juris_subfile = JurisdictionSubfile(
        jurisdiction='AZ',
        fields=juris_data
    )

    # Encode with multiple subfiles
    barcode_string = encoder.encode([dl_subfile, juris_subfile])

    print(f"\n✓ Encoded barcode with 2 subfiles!")
    print(f"  Total length: {len(barcode_string)} bytes")
    print(f"  DL subfile: {len(dl_subfile.fields)} fields")
    print(f"  Jurisdiction subfile: {len(juris_subfile.fields)} fields")

    # Decode to verify
    decoded = decode_license_data(barcode_string)
    print(f"  Decoded: {decoded['header']['number_of_entries']} subfiles")

    return barcode_string


def example_6_formatting(dl_data):
    """Example 6: Formatting and display."""
    print("\n" + "="*70)
    print("EXAMPLE 6: Formatting and Display")
    print("="*70)

    # Create subfile
    subfile = DLSubfile(fields=dl_data)

    # Format as table
    print("\nTable Format:")
    print(BarcodeFormatter.format_table(subfile))

    # Format license summary
    print("\nLicense Summary:")
    print(format_license_summary(dl_data))

    # Format compact
    print("\nCompact Format:")
    compact = BarcodeFormatter.format_compact(subfile)
    print(f"  {compact[:100]}...")

    print(f"\n✓ Formatted data in multiple ways!")


def example_7_field_definitions():
    """Example 7: Using field definitions."""
    print("\n" + "="*70)
    print("EXAMPLE 7: Field Definitions")
    print("="*70)

    # Get field definition
    field_def = get_field_definition('DAQ')

    print(f"\nField DAQ (License Number):")
    print(f"  Name: {field_def.name}")
    print(f"  Data Type: {field_def.data_type.value}")
    print(f"  Max Length: {field_def.max_length}")
    print(f"  Category: {field_def.category.value}")
    print(f"  Description: {field_def.description}")

    # Validate values
    test_values = ['D1234567', 'X' * 30, '']

    print(f"\nValidation Examples:")
    for value in test_values:
        is_valid, error = field_def.validate(value)
        status = "✓" if is_valid else "✗"
        print(f"  {status} '{value}': {error if error else 'Valid'}")

    print(f"\n✓ Field definition system working!")


def example_8_iin_lookups():
    """Example 8: IIN lookups."""
    print("\n" + "="*70)
    print("EXAMPLE 8: IIN Lookups")
    print("="*70)

    # Get IIN by state
    states = ['CA', 'NY', 'TX', 'FL', 'AZ']

    print(f"\nIIN Lookups:")
    for state in states:
        iin = get_iin_by_state(state)
        print(f"  {state}: {iin}")

    from aamva_license_generator.barcode import get_state_by_iin

    # Reverse lookup
    iin = '636014'
    info = get_state_by_iin(iin)
    print(f"\nReverse Lookup for IIN {iin}:")
    print(f"  Jurisdiction: {info['jurisdiction']}")
    print(f"  Abbreviation: {info['abbr']}")
    print(f"  Country: {info['country']}")

    print(f"\n✓ IIN lookup system working!")


def example_9_round_trip():
    """Example 9: Round-trip encode/decode test."""
    print("\n" + "="*70)
    print("EXAMPLE 9: Round-Trip Test")
    print("="*70)

    # Original data
    original_data = {
        'DAQ': 'TEST123',
        'DCS': 'ROUNDTRIP',
        'DAC': 'TEST',
        'DBB': '01011990',
        'DBD': '01012020',
        'DBA': '01012030',
        'DBC': '1',
        'DAY': 'BLU',
        'DAU': '072',
        'DAG': 'TEST ADDRESS',
        'DAI': 'TEST CITY',
        'DAJ': 'CA',
        'DAK': '12345',
        'DCA': 'D',
        'DCB': '',
        'DCD': '',
        'DCF': 'DOC999',
        'DCG': 'USA',
    }

    # Encode
    barcode = encode_license_data(original_data)
    print(f"  Encoded: {len(barcode)} bytes")

    # Decode
    decoded = decode_license_data(barcode)
    decoded_fields = decoded['subfiles'][0]['fields']
    print(f"  Decoded: {len(decoded_fields)} fields")

    # Compare
    print(f"\nField Comparison:")
    all_match = True
    for key, value in original_data.items():
        decoded_value = decoded_fields.get(key, '')
        match = (value == decoded_value)
        all_match = all_match and match
        status = "✓" if match else "✗"
        print(f"  {status} {key}: {value} == {decoded_value}")

    if all_match:
        print(f"\n✓ Round-trip successful! All fields match!")
    else:
        print(f"\n✗ Round-trip failed! Some fields don't match!")

    return all_match


def example_10_rendering():
    """Example 10: Rendering to image (if libraries available)."""
    print("\n" + "="*70)
    print("EXAMPLE 10: Rendering")
    print("="*70)

    try:
        # Create simple test data
        test_data = {
            'DAQ': 'RENDER123',
            'DCS': 'TEST',
            'DAC': 'RENDER',
            'DBB': '01011990',
            'DBD': '01012020',
            'DBA': '01012030',
            'DBC': '1',
            'DAY': 'BRO',
            'DAU': '070',
            'DAG': 'TEST',
            'DAI': 'TEST',
            'DAJ': 'AZ',
            'DAK': '12345',
            'DCA': 'D',
            'DCB': '',
            'DCD': '',
            'DCF': 'DOC',
            'DCG': 'USA',
        }

        # Encode
        barcode = encode_license_data(test_data)

        # Try to render
        output_path = '/tmp/test_barcode.bmp'
        render_barcode(barcode, output_path)

        print(f"\n✓ Rendered barcode to: {output_path}")

        # Check file size
        if os.path.exists(output_path):
            size = os.path.getsize(output_path)
            print(f"  File size: {size} bytes")

    except Exception as e:
        print(f"\n⚠ Rendering skipped: {e}")
        print(f"  (Install pdf417 and Pillow to enable rendering)")


def main():
    """Run all examples."""
    print("\n" + "="*70)
    print("AAMVA BARCODE MODULE - COMPREHENSIVE EXAMPLES")
    print("="*70)

    try:
        # Example 1: Basic encoding
        barcode_string, dl_data = example_1_basic_encoding()

        # Example 2: Decoding
        decoded_data = example_2_decoding(barcode_string)

        # Example 3: Validation (valid data)
        validation_result = example_3_validation(dl_data)

        # Example 4: Validation (invalid data)
        error_result = example_4_validation_with_errors()

        # Example 5: Multiple subfiles
        multi_subfile_barcode = example_5_encoding_with_jurisdiction_subfile(dl_data)

        # Example 6: Formatting
        example_6_formatting(dl_data)

        # Example 7: Field definitions
        example_7_field_definitions()

        # Example 8: IIN lookups
        example_8_iin_lookups()

        # Example 9: Round-trip test
        roundtrip_success = example_9_round_trip()

        # Example 10: Rendering (optional)
        example_10_rendering()

        # Summary
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        print("\n✓ All examples completed successfully!")
        print("\nThe barcode module provides:")
        print("  • Clean encoding and decoding")
        print("  • Comprehensive validation")
        print("  • Multiple display formats")
        print("  • Field definitions and metadata")
        print("  • IIN lookup utilities")
        print("  • Round-trip encode/decode")
        print("  • PDF417 rendering")

    except Exception as e:
        print(f"\n✗ Example failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
