"""
Unit tests for license data generation.

These tests follow TDD RED phase - they are written BEFORE implementation
and will FAIL until the code is written to make them pass.

Test coverage: generate_license_data() function
Target coverage: 100% of license generation logic
"""

import pytest
from datetime import datetime, timedelta
from freezegun import freeze_time
from hypothesis import given, strategies as st, settings, assume

# Import will fail - this is expected in TDD RED phase
# from src.core.license_generator import generate_license_data


pytestmark = pytest.mark.unit


class TestLicenseDataStructure:
    """Tests for basic license data structure."""

    def test_returns_list_with_two_subfiles(self):
        """License data should return list with exactly 2 elements [DL, State]."""
        from src.core.license_generator import generate_license_data

        result = generate_license_data('CA')

        assert isinstance(result, list), "Result should be a list"
        assert len(result) == 2, "Should have exactly 2 subfiles"

    def test_first_element_is_dl_subfile(self):
        """First element should be DL subfile dictionary."""
        from src.core.license_generator import generate_license_data

        result = generate_license_data('CA')
        dl_subfile = result[0]

        assert isinstance(dl_subfile, dict), "DL subfile should be a dictionary"
        assert dl_subfile.get('subfile_type') == 'DL', "Should have DL subfile_type"

    def test_second_element_is_state_subfile(self):
        """Second element should be state-specific subfile."""
        from src.core.license_generator import generate_license_data

        result = generate_license_data('CA')
        state_subfile = result[1]

        assert isinstance(state_subfile, dict), "State subfile should be a dictionary"
        assert state_subfile.get('subfile_type', '').startswith('Z'), \
            "State subfile should start with Z"


class TestAAMVARequiredFields:
    """Tests for AAMVA mandatory fields."""

    def test_dl_subfile_contains_all_required_fields(self, aamva_required_fields):
        """DL subfile must contain all AAMVA mandatory fields."""
        from src.core.license_generator import generate_license_data

        result = generate_license_data('CA')
        dl_subfile = result[0]

        for field in aamva_required_fields:
            assert field in dl_subfile, f"Missing required AAMVA field: {field}"
            assert dl_subfile[field] is not None, f"Field {field} should not be None"
            assert len(str(dl_subfile[field])) > 0, f"Field {field} should not be empty"

    def test_daq_license_number_present(self):
        """DAQ field (license number) must be present and non-empty."""
        from src.core.license_generator import generate_license_data

        result = generate_license_data('CA')

        assert 'DAQ' in result[0]
        assert len(result[0]['DAQ']) > 0

    def test_name_fields_present(self):
        """DCS (last name) and DAC (first name) must be present."""
        from src.core.license_generator import generate_license_data

        result = generate_license_data('CA')
        dl = result[0]

        assert 'DCS' in dl, "Last name (DCS) missing"
        assert 'DAC' in dl, "First name (DAC) missing"
        assert len(dl['DCS']) > 0, "Last name should not be empty"
        assert len(dl['DAC']) > 0, "First name should not be empty"

    def test_date_fields_present(self):
        """DBB (DOB), DBA (expiration), DBD (issue) must be present."""
        from src.core.license_generator import generate_license_data

        result = generate_license_data('CA')
        dl = result[0]

        assert 'DBB' in dl, "Date of birth (DBB) missing"
        assert 'DBA' in dl, "Expiration date (DBA) missing"
        assert 'DBD' in dl, "Issue date (DBD) missing"

    def test_address_fields_present(self):
        """Address fields DAG, DAI, DAJ, DAK must be present."""
        from src.core.license_generator import generate_license_data

        result = generate_license_data('CA')
        dl = result[0]

        assert 'DAG' in dl, "Street address (DAG) missing"
        assert 'DAI' in dl, "City (DAI) missing"
        assert 'DAJ' in dl, "State (DAJ) missing"
        assert 'DAK' in dl, "Zip code (DAK) missing"


