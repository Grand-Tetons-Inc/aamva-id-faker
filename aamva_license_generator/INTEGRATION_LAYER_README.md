# AAMVA License Generator - Integration Layer

## Overview

The integration layer provides a comprehensive service and facade architecture that orchestrates all components of the AAMVA License Generator into cohesive workflows. It offers a clean, simple API for GUI and CLI applications while hiding the complexity of component interactions.

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      FACADE LAYER                             │
│                 (AAMVALicenseGenerator)                       │
│  • Simple, unified API                                        │
│  • Hides service complexity                                   │
│  • Progress reporting                                         │
│  • Error handling                                             │
└─────────────────────┬────────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┬──────────────┐
        │             │             │              │
        ▼             ▼             ▼              ▼
┌──────────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐
│  WORKFLOWS   │ │ SERVICES │ │ SERVICES │ │   SERVICES   │
│              │ │          │ │          │ │              │
│ • Generate   │ │ License  │ │ Validate │ │   Export     │
│ • Validate   │ │ Service  │ │ Service  │ │   Service    │
│ • Export     │ ├──────────┤ ├──────────┤ ├──────────────┤
│ • Batch      │ │  Import  │ │  Batch   │ │              │
│              │ │  Service │ │  Service │ │              │
└──────────────┘ └──────────┘ └──────────┘ └──────────────┘
        │             │             │              │
        └─────────────┴─────────────┴──────────────┘
                      │
        ┌─────────────┼─────────────┬──────────────┐
        │             │             │              │
        ▼             ▼             ▼              ▼
┌──────────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐
│  GENERATORS  │ │ BARCODE  │ │ EXPORT   │ │   VALIDATION │
│              │ │  ENCODER │ │ MODULES  │ │    MODULES   │
└──────────────┘ └──────────┘ └──────────┘ └──────────────┘
```

## Components

### 1. Facade Layer (`facade.py`)

**AAMVALicenseGenerator** - Main entry point providing simple API:
- Single license generation
- Batch processing
- Validation workflows
- Export operations
- Import operations
- Statistics and utilities

### 2. Service Layer (`services/`)

#### LicenseService (`license_service.py`)
- License data generation
- State-specific formatting
- IIN jurisdiction mapping
- Gender-appropriate name generation
- Date formatting and validation

#### ValidationService (`validation_service.py`)
- AAMVA field validation
- Date consistency checking
- Enumerated value validation
- Cross-field validation
- Barcode structure validation
- Batch validation

#### ExportService (`export_service.py`)
- Barcode generation (BMP/PNG)
- AAMVA text formatting
- PDF export (Avery templates)
- DOCX export (table layouts)
- JSON/CSV export
- Card image generation

#### ImportService (`import_service.py`)
- JSON import
- CSV import
- AAMVA text parsing
- Configuration loading
- IIN mapping import
- Auto-format detection

#### BatchService (`batch_service.py`)
- Batch processing orchestration
- Progress tracking
- Error recovery
- Partial success handling
- Transaction-like operations
- Rollback capabilities
- Chunk processing

### 3. Workflow Layer (`workflows.py`)

Defines common workflow patterns:
- **GenerateWorkflow**: Generation → Validation
- **ValidateWorkflow**: Validation → Reporting
- **ExportWorkflow**: Export → Verification
- **BatchWorkflow**: Generation → Validation → Export
- **ImportWorkflow**: Import → Validation → Processing

## Key Features

### 1. Clean API Surface

```python
from aamva_license_generator import AAMVALicenseGenerator

# Create generator
generator = AAMVALicenseGenerator()

# Generate single license
license, validation = generator.generate_license(state="CA")

# Generate batch
result = generator.generate_batch(count=10, export_formats=['pdf', 'json'])
```

### 2. Progress Reporting

All operations support optional progress callbacks:

```python
def progress(current, total, status):
    print(f"{status}: {current}/{total}")

generator.generate_batch(
    count=100,
    progress_callback=progress
)
```

### 3. Comprehensive Error Handling

```python
try:
    result = generator.full_workflow(count=50)
