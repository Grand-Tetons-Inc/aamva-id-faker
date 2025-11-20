"""
Unit tests for validation logic.

These tests validate data validation functions used to ensure
license data conforms to AAMVA standards and real-world constraints.

TDD RED phase - tests written before implementation.
"""

import pytest
from datetime import datetime, timedelta
from hypothesis import given, strategies as st, settings

# Import will fail initially (TDD RED phase)
# from src.core.validators import (
#     validate_license_data,
#     validate_date_format,
#     validate_date_logic,
#     validate_state_code,
#     validate_license_number_format,
#     validate_physical_characteristics,
#     validate_aamva_compliance,
#     is_valid_eye_color,
#     is_valid_hair_color,
#     is_valid_sex_code,
#     is_leap_year,
#     calculate_age
# )

pytestmark = pytest.mark.unit


class TestDateFormatValidation:
    """Tests for AAMVA date format validation (MMDDYYYY)."""

    def test_valid_date_format_accepted(self):
        """Valid MMDDYYYY dates should pass validation."""
        from src.core.validators import validate_date_format

        valid_dates = [
            '01012025',  # Jan 1, 2025
            '12312024',  # Dec 31, 2024
            '06152023',  # Jun 15, 2023
            '02292024',  # Leap day 2024
        ]

        for date_str in valid_dates:
            assert validate_date_format(date_str) is True, \
                f"Date {date_str} should be valid"

    def test_invalid_date_format_rejected(self):
        """Invalid date formats should fail validation."""
        from src.core.validators import validate_date_format

        invalid_dates = [
            '2025-01-01',  # Wrong format (YYYY-MM-DD)
            '01/01/2025',  # Has slashes
            '010125',      # Only 6 digits
            '0101202',     # Only 7 digits
            '010120255',   # 9 digits
            'abcd2025',    # Contains letters
            '',            # Empty string
            '13012025',    # Invalid month (13)
            '00012025',    # Invalid month (00)
            '01322025',    # Invalid day (32)
            '02302023',    # Feb 30 doesn't exist
        ]

        for date_str in invalid_dates:
            assert validate_date_format(date_str) is False, \
                f"Date {date_str} should be invalid"

    def test_leap_year_feb_29_valid(self):
        """Feb 29 should be valid in leap years."""
        from src.core.validators import validate_date_format

        assert validate_date_format('02292024') is True, "2024 is a leap year"
        assert validate_date_format('02292020') is True, "2020 is a leap year"

    def test_non_leap_year_feb_29_invalid(self):
        """Feb 29 should be invalid in non-leap years."""
        from src.core.validators import validate_date_format

        assert validate_date_format('02292023') is False, "2023 is not a leap year"
        assert validate_date_format('02292025') is False, "2025 is not a leap year"


class TestDateLogicValidation:
    """Tests for date logic validation (chronological ordering)."""

    def test_valid_date_sequence_accepted(self):
        """DOB < Issue < Expiration should pass."""
        from src.core.validators import validate_date_logic

        dob = '01011990'      # Jan 1, 1990
        issue = '11202025'    # Nov 20, 2025
        exp = '11202030'      # Nov 20, 2030

        assert validate_date_logic(dob, issue, exp) is True

    def test_birth_after_issue_rejected(self):
        """Birth date after issue date should fail."""
        from src.core.validators import validate_date_logic

        dob = '01012026'      # Born in 2026
        issue = '11202025'    # Issued in 2025 (before birth!)
        exp = '11202030'

        assert validate_date_logic(dob, issue, exp) is False

    def test_issue_after_expiration_rejected(self):
        """Issue date after expiration should fail."""
        from src.core.validators import validate_date_logic

        dob = '01011990'
        issue = '11202030'    # Issued in 2030
        exp = '11202025'      # Expires in 2025 (before issue!)

        assert validate_date_logic(dob, issue, exp) is False

    def test_minimum_age_16_enforced(self):
        """Driver must be at least 16 at issue date."""
        from src.core.validators import validate_date_logic

        # 15 years old at issue
        dob = '11212010'
        issue = '11202025'    # Exactly 15 years minus 1 day
        exp = '11202030'

        assert validate_date_logic(dob, issue, exp) is False

    def test_age_16_exactly_accepted(self):
        """Exactly 16 years old should be valid."""
        from src.core.validators import validate_date_logic

        dob = '11202009'      # Born Nov 20, 2009
        issue = '11202025'    # Issued Nov 20, 2025 (16th birthday)
        exp = '11202030'

        assert validate_date_logic(dob, issue, exp) is True


