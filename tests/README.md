# AAMVA ID Faker - Test Suite

## Overview

This test suite implements **Test-Driven Development (TDD)** practices with **95%+ code coverage** requirements and innovative testing approaches including:

- Property-based testing with Hypothesis
- Mutation testing for test quality validation
- Visual regression testing
- Accessibility testing (WCAG 2.1 AA)
- Performance benchmarking
- Contract testing for AAMVA spec compliance

## Test Structure

```
tests/
├── unit/                   # Unit tests (isolated, fast)
│   ├── test_generators.py  # License generation tests
│   ├── test_validators.py  # Validation logic tests
│   └── test_formatters.py  # Barcode formatting tests
├── integration/            # Integration tests (multiple components)
├── gui/                    # GUI component tests
├── e2e/                    # End-to-end workflow tests
├── visual/                 # Visual regression tests
├── accessibility/          # Accessibility tests
├── performance/            # Performance benchmarks
├── contract/               # AAMVA spec compliance tests
├── security/               # Security/fuzzing tests
├── property/               # Property-based tests (Hypothesis)
│   └── test_properties.py  # Generative tests
├── fixtures/               # Test data fixtures
├── utils/                  # Test utilities
│   └── assertions.py       # Custom assertions
├── conftest.py             # Shared fixtures
└── README.md               # This file
```

## Installation

### 1. Install Test Dependencies

```bash
# From project root
pip install -r requirements-test.txt
```

### 2. Verify Installation

```bash
pytest --version
```

## Running Tests

### Run All Tests

```bash
# Run complete test suite
pytest

# Run with coverage report
pytest --cov=src --cov-report=html --cov-report=term

# Fail if coverage < 95%
pytest --cov=src --cov-fail-under=95
```

### Run Specific Test Categories

```bash
# Unit tests only (fast)
pytest tests/unit/ -v

# Property-based tests
pytest tests/property/ -v

# Integration tests
pytest tests/integration/ -v

# Specific test file
pytest tests/unit/test_generators.py -v

# Specific test class
pytest tests/unit/test_generators.py::TestLicenseDataStructure -v

# Specific test function
pytest tests/unit/test_generators.py::TestLicenseDataStructure::test_returns_list_with_two_subfiles -v
```

### Run Tests by Marker

```bash
# Unit tests only
pytest -m unit

# Slow tests
pytest -m slow

# Property-based tests
pytest -m property

# Skip slow tests
pytest -m "not slow"
```

### Run Tests in Parallel

```bash
# Use all available CPU cores
pytest -n auto

# Use 4 workers
pytest -n 4
```

## TDD Workflow

### RED Phase (Current Phase)

All tests are currently **FAILING** because implementation doesn't exist yet. This is intentional and correct for TDD.

```bash
# Run tests to see failures
pytest tests/unit/test_generators.py -v

# Expected output: All tests FAIL with import errors
# This is CORRECT for TDD RED phase
```

### GREEN Phase (Next)

1. Implement minimal code to make tests pass
2. Run tests until they pass
3. Commit with message: "GREEN: Implement [feature]"

```bash
# Create implementation
# src/core/license_generator.py

# Run tests
pytest tests/unit/test_generators.py -v

# Expected: Tests should PASS
```

### REFACTOR Phase

1. Improve code quality
2. Ensure tests still pass
3. Commit with message: "REFACTOR: Clean up [feature]"

## Test Coverage

### View Coverage Report

```bash
# Generate HTML coverage report
pytest --cov=src --cov-report=html

# Open in browser
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Coverage Requirements

| Metric | Target | Current |
|--------|--------|---------|
| Line Coverage | 95%+ | 0% (no implementation yet) |
| Branch Coverage | 90%+ | 0% |
| Mutation Score | 80%+ | N/A |

## Property-Based Testing

Property-based tests use Hypothesis to generate hundreds of test cases automatically.

```bash
# Run property tests
pytest tests/property/ -v

# Run with more examples
pytest tests/property/ -v --hypothesis-max-examples=1000
```

### Example Property Test

```python
@given(state=st.sampled_from(['CA', 'NY', 'TX']))
def test_any_state_produces_valid_structure(state):
    """Property: Any state produces 2 subfiles."""
    result = generate_license_data(state)
    assert len(result) == 2