class TestDateLogic:
    """Tests for date field logic and validation."""

    def test_dates_in_chronological_order(self):
        """Birth date < Issue date < Expiration date."""
        from src.core.license_generator import generate_license_data

        result = generate_license_data('CA')
        dl = result[0]

        dob = datetime.strptime(dl['DBB'], '%m%d%Y')
        issue = datetime.strptime(dl['DBD'], '%m%d%Y')
        exp = datetime.strptime(dl['DBA'], '%m%d%Y')

        assert dob < issue, "Birth date must be before issue date"
        assert issue < exp, "Issue date must be before expiration date"
        assert dob < exp, "Birth date must be before expiration date"

    def test_age_at_least_16_years(self):
        """Driver must be at least 16 years old at issue date."""
        from src.core.license_generator import generate_license_data

        result = generate_license_data('CA')
        dl = result[0]

        dob = datetime.strptime(dl['DBB'], '%m%d%Y')
        issue = datetime.strptime(dl['DBD'], '%m%d%Y')

        age_days = (issue - dob).days
        age_years = age_days / 365.25

        assert age_years >= 16, f"Driver age {age_years:.1f} is below minimum 16 years"

    def test_age_not_over_100_years(self):
        """Driver should not be over 100 years old (sanity check)."""
        from src.core.license_generator import generate_license_data

        result = generate_license_data('CA')
        dl = result[0]

        dob = datetime.strptime(dl['DBB'], '%m%d%Y')
        issue = datetime.strptime(dl['DBD'], '%m%d%Y')

        age_years = (issue - dob).days / 365.25

        assert age_years <= 100, f"Driver age {age_years:.1f} is unreasonably high"

    @freeze_time("2025-11-20")
    def test_issue_date_is_today(self):
        """Issue date should be today's date."""
        from src.core.license_generator import generate_license_data

        result = generate_license_data('CA')

        assert result[0]['DBD'] == '11202025', "Issue date should be today (11/20/2025)"

    def test_expiration_is_5_to_10_years_future(self):
        """Expiration should be 5-10 years after issue date."""
        from src.core.license_generator import generate_license_data

        result = generate_license_data('CA')
        dl = result[0]

        issue = datetime.strptime(dl['DBD'], '%m%d%Y')
        exp = datetime.strptime(dl['DBA'], '%m%d%Y')

        years_diff = (exp - issue).days / 365.25

        assert 5 <= years_diff <= 10, \
            f"Expiration {years_diff:.1f} years from issue, expected 5-10"

    def test_date_format_is_mmddyyyy(self):
        """All dates should be in MMDDYYYY format."""
        from src.core.license_generator import generate_license_data

        result = generate_license_data('CA')
        dl = result[0]

        date_fields = ['DBB', 'DBA', 'DBD']

        for field in date_fields:
            date_str = dl[field]
            assert len(date_str) == 8, f"{field} should be 8 characters"
            assert date_str.isdigit(), f"{field} should be all digits"

            # Should parse without error
            parsed = datetime.strptime(date_str, '%m%d%Y')
            assert parsed is not None


