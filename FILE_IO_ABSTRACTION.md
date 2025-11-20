# File I/O Abstraction Layer

**Production-Quality File Operations for AAMVA License Generator**

## Overview

This document describes the comprehensive file I/O abstraction layer implemented for the AAMVA License Generator. The implementation provides:

- **Robust Error Handling**: Comprehensive handling of permissions, disk space, encoding, and other file system errors
- **Progress Tracking**: Real-time progress callbacks for long-running operations
- **Streaming Support**: Memory-efficient processing of large datasets
- **Resource Safety**: Automatic cleanup using context managers
- **Multiple Formats**: Support for PDF, DOCX, Images, JSON, and CSV
- **Abstract Design**: Easy to extend with new formats

## Architecture

```
aamva_license_generator/
├── storage.py              # Core file system operations
├── exporters/              # Export functionality
│   ├── __init__.py
│   ├── base.py            # Abstract exporter interface
│   ├── pdf_exporter.py    # PDF generation (Avery layout)
│   ├── docx_exporter.py   # DOCX generation
│   ├── image_exporter.py  # Barcode and card images
│   ├── json_exporter.py   # JSON data export
│   └── csv_exporter.py    # CSV data export
└── importers/              # Import functionality
    ├── __init__.py
    ├── base.py            # Abstract importer interface
    ├── json_importer.py   # Import from JSON
    └── csv_importer.py    # Import from CSV
```

## Features

### 1. Storage Module (`storage.py`)

Provides low-level file system operations with comprehensive error handling:

#### FileSystemValidator
- Path validation and sanitization
- Permission checking (read/write)
- Disk space monitoring
- Space requirement validation

```python
from aamva_license_generator.storage import FileSystemValidator

# Validate path
path = FileSystemValidator.validate_path("/path/to/output")

# Check if writable
if FileSystemValidator.check_writable(path):
    print("Can write to path")

# Get disk space info
space = FileSystemValidator.get_disk_space(path)
print(f"Free space: {space.free_gb:.2f} GB")

# Ensure sufficient space
FileSystemValidator.ensure_space(path, required_bytes=100*1024*1024)
```

#### SafeFileOperations
- Atomic file writes
- Safe reads with error handling
- Checksum verification
- Safe file copying

```python
from aamva_license_generator.storage import SafeFileOperations

# Atomic write (file never corrupted on failure)
with SafeFileOperations.atomic_write('output.txt') as f:
    f.write('Hello, World!')

# Safe read
content = SafeFileOperations.safe_read('input.txt')

# Copy with verification
SafeFileOperations.safe_copy('source.pdf', 'dest.pdf', verify=True)

# Calculate checksum
checksum = SafeFileOperations.calculate_checksum('file.pdf')
```

#### DirectoryManager
- Directory creation with parents
- Safe cleanup operations
- Size calculation

```python
from aamva_license_generator.storage import DirectoryManager

# Create directory tree
DirectoryManager.ensure_directory_tree('/path/to/deep/directory')

# Clean up old files
removed = DirectoryManager.safe_cleanup(
    '/tmp/cache',
    pattern='*.tmp',
    max_age_seconds=3600
)
```

#### TemporaryFileManager
- Temporary directory management
- Temporary file creation
- Automatic cleanup

```python
from aamva_license_generator.storage import TemporaryFileManager

# Temporary directory
with TemporaryFileManager.temporary_directory() as temp_dir:
    # Use temp_dir
    pass  # Automatically cleaned up

# Temporary file
with TemporaryFileManager.temporary_file(suffix='.txt') as (f, path):
    f.write('temp data')
    # File automatically cleaned up
```

### 2. Export System

#### Base Exporters

Three abstract base classes provide different export patterns:

**BaseExporter**: Single-pass export
```python
from aamva_license_generator.exporters import BaseExporter

class MyExporter(BaseExporter):
    def format(self) -> ExportFormat:
        return ExportFormat.PDF

    def file_extension(self) -> str:
        return "pdf"

    def validate_data(self, data):
        # Validate data structure
        pass

    def _export_impl(self, data) -> ExportResult:
        # Implementation
        pass
```

**BatchExporter**: Item-by-item processing with error recovery
```python
from aamva_license_generator.exporters import BatchExporter

class MyBatchExporter(BatchExporter):
    def _export_item(self, item, index) -> Optional[str]:
        # Export single item
        # Return error message or None
        pass
```