class TestStateCodeValidation:
    """Tests for state code validation."""

    def test_valid_state_codes_accepted(self, valid_state_codes):
        """All 50 states + DC should be valid."""
        from src.core.validators import validate_state_code

        for state in valid_state_codes:
            assert validate_state_code(state) is True, \
                f"State {state} should be valid"

    def test_lowercase_state_codes_accepted(self):
        """Lowercase state codes should be accepted."""
        from src.core.validators import validate_state_code

        assert validate_state_code('ca') is True
        assert validate_state_code('ny') is True
        assert validate_state_code('tx') is True

    def test_invalid_state_codes_rejected(self, invalid_state_codes):
        """Invalid state codes should be rejected."""
        from src.core.validators import validate_state_code

        for invalid_state in invalid_state_codes:
            if invalid_state is None:
                continue
            assert validate_state_code(invalid_state) is False, \
                f"State '{invalid_state}' should be invalid"


class TestLicenseNumberFormatValidation:
    """Tests for state-specific license number format validation."""

    def test_california_valid_format(self):
        """California: 1 letter + 7 digits."""
        from src.core.validators import validate_license_number_format

        valid_ca = [
            'A1234567',
            'Z9876543',
            'M5555555',
        ]

        for license_num in valid_ca:
            assert validate_license_number_format(license_num, 'CA') is True, \
                f"CA license {license_num} should be valid"

    def test_california_invalid_format(self):
        """Invalid California license numbers."""
        from src.core.validators import validate_license_number_format

        invalid_ca = [
            '12345678',    # All digits (no letter)
            'AB123456',    # Two letters
            'A123456',     # Only 6 digits
            'A12345678',   # 8 digits
            'a1234567',    # Lowercase
            '1A234567',    # Letter not first
        ]

        for license_num in invalid_ca:
            assert validate_license_number_format(license_num, 'CA') is False, \
                f"CA license {license_num} should be invalid"

    def test_texas_valid_format(self):
        """Texas: 8 digits."""
        from src.core.validators import validate_license_number_format

        valid_tx = [
            '12345678',
            '00000001',
            '99999999',
        ]

        for license_num in valid_tx:
            assert validate_license_number_format(license_num, 'TX') is True

    def test_texas_invalid_format(self):
        """Invalid Texas license numbers."""
        from src.core.validators import validate_license_number_format

        invalid_tx = [
            'A1234567',    # Has letter
            '1234567',     # Only 7 digits
            '123456789',   # 9 digits
        ]

        for license_num in invalid_tx:
            assert validate_license_number_format(license_num, 'TX') is False

    def test_florida_valid_format(self):
        """Florida: 1 letter + 12 digits."""
        from src.core.validators import validate_license_number_format

        valid_fl = [
            'A123456789012',
            'Z999999999999',
        ]

        for license_num in valid_fl:
            assert validate_license_number_format(license_num, 'FL') is True

    def test_new_york_valid_format(self):
        """New York: 1 letter + 7-18 digits."""
        from src.core.validators import validate_license_number_format

        valid_ny = [
            'A1234567',        # 7 digits (min)
            'A12345678',       # 8 digits
            'A123456789012345678',  # 18 digits (max)
        ]

        for license_num in valid_ny:
            assert validate_license_number_format(license_num, 'NY') is True