class TestPhysicalCharacteristics:
    """Tests for physical characteristic fields."""

    def test_sex_code_is_valid(self, valid_sex_codes):
        """Sex field (DBC) must be 1, 2, or 9."""
        from src.core.license_generator import generate_license_data

        result = generate_license_data('CA')

        assert result[0]['DBC'] in valid_sex_codes, \
            f"Sex code {result[0]['DBC']} not in {valid_sex_codes}"

    def test_eye_color_is_valid(self, valid_eye_colors):
        """Eye color (DAY) must be from AAMVA standard codes."""
        from src.core.license_generator import generate_license_data

        result = generate_license_data('CA')

        assert result[0]['DAY'] in valid_eye_colors, \
            f"Eye color {result[0]['DAY']} not in valid set"

    def test_hair_color_is_valid(self, valid_hair_colors):
        """Hair color (DAZ) must be from AAMVA standard codes."""
        from src.core.license_generator import generate_license_data

        result = generate_license_data('CA')

        assert result[0]['DAZ'] in valid_hair_colors, \
            f"Hair color {result[0]['DAZ']} not in valid set"

    def test_height_in_valid_range(self):
        """Height (DAU) should be 58-78 inches (4'10" to 6'6")."""
        from src.core.license_generator import generate_license_data

        result = generate_license_data('CA')
        height_str = result[0]['DAU']
        height = int(height_str)

        assert 58 <= height <= 78, \
            f"Height {height} inches outside valid range 58-78"

    def test_height_is_three_digits(self):
        """Height should be zero-padded to 3 digits."""
        from src.core.license_generator import generate_license_data

        result = generate_license_data('CA')
        height_str = result[0]['DAU']

        assert len(height_str) == 3, f"Height should be 3 digits, got {len(height_str)}"
        assert height_str.isdigit(), "Height should be numeric"

    def test_weight_in_valid_range(self):
        """Weight (DAW) should be 100-300 lbs."""
        from src.core.license_generator import generate_license_data

        result = generate_license_data('CA')

        if 'DAW' in result[0]:
            weight = int(result[0]['DAW'])
            assert 100 <= weight <= 300, \
                f"Weight {weight} lbs outside valid range 100-300"


class TestNameFields:
    """Tests for name field generation and formatting."""

    def test_all_name_fields_uppercase(self):
        """All name fields should be uppercase."""
        from src.core.license_generator import generate_license_data

        result = generate_license_data('CA')
        dl = result[0]

        name_fields = ['DCS', 'DAC']
        if 'DAD' in dl and dl['DAD']:  # Middle name optional
            name_fields.append('DAD')

        for field in name_fields:
            name = dl[field]
            assert name == name.upper(), \
                f"Field {field} value '{name}' is not uppercase"

    def test_last_name_not_empty(self):
        """Last name (DCS) must not be empty."""
        from src.core.license_generator import generate_license_data

        result = generate_license_data('CA')

        assert len(result[0]['DCS']) > 0, "Last name should not be empty"

    def test_first_name_not_empty(self):
        """First name (DAC) must not be empty."""
        from src.core.license_generator import generate_license_data

        result = generate_license_data('CA')

        assert len(result[0]['DAC']) > 0, "First name should not be empty"

    def test_names_contain_only_letters(self):
        """Names should contain only letters (no numbers or special chars)."""
        from src.core.license_generator import generate_license_data

        result = generate_license_data('CA')
        dl = result[0]

        name_fields = ['DCS', 'DAC']

        for field in name_fields:
            name = dl[field]
            # Allow letters, spaces, hyphens
            assert all(c.isalpha() or c in [' ', '-'] for c in name), \
                f"Name field {field} contains invalid characters: {name}"


class TestAddressFields:
    """Tests for address field generation."""

    def test_state_matches_requested_state(self):
        """DAJ field should match the requested state."""
        from src.core.license_generator import generate_license_data

        result = generate_license_data('TX')

        assert result[0]['DAJ'] == 'TX', "State field should match requested state"

    def test_state_is_uppercase(self):
        """State code should be uppercase."""
        from src.core.license_generator import generate_license_data

        result = generate_license_data('ca')  # lowercase input

        assert result[0]['DAJ'] == 'CA', "State should be uppercase"

    def test_zip_code_is_nine_digits(self):
        """Zip code (DAK) should be 9 digits (ZIP+4 format)."""
        from src.core.license_generator import generate_license_data

        result = generate_license_data('CA')
        zip_code = result[0]['DAK']

        assert len(zip_code) == 9, f"Zip code should be 9 digits, got {len(zip_code)}"
        assert zip_code.isdigit(), "Zip code should be all digits"

    def test_street_address_not_empty(self):
        """Street address (DAG) should not be empty."""
        from src.core.license_generator import generate_license_data

        result = generate_license_data('CA')

        assert len(result[0]['DAG']) > 0, "Street address should not be empty"

    def test_city_not_empty(self):
        """City (DAI) should not be empty."""
        from src.core.license_generator import generate_license_data

        result = generate_license_data('CA')

        assert len(result[0]['DAI']) > 0, "City should not be empty"


