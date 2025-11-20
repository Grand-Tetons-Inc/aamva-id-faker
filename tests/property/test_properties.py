"""
Property-based tests using Hypothesis.

These tests generate hundreds of test cases automatically to find edge cases
that manual test writing might miss. This is an INNOVATIVE approach that goes
beyond traditional example-based testing.

TDD RED phase - tests will fail until implementation exists.
"""

import pytest
from datetime import datetime, timedelta
from hypothesis import given, strategies as st, settings, assume, example
from hypothesis import Phase, HealthCheck
from string import ascii_uppercase, digits

# Imports will fail initially (TDD RED phase)
# from src.core.license_generator import generate_license_data
# from src.core.barcode_formatter import format_barcode_data
# from src.core.validators import (
#     validate_license_data,
#     validate_date_format,
#     is_leap_year
# )

pytestmark = pytest.mark.property


# ============================================================================
# CUSTOM HYPOTHESIS STRATEGIES
# ============================================================================

# Valid state codes
valid_states = st.sampled_from([
    'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
    'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
    'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
    'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
    'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY', 'DC'
])

# AAMVA date format (MMDDYYYY)
def aamva_dates():
    """Generate valid AAMVA format dates."""
    return st.dates(
        min_value=datetime(1920, 1, 1).date(),
        max_value=datetime(2099, 12, 31).date()
    ).map(lambda d: d.strftime('%m%d%Y'))

# License number patterns
def california_license_numbers():
    """Generate valid California license numbers."""
    return st.builds(
        lambda letter, num: f"{letter}{num:07d}",
        st.sampled_from(ascii_uppercase),
        st.integers(min_value=0, max_value=9999999)
    )

def texas_license_numbers():
    """Generate valid Texas license numbers."""
    return st.integers(min_value=10000000, max_value=99999999).map(str)

def florida_license_numbers():
    """Generate valid Florida license numbers."""
    return st.builds(
        lambda letter, num: f"{letter}{num:012d}",
        st.sampled_from(ascii_uppercase),
        st.integers(min_value=0, max_value=999999999999)
    )

# Physical characteristics
def valid_heights():
    """Generate valid heights (58-78 inches)."""
    return st.integers(min_value=58, max_value=78)

def valid_weights():
    """Generate valid weights (100-300 lbs)."""
    return st.integers(min_value=100, max_value=300)

def valid_eye_colors():
    """Generate valid AAMVA eye color codes."""
    return st.sampled_from(['BLK', 'BLU', 'BRO', 'GRY', 'GRN', 'HAZ', 'MAR', 'PNK', 'DIC', 'UNK'])

def valid_hair_colors():
    """Generate valid AAMVA hair color codes."""
    return st.sampled_from(['BLK', 'BLN', 'BRO', 'GRY', 'RED', 'WHI', 'SDY', 'UNK', 'BAL'])


# ============================================================================
# PROPERTY TESTS: LICENSE GENERATION
# ============================================================================

