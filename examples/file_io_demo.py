#!/usr/bin/env python3
"""
File I/O Abstraction Layer - Comprehensive Demo

This demonstrates the robust file I/O operations with:
- Storage operations with error handling
- Export to multiple formats (PDF, DOCX, Images, JSON, CSV)
- Import from JSON and CSV
- Progress tracking
- Error recovery
- Streaming for large datasets
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from aamva_license_generator.exporters import (
    PDFExporter, PDFExportOptions,
    DOCXExporter, DOCXExportOptions,
    BarcodeExporter, CardImageExporter, ImageExportOptions,
    JSONExporter, JSONExportOptions,
    CSVExporter, CSVExportOptions,
    ExportProgress,
)

from aamva_license_generator.importers import (
    JSONImporter, JSONImportOptions,
    CSVImporter, CSVImportOptions,
    ImportProgress,
)

from aamva_license_generator.storage import (
    FileSystemValidator,
    DirectoryManager,
    SafeFileOperations,
    DiskSpaceInfo,
)


# Sample license data for demonstrations
SAMPLE_LICENSE_DATA = [
    # License 1
    [
        {
            "subfile_type": "DL",
            "DAQ": "D1234567",
            "DCS": "SMITH",
            "DAC": "JOHN",
            "DAD": "MICHAEL",
            "DBB": "01011990",
            "DBA": "01012030",
            "DBC": "1",
            "DAY": "BRO",
            "DAU": "72",
            "DAW": "180",
            "DAZ": "BRO",
            "DCA": "D",
            "DAI": "SAN FRANCISCO",
            "DAJ": "CA",
            "DAK": "941010000",
            "DAG": "123 MAIN ST",
            "DCL": "W",
            "DDK": "1",
            "DDL": "0",
        },
        {
            "subfile_type": "ZC",
            "ZCW": "SAN FRANCISCO",
            "ZCT": "TEST DATA",
        }
    ],
    # License 2
    [
        {
            "subfile_type": "DL",
            "DAQ": "N9876543",
            "DCS": "JOHNSON",
            "DAC": "JANE",
            "DAD": "MARIE",
            "DBB": "06151985",
            "DBA": "06152035",
            "DBC": "2",
            "DAY": "BLU",
            "DAU": "65",
            "DAW": "140",
            "DAZ": "BLN",
            "DCA": "D",
            "DAI": "NEW YORK",
            "DAJ": "NY",
            "DAK": "100010000",
            "DAG": "456 PARK AVE",
            "DCL": "W",
            "DDK": "0",
            "DDL": "1",
        },
        {
            "subfile_type": "ZN",
            "ZNW": "NEW YORK",
            "ZNT": "SAMPLE",
        }
    ],
]


def progress_callback(progress: ExportProgress):
    """Example progress callback"""
    print(f"  [{progress.percent_complete:.1f}%] {progress.stage}: {progress.message}")


def import_progress_callback(progress: ImportProgress):
    """Example import progress callback"""
    print(f"  [{progress.percent_complete:.1f}%] {progress.stage}: {progress.message}")


def demo_storage_operations():
    """Demonstrate storage operations"""
    print("\n" + "=" * 60)
    print("DEMO 1: Storage Operations")
    print("=" * 60)

    output_dir = Path("demo_output")

    # 1. Directory management
    print("\n1. Creating directory structure...")
    try:
        DirectoryManager.ensure_directory_tree(output_dir / "exports" / "pdf")
        DirectoryManager.ensure_directory_tree(output_dir / "exports" / "json")
        print("   ✓ Directories created successfully")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    # 2. Check disk space
    print("\n2. Checking disk space...")
    try:
        space_info = FileSystemValidator.get_disk_space(output_dir)
        print(f"   Total: {space_info.total / (1024**3):.2f} GB")
        print(f"   Free: {space_info.free_gb:.2f} GB ({100 - space_info.percent_used:.1f}%)")
        print(f"   Used: {space_info.percent_used:.1f}%")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    # 3. Validate paths
    print("\n3. Validating paths...")
    try:
        valid_path = FileSystemValidator.validate_path(output_dir)
        print(f"   ✓ Path is valid: {valid_path}")

        if FileSystemValidator.check_writable(output_dir):
            print("   ✓ Path is writable")
        else:
            print("   ✗ Path is not writable")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    # 4. Atomic file write
    print("\n4. Testing atomic file write...")
    try:
        test_file = output_dir / "test.txt"
        with SafeFileOperations.atomic_write(test_file) as f:
            f.write("Hello, World!\n")
            f.write("This is an atomic write operation.\n")
        print(f"   ✓ File written atomically: {test_file}")

        # Read it back
        content = SafeFileOperations.safe_read(test_file)
        print(f"   ✓ Content verified: {len(content)} bytes")
    except Exception as e:
        print(f"   ✗ Error: {e}")


def demo_barcode_export():
    """Demonstrate barcode image export"""
    print("\n" + "=" * 60)
    print("DEMO 2: Barcode Image Export")
    print("=" * 60)

    output_dir = Path("demo_output/barcodes")

    try:
        # Create exporter
        options = ImageExportOptions(
            output_path=str(output_dir),
            dpi=300,
            progress_callback=progress_callback
        )

        exporter = BarcodeExporter(options)

        # Export barcodes
        print("\nExporting barcode images...")
        result = exporter.export(SAMPLE_LICENSE_DATA)

        # Show results
        if result.success:
            print(f"\n✓ Export successful!")
            print(f"  Items processed: {result.items_processed}")
            print(f"  Duration: {result.duration_seconds:.2f}s")
        else:
            print(f"\n✗ Export failed!")
            for error in result.errors:
                print(f"  - {error}")

    except Exception as e:
        print(f"\n✗ Error: {e}")


def demo_json_export():
    """Demonstrate JSON export"""
    print("\n" + "=" * 60)
    print("DEMO 3: JSON Export")
    print("=" * 60)

    output_file = Path("demo_output/exports/licenses.json")

    try:
        # Create exporter with options
        options = JSONExportOptions(
            output_path=str(output_file),
            pretty_print=True,
            include_metadata=True,
            progress_callback=progress_callback
        )

        exporter = JSONExporter(options)

        # Export data
        print("\nExporting to JSON...")
        result = exporter.export(SAMPLE_LICENSE_DATA)

        # Show results
        if result.success:
            print(f"\n✓ Export successful!")
            print(f"  Output: {result.output_path}")
            print(f"  Size: {result.file_size_bytes / 1024:.2f} KB")
            print(f"  Items: {result.items_processed}")
            print(f"  Duration: {result.duration_seconds:.2f}s")

            # Show file content preview
            content = SafeFileOperations.safe_read(output_file)
            print(f"\n  Preview (first 200 chars):")
            print(f"  {content[:200]}...")
        else:
            print(f"\n✗ Export failed!")
            for error in result.errors:
                print(f"  - {error}")

    except Exception as e:
        print(f"\n✗ Error: {e}")


def demo_csv_export():
    """Demonstrate CSV export"""
    print("\n" + "=" * 60)
    print("DEMO 4: CSV Export")
    print("=" * 60)

    output_file = Path("demo_output/exports/licenses.csv")

    try:
        # Create exporter
        options = CSVExportOptions(
            output_path=str(output_file),
            progress_callback=progress_callback
        )

        exporter = CSVExporter(options)

        # Export data
        print("\nExporting to CSV...")
        result = exporter.export(SAMPLE_LICENSE_DATA)

        # Show results
        if result.success:
            print(f"\n✓ Export successful!")
            print(f"  Output: {result.output_path}")
            print(f"  Size: {result.file_size_bytes / 1024:.2f} KB")
            print(f"  Items: {result.items_processed}")
            print(f"  Duration: {result.duration_seconds:.2f}s")

            # Show file content preview
            content = SafeFileOperations.safe_read(output_file)
            lines = content.split('\n')[:3]
            print(f"\n  Preview (first 3 lines):")
            for line in lines:
                print(f"  {line}")
        else:
            print(f"\n✗ Export failed!")
            for error in result.errors:
                print(f"  - {error}")

    except Exception as e:
        print(f"\n✗ Error: {e}")


def demo_json_import():
    """Demonstrate JSON import"""
    print("\n" + "=" * 60)
    print("DEMO 5: JSON Import")
    print("=" * 60)

    # First export data, then import it back
    output_file = Path("demo_output/exports/licenses.json")

    if not output_file.exists():
        print("  First exporting data to import...")
        demo_json_export()

    try:
        # Create importer
        options = JSONImportOptions(
            input_path=str(output_file),
            validate_schema=True,
            progress_callback=import_progress_callback
        )

        importer = JSONImporter(options)

        # Import data
        print("\nImporting from JSON...")
        result = importer.import_data()

        # Show results
        if result.success:
            print(f"\n✓ Import successful!")
            print(f"  Items imported: {result.items_imported}")
            print(f"  Items skipped: {result.items_skipped}")
            print(f"  Duration: {result.duration_seconds:.2f}s")

            if result.warnings:
                print(f"\n  Warnings:")
                for warning in result.warnings:
                    print(f"    - {warning}")

            # Show first item
            if result.data:
                print(f"\n  First item preview:")
                first_item = result.data[0]
                print(f"    DL Number: {first_item[0].get('DAQ')}")
                print(f"    Name: {first_item[0].get('DAC')} {first_item[0].get('DCS')}")
                print(f"    State: {first_item[0].get('DAJ')}")
        else:
            print(f"\n✗ Import failed!")
            for error in result.errors:
                print(f"  - {error}")

    except Exception as e:
        print(f"\n✗ Error: {e}")


def demo_csv_import():
    """Demonstrate CSV import"""
    print("\n" + "=" * 60)
    print("DEMO 6: CSV Import")
    print("=" * 60)

    # First export data, then import it back
    output_file = Path("demo_output/exports/licenses.csv")

    if not output_file.exists():
        print("  First exporting data to import...")
        demo_csv_export()

    try:
        # Create importer
        options = CSVImportOptions(
            input_path=str(output_file),
            validate_schema=True,
            auto_detect_format=True,
            progress_callback=import_progress_callback
        )

        importer = CSVImporter(options)

        # Import data
        print("\nImporting from CSV...")
        result = importer.import_data()

        # Show results
        if result.success:
            print(f"\n✓ Import successful!")
            print(f"  Items imported: {result.items_imported}")
            print(f"  Items skipped: {result.items_skipped}")
            print(f"  Duration: {result.duration_seconds:.2f}s")

            if result.warnings:
                print(f"\n  Warnings:")
                for warning in result.warnings:
                    print(f"    - {warning}")

            # Show first item
            if result.data:
                print(f"\n  First item preview:")
                first_item = result.data[0]
                if first_item:
                    dl_data = first_item[0]
                    print(f"    DL Number: {dl_data.get('DAQ', 'N/A')}")
                    print(f"    Name: {dl_data.get('DAC', 'N/A')} {dl_data.get('DCS', 'N/A')}")
                    print(f"    State: {dl_data.get('DAJ', 'N/A')}")
        else:
            print(f"\n✗ Import failed!")
            for error in result.errors:
                print(f"  - {error}")

    except Exception as e:
        print(f"\n✗ Error: {e}")


def demo_error_handling():
    """Demonstrate error handling"""
    print("\n" + "=" * 60)
    print("DEMO 7: Error Handling")
    print("=" * 60)

    # Test various error conditions

    # 1. Invalid path
    print("\n1. Testing invalid path handling...")
    try:
        options = JSONExportOptions(
            output_path="/invalid/path/that/does/not/exist/output.json"
        )
        exporter = JSONExporter(options)
        result = exporter.export(SAMPLE_LICENSE_DATA)

        if not result.success:
            print("   ✓ Error caught gracefully:")
            print(f"     {result.errors[0]}")
        else:
            print("   ✗ Should have failed!")
    except Exception as e:
        print(f"   ✓ Exception caught: {type(e).__name__}")

    # 2. Invalid data
    print("\n2. Testing invalid data handling...")
    try:
        options = JSONExportOptions(output_path="demo_output/test.json")
        exporter = JSONExporter(options)

        # Try to export invalid data
        result = exporter.export("not a list")

        if not result.success:
            print("   ✓ Validation error caught:")
            print(f"     {result.errors[0]}")
        else:
            print("   ✗ Should have failed validation!")
    except Exception as e:
        print(f"   ✓ Exception caught: {type(e).__name__}")

    # 3. Disk space check
    print("\n3. Testing disk space validation...")
    try:
        # Try to ensure ridiculous amount of space
        FileSystemValidator.ensure_space("demo_output", 999999999999999)
        print("   ✗ Should have raised DiskSpaceError!")
    except Exception as e:
        print(f"   ✓ Error caught: {type(e).__name__}: {e}")


def main():
    """Run all demos"""
    print("\n" + "=" * 60)
    print("FILE I/O ABSTRACTION LAYER - COMPREHENSIVE DEMO")
    print("=" * 60)

    try:
        demo_storage_operations()
        demo_barcode_export()
        demo_json_export()
        demo_csv_export()
        demo_json_import()
        demo_csv_import()
        demo_error_handling()

        print("\n" + "=" * 60)
        print("ALL DEMOS COMPLETED!")
        print("=" * 60)
        print(f"\nCheck the 'demo_output' directory for generated files.")

    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
