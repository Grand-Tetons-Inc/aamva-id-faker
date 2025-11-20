#!/usr/bin/env python3
"""
Validation Engine Demonstration

This script demonstrates the comprehensive validation capabilities
of the AAMVA license generator validation engine.
"""

import sys
import os
from datetime import date, timedelta
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aamva_license_generator.validation import (
    LicenseValidator,
    StateCodeValidator,
    DateValidator,
    LicenseNumberValidator,
    AddressValidator,
    PersonalDataValidator,
    check_aamva_compliance,
    LicenseData,
    ValidationLevel,
)


def print_validation_result(result, title="Validation Result"):
    """Pretty print validation results."""
    print(f"\n{'='*70}")
    print(f"{title}")
    print(f"{'='*70}")
    print(f"Valid: {result.is_valid}")
    print(f"Errors: {len(result.errors)}")
    print(f"Warnings: {len(result.warnings)}")
    print(f"Info: {len(result.info)}")

    if result.errors:
        print(f"\n{'-'*70}")
        print("ERRORS:")
        for error in result.errors:
            print(f"  [{error.field_name}] {error.message}")
            if error.suggestions:
                print(f"    Suggestions: {', '.join(error.suggestions)}")
            if error.auto_fix:
                print(f"    Auto-fix: {error.auto_fix}")

    if result.warnings:
        print(f"\n{'-'*70}")
        print("WARNINGS:")
        for warning in result.warnings:
            print(f"  [{warning.field_name}] {warning.message}")

    if result.info:
        print(f"\n{'-'*70}")
        print("INFO:")
        for info_msg in result.info:
            print(f"  [{info_msg.field_name}] {info_msg.message}")

    print(f"{'='*70}\n")


def demo_state_code_validation():
    """Demonstrate state code validation with fuzzy matching."""
    print("\n" + "="*70)
    print("DEMO 1: State Code Validation with Fuzzy Matching")
    print("="*70)

    validator = StateCodeValidator()

    test_cases = [
        "CA",           # Valid
        "NY",           # Valid
        "XX",           # Invalid - no match
        "CALIFORNIA",   # Full name instead of code
        "Cali",         # Typo
        "CAL",          # Partial match
        "NW",           # Close to NY
        "",             # Empty
    ]

    for test_code in test_cases:
        print(f"\nTesting: '{test_code}'")
        result = validator.validate(test_code)
        print(f"  Valid: {result.is_valid}")
        print(f"  Level: {result.level.value}")
        print(f"  Message: {result.message}")
        if result.suggestions:
            print(f"  Suggestions: {', '.join(result.suggestions[:5])}")
        if result.auto_fix:
            print(f"  Auto-fix: {result.auto_fix}")


def demo_date_validation():
    """Demonstrate date validation and sequencing."""
    print("\n" + "="*70)
    print("DEMO 2: Date Validation and Cross-Field Validation")
    print("="*70)

    validator = DateValidator()

    # Valid dates
    print("\n--- Valid Date Sequence ---")
    dob = date(1990, 5, 15)
    issue = date(2020, 1, 10)
    exp = date(2028, 5, 15)

    dob_result = validator.validate_date_of_birth(dob)
    print(f"DOB: {dob_result.message}")

    seq_results = validator.validate_date_sequence(dob, issue, exp)
    if seq_results:
        for res in seq_results:
            print(f"  {res.message}")
    else:
        print("  All dates in correct sequence!")

    # Invalid sequence - DOB after issue
    print("\n--- Invalid Sequence (DOB after Issue) ---")
    bad_dob = date(2021, 1, 1)
    bad_results = validator.validate_date_sequence(bad_dob, issue, exp)
    for res in bad_results:
        print(f"  ERROR: {res.message}")

    # Warning - age too young
    print("\n--- Warning (Minor License) ---")
    young_dob = date(2005, 1, 1)
    young_result = validator.validate_date_of_birth(young_dob)
    print(f"  {young_result.level.value.upper()}: {young_result.message}")


def demo_license_number_validation():
    """Demonstrate state-specific license number validation."""
    print("\n" + "="*70)
    print("DEMO 3: State-Specific License Number Validation")
    print("="*70)

    validator = LicenseNumberValidator()

    test_cases = [
        ("CA", "D1234567"),      # Valid CA format
        ("CA", "12345678"),      # Invalid CA format
        ("NY", "D1234567"),      # Valid NY format
        ("NY", "D123456789012345678"),  # Valid NY format (18 digits)
        ("TX", "12345678"),      # Valid TX format
        ("FL", "D123456789012"), # Valid FL format
        ("XX", "ABC123"),        # Invalid state
    ]

    for state, license_num in test_cases:
        print(f"\nTesting: {state} - {license_num}")
        result = validator.validate(license_num, state)
        print(f"  Valid: {result.is_valid}")
        print(f"  Level: {result.level.value}")
        print(f"  Message: {result.message}")


