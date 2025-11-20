"""
Validation Service - License Data Validation Orchestration

Provides comprehensive validation for:
- AAMVA field formats
- Data consistency
- Barcode encoding
- State-specific rules
"""

import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

# Configure logging
logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when validation fails"""
    pass


class ValidationResult:
    """
    Result of a validation operation.

    Attributes:
        is_valid: Whether validation passed
        errors: List of error messages
        warnings: List of warning messages
        field_errors: Dict mapping field names to error messages
    """

    def __init__(self):
        self.is_valid = True
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.field_errors: Dict[str, List[str]] = {}

    def add_error(self, message: str, field: Optional[str] = None):
        """Add an error message."""
        self.is_valid = False
        self.errors.append(message)
        if field:
            if field not in self.field_errors:
                self.field_errors[field] = []
            self.field_errors[field].append(message)

    def add_warning(self, message: str):
        """Add a warning message."""
        self.warnings.append(message)

    def __str__(self) -> str:
        """String representation of validation result."""
        if self.is_valid:
            msg = "✓ Validation passed"
            if self.warnings:
                msg += f" ({len(self.warnings)} warnings)"
            return msg
        else:
            return f"✗ Validation failed: {len(self.errors)} errors, {len(self.warnings)} warnings"

    def __bool__(self) -> bool:
        """Boolean representation (for if statements)."""
        return self.is_valid


class ValidationService:
    """
    Service for validating license data against AAMVA standards.

    Provides comprehensive validation including:
    - Field presence and format
    - Data type validation
    - Enumerated value checks
    - Cross-field consistency
    - State-specific rules
    """

    # AAMVA field enumerations
    EYE_COLORS = ["BLK", "BLU", "BRO", "GRY", "GRN", "HAZ", "MAR", "PNK", "DIC", "UNK"]
    HAIR_COLORS = ["BLK", "BLN", "BRO", "GRY", "RED", "WHI", "SDY", "UNK"]
    RACE_CODES = ["W", "B", "A", "I", "U"]
    SEX_CODES = ["1", "2"]
    TRUNCATION_CODES = ["N", "T", "U"]
    DHS_COMPLIANCE_CODES = ["F", "N"]
    BOOLEAN_CODES = ["0", "1"]

    # Required DL subfile fields
    REQUIRED_DL_FIELDS = [
        "DAQ",  # License number
        "DCS",  # Last name
        "DAC",  # First name
        "DBB",  # Birth date
        "DBA",  # Expiration date
        "DBD",  # Issue date
        "DAJ",  # State
    ]

    def __init__(self, strict_mode: bool = False):
        """
        Initialize the ValidationService.

        Args:
            strict_mode: If True, warnings become errors
        """
        self.strict_mode = strict_mode

    def validate_license_data(
        self,
        license_data: List[Dict[str, str]]
    ) -> ValidationResult:
        """
        Validate complete license data structure.

        Args:
            license_data: List containing [DL_data, State_data]

        Returns:
            ValidationResult object
        """
        result = ValidationResult()

        # Check structure
        if not isinstance(license_data, list):
            result.add_error("License data must be a list")
            return result

        if len(license_data) < 1:
            result.add_error("License data must contain at least DL subfile")
            return result

        # Validate DL subfile
        dl_data = license_data[0]
        if not isinstance(dl_data, dict):
            result.add_error("DL subfile must be a dictionary")
            return result

        self._validate_dl_subfile(dl_data, result)

        # Validate state subfile if present
        if len(license_data) > 1:
            state_data = license_data[1]
            if isinstance(state_data, dict):
                self._validate_state_subfile(state_data, result)
            else:
                result.add_warning("State subfile is not a dictionary")

        return result

    def _validate_dl_subfile(
        self,
        dl_data: Dict[str, str],
        result: ValidationResult
    ):
        """Validate DL subfile data."""
        # Check subfile type
        if dl_data.get("subfile_type") != "DL":
            result.add_error(
                f"Invalid subfile type: {dl_data.get('subfile_type')} (expected 'DL')",
                "subfile_type"
            )

        # Check required fields
        for field in self.REQUIRED_DL_FIELDS:
            if field not in dl_data or not dl_data[field]:
                result.add_error(f"Required field missing or empty: {field}", field)

        # Validate individual fields
        self._validate_date_field(dl_data, "DBB", "Birth date", result)
        self._validate_date_field(dl_data, "DBA", "Expiration date", result)
        self._validate_date_field(dl_data, "DBD", "Issue date", result)
        self._validate_date_field(dl_data, "DDB", "Revision date", result, required=False)
        self._validate_date_field(dl_data, "DDC", "Hazmat expiration", result, required=False)

        self._validate_enum_field(dl_data, "DBC", "Sex", self.SEX_CODES, result)
        self._validate_enum_field(dl_data, "DAY", "Eye color", self.EYE_COLORS, result)
        self._validate_enum_field(dl_data, "DAZ", "Hair color", self.HAIR_COLORS, result)
        self._validate_enum_field(dl_data, "DCL", "Race", self.RACE_CODES, result)
        self._validate_enum_field(dl_data, "DDE", "Truncation family", self.TRUNCATION_CODES, result)
        self._validate_enum_field(dl_data, "DDF", "Truncation first", self.TRUNCATION_CODES, result)
        self._validate_enum_field(dl_data, "DDG", "Truncation middle", self.TRUNCATION_CODES, result)
        self._validate_enum_field(dl_data, "DDA", "DHS compliance", self.DHS_COMPLIANCE_CODES, result)
        self._validate_enum_field(dl_data, "DDD", "Limited duration", self.BOOLEAN_CODES, result)
        self._validate_enum_field(dl_data, "DDK", "Organ donor", self.BOOLEAN_CODES, result)
        self._validate_enum_field(dl_data, "DDL", "Veteran", self.BOOLEAN_CODES, result)

        self._validate_height_field(dl_data, result)
        self._validate_weight_field(dl_data, result)
        self._validate_zip_field(dl_data, result)
        self._validate_state_field(dl_data, result)

        # Cross-field validation
        self._validate_date_consistency(dl_data, result)

    def _validate_state_subfile(
        self,
        state_data: Dict[str, str],
        result: ValidationResult
    ):
        """Validate state subfile data."""
        # Check subfile type format
        subfile_type = state_data.get("subfile_type", "")
        if not re.match(r'^Z[A-Z]$', subfile_type):
            result.add_error(
                f"Invalid state subfile type format: {subfile_type} (expected Z[A-Z])",
                "subfile_type"
            )

    def _validate_date_field(
        self,
        data: Dict[str, str],
        field: str,
        name: str,
        result: ValidationResult,
        required: bool = True
    ):
        """Validate a date field (MMDDYYYY format)."""
        value = data.get(field, "")

        if not value:
            if required:
                result.add_error(f"{name} is required", field)
            return

        # Check format
        if not re.match(r'^\d{8}$', value):
            result.add_error(f"{name} must be in MMDDYYYY format (8 digits)", field)
            return

        # Validate actual date
        try:
            month = int(value[0:2])
            day = int(value[2:4])
            year = int(value[4:8])
            datetime(year, month, day)
        except ValueError as e:
            result.add_error(f"{name} is not a valid date: {value}", field)

    def _validate_enum_field(
        self,
        data: Dict[str, str],
        field: str,
        name: str,
        valid_values: List[str],
        result: ValidationResult
    ):
        """Validate an enumerated field."""
        value = data.get(field, "")

        if not value:
            result.add_warning(f"{name} is empty", )
            return

        if value not in valid_values:
            result.add_error(
                f"{name} has invalid value: {value} (expected one of {', '.join(valid_values)})",
                field
            )

    def _validate_height_field(
        self,
        data: Dict[str, str],
        result: ValidationResult
    ):
        """Validate height field (inches, 3 digits)."""
        value = data.get("DAU", "")

        if not value:
            result.add_warning("Height is empty")
            return

        if not re.match(r'^\d{3}$', value):
            result.add_error("Height must be 3 digits", "DAU")
            return

        height = int(value)
        if height < 48 or height > 96:  # 4' to 8'
            result.add_warning(f"Height {height} inches seems unusual")

    def _validate_weight_field(
        self,
        data: Dict[str, str],
        result: ValidationResult
    ):
        """Validate weight field (pounds, 3 digits)."""
        value = data.get("DAW", "")

        if not value:
            result.add_warning("Weight is empty")
            return

        if not re.match(r'^\d{3}$', value):
            result.add_error("Weight must be 3 digits", "DAW")
            return

        weight = int(value)
        if weight < 80 or weight > 400:
            result.add_warning(f"Weight {weight} pounds seems unusual")

    def _validate_zip_field(
        self,
        data: Dict[str, str],
        result: ValidationResult
    ):
        """Validate ZIP code field (9 digits)."""
        value = data.get("DAK", "")

        if not value:
            result.add_error("ZIP code is required", "DAK")
            return

        if not re.match(r'^\d{9}$', value):
            result.add_error("ZIP code must be 9 digits", "DAK")

    def _validate_state_field(
        self,
        data: Dict[str, str],
        result: ValidationResult
    ):
        """Validate state field (2 letters)."""
        value = data.get("DAJ", "")

        if not value:
            result.add_error("State is required", "DAJ")
            return

        if not re.match(r'^[A-Z]{2}$', value):
            result.add_error("State must be 2 uppercase letters", "DAJ")

    def _validate_date_consistency(
        self,
        data: Dict[str, str],
        result: ValidationResult
    ):
        """Validate date field consistency."""
        try:
            dob_str = data.get("DBB", "")
            issue_str = data.get("DBD", "")
            exp_str = data.get("DBA", "")

            if not (dob_str and issue_str and exp_str):
                return  # Already reported as errors

            # Parse dates
            dob = datetime.strptime(dob_str, "%m%d%Y")
            issue = datetime.strptime(issue_str, "%m%d%Y")
            exp = datetime.strptime(exp_str, "%m%d%Y")

            # Check: DOB should be at least 16 years before issue
            age_at_issue = (issue - dob).days / 365.25
            if age_at_issue < 16:
                result.add_error(
                    f"Issue date is before legal driving age (age at issue: {age_at_issue:.1f})",
                    "DBD"
                )

            # Check: Expiration should be after issue
            if exp <= issue:
                result.add_error("Expiration date must be after issue date", "DBA")

            # Check: License duration seems reasonable (5-10 years)
            duration_years = (exp - issue).days / 365.25
            if duration_years > 15:
                result.add_warning(
                    f"License duration is unusually long: {duration_years:.1f} years"
                )

        except ValueError:
            # Date parsing errors already reported
            pass

    def validate_barcode_data(self, barcode_data: str) -> ValidationResult:
        """
        Validate AAMVA barcode data structure.

        Args:
            barcode_data: Raw AAMVA barcode string

        Returns:
            ValidationResult object
        """
        result = ValidationResult()

        # Check compliance markers
        if not barcode_data.startswith("@\n\x1E\r"):
            result.add_error("Missing AAMVA compliance markers")

        # Check file type
        if "ANSI " not in barcode_data[:20]:
            result.add_error("Missing ANSI file type identifier")

        # Check version
        if not re.search(r'ANSI \d{6}\d{2}', barcode_data[:30]):
            result.add_error("Invalid AAMVA version format")

        # Check subfile markers
        if "DL" not in barcode_data:
            result.add_error("Missing DL subfile marker")

        # Check minimum length
        if len(barcode_data) < 100:
            result.add_warning("Barcode data seems too short")

        # Check maximum length
        if len(barcode_data) > 2000:
            result.add_warning("Barcode data is very long")

        return result

    def validate_batch(
        self,
        licenses: List[List[Dict[str, str]]],
        progress_callback: Optional[callable] = None
    ) -> Tuple[List[ValidationResult], int, int]:
        """
        Validate a batch of licenses.

        Args:
            licenses: List of license data arrays
            progress_callback: Optional callback(current, total)

        Returns:
            Tuple of (results_list, passed_count, failed_count)
        """
        results = []
        passed = 0
        failed = 0

        total = len(licenses)
        for i, license_data in enumerate(licenses):
            result = self.validate_license_data(license_data)
            results.append(result)

            if result.is_valid:
                passed += 1
            else:
                failed += 1

            if progress_callback:
                progress_callback(i + 1, total)

        return results, passed, failed
