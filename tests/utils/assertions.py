"""
Custom test assertions for AAMVA license testing.

Provides domain-specific assertion helpers to make tests more readable
and maintainable.
"""

from datetime import datetime
from typing import Dict, Any, List


def assert_aamva_compliant(license_data: List[Dict[str, Any]]) -> None:
    """
    Assert that license data is AAMVA compliant.

    Args:
        license_data: License data structure [DL_subfile, State_subfile]

    Raises:
        AssertionError: If data is not AAMVA compliant
    """
    assert isinstance(license_data, list), "License data should be a list"
    assert len(license_data) == 2, "Should have exactly 2 subfiles"

    dl_subfile = license_data[0]
    state_subfile = license_data[1]

    # Check subfile types
    assert dl_subfile.get('subfile_type') == 'DL', "First subfile should be DL"
    assert state_subfile.get('subfile_type', '').startswith('Z'), \
        "Second subfile should start with Z"

    # Check required fields
    required_fields = [
        'DAQ', 'DCS', 'DAC', 'DBB', 'DBA', 'DBD',
        'DAG', 'DAI', 'DAJ', 'DAK', 'DBC', 'DAY', 'DAU'
    ]

    for field in required_fields:
        assert field in dl_subfile, f"Missing required field: {field}"
        assert dl_subfile[field] is not None, f"Field {field} is None"
        assert len(str(dl_subfile[field])) > 0, f"Field {field} is empty"


def assert_valid_barcode_structure(barcode: str) -> None:
    """
    Assert that barcode has valid AAMVA structure.

    Args:
        barcode: Formatted barcode string

    Raises:
        AssertionError: If barcode structure is invalid
    """
    # Compliance markers
    assert barcode[0] == '@', "Missing @ compliance marker"
    assert barcode[1] == '\n', "Missing LF after @"
    assert barcode[2] == '\x1E', "Missing RS record separator"
    assert barcode[3] == '\r', "Missing CR after RS"

    # ANSI marker
    assert barcode[4:9] == 'ANSI ', "Missing or invalid ANSI marker"

    # IIN
    iin = barcode[9:15]
    assert len(iin) == 6, f"IIN should be 6 characters, got {len(iin)}"
    assert iin.isdigit(), f"IIN should be numeric, got '{iin}'"

    # Version
    version = barcode[15:17]
    assert version == '10', f"Version should be '10', got '{version}'"

    # Subfile count
    count = barcode[19:21]
    assert count == '02', f"Should have '02' subfiles, got '{count}'"


def assert_dates_chronological(dob: str, issue: str, exp: str) -> None:
    """
    Assert that dates are in chronological order.

    Args:
        dob: Date of birth (MMDDYYYY)
        issue: Issue date (MMDDYYYY)
        exp: Expiration date (MMDDYYYY)

    Raises:
        AssertionError: If dates are not chronological
    """
    dob_date = datetime.strptime(dob, '%m%d%Y')
    issue_date = datetime.strptime(issue, '%m%d%Y')
    exp_date = datetime.strptime(exp, '%m%d%Y')

    assert dob_date < issue_date, \
        f"Birth date {dob} must be before issue date {issue}"
    assert issue_date < exp_date, \
        f"Issue date {issue} must be before expiration date {exp}"


def assert_age_at_least(dob: str, issue: str, min_age: int) -> None:
    """
    Assert that age at issue date is at least min_age.

    Args:
        dob: Date of birth (MMDDYYYY)
        issue: Issue date (MMDDYYYY)
        min_age: Minimum age in years

    Raises:
        AssertionError: If age is below minimum
    """
    dob_date = datetime.strptime(dob, '%m%d%Y')
    issue_date = datetime.strptime(issue, '%m%d%Y')

    age_years = (issue_date - dob_date).days / 365.25

    assert age_years >= min_age, \
        f"Age {age_years:.1f} is below minimum {min_age}"