def demo_address_validation():
    """Demonstrate address validation."""
    print("\n" + "="*70)
    print("DEMO 4: Address Validation")
    print("="*70)

    validator = AddressValidator()

    # Street address
    print("\n--- Street Address ---")
    addresses = [
        "123 MAIN ST",
        "P.O. BOX 456",  # Warning - PO Box
        "A" * 40,        # Too long
        "",              # Empty
    ]

    for addr in addresses:
        result = validator.validate_address(addr)
        print(f"  {addr[:30]+'...' if len(addr) > 30 else addr}")
        print(f"    {result.level.value.upper()}: {result.message}")

    # ZIP codes
    print("\n--- ZIP Code Validation ---")
    zip_codes = [
        "90001",         # Valid 5-digit
        "90001-2345",    # Valid 9-digit
        "900012345",     # Valid 9-digit (no dash)
        "1234",          # Invalid - too short
        "ABC12",         # Invalid - letters
    ]

    for zip_code in zip_codes:
        result = validator.validate_zip_code(zip_code)
        print(f"  {zip_code}")
        print(f"    {result.level.value.upper()}: {result.message}")
        if result.auto_fix:
            print(f"    Auto-fix: {result.auto_fix}")


def demo_personal_data_validation():
    """Demonstrate personal characteristic validation."""
    print("\n" + "="*70)
    print("DEMO 5: Personal Data Validation")
    print("="*70)

    validator = PersonalDataValidator()

    # Height validation
    print("\n--- Height Validation ---")
    heights = ["69", "35", "97", "abc"]  # Valid, too short, too tall, invalid

    for height in heights:
        result = validator.validate_height(height)
        print(f"  {height} inches")
        print(f"    {result.level.value.upper()}: {result.message}")

    # Weight validation
    print("\n--- Weight Validation ---")
    weights = ["180", "40", "550", "xyz"]  # Valid, too light, too heavy, invalid

    for weight in weights:
        result = validator.validate_weight(weight)
        print(f"  {weight} lbs")
        print(f"    {result.level.value.upper()}: {result.message}")


def demo_comprehensive_validation():
    """Demonstrate comprehensive license validation."""
    print("\n" + "="*70)
    print("DEMO 6: Comprehensive License Validation")
    print("="*70)

    validator = LicenseValidator()

    # Valid license data
    print("\n--- Valid License Data ---")
    valid_data = {
        "state": "CA",
        "license_number": "D1234567",
        "first_name": "JOHN",
        "last_name": "DOE",
        "middle_name": "MICHAEL",
        "date_of_birth": date(1990, 5, 15),
        "issue_date": date(2020, 1, 10),
        "expiration_date": date(2028, 5, 15),
        "sex": "1",
        "eye_color": "BRO",
        "hair_color": "BRO",
        "height": "69",
        "weight": "180",
        "address": "123 MAIN ST",
        "city": "LOS ANGELES",
        "postal_code": "90001",
    }

    result = validator.validate(valid_data)
    print_validation_result(result, "Valid License Data")

    # Invalid license data (multiple errors)
    print("\n--- Invalid License Data (Multiple Errors) ---")
    invalid_data = {
        "state": "XX",              # Invalid state
        "license_number": "ABC",    # Wrong format for any state
        "first_name": "JOHN",
        "last_name": "DOE",
        "date_of_birth": date(2022, 1, 1),   # Too young
        "issue_date": date(2020, 1, 10),
        "expiration_date": date(2019, 5, 15),  # Before issue date!
        "sex": "3",                 # Invalid value
        "eye_color": "XXX",         # Invalid
        "hair_color": "BRO",
        "height": "25",             # Too short
        "weight": "600",            # Too heavy
        "address": "A" * 40,        # Too long
        "city": "LOS ANGELES",
        "postal_code": "ABC",       # Invalid
    }

    result = validator.validate(invalid_data)
    print_validation_result(result, "Invalid License Data (Multiple Errors)")


def demo_aamva_compliance():
    """Demonstrate AAMVA compliance checking."""
    print("\n" + "="*70)
    print("DEMO 7: AAMVA Compliance Validation")
    print("="*70)

    # Valid AAMVA-compliant data
    print("\n--- REAL ID Compliant License ---")
    compliant_data = {
        "license_number": "D1234567",
        "last_name": "DOE",
        "first_name": "JOHN",
        "middle_name": "MICHAEL",
        "date_of_birth": "05151990",
        "issue_date": "01102020",
        "expiration_date": "05152028",
        "sex": "1",
        "eye_color": "BRO",
        "hair_color": "BRO",
        "height": "69",
        "weight": "180",
        "address": "123 MAIN ST",
        "city": "LOS ANGELES",
        "state": "CA",
        "postal_code": "900010000",
        "vehicle_class": "D",
        "compliance_type": "F",  # REAL ID compliant
        "truncation_last_name": "N",
        "truncation_first_name": "N",
        "truncation_middle_name": "N",
    }

    result = check_aamva_compliance(compliant_data)
    print_validation_result(result, "REAL ID Compliant License")

    # Non-compliant (missing mandatory fields)
    print("\n--- Non-Compliant (Missing Fields) ---")
    non_compliant_data = {
        "license_number": "D1234567",
        "last_name": "DOE",
        # Missing first_name
        # Missing dates
        "state": "CA",
    }

    result = check_aamva_compliance(non_compliant_data)
    print_validation_result(result, "Non-Compliant License")

    # Name truncation warning
    print("\n--- Name Truncation Validation ---")
    long_name_data = {
        "license_number": "D1234567",
        "last_name": "VERYLONGFAMILYNAMETHATEXCEEDSLIMIT",  # 40 chars
        "first_name": "JOHN",
        "date_of_birth": "05151990",
        "issue_date": "01102020",
        "expiration_date": "05152028",
        "sex": "1",
        "eye_color": "BRO",
        "height": "69",
        "address": "123 MAIN ST",
        "city": "LOS ANGELES",
        "state": "CA",
        "postal_code": "900010000",
        "truncation_last_name": "N",  # Should be "T"
    }

    result = check_aamva_compliance(long_name_data)
    print_validation_result(result, "Name Truncation Validation")


