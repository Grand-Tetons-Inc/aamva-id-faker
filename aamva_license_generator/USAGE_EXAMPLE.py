"""
Usage examples for the AAMVA License Generator business logic layer.

This file demonstrates how to use the clean, testable business logic
modules to generate license data without any I/O or GUI dependencies.
"""

from datetime import date
from aamva_license_generator import (
    LicenseGenerator,
    AAMVABarcodeFormatter,
    LicenseValidator,
    StateFormatRegistry,
    Sex,
)


def example_1_basic_generation():
    """Example 1: Generate a single license for California."""
    print("=" * 60)
    print("Example 1: Basic License Generation")
    print("=" * 60)

    # Create generator
    generator = LicenseGenerator()

    # Generate California license
    license_obj = generator.generate_license(state_code="CA")

    # Access the data
    print(f"\nLicense Number: {license_obj.dl_subfile.license_number}")
    print(f"Holder: {license_obj.holder_name}")
    print(f"State: {license_obj.dl_subfile.address.state}")
    print(f"DOB: {license_obj.dl_subfile.person.date_of_birth}")
    print(f"Expires: {license_obj.dl_subfile.expiration_date}")
    print(f"Days until expiration: {license_obj.days_until_expiration}")


def example_2_specific_attributes():
    """Example 2: Generate license with specific sex."""
    print("\n" + "=" * 60)
    print("Example 2: Generate Male License")
    print("=" * 60)

    generator = LicenseGenerator()

    # Generate license for male person
    license_obj = generator.generate_license(state_code="NY", sex=Sex.MALE)

    print(f"\nName: {license_obj.holder_name}")
    print(f"Sex: {license_obj.dl_subfile.person.sex.value} (1=Male)")
    print(f"Height: {license_obj.dl_subfile.physical.height_inches} inches")
    print(f"Weight: {license_obj.dl_subfile.physical.weight_pounds} lbs")


def example_3_batch_generation():
    """Example 3: Generate multiple licenses."""
    print("\n" + "=" * 60)
    print("Example 3: Batch Generation")
    print("=" * 60)

    generator = LicenseGenerator()

    # Generate 5 Texas licenses
    licenses = generator.generate_batch(count=5, state_code="TX")

    print(f"\nGenerated {len(licenses)} Texas licenses:")
    for i, lic in enumerate(licenses, 1):
        print(f"  {i}. {lic.dl_subfile.license_number} - {lic.holder_name}")


def example_4_barcode_formatting():
    """Example 4: Generate and format as AAMVA barcode."""
    print("\n" + "=" * 60)
    print("Example 4: Barcode Formatting")
    print("=" * 60)

    generator = LicenseGenerator()
    formatter = AAMVABarcodeFormatter()

    # Generate license
    license_obj = generator.generate_license(state_code="FL")

    # Format as AAMVA barcode string
    barcode_string = formatter.format(license_obj)

    print(f"\nLicense: {license_obj.dl_subfile.license_number}")
    print(f"Barcode length: {len(barcode_string)} bytes")
    print(f"Barcode preview (first 100 chars):")
    print(f"  {repr(barcode_string[:100])}...")

    # Validate barcode
    is_valid = formatter.validate_barcode_string(barcode_string)
    print(f"\nBarcode valid: {is_valid}")


def example_5_validation():
    """Example 5: Validate license data."""
    print("\n" + "=" * 60)
    print("Example 5: License Validation")
    print("=" * 60)

    generator = LicenseGenerator()
    validator = LicenseValidator()

    # Generate license
    license_obj = generator.generate_license(state_code="WA")

    # Validate and get warnings
    try:
        warnings = validator.validate_all(license_obj)

        print(f"\nLicense: {license_obj.dl_subfile.license_number}")
        print(f"Validation: PASSED ✓")

        if warnings:
            print(f"\nWarnings ({len(warnings)}):")
            for warning in warnings:
                print(f"  - {warning}")
        else:
            print("\nNo warnings.")

    except Exception as e:
        print(f"\nValidation FAILED: {e}")


def example_6_state_formats():
    """Example 6: Explore state-specific formats."""
    print("\n" + "=" * 60)
    print("Example 6: State Format Registry")
    print("=" * 60)

    # Get all supported states
    states = StateFormatRegistry.get_supported_states()
    print(f"\nSupported states: {len(states)}")
    print(f"  {', '.join(states[:10])}... (showing first 10)")

    # Generate license numbers for different states
    print("\nSample license numbers by state:")
    sample_states = ["CA", "NY", "TX", "FL", "IL"]
    for state in sample_states:
        numbers = [
            StateFormatRegistry.generate_license_number(state) for _ in range(3)
        ]
        print(f"  {state}: {', '.join(numbers)}")


