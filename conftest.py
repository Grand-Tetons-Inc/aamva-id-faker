"""
Pytest configuration and shared fixtures for AAMVA ID Faker test suite.

This module provides:
- Common test fixtures
- Test data factories
- Mock builders
- Parametrized test data
- Hypothesis strategies
"""

import pytest
import random
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any
from faker import Faker
from hypothesis import strategies as st


# ============================================================================
# PYTEST CONFIGURATION HOOKS
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom settings."""
    # Register custom markers (already in pytest.ini, but explicit is good)
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "slow: Slow running tests")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Auto-mark based on path
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
        elif "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)
        elif "property" in str(item.fspath):
            item.add_marker(pytest.mark.property)


# ============================================================================
# BASIC FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def faker_instance():
    """Provide a Faker instance for generating test data."""
    fake = Faker()
    Faker.seed(42)  # Deterministic for reproducibility
    return fake


@pytest.fixture
def faker_seed():
    """Reset Faker seed before each test for deterministic results."""
    Faker.seed(12345)
    random.seed(12345)
    fake = Faker()
    return fake


@pytest.fixture
def random_seed():
    """Reset random seed for deterministic testing."""
    random.seed(42)
    return 42


# ============================================================================
# FILE SYSTEM FIXTURES
# ============================================================================

@pytest.fixture
def temp_dir():
    """Provide a temporary directory that's cleaned up after test."""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def temp_output_dir(temp_dir):
    """Provide temporary output directory structure."""
    output_dir = temp_dir / "output"
    output_dir.mkdir()
    (output_dir / "barcodes").mkdir()
    (output_dir / "data").mkdir()
    (output_dir / "images").mkdir()
    return output_dir


@pytest.fixture
def project_root():
    """Return the project root directory."""
    return Path(__file__).parent


@pytest.fixture
def tests_dir(project_root):
    """Return the tests directory."""
    return project_root / "tests"


# ============================================================================
# STATE AND IIN FIXTURES
# ============================================================================

@pytest.fixture
def valid_state_codes():
    """List of valid US state codes."""
    return [
        'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
        'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
        'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
        'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
        'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY',
        'DC'  # District of Columbia
    ]


@pytest.fixture
def california_iin():
    """California's official IIN (Issuer Identification Number)."""
    return "636014"


@pytest.fixture
def new_york_iin():
    """New York's official IIN."""
    return "636001"


@pytest.fixture
def test_iins():
    """Mapping of states to IINs for testing."""
    return {
        'CA': '636014',
        'NY': '636001',
        'TX': '636015',
        'FL': '636010',
        'WA': '636045',
        'IL': '636035',
        'PA': '636025',
        'AZ': '636026',
    }


# ============================================================================
# AAMVA FIELD DATA FIXTURES
# ============================================================================

@pytest.fixture
def valid_eye_colors():
    """Valid AAMVA eye color codes."""
    return ['BLK', 'BLU', 'BRO', 'GRY', 'GRN', 'HAZ', 'MAR', 'PNK', 'DIC', 'UNK']


@pytest.fixture
def valid_hair_colors():
    """Valid AAMVA hair color codes."""
    return ['BLK', 'BLN', 'BRO', 'GRY', 'RED', 'WHI', 'SDY', 'UNK', 'BAL']


@pytest.fixture
def valid_sex_codes():
    """Valid AAMVA sex codes."""
    return ['1', '2', '9']  # 1=Male, 2=Female, 9=Not specified


@pytest.fixture
def aamva_required_fields():
    """List of required AAMVA DL subfile fields."""
    return [
        'DAQ',  # Customer ID Number (License Number)
        'DCS',  # Last Name
        'DAC',  # First Name
        'DBB',  # Date of Birth
        'DBA',  # Expiration Date
        'DBD',  # Issue Date
        'DAG',  # Street Address
        'DAI',  # City
        'DAJ',  # State
        'DAK',  # Zip Code
        'DBC',  # Sex
        'DAY',  # Eye Color
        'DAU',  # Height
    ]


# ============================================================================
# SAMPLE LICENSE DATA FIXTURES
# ============================================================================