**StreamingExporter**: Memory-efficient streaming for large datasets
```python
from aamva_license_generator.exporters import StreamingExporter

class MyStreamingExporter(StreamingExporter):
    def _begin_stream(self):
        # Initialize stream
        pass

    def _write_item(self, item):
        # Write single item
        pass

    def _end_stream(self):
        # Finalize stream
        pass
```

#### PDF Exporter

Generates PDF with Avery 28371 business card layout (10 cards per page):

```python
from aamva_license_generator.exporters import PDFExporter, PDFExportOptions

# Create options
options = PDFExportOptions(
    output_path='licenses.pdf',
    dpi=300,
    progress_callback=lambda p: print(f"{p.percent_complete:.0f}%")
)

# Create exporter
exporter = PDFExporter(options)

# Export data (list of (barcode_path, license_data) tuples)
result = exporter.export(data)

if result.success:
    print(f"Exported {result.items_processed} licenses")
    print(f"Output: {result.output_path}")
    print(f"Size: {result.file_size_bytes / 1024:.1f} KB")
else:
    for error in result.errors:
        print(f"Error: {error}")
```

#### DOCX Exporter

Generates Word documents with Avery layout:

```python
from aamva_license_generator.exporters import DOCXExporter, DOCXExportOptions

options = DOCXExportOptions(
    output_path='licenses.docx',
    dpi=300
)

exporter = DOCXExporter(options)
result = exporter.export(data)
```

#### Image Exporters

Generate barcode images and complete card images:

```python
from aamva_license_generator.exporters import (
    BarcodeExporter,
    CardImageExporter,
    ImageExportOptions,
    ImageFormat
)

# Barcode images
options = ImageExportOptions(
    output_path='barcodes/',
    dpi=300,
    image_format=ImageFormat.PNG
)
exporter = BarcodeExporter(options)
result = exporter.export(license_data_list)

# Complete card images
exporter = CardImageExporter(options, width_inches=3.5)
result = exporter.export(data_with_barcodes)
```

#### JSON Exporter

Export license data in structured JSON format:

```python
from aamva_license_generator.exporters import JSONExporter, JSONExportOptions

options = JSONExportOptions(
    output_path='licenses.json',
    pretty_print=True,
    include_metadata=True
)

exporter = JSONExporter(options)
result = exporter.export(license_data)
```

#### CSV Exporter

Export flattened license data to CSV:

```python
from aamva_license_generator.exporters import CSVExporter, CSVExportOptions

options = CSVExportOptions(
    output_path='licenses.csv'
)

exporter = CSVExporter(options)
result = exporter.export(license_data)
```

### 3. Import System

#### JSON Importer

Import license data from JSON files:

```python
from aamva_license_generator.importers import JSONImporter, JSONImportOptions

options = JSONImportOptions(
    input_path='licenses.json',
    validate_schema=True,
    skip_invalid=False,
    max_errors=10
)

importer = JSONImporter(options)
result = importer.import_data()

if result.success:
    print(f"Imported {result.items_imported} licenses")
    for license_data in result.data:
        # Process license data
        pass
else:
    for error in result.errors:
        print(f"Error: {error}")
```

Supports two formats:
1. **Array format**: `[license1, license2, ...]`
2. **Object format**: `{"metadata": {...}, "licenses": [...]}`

#### JSON Lines Importer

For very large datasets, use JSON Lines format (one JSON object per line):

```python
from aamva_license_generator.importers import JSONLinesImporter, ImportOptions

options = ImportOptions(
    input_path='licenses.jsonl',
    validate_schema=True
)

importer = JSONLinesImporter(options)
result = importer.import_data()
```

#### CSV Importer

Import and reconstruct license data from CSV:

```python
from aamva_license_generator.importers import CSVImporter, CSVImportOptions

options = CSVImportOptions(
    input_path='licenses.csv',
    validate_schema=True,
    auto_detect_format=True  # Auto-detect column format
)

importer = CSVImporter(options)
result = importer.import_data()
```

The CSV importer automatically reconstructs nested license structure from flattened CSV columns (e.g., `DL_DAQ`, `DL_DCS`, `ZC_ZCW`).

## Progress Tracking

All exporters and importers support progress callbacks:

```python
def progress_callback(progress):
    print(f"[{progress.percent_complete:.1f}%] {progress.stage}: {progress.message}")
    print(f"  Items: {progress.current}/{progress.total}")
    print(f"  Elapsed: {progress.elapsed_seconds:.1f}s")
    if progress.estimated_remaining > 0:
        print(f"  Remaining: {progress.estimated_remaining:.1f}s")

options = ExportOptions(
    output_path='output.pdf',
    progress_callback=progress_callback
)
```

