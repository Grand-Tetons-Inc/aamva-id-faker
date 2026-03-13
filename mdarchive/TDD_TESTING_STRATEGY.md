# AAMVA ID Faker - Test-Driven Development Testing Strategy

**Version:** 2.0
**Date:** 2025-11-20
**Author:** QA & Testing Architecture Team
**Status:** Comprehensive Strategy - Ready for Implementation

---

## Executive Summary

This document presents a **revolutionary testing approach** for the AAMVA license generator that **exceeds industry standards** by implementing:

- **95%+ code coverage requirement** (vs typical 70-80%)
- **Property-based testing** for data validation (not just example-based)
- **Mutation testing** to validate test quality (not just coverage)
- **Visual regression testing** with pixel-perfect comparisons
- **Fuzzing-based security testing** for barcode parsing
- **Contract testing** for AAMVA specification compliance
- **Performance profiling** integrated into unit tests
- **Accessibility testing** as first-class citizen (WCAG 2.1 AA compliance)

**Core Philosophy:** Write tests BEFORE implementation. Every line of production code must be justified by a failing test.

---

## Table of Contents

1. [Test Framework Recommendations](#1-test-framework-recommendations)
2. [Test Organization Structure](#2-test-organization-structure)
3. [TDD Workflow Process](#3-tdd-workflow-process)
4. [Unit Testing Strategy](#4-unit-testing-strategy)
5. [GUI Component Testing](#5-gui-component-testing)
6. [Integration Testing](#6-integration-testing)
7. [End-to-End Workflow Testing](#7-end-to-end-workflow-testing)
8. [Visual Regression Testing](#8-visual-regression-testing)
9. [Accessibility Testing](#9-accessibility-testing)
10. [Performance Testing](#10-performance-testing)
11. [Cross-Platform Testing](#11-cross-platform-testing)
12. [Test Data Management](#12-test-data-management)
13. [Coverage Requirements](#13-coverage-requirements)
14. [CI/CD Integration](#14-ci-cd-integration)
15. [Innovative Testing Approaches](#15-innovative-testing-approaches)

---

## 1. Test Framework Recommendations

### Core Testing Stack

```python
# Primary Testing Framework
pytest==7.4.3                    # Modern, fixture-based testing
pytest-cov==4.1.0               # Coverage reporting
pytest-xdist==3.5.0             # Parallel test execution
pytest-timeout==2.2.0           # Prevent hanging tests
pytest-benchmark==4.0.0         # Performance benchmarking
pytest-mock==3.12.0             # Mocking utilities

# Property-Based Testing (INNOVATIVE)
hypothesis==6.92.1              # Generative testing for edge cases
hypothesis-jsonschema==0.23.1   # Schema-based generation

# GUI Testing
pytest-qt==4.3.1                # Qt GUI testing
PyAutoGUI==0.9.54              # UI automation (cross-platform)

# Visual Testing (INNOVATIVE)
pixelmatch==0.3.0              # Pixel-perfect image comparison
pillow-heif==0.14.0            # Advanced image format support
opencv-python==4.8.1.78        # Computer vision for visual testing

# API/Contract Testing
pact-python==2.1.0             # Contract testing for AAMVA spec
jsonschema==4.20.0             # Schema validation

# Mutation Testing (INNOVATIVE)
mutmut==2.4.4                  # Mutation testing for test quality
cosmic-ray==8.3.9              # Alternative mutation testing

# Security/Fuzzing (INNOVATIVE)
atheris==2.3.0                 # Fuzzing for barcode parsing
hypothesis-fspaths==0.1        # Filesystem path fuzzing

# Accessibility Testing (INNOVATIVE)
axe-selenium-python==2.1.6     # WCAG compliance testing
pa11y-python==0.3.0            # Automated accessibility checks

# Mocking & Fixtures
faker==20.1.0                  # Already used, extend for testing
freezegun==1.4.0               # Time-travel testing
responses==0.24.1              # HTTP mocking (future API tests)

# Reporting
pytest-html==4.1.1             # Beautiful HTML reports
allure-pytest==2.13.2          # Advanced test reporting
coverage[toml]==7.3.4          # TOML config support
```

### Justification for Innovative Choices

**Why Hypothesis?**
- Traditional testing: 5-10 handwritten examples per function
- Property-based testing: Generates 100-1000 test cases automatically
- Finds edge cases developers never consider (e.g., empty strings, Unicode, extreme values)

**Why Mutation Testing?**
- 100% coverage doesn't mean quality tests
- Mutation testing validates that tests actually catch bugs
- Typical projects: 0% mutation testing. This project: 80%+ mutation score target

**Why Visual Regression?**
- Manual visual inspection is unreliable and slow
- Automated pixel-perfect comparisons catch subtle rendering bugs
- Especially critical for barcode generation (one pixel error = scan failure)

**Why Accessibility Testing?**
- Often treated as afterthought
- This project: First-class requirement from day one
- Automated WCAG 2.1 AA compliance checks in CI/CD

---

## 2. Test Organization Structure

### Directory Layout

```
aamva-id-faker/
├── src/                              # Production code (refactored)
│   ├── __init__.py
│   ├── core/                         # Business logic
│   │   ├── __init__.py
│   │   ├── license_generator.py
│   │   ├── barcode_formatter.py
│   │   ├── state_formats.py
│   │   └── validators.py
│   ├── document/                     # Document generation
│   │   ├── __init__.py
│   │   ├── pdf_generator.py
│   │   ├── docx_generator.py
│   │   └── image_generator.py
│   ├── gui/                          # GUI components (future)
│   │   ├── __init__.py
│   │   ├── main_window.py
│   │   ├── license_form.py
│   │   └── preview_widget.py
│   └── utils/                        # Utilities
│       ├── __init__.py
│       ├── iin_lookup.py
│       └── file_io.py
│
├── tests/                            # Test suite
│   ├── __init__.py
│   ├── conftest.py                   # Shared fixtures
│   │
│   ├── unit/                         # Unit tests (isolated)
│   │   ├── __init__.py
│   │   ├── test_license_generator.py
│   │   ├── test_barcode_formatter.py
│   │   ├── test_state_formats.py
│   │   ├── test_validators.py
│   │   ├── test_iin_lookup.py
│   │   └── test_date_formatting.py
│   │
│   ├── integration/                  # Integration tests
│   │   ├── __init__.py
│   │   ├── test_license_to_barcode.py
│   │   ├── test_barcode_to_pdf.py
│   │   ├── test_full_pipeline.py
│   │   └── test_document_generation.py
│   │
│   ├── gui/                          # GUI component tests
│   │   ├── __init__.py
│   │   ├── test_main_window.py
│   │   ├── test_license_form.py
│   │   ├── test_preview_widget.py
│   │   └── test_user_interactions.py
│   │
│   ├── e2e/                          # End-to-end tests
│   │   ├── __init__.py
│   │   ├── test_cli_workflow.py
│   │   ├── test_gui_workflow.py
│   │   ├── test_batch_generation.py
│   │   └── test_error_scenarios.py
│   │
│   ├── visual/                       # Visual regression tests
│   │   ├── __init__.py
│   │   ├── test_barcode_rendering.py
│   │   ├── test_card_layout.py
│   │   ├── test_pdf_output.py
│   │   └── snapshots/                # Baseline images
│   │       ├── barcode_ca_baseline.png
│   │       ├── card_ny_baseline.png
│   │       └── ...
│   │
│   ├── accessibility/                # Accessibility tests
│   │   ├── __init__.py
│   │   ├── test_wcag_compliance.py
│   │   ├── test_keyboard_navigation.py
│   │   ├── test_screen_reader.py
│   │   └── test_color_contrast.py
│   │
│   ├── performance/                  # Performance tests
│   │   ├── __init__.py
│   │   ├── test_generation_speed.py
│   │   ├── test_memory_usage.py
│   │   ├── test_batch_performance.py
│   │   └── benchmarks/               # Benchmark results
│   │       └── baseline.json
│   │
│   ├── contract/                     # AAMVA spec compliance
│   │   ├── __init__.py
│   │   ├── test_aamva_2020_spec.py
│   │   ├── test_pdf417_spec.py
│   │   ├── test_field_formats.py
│   │   └── aamva_schema.json         # AAMVA spec as contract
│   │
│   ├── security/                     # Security/fuzzing tests
│   │   ├── __init__.py
│   │   ├── test_barcode_fuzzing.py
│   │   ├── test_input_sanitization.py
│   │   └── test_path_traversal.py
│   │
│   ├── property/                     # Property-based tests
│   │   ├── __init__.py
│   │   ├── test_data_invariants.py
│   │   ├── test_barcode_properties.py
│   │   └── test_roundtrip_encoding.py
│   │
│   ├── mutation/                     # Mutation test configs
│   │   ├── mutmut_config.py
│   │   └── cosmic_ray_config.toml
│   │
│   ├── fixtures/                     # Test data
│   │   ├── __init__.py
│   │   ├── sample_licenses.json
│   │   ├── aamva_test_vectors.json
│   │   └── edge_cases.json
│   │
│   └── utils/                        # Test utilities
│       ├── __init__.py
│       ├── assertions.py             # Custom assertions
│       ├── factories.py              # Test data factories
│       ├── matchers.py               # Custom matchers
│       └── mock_builders.py          # Mock object builders
│
├── pytest.ini                        # Pytest configuration
├── pyproject.toml                    # Modern Python config
├── .coveragerc                       # Coverage configuration
├── tox.ini                           # Multi-environment testing
└── .github/
    └── workflows/
        ├── test.yml                  # Main test workflow
        ├── mutation.yml              # Mutation testing
        └── visual-regression.yml     # Visual tests
```

### File Naming Conventions

**STRICT RULES:**

1. **Test files:** `test_<module_name>.py` (discoverable by pytest)
2. **Test classes:** `Test<FeatureName>` (optional, use for grouping)
3. **Test functions:** `test_<what>_<condition>_<expected>`
   - ✅ `test_california_license_number_matches_pattern`
   - ✅ `test_barcode_encoding_with_unicode_raises_error`
   - ✅ `test_pdf_generation_with_zero_licenses_creates_empty_file`
   - ❌ `test_license` (too vague)
   - ❌ `testLicense` (wrong convention)

4. **Fixture files:** Descriptive names in `fixtures/`
5. **Snapshot files:** `<test_name>_baseline.<ext>` in `visual/snapshots/`

---

## 3. TDD Workflow Process

### The Red-Green-Refactor Cycle

```
┌─────────────────────────────────────────────────────────┐
│                    TDD WORKFLOW                          │
└─────────────────────────────────────────────────────────┘

PHASE 1: RED (Write Failing Test)
├─ 1. Write a test for the next bit of functionality
├─ 2. Run test → verify it FAILS for the right reason
├─ 3. If test passes without implementation → bad test!
└─ Commit: "RED: Test for [feature]"

PHASE 2: GREEN (Make it Pass)
├─ 1. Write minimal code to make test pass
├─ 2. Run test → verify it PASSES
├─ 3. All other tests still pass
└─ Commit: "GREEN: Implement [feature]"

PHASE 3: REFACTOR (Clean up)
├─ 1. Improve code quality without changing behavior
├─ 2. Run all tests → verify still passing
├─ 3. Consider: DRY, naming, complexity
└─ Commit: "REFACTOR: Clean up [feature]"

REPEAT for each small feature increment
```

### Detailed TDD Process for This Project

#### Example: Implementing California License Number Generation

**STEP 1: Write the Test FIRST**

```python
# tests/unit/test_state_formats.py

import pytest
from src.core.state_formats import generate_license_number


class TestCaliforniaLicenseFormat:
    """Tests for California license number format: 1 letter + 7 digits"""

    def test_california_license_has_correct_length(self):
        """CA license should be exactly 8 characters"""
        result = generate_license_number('CA')
        assert len(result) == 8

    def test_california_license_starts_with_letter(self):
        """CA license should start with uppercase letter A-Z"""
        result = generate_license_number('CA')
        assert result[0].isalpha()
        assert result[0].isupper()

    def test_california_license_has_seven_digits(self):
        """CA license should have 7 digits after first letter"""
        result = generate_license_number('CA')
        assert result[1:].isdigit()
        assert len(result[1:]) == 7

    @pytest.mark.parametrize("iteration", range(100))
    def test_california_license_format_consistency(self, iteration):
        """Generate 100 CA licenses, all should match pattern"""
        result = generate_license_number('CA')
        assert len(result) == 8
        assert result[0].isalpha()
        assert result[1:].isdigit()

    def test_california_license_uniqueness(self):
        """Generated licenses should be unique (statistically)"""
        licenses = [generate_license_number('CA') for _ in range(1000)]
        unique_licenses = set(licenses)
        # Allow 1% collision rate (very generous)
        assert len(unique_licenses) >= 990
```

**STEP 2: Run Test → Watch it FAIL**

```bash
$ pytest tests/unit/test_state_formats.py::TestCaliforniaLicenseFormat -v

FAILED - ImportError: cannot import name 'generate_license_number'
```

**Perfect!** Test fails because code doesn't exist yet.

**STEP 3: Write Minimal Implementation**

```python
# src/core/state_formats.py

import random
import string


def generate_license_number(state: str) -> str:
    """Generate state-specific license number.

    Args:
        state: Two-letter state abbreviation

    Returns:
        License number conforming to state format
    """
    if state.upper() == 'CA':
        # California: 1 letter + 7 digits
        letter = random.choice(string.ascii_uppercase)
        digits = ''.join(random.choices(string.digits, k=7))
        return f"{letter}{digits}"

    raise NotImplementedError(f"State {state} not implemented yet")
```

**STEP 4: Run Test → Watch it PASS**

```bash
$ pytest tests/unit/test_state_formats.py::TestCaliforniaLicenseFormat -v

tests/unit/test_state_formats.py::TestCaliforniaLicenseFormat::test_california_license_has_correct_length PASSED
tests/unit/test_state_formats.py::TestCaliforniaLicenseFormat::test_california_license_starts_with_letter PASSED
tests/unit/test_state_formats.py::TestCaliforniaLicenseFormat::test_california_license_has_seven_digits PASSED
tests/unit/test_state_formats.py::TestCaliforniaLicenseFormat::test_california_license_format_consistency PASSED
tests/unit/test_state_formats.py::TestCaliforniaLicenseFormat::test_california_license_uniqueness PASSED

========== 5 passed in 0.23s ==========
```

**STEP 5: Refactor (if needed)**

```python
# src/core/state_formats.py (refactored)

import random
import string
from typing import Callable


# State format registry (Strategy pattern)
_STATE_FORMATS: dict[str, Callable[[], str]] = {}


def _register_format(state: str):
    """Decorator to register state format generators"""
    def decorator(func: Callable[[], str]):
        _STATE_FORMATS[state.upper()] = func
        return func
    return decorator


@_register_format('CA')
def _california_format() -> str:
    """California: 1 letter + 7 digits"""
    letter = random.choice(string.ascii_uppercase)
    digits = ''.join(random.choices(string.digits, k=7))
    return f"{letter}{digits}"


def generate_license_number(state: str) -> str:
    """Generate state-specific license number."""
    state_upper = state.upper()

    if state_upper not in _STATE_FORMATS:
        raise ValueError(f"Unknown state: {state}")

    return _STATE_FORMATS[state_upper]()
```

**STEP 6: Run Tests Again → Still PASS**

```bash
$ pytest tests/unit/test_state_formats.py -v
========== 5 passed in 0.21s ==========
```

**STEP 7: Commit**

```bash
git add tests/unit/test_state_formats.py src/core/state_formats.py
git commit -m "Add California license number generation with tests

- Implement CA format (1 letter + 7 digits)
- Add comprehensive unit tests with 100 iterations
- Use strategy pattern for extensibility
- Test coverage: 100%"
```

### TDD Commit Message Convention

```
<TYPE>: <Short description>

<Detailed description>

- Test coverage: X%
- Mutation score: Y% (if run)
- Performance: Z ms/op (if tested)
```

**Types:**
- `RED:` - Failing test (rare to commit)
- `GREEN:` - Implementation to pass test
- `REFACTOR:` - Code improvement, tests unchanged
- `TEST:` - Test-only changes
- `FIX:` - Bug fix (with test)

---

## 4. Unit Testing Strategy

### Principles

1. **Isolation:** Each unit test tests ONE function/method in isolation
2. **Fast:** Unit tests should run in <1ms each
3. **Deterministic:** Same input = same output, always
4. **Independent:** Tests can run in any order
5. **Self-contained:** No external dependencies (files, network, DB)

### Test Coverage Map

| Module | Functions | Unit Tests | Coverage Target |
|--------|-----------|------------|-----------------|
| `license_generator.py` | `generate_license_data()` | 20+ tests | 100% |
| `barcode_formatter.py` | `format_barcode_data()` | 15+ tests | 100% |
| `state_formats.py` | `generate_license_number()` | 51 states × 5 tests = 255+ | 100% |
| `validators.py` | All validation functions | 10+ per validator | 100% |
| `iin_lookup.py` | `get_iin_by_state()` | 67 jurisdictions | 100% |
| `date_formatting.py` | `format_date()` | 10+ edge cases | 100% |

### Example Unit Tests

#### test_license_generator.py

```python
"""Unit tests for license data generation"""

import pytest
from datetime import datetime, timedelta
from freezegun import freeze_time
from hypothesis import given, strategies as st

from src.core.license_generator import generate_license_data
from tests.utils.assertions import assert_aamva_compliant


class TestLicenseDataGeneration:
    """Tests for generate_license_data() function"""

    def test_returns_two_element_list(self):
        """Should return [DL_subfile, State_subfile]"""
        result = generate_license_data('CA')
        assert isinstance(result, list)
        assert len(result) == 2

    def test_dl_subfile_has_required_fields(self):
        """DL subfile must contain all mandatory AAMVA fields"""
        result = generate_license_data('CA')
        dl_subfile = result[0]

        required_fields = [
            'DAQ', 'DCS', 'DAC', 'DBB', 'DBA', 'DAG',
            'DAI', 'DAJ', 'DAK', 'DBC', 'DAY', 'DAU'
        ]

        for field in required_fields:
            assert field in dl_subfile, f"Missing required field: {field}"

    def test_state_subfile_has_correct_prefix(self):
        """State subfile type should be Z + first letter of state"""
        result = generate_license_data('CA')
        state_subfile = result[1]
        assert state_subfile['subfile_type'] == 'ZC'

        result_ny = generate_license_data('NY')
        state_subfile_ny = result_ny[1]
        assert state_subfile_ny['subfile_type'] == 'ZN'

    def test_dates_are_logically_consistent(self):
        """DOB < Issue Date < Expiration Date"""
        result = generate_license_data('CA')
        dl = result[0]

        dob = datetime.strptime(dl['DBB'], '%m%d%Y')
        issue = datetime.strptime(dl['DBD'], '%m%d%Y')
        exp = datetime.strptime(dl['DBA'], '%m%d%Y')

        assert dob < issue, "Birth date must be before issue date"
        assert issue < exp, "Issue date must be before expiration"

    def test_age_is_at_least_16(self):
        """Driver must be at least 16 years old"""
        result = generate_license_data('CA')
        dl = result[0]

        dob = datetime.strptime(dl['DBB'], '%m%d%Y')
        issue = datetime.strptime(dl['DBD'], '%m%d%Y')
        age = (issue - dob).days / 365.25

        assert age >= 16, f"Driver age {age} is below minimum 16"

    def test_sex_code_is_valid(self):
        """Sex field must be '1' (male) or '2' (female)"""
        result = generate_license_data('CA')
        dl = result[0]
        assert dl['DBC'] in ['1', '2']

    def test_male_has_male_name(self):
        """When sex=1 (male), first name should be masculine"""
        # This is probabilistic, run 50 times
        male_results = []
        for _ in range(50):
            result = generate_license_data('CA')
            dl = result[0]
            if dl['DBC'] == '1':  # Male
                male_results.append(dl['DAC'])

        # Check against known male names (faker library)
        from faker import Faker
        fake = Faker()
        male_names = {fake.first_name_male().upper() for _ in range(1000)}

        matches = sum(1 for name in male_results if name in male_names)
        # At least 80% should match known male names
        assert matches >= len(male_results) * 0.8

    def test_height_in_valid_range(self):
        """Height should be 58-78 inches (4'10" to 6'6")"""
        result = generate_license_data('CA')
        dl = result[0]
        height = int(dl['DAU'])
        assert 58 <= height <= 78

    def test_weight_in_valid_range(self):
        """Weight should be 115-275 lbs"""
        result = generate_license_data('CA')
        dl = result[0]
        weight = int(dl['DAW'])
        assert 115 <= weight <= 275

    def test_eye_color_is_valid(self):
        """Eye color must be from AAMVA standard codes"""
        valid_eyes = ['BLK', 'BLU', 'BRO', 'GRY', 'GRN',
                      'HAZ', 'MAR', 'PNK', 'DIC', 'UNK']
        result = generate_license_data('CA')
        dl = result[0]
        assert dl['DAY'] in valid_eyes

    def test_hair_color_is_valid(self):
        """Hair color must be from AAMVA standard codes"""
        valid_hair = ['BLK', 'BLN', 'BRO', 'GRY',
                      'RED', 'WHI', 'SDY', 'UNK']
        result = generate_license_data('CA')
        dl = result[0]
        assert dl['DAZ'] in valid_hair

    def test_state_matches_requested_state(self):
        """DAJ field should match requested state"""
        result = generate_license_data('TX')
        dl = result[0]
        assert dl['DAJ'] == 'TX'

    def test_zip_code_is_nine_digits(self):
        """ZIP code should be 9 digits (zero-padded)"""
        result = generate_license_data('CA')
        dl = result[0]
        assert len(dl['DAK']) == 9
        assert dl['DAK'].isdigit()

    @freeze_time("2025-11-20")
    def test_issue_date_is_today(self):
        """Issue date should be current date"""
        result = generate_license_data('CA')
        dl = result[0]
        assert dl['DBD'] == '11202025'

    def test_expiration_is_5_to_10_years_future(self):
        """Expiration should be 5-10 years after issue"""
        result = generate_license_data('CA')
        dl = result[0]

        issue = datetime.strptime(dl['DBD'], '%m%d%Y')
        exp = datetime.strptime(dl['DBA'], '%m%d%Y')
        years_diff = (exp - issue).days / 365.25

        assert 5 <= years_diff <= 10

    def test_all_text_fields_are_uppercase(self):
        """All text fields should be uppercase"""
        result = generate_license_data('CA')
        dl = result[0]

        text_fields = ['DCS', 'DAC', 'DAD', 'DAG', 'DAI']
        for field in text_fields:
            assert dl[field].isupper(), f"{field} is not uppercase"

    def test_document_discriminator_is_unique(self):
        """DCF field should be unique across licenses"""
        licenses = [generate_license_data('CA') for _ in range(100)]
        discriminators = [lic[0]['DCF'] for lic in licenses]
        assert len(set(discriminators)) == 100

    # PROPERTY-BASED TESTS (INNOVATIVE)
    @given(state=st.sampled_from(['CA', 'NY', 'TX', 'FL', 'WA']))
    def test_any_state_produces_valid_data(self, state):
        """Property: Any valid state produces valid license data"""
        result = generate_license_data(state)
        assert len(result) == 2
        assert result[0]['DAJ'] == state

    @given(iteration=st.integers(min_value=0, max_value=1000))
    def test_generation_is_deterministic_with_seed(self, iteration):
        """Property: Same seed produces same output"""
        import random
        random.seed(12345)
        result1 = generate_license_data('CA')

        random.seed(12345)
        result2 = generate_license_data('CA')

        assert result1[0]['DAQ'] == result2[0]['DAQ']


class TestEdgeCases:
    """Edge case tests for license generation"""

    def test_none_state_generates_random_state(self):
        """Passing None should generate random US state"""
        result = generate_license_data(None)
        dl = result[0]
        # Should have a valid 2-letter state code
        assert len(dl['DAJ']) == 2
        assert dl['DAJ'].isalpha()

    def test_lowercase_state_converts_to_uppercase(self):
        """Lowercase state code should work"""
        result = generate_license_data('ca')
        dl = result[0]
        assert dl['DAJ'] == 'CA'

    def test_invalid_state_raises_error(self):
        """Invalid state code should raise error"""
        with pytest.raises(ValueError, match="Unknown state"):
            generate_license_data('ZZ')

    def test_canadian_province_not_supported(self):
        """Canadian provinces should raise NotImplementedError"""
        with pytest.raises(NotImplementedError):
            generate_license_data('ON')  # Ontario
```

#### test_barcode_formatter.py

```python
"""Unit tests for AAMVA barcode formatting"""

import pytest
from hypothesis import given, strategies as st

from src.core.barcode_formatter import format_barcode_data
from src.core.license_generator import generate_license_data


class TestBarcodeFormatting:
    """Tests for format_barcode_data()"""

    def test_compliance_markers_present(self):
        """Barcode must start with @LF RS CR"""
        data = generate_license_data('CA')
        result = format_barcode_data(data)

        assert result[0:4] == "@\n\x1E\r", "Missing compliance markers"

    def test_ansi_file_type_present(self):
        """Header must contain 'ANSI ' file type"""
        data = generate_license_data('CA')
        result = format_barcode_data(data)

        header = result[4:9]
        assert header == 'ANSI '

    def test_iin_is_six_digits(self):
        """IIN (Issuer Identification Number) must be 6 digits"""
        data = generate_license_data('CA')
        result = format_barcode_data(data)

        iin = result[9:15]
        assert len(iin) == 6
        assert iin.isdigit()

    def test_california_has_correct_iin(self):
        """California IIN should be 636014"""
        data = generate_license_data('CA')
        result = format_barcode_data(data)

        iin = result[9:15]
        assert iin == '636014'

    def test_version_is_10(self):
        """AAMVA version should be '10' (2020 spec)"""
        data = generate_license_data('CA')
        result = format_barcode_data(data)

        version = result[15:17]
        assert version == '10'

    def test_subfile_count_is_02(self):
        """Should have 2 subfiles (DL + State)"""
        data = generate_license_data('CA')
        result = format_barcode_data(data)

        count = result[19:21]
        assert count == '02'

    def test_dl_subfile_designator_present(self):
        """DL subfile designator should be in header"""
        data = generate_license_data('CA')
        result = format_barcode_data(data)

        # Designator starts at position 21
        designator_type = result[21:23]
        assert designator_type == 'DL'

    def test_dl_offset_is_correct(self):
        """DL subfile offset should point to DL data start"""
        data = generate_license_data('CA')
        result = format_barcode_data(data)

        # Offset is at positions 23-27 (4 digits)
        offset_str = result[23:27]
        offset = int(offset_str)

        # DL data should start at this offset
        dl_data_start = result[offset:offset+2]
        assert dl_data_start == 'DL'

    def test_daq_field_comes_first_in_dl_subfile(self):
        """DAQ (license number) should be first field after DL marker"""
        data = generate_license_data('CA')
        result = format_barcode_data(data)

        # Find DL subfile start
        dl_start = result.find('DLDAQ')
        assert dl_start > 0, "DAQ field not found after DL marker"

    def test_fields_separated_by_newline(self):
        """Fields should be separated by LF (\\n)"""
        data = generate_license_data('CA')
        result = format_barcode_data(data)

        # Count field separators
        newline_count = result.count('\n')
        # Should have ~30 fields in DL + 3 in State + compliance LF
        assert newline_count >= 30

    def test_subfiles_terminated_by_carriage_return(self):
        """Subfiles should end with CR (\\r)"""
        data = generate_license_data('CA')
        result = format_barcode_data(data)

        # Should have 2 CR (one per subfile)
        cr_count = result.count('\r')
        assert cr_count == 3  # Compliance CR + 2 subfile CRs

    def test_total_length_in_valid_range(self):
        """Total barcode length should be 200-500 bytes"""
        data = generate_license_data('CA')
        result = format_barcode_data(data)

        length = len(result.encode('ascii'))
        assert 200 <= length <= 500

    def test_ascii_encoding_only(self):
        """Barcode should only contain ASCII characters"""
        data = generate_license_data('CA')
        result = format_barcode_data(data)

        # Should encode without error
        encoded = result.encode('ascii')
        assert isinstance(encoded, bytes)

    def test_roundtrip_encoding(self):
        """Encoding to ASCII and back should preserve data"""
        data = generate_license_data('CA')
        result = format_barcode_data(data)

        encoded = result.encode('ascii')
        decoded = encoded.decode('ascii')
        assert decoded == result

    # PROPERTY-BASED TEST
    @given(state=st.sampled_from(['CA', 'NY', 'TX', 'FL']))
    def test_barcode_structure_invariants(self, state):
        """Property: Barcode structure is always valid"""
        data = generate_license_data(state)
        result = format_barcode_data(data)

        # Invariants that must hold for ANY state
        assert result.startswith("@\n\x1E\r")
        assert "ANSI " in result
        assert "DL" in result
        assert result.count('\r') >= 2  # At least 2 subfiles
```

### Mocking Strategies

```python
# tests/unit/test_file_io.py

import pytest
from unittest.mock import Mock, patch, mock_open
from pathlib import Path

from src.utils.file_io import save_barcode, ensure_directories


class TestFileSaving:
    """Tests for file I/O with mocking"""

    @patch('src.utils.file_io.open', new_callable=mock_open)
    def test_save_barcode_writes_correct_data(self, mock_file):
        """Should write barcode data to file"""
        save_barcode("test_data", "/fake/path.txt")

        mock_file.assert_called_once_with("/fake/path.txt", "w")
        mock_file().write.assert_called_once_with("test_data")

    @patch('pathlib.Path.mkdir')
    def test_ensure_directories_creates_missing_dirs(self, mock_mkdir):
        """Should create directories if they don't exist"""
        ensure_directories()

        # Should call mkdir for output/barcodes, output/data, etc.
        assert mock_mkdir.call_count >= 3
        mock_mkdir.assert_called_with(parents=True, exist_ok=True)

    @patch('src.utils.file_io.os.path.exists', return_value=False)
    @patch('src.utils.file_io.os.makedirs')
    def test_directory_creation_error_handling(self, mock_makedirs, mock_exists):
        """Should raise RuntimeError if directory creation fails"""
        mock_makedirs.side_effect = OSError("Permission denied")

        with pytest.raises(RuntimeError, match="Unable to create"):
            ensure_directories()
```

---

## 5. GUI Component Testing

### Framework: pytest-qt

```python
# tests/gui/test_main_window.py

import pytest
from pytestqt.qt_compat import qt_api
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from src.gui.main_window import MainWindow


@pytest.fixture
def app(qtbot):
    """Fixture for main application window"""
    window = MainWindow()
    qtbot.addWidget(window)
    return window


class TestMainWindow:
    """Tests for main GUI window"""

    def test_window_title(self, app):
        """Window should have correct title"""
        assert app.windowTitle() == "AAMVA License Generator"

    def test_state_selector_has_all_states(self, app):
        """State dropdown should contain all 51 jurisdictions"""
        state_combo = app.findChild(QtWidgets.QComboBox, "state_selector")
        assert state_combo.count() == 51

    def test_generate_button_enabled_by_default(self, app):
        """Generate button should be enabled initially"""
        generate_btn = app.findChild(QtWidgets.QPushButton, "generate_btn")
        assert generate_btn.isEnabled()

    def test_clicking_generate_creates_license(self, app, qtbot):
        """Clicking generate should create license preview"""
        generate_btn = app.findChild(QtWidgets.QPushButton, "generate_btn")

        with qtbot.waitSignal(app.license_generated, timeout=1000):
            qtbot.mouseClick(generate_btn, Qt.LeftButton)

        # Preview should be populated
        preview = app.findChild(QtWidgets.QTextEdit, "preview")
        assert len(preview.toPlainText()) > 0

    def test_batch_mode_shows_count_input(self, app, qtbot):
        """Selecting batch mode should show quantity input"""
        batch_checkbox = app.findChild(QtWidgets.QCheckBox, "batch_mode")
        count_spinner = app.findChild(QtWidgets.QSpinBox, "batch_count")

        # Initially hidden
        assert not count_spinner.isVisible()

        # Click batch mode
        qtbot.mouseClick(batch_checkbox, Qt.LeftButton)

        # Now visible
        assert count_spinner.isVisible()

    def test_keyboard_shortcut_ctrl_g_generates(self, app, qtbot):
        """Ctrl+G should trigger generation"""
        with qtbot.waitSignal(app.license_generated, timeout=1000):
            qtbot.keyPress(app, Qt.Key_G, Qt.ControlModifier)

    def test_error_dialog_on_invalid_input(self, app, qtbot, monkeypatch):
        """Invalid input should show error dialog"""
        # Monkeypatch to simulate invalid state
        monkeypatch.setattr(app, "get_selected_state", lambda: "INVALID")

        generate_btn = app.findChild(QtWidgets.QPushButton, "generate_btn")

        with qtbot.waitSignal(app.error_occurred, timeout=1000):
            qtbot.mouseClick(generate_btn, Qt.LeftButton)


class TestLicenseForm:
    """Tests for license input form"""

    @pytest.fixture
    def form(self, qtbot):
        from src.gui.license_form import LicenseForm
        form = LicenseForm()
        qtbot.addWidget(form)
        return form

    def test_first_name_field_accepts_text(self, form, qtbot):
        """First name field should accept alphabetic input"""
        first_name = form.findChild(QtWidgets.QLineEdit, "first_name")
        qtbot.keyClicks(first_name, "John")
        assert first_name.text() == "John"

    def test_first_name_field_rejects_numbers(self, form, qtbot):
        """First name field should reject numeric input"""
        first_name = form.findChild(QtWidgets.QLineEdit, "first_name")
        qtbot.keyClicks(first_name, "123")
        assert first_name.text() == ""  # Should be empty

    def test_dob_picker_restricts_future_dates(self, form):
        """DOB picker should not allow future dates"""
        dob_picker = form.findChild(QtWidgets.QDateEdit, "dob")
        today = QtCore.QDate.currentDate()

        assert dob_picker.maximumDate() <= today

    def test_form_validation_on_submit(self, form, qtbot):
        """Submit should validate all required fields"""
        submit_btn = form.findChild(QtWidgets.QPushButton, "submit")

        # Try to submit empty form
        with qtbot.waitSignal(form.validation_failed, timeout=500):
            qtbot.mouseClick(submit_btn, Qt.LeftButton)
```

---

## 6. Integration Testing

Integration tests verify that multiple components work together correctly.

```python
# tests/integration/test_full_pipeline.py

import pytest
from pathlib import Path
import tempfile
import shutil

from src.core.license_generator import generate_license_data
from src.core.barcode_formatter import format_barcode_data
from src.document.pdf_generator import create_pdf
from src.utils.barcode_encoder import encode_and_save


@pytest.fixture
def temp_output_dir():
    """Temporary directory for test outputs"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


class TestLicenseToBarcodeIntegration:
    """Tests for license generation → barcode encoding"""

    def test_generated_license_encodes_to_valid_barcode(self):
        """License data should produce valid PDF417 barcode"""
        # Generate license
        data = generate_license_data('CA')

        # Format as AAMVA barcode
        barcode_string = format_barcode_data(data)

        # Encode to PDF417
        import pdf417
        codes = pdf417.encode(barcode_string, columns=13, security_level=5)

        # Should produce code array
        assert codes is not None
        assert len(codes) > 0

    def test_barcode_roundtrip_decoding(self):
        """Encoded barcode should decode back to same data"""
        # Generate and encode
        data = generate_license_data('CA')
        barcode_string = format_barcode_data(data)

        import pdf417
        codes = pdf417.encode(barcode_string)
        image = pdf417.render_image(codes)

        # Decode (requires pdf417 decoder - may need pyzbar)
        from pyzbar.pyzbar import decode
        decoded = decode(image)

        assert len(decoded) == 1
        assert decoded[0].data.decode('ascii') == barcode_string


class TestDocumentGenerationIntegration:
    """Tests for complete document generation pipeline"""

    def test_single_license_to_pdf(self, temp_output_dir):
        """Should generate PDF from single license"""
        # Generate license
        data = generate_license_data('CA')

        # Save barcode
        barcode_path, _ = encode_and_save(data, 0, temp_output_dir)

        # Generate PDF
        pdf_path = create_pdf([(barcode_path, data)], temp_output_dir)

        # Verify PDF exists and is valid
        assert pdf_path.exists()
        assert pdf_path.stat().st_size > 0

        # Verify PDF structure (using PyPDF2)
        from PyPDF2 import PdfReader
        reader = PdfReader(pdf_path)
        assert len(reader.pages) == 1

    def test_batch_10_licenses_to_pdf(self, temp_output_dir):
        """Should generate single-page PDF for 10 licenses"""
        # Generate 10 licenses
        licenses = [generate_license_data('CA') for _ in range(10)]

        # Save all barcodes
        records = []
        for i, data in enumerate(licenses):
            barcode_path, d = encode_and_save(data, i, temp_output_dir)
            records.append((barcode_path, d))

        # Generate PDF (Avery template fits 10 per page)
        pdf_path = create_pdf(records, temp_output_dir)

        from PyPDF2 import PdfReader
        reader = PdfReader(pdf_path)
        assert len(reader.pages) == 1

    def test_batch_25_licenses_to_pdf(self, temp_output_dir):
        """Should generate 3-page PDF for 25 licenses"""
        licenses = [generate_license_data('CA') for _ in range(25)]

        records = []
        for i, data in enumerate(licenses):
            barcode_path, d = encode_and_save(data, i, temp_output_dir)
            records.append((barcode_path, d))

        pdf_path = create_pdf(records, temp_output_dir)

        from PyPDF2 import PdfReader
        reader = PdfReader(pdf_path)
        # 10 per page: 25 licenses = 3 pages
        assert len(reader.pages) == 3


class TestErrorPropagation:
    """Tests for error handling across component boundaries"""

    def test_invalid_state_propagates_error(self):
        """Invalid state should propagate error through pipeline"""
        with pytest.raises(ValueError, match="Unknown state"):
            data = generate_license_data('ZZ')

    def test_corrupt_data_fails_barcode_encoding(self):
        """Corrupt license data should fail at encoding step"""
        # Create invalid data structure
        bad_data = [{'not_a_valid_field': 'bad'}]

        with pytest.raises(KeyError):
            format_barcode_data(bad_data)

    def test_missing_iin_fails_gracefully(self):
        """Missing IIN should use default gracefully"""
        # Create data for state without IIN mapping
        data = generate_license_data('CA')
        # Corrupt state code
        data[0]['DAJ'] = 'FAKE'

        # Should use default IIN (636026 - Arizona)
        result = format_barcode_data(data)
        assert '636026' in result
```

---

## 7. End-to-End Workflow Testing

E2E tests verify complete user workflows from start to finish.

```python
# tests/e2e/test_cli_workflow.py

import pytest
import subprocess
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def temp_workspace():
    """Isolated workspace for CLI tests"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


class TestCLIWorkflows:
    """End-to-end CLI workflow tests"""

    def test_generate_single_license_default(self, temp_workspace):
        """Default command should generate 10 random licenses"""
        result = subprocess.run(
            ['python', 'generate_licenses.py'],
            cwd=temp_workspace,
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        assert Path(temp_workspace / 'output').exists()

        # Should have 10 barcodes
        barcodes = list((temp_workspace / 'output/barcodes').glob('*.bmp'))
        assert len(barcodes) == 10

        # Should have PDF
        assert (temp_workspace / 'output/licenses_avery_28371.pdf').exists()

        # Should have DOCX
        assert (temp_workspace / 'output/cards.docx').exists()

    def test_generate_specific_state_california(self, temp_workspace):
        """Generate 5 California licenses"""
        result = subprocess.run(
            ['python', 'generate_licenses.py', '-s', 'CA', '-n', '5'],
            cwd=temp_workspace,
            capture_output=True,
            text=True
        )

        assert result.returncode == 0

        # Should have 5 barcodes
        barcodes = list((temp_workspace / 'output/barcodes').glob('*.bmp'))
        assert len(barcodes) == 5

        # Verify all are CA licenses (check data files)
        data_files = sorted((temp_workspace / 'output/data').glob('*.txt'))
        for data_file in data_files:
            content = data_file.read_text()
            assert 'DAJCA' in content  # State field

    def test_all_states_workflow(self, temp_workspace):
        """Generate one license per state (51 total)"""
        result = subprocess.run(
            ['python', 'generate_licenses.py', '--all-states'],
            cwd=temp_workspace,
            capture_output=True,
            text=True,
            timeout=60  # May take longer
        )

        assert result.returncode == 0

        # Should have 51 barcodes (50 states + DC)
        barcodes = list((temp_workspace / 'output/barcodes').glob('*.bmp'))
        assert len(barcodes) == 51

        # PDF should have 6 pages (10 per page)
        from PyPDF2 import PdfReader
        pdf_path = temp_workspace / 'output/licenses_avery_28371.pdf'
        reader = PdfReader(pdf_path)
        assert len(reader.pages) == 6  # 51 licenses / 10 per page = 6 pages

    def test_no_pdf_flag(self, temp_workspace):
        """--no-pdf should skip PDF generation"""
        result = subprocess.run(
            ['python', 'generate_licenses.py', '-n', '5', '--no-pdf'],
            cwd=temp_workspace,
            capture_output=True,
            text=True
        )

        assert result.returncode == 0

        # Should have barcodes
        assert (temp_workspace / 'output/barcodes').exists()

        # Should NOT have PDF
        assert not (temp_workspace / 'output/licenses_avery_28371.pdf').exists()

    def test_invalid_state_shows_error(self, temp_workspace):
        """Invalid state code should show clear error"""
        result = subprocess.run(
            ['python', 'generate_licenses.py', '-s', 'ZZ'],
            cwd=temp_workspace,
            capture_output=True,
            text=True
        )

        assert result.returncode != 0
        assert 'Unknown state' in result.stderr or 'Unknown state' in result.stdout

    def test_batch_1000_licenses_performance(self, temp_workspace):
        """Large batch should complete in reasonable time"""
        import time

        start = time.time()
        result = subprocess.run(
            ['python', 'generate_licenses.py', '-n', '1000', '--no-pdf', '--no-word'],
            cwd=temp_workspace,
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )
        elapsed = time.time() - start

        assert result.returncode == 0

        # Should complete in under 60 seconds
        assert elapsed < 60, f"Took {elapsed}s, expected <60s"

        # Should have 1000 barcodes
        barcodes = list((temp_workspace / 'output/barcodes').glob('*.bmp'))
        assert len(barcodes) == 1000
```

---

## 8. Visual Regression Testing

**INNOVATIVE APPROACH:** Pixel-perfect comparisons for barcode and document rendering.

```python
# tests/visual/test_barcode_rendering.py

import pytest
from PIL import Image
import numpy as np
from pathlib import Path

from src.core.license_generator import generate_license_data
from src.utils.barcode_encoder import encode_and_save
from tests.utils.visual_comparison import compare_images, save_baseline


BASELINE_DIR = Path(__file__).parent / 'snapshots'


@pytest.fixture
def fixed_license_data():
    """Generate deterministic license data for visual testing"""
    import random
    random.seed(42)  # Fixed seed for reproducibility

    return generate_license_data('CA')


class TestBarcodeVisualRegression:
    """Visual regression tests for barcode rendering"""

    def test_california_barcode_matches_baseline(self, fixed_license_data, tmp_path):
        """CA barcode should match pixel-perfect baseline"""
        # Generate barcode
        barcode_path, _ = encode_and_save(fixed_license_data, 0, tmp_path)

        # Load baseline
        baseline_path = BASELINE_DIR / 'barcode_ca_baseline.png'

        if not baseline_path.exists():
            # First run: save as baseline
            save_baseline(barcode_path, baseline_path)
            pytest.skip("Baseline created, re-run test")

        # Compare
        diff_percentage = compare_images(barcode_path, baseline_path)

        # Allow 0.1% difference (for anti-aliasing variations)
        assert diff_percentage < 0.1, \
            f"Barcode differs from baseline by {diff_percentage}%"

    def test_barcode_dimensions_consistent(self, fixed_license_data, tmp_path):
        """Barcode dimensions should be consistent"""
        barcode_path, _ = encode_and_save(fixed_license_data, 0, tmp_path)

        img = Image.open(barcode_path)
        width, height = img.size

        # PDF417 with 13 columns should have consistent dimensions
        # Actual dimensions depend on pdf417 library rendering
        assert width > 0
        assert height > 0
        assert width / height > 2  # Barcodes are wider than tall

    def test_barcode_is_black_and_white(self, fixed_license_data, tmp_path):
        """Barcode should only contain black and white pixels"""
        barcode_path, _ = encode_and_save(fixed_license_data, 0, tmp_path)

        img = Image.open(barcode_path).convert('L')  # Grayscale
        pixels = np.array(img)

        unique_values = np.unique(pixels)

        # Should only have 2 values (black=0, white=255)
        # Allow some anti-aliasing (values close to 0 or 255)
        assert len(unique_values) <= 10, \
            "Barcode has too many gray levels (anti-aliasing issue)"

    @pytest.mark.parametrize("state", ['CA', 'NY', 'TX', 'FL'])
    def test_barcode_visual_consistency_across_states(self, state, tmp_path):
        """Barcodes for different states should have similar structure"""
        import random
        random.seed(42)

        data = generate_license_data(state)
        barcode_path, _ = encode_and_save(data, 0, tmp_path)

        img = Image.open(barcode_path)
        width, height = img.size

        # All barcodes should have similar aspect ratio
        aspect_ratio = width / height
        assert 2 < aspect_ratio < 6


class TestCardImageVisualRegression:
    """Visual regression tests for card images"""

    def test_card_layout_matches_baseline(self, fixed_license_data, tmp_path):
        """Card image should match baseline layout"""
        from src.document.image_generator import generate_card_image

        barcode_path, _ = encode_and_save(fixed_license_data, 0, tmp_path)
        card_path = generate_card_image(fixed_license_data, barcode_path)

        baseline_path = BASELINE_DIR / 'card_ca_baseline.png'

        if not baseline_path.exists():
            save_baseline(card_path, baseline_path)
            pytest.skip("Baseline created")

        # Allow 1% difference (font rendering variations)
        diff = compare_images(card_path, baseline_path)
        assert diff < 1.0

    def test_card_text_is_readable(self, fixed_license_data, tmp_path):
        """Card text should be sharp and readable (OCR test)"""
        from src.document.image_generator import generate_card_image
        import pytesseract

        barcode_path, _ = encode_and_save(fixed_license_data, 0, tmp_path)
        card_path = generate_card_image(fixed_license_data, barcode_path)

        # Run OCR on card
        img = Image.open(card_path)
        text = pytesseract.image_to_string(img)

        # Should recognize name fields
        dl_data = fixed_license_data[0]
        assert dl_data['DCS'] in text  # Last name
        assert dl_data['DAC'] in text  # First name


# tests/utils/visual_comparison.py

def compare_images(image1_path, image2_path):
    """Compare two images and return difference percentage

    Returns:
        float: Percentage of different pixels (0-100)
    """
    from pixelmatch.contrib.PIL import pixelmatch

    img1 = Image.open(image1_path).convert('RGB')
    img2 = Image.open(image2_path).convert('RGB')

    # Ensure same dimensions
    if img1.size != img2.size:
        raise ValueError("Images have different dimensions")

    # Create diff image
    diff_img = Image.new('RGB', img1.size)

    # Count different pixels
    mismatch = pixelmatch(img1, img2, diff_img, threshold=0.1)

    # Calculate percentage
    total_pixels = img1.size[0] * img1.size[1]
    diff_percentage = (mismatch / total_pixels) * 100

    return diff_percentage


def save_baseline(source_path, baseline_path):
    """Save image as baseline for future comparisons"""
    import shutil
    baseline_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(source_path, baseline_path)
```

---

## 9. Accessibility Testing

**INNOVATIVE:** Treat accessibility as first-class requirement, not afterthought.

```python
# tests/accessibility/test_wcag_compliance.py

import pytest
from selenium import webdriver
from axe_selenium_python import Axe


@pytest.fixture
def browser():
    """Selenium browser for accessibility testing"""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()


class TestGUIAccessibility:
    """WCAG 2.1 AA compliance tests"""

    def test_main_window_passes_axe_checks(self, browser):
        """Main window should pass all axe-core accessibility checks"""
        # Load GUI in browser (requires web export or Qt WebEngine)
        browser.get('http://localhost:8000/gui')

        # Run axe accessibility scan
        axe = Axe(browser)
        axe.inject()
        results = axe.run()

        # No violations
        assert len(results['violations']) == 0, \
            f"Found {len(results['violations'])} accessibility violations"

    def test_color_contrast_ratio_meets_wcag_aa(self):
        """UI colors should have 4.5:1 contrast ratio (WCAG AA)"""
        from tests.utils.accessibility import check_contrast_ratio

        # Test common color combinations
        fg_color = (0, 0, 0)      # Black text
        bg_color = (255, 255, 255) # White background

        ratio = check_contrast_ratio(fg_color, bg_color)
        assert ratio >= 4.5, f"Contrast ratio {ratio} below 4.5:1 minimum"

    def test_all_buttons_have_accessible_names(self, browser):
        """All buttons should have accessible labels"""
        browser.get('http://localhost:8000/gui')

        buttons = browser.find_elements_by_tag_name('button')

        for button in buttons:
            # Should have aria-label or visible text
            label = button.get_attribute('aria-label') or button.text
            assert label and len(label) > 0, \
                "Button without accessible label found"

    def test_keyboard_navigation_complete(self, qtbot):
        """Should be able to navigate entire UI with keyboard"""
        from src.gui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)

        # Start at first focusable element
        window.setFocus()

        # Tab through all elements
        focusable_count = 0
        for _ in range(50):  # Max 50 elements
            qtbot.keyPress(window, Qt.Key_Tab)
            if window.focusWidget():
                focusable_count += 1

        # Should have at least 5 focusable elements
        assert focusable_count >= 5

    def test_screen_reader_announcements(self, qtbot):
        """Screen reader should receive appropriate announcements"""
        from src.gui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)

        # Generate button should announce action
        generate_btn = window.findChild(QPushButton, "generate_btn")
        accessible_name = generate_btn.accessibleName()

        assert "generate" in accessible_name.lower()
        assert "license" in accessible_name.lower()

    def test_error_messages_announced_to_screen_readers(self, qtbot):
        """Error messages should be announced via aria-live"""
        from src.gui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)

        # Trigger error
        with qtbot.waitSignal(window.error_occurred):
            window.trigger_error("Test error")

        # Error container should have aria-live="assertive"
        error_label = window.findChild(QLabel, "error_message")
        # In Qt, check accessible description
        assert error_label.accessibleDescription() == "Test error"


# tests/utils/accessibility.py

def check_contrast_ratio(fg_rgb, bg_rgb):
    """Calculate WCAG color contrast ratio

    Args:
        fg_rgb: Foreground color (R, G, B) tuple
        bg_rgb: Background color (R, G, B) tuple

    Returns:
        float: Contrast ratio (1.0 to 21.0)
    """
    def relative_luminance(rgb):
        """Calculate relative luminance per WCAG formula"""
        r, g, b = rgb
        r, g, b = r / 255, g / 255, b / 255

        def adjust(c):
            if c <= 0.03928:
                return c / 12.92
            else:
                return ((c + 0.055) / 1.055) ** 2.4

        r, g, b = adjust(r), adjust(g), adjust(b)
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    lum1 = relative_luminance(fg_rgb)
    lum2 = relative_luminance(bg_rgb)

    lighter = max(lum1, lum2)
    darker = min(lum1, lum2)

    return (lighter + 0.05) / (darker + 0.05)
```

---

## 10. Performance Testing

```python
# tests/performance/test_generation_speed.py

import pytest
from time import time
import cProfile
import pstats
from io import StringIO

from src.core.license_generator import generate_license_data
from src.core.barcode_formatter import format_barcode_data


class TestGenerationPerformance:
    """Performance benchmarks for license generation"""

    def test_single_license_generation_speed(self, benchmark):
        """Single license should generate in <10ms"""
        result = benchmark(generate_license_data, 'CA')

        # Should be very fast
        assert benchmark.stats['mean'] < 0.01  # 10ms

    def test_barcode_formatting_speed(self, benchmark):
        """Barcode formatting should complete in <5ms"""
        data = generate_license_data('CA')

        result = benchmark(format_barcode_data, data)
        assert benchmark.stats['mean'] < 0.005  # 5ms

    def test_batch_100_licenses_speed(self, benchmark):
        """100 licenses should generate in <1 second"""
        def generate_batch():
            return [generate_license_data('CA') for _ in range(100)]

        result = benchmark(generate_batch)
        assert benchmark.stats['mean'] < 1.0  # 1 second

    @pytest.mark.slow
    def test_batch_1000_licenses_speed(self):
        """1000 licenses benchmark"""
        start = time()
        licenses = [generate_license_data('CA') for _ in range(1000)]
        elapsed = time() - start

        print(f"\n1000 licenses generated in {elapsed:.2f}s")
        print(f"Rate: {1000/elapsed:.2f} licenses/second")

        # Should be <30 seconds
        assert elapsed < 30

    def test_profiling_license_generation(self):
        """Profile license generation to find bottlenecks"""
        profiler = cProfile.Profile()

        profiler.enable()
        for _ in range(100):
            generate_license_data('CA')
        profiler.disable()

        # Print stats
        s = StringIO()
        ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
        ps.print_stats(10)  # Top 10 functions

        print(s.getvalue())


class TestMemoryUsage:
    """Memory usage tests"""

    def test_single_license_memory_footprint(self):
        """Single license should use <5KB memory"""
        import sys

        data = generate_license_data('CA')
        size = sys.getsizeof(data)

        # Rough estimate
        assert size < 5000  # 5KB

    def test_batch_100_licenses_memory(self):
        """100 licenses should use <500KB"""
        import tracemalloc

        tracemalloc.start()

        licenses = [generate_license_data('CA') for _ in range(100)]

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        print(f"\n100 licenses: {peak / 1024:.2f} KB peak memory")

        # Should be <500KB
        assert peak < 500 * 1024

    def test_no_memory_leaks_in_loop(self):
        """Repeated generation should not leak memory"""
        import tracemalloc

        tracemalloc.start()

        # Generate 1000 licenses in loop (discarding each)
        for _ in range(1000):
            data = generate_license_data('CA')
            del data

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        print(f"\n1000 iterations: {current / 1024:.2f} KB current memory")

        # Current should be near zero (garbage collected)
        assert current < 100 * 1024  # <100KB
```

---

## 11. Cross-Platform Testing

```python
# tests/cross_platform/test_platform_compatibility.py

import pytest
import platform
import sys
from pathlib import Path


class TestCrossPlatformFileIO:
    """Test file I/O across different platforms"""

    def test_output_directory_creation_windows_style(self, tmp_path):
        """Should handle Windows-style paths"""
        if platform.system() != 'Windows':
            pytest.skip("Windows-only test")

        from src.utils.file_io import ensure_directories

        # Should create directories without error
        ensure_directories()
        assert Path('output/barcodes').exists()

    def test_output_directory_creation_unix_style(self, tmp_path):
        """Should handle Unix-style paths"""
        if platform.system() == 'Windows':
            pytest.skip("Unix-only test")

        from src.utils.file_io import ensure_directories

        ensure_directories()
        assert Path('output/barcodes').exists()

    def test_path_separators_normalized(self):
        """Paths should use os.sep correctly"""
        from src.utils.file_io import get_output_path

        path = get_output_path('barcodes', 'test.bmp')

        # Should use correct separator for platform
        assert os.sep in str(path)


class TestFontRendering:
    """Test font rendering across platforms"""

    @pytest.mark.parametrize("platform_name", ['Windows', 'Linux', 'Darwin'])
    def test_font_loads_on_platform(self, platform_name):
        """Font should load on all platforms"""
        if platform.system() != platform_name:
            pytest.skip(f"Skipping {platform_name} test")

        from src.document.image_generator import load_font

        font = load_font('LiberationMono-Bold.ttf', size=50)
        assert font is not None


# tox.ini - Multi-platform testing configuration

[tox]
envlist = py39-{linux,macos,windows}

[testenv]
platform =
    linux: linux
    macos: darwin
    windows: win32

deps =
    pytest
    pytest-cov
    -r requirements.txt

commands =
    pytest tests/ -v --cov=src
```

---

## 12. Test Data Management

### Fixtures and Factories

```python
# tests/fixtures/test_data.py

import pytest
from faker import Faker
import random


@pytest.fixture
def faker_seed():
    """Provide seeded Faker for reproducible tests"""
    fake = Faker()
    Faker.seed(12345)
    random.seed(12345)
    return fake


@pytest.fixture
def sample_california_license():
    """Fixed California license for testing"""
    return [
        {
            "subfile_type": "DL",
            "DAQ": "A1234567",
            "DCA": "D",
            "DCB": "",
            "DCD": "",
            "DBA": "08142032",
            "DCS": "DOE",
            "DAC": "JOHN",
            "DAD": "MICHAEL",
            "DBD": "11202025",
            "DBB": "05151990",
            "DBC": "1",
            "DAY": "BRO",
            "DAU": "070",
            "DAW": "180",
            "DAZ": "BRO",
            "DCL": "W",
            "DAG": "123 MAIN STREET",
            "DAI": "LOS ANGELES",
            "DAJ": "CA",
            "DAK": "900120000",
            "DCF": "DOC12345",
            "DCG": "USA",
            "DDE": "N",
            "DDF": "N",
            "DDG": "N",
            "DDA": "F",
            "DDB": "11202025",
            "DDC": "",
            "DDD": "0",
            "DDK": "1",
            "DDL": "0"
        },
        {
            "subfile_type": "ZC",
            "ZCW": "ORANGE",
            "ZCT": "TEST STRING",
            "ZCX": "A123456"
        }
    ]


@pytest.fixture
def aamva_test_vectors():
    """Official AAMVA test vectors for compliance testing"""
    return {
        "california_valid": {
            "iin": "636014",
            "version": "10",
            "license_number": "A1234567"
        },
        "new_york_valid": {
            "iin": "636001",
            "version": "10",
            "license_number": "A123456789012345678"  # NY can be very long
        }
    }
```

### Property-Based Testing with Hypothesis

```python
# tests/property/test_data_invariants.py

from hypothesis import given, strategies as st, assume
from datetime import datetime, timedelta

from src.core.license_generator import generate_license_data


# Custom strategies
state_codes = st.sampled_from([
    'CA', 'NY', 'TX', 'FL', 'WA', 'IL', 'PA', 'OH',
    'GA', 'NC', 'MI', 'NJ', 'VA', 'AZ', 'MA'
])

eye_colors = st.sampled_from([
    'BLK', 'BLU', 'BRO', 'GRY', 'GRN', 'HAZ', 'MAR', 'PNK', 'DIC', 'UNK'
])

class TestDataInvariants:
    """Property-based tests for data invariants"""

    @given(state=state_codes)
    def test_property_generated_data_has_two_subfiles(self, state):
        """Property: All licenses have exactly 2 subfiles"""
        result = generate_license_data(state)
        assert len(result) == 2

    @given(state=state_codes)
    def test_property_dates_always_ordered(self, state):
        """Property: DOB < Issue < Expiration always holds"""
        result = generate_license_data(state)
        dl = result[0]

        dob = datetime.strptime(dl['DBB'], '%m%d%Y')
        issue = datetime.strptime(dl['DBD'], '%m%d%Y')
        exp = datetime.strptime(dl['DBA'], '%m%d%Y')

        assert dob < issue < exp

    @given(state=state_codes)
    def test_property_license_number_never_empty(self, state):
        """Property: License number is never empty"""
        result = generate_license_data(state)
        assert len(result[0]['DAQ']) > 0

    @given(
        state=state_codes,
        iterations=st.integers(min_value=1, max_value=100)
    )
    def test_property_generation_deterministic_with_seed(self, state, iterations):
        """Property: Same seed produces same output"""
        import random

        random.seed(42)
        result1 = generate_license_data(state)

        random.seed(42)
        result2 = generate_license_data(state)

        assert result1[0]['DAQ'] == result2[0]['DAQ']
```

---

## 13. Coverage Requirements

### Coverage Targets

| Test Type | Coverage Requirement | Rationale |
|-----------|---------------------|-----------|
| **Unit Tests** | 95% line coverage | Core business logic must be fully tested |
| **Branch Coverage** | 90% | All conditional paths tested |
| **Integration Tests** | 85% of integration points | All component interactions tested |
| **E2E Tests** | 100% of user workflows | Every user path must work |
| **Mutation Score** | 80%+ | Tests must actually catch bugs |

### Coverage Configuration

```ini
# .coveragerc

[run]
source = src
omit =
    */tests/*
    */conftest.py
    */__init__.py
    */setup.py

[report]
precision = 2
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:
    @abstractmethod

[html]
directory = htmlcov

[json]
output = coverage.json
```

### Running Coverage

```bash
# Generate coverage report
pytest tests/ --cov=src --cov-report=html --cov-report=term

# Check minimum coverage (fail if below 95%)
pytest tests/ --cov=src --cov-fail-under=95

# Coverage with branch analysis
pytest tests/ --cov=src --cov-branch --cov-report=term-missing

# Generate JSON report for CI/CD
pytest tests/ --cov=src --cov-report=json
```

### Mutation Testing

```bash
# Run mutation testing with mutmut
mutmut run --paths-to-mutate=src/

# Show results
mutmut results

# Show specific mutations
mutmut show 1

# Apply mutations that weren't caught (to improve tests)
mutmut apply 1
```

---

## 14. CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml

name: Comprehensive Test Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  # JOB 1: Unit & Integration Tests
  unit-integration-tests:
    name: Unit & Integration Tests (Python ${{ matrix.python-version }})
    runs-on: ${{ matrix.os }}

    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ['3.9', '3.10', '3.11', '3.12']

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Cache dependencies
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-test.txt

      - name: Run unit tests with coverage
        run: |
          pytest tests/unit/ tests/integration/ \
            --cov=src \
            --cov-report=xml \
            --cov-report=html \
            --cov-fail-under=95 \
            -v \
            --tb=short

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
          flags: unittests
          name: codecov-${{ matrix.os }}-py${{ matrix.python-version }}

  # JOB 2: E2E Tests
  e2e-tests:
    name: End-to-End Tests
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt

      - name: Run E2E tests
        run: |
          pytest tests/e2e/ -v --tb=short

      - name: Upload E2E artifacts
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: e2e-failures
          path: |
            output/
            logs/

  # JOB 3: Visual Regression Tests
  visual-regression:
    name: Visual Regression Tests
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Need full history for baselines

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt
          pip install pixelmatch pillow opencv-python

      - name: Run visual tests
        run: |
          pytest tests/visual/ -v

      - name: Upload diff images on failure
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: visual-diffs
          path: tests/visual/diffs/

  # JOB 4: Performance Tests
  performance-tests:
    name: Performance Benchmarks
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest-benchmark

      - name: Run performance tests
        run: |
          pytest tests/performance/ \
            --benchmark-only \
            --benchmark-json=benchmark.json

      - name: Store benchmark result
        uses: benchmark-action/github-action-benchmark@v1
        with:
          tool: 'pytest'
          output-file-path: benchmark.json
          github-token: ${{ secrets.GITHUB_TOKEN }}
          auto-push: true

  # JOB 5: Mutation Testing (Weekly)
  mutation-testing:
    name: Mutation Testing
    runs-on: ubuntu-latest
    if: github.event_name == 'schedule'  # Only run on schedule

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install mutmut

      - name: Run mutation testing
        run: |
          mutmut run --paths-to-mutate=src/ --tests-dir=tests/

      - name: Check mutation score
        run: |
          mutmut results
          # Fail if mutation score < 80%
          python scripts/check_mutation_score.py --minimum=80

  # JOB 6: Security/Fuzzing Tests
  security-fuzzing:
    name: Security & Fuzzing Tests
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install atheris hypothesis

      - name: Run fuzzing tests
        run: |
          pytest tests/security/ -v --timeout=300

  # JOB 7: Accessibility Tests
  accessibility-tests:
    name: Accessibility Tests (WCAG 2.1 AA)
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install axe-selenium-python selenium

      - name: Run accessibility tests
        run: |
          pytest tests/accessibility/ -v

      - name: Generate accessibility report
        run: |
          python scripts/generate_a11y_report.py

  # JOB 8: Code Quality Checks
  code-quality:
    name: Code Quality (Linting, Type Checking)
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install ruff mypy pylint

      - name: Run Ruff linter
        run: |
          ruff check src/ tests/

      - name: Run MyPy type checker
        run: |
          mypy src/ --strict

      - name: Run Pylint
        run: |
          pylint src/ --fail-under=9.0
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml

repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.12.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  - repo: local
    hooks:
      - id: pytest-unit
        name: Run unit tests
        entry: pytest tests/unit/ -x
        language: system
        pass_filenames: false
        always_run: true
```

---

## 15. Innovative Testing Approaches

### 1. Contract Testing for AAMVA Spec Compliance

```python
# tests/contract/test_aamva_2020_spec.py

import pytest
from pact import Consumer, Provider
import jsonschema

# Load AAMVA specification as JSON schema
with open('tests/contract/aamva_schema.json') as f:
    AAMVA_SCHEMA = json.load(f)


class TestAAMVASpecCompliance:
    """Contract tests against AAMVA 2020 specification"""

    def test_dl_subfile_matches_aamva_schema(self):
        """DL subfile must conform to AAMVA DL/ID-2020 spec"""
        from src.core.license_generator import generate_license_data

        data = generate_license_data('CA')
        dl_subfile = data[0]

        # Validate against schema
        jsonschema.validate(instance=dl_subfile, schema=AAMVA_SCHEMA['dl_subfile'])

    def test_barcode_header_matches_aamva_format(self):
        """Barcode header must match exact AAMVA specification"""
        from src.core.barcode_formatter import format_barcode_data
        from src.core.license_generator import generate_license_data

        data = generate_license_data('CA')
        barcode = format_barcode_data(data)

        # Test compliance markers
        assert barcode[0:1] == '@', "Missing @ compliance marker"
        assert barcode[1:2] == '\n', "Missing LF after @"
        assert barcode[2:3] == '\x1E', "Missing RS (0x1E) record separator"
        assert barcode[3:4] == '\r', "Missing CR after RS"

        # Test ANSI header
        assert barcode[4:9] == 'ANSI ', "Invalid ANSI file type"

        # IIN must be 6 digits
        iin = barcode[9:15]
        assert len(iin) == 6, "IIN must be 6 characters"
        assert iin.isdigit(), "IIN must be numeric"

        # Version must be '10' for AAMVA 2020
        version = barcode[15:17]
        assert version == '10', "Version must be '10' for DL/ID-2020"
```

### 2. Fuzzing for Security

```python
# tests/security/test_barcode_fuzzing.py

import pytest
import atheris
import sys

from src.core.barcode_formatter import format_barcode_data


def test_barcode_formatter_fuzzing():
    """Fuzz barcode formatter with random inputs"""

    @atheris.instrument_func
    def fuzz_barcode_formatter(data):
        """Fuzz target for barcode formatter"""
        try:
            # Create pseudo-random license data
            fdp = atheris.FuzzedDataProvider(data)

            license_data = [{
                'subfile_type': 'DL',
                'DAQ': fdp.ConsumeUnicode(20),
                'DCS': fdp.ConsumeUnicode(30),
                'DAC': fdp.ConsumeUnicode(30),
                'DAJ': fdp.ConsumeUnicode(2),
                # ... more fields
            }]

            # Should not crash
            result = format_barcode_data(license_data)

        except (ValueError, KeyError, TypeError):
            # Expected exceptions are OK
            pass
        except Exception as e:
            # Unexpected exception - report
            print(f"Unexpected exception: {e}")
            raise

    # Run fuzzer
    atheris.Setup(sys.argv, fuzz_barcode_formatter)
    atheris.Fuzz()
```

### 3. Metamorphic Testing

```python
# tests/property/test_metamorphic.py

import pytest
from hypothesis import given, strategies as st

from src.core.license_generator import generate_license_data
from src.core.barcode_formatter import format_barcode_data


class TestMetamorphicProperties:
    """Metamorphic testing: relationships between test executions"""

    @given(state=st.sampled_from(['CA', 'NY', 'TX']))
    def test_determinism_property(self, state):
        """Property: Same seed → same output"""
        import random

        random.seed(42)
        result1 = generate_license_data(state)

        random.seed(42)
        result2 = generate_license_data(state)

        # Metamorphic relation: f(x, seed=s) = f(x, seed=s)
        assert result1 == result2

    def test_encoding_length_monotonicity(self):
        """Property: More data → longer encoding"""
        # Generate minimal license
        minimal = generate_license_data('CA')
        minimal[0]['DAG'] = 'A'  # Short address

        # Generate maximal license
        maximal = generate_license_data('CA')
        maximal[0]['DAG'] = 'A' * 100  # Long address

        minimal_encoded = format_barcode_data(minimal)
        maximal_encoded = format_barcode_data(maximal)

        # Metamorphic relation: more data → longer encoding
        assert len(maximal_encoded) > len(minimal_encoded)
```

### 4. Chaos Engineering for Robustness

```python
# tests/chaos/test_failure_scenarios.py

import pytest
import random
from unittest.mock import patch

from src.core.license_generator import generate_license_data


class TestChaosScenarios:
    """Chaos engineering: inject failures randomly"""

    def test_survives_random_none_returns(self, monkeypatch):
        """System should handle random None returns gracefully"""
        original_random_choice = random.choice

        def chaos_choice(seq):
            if random.random() < 0.1:  # 10% failure rate
                return None
            return original_random_choice(seq)

        monkeypatch.setattr(random, 'choice', chaos_choice)

        # Should either succeed or raise ValueError (not crash)
        try:
            result = generate_license_data('CA')
            assert result is not None
        except (ValueError, TypeError, AttributeError):
            # Expected error handling
            pass

    @patch('src.utils.file_io.open')
    def test_survives_filesystem_failures(self, mock_open):
        """System should handle random filesystem failures"""
        # Randomly fail file operations
        def chaos_open(*args, **kwargs):
            if random.random() < 0.2:  # 20% failure
                raise OSError("Simulated disk failure")
            return mock_open.return_value

        mock_open.side_effect = chaos_open

        # Should handle gracefully
        from src.utils.file_io import save_barcode

        try:
            save_barcode("data", "/tmp/test.txt")
        except OSError:
            # Expected
            pass
```

---

## 16. Test Maintenance Guidelines

### Test Code Quality Standards

1. **Tests are first-class code:**
   - Same quality standards as production code
   - Reviewed like production code
   - Refactored regularly

2. **DRY in tests:**
   - Use fixtures for common setup
   - Extract helper functions
   - Avoid copy-paste test code

3. **Test naming:**
   ```python
   # ✅ Good
   def test_california_license_number_has_eight_characters():
       pass

   # ❌ Bad
   def test_ca():
       pass
   ```

4. **One assertion per test (guideline, not rule):**
   - Prefer focused tests
   - Group related assertions
   - Use `pytest.mark.parametrize` for variations

### Dealing with Flaky Tests

```python
# Mark flaky tests for retry
@pytest.mark.flaky(reruns=3, reruns_delay=1)
def test_sometimes_fails_due_to_timing():
    pass

# Quarantine unstable tests
@pytest.mark.quarantine
def test_needs_investigation():
    pass

# Run quarantined tests separately
pytest -m quarantine
```

---

## Conclusion

This testing strategy represents a **paradigm shift** from typical software testing:

### Traditional Approach vs. This Strategy

| Aspect | Traditional | This Strategy |
|--------|-------------|---------------|
| Coverage target | 70-80% | 95%+ |
| Test quality validation | None | Mutation testing (80%+ score) |
| Visual testing | Manual review | Automated pixel-perfect comparison |
| Accessibility | Afterthought | First-class requirement (WCAG 2.1 AA) |
| Performance | Ad-hoc benchmarks | Integrated benchmarking in CI/CD |
| Property testing | Rare | Standard practice (Hypothesis) |
| Security testing | Separate audit | Continuous fuzzing |
| Test organization | tests/ folder | Structured by type (8+ categories) |

### Implementation Roadmap

**Phase 1 (Weeks 1-2): Foundation**
- Set up test infrastructure
- Configure pytest, coverage, CI/CD
- Write first 50 unit tests

**Phase 2 (Weeks 3-4): Core Testing**
- Complete unit test coverage (95%+)
- Implement integration tests
- Set up visual regression baseline

**Phase 3 (Weeks 5-6): Advanced Testing**
- Property-based testing with Hypothesis
- Mutation testing setup
- Performance benchmarking

**Phase 4 (Weeks 7-8): Specialized Testing**
- Accessibility testing
- Security fuzzing
- Cross-platform testing

**Phase 5 (Ongoing): Maintenance**
- Update baselines
- Refactor tests
- Monitor mutation scores

### Success Metrics

Track these metrics weekly:

```python
# scripts/test_metrics.py

def calculate_test_metrics():
    return {
        'line_coverage': 95.8,          # Target: 95%+
        'branch_coverage': 92.3,        # Target: 90%+
        'mutation_score': 83.1,         # Target: 80%+
        'avg_test_speed': 0.003,        # seconds, Target: <0.01s
        'flaky_test_rate': 0.5,         # %, Target: <1%
        'visual_regression_diffs': 0,   # Target: 0
        'accessibility_violations': 0,   # Target: 0
        'performance_regressions': 0     # Target: 0
    }
```

---

**This testing strategy ensures that every feature is tested comprehensively BEFORE implementation, creating a robust, maintainable, and high-quality codebase that exceeds industry standards.**