class TestLicenseNumberFormats:
    """Tests for state-specific license number formats."""

    def test_california_license_format(self):
        """California: 1 letter + 7 digits."""
        from src.core.license_generator import generate_license_data

        result = generate_license_data('CA')
        license_num = result[0]['DAQ']

        assert len(license_num) == 8, "CA license should be 8 characters"
        assert license_num[0].isalpha(), "CA license should start with letter"
        assert license_num[0].isupper(), "CA license letter should be uppercase"
        assert license_num[1:].isdigit(), "CA license should have 7 digits after letter"

    def test_texas_license_format(self):
        """Texas: 8 digits."""
        from src.core.license_generator import generate_license_data

        result = generate_license_data('TX')
        license_num = result[0]['DAQ']

        assert len(license_num) == 8, "TX license should be 8 characters"
        assert license_num.isdigit(), "TX license should be all digits"

    def test_florida_license_format(self):
        """Florida: 1 letter + 12 digits."""
        from src.core.license_generator import generate_license_data

        result = generate_license_data('FL')
        license_num = result[0]['DAQ']

        assert len(license_num) == 13, "FL license should be 13 characters"
        assert license_num[0].isalpha(), "FL license should start with letter"
        assert license_num[1:].isdigit(), "FL license should have 12 digits after letter"


class TestStateSubfile:
    """Tests for state-specific subfile."""

    def test_california_state_subfile_type(self):
        """California state subfile should be 'ZC'."""
        from src.core.license_generator import generate_license_data

        result = generate_license_data('CA')
        state_subfile = result[1]

        assert state_subfile['subfile_type'] == 'ZC', \
            "CA state subfile should be ZC"

    def test_new_york_state_subfile_type(self):
        """New York state subfile should be 'ZN'."""
        from src.core.license_generator import generate_license_data

        result = generate_license_data('NY')
        state_subfile = result[1]

        assert state_subfile['subfile_type'] == 'ZN', \
            "NY state subfile should be ZN"

    def test_state_subfile_has_data(self):
        """State subfile should contain at least one data field."""
        from src.core.license_generator import generate_license_data

        result = generate_license_data('CA')
        state_subfile = result[1]

        # Should have more than just subfile_type
        assert len(state_subfile) > 1, \
            "State subfile should have data fields beyond subfile_type"


class TestUniqueness:
    """Tests for uniqueness of generated data."""

    def test_license_numbers_are_unique(self):
        """Generated license numbers should be statistically unique."""
        from src.core.license_generator import generate_license_data

        licenses = [generate_license_data('CA')[0]['DAQ'] for _ in range(100)]
        unique_licenses = set(licenses)

        # Allow max 1% collision rate
        assert len(unique_licenses) >= 99, \
            f"Only {len(unique_licenses)}/100 licenses were unique"

    def test_document_discriminator_is_unique(self):
        """DCF field (document discriminator) should be unique."""
        from src.core.license_generator import generate_license_data

        licenses = [generate_license_data('CA') for _ in range(100)]
        discriminators = [lic[0]['DCF'] for lic in licenses]

        assert len(set(discriminators)) == 100, \
            "Document discriminators should be unique"


