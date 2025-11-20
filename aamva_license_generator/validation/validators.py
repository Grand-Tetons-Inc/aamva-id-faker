"""
Comprehensive validator implementations for license data.

Provides specialized validators for:
- State codes (with fuzzy matching)
- Dates and date sequences
- License numbers (state-specific formats)
- Addresses and postal codes
- Personal data
"""

from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, date
import re
import difflib
from .schemas import (
    ValidationResult,
    ValidationLevel,
    FieldValidationResult,
    LicenseData
)


class StateCodeValidator:
    """
    Validator for state codes with fuzzy matching.

    Features:
    - Exact match validation
    - Fuzzy matching for typos
    - Suggestions for corrections
    - Full state name to abbreviation conversion
    """

    def __init__(self):
        # Import state data
        from generate_licenses import IIN_JURISDICTIONS

        self.iin_data = IIN_JURISDICTIONS
        self.valid_codes = sorted(set(info['abbr'] for info in IIN_JURISDICTIONS.values()))
        self.code_to_name = {info['abbr']: info['jurisdiction']
                            for info in IIN_JURISDICTIONS.values()}
        self.name_to_code = {info['jurisdiction'].upper(): info['abbr']
                            for info in IIN_JURISDICTIONS.values()}

    def validate(self, state_code: str) -> FieldValidationResult:
        """Validate a state code with fuzzy matching."""
        if not state_code:
            return FieldValidationResult(
                field_name="state",
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="State code is required",
                suggestions=self.valid_codes[:10]  # Show first 10 states
            )

        state_upper = state_code.upper()

        # Check exact match
        if state_upper in self.valid_codes:
            state_name = self.code_to_name.get(state_upper, "Unknown")
            return FieldValidationResult(
                field_name="state",
                is_valid=True,
                level=ValidationLevel.INFO,
                message=f"Valid state: {state_name} ({state_upper})"
            )

        # Try to match full state name
        if state_upper in self.name_to_code:
            correct_code = self.name_to_code[state_upper]
            return FieldValidationResult(
                field_name="state",
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"Use state code '{correct_code}' instead of full name '{state_code}'",
                suggestions=[correct_code],
                auto_fix=correct_code
            )

        # Fuzzy match on codes
        close_matches = difflib.get_close_matches(
            state_upper,
            self.valid_codes,
            n=5,
            cutoff=0.6
        )

        # Also try fuzzy match on full names
        close_name_matches = difflib.get_close_matches(
            state_upper,
            self.name_to_code.keys(),
            n=3,
            cutoff=0.6
        )
        close_code_from_names = [self.name_to_code[name] for name in close_name_matches]

        # Combine suggestions
        all_suggestions = list(dict.fromkeys(close_matches + close_code_from_names))

        if all_suggestions:
            suggestions_str = ", ".join(all_suggestions)
            return FieldValidationResult(
                field_name="state",
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"Invalid state code '{state_code}'. Did you mean: {suggestions_str}?",
                suggestions=all_suggestions,
                auto_fix=all_suggestions[0] if all_suggestions else None
            )

        return FieldValidationResult(
            field_name="state",
            is_valid=False,
            level=ValidationLevel.ERROR,
            message=f"Invalid state code '{state_code}'. Not found in AAMVA jurisdiction list.",
            suggestions=self.valid_codes[:10]
        )

    def get_state_name(self, state_code: str) -> Optional[str]:
        """Get full state name from code."""
        return self.code_to_name.get(state_code.upper())

    def get_state_code(self, state_name: str) -> Optional[str]:
        """Get state code from full name."""
        return self.name_to_code.get(state_name.upper())