class TestPhysicalCharacteristicsValidation:
    """Tests for physical characteristic validation."""

    def test_valid_eye_colors(self, valid_eye_colors):
        """AAMVA standard eye colors should be valid."""
        from src.core.validators import is_valid_eye_color

        for color in valid_eye_colors:
            assert is_valid_eye_color(color) is True, \
                f"Eye color {color} should be valid"

    def test_invalid_eye_colors(self):
        """Non-standard eye colors should be invalid."""
        from src.core.validators import is_valid_eye_color

        invalid_colors = ['RED', 'YEL', 'WHT', 'XXX', '', '123']

        for color in invalid_colors:
            assert is_valid_eye_color(color) is False

    def test_valid_hair_colors(self, valid_hair_colors):
        """AAMVA standard hair colors should be valid."""
        from src.core.validators import is_valid_hair_color

        for color in valid_hair_colors:
            assert is_valid_hair_color(color) is True

    def test_invalid_hair_colors(self):
        """Non-standard hair colors should be invalid."""
        from src.core.validators import is_valid_hair_color

        invalid_colors = ['BLK', 'PUR', 'XXX', '', '123']

        for color in invalid_colors:
            assert is_valid_hair_color(color) is False

    def test_valid_sex_codes(self, valid_sex_codes):
        """AAMVA sex codes (1, 2, 9) should be valid."""
        from src.core.validators import is_valid_sex_code

        for code in valid_sex_codes:
            assert is_valid_sex_code(code) is True

    def test_invalid_sex_codes(self):
        """Invalid sex codes should be rejected."""
        from src.core.validators import is_valid_sex_code

        invalid_codes = ['0', '3', 'M', 'F', 'X', '', 'male']

        for code in invalid_codes:
            assert is_valid_sex_code(code) is False

    def test_height_valid_range(self):
        """Height validation (58-78 inches)."""
        from src.core.validators import validate_physical_characteristics

        # Valid heights
        for height in range(58, 79):
            assert validate_physical_characteristics(height=height) is True

    def test_height_invalid_range(self):
        """Heights outside 58-78 should be invalid."""
        from src.core.validators import validate_physical_characteristics

        invalid_heights = [30, 50, 57, 79, 100, 200]

        for height in invalid_heights:
            assert validate_physical_characteristics(height=height) is False

    def test_weight_valid_range(self):
        """Weight validation (100-300 lbs)."""
        from src.core.validators import validate_physical_characteristics

        # Valid weights
        for weight in [100, 150, 200, 250, 300]:
            assert validate_physical_characteristics(weight=weight) is True

    def test_weight_invalid_range(self):
        """Weights outside 100-300 should be invalid."""
        from src.core.validators import validate_physical_characteristics

        invalid_weights = [50, 99, 301, 400, 1000]

        for weight in invalid_weights:
            assert validate_physical_characteristics(weight=weight) is False


class TestAAMVAComplianceValidation:
    """Tests for overall AAMVA specification compliance."""

    def test_all_required_fields_present(self, sample_california_license, aamva_required_fields):
        """Validate that all required AAMVA fields are present."""
        from src.core.validators import validate_aamva_compliance

        dl_subfile = sample_california_license[0]

        result = validate_aamva_compliance(dl_subfile)

        assert result is True, "Valid license should pass AAMVA compliance"

    def test_missing_required_field_fails(self, sample_california_license):
        """License missing required field should fail validation."""
        from src.core.validators import validate_aamva_compliance

        dl_subfile = sample_california_license[0].copy()
        del dl_subfile['DAQ']  # Remove license number

        result = validate_aamva_compliance(dl_subfile)

        assert result is False, "Missing DAQ should fail validation"

    def test_empty_required_field_fails(self, sample_california_license):
        """Empty required field should fail validation."""
        from src.core.validators import validate_aamva_compliance

        dl_subfile = sample_california_license[0].copy()
        dl_subfile['DCS'] = ''  # Empty last name

        result = validate_aamva_compliance(dl_subfile)

        assert result is False, "Empty last name should fail validation"