class TestLicenseGenerationProperties:
    """Property-based tests for license generation."""

    @given(state=valid_states)
    @settings(max_examples=100, deadline=None)
    def test_property_any_state_produces_two_subfiles(self, state):
        """Property: Every state produces exactly 2 subfiles."""
        from src.core.license_generator import generate_license_data

        result = generate_license_data(state)

        assert isinstance(result, list), "Result should be a list"
        assert len(result) == 2, f"Expected 2 subfiles, got {len(result)}"

    @given(state=valid_states)
    @settings(max_examples=100, deadline=None)
    def test_property_state_field_matches_input(self, state):
        """Property: DAJ field always matches requested state."""
        from src.core.license_generator import generate_license_data

        result = generate_license_data(state)

        assert result[0]['DAJ'] == state.upper(), \
            f"Expected state {state.upper()}, got {result[0]['DAJ']}"

    @given(state=valid_states)
    @settings(max_examples=100, deadline=None)
    def test_property_dates_chronologically_ordered(self, state):
        """Property: Birth < Issue < Expiration always holds."""
        from src.core.license_generator import generate_license_data

        result = generate_license_data(state)
        dl = result[0]

        dob = datetime.strptime(dl['DBB'], '%m%d%Y')
        issue = datetime.strptime(dl['DBD'], '%m%d%Y')
        exp = datetime.strptime(dl['DBA'], '%m%d%Y')

        assert dob < issue, "Birth date must be before issue date"
        assert issue < exp, "Issue date must be before expiration date"

    @given(state=valid_states)
    @settings(max_examples=100, deadline=None)
    def test_property_age_always_16_or_older(self, state):
        """Property: Driver is always at least 16 years old."""
        from src.core.license_generator import generate_license_data

        result = generate_license_data(state)
        dl = result[0]

        dob = datetime.strptime(dl['DBB'], '%m%d%Y')
        issue = datetime.strptime(dl['DBD'], '%m%d%Y')

        age_years = (issue - dob).days / 365.25

        assert age_years >= 16, f"Age {age_years:.1f} is below minimum 16"

    @given(state=valid_states)
    @settings(max_examples=100, deadline=None)
    def test_property_license_number_never_empty(self, state):
        """Property: License number (DAQ) is never empty."""
        from src.core.license_generator import generate_license_data

        result = generate_license_data(state)

        assert 'DAQ' in result[0], "DAQ field missing"
        assert len(result[0]['DAQ']) > 0, "License number is empty"

    @given(state=valid_states)
    @settings(max_examples=100, deadline=None)
    def test_property_names_always_uppercase(self, state):
        """Property: Name fields are always uppercase."""
        from src.core.license_generator import generate_license_data

        result = generate_license_data(state)
        dl = result[0]

        name_fields = ['DCS', 'DAC']  # Last name, First name
        if 'DAD' in dl and dl['DAD']:  # Middle name optional
            name_fields.append('DAD')

        for field in name_fields:
            name = dl[field]
            assert name == name.upper(), \
                f"Field {field} '{name}' is not uppercase"

    @given(state=valid_states)
    @settings(max_examples=50, deadline=None)
    def test_property_physical_characteristics_in_range(self, state):
        """Property: Physical characteristics are always in valid ranges."""
        from src.core.license_generator import generate_license_data

        result = generate_license_data(state)
        dl = result[0]

        # Height: 58-78 inches
        if 'DAU' in dl:
            height = int(dl['DAU'])
            assert 58 <= height <= 78, f"Height {height} out of range"

        # Weight: 100-300 lbs
        if 'DAW' in dl:
            weight = int(dl['DAW'])
            assert 100 <= weight <= 300, f"Weight {weight} out of range"

    @given(
        state=valid_states,
        seed=st.integers(min_value=0, max_value=1000000)
    )
    @settings(max_examples=50, deadline=None)
    def test_property_deterministic_with_seed(self, state, seed):
        """Property: Same seed produces same output."""
        from src.core.license_generator import generate_license_data
        import random

        random.seed(seed)
        result1 = generate_license_data(state)

        random.seed(seed)
        result2 = generate_license_data(state)

        # Key fields should match
        assert result1[0]['DAQ'] == result2[0]['DAQ'], \
            "License numbers differ with same seed"
        assert result1[0]['DCS'] == result2[0]['DCS'], \
            "Last names differ with same seed"


# ============================================================================
# PROPERTY TESTS: BARCODE FORMATTING
# ============================================================================

class TestBarcodeFormattingProperties:
    """Property-based tests for barcode formatting."""

    @given(state=valid_states)
    @settings(max_examples=100, deadline=None)
    def test_property_barcode_structure_invariants(self, state):
        """Property: Barcode structure is always valid."""
        from src.core.license_generator import generate_license_data
        from src.core.barcode_formatter import format_barcode_data

        data = generate_license_data(state)
        result = format_barcode_data(data)

        # Structural invariants
        assert result.startswith("@\n\x1E\r"), "Must start with compliance markers"
        assert "ANSI " in result, "Must contain ANSI marker"
        assert "DL" in result, "Must contain DL subfile"
        assert result.count('\r') >= 2, "Must have at least 2 CRs"

    @given(state=valid_states)
    @settings(max_examples=100, deadline=None)
    def test_property_barcode_is_pure_ascii(self, state):
        """Property: Barcode always contains only ASCII."""
        from src.core.license_generator import generate_license_data
        from src.core.barcode_formatter import format_barcode_data

        data = generate_license_data(state)
        result = format_barcode_data(data)

        # Should encode to ASCII without error
        encoded = result.encode('ascii')
        decoded = encoded.decode('ascii')

        assert decoded == result, "Roundtrip encoding failed"

    @given(state=valid_states)
    @settings(max_examples=100, deadline=None)
    def test_property_barcode_length_in_range(self, state):
        """Property: Barcode length is always in valid range."""
        from src.core.license_generator import generate_license_data
        from src.core.barcode_formatter import format_barcode_data

        data = generate_license_data(state)
        result = format_barcode_data(data)

        length = len(result.encode('ascii'))
        assert 150 <= length <= 1000, \
            f"Barcode length {length} outside valid range"

    @given(state=valid_states)
    @settings(max_examples=50, deadline=None)
    def test_property_version_always_10(self, state):
        """Property: AAMVA version is always '10'."""
        from src.core.license_generator import generate_license_data
        from src.core.barcode_formatter import format_barcode_data

        data = generate_license_data(state)
        result = format_barcode_data(data)

        version = result[15:17]
        assert version == '10', f"Expected version '10', got '{version}'"