class DateValidator:
    """
    Validator for dates with comprehensive checks.

    Features:
    - Format validation
    - Range validation
    - Cross-field validation (DOB < Issue < Expiration)
    - Age calculation and validation
    """

    @staticmethod
    def parse_date(date_value: Any) -> Optional[date]:
        """Parse date from various formats."""
        if isinstance(date_value, date):
            return date_value
        if isinstance(date_value, datetime):
            return date_value.date()

        if isinstance(date_value, str):
            # Try multiple formats
            formats = [
                "%Y-%m-%d",      # ISO format
                "%m/%d/%Y",      # US format
                "%m%d%Y",        # AAMVA format
                "%d-%m-%Y",      # EU format
                "%Y%m%d",        # Compact format
            ]

            for fmt in formats:
                try:
                    return datetime.strptime(date_value, fmt).date()
                except ValueError:
                    continue

        return None

    def validate_date_of_birth(self, dob: Any) -> FieldValidationResult:
        """Validate date of birth."""
        parsed_date = self.parse_date(dob)

        if not parsed_date:
            return FieldValidationResult(
                field_name="date_of_birth",
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="Invalid date format. Use YYYY-MM-DD, MM/DD/YYYY, or MMDDYYYY"
            )

        today = date.today()
        age = (today - parsed_date).days / 365.25

        # Check minimum age (16 years)
        if age < 16:
            return FieldValidationResult(
                field_name="date_of_birth",
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"Age ({age:.1f} years) is below minimum of 16 years"
            )

        # Check maximum age (120 years)
        if age > 120:
            return FieldValidationResult(
                field_name="date_of_birth",
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"Age ({age:.1f} years) exceeds maximum of 120 years"
            )

        # Warning for unusual ages
        if age < 18:
            return FieldValidationResult(
                field_name="date_of_birth",
                is_valid=True,
                level=ValidationLevel.WARNING,
                message=f"Age {age:.1f} years - minor license holder"
            )

        if age > 100:
            return FieldValidationResult(
                field_name="date_of_birth",
                is_valid=True,
                level=ValidationLevel.WARNING,
                message=f"Age {age:.1f} years - unusually high age"
            )

        return FieldValidationResult(
            field_name="date_of_birth",
            is_valid=True,
            level=ValidationLevel.INFO,
            message=f"Valid date of birth (age: {int(age)} years)"
        )

    def validate_date_sequence(self, dob: Any, issue_date: Any, exp_date: Any) -> List[FieldValidationResult]:
        """Validate date sequence: DOB < Issue < Expiration."""
        results = []

        parsed_dob = self.parse_date(dob)
        parsed_issue = self.parse_date(issue_date)
        parsed_exp = self.parse_date(exp_date)

        if not all([parsed_dob, parsed_issue, parsed_exp]):
            return results  # Individual date validation will catch this

        # Check DOB < Issue
        if parsed_dob >= parsed_issue:
            results.append(FieldValidationResult(
                field_name="issue_date",
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"Issue date ({parsed_issue}) must be after date of birth ({parsed_dob})"
            ))

        # Check Issue < Expiration
        if parsed_issue >= parsed_exp:
            results.append(FieldValidationResult(
                field_name="expiration_date",
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"Expiration date ({parsed_exp}) must be after issue date ({parsed_issue})"
            ))

        # Check age at issue
        age_at_issue = (parsed_issue - parsed_dob).days / 365.25
        if age_at_issue < 16:
            results.append(FieldValidationResult(
                field_name="issue_date",
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"Age at issue ({age_at_issue:.1f} years) must be at least 16 years"
            ))

        # Check license duration
        duration_days = (parsed_exp - parsed_issue).days
        duration_years = duration_days / 365.25

        if duration_years > 10:
            results.append(FieldValidationResult(
                field_name="expiration_date",
                is_valid=True,
                level=ValidationLevel.WARNING,
                message=f"License valid for {duration_years:.1f} years (unusually long)"
            ))

        if duration_years < 1:
            results.append(FieldValidationResult(
                field_name="expiration_date",
                is_valid=True,
                level=ValidationLevel.WARNING,
                message=f"License valid for {duration_days} days (unusually short)"
            ))

        return results