```

This test will run with multiple state values automatically.

## Mutation Testing (Advanced)

Mutation testing validates that tests actually catch bugs.

```bash
# Install mutmut
pip install mutmut

# Run mutation testing
mutmut run --paths-to-mutate=src/

# View results
mutmut results

# Show specific mutation
mutmut show 1

# HTML report
mutmut html
```

## Performance Benchmarking

```bash
# Run performance tests
pytest tests/performance/ -v

# Run only benchmarks
pytest --benchmark-only

# Compare with baseline
pytest --benchmark-compare
```

## Continuous Integration

Tests are designed to run in CI/CD pipelines:

```bash
# CI-friendly format
pytest -v --tb=short --cov=src --cov-report=xml --junitxml=junit.xml

# Strict mode (fail on warnings)
pytest --strict-markers --strict-config
```

## Test Data

### Fixtures

Shared test data is defined in `conftest.py`:

```python
# Use fixture in test
def test_something(sample_california_license):
    # sample_california_license is automatically injected
    assert sample_california_license[0]['DAJ'] == 'CA'
```

### Custom Assertions

Use custom assertions from `tests/utils/assertions.py`:

```python
from tests.utils.assertions import assert_aamva_compliant

def test_license_compliance():
    data = generate_license_data('CA')
    assert_aamva_compliant(data)  # Custom assertion
```

## Debugging Tests

### Verbose Output

```bash
# Show print statements
pytest -s

# Extra verbose
pytest -vv

# Show local variables on failure
pytest --showlocals
```

### Debug Specific Test

```bash
# Stop on first failure
pytest -x

# Drop into debugger on failure
pytest --pdb

# Drop into debugger at test start
pytest --trace
```

### Filter Warnings

```bash
# Show all warnings
pytest -W default

# Treat warnings as errors
pytest -W error
```

## Writing New Tests

### Test Naming Convention

```python
# ✅ GOOD - Descriptive test names
def test_california_license_number_has_eight_characters():
    pass

def test_barcode_encoding_with_unicode_raises_error():
    pass

# ❌ BAD - Vague test names
def test_license():
    pass

def test_1():
    pass
```

### Test Organization

```python
class TestFeatureName:
    """Tests for specific feature."""

    def test_happy_path(self):
        """Test normal operation."""
        pass

    def test_edge_case_empty_input(self):
        """Test edge case."""
        pass

    def test_error_handling_invalid_input(self):
        """Test error conditions."""
        pass
```

### Using Parametrize

```python
@pytest.mark.parametrize("state,expected_length", [
    ('CA', 8),
    ('TX', 8),
    ('FL', 13),
])
def test_license_number_length(state, expected_length):
    result = generate_license_data(state)
    assert len(result[0]['DAQ']) == expected_length
```

## Common Issues

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'src'`

**Solution:** Tests currently fail with import errors - this is CORRECT for TDD RED phase. Implement the code to fix.

### Slow Tests

**Problem:** Tests take too long

**Solutions:**
```bash
# Run in parallel
pytest -n auto

# Skip slow tests
pytest -m "not slow"

# Show slowest tests
pytest --durations=10
```

### Flaky Tests

**Problem:** Tests fail randomly

**Solution:** Mark as flaky for investigation
```python
@pytest.mark.flaky(reruns=3)
def test_sometimes_fails():
    pass
```

## Best Practices

1. **Write tests BEFORE implementation** (TDD)
2. **One assertion per test** (guideline, not rule)
3. **Descriptive test names** that explain what is being tested
4. **Use fixtures** for common setup
5. **Test edge cases** and error conditions
6. **Keep tests fast** (<1ms for unit tests)
7. **Tests should be independent** (can run in any order)
8. **Use property-based testing** for comprehensive coverage

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Hypothesis Documentation](https://hypothesis.readthedocs.io/)
- [TDD Best Practices](https://martinfowler.com/bliki/TestDrivenDevelopment.html)
- [AAMVA DL/ID Card Design Standard](https://www.aamva.org/)

## Getting Help

- Check test output: `pytest -v --tb=short`
- View coverage: `pytest --cov=src --cov-report=html`
- Run specific test: `pytest tests/unit/test_generators.py::test_name -v`
- Debug test: `pytest --pdb`

---

**Current Status:** 🔴 RED Phase (tests failing - implementation needed)

**Next Step:** Implement `src/core/license_generator.py` to make tests pass (GREEN phase)
