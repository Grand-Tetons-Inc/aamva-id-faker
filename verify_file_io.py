#!/usr/bin/env python3
"""
Verification script for File I/O Abstraction Layer

Quick test to verify all imports work correctly and basic functionality is operational.
"""

import sys
from pathlib import Path

print("=" * 60)
print("File I/O Abstraction Layer - Verification")
print("=" * 60)

print("\nNOTE: Some exporters require optional dependencies:")
print("  - PDFExporter requires: reportlab")
print("  - DOCXExporter requires: python-docx")
print("  - BarcodeExporter requires: pdf417gen, pillow")
print("  - CardImageExporter requires: pillow")
print("\nCore functionality (JSON, CSV, Storage) has no external dependencies.")
print()

# Test 1: Import storage module
print("\n1. Testing storage module imports...")
try:
    from aamva_license_generator.storage import (
        FileSystemValidator,
        SafeFileOperations,
        DirectoryManager,
        TemporaryFileManager,
        DiskSpaceInfo,
        StorageError,
        DiskSpaceError,
        PathError,
    )
    print("   ✓ Storage module imports successful")
except ImportError as e:
    print(f"   ✗ Storage import failed: {e}")
    sys.exit(1)

# Test 2: Import exporters
print("\n2. Testing exporters imports...")
print("   Testing base classes...")
try:
    from aamva_license_generator.exporters.base import (
        BaseExporter,
        BatchExporter,
        StreamingExporter,
        ExportOptions,
        ExportResult,
        ExportProgress,
        ExportFormat,
    )
    print("   ✓ Base exporter classes imported")
except ImportError as e:
    print(f"   ✗ Base exporter import failed: {e}")
    sys.exit(1)

print("   Testing JSON/CSV exporters (no dependencies)...")
try:
    from aamva_license_generator.exporters.json_exporter import JSONExporter, CompactJSONExporter
    from aamva_license_generator.exporters.csv_exporter import CSVExporter
    print("   ✓ JSON/CSV exporters imported")
except ImportError as e:
    print(f"   ✗ JSON/CSV exporter import failed: {e}")
    sys.exit(1)

print("   Testing PDF/DOCX/Image exporters (optional dependencies)...")
pdf_available = False
docx_available = False
image_available = False

try:
    from aamva_license_generator.exporters.pdf_exporter import PDFExporter
    pdf_available = True
    print("   ✓ PDFExporter imported")
except ImportError as e:
    print(f"   ⚠ PDFExporter unavailable: {e}")

try:
    from aamva_license_generator.exporters.docx_exporter import DOCXExporter
    docx_available = True
    print("   ✓ DOCXExporter imported")
except ImportError as e:
    print(f"   ⚠ DOCXExporter unavailable: {e}")

try:
    from aamva_license_generator.exporters.image_exporter import BarcodeExporter, CardImageExporter
    image_available = True
    print("   ✓ Image exporters imported")
except ImportError as e:
    print(f"   ⚠ Image exporters unavailable: {e}")

# Test 3: Import importers
print("\n3. Testing importers imports...")
try:
    from aamva_license_generator.importers import (
        BaseImporter,
        StreamingImporter,
        JSONImporter,
        JSONLinesImporter,
        CSVImporter,
        ImportOptions,
        ImportResult,
        ImportProgress,
        ImportFormat,
    )
    print("   ✓ Importers module imports successful")
except ImportError as e:
    print(f"   ✗ Importers import failed: {e}")
    sys.exit(1)

# Test 4: Test basic storage operations
print("\n4. Testing basic storage operations...")
try:
    test_dir = Path("test_verification_output")
    DirectoryManager.ensure_directory_tree(test_dir)
    print(f"   ✓ Created directory: {test_dir}")

    # Test disk space
    space_info = FileSystemValidator.get_disk_space(test_dir)
    print(f"   ✓ Disk space check: {space_info.free_gb:.2f} GB free")

    # Test atomic write
    test_file = test_dir / "test.txt"
    with SafeFileOperations.atomic_write(test_file) as f:
        f.write("Test content")
    print(f"   ✓ Atomic write successful")

    # Test read
    content = SafeFileOperations.safe_read(test_file)
    assert content == "Test content"
    print(f"   ✓ Safe read successful")

    # Cleanup
    import shutil
    shutil.rmtree(test_dir)
    print(f"   ✓ Cleanup successful")

except Exception as e:
    print(f"   ✗ Storage operations failed: {e}")
    sys.exit(1)

# Test 5: Test exporter instantiation
print("\n5. Testing exporter instantiation...")
try:
    from aamva_license_generator.exporters.json_exporter import JSONExportOptions
    from aamva_license_generator.exporters.csv_exporter import CSVExportOptions

    json_opts = JSONExportOptions(output_path="test.json")
    json_exporter = JSONExporter(json_opts)
    print(f"   ✓ JSONExporter created: {json_exporter.format}")

    csv_opts = CSVExportOptions(output_path="test.csv")
    csv_exporter = CSVExporter(csv_opts)
    print(f"   ✓ CSVExporter created: {csv_exporter.format}")

    if pdf_available:
        from aamva_license_generator.exporters.pdf_exporter import PDFExportOptions
        pdf_opts = PDFExportOptions(output_path="test.pdf")
        pdf_exporter = PDFExporter(pdf_opts)
        print(f"   ✓ PDFExporter created: {pdf_exporter.format}")

except Exception as e:
    print(f"   ✗ Exporter instantiation failed: {e}")
    sys.exit(1)

# Test 6: Test importer instantiation
print("\n6. Testing importer instantiation...")
try:
    from aamva_license_generator.importers import (
        JSONImportOptions,
        CSVImportOptions,
    )

    # Note: These will fail if files don't exist, but we're just testing instantiation
    json_import_opts = JSONImportOptions(input_path="test.json")
    json_importer = JSONImporter(json_import_opts)
    print(f"   ✓ JSONImporter created: {json_importer.format}")

    csv_import_opts = CSVImportOptions(input_path="test.csv")
    csv_importer = CSVImporter(csv_import_opts)
    print(f"   ✓ CSVImporter created: {csv_importer.format}")

except Exception as e:
    print(f"   ✗ Importer instantiation failed: {e}")
    sys.exit(1)

# Test 7: Verify main package exports
print("\n7. Testing main package exports...")
try:
    from aamva_license_generator import (
        FileStorageError,
        DiskSpaceError,
        FileSystemValidator as FSV,
        JSONExporter as JSONE,
        JSONImporter as JSONI,
        CSVExporter as CSVE,
    )
    print("   ✓ Core main package exports successful")

    # Try optional exports
    if pdf_available:
        from aamva_license_generator import PDFExporter as PDFE
        print("   ✓ PDFExporter available from main package")
    if docx_available:
        from aamva_license_generator import DOCXExporter as DOCXE
        print("   ✓ DOCXExporter available from main package")

except ImportError as e:
    print(f"   ✗ Main package exports failed: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ ALL VERIFICATION TESTS PASSED!")
print("=" * 60)
print("\nThe File I/O Abstraction Layer is correctly installed and operational.")
print("\nNext steps:")
print("  - Run the demo: python examples/file_io_demo.py")
print("  - Read the docs: FILE_IO_ABSTRACTION.md")
print("  - Check the summary: FILE_IO_IMPLEMENTATION_SUMMARY.md")
print()