@pytest.fixture
def sample_california_license():
    """Fixed California license data for deterministic testing."""
    return [
        {
            "subfile_type": "DL",
            "DAQ": "A1234567",  # License number
            "DCA": "D",  # Class
            "DCB": "",  # Restrictions
            "DCD": "",  # Endorsements
            "DBA": "08142032",  # Expiration date
            "DCS": "DOE",  # Last name
            "DAC": "JOHN",  # First name
            "DAD": "MICHAEL",  # Middle name
            "DBD": "11202025",  # Issue date
            "DBB": "05151990",  # Date of birth
            "DBC": "1",  # Sex (1=Male)
            "DAY": "BRO",  # Eye color
            "DAU": "070",  # Height (inches)
            "DAW": "180",  # Weight (lbs)
            "DAZ": "BRO",  # Hair color
            "DCL": "W",  # Race
            "DAG": "123 MAIN STREET",  # Address
            "DAI": "LOS ANGELES",  # City
            "DAJ": "CA",  # State
            "DAK": "900120000",  # Zip code (9 digits)
            "DCF": "DOC12345",  # Document discriminator
            "DCG": "USA",  # Country
            "DDE": "N",  # Family name truncation
            "DDF": "N",  # First name truncation
            "DDG": "N",  # Middle name truncation
            "DDA": "F",  # Compliance type
            "DDB": "11202025",  # Card revision date
            "DDC": "",  # Hazmat endorsement expiration
            "DDD": "0",  # Limited duration
            "DDK": "1",  # Organ donor
            "DDL": "0"  # Veteran
        },
        {
            "subfile_type": "ZC",
            "ZCW": "ORANGE",  # Weight range code
            "ZCT": "TEST STRING",  # State-specific field
            "ZCX": "A123456"  # State-specific identifier
        }
    ]


@pytest.fixture
def sample_new_york_license(faker_seed):
    """Sample New York license data."""
    return [
        {
            "subfile_type": "DL",
            "DAQ": "A123456789012345",  # NY licenses can be very long
            "DCS": "SMITH",
            "DAC": "JANE",
            "DAD": "MARIE",
            "DBB": "03221985",
            "DBA": "03222033",
            "DBD": "11202025",
            "DBC": "2",  # Female
            "DAY": "BLU",
            "DAU": "064",
            "DAW": "135",
            "DAZ": "BLN",
            "DAG": "456 PARK AVENUE",
            "DAI": "NEW YORK",
            "DAJ": "NY",
            "DAK": "100010000",
            "DCF": "NY123456",
        },
        {
            "subfile_type": "ZN",
            "ZNT": "NY SPECIFIC DATA"
        }
    ]


# ============================================================================
# DATE FIXTURES
# ============================================================================

@pytest.fixture
def today():
    """Current date."""
    return datetime.now()


@pytest.fixture
def fixed_today():
    """Fixed date for deterministic testing."""
    return datetime(2025, 11, 20)


@pytest.fixture
def valid_dob(fixed_today):
    """Valid date of birth (21 years old)."""
    return fixed_today - timedelta(days=21*365)


@pytest.fixture
def valid_issue_date(fixed_today):
    """Valid issue date (today)."""
    return fixed_today


@pytest.fixture
def valid_expiration_date(fixed_today):
    """Valid expiration date (5 years from now)."""
    return fixed_today + timedelta(days=5*365)


# ============================================================================
# MOCK AND STUB FIXTURES
# ============================================================================

@pytest.fixture
def mock_random_seed(monkeypatch):
    """Mock random.seed to ensure deterministic behavior."""
    def mock_seed(value):
        random.seed(42)
    monkeypatch.setattr(random, 'seed', mock_seed)


# ============================================================================
# HYPOTHESIS STRATEGIES (Property-Based Testing)
# ============================================================================

@pytest.fixture
def state_code_strategy():
    """Hypothesis strategy for state codes."""
    return st.sampled_from([
        'CA', 'NY', 'TX', 'FL', 'WA', 'IL', 'PA', 'OH',
        'GA', 'NC', 'MI', 'NJ', 'VA', 'AZ', 'MA', 'CO'
    ])


@pytest.fixture
def date_strategy():
    """Hypothesis strategy for dates."""
    return st.dates(
        min_value=datetime(1920, 1, 1).date(),
        max_value=datetime(2025, 12, 31).date()
    )


