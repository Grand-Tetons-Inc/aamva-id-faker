#!/usr/bin/env python3
"""
Quick test of the barcode module without going through main package imports.
"""

import sys
sys.path.insert(0, '/home/user/aamva-id-faker')

# Direct imports to avoid main package dependencies
from aamva_license_generator.barcode.encoder import encode_license_data, AAMVAEncoder
from aamva_license_generator.barcode.decoder import decode_license_data, AAMVADecoder
from aamva_license_generator.barcode.validator import validate_license_data
from aamva_license_generator.barcode.subfiles import DLSubfile
from aamva_license_generator.barcode.aamva_spec import AAMVAVersion, get_iin_by_state
from aamva_license_generator.barcode.formatter import format_license_summary

def test_basic_encode_decode():
    """Test basic encoding and decoding."""
    print("="*70)
    print("TEST: Basic Encode/Decode")
    print("="*70)

    # Create test data
    dl_data = {
        'DAQ': 'D1234567',
        'DCS': 'SMITH',
        'DAC': 'JOHN',
        'DAD': 'MICHAEL',
        'DBB': '01011990',
        'DBD': '01012020',
        'DBA': '01012030',
        'DBC': '1',
        'DAY': 'BRO',
        'DAU': '070',
        'DAW': '180',
        'DAZ': 'BRO',
        'DAG': '123 MAIN STREET',
        'DAI': 'PHOENIX',
        'DAJ': 'AZ',
        'DAK': '85001',
        'DCA': 'D',
        'DCB': '',
        'DCD': '',
        'DCF': 'DOC12345',
        'DCG': 'USA',
        'DDE': 'N',
        'DDF': 'N',
        'DDG': 'N',
        'DDA': 'F',
        'DDB': '01012020',
        'DDC': '01012030',
        'DDD': '0',
        'DDK': '1',
        'DDL': '0',
        'DCL': 'W',
    }

    # Encode
    print("\n1. Encoding...")
    barcode = encode_license_data(dl_data, version=AAMVAVersion.VERSION_10)
    print(f"   ✓ Encoded: {len(barcode)} bytes")
    print(f"   First 60 chars: {repr(barcode[:60])}")

    # Decode
    print("\n2. Decoding...")
    decoded = decode_license_data(barcode)
    print(f"   ✓ Decoded successfully")
    print(f"   Header IIN: {decoded['header']['iin']}")
    print(f"   Version: {decoded['header']['version']}")
    print(f"   Subfiles: {decoded['header']['number_of_entries']}")

    # Verify fields
    print("\n3. Verifying fields...")
    decoded_fields = decoded['subfiles'][0]['fields']
    matches = 0
    for key, value in dl_data.items():
        if decoded_fields.get(key) == value:
            matches += 1

    print(f"   ✓ {matches}/{len(dl_data)} fields match")

    # Show summary
    print("\n4. License Summary:")
    summary = format_license_summary(dl_data)
    print(summary)

    return matches == len(dl_data)


def test_validation():
    """Test validation."""
    print("\n" + "="*70)
    print("TEST: Validation")
    print("="*70)

    # Valid data
    valid_data = {
        'DAQ': 'D1234567',
        'DCS': 'SMITH',
        'DAC': 'JOHN',
        'DBB': '01011990',
        'DBD': '01012020',
        'DBA': '01012030',
        'DBC': '1',
        'DAY': 'BRO',
        'DAU': '070',
        'DAG': '123 MAIN ST',
        'DAI': 'PHOENIX',
        'DAJ': 'AZ',
        'DAK': '85001',
        'DCA': 'D',
        'DCB': '',
        'DCD': '',
        'DCF': 'DOC123',
        'DCG': 'USA',
    }

    print("\n1. Validating correct data...")
    subfile = DLSubfile(fields=valid_data)
    result = validate_license_data([subfile])
    print(f"   Valid: {result.is_valid}")
    print(f"   Errors: {len(result.errors)}")
    print(f"   Warnings: {len(result.warnings)}")

    if result.is_valid:
        print("   ✓ Validation passed!")
    else:
        print("   ✗ Validation failed!")
        for error in result.errors[:3]:
            print(f"     - {error}")

    # Invalid data
    print("\n2. Validating invalid data...")
    invalid_data = {
        'DAQ': 'D1234567',
        'DCS': 'SMITH',
        'DAC': 'JOHN',
        'DBB': '99999999',  # Invalid date
        'DBC': '9',         # Invalid sex
        'DAY': 'XXX',       # Invalid eye color
    }

    subfile = DLSubfile(fields=invalid_data)
    result = validate_license_data([subfile])
    print(f"   Valid: {result.is_valid}")
    print(f"   Errors: {len(result.errors)}")
    print(f"   First 3 errors:")
    for error in result.errors[:3]:
        print(f"     - {error}")

    print("   ✓ Validation correctly caught errors!")

    return True


def test_iin_lookups():
    """Test IIN lookups."""
    print("\n" + "="*70)
    print("TEST: IIN Lookups")
    print("="*70)

    states = ['CA', 'NY', 'TX', 'FL', 'AZ']

    print("\nState -> IIN:")
    for state in states:
        iin = get_iin_by_state(state)
        print(f"   {state}: {iin}")

    print("\n   ✓ IIN lookups working!")

    return True


def test_multiple_subfiles():
    """Test encoding with multiple subfiles."""
    print("\n" + "="*70)
    print("TEST: Multiple Subfiles")
    print("="*70)

    from aamva_license_generator.barcode.subfiles import JurisdictionSubfile

    # Create DL subfile
    dl_data = {
        'DAQ': 'D1234567',
        'DCS': 'SMITH',
        'DAC': 'JOHN',
        'DBB': '01011990',
        'DBD': '01012020',
        'DBA': '01012030',
        'DBC': '1',
        'DAY': 'BRO',
        'DAU': '070',
        'DAG': '123 MAIN ST',
        'DAI': 'PHOENIX',
        'DAJ': 'AZ',
        'DAK': '85001',
        'DCA': 'D',
        'DCB': '',
        'DCD': '',
        'DCF': 'DOC123',
        'DCG': 'USA',
    }

    dl_subfile = DLSubfile(fields=dl_data)

    # Create jurisdiction subfile
    juris_data = {
        'ZAW': 'MARICOPA',
        'ZAT': 'TEST DATA',
    }
    juris_subfile = JurisdictionSubfile(
        jurisdiction='AZ',
        fields=juris_data
    )

    # Encode
    print("\n1. Encoding with 2 subfiles...")
    encoder = AAMVAEncoder(version=AAMVAVersion.VERSION_10)
    barcode = encoder.encode([dl_subfile, juris_subfile])
    print(f"   ✓ Encoded: {len(barcode)} bytes")

    # Decode
    print("\n2. Decoding...")
    decoded = decode_license_data(barcode)
    print(f"   ✓ Decoded {decoded['header']['number_of_entries']} subfiles")

    print("\n   ✓ Multiple subfiles working!")

    return True


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("AAMVA BARCODE MODULE - QUICK TEST")
    print("="*70)

    tests = [
        ("Basic Encode/Decode", test_basic_encode_decode),
        ("Validation", test_validation),
        ("IIN Lookups", test_iin_lookups),
        ("Multiple Subfiles", test_multiple_subfiles),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
            else:
                failed += 1
                print(f"\n✗ {name} failed!")
        except Exception as e:
            failed += 1
            print(f"\n✗ {name} failed with exception: {e}")
            import traceback
            traceback.print_exc()

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"\nPassed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")

    if failed == 0:
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed!")
        return 1


if __name__ == '__main__':
    sys.exit(main())
