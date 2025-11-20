"""
State-specific validation rules.

Provides detailed validation rules for each state's specific requirements
including license number formats, age requirements, and special rules.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import re
from .schemas import ValidationLevel, FieldValidationResult


@dataclass
class StateRules:
    """
    State-specific validation rules.

    Attributes:
        state_code: Two-letter state abbreviation
        state_name: Full state name
        min_age: Minimum age for license issuance
        license_patterns: List of valid license number regex patterns
        license_description: Human-readable format description
        requires_real_id: Whether state requires REAL ID compliance
        allows_po_box: Whether PO Box addresses are allowed
        special_rules: Dictionary of state-specific special rules
    """
    state_code: str
    state_name: str
    min_age: int = 16
    license_patterns: List[str] = None
    license_description: str = ""
    requires_real_id: bool = True
    allows_po_box: bool = False
    special_rules: Dict[str, Any] = None

    def __post_init__(self):
        if self.license_patterns is None:
            self.license_patterns = []
        if self.special_rules is None:
            self.special_rules = {}


# === STATE-SPECIFIC RULES DATABASE ===

STATE_RULES_DB: Dict[str, StateRules] = {
    "CA": StateRules(
        state_code="CA",
        state_name="California",
        min_age=16,
        license_patterns=[r'^[A-Z]\d{7}$'],
        license_description="1 letter followed by 7 digits (e.g., D1234567)",
        requires_real_id=True,
        allows_po_box=False,
        special_rules={
            "max_renewal_period": 5,  # years
            "senior_renewal_period": 5,  # years for age 70+
            "veteran_indicator": True,
        }
    ),
    "NY": StateRules(
        state_code="NY",
        state_name="New York",
        min_age=16,
        license_patterns=[
            r'^[A-Z]\d{7}$',
            r'^[A-Z]\d{18}$',
            r'^\d{8,9}$',
            r'^\d{16}$',
            r'^[A-Z]{8}$'
        ],
        license_description="Various formats: 1 letter + 7 digits, 1 letter + 18 digits, 8-9 digits, 16 digits, or 8 letters",
        requires_real_id=True,
        allows_po_box=False,
    ),
    "TX": StateRules(
        state_code="TX",
        state_name="Texas",
        min_age=16,
        license_patterns=[r'^\d{7,8}$'],
        license_description="7 or 8 digits (e.g., 12345678)",
        requires_real_id=True,
        allows_po_box=False,
    ),
    "FL": StateRules(
        state_code="FL",
        state_name="Florida",
        min_age=16,
        license_patterns=[r'^[A-Z]\d{12}$'],
        license_description="1 letter followed by 12 digits (e.g., D123456789012)",
        requires_real_id=True,
        allows_po_box=False,
    ),
    "IL": StateRules(
        state_code="IL",
        state_name="Illinois",
        min_age=16,
        license_patterns=[r'^[A-Z]\d{11,12}$'],
        license_description="1 letter followed by 11-12 digits",
        requires_real_id=True,
        allows_po_box=False,
    ),
    "PA": StateRules(
        state_code="PA",
        state_name="Pennsylvania",
        min_age=16,
        license_patterns=[r'^\d{8}$'],
        license_description="8 digits",
        requires_real_id=True,
        allows_po_box=False,
    ),
    "OH": StateRules(
        state_code="OH",
        state_name="Ohio",
        min_age=16,
        license_patterns=[r'^[A-Z]{2}\d{6}$'],
        license_description="2 letters followed by 6 digits",
        requires_real_id=True,
        allows_po_box=False,
    ),
    "GA": StateRules(
        state_code="GA",
        state_name="Georgia",
        min_age=16,
        license_patterns=[r'^\d{7,9}$'],
        license_description="7 to 9 digits",
        requires_real_id=True,
        allows_po_box=False,
    ),
    "MI": StateRules(
        state_code="MI",
        state_name="Michigan",
        min_age=16,
        license_patterns=[r'^[A-Z]\d{10,12}$'],
        license_description="1 letter followed by 10-12 digits",
        requires_real_id=True,
        allows_po_box=False,
    ),
    "NC": StateRules(
        state_code="NC",
        state_name="North Carolina",
        min_age=16,
        license_patterns=[r'^\d{1,12}$'],
        license_description="1 to 12 digits",
        requires_real_id=True,
        allows_po_box=False,
    ),
    "NJ": StateRules(
        state_code="NJ",
        state_name="New Jersey",
        min_age=17,  # NJ has higher minimum age
        license_patterns=[r'^[A-Z]\d{14}$'],
        license_description="1 letter followed by 14 digits",
        requires_real_id=True,
        allows_po_box=False,
    ),
    "VA": StateRules(
        state_code="VA",
        state_name="Virginia",
        min_age=16,
        license_patterns=[r'^[A-Z]\d{9,11}$', r'^\d{9}$'],
        license_description="1 letter + 9-11 digits, or 9 digits",
        requires_real_id=True,
        allows_po_box=False,
    ),
    "WA": StateRules(
        state_code="WA",
        state_name="Washington",
        min_age=16,
        license_patterns=[r'^[A-Z\*]{7}\d{3}[A-Z0-9]{2}$'],
        license_description="7 alphanumeric characters + 3 digits + 2 alphanumeric",
        requires_real_id=True,
        allows_po_box=False,
    ),
    "AZ": StateRules(
        state_code="AZ",
        state_name="Arizona",
        min_age=16,
        license_patterns=[r'^[A-Z]\d{1,8}$', r'^[A-Z]{2}\d{2,5}$', r'^\d{9}$'],
        license_description="Various formats: 1 letter + 1-8 digits, 2 letters + 2-5 digits, or 9 digits",
        requires_real_id=True,
        allows_po_box=False,
    ),
    "MA": StateRules(
        state_code="MA",
        state_name="Massachusetts",
        min_age=16,
        license_patterns=[r'^[A-Z]\d{8}$', r'^\d{9}$'],
        license_description="1 letter + 8 digits, or 9 digits",
        requires_real_id=True,
        allows_po_box=False,
    ),
    "TN": StateRules(
        state_code="TN",
        state_name="Tennessee",
        min_age=16,
        license_patterns=[r'^\d{7,9}$'],
        license_description="7 to 9 digits",
        requires_real_id=True,
        allows_po_box=False,
    ),
    "IN": StateRules(
        state_code="IN",
        state_name="Indiana",
        min_age=16,
        license_patterns=[r'^[A-Z]\d{9}$', r'^\d{9,10}$'],
        license_description="1 letter + 9 digits, or 9-10 digits",
        requires_real_id=True,
        allows_po_box=False,
    ),
    "MO": StateRules(
        state_code="MO",
        state_name="Missouri",
        min_age=16,
        license_patterns=[r'^[A-Z]\d{5,9}R?$', r'^\d{8}[A-Z]{2}$', r'^\d{9}[A-Z]?$'],
        license_description="Various formats with letters and numbers",
        requires_real_id=True,
        allows_po_box=False,
    ),
    "MD": StateRules(
        state_code="MD",
        state_name="Maryland",
        min_age=16,
        license_patterns=[r'^[A-Z]\d{12}$'],
        license_description="1 letter followed by 12 digits",
        requires_real_id=True,
        allows_po_box=False,
    ),
    "WI": StateRules(
        state_code="WI",
        state_name="Wisconsin",
        min_age=16,
        license_patterns=[r'^[A-Z]\d{13}$'],
        license_description="1 letter followed by 13 digits",
        requires_real_id=True,
        allows_po_box=False,
    ),
    "MN": StateRules(
        state_code="MN",
        state_name="Minnesota",
        min_age=16,
        license_patterns=[r'^[A-Z]\d{12}$'],
        license_description="1 letter followed by 12 digits",
        requires_real_id=True,
        allows_po_box=False,
    ),
    "CO": StateRules(
        state_code="CO",
        state_name="Colorado",
        min_age=16,
        license_patterns=[r'^\d{9}$', r'^[A-Z]\d{3,6}$', r'^[A-Z]{2}\d{2,5}$'],
        license_description="9 digits, 1 letter + 3-6 digits, or 2 letters + 2-5 digits",
        requires_real_id=True,
        allows_po_box=False,
    ),
    "AL": StateRules(
        state_code="AL",
        state_name="Alabama",
        min_age=16,
        license_patterns=[r'^\d{1,7}$'],
        license_description="1 to 7 digits",
        requires_real_id=True,
        allows_po_box=False,
    ),
    "SC": StateRules(
        state_code="SC",
        state_name="South Carolina",
        min_age=16,
        license_patterns=[r'^\d{5,11}$'],
        license_description="5 to 11 digits",
        requires_real_id=True,
        allows_po_box=False,
    ),
    "LA": StateRules(
        state_code="LA",
        state_name="Louisiana",
        min_age=16,
        license_patterns=[r'^\d{1,9}$'],
        license_description="1 to 9 digits",
        requires_real_id=True,
        allows_po_box=False,
    ),
    "KY": StateRules(
        state_code="KY",
        state_name="Kentucky",
        min_age=16,
        license_patterns=[r'^[A-Z]\d{8,9}$', r'^\d{9}$'],
        license_description="1 letter + 8-9 digits, or 9 digits",
        requires_real_id=True,
        allows_po_box=False,
    ),
    "OR": StateRules(
        state_code="OR",
        state_name="Oregon",
        min_age=16,
        license_patterns=[r'^\d{1,9}$'],
        license_description="1 to 9 digits",
        requires_real_id=True,
        allows_po_box=False,
    ),
    "OK": StateRules(
        state_code="OK",
        state_name="Oklahoma",
        min_age=16,
        license_patterns=[r'^[A-Z]\d{9}$', r'^\d{9}$'],
        license_description="1 letter + 9 digits, or 9 digits",
        requires_real_id=True,
        allows_po_box=False,
    ),
    "CT": StateRules(
        state_code="CT",
        state_name="Connecticut",
        min_age=16,
        license_patterns=[r'^\d{9}$'],
        license_description="9 digits",
        requires_real_id=True,
        allows_po_box=False,
    ),
    "IA": StateRules(
        state_code="IA",
        state_name="Iowa",
        min_age=16,
        license_patterns=[r'^\d{9}$', r'^\d{3}[A-Z]{2}\d{4}$'],
        license_description="9 digits, or 3 digits + 2 letters + 4 digits",
        requires_real_id=True,
        allows_po_box=False,
    ),
    "MS": StateRules(
        state_code="MS",
        state_name="Mississippi",
        min_age=16,
        license_patterns=[r'^\d{9}$'],
        license_description="9 digits",
        requires_real_id=True,
        allows_po_box=False,
    ),
    "AR": StateRules(
        state_code="AR",
        state_name="Arkansas",
        min_age=16,
        license_patterns=[r'^\d{4,9}$'],
        license_description="4 to 9 digits",
        requires_real_id=True,
        allows_po_box=False,
    ),
    "KS": StateRules(
        state_code="KS",
        state_name="Kansas",
        min_age=16,
        license_patterns=[r'^[A-Z]\d[A-Z]\d[A-Z]$', r'^[A-Z]\d{8}$', r'^\d{9}$'],
        license_description="K0K0K format, 1 letter + 8 digits, or 9 digits",
        requires_real_id=True,
        allows_po_box=False,
    ),
    "UT": StateRules(
        state_code="UT",
        state_name="Utah",
        min_age=16,
        license_patterns=[r'^\d{4,10}$'],
        license_description="4 to 10 digits",
        requires_real_id=True,
        allows_po_box=False,
    ),
    "NV": StateRules(
        state_code="NV",
        state_name="Nevada",
        min_age=16,
        license_patterns=[r'^\d{9,10}$', r'^X\d{8}$'],
        license_description="9-10 digits, or X followed by 8 digits",
        requires_real_id=True,
        allows_po_box=False,
    ),
    "NM": StateRules(
        state_code="NM",
        state_name="New Mexico",
        min_age=16,
        license_patterns=[r'^\d{8,9}$'],
        license_description="8 or 9 digits",
        requires_real_id=True,
        allows_po_box=False,
    ),
    "WV": StateRules(
        state_code="WV",
        state_name="West Virginia",
        min_age=16,
        license_patterns=[r'^\d{7}$', r'^[A-Z]{1,2}\d{5,6}$'],
        license_description="7 digits, or 1-2 letters + 5-6 digits",
        requires_real_id=True,
        allows_po_box=False,
    ),
    "NE": StateRules(
        state_code="NE",
        state_name="Nebraska",
        min_age=16,
        license_patterns=[r'^[A-Z]\d{6,8}$'],
        license_description="1 letter followed by 6-8 digits",
        requires_real_id=True,
        allows_po_box=False,
    ),
    "ID": StateRules(
        state_code="ID",
        state_name="Idaho",
        min_age=16,
        license_patterns=[r'^[A-Z]{2}\d{6}[A-Z]$', r'^\d{9}$'],
        license_description="2 letters + 6 digits + 1 letter, or 9 digits",
        requires_real_id=True,
        allows_po_box=False,
    ),
    "HI": StateRules(
        state_code="HI",
        state_name="Hawaii",
        min_age=16,
        license_patterns=[r'^[A-Z]\d{8}$', r'^\d{9}$'],
        license_description="1 letter + 8 digits, or 9 digits",
        requires_real_id=True,
        allows_po_box=False,
    ),
    "NH": StateRules(
        state_code="NH",
        state_name="New Hampshire",
        min_age=16,
        license_patterns=[r'^\d{2}[A-Z]{3}\d{5}$'],
        license_description="2 digits + 3 letters + 5 digits",
        requires_real_id=True,
        allows_po_box=False,
    ),
    "ME": StateRules(
        state_code="ME",
        state_name="Maine",
        min_age=16,
        license_patterns=[r'^\d{7,8}[A-Z]?$'],
        license_description="7-8 digits, optionally followed by 1 letter",
        requires_real_id=True,
        allows_po_box=False,
    ),
    "RI": StateRules(
        state_code="RI",
        state_name="Rhode Island",
        min_age=16,
        license_patterns=[r'^\d{7}$', r'^[A-Z]\d{6}$'],
        license_description="7 digits, or 1 letter + 6 digits",
        requires_real_id=True,
        allows_po_box=False,
    ),
    "MT": StateRules(
        state_code="MT",
        state_name="Montana",
        min_age=16,
        license_patterns=[r'^\d{9,13}$', r'^[A-Z]{2}\d{13}$'],
        license_description="9-13 digits, or 2 letters + 13 digits",
        requires_real_id=True,
        allows_po_box=False,
    ),
    "DE": StateRules(
        state_code="DE",
        state_name="Delaware",
        min_age=16,
        license_patterns=[r'^\d{1,7}$'],
        license_description="1 to 7 digits",
        requires_real_id=True,
        allows_po_box=False,
    ),
    "SD": StateRules(
        state_code="SD",
        state_name="South Dakota",
        min_age=16,
        license_patterns=[r'^\d{6,10}$'],
        license_description="6 to 10 digits",
        requires_real_id=True,
        allows_po_box=False,
    ),
    "ND": StateRules(
        state_code="ND",
        state_name="North Dakota",
        min_age=16,
        license_patterns=[r'^[A-Z]{3}\d{6}$', r'^\d{9}$'],
        license_description="3 letters + 6 digits, or 9 digits",
        requires_real_id=True,
        allows_po_box=False,
    ),
    "AK": StateRules(
        state_code="AK",
        state_name="Alaska",
        min_age=16,
        license_patterns=[r'^\d{1,7}$'],
        license_description="1 to 7 digits",
        requires_real_id=True,
        allows_po_box=False,
    ),
    "VT": StateRules(
        state_code="VT",
        state_name="Vermont",
        min_age=16,
        license_patterns=[r'^\d{8}[A-Z]?$', r'^\d{7}[A-Z]$'],
        license_description="7-8 digits, optionally followed by 1 letter",
        requires_real_id=True,
        allows_po_box=False,
    ),
    "WY": StateRules(
        state_code="WY",
        state_name="Wyoming",
        min_age=16,
        license_patterns=[r'^\d{9,10}$'],
        license_description="9 or 10 digits",
        requires_real_id=True,
        allows_po_box=False,
    ),
    "DC": StateRules(
        state_code="DC",
        state_name="District of Columbia",
        min_age=16,
        license_patterns=[r'^\d{7}$', r'^\d{9}$'],
        license_description="7 or 9 digits",
        requires_real_id=True,
        allows_po_box=False,
    ),
}


def get_state_rules(state_code: str) -> Optional[StateRules]:
    """
    Get validation rules for a specific state.

    Args:
        state_code: Two-letter state abbreviation

    Returns:
        StateRules object or None if state not found
    """
    return STATE_RULES_DB.get(state_code.upper())


def validate_state_license_format(license_number: str, state_code: str) -> FieldValidationResult:
    """
    Validate license number against state-specific format rules.

    Args:
        license_number: The license number to validate
        state_code: Two-letter state abbreviation

    Returns:
        FieldValidationResult with validation details
    """
    state_rules = get_state_rules(state_code)

    if not state_rules:
        return FieldValidationResult(
            field_name="license_number",
            is_valid=True,
            level=ValidationLevel.INFO,
            message=f"No specific format validation available for state {state_code}"
        )

    # Check if license matches any of the state's patterns
    for pattern in state_rules.license_patterns:
        if re.match(pattern, license_number.upper()):
            return FieldValidationResult(
                field_name="license_number",
                is_valid=True,
                level=ValidationLevel.INFO,
                message=f"Valid {state_code} license format: {state_rules.license_description}"
            )

    # No match found
    return FieldValidationResult(
        field_name="license_number",
        is_valid=False,
        level=ValidationLevel.WARNING,
        message=f"License number '{license_number}' does not match {state_code} format. "
                f"Expected: {state_rules.license_description}",
        suggestions=[f"Format should be: {state_rules.license_description}"]
    )


def validate_state_specific_rules(data: Dict[str, Any]) -> List[FieldValidationResult]:
    """
    Apply all state-specific validation rules.

    Args:
        data: License data dictionary

    Returns:
        List of validation results
    """
    results = []
    state_code = data.get('state', '').upper()

    if not state_code:
        return results

    state_rules = get_state_rules(state_code)
    if not state_rules:
        return results

    # Check minimum age requirement
    if 'date_of_birth' in data and 'issue_date' in data:
        from datetime import datetime, date

        dob = data['date_of_birth']
        issue = data['issue_date']

        # Parse dates if strings
        if isinstance(dob, str):
            dob = datetime.strptime(dob, "%Y-%m-%d").date()
        if isinstance(issue, str):
            issue = datetime.strptime(issue, "%Y-%m-%d").date()

        age_at_issue = (issue - dob).days / 365.25

        if age_at_issue < state_rules.min_age:
            results.append(FieldValidationResult(
                field_name="date_of_birth",
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"Age at issue ({age_at_issue:.1f} years) is below {state_code} "
                        f"minimum of {state_rules.min_age} years"
            ))

    # Check PO Box restriction
    if not state_rules.allows_po_box and 'address' in data:
        address = data['address']
        if re.search(r'\bP\.?O\.?\s*BOX\b', address, re.IGNORECASE):
            results.append(FieldValidationResult(
                field_name="address",
                is_valid=False,
                level=ValidationLevel.WARNING,
                message=f"{state_code} does not accept PO Box addresses"
            ))

    # Check REAL ID compliance
    if state_rules.requires_real_id and 'compliance_type' in data:
        if data['compliance_type'] != 'F':
            results.append(FieldValidationResult(
                field_name="compliance_type",
                is_valid=True,
                level=ValidationLevel.INFO,
                message=f"{state_code} requires REAL ID compliance (use 'F' for full compliance)"
            ))

    return results