@pytest.fixture
def name_strategy():
    """Hypothesis strategy for names."""
    return st.text(
        alphabet=st.characters(whitelist_categories=('Lu',)),
        min_size=2,
        max_size=30
    )


# ============================================================================
# VALIDATION FIXTURES
# ============================================================================

@pytest.fixture
def valid_license_number_patterns():
    """Valid license number patterns by state."""
    return {
        'CA': r'^[A-Z]\d{7}$',  # 1 letter + 7 digits
        'NY': r'^[A-Z]\d{7,18}$',  # 1 letter + 7-18 digits
        'TX': r'^\d{8}$',  # 8 digits
        'FL': r'^[A-Z]\d{12}$',  # 1 letter + 12 digits
    }


# ============================================================================
# BARCODE FIXTURES
# ============================================================================

@pytest.fixture
def aamva_compliance_header():
    """AAMVA compliance header bytes."""
    return b"@\n\x1E\r"


@pytest.fixture
def aamva_version():
    """Current AAMVA version (2020 spec)."""
    return "10"


@pytest.fixture
def expected_barcode_structure():
    """Expected structure of AAMVA barcode."""
    return {
        'compliance_marker': '@',
        'line_feed': '\n',
        'record_separator': '\x1E',
        'carriage_return': '\r',
        'file_type': 'ANSI ',
        'version': '10',
        'subfile_count': '02'
    }


# ============================================================================
# PERFORMANCE FIXTURES
# ============================================================================

@pytest.fixture
def performance_thresholds():
    """Performance thresholds for various operations."""
    return {
        'single_license_generation': 0.01,  # 10ms
        'barcode_formatting': 0.005,  # 5ms
        'batch_100_generation': 1.0,  # 1 second
        'batch_1000_generation': 30.0,  # 30 seconds
    }


# ============================================================================
# ERROR TEST FIXTURES
# ============================================================================

@pytest.fixture
def invalid_state_codes():
    """Invalid state codes for error testing."""
    return ['ZZ', 'XX', '99', 'ABC', '', None, 123, 'INVALID']


@pytest.fixture
def edge_case_dates():
    """Edge case dates for testing."""
    return {
        'leap_day': datetime(2024, 2, 29),
        'y2k': datetime(2000, 1, 1),
        'far_future': datetime(2099, 12, 31),
        'early_date': datetime(1920, 1, 1),
    }


# ============================================================================
# VISUAL REGRESSION FIXTURES
# ============================================================================

@pytest.fixture
def visual_baseline_dir(tests_dir):
    """Directory for visual regression baselines."""
    baseline_dir = tests_dir / "visual" / "snapshots"
    baseline_dir.mkdir(parents=True, exist_ok=True)
    return baseline_dir


@pytest.fixture
def visual_diff_threshold():
    """Allowed percentage difference for visual regression tests."""
    return 0.1  # 0.1% difference allowed


# ============================================================================
# ACCESSIBILITY FIXTURES
# ============================================================================

@pytest.fixture
def wcag_aa_contrast_ratio():
    """Minimum contrast ratio for WCAG 2.1 AA compliance."""
    return 4.5


@pytest.fixture
def wcag_aaa_contrast_ratio():
    """Minimum contrast ratio for WCAG 2.1 AAA compliance."""
    return 7.0


# ============================================================================
# TEST DATA FACTORIES
# ============================================================================

class LicenseDataFactory:
    """Factory for creating test license data."""

    @staticmethod
    def create_minimal_license(state='CA'):
        """Create minimal valid license data."""
        return [{
            'subfile_type': 'DL',
            'DAQ': 'TEST123',
            'DCS': 'DOE',
            'DAC': 'JOHN',
            'DBB': '01011990',
            'DBA': '01012030',
            'DBD': '11202025',
            'DAJ': state,
        }]

    @staticmethod
    def create_maximal_license(state='CA'):
        """Create license data with all possible fields."""
        # This will be implemented as tests are written
        pass


@pytest.fixture
def license_factory():
    """Provide license data factory."""
    return LicenseDataFactory


# ============================================================================
# CLEANUP
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup_output_dirs():
    """Automatically cleanup test output directories after each test."""
    yield
    # Cleanup logic runs after test
    output_dir = Path("output")
    if output_dir.exists() and "test" in str(output_dir):
        shutil.rmtree(output_dir, ignore_errors=True)