# ============================================================================
# PROPERTY TESTS: DATE VALIDATION
# ============================================================================

class TestDateValidationProperties:
    """Property-based tests for date validation."""

    @given(year=st.integers(min_value=1900, max_value=2100))
    @settings(max_examples=200, deadline=None)
    def test_property_leap_year_rules(self, year):
        """Property: Leap year detection follows standard rules."""
        from src.core.validators import is_leap_year

        # Leap year rules:
        # - Divisible by 4: leap year
        # - EXCEPT divisible by 100: not leap year
        # - EXCEPT divisible by 400: leap year
        expected = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

        assert is_leap_year(year) == expected, \
            f"Leap year calculation wrong for {year}"

    @given(
        month=st.integers(min_value=1, max_value=12),
        day=st.integers(min_value=1, max_value=28),  # Safe for all months
        year=st.integers(min_value=1920, max_value=2099)
    )
    @settings(max_examples=100, deadline=None)
    def test_property_valid_dates_accepted(self, month, day, year):
        """Property: All valid dates are accepted."""
        from src.core.validators import validate_date_format

        date_str = f"{month:02d}{day:02d}{year}"

        assert validate_date_format(date_str) is True, \
            f"Valid date {date_str} rejected"

    @given(
        month=st.integers(min_value=13, max_value=99),
        day=st.integers(min_value=1, max_value=31),
        year=st.integers(min_value=1920, max_value=2099)
    )
    @settings(max_examples=50, deadline=None)
    def test_property_invalid_months_rejected(self, month, day, year):
        """Property: Invalid months are always rejected."""
        from src.core.validators import validate_date_format

        date_str = f"{month:02d}{day:02d}{year}"

        assert validate_date_format(date_str) is False, \
            f"Invalid month {month} was accepted"


# ============================================================================
# PROPERTY TESTS: ROUNDTRIP ENCODING
# ============================================================================

class TestRoundtripProperties:
    """Property-based tests for roundtrip encoding/decoding."""

    @given(state=valid_states)
    @settings(max_examples=50, deadline=None)
    def test_property_license_to_barcode_to_ascii_roundtrip(self, state):
        """Property: License → Barcode → ASCII → Barcode is identity."""
        from src.core.license_generator import generate_license_data
        from src.core.barcode_formatter import format_barcode_data

        data = generate_license_data(state)
        barcode1 = format_barcode_data(data)

        # Encode to ASCII and back
        encoded = barcode1.encode('ascii')
        barcode2 = encoded.decode('ascii')

        assert barcode1 == barcode2, "Roundtrip encoding changed barcode"


# ============================================================================
# PROPERTY TESTS: METAMORPHIC PROPERTIES
# ============================================================================

class TestMetamorphicProperties:
    """Metamorphic testing: relationships between test executions."""

    @given(state=valid_states)
    @settings(max_examples=50, deadline=None)
    def test_metamorphic_same_state_same_format(self, state):
        """Metamorphic: Same state → same license number format."""
        from src.core.license_generator import generate_license_data

        result1 = generate_license_data(state)
        result2 = generate_license_data(state)

        # Format should be identical (length and pattern)
        len1 = len(result1[0]['DAQ'])
        len2 = len(result2[0]['DAQ'])

        assert len1 == len2, \
            f"License number length differs: {len1} vs {len2}"

    @given(state=valid_states)
    @settings(max_examples=50, deadline=None)
    def test_metamorphic_barcode_length_monotonic(self, state):
        """Metamorphic: More data → longer or equal barcode."""
        from src.core.license_generator import generate_license_data
        from src.core.barcode_formatter import format_barcode_data

        # Generate minimal license
        data_minimal = generate_license_data(state)
        data_minimal[0]['DAD'] = ''  # Remove middle name

        # Generate maximal license (with middle name)
        data_maximal = generate_license_data(state)

        barcode_minimal = format_barcode_data(data_minimal)
        barcode_maximal = format_barcode_data(data_maximal)

        # Maximal should be >= minimal (if middle name present)
        if data_maximal[0].get('DAD'):
            assert len(barcode_maximal) >= len(barcode_minimal), \
                "More data should not produce shorter barcode"


# ============================================================================
# PROPERTY TESTS: INVARIANT PROPERTIES
# ============================================================================

