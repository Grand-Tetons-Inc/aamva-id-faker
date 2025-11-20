# File I/O Abstraction Layer - Quick Start Guide

## Installation Verification

First, verify the installation:

```bash
python verify_file_io.py
```

This will show which exporters are available based on installed dependencies.

## Core Features (No Dependencies)

These features work without any external dependencies:

### 1. Storage Operations

```python
from aamva_license_generator.storage import (
    FileSystemValidator,
    SafeFileOperations,
    DirectoryManager,
)

# Create directories
DirectoryManager.ensure_directory_tree('/path/to/output')

# Check disk space
space = FileSystemValidator.get_disk_space('/path/to/output')
print(f"Free space: {space.free_gb:.2f} GB")

# Atomic file write (never corrupts file on failure)
with SafeFileOperations.atomic_write('output.txt') as f:
    f.write('Hello, World!')

# Safe file read
content = SafeFileOperations.safe_read('output.txt')
```

### 2. JSON Export

```python
from aamva_license_generator.exporters import JSONExporter, JSONExportOptions

# Sample license data
license_data = [
    [  # License 1
        {
            "subfile_type": "DL",
            "DAQ": "D1234567",
            "DCS": "SMITH",
            "DAC": "JOHN",
            # ... more fields
        }
    ]
]

# Export to JSON
options = JSONExportOptions(
    output_path='licenses.json',
    pretty_print=True
)
exporter = JSONExporter(options)
result = exporter.export(license_data)

if result.success:
    print(f"Exported {result.items_processed} licenses")
```

### 3. CSV Export

```python
from aamva_license_generator.exporters import CSVExporter, CSVExportOptions

options = CSVExportOptions(output_path='licenses.csv')
exporter = CSVExporter(options)
result = exporter.export(license_data)
```

### 4. JSON Import

```python
from aamva_license_generator.importers import JSONImporter, JSONImportOptions

options = JSONImportOptions(
    input_path='licenses.json',
    validate_schema=True
)
importer = JSONImporter(options)
result = importer.import_data()

for license_data in result.data:
    # Process each license
    pass
```

### 5. CSV Import

```python
from aamva_license_generator.importers import CSVImporter, CSVImportOptions

options = CSVImportOptions(
    input_path='licenses.csv',
    auto_detect_format=True
)
importer = CSVImporter(options)
result = importer.import_data()
```

## Optional Features (Require Dependencies)

### PDF Export (requires: reportlab)

```bash
pip install reportlab
```

```python
from aamva_license_generator.exporters import PDFExporter, PDFExportOptions

# Need barcode images and license data
data_with_barcodes = [
    (barcode_image_path, license_data),
    # ... more items
]

options = PDFExportOptions(
    output_path='licenses.pdf',
    dpi=300
)
exporter = PDFExporter(options)
result = exporter.export(data_with_barcodes)
```

### DOCX Export (requires: python-docx, pillow)

```bash
pip install python-docx pillow
```

```python
from aamva_license_generator.exporters import DOCXExporter, DOCXExportOptions

options = DOCXExportOptions(
    output_path='licenses.docx',
    dpi=300
)
exporter = DOCXExporter(options)
result = exporter.export(data_with_barcodes)
```

### Barcode Generation (requires: pdf417gen, pillow)

```bash
pip install pdf417gen pillow
```

```python
from aamva_license_generator.exporters import BarcodeExporter, ImageExportOptions

options = ImageExportOptions(
    output_path='barcodes/',
    dpi=300
)
exporter = BarcodeExporter(options)
result = exporter.export(license_data_list)
```

## Progress Tracking

All operations support progress callbacks:

```python
def progress_callback(progress):
    percent = progress.percent_complete
    stage = progress.stage
    message = progress.message
    print(f"[{percent:.1f}%] {stage}: {message}")

options = JSONExportOptions(
    output_path='licenses.json',
    progress_callback=progress_callback
)
```

## Error Handling

All operations return detailed result objects:

```python
result = exporter.export(data)

if result.success:
    print(f"Success! Processed {result.items_processed} items")
    print(f"Output: {result.output_path}")
    print(f"Size: {result.file_size_bytes / 1024:.1f} KB")
    print(f"Duration: {result.duration_seconds:.2f}s")
else:
    print("Export failed!")
    for error in result.errors:
        print(f"  Error: {error}")

# Warnings don't fail the operation
if result.warnings:
    for warning in result.warnings:
        print(f"  Warning: {warning}")
```

## Common Workflows

### 1. Generate and Export

```python
# Generate some license data
from aamva_license_generator import LicenseGenerator

generator = LicenseGenerator()
licenses = [generator.generate() for _ in range(10)]

# Convert to export format
license_data = [[license.to_dict()] for license in licenses]

# Export to JSON
from aamva_license_generator.exporters import JSONExporter, JSONExportOptions

options = JSONExportOptions(output_path='output/licenses.json')
exporter = JSONExporter(options)
result = exporter.export(license_data)
```

### 2. Import and Process

```python
from aamva_license_generator.importers import JSONImporter, JSONImportOptions

# Import licenses
options = JSONImportOptions(input_path='licenses.json')
importer = JSONImporter(options)
result = importer.import_data()

# Process each license
for license_data in result.data:
    dl_subfile = license_data[0]  # First subfile is always DL
    print(f"License: {dl_subfile['DAQ']}")
    print(f"Name: {dl_subfile['DAC']} {dl_subfile['DCS']}")
    print(f"State: {dl_subfile['DAJ']}")
```

### 3. Convert Formats