def assert_valid_physical_characteristics(
    height: int = None,
    weight: int = None,
    eye_color: str = None,
    hair_color: str = None,
    sex: str = None
) -> None:
    """
    Assert that physical characteristics are valid.

    Args:
        height: Height in inches
        weight: Weight in pounds
        eye_color: AAMVA eye color code
        hair_color: AAMVA hair color code
        sex: AAMVA sex code

    Raises:
        AssertionError: If any characteristic is invalid
    """
    if height is not None:
        assert 58 <= height <= 78, \
            f"Height {height} outside valid range 58-78 inches"

    if weight is not None:
        assert 100 <= weight <= 300, \
            f"Weight {weight} outside valid range 100-300 lbs"

    if eye_color is not None:
        valid_eyes = ['BLK', 'BLU', 'BRO', 'GRY', 'GRN', 'HAZ', 'MAR', 'PNK', 'DIC', 'UNK']
        assert eye_color in valid_eyes, \
            f"Eye color '{eye_color}' not in valid set"

    if hair_color is not None:
        valid_hair = ['BLK', 'BLN', 'BRO', 'GRY', 'RED', 'WHI', 'SDY', 'UNK', 'BAL']
        assert hair_color in valid_hair, \
            f"Hair color '{hair_color}' not in valid set"

    if sex is not None:
        valid_sex = ['1', '2', '9']
        assert sex in valid_sex, \
            f"Sex code '{sex}' not in valid set {valid_sex}"


def assert_license_number_format(license_num: str, state: str) -> None:
    """
    Assert that license number matches state-specific format.

    Args:
        license_num: License number
        state: State code

    Raises:
        AssertionError: If format doesn't match state requirements
    """
    state = state.upper()

    if state == 'CA':
        # California: 1 letter + 7 digits
        assert len(license_num) == 8, \
            f"CA license should be 8 characters, got {len(license_num)}"
        assert license_num[0].isalpha(), "CA license should start with letter"
        assert license_num[1:].isdigit(), "CA license should have 7 digits"

    elif state == 'TX':
        # Texas: 8 digits
        assert len(license_num) == 8, \
            f"TX license should be 8 characters, got {len(license_num)}"
        assert license_num.isdigit(), "TX license should be all digits"

    elif state == 'FL':
        # Florida: 1 letter + 12 digits
        assert len(license_num) == 13, \
            f"FL license should be 13 characters, got {len(license_num)}"
        assert license_num[0].isalpha(), "FL license should start with letter"
        assert license_num[1:].isdigit(), "FL license should have 12 digits"

    elif state == 'NY':
        # New York: 1 letter + 7-18 digits
        assert 8 <= len(license_num) <= 19, \
            f"NY license should be 8-19 characters, got {len(license_num)}"
        assert license_num[0].isalpha(), "NY license should start with letter"
        assert license_num[1:].isdigit(), "NY license should have digits"


def assert_valid_state_code(state: str) -> None:
    """
    Assert that state code is valid US state or DC.

    Args:
        state: Two-letter state code

    Raises:
        AssertionError: If state code is invalid
    """
    valid_states = {
        'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
        'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
        'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
        'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
        'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY', 'DC'
    }

    state_upper = state.upper()
    assert state_upper in valid_states, \
        f"State '{state}' is not a valid US state or DC"


def assert_all_uppercase(value: str, field_name: str = "value") -> None:
    """
    Assert that string value is all uppercase.

    Args:
        value: String to check
        field_name: Name of field for error message

    Raises:
        AssertionError: If value contains lowercase characters
    """
    assert value == value.upper(), \
        f"{field_name} '{value}' should be all uppercase"


def assert_ascii_only(value: str, field_name: str = "value") -> None:
    """
    Assert that string contains only ASCII characters.

    Args:
        value: String to check
        field_name: Name of field for error message

    Raises:
        AssertionError: If value contains non-ASCII characters
    """
    try:
        value.encode('ascii')
    except UnicodeEncodeError as e:
        raise AssertionError(
            f"{field_name} contains non-ASCII characters: {e}"
        )


def assert_valid_date_format(date_str: str, field_name: str = "date") -> None:
    """
    Assert that date string is in AAMVA format (MMDDYYYY).

    Args:
        date_str: Date string to validate
        field_name: Name of field for error message

    Raises:
        AssertionError: If date format is invalid
    """
    assert len(date_str) == 8, \
        f"{field_name} should be 8 characters (MMDDYYYY), got {len(date_str)}"
    assert date_str.isdigit(), \
        f"{field_name} should be all digits, got '{date_str}'"

    # Try to parse
    try:
        parsed = datetime.strptime(date_str, '%m%d%Y')
        assert parsed is not None
    except ValueError as e:
        raise AssertionError(f"{field_name} '{date_str}' is not a valid date: {e}")