class TestErrorHandling:
    """Tests for error handling and edge cases."""

    def test_invalid_state_raises_error(self, invalid_state_codes):
        """Invalid state codes should raise ValueError."""
        from src.core.license_generator import generate_license_data

        for invalid_state in invalid_state_codes:
            if invalid_state is None or invalid_state == '':
                continue  # None might be valid for random state

            with pytest.raises((ValueError, KeyError),
                             match="(Unknown state|Invalid state|not found)"):
                generate_license_data(invalid_state)

    def test_none_state_generates_random_state(self, valid_state_codes):
        """Passing None should generate a random valid state."""
        from src.core.license_generator import generate_license_data

        result = generate_license_data(None)

        assert result[0]['DAJ'] in valid_state_codes, \
            "Random state should be from valid state list"

    def test_lowercase_state_converts_to_uppercase(self):
        """Lowercase state codes should be accepted and converted."""
        from src.core.license_generator import generate_license_data

        result = generate_license_data('ca')

        assert result[0]['DAJ'] == 'CA', "State should be converted to uppercase"


class TestDeterminism:
    """Tests for deterministic behavior with seeds."""

    def test_same_seed_produces_same_output(self):
        """Using same random seed should produce identical output."""
        from src.core.license_generator import generate_license_data
        import random

        random.seed(42)
        result1 = generate_license_data('CA')

        random.seed(42)
        result2 = generate_license_data('CA')

        assert result1[0]['DAQ'] == result2[0]['DAQ'], \
            "Same seed should produce same license number"
        assert result1[0]['DCS'] == result2[0]['DCS'], \
            "Same seed should produce same last name"


# ============================================================================
# PROPERTY-BASED TESTS (Hypothesis)
# ============================================================================

class TestPropertyBased:
    """Property-based tests using Hypothesis."""

    @given(state=st.sampled_from(['CA', 'NY', 'TX', 'FL', 'WA']))
    @settings(max_examples=50)
    def test_property_any_valid_state_produces_valid_structure(self, state):
        """Property: Any valid state produces correctly structured data."""
        from src.core.license_generator import generate_license_data

        result = generate_license_data(state)

        assert len(result) == 2, "Should always have 2 subfiles"
        assert result[0]['subfile_type'] == 'DL'
        assert result[0]['DAJ'] == state

    @given(state=st.sampled_from(['CA', 'NY', 'TX']))
    @settings(max_examples=50)
    def test_property_dates_always_ordered(self, state):
        """Property: Date ordering always holds."""
        from src.core.license_generator import generate_license_data

        result = generate_license_data(state)
        dl = result[0]

        dob = datetime.strptime(dl['DBB'], '%m%d%Y')
        issue = datetime.strptime(dl['DBD'], '%m%d%Y')
        exp = datetime.strptime(dl['DBA'], '%m%d%Y')

        assert dob < issue < exp

    @given(state=st.sampled_from(['CA', 'NY', 'TX', 'FL']))
    @settings(max_examples=50)
    def test_property_license_number_never_empty(self, state):
        """Property: License number is always non-empty."""
        from src.core.license_generator import generate_license_data

        result = generate_license_data(state)

        assert len(result[0]['DAQ']) > 0


# ============================================================================
# PARAMETRIZED TESTS
# ============================================================================

class TestParametrized:
    """Parametrized tests for multiple states."""

    @pytest.mark.parametrize("state", ['CA', 'NY', 'TX', 'FL', 'WA', 'IL'])
    def test_all_states_produce_valid_structure(self, state):
        """All states should produce valid license structure."""
        from src.core.license_generator import generate_license_data

        result = generate_license_data(state)

        assert len(result) == 2
        assert result[0]['DAJ'] == state

    @pytest.mark.parametrize("iteration", range(10))
    def test_consistency_over_multiple_generations(self, iteration):
        """Format should be consistent across multiple generations."""
        from src.core.license_generator import generate_license_data

        result = generate_license_data('CA')

        # Basic structure checks
        assert len(result[0]['DAQ']) == 8
        assert result[0]['DAQ'][0].isalpha()
        assert result[0]['DAQ'][1:].isdigit()