except LicenseGenerationError as e:
    print(f"Generation failed: {e}")
except ExportError as e:
    print(f"Export failed: {e}")
```

### 4. Thread Safety

All services use locks for thread-safe operations:

```python
from threading import Thread

def generate_batch(state):
    generator = AAMVALicenseGenerator()
    return generator.generate_multiple(10, state=state)

# Safe parallel execution
threads = [
    Thread(target=generate_batch, args=("CA",)),
    Thread(target=generate_batch, args=("TX",)),
]
for t in threads:
    t.start()
```

### 5. Transaction-Like Operations

```python
# All-or-nothing batch processing
config = {'rollback_on_failure': True}
generator = AAMVALicenseGenerator(config)

result = generator.generate_batch(count=100)
# If any fail, all are rolled back
```

### 6. Partial Success Handling

```python
# Continue on errors, track failures
config = {'fail_fast': False, 'max_failures': 10}
generator = AAMVALicenseGenerator(config)

result = generator.generate_batch(count=100)
print(f"Succeeded: {result['summary']['total_generated']}")
print(f"Failed: {len(result.get('errors', []))}")
```

## Usage Examples

### Example 1: Simple Generation

```python
from aamva_license_generator import AAMVALicenseGenerator

generator = AAMVALicenseGenerator()

# Generate California license
license_data, validation = generator.generate_license(state="CA")

if validation.is_valid:
    print(f"License #: {license_data[0]['DAQ']}")
    print(f"Name: {license_data[0]['DAC']} {license_data[0]['DCS']}")
```

### Example 2: Batch with Export

```python
generator = AAMVALicenseGenerator({'output_dir': 'my_licenses'})

result = generator.generate_batch(
    count=50,
    state="TX",
    validate=True,
    export_formats=['pdf', 'docx', 'json'],
    progress_callback=lambda c, t, s: print(f"{s}: {c}/{t}")
)

print(f"Generated: {result['summary']['total']}")
print(f"PDF: {result['export_paths']['pdf']}")
```

### Example 3: Full Workflow

```python
def progress(stage, current, total):
    print(f"[{stage}] {current}/{total}")

result = generator.full_workflow(
    count=100,
    export_formats=['pdf', 'json'],
    validate_before_export=True,
    progress_callback=progress
)

if result['summary']['success']:
    print(f"✓ Workflow completed successfully")
    print(f"  Generated: {result['summary']['total_generated']}")
    print(f"  Validated: {result['summary']['passed_validation']}")
    print(f"  Exported: {result['summary']['exported_formats']}")
```

### Example 4: Import and Validate

```python
# Import existing licenses
import_result = generator.import_json("licenses.json")

if import_result.success:
    # Validate imported data
    results, passed, failed = generator.validate_licenses(import_result.data)
    print(f"Validated: {passed} passed, {failed} failed")
```

### Example 5: Custom Configuration

```python
config = {
    'output_dir': 'output',
    'seed': 42,  # Reproducible generation
    'locale': 'en_US',
    'strict_validation': True,
    'fail_fast': False,
    'max_failures': 5,
    'max_retries': 2,
}

generator = AAMVALicenseGenerator(config)
```

### Example 6: Statistics

```python
licenses, _ = generator.generate_multiple(count=100)
stats = generator.get_statistics(licenses)

print(f"States: {len(stats['states'])}")
print(f"Male: {stats['sex_distribution']['male']}")
print(f"Female: {stats['sex_distribution']['female']}")
print(f"Veterans: {stats['veteran_count']}")
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `output_dir` | str | "output" | Output directory for exports |
| `seed` | int | None | Random seed for reproducibility |
| `locale` | str | "en_US" | Faker locale |
| `validation_enabled` | bool | True | Enable validation |
| `strict_validation` | bool | False | Warnings become errors |
| `fail_fast` | bool | False | Stop on first error |
| `max_failures` | int | None | Max failures before stopping |
| `max_retries` | int | 0 | Retry attempts for failed items |
| `rollback_on_failure` | bool | False | Rollback on total failure |
| `iin_jurisdictions` | dict | Built-in | Custom IIN mappings |
| `state_formats` | dict | Built-in | Custom state formats |