## Error Handling

### Error Types

**Storage Errors:**
- `StorageError` - Base storage error
- `PermissionError` - Insufficient permissions
- `DiskSpaceError` - Insufficient disk space
- `PathError` - Invalid path
- `ChecksumError` - Checksum verification failed

**Export Errors:**
- `ExportError` - Base export error
- `ValidationError` - Data validation failed
- `RenderError` - Rendering/generation failed
- `EncodingError` - Encoding failed

**Import Errors:**
- `ImportError` - Base import error
- `ParseError` - File parsing failed
- `SchemaError` - Schema validation failed

### Error Recovery

All operations return a result object with detailed error information:

```python
result = exporter.export(data)

if result.success:
    print(f"Success! {result.items_processed} items")
else:
    print(f"Failed: {result.items_failed} items")

    for error in result.errors:
        print(f"Error: {error}")

    for warning in result.warnings:
        print(f"Warning: {warning}")
```

## Advanced Features

### Streaming Large Datasets

For very large datasets, use streaming to avoid loading everything into memory:

```python
# Streaming JSON export
exporter = JSONExporter(options)
# Data is written item-by-item, never fully in memory

# Streaming import
importer = JSONLinesImporter(options)
# Data is read line-by-line
result = importer.import_data()
```

### Atomic Writes

All file writes are atomic - the target file is never corrupted if the operation fails:

```python
# If this fails, output.txt is never partially written
with SafeFileOperations.atomic_write('output.txt') as f:
    f.write('data')
    # If error occurs here, temp file is cleaned up
    # Original output.txt is untouched
```

### Checksum Verification

Verify file integrity after operations:

```python
# Export with verification
result = exporter.export(data)
checksum = SafeFileOperations.calculate_checksum(result.output_path)

# Copy with verification
SafeFileOperations.safe_copy(
    'source.pdf',
    'dest.pdf',
    verify=True  # Checksums must match
)
```

### Metadata

All exports can include metadata:

```python
options = JSONExportOptions(
    output_path='licenses.json',
    include_metadata=True,
    metadata={
        'generated_by': 'AAMVA Generator',
        'purpose': 'Testing',
        'batch_id': 'BATCH-001'
    }
)
```

## Performance Characteristics

### Memory Usage

| Operation | Memory Usage | Notes |
|-----------|-------------|-------|
| PDF Export | ~50MB + images | Loads images into memory |
| DOCX Export | ~100MB + images | Temporary card images |
| JSON Export (streaming) | ~1MB | Constant memory |
| JSON Import (streaming) | ~1MB per item | Items processed one at a time |
| CSV Export (streaming) | ~1MB | Constant memory |
| Barcode Export | ~10MB per batch | Batch processing |

### Disk Space

Estimated disk space requirements:

- **Barcode (BMP)**: ~100KB per license
- **Card Image (PNG)**: ~200KB per license
- **PDF**: ~10KB per license + images
- **DOCX**: ~50KB per license + images
- **JSON**: ~1KB per license (pretty), ~500B (compact)
- **CSV**: ~500B per license

### Throughput

Approximate processing speeds (typical hardware):

- **PDF Generation**: 50-100 licenses/second
- **DOCX Generation**: 20-50 licenses/second (slower due to image generation)
- **Barcode Encoding**: 100-200 licenses/second
- **JSON Export**: 1000+ licenses/second
- **CSV Export**: 500+ licenses/second

## Best Practices

### 1. Always Use Progress Callbacks for Long Operations

```python
def progress_callback(progress):
    # Update UI, log progress, etc.
    pass

options = ExportOptions(
    output_path='output.pdf',
    progress_callback=progress_callback
)
```

### 2. Check Disk Space Before Large Exports

```python
from aamva_license_generator.storage import FileSystemValidator

# Estimate size
estimated_size = num_licenses * 100 * 1024  # 100KB per license

# Check space
try:
    FileSystemValidator.ensure_space(output_path, estimated_size)
except DiskSpaceError as e:
    print(f"Insufficient space: {e}")
```

### 3. Use Streaming for Large Datasets

```python
# For >10,000 licenses, use streaming exporters
if num_licenses > 10000:
    exporter = JSONExporter(options)  # Streams automatically
else:
    exporter = PDFExporter(options)
```

### 4. Handle Partial Failures Gracefully

