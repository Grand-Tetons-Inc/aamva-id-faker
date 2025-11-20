#!/usr/bin/env python3
"""
AAMVA License Generator - Integration Layer Usage Examples

Demonstrates how to use the new service layer and facade API for:
- Simple license generation
- Batch processing
- Validation workflows
- Export operations
- Full end-to-end workflows
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aamva_license_generator import (
    AAMVALicenseGenerator,
    create_generator,
    configure_logging,
)


def example_1_simple_generation():
    """Example 1: Simple license generation"""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Simple License Generation")
    print("=" * 70)

    # Create generator
    generator = AAMVALicenseGenerator()

    # Generate a single license
    license_data, validation = generator.generate_license(state="CA")

    print(f"✓ Generated California license:")
    print(f"  License #: {license_data[0]['DAQ']}")
    print(f"  Name: {license_data[0]['DAC']} {license_data[0]['DCS']}")
    print(f"  DOB: {license_data[0]['DBB']}")
    print(f"  Validation: {validation}")


def example_2_batch_generation():
    """Example 2: Batch generation with progress"""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Batch Generation with Progress")
    print("=" * 70)

    generator = AAMVALicenseGenerator()

    # Progress callback
    def progress(current, total):
        percent = (current / total) * 100
        print(f"  Progress: {current}/{total} ({percent:.1f}%)", end='\r')

    # Generate 10 licenses
    licenses, validations = generator.generate_multiple(
        count=10,
        state="TX",
        progress_callback=progress
    )

    print(f"\n✓ Generated {len(licenses)} Texas licenses")
    print(f"  All valid: {all(v.is_valid for v in validations)}")


def example_3_all_states():
    """Example 3: Generate one license per state"""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Generate One License Per State")
    print("=" * 70)

    generator = AAMVALicenseGenerator()

    def progress(current, total, state):
        print(f"  Generating {state}... ({current}/{total})")

    licenses, validations = generator.generate_all_states(
        progress_callback=progress
    )

    print(f"\n✓ Generated {len(licenses)} licenses (one per state)")

    # Count by state
    states = {}
    for license_data in licenses:
        state = license_data[0]['DAJ']
        states[state] = states.get(state, 0) + 1

    print(f"  States covered: {len(states)}")


def example_4_validation():
    """Example 4: Validation workflow"""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Validation Workflow")
    print("=" * 70)

    generator = AAMVALicenseGenerator()

    # Generate a license
    license_data, _ = generator.generate_license(state="FL")

    # Validate it
    validation = generator.validate_license(license_data)

    print(f"Validation Result:")
    print(f"  Valid: {validation.is_valid}")
    print(f"  Errors: {len(validation.errors)}")
    print(f"  Warnings: {len(validation.warnings)}")

    if validation.errors:
        print(f"  Error details:")
        for error in validation.errors:
            print(f"    - {error}")

    if validation.warnings:
        print(f"  Warnings:")
        for warning in validation.warnings:
            print(f"    - {warning}")


def example_5_export_formats():
    """Example 5: Export to multiple formats"""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Export to Multiple Formats")
    print("=" * 70)

    generator = create_generator(output_dir="example_output")

    # Generate licenses
    print("Generating 5 licenses...")
    licenses, _ = generator.generate_multiple(count=5, state="NY")

    # Export barcodes
    print("Exporting barcodes...")
    records = []
    for i, license_data in enumerate(licenses):
        img_path, txt_path = generator.export_barcode(license_data, i)
        records.append((img_path, license_data))
        print(f"  License {i}: {img_path}")

    # Export JSON
    print("Exporting JSON...")
    json_path = generator.export_json(licenses, "example_licenses.json")
    print(f"  JSON: {json_path}")

    # Export CSV
    print("Exporting CSV...")
    csv_path = generator.export_csv(licenses, "example_licenses.csv")
    print(f"  CSV: {csv_path}")

    # Export PDF
    print("Exporting PDF...")
    pdf_path = generator.export_pdf(records, "example_licenses.pdf")
    print(f"  PDF: {pdf_path}")

    print(f"\n✓ Exported to 4 formats successfully")


def example_6_batch_workflow():
    """Example 6: Complete batch workflow"""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Complete Batch Workflow")
    print("=" * 70)

    generator = create_generator(output_dir="batch_output", seed=42)

    def progress(current, total, status):
        print(f"  {status}: {current}/{total}")

    # Full batch workflow
    result = generator.generate_batch(
        count=20,
        validate=True,
        export_formats=['json', 'csv', 'pdf'],
        progress_callback=progress
    )

    print(f"\nBatch Summary:")
    print(f"  Total generated: {result['summary']['total']}")
    print(f"  Validated: {result['summary']['validated']}")
    print(f"  Passed validation: {result['summary']['passed_validation']}")
    print(f"  Export formats: {result['summary']['exported_formats']}")
    print(f"  Export paths:")
    for fmt, path in result['export_paths'].items():
        print(f"    {fmt}: {path}")


def example_7_full_workflow():
    """Example 7: Full end-to-end workflow"""
    print("\n" + "=" * 70)
    print("EXAMPLE 7: Full End-to-End Workflow")
    print("=" * 70)

    generator = create_generator(output_dir="full_workflow_output")

    def progress(stage, current, total):
        print(f"  [{stage}] {current}/{total}")

    # Execute full workflow
    result = generator.full_workflow(
        count=10,
        state="CA",
        export_formats=['pdf', 'docx', 'json'],
        validate_before_export=True,
        progress_callback=progress
    )

    print(f"\nWorkflow Summary:")
    print(f"  Requested: {result['summary']['total_requested']}")
    print(f"  Generated: {result['summary']['total_generated']}")
    print(f"  Validated: {result['summary']['total_validated']}")
    print(f"  Passed: {result['summary']['passed_validation']}")
    print(f"  Failed: {result['summary']['failed_validation']}")
    print(f"  Exported: {result['summary']['exported_formats']}")
    print(f"  Errors: {result['summary']['total_errors']}")
    print(f"  Success: {result['summary']['success']}")


def example_8_custom_config():
    """Example 8: Custom configuration"""
    print("\n" + "=" * 70)
    print("EXAMPLE 8: Custom Configuration")
    print("=" * 70)

    # Custom configuration
    config = {
        'output_dir': 'custom_output',
        'seed': 12345,  # For reproducibility
        'locale': 'en_US',
        'strict_validation': True,
        'fail_fast': False,
        'max_failures': 5,
        'max_retries': 2,
    }

    generator = AAMVALicenseGenerator(config)

    # Generate with custom config
    licenses, validations = generator.generate_multiple(count=5)

    print(f"✓ Generated {len(licenses)} licenses with custom config")
    print(f"  Seed: {config['seed']}")
    print(f"  Output dir: {config['output_dir']}")
    print(f"  Strict validation: {config['strict_validation']}")


def example_9_statistics():
    """Example 9: Get statistics"""
    print("\n" + "=" * 70)
    print("EXAMPLE 9: License Statistics")
    print("=" * 70)

    generator = AAMVALicenseGenerator()

    # Generate diverse licenses
    licenses, _ = generator.generate_multiple(count=50)

    # Get statistics
    stats = generator.get_statistics(licenses)

    print(f"Statistics:")
    print(f"  Total licenses: {stats['total_licenses']}")
    print(f"  States represented: {len(stats['states'])}")
    print(f"  Male: {stats['sex_distribution']['male']}")
    print(f"  Female: {stats['sex_distribution']['female']}")
    print(f"  Veterans: {stats['veteran_count']}")
    print(f"  Organ donors: {stats['organ_donor_count']}")
    print(f"  DHS compliant: {stats['dhs_compliant_count']}")

    print(f"\n  Top 5 states:")
    top_states = sorted(stats['states'].items(), key=lambda x: x[1], reverse=True)[:5]
    for state, count in top_states:
        print(f"    {state}: {count}")


def example_10_import_export():
    """Example 10: Import and export"""
    print("\n" + "=" * 70)
    print("EXAMPLE 10: Import and Export")
    print("=" * 70)

    generator = create_generator(output_dir="import_export_output")

    # Generate and export
    print("Generating licenses...")
    licenses, _ = generator.generate_multiple(count=5)

    print("Exporting to JSON...")
    json_path = generator.export_json(licenses, "temp_licenses.json")

    # Import back
    print("Importing from JSON...")
    import_result = generator.import_json(json_path)

    if import_result.success:
        print(f"✓ Successfully imported {import_result.count} licenses")

        # Validate imported data
        results, passed, failed = generator.validate_licenses(import_result.data)
        print(f"  Validation: {passed} passed, {failed} failed")
    else:
        print(f"✗ Import failed: {import_result.errors}")


def main():
    """Run all examples"""
    print("\n" + "=" * 70)
    print("AAMVA LICENSE GENERATOR - INTEGRATION LAYER EXAMPLES")
    print("=" * 70)

    # Configure logging
    configure_logging(level='INFO')

    try:
        # Run examples
        example_1_simple_generation()
        example_2_batch_generation()
        # example_3_all_states()  # Commented out - takes longer
        example_4_validation()
        example_5_export_formats()
        example_6_batch_workflow()
        example_7_full_workflow()
        example_8_custom_config()
        example_9_statistics()
        example_10_import_export()

        print("\n" + "=" * 70)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("=" * 70)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