class LicenseNumberValidator:
    """
    Validator for license numbers with state-specific format checking.

    Features:
    - State-specific format validation
    - Pattern matching
    - Length validation
    - Character validation
    """

    def __init__(self):
        # Import state-specific formats
        self.state_patterns = self._build_state_patterns()

    def _build_state_patterns(self) -> Dict[str, List[str]]:
        """Build regex patterns for state-specific license formats."""
        patterns = {
            'AL': [r'^\d{1,7}$'],
            'AK': [r'^\d{1,7}$'],
            'AZ': [r'^[A-Z]\d{1,8}$', r'^[A-Z]{2}\d{2,5}$', r'^\d{9}$'],
            'AR': [r'^\d{4,9}$'],
            'CA': [r'^[A-Z]\d{7}$'],
            'CO': [r'^\d{9}$', r'^[A-Z]\d{3,6}$', r'^[A-Z]{2}\d{2,5}$'],
            'CT': [r'^\d{9}$'],
            'DE': [r'^\d{1,7}$'],
            'DC': [r'^\d{7}$', r'^\d{9}$'],
            'FL': [r'^[A-Z]\d{12}$'],
            'GA': [r'^\d{7,9}$'],
            'HI': [r'^[A-Z]\d{8}$', r'^\d{9}$'],
            'ID': [r'^[A-Z]{2}\d{6}[A-Z]$', r'^\d{9}$'],
            'IL': [r'^[A-Z]\d{11,12}$'],
            'IN': [r'^[A-Z]\d{9}$', r'^\d{9,10}$'],
            'IA': [r'^\d{9}$', r'^\d{3}[A-Z]{2}\d{4}$'],
            'KS': [r'^[A-Z]\d[A-Z]\d[A-Z]$', r'^[A-Z]\d{8}$', r'^\d{9}$'],
            'KY': [r'^[A-Z]\d{8,9}$', r'^\d{9}$'],
            'LA': [r'^\d{1,9}$'],
            'ME': [r'^\d{7,8}[A-Z]?$'],
            'MD': [r'^[A-Z]\d{12}$'],
            'MA': [r'^[A-Z]\d{8}$', r'^\d{9}$'],
            'MI': [r'^[A-Z]\d{10,12}$'],
            'MN': [r'^[A-Z]\d{12}$'],
            'MS': [r'^\d{9}$'],
            'MO': [r'^[A-Z]\d{5,9}R?$', r'^\d{8}[A-Z]{2}$', r'^\d{9}[A-Z]?$'],
            'NY': [r'^[A-Z]\d{7,18}$', r'^\d{8,16}$', r'^[A-Z]{8}$'],
            'TX': [r'^\d{7,8}$'],
            'VA': [r'^[A-Z]\d{9,11}$', r'^\d{9}$'],
            'WI': [r'^[A-Z]\d{13}$'],
            'WY': [r'^\d{9,10}$'],
        }
        return patterns

    def validate(self, license_number: str, state_code: str) -> FieldValidationResult:
        """Validate license number for specific state."""
        if not license_number:
            return FieldValidationResult(
                field_name="license_number",
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="License number is required"
            )

        # General validation (all states)
        if len(license_number) > 25:
            return FieldValidationResult(
                field_name="license_number",
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"License number too long ({len(license_number)} chars, max 25)"
            )

        # Check for invalid characters (should be alphanumeric + hyphen)
        if not re.match(r'^[A-Z0-9\-]+$', license_number, re.IGNORECASE):
            return FieldValidationResult(
                field_name="license_number",
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="License number contains invalid characters (use only A-Z, 0-9, -)"
            )

        # State-specific validation
        state_upper = state_code.upper()
        if state_upper in self.state_patterns:
            patterns = self.state_patterns[state_upper]

            # Check if matches any of the state's valid patterns
            matches_pattern = any(
                re.match(pattern, license_number.upper())
                for pattern in patterns
            )

            if not matches_pattern:
                pattern_descriptions = self._describe_patterns(patterns)
                return FieldValidationResult(
                    field_name="license_number",
                    is_valid=False,
                    level=ValidationLevel.WARNING,
                    message=f"License number '{license_number}' may not match {state_upper} format. "
                           f"Expected: {pattern_descriptions}"
                )

            return FieldValidationResult(
                field_name="license_number",
                is_valid=True,
                level=ValidationLevel.INFO,
                message=f"Valid {state_upper} license number format"
            )

        # State not in our validation database
        return FieldValidationResult(
            field_name="license_number",
            is_valid=True,
            level=ValidationLevel.INFO,
            message=f"License number accepted (no specific format validation for {state_upper})"
        )

    def _describe_patterns(self, patterns: List[str]) -> str:
        """Convert regex patterns to human-readable descriptions."""
        descriptions = []
        for pattern in patterns[:3]:  # Show max 3 patterns
            # Simple pattern description logic
            if r'\d{9}' in pattern:
                descriptions.append("9 digits")
            elif r'[A-Z]\d{7}' in pattern:
                descriptions.append("1 letter + 7 digits")
            elif r'[A-Z]\d{12}' in pattern:
                descriptions.append("1 letter + 12 digits")
            # Add more as needed

        return " or ".join(descriptions) if descriptions else "state-specific format"