```python
from aamva_license_generator.importers import JSONImporter, JSONImportOptions
from aamva_license_generator.exporters import CSVExporter, CSVExportOptions

# Import from JSON
import_opts = JSONImportOptions(input_path='input.json')
importer = JSONImporter(import_opts)
import_result = importer.import_data()

# Export to CSV
export_opts = CSVExportOptions(output_path='output.csv')
exporter = CSVExporter(export_opts)
export_result = exporter.export(import_result.data)

print(f"Converted {import_result.items_imported} licenses")
```

## Best Practices

### 1. Always Check Disk Space

```python
from aamva_license_generator.storage import FileSystemValidator, DiskSpaceError

try:
    estimated_size = num_items * 100 * 1024  # 100KB per item
    FileSystemValidator.ensure_space(output_path, estimated_size)
except DiskSpaceError as e:
    print(f"Insufficient space: {e}")
    # Handle error...
```

### 2. Use Progress Callbacks

```python
def progress(p):
    print(f"\r[{p.percent_complete:.0f}%] {p.message}", end='', flush=True)

options = ExportOptions(
    output_path='output.json',
    progress_callback=progress
)
```

### 3. Handle Partial Failures

```python
result = exporter.export(data)

if result.items_failed > 0:
    failure_rate = result.items_failed / result.items_total
    if failure_rate < 0.1:  # Less than 10% failed
        print(f"Accepting partial results: {result.items_processed} succeeded")
    else:
        print(f"Too many failures ({failure_rate*100:.1f}%), rejecting batch")
```

### 4. Use Appropriate Exporters for Data Size

```python
# Small datasets (<1000 items): Any exporter
# Medium datasets (1000-10000): Use streaming exporters
# Large datasets (>10000): Definitely use streaming

if num_items < 1000:
    exporter = PDFExporter(options)
elif num_items < 10000:
    exporter = JSONExporter(options)  # Streams automatically
else:
    exporter = CompactJSONExporter(options)  # JSON Lines format
```

## Troubleshooting

### Import Errors

If you get import errors for optional exporters:

```python
# Check which exporters are available
from aamva_license_generator.exporters import (
    _PDF_AVAILABLE,
    _DOCX_AVAILABLE,
    _IMAGE_AVAILABLE,
)

print(f"PDF Export: {'✓' if _PDF_AVAILABLE else '✗'}")
print(f"DOCX Export: {'✓' if _DOCX_AVAILABLE else '✗'}")
print(f"Image Export: {'✓' if _IMAGE_AVAILABLE else '✗'}")
```

### Validation Errors

If exports fail validation:

```python
# Enable detailed error reporting
result = exporter.export(data)

if not result.success:
    print("Validation errors:")
    for error in result.errors:
        print(f"  - {error}")

    # Try with validation disabled
    options = ExportOptions(
        output_path='output.json',
        validate_schema=False  # Skip validation
    )
```

### Performance Issues

If exports are slow:

```python
# Disable progress callbacks for faster execution
options = ExportOptions(
    output_path='output.json',
    progress_callback=None  # No callbacks
)

# For very large datasets, use streaming
from aamva_license_generator.exporters import CompactJSONExporter

# JSON Lines format is fastest for large datasets
exporter = CompactJSONExporter(options)
```

## Full Example

Complete example from generation to export:

```python
from pathlib import Path
from aamva_license_generator import LicenseGenerator
from aamva_license_generator.exporters import JSONExporter, JSONExportOptions
from aamva_license_generator.storage import DirectoryManager, FileSystemValidator

# 1. Setup
output_dir = Path('output')
DirectoryManager.ensure_directory_tree(output_dir)

# 2. Generate licenses
generator = LicenseGenerator()
licenses = [generator.generate() for _ in range(100)]

# 3. Convert to export format
license_data = [[license.to_dict()] for license in licenses]

# 4. Check space
estimated_size = len(license_data) * 1024  # 1KB per license
try:
    FileSystemValidator.ensure_space(output_dir, estimated_size)
except Exception as e:
    print(f"Error: {e}")
    exit(1)

# 5. Export with progress tracking
def progress(p):
    if p.current % 10 == 0:  # Update every 10 items
        print(f"[{p.percent_complete:.0f}%] {p.message}")

options = JSONExportOptions(
    output_path=str(output_dir / 'licenses.json'),
    pretty_print=True,
    include_metadata=True,
    progress_callback=progress
)

exporter = JSONExporter(options)
result = exporter.export(license_data)

# 6. Handle results
if result.success:
    print(f"\n✓ Success!")
    print(f"  Exported: {result.items_processed} licenses")
    print(f"  Output: {result.output_path}")
    print(f"  Size: {result.file_size_bytes / 1024:.1f} KB")
    print(f"  Time: {result.duration_seconds:.2f}s")
else:
    print(f"\n✗ Failed!")
    for error in result.errors:
        print(f"  - {error}")
```

## Further Reading

- **Complete API Documentation**: `FILE_IO_ABSTRACTION.md`
- **Implementation Details**: `FILE_IO_IMPLEMENTATION_SUMMARY.md`
- **Full Demo**: `examples/file_io_demo.py`
- **Error Handling Specification**: `ERROR_HANDLING_SPECIFICATION.md`

## Getting Help

If you encounter issues:

1. Run the verification script: `python verify_file_io.py`
2. Check which dependencies are installed
3. Review the error messages in the result object
4. See the full demo for working examples
5. Read the comprehensive documentation

The File I/O abstraction layer is designed to be robust and self-documenting. Most errors include actionable guidance for resolution.