## Error Handling

### Exception Hierarchy

```
Exception
├── LicenseGenerationError
├── ValidationError
├── ExportError
├── ImportError
├── BatchError
└── WorkflowError
```

### Error Recovery

```python
from aamva_license_generator import LicenseGenerationError

try:
    result = generator.full_workflow(count=100)
except LicenseGenerationError as e:
    # Handle generation errors
    logger.error(f"Generation failed: {e}")
except ExportError as e:
    # Handle export errors
    logger.error(f"Export failed: {e}")
except Exception as e:
    # Handle unexpected errors
    logger.error(f"Unexpected error: {e}")
```

## Progress Reporting

### Callback Signatures

```python
# Simple progress (used by most methods)
def progress(current: int, total: int):
    pass

# Status progress (used by batch operations)
def progress_with_status(current: int, total: int, status: str):
    pass

# Stage progress (used by full workflow)
def progress_with_stage(stage: str, current: int, total: int):
    pass

# State progress (used by all-states generation)
def progress_with_state(current: int, total: int, state: str):
    pass
```

### Progress Bar Example

```python
from tqdm import tqdm

def create_progress_callback():
    pbar = tqdm(total=100)
    def callback(current, total):
        pbar.n = current
        pbar.refresh()
    return callback

result = generator.generate_batch(
    count=100,
    progress_callback=create_progress_callback()
)
```

## Performance Considerations

### Memory Management

```python
# Process in chunks for large batches
result = generator.batch_service.process_in_chunks(
    items=range(1000),
    processor=lambda x, i: generator.generate_license(),
    chunk_size=100
)
```

### Parallel Processing

```python
from concurrent.futures import ThreadPoolExecutor

def generate_state(state):
    generator = AAMVALicenseGenerator()
    return generator.generate_multiple(10, state=state)

with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(generate_state, state)
               for state in ['CA', 'TX', 'FL', 'NY']]
    results = [f.result() for f in futures]
```

## Testing

### Unit Testing

```python
import unittest
from aamva_license_generator import AAMVALicenseGenerator

class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.generator = AAMVALicenseGenerator({'seed': 42})

    def test_generate_single(self):
        license, validation = self.generator.generate_license(state="CA")
        self.assertTrue(validation.is_valid)
        self.assertEqual(license[0]['DAJ'], "CA")
```

### Integration Testing

```python
def test_full_workflow():
    generator = AAMVALicenseGenerator({'output_dir': 'test_output'})

    result = generator.full_workflow(
        count=10,
        export_formats=['json'],
        validate_before_export=True
    )

    assert result['summary']['success']
    assert result['summary']['total_generated'] == 10
    assert 'json' in result['export_paths']
```

## Comparison with Monolithic Approach

### Before (generate_licenses.py)

```python
# Monolithic, procedural
ensure_dirs()
records = []
for i in range(10):
    data = generate_license_data()
    img_path, d = save_barcode_and_data(data, i)
    records.append((img_path, d))
create_avery_pdf(records)
create_docx_card(records)
```

### After (Integration Layer)

```python
# Clean, orchestrated
generator = AAMVALicenseGenerator()
result = generator.generate_batch(
    count=10,
    validate=True,
    export_formats=['pdf', 'docx'],
    progress_callback=callback
)
```

## Benefits

1. **Cleaner API**: Simple, intuitive interface
2. **Better Orchestration**: Services work together seamlessly
3. **Robust Error Handling**: Comprehensive exception hierarchy
4. **Progress Reporting**: Track long-running operations
5. **Thread Safety**: Safe for concurrent use
6. **Transaction Support**: All-or-nothing operations
7. **Partial Success**: Continue despite errors
8. **Extensible**: Easy to add new services/workflows

## Future Enhancements

- Async/await support for better performance
- Distributed processing for very large batches
- Caching layer for improved performance
- Plugin system for custom services
- REST API wrapper
- WebSocket for real-time progress

## License

MIT License - See LICENSE.md for details

## Authors

AAMVA License Generator Development Team