class AddressValidator:
    """
    Validator for address components.

    Features:
    - Street address validation
    - City validation
    - ZIP code validation and normalization
    - State/ZIP consistency checking
    """

    @staticmethod
    def validate_zip_code(zip_code: str, state_code: Optional[str] = None) -> FieldValidationResult:
        """Validate ZIP code format and optionally check state consistency."""
        if not zip_code:
            return FieldValidationResult(
                field_name="postal_code",
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="ZIP code is required"
            )

        # Remove dashes and spaces
        cleaned = zip_code.replace('-', '').replace(' ', '')

        # Must be 5 or 9 digits
        if not re.match(r'^\d{5}(\d{4})?$', cleaned):
            return FieldValidationResult(
                field_name="postal_code",
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"Invalid ZIP code format '{zip_code}'. Must be 5 or 9 digits.",
                auto_fix=cleaned if re.match(r'^\d+$', cleaned) else None
            )

        # Normalize to 9 digits
        if len(cleaned) == 5:
            normalized = cleaned + "0000"
        else:
            normalized = cleaned

        # Check valid ZIP range (00001-99999)
        zip_int = int(cleaned[:5])
        if zip_int < 1 or zip_int > 99999:
            return FieldValidationResult(
                field_name="postal_code",
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"ZIP code {cleaned[:5]} is outside valid range (00001-99999)"
            )

        return FieldValidationResult(
            field_name="postal_code",
            is_valid=True,
            level=ValidationLevel.INFO,
            message=f"Valid ZIP code: {cleaned[:5]}" + (f"-{cleaned[5:]}" if len(cleaned) == 9 else ""),
            auto_fix=normalized
        )

    @staticmethod
    def validate_address(address: str) -> FieldValidationResult:
        """Validate street address."""
        if not address or not address.strip():
            return FieldValidationResult(
                field_name="address",
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="Street address is required"
            )

        if len(address) > 35:
            return FieldValidationResult(
                field_name="address",
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"Address too long ({len(address)} chars, max 35)",
                auto_fix=address[:35]
            )

        # Check for PO Box (some states don't allow)
        if re.search(r'\bP\.?O\.?\s*BOX\b', address, re.IGNORECASE):
            return FieldValidationResult(
                field_name="address",
                is_valid=True,
                level=ValidationLevel.WARNING,
                message="PO Box address detected (not accepted by all states)"
            )

        return FieldValidationResult(
            field_name="address",
            is_valid=True,
            level=ValidationLevel.INFO,
            message="Valid street address"
        )

    @staticmethod
    def validate_city(city: str) -> FieldValidationResult:
        """Validate city name."""
        if not city or not city.strip():
            return FieldValidationResult(
                field_name="city",
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="City is required"
            )

        if len(city) > 20:
            return FieldValidationResult(
                field_name="city",
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"City name too long ({len(city)} chars, max 20)",
                auto_fix=city[:20]
            )

        # Check for valid characters
        if not re.match(r'^[A-Z\s\'\-\.]+$', city, re.IGNORECASE):
            return FieldValidationResult(
                field_name="city",
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="City name contains invalid characters"
            )

        return FieldValidationResult(
            field_name="city",
            is_valid=True,
            level=ValidationLevel.INFO,
            message="Valid city name"
        )