def example_7_all_states():
    """Example 7: Generate one license for each state."""
    print("\n" + "=" * 60)
    print("Example 7: Generate for All States")
    print("=" * 60)

    generator = LicenseGenerator()

    # Generate one license per state
    all_licenses = generator.generate_for_all_states()

    print(f"\nGenerated {len(all_licenses)} licenses (one per state)")
    print("\nSample licenses:")
    for state in ["CA", "NY", "TX", "FL", "WA"]:
        if state in all_licenses:
            lic = all_licenses[state]
            print(
                f"  {state}: {lic.dl_subfile.license_number} - {lic.holder_name}"
            )


def example_8_reproducible_generation():
    """Example 8: Reproducible generation with seed."""
    print("\n" + "=" * 60)
    print("Example 8: Reproducible Generation")
    print("=" * 60)

    # Generate with seed
    generator1 = LicenseGenerator(seed=42)
    license1 = generator1.generate_license(state_code="CA")

    # Generate again with same seed
    generator2 = LicenseGenerator(seed=42)
    license2 = generator2.generate_license(state_code="CA")

    print(f"\nLicense 1: {license1.dl_subfile.license_number}")
    print(f"License 2: {license2.dl_subfile.license_number}")
    print(f"\nSame license number: {license1.dl_subfile.license_number == license2.dl_subfile.license_number}")
    print(f"Same person name: {license1.holder_name == license2.holder_name}")


def example_9_minimal_generator():
    """Example 9: Use minimal generator for compact barcodes."""
    print("\n" + "=" * 60)
    print("Example 9: Minimal License Generation")
    print("=" * 60)

    from aamva_license_generator.generators import MinimalLicenseGenerator

    # Create minimal generator
    generator = MinimalLicenseGenerator()
    license_obj = generator.generate_license(state_code="CA")

    print(f"\nLicense: {license_obj.dl_subfile.license_number}")
    print(f"Organ donor: {license_obj.dl_subfile.organ_donor}")
    print(f"Veteran: {license_obj.dl_subfile.veteran}")
    print(f"State custom fields: {len(license_obj.state_subfile.custom_fields)}")

    # Format as barcode
    formatter = AAMVABarcodeFormatter()
    barcode = formatter.format(license_obj)
    print(f"\nBarcode size: {len(barcode)} bytes (compact)")


def example_10_data_access():
    """Example 10: Access nested data structures."""
    print("\n" + "=" * 60)
    print("Example 10: Accessing Nested Data")
    print("=" * 60)

    generator = LicenseGenerator()
    license_obj = generator.generate_license(state_code="OH")

    # Access person data
    person = license_obj.dl_subfile.person
    print(f"\nPerson Information:")
    print(f"  Name: {person.full_name}")
    print(f"  DOB: {person.date_of_birth}")
    print(f"  Age: {person.age:.1f} years")
    print(f"  Sex: {'Male' if person.sex == Sex.MALE else 'Female'}")

    # Access physical attributes
    physical = license_obj.dl_subfile.physical
    print(f"\nPhysical Attributes:")
    print(f"  Height: {physical.height_inches} inches")
    print(f"  Weight: {physical.weight_pounds} lbs")
    print(f"  Eyes: {physical.eye_color.value}")
    print(f"  Hair: {physical.hair_color.value}")

    # Access address
    address = license_obj.dl_subfile.address
    print(f"\nAddress:")
    print(f"  {address.street}")
    print(f"  {address.city}, {address.state} {address.postal_code}")

    # Access license metadata
    print(f"\nLicense Metadata:")
    print(f"  IIN: {license_obj.jurisdiction_iin}")
    print(f"  Issue Date: {license_obj.dl_subfile.issue_date}")
    print(f"  Expiration: {license_obj.dl_subfile.expiration_date}")
    print(f"  Expired: {license_obj.is_expired}")


if __name__ == "__main__":
    """Run all examples."""
    print("\n" + "=" * 60)
    print("AAMVA License Generator - Usage Examples")
    print("Business Logic Layer Demonstration")
    print("=" * 60)

    example_1_basic_generation()
    example_2_specific_attributes()
    example_3_batch_generation()
    example_4_barcode_formatting()
    example_5_validation()
    example_6_state_formats()
    example_7_all_states()
    example_8_reproducible_generation()
    example_9_minimal_generator()
    example_10_data_access()

    print("\n" + "=" * 60)
    print("All examples completed successfully!")
    print("=" * 60 + "\n")