class TestInvariantProperties:
    """Tests for properties that must always hold (invariants)."""

    @given(state=valid_states)
    @settings(max_examples=100, deadline=None)
    def test_invariant_subfile_type_dl_first(self, state):
        """Invariant: First subfile type is always 'DL'."""
        from src.core.license_generator import generate_license_data

        result = generate_license_data(state)

        assert result[0]['subfile_type'] == 'DL', \
            "First subfile must be DL"

    @given(state=valid_states)
    @settings(max_examples=100, deadline=None)
    def test_invariant_state_subfile_starts_with_z(self, state):
        """Invariant: State subfile type always starts with 'Z'."""
        from src.core.license_generator import generate_license_data

        result = generate_license_data(state)

        assert result[1]['subfile_type'].startswith('Z'), \
            "State subfile must start with Z"

    @given(state=valid_states)
    @settings(max_examples=100, deadline=None)
    def test_invariant_zip_code_nine_digits(self, state):
        """Invariant: Zip code is always 9 digits."""
        from src.core.license_generator import generate_license_data

        result = generate_license_data(state)

        zip_code = result[0]['DAK']
        assert len(zip_code) == 9, f"Zip code should be 9 digits, got {len(zip_code)}"
        assert zip_code.isdigit(), "Zip code should be all digits"


# ============================================================================
# PROPERTY TESTS: EDGE CASES
# ============================================================================

class TestEdgeCaseProperties:
    """Property-based tests for edge cases."""

    @given(state=valid_states)
    @settings(max_examples=50, deadline=None)
    @example(state='CA')
    @example(state='NY')
    @example(state='TX')
    def test_edge_common_states_work(self, state):
        """Edge case: Common states always work."""
        from src.core.license_generator import generate_license_data

        result = generate_license_data(state)

        assert len(result) == 2
        assert result[0]['DAJ'] == state.upper()

    @given(
        year=st.one_of(
            st.just(2000),  # Leap year (divisible by 400)
            st.just(1900),  # Not leap year (divisible by 100 but not 400)
            st.just(2024),  # Leap year (divisible by 4)
            st.just(2023),  # Not leap year
        )
    )
    @settings(max_examples=20, deadline=None)
    def test_edge_leap_year_boundaries(self, year):
        """Edge case: Leap year edge cases handled correctly."""
        from src.core.validators import is_leap_year

        expected_leap = [2000, 2024]
        expected_not_leap = [1900, 2023]

        if year in expected_leap:
            assert is_leap_year(year) is True
        else:
            assert is_leap_year(year) is False


# ============================================================================
# PROPERTY TESTS: STATISTICAL PROPERTIES
# ============================================================================

class TestStatisticalProperties:
    """Statistical properties that should hold over many samples."""

    @given(state=valid_states)
    @settings(max_examples=100, deadline=None,
              suppress_health_check=[HealthCheck.too_slow])
    def test_statistical_license_numbers_mostly_unique(self, state):
        """Statistical: License numbers should be mostly unique."""
        from src.core.license_generator import generate_license_data

        # Generate 20 licenses
        licenses = [generate_license_data(state)[0]['DAQ']
                   for _ in range(20)]

        unique_count = len(set(licenses))

        # At least 95% should be unique (allow 1 collision in 20)
        assert unique_count >= 19, \
            f"Only {unique_count}/20 licenses unique"

    @given(state=valid_states)
    @settings(max_examples=50, deadline=None,
              suppress_health_check=[HealthCheck.too_slow])
    def test_statistical_sex_distribution_balanced(self, state):
        """Statistical: Sex distribution should be roughly balanced."""
        from src.core.license_generator import generate_license_data

        # Generate 50 licenses
        licenses = [generate_license_data(state) for _ in range(50)]
        sex_codes = [lic[0]['DBC'] for lic in licenses]

        male_count = sex_codes.count('1')
        female_count = sex_codes.count('2')

        # Should be somewhat balanced (30-70% each)
        total = male_count + female_count
        male_ratio = male_count / total

        assert 0.3 <= male_ratio <= 0.7, \
            f"Sex distribution imbalanced: {male_ratio:.2%} male"


# ============================================================================
# PROPERTY TESTS: COMPOSITION PROPERTIES
# ============================================================================

class TestCompositionProperties:
    """Properties about function composition."""

    @given(state=valid_states)
    @settings(max_examples=50, deadline=None)
    def test_composition_generate_then_format_always_succeeds(self, state):
        """Property: generate → format always succeeds."""
        from src.core.license_generator import generate_license_data
        from src.core.barcode_formatter import format_barcode_data

        # Should not raise exception
        data = generate_license_data(state)
        barcode = format_barcode_data(data)

        assert len(barcode) > 0

    @given(state=valid_states)
    @settings(max_examples=50, deadline=None)
    def test_composition_generate_then_validate_always_succeeds(self, state):
        """Property: generate → validate always passes."""
        from src.core.license_generator import generate_license_data
        from src.core.validators import validate_license_data

        data = generate_license_data(state)
        result = validate_license_data(data)

        assert result['valid'] is True, \
            f"Generated license failed validation: {result.get('errors')}"