def demo_pydantic_schema():
    """Demonstrate Pydantic schema validation."""
    print("\n" + "="*70)
    print("DEMO 8: Pydantic Schema Validation")
    print("="*70)

    # Valid data
    print("\n--- Valid Pydantic Model ---")
    try:
        valid_license = LicenseData(
            license_number="D1234567",
            state="CA",
            last_name="DOE",
            first_name="JOHN",
            middle_name="MICHAEL",
            date_of_birth=date(1990, 5, 15),
            issue_date=date(2020, 1, 10),
            expiration_date=date(2028, 5, 15),
            sex="1",
            eye_color="BRO",
            hair_color="BRO",
            height="69",
            weight="180",
            race="W",
            address="123 MAIN ST",
            city="LOS ANGELES",
            postal_code="90001",
        )
        print("  SUCCESS: Valid license created")
        print(f"  License Number: {valid_license.license_number}")
        print(f"  Name: {valid_license.first_name} {valid_license.last_name}")
        print(f"  State: {valid_license.state}")

        # Convert to AAMVA dict
        aamva_dict = valid_license.to_aamva_dict()
        print(f"\n  AAMVA Fields: {len(aamva_dict)} fields")
        for key in sorted(aamva_dict.keys())[:5]:
            print(f"    {key}: {aamva_dict[key]}")

    except Exception as e:
        print(f"  ERROR: {e}")

    # Invalid data - Pydantic will catch errors
    print("\n--- Invalid Pydantic Model (Validation Errors) ---")
    try:
        invalid_license = LicenseData(
            license_number="D1234567",
            state="CALIFORNIA",  # Should be 2 letters
            last_name="DOE",
            first_name="JOHN",
            date_of_birth=date(2022, 1, 1),  # Too young
            issue_date=date(2020, 1, 10),
            expiration_date=date(2019, 5, 15),  # Before issue!
            sex="3",  # Invalid value
            eye_color="INVALID",  # Invalid
            hair_color="BRO",
            height="999",  # Too tall
            weight="1000",  # Too heavy
            address="123 MAIN ST",
            city="LOS ANGELES",
            postal_code="ABC",  # Invalid
        )
        print("  SUCCESS: This shouldn't happen!")

    except Exception as e:
        print(f"  CAUGHT VALIDATION ERROR:")
        print(f"  {type(e).__name__}: {str(e)[:200]}")


def main():
    """Run all demonstrations."""
    print("\n" + "="*70)
    print("AAMVA LICENSE VALIDATION ENGINE DEMONSTRATION")
    print("="*70)
    print("\nThis demo showcases the comprehensive validation capabilities")
    print("including field-level, cross-field, state-specific, and AAMVA")
    print("compliance validation.\n")

    demos = [
        ("State Code Validation", demo_state_code_validation),
        ("Date Validation", demo_date_validation),
        ("License Number Validation", demo_license_number_validation),
        ("Address Validation", demo_address_validation),
        ("Personal Data Validation", demo_personal_data_validation),
        ("Comprehensive Validation", demo_comprehensive_validation),
        ("AAMVA Compliance", demo_aamva_compliance),
        ("Pydantic Schema", demo_pydantic_schema),
    ]

    for i, (name, demo_func) in enumerate(demos, 1):
        print(f"\n\n{'#'*70}")
        print(f"# {i}/{len(demos)}: {name}")
        print(f"{'#'*70}")
        try:
            demo_func()
        except Exception as e:
            print(f"\nERROR in demo: {e}")
            import traceback
            traceback.print_exc()

    print("\n\n" + "="*70)
    print("DEMONSTRATION COMPLETE")
    print("="*70)
    print("\nThe validation engine provides:")
    print("  - Real-time field validation")
    print("  - Fuzzy matching for state codes")
    print("  - Comprehensive error messages")
    print("  - Auto-fix suggestions")
    print("  - Cross-field validation")
    print("  - State-specific rules")
    print("  - AAMVA compliance checking")
    print("  - Pydantic schema validation")
    print("\nFor production use, integrate with GUI for real-time feedback!")


if __name__ == "__main__":
    main()