class TestUtilityFunctions:
    """Tests for utility validation functions."""

    def test_is_leap_year_true(self):
        """Leap years should be detected correctly."""
        from src.core.validators import is_leap_year

        leap_years = [2000, 2004, 2008, 2012, 2016, 2020, 2024, 2028]

        for year in leap_years:
            assert is_leap_year(year) is True, f"{year} should be a leap year"

    def test_is_leap_year_false(self):
        """Non-leap years should be detected correctly."""
        from src.core.validators import is_leap_year

        non_leap_years = [1900, 2001, 2002, 2003, 2005, 2100, 2023, 2025]

        for year in non_leap_years:
            assert is_leap_year(year) is False, f"{year} should NOT be a leap year"

    def test_calculate_age_accurate(self):
        """Age calculation should be accurate."""
        from src.core.validators import calculate_age

        dob = datetime(1990, 1, 1)
        current = datetime(2025, 1, 1)

        age = calculate_age(dob, current)

        assert age == 35, "Age should be exactly 35 years"

    def test_calculate_age_before_birthday(self):
        """Age before birthday should be one less."""
        from src.core.validators import calculate_age

        dob = datetime(1990, 12, 31)
        current = datetime(2025, 1, 1)  # 1 day before 35th birthday

        age = calculate_age(dob, current)

        assert age == 34, "Age should be 34 (birthday not reached yet)"

    def test_calculate_age_on_birthday(self):
        """Age on birthday should increment."""
        from src.core.validators import calculate_age

        dob = datetime(1990, 11, 20)
        current = datetime(2025, 11, 20)  # Exactly 35th birthday

        age = calculate_age(dob, current)

        assert age == 35, "Age should be 35 on birthday"


class TestFullLicenseValidation:
    """Tests for validating complete license data structures."""

    def test_valid_complete_license_passes(self, sample_california_license):
        """Complete valid license should pass all validations."""
        from src.core.validators import validate_license_data

        result = validate_license_data(sample_california_license)

        assert result['valid'] is True, "Valid license should pass"
        assert len(result.get('errors', [])) == 0, "Should have no errors"

    def test_invalid_license_returns_errors(self):
        """Invalid license should return detailed error messages."""
        from src.core.validators import validate_license_data

        invalid_license = [
            {
                'subfile_type': 'DL',
                'DAQ': '123',  # Too short
                'DCS': '',     # Empty last name
                'DAC': 'john', # Lowercase
                'DBB': '13012025',  # Invalid date
                'DBA': '01012020',  # Expiration before issue
                'DBD': '01012025',
                'DAJ': 'ZZ',   # Invalid state
                'DBC': '5',    # Invalid sex code
                'DAY': 'RED',  # Invalid eye color
            }
        ]

        result = validate_license_data(invalid_license)

        assert result['valid'] is False
        assert len(result['errors']) > 0
        assert 'license_number' in str(result['errors']).lower()


# ============================================================================
# PROPERTY-BASED TESTS
# ============================================================================

class TestPropertyBasedValidation:
    """Property-based tests for validators."""

    @given(year=st.integers(min_value=1900, max_value=2100))
    @settings(max_examples=50)
    def test_property_leap_year_consistency(self, year):
        """Property: Leap year detection is consistent."""
        from src.core.validators import is_leap_year

        # Leap year rules
        expected = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

        assert is_leap_year(year) == expected

    @given(
        month=st.integers(min_value=1, max_value=12),
        day=st.integers(min_value=1, max_value=28),  # Safe for all months
        year=st.integers(min_value=1920, max_value=2099)
    )
    @settings(max_examples=50)
    def test_property_valid_dates_accepted(self, month, day, year):
        """Property: Valid dates are always accepted."""
        from src.core.validators import validate_date_format

        date_str = f"{month:02d}{day:02d}{year}"

        assert validate_date_format(date_str) is True


# ============================================================================
# PARAMETRIZED TESTS
# ============================================================================

class TestParametrizedValidation:
    """Parametrized validation tests."""

    @pytest.mark.parametrize("state,license_num", [
        ('CA', 'A1234567'),
        ('TX', '12345678'),
        ('FL', 'A123456789012'),
        ('NY', 'A123456789'),
    ])
    def test_valid_license_formats_for_states(self, state, license_num):
        """Test valid license formats for multiple states."""
        from src.core.validators import validate_license_number_format

        assert validate_license_number_format(license_num, state) is True

    @pytest.mark.parametrize("height", [58, 60, 65, 70, 75, 78])
    def test_boundary_heights_valid(self, height):
        """Test boundary and midpoint heights."""
        from src.core.validators import validate_physical_characteristics

        assert validate_physical_characteristics(height=height) is True

    @pytest.mark.parametrize("weight", [100, 150, 200, 250, 300])
    def test_boundary_weights_valid(self, weight):
        """Test boundary and midpoint weights."""
        from src.core.validators import validate_physical_characteristics

        assert validate_physical_characteristics(weight=weight) is True