```python
result = exporter.export(data)

if result.items_failed > 0:
    # Some items failed but operation continued
    print(f"Partial success: {result.items_processed}/{result.items_total}")

    # Log errors for investigation
    for error in result.errors:
        log_error(error)

    # Decide whether to accept partial results
    if result.items_failed / result.items_total < 0.1:  # <10% failure
        accept_results()
    else:
        retry_operation()
```

### 5. Clean Up Temporary Files

```python
# Temporary files are auto-cleaned
with TemporaryFileManager.temporary_directory() as temp_dir:
    # Generate intermediate files in temp_dir
    process_data(temp_dir)
    # temp_dir automatically deleted on exit
```

## Example: Complete Workflow

```python
from pathlib import Path
from aamva_license_generator.exporters import PDFExporter, PDFExportOptions
from aamva_license_generator.storage import DirectoryManager, FileSystemValidator

def export_licenses_to_pdf(license_data, output_path):
    """Complete workflow with error handling"""

    # 1. Validate and prepare output directory
    output_path = Path(output_path)
    try:
        DirectoryManager.ensure_directory_tree(output_path.parent)
    except Exception as e:
        print(f"Failed to create output directory: {e}")
        return None

    # 2. Check disk space
    estimated_size = len(license_data) * 100 * 1024  # 100KB per license
    try:
        FileSystemValidator.ensure_space(output_path, estimated_size)
    except DiskSpaceError as e:
        print(f"Insufficient disk space: {e}")
        return None

    # 3. Set up progress tracking
    def progress_callback(progress):
        print(f"[{progress.percent_complete:.0f}%] {progress.message}")

    # 4. Create exporter with options
    options = PDFExportOptions(
        output_path=str(output_path),
        dpi=300,
        progress_callback=progress_callback
    )

    # 5. Export
    exporter = PDFExporter(options)
    result = exporter.export(license_data)

    # 6. Handle results
    if result.success:
        print(f"✓ Export successful!")
        print(f"  Output: {result.output_path}")
        print(f"  Licenses: {result.items_processed}")
        print(f"  Size: {result.file_size_bytes / 1024:.1f} KB")
        print(f"  Duration: {result.duration_seconds:.1f}s")
        return result.output_path
    else:
        print(f"✗ Export failed!")
        for error in result.errors:
            print(f"  - {error}")
        return None
```

## Extending the System

### Adding a New Export Format

1. Create a new exporter class inheriting from `BaseExporter`, `BatchExporter`, or `StreamingExporter`
2. Implement required abstract methods
3. Add to `exporters/__init__.py`

```python
from .base import BaseExporter, ExportFormat, ExportResult

class XMLExporter(BaseExporter):
    @property
    def format(self) -> ExportFormat:
        return ExportFormat.XML  # Add to enum

    @property
    def file_extension(self) -> str:
        return "xml"

    def validate_data(self, data):
        # Validation logic
        pass

    def _export_impl(self, data) -> ExportResult:
        # Export logic
        pass
```

### Adding a New Import Format

Similar process for importers:

```python
from .base import StreamingImporter, ImportFormat, ImportResult

class XMLImporter(StreamingImporter):
    @property
    def format(self) -> ImportFormat:
        return ImportFormat.XML

    @property
    def supported_extensions(self) -> List[str]:
        return ["xml"]

    def validate_file(self, filepath):
        # File validation
        pass

    def _open_stream(self):
        # Open XML file
        pass

    def _read_item(self):
        # Read next item
        pass

    def _close_stream(self):
        # Close file
        pass

    def validate_item_schema(self, item):
        # Item validation
        pass
```

## Testing

Run the demo to test all functionality:

```bash
python examples/file_io_demo.py
```

The demo will:
1. Test storage operations
2. Export barcodes as images
3. Export data to JSON
4. Export data to CSV
5. Import data from JSON
6. Import data from CSV
7. Test error handling

## Comparison with Original Implementation

### Improvements Over `generate_licenses.py`

| Feature | Original | New Implementation |
|---------|----------|-------------------|
| Error Handling | Minimal | Comprehensive (10+ error types) |
| Progress Tracking | None | Full progress callbacks |
| Disk Space Check | None | Automatic validation |
| Atomic Writes | No | Yes (never corrupt files) |
| Streaming | No | Yes (for large datasets) |
| Resource Cleanup | Manual | Automatic (context managers) |
| Extensibility | Hardcoded | Abstract interfaces |
| Partial Failure Handling | Fail all | Continue with errors |
| Metadata Support | None | Full metadata support |
| Format Support | PDF, DOCX, Images | + JSON, CSV, streaming |

## License

MIT License - See project LICENSE file for details.

## Author

Developed for the AAMVA License Generator project.