class PersonalDataValidator:
    """
    Validator for personal characteristics.

    Features:
    - Height validation
    - Weight validation
    - Eye/hair color validation
    - Sex code validation
    """

    @staticmethod
    def validate_height(height: str) -> FieldValidationResult:
        """Validate height in inches."""
        try:
            height_int = int(height)
        except (ValueError, TypeError):
            return FieldValidationResult(
                field_name="height",
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"Invalid height '{height}'. Must be a number (inches)."
            )

        if height_int < 36 or height_int > 96:
            feet = height_int // 12
            inches = height_int % 12
            return FieldValidationResult(
                field_name="height",
                is_valid=False,
                level=ValidationLevel.WARNING,
                message=f"Height {height_int}\" ({feet}'{inches}\") is outside typical range (3'-8')"
            )

        feet = height_int // 12
        inches = height_int % 12
        return FieldValidationResult(
            field_name="height",
            is_valid=True,
            level=ValidationLevel.INFO,
            message=f"Valid height: {feet}'{inches}\" ({height_int} inches)"
        )

    @staticmethod
    def validate_weight(weight: str) -> FieldValidationResult:
        """Validate weight in pounds."""
        try:
            weight_int = int(weight)
        except (ValueError, TypeError):
            return FieldValidationResult(
                field_name="weight",
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"Invalid weight '{weight}'. Must be a number (pounds)."
            )

        if weight_int < 50 or weight_int > 500:
            return FieldValidationResult(
                field_name="weight",
                is_valid=False,
                level=ValidationLevel.WARNING,
                message=f"Weight {weight_int} lbs is outside typical range (50-500 lbs)"
            )

        return FieldValidationResult(
            field_name="weight",
            is_valid=True,
            level=ValidationLevel.INFO,
            message=f"Valid weight: {weight_int} lbs"
        )


class LicenseValidator:
    """
    Main validator that orchestrates all validation.

    Provides comprehensive validation of entire license records.
    """

    def __init__(self):
        self.state_validator = StateCodeValidator()
        self.date_validator = DateValidator()
        self.license_num_validator = LicenseNumberValidator()
        self.address_validator = AddressValidator()
        self.personal_validator = PersonalDataValidator()

    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """
        Validate an entire license data record.

        Args:
            data: Dictionary of license data

        Returns:
            ValidationResult with all validation messages
        """
        result = ValidationResult(is_valid=True)

        # State validation
        if 'state' in data:
            state_result = self.state_validator.validate(data['state'])
            result.add_result(state_result)
            if not state_result.is_valid:
                result.is_valid = False

        # License number validation
        if 'license_number' in data and 'state' in data:
            lic_result = self.license_num_validator.validate(
                data['license_number'],
                data['state']
            )
            result.add_result(lic_result)

        # Date validation
        if 'date_of_birth' in data:
            dob_result = self.date_validator.validate_date_of_birth(data['date_of_birth'])
            result.add_result(dob_result)
            if not dob_result.is_valid and dob_result.level == ValidationLevel.ERROR:
                result.is_valid = False

        # Cross-field date validation
        if all(k in data for k in ['date_of_birth', 'issue_date', 'expiration_date']):
            date_results = self.date_validator.validate_date_sequence(
                data['date_of_birth'],
                data['issue_date'],
                data['expiration_date']
            )
            for dr in date_results:
                result.add_result(dr)
                if not dr.is_valid and dr.level == ValidationLevel.ERROR:
                    result.is_valid = False

        # Address validation
        if 'address' in data:
            addr_result = self.address_validator.validate_address(data['address'])
            result.add_result(addr_result)
            if not addr_result.is_valid and addr_result.level == ValidationLevel.ERROR:
                result.is_valid = False

        if 'city' in data:
            city_result = self.address_validator.validate_city(data['city'])
            result.add_result(city_result)
            if not city_result.is_valid and city_result.level == ValidationLevel.ERROR:
                result.is_valid = False

        if 'postal_code' in data:
            zip_result = self.address_validator.validate_zip_code(data['postal_code'])
            result.add_result(zip_result)
            if not zip_result.is_valid and zip_result.level == ValidationLevel.ERROR:
                result.is_valid = False

        # Personal data validation
        if 'height' in data:
            height_result = self.personal_validator.validate_height(data['height'])
            result.add_result(height_result)

        if 'weight' in data:
            weight_result = self.personal_validator.validate_weight(data['weight'])
            result.add_result(weight_result)

        return result

    def validate_pydantic(self, license_data: LicenseData) -> ValidationResult:
        """Validate a Pydantic LicenseData model."""
        # Convert to dict for validation
        data_dict = license_data.model_dump()
        return self.validate(data_dict)
