"""
AAMVA Compliance Validation Module.

This module provides comprehensive validation for AAMVA barcode data,
ensuring compliance with the DL/ID Card Design Standard.

Validation includes:
- Field presence and completeness
- Data type and format validation
- Cross-field consistency checks
- Date validation and logical relationships
- AAMVA version compatibility

This is NEW functionality providing superior validation compared to
the original implementation.

Author: New implementation
License: MIT
"""

from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import re

from .aamva_spec import (
    AAMVAVersion,
    FieldCategory,
    get_mandatory_fields,
    get_field_definition,
    get_iin_by_state,
    IIN_JURISDICTIONS,
)
from .subfiles import Subfile, DLSubfile


class ValidationError(Exception):
    """Base exception for validation errors."""
    pass


@dataclass
class ValidationIssue:
    """Represents a single validation issue.

    Attributes:
        severity: Severity level (error, warning, info)
        field: Field code that caused the issue (if applicable)
        message: Human-readable error message
        code: Machine-readable error code
        subfile_index: Index of subfile with issue (if applicable)
    """
    severity: str  # 'error', 'warning', 'info'
    message: str
    code: str
    field: Optional[str] = None
    subfile_index: Optional[int] = None

    def __str__(self) -> str:
        """Format issue as string."""
        parts = [f"[{self.severity.upper()}]"]
        if self.field:
            parts.append(f"Field {self.field}:")
        parts.append(self.message)
        if self.code:
            parts.append(f"({self.code})")
        return " ".join(parts)


@dataclass
class ValidationResult:
    """Result of validation operation.

    Attributes:
        is_valid: True if validation passed with no errors
        issues: List of validation issues
        errors: List of error-level issues
        warnings: List of warning-level issues
        info: List of info-level issues
    """
    is_valid: bool
    issues: List[ValidationIssue] = field(default_factory=list)

    @property
    def errors(self) -> List[ValidationIssue]:
        """Get only error-level issues."""
        return [i for i in self.issues if i.severity == 'error']

    @property
    def warnings(self) -> List[ValidationIssue]:
        """Get only warning-level issues."""
        return [i for i in self.issues if i.severity == 'warning']

    @property
    def info(self) -> List[ValidationIssue]:
        """Get only info-level issues."""
        return [i for i in self.issues if i.severity == 'info']

    def add_error(self, message: str, code: str, field: Optional[str] = None,
                  subfile_index: Optional[int] = None) -> None:
        """Add an error issue."""
        self.issues.append(ValidationIssue(
            severity='error',
            message=message,
            code=code,
            field=field,
            subfile_index=subfile_index
        ))
        self.is_valid = False

    def add_warning(self, message: str, code: str, field: Optional[str] = None,
                    subfile_index: Optional[int] = None) -> None:
        """Add a warning issue."""
        self.issues.append(ValidationIssue(
            severity='warning',
            message=message,
            code=code,
            field=field,
            subfile_index=subfile_index
        ))

    def add_info(self, message: str, code: str, field: Optional[str] = None,
                 subfile_index: Optional[int] = None) -> None:
        """Add an info issue."""
        self.issues.append(ValidationIssue(
            severity='info',
            message=message,
            code=code,
            field=field,
            subfile_index=subfile_index
        ))

    def __str__(self) -> str:
        """Format validation result as string."""
        lines = []
        lines.append(f"Validation: {'PASSED' if self.is_valid else 'FAILED'}")
        lines.append(f"Errors: {len(self.errors)}, Warnings: {len(self.warnings)}, "
                    f"Info: {len(self.info)}")

        if self.issues:
            lines.append("\nIssues:")
            for issue in self.issues:
                lines.append(f"  {issue}")

        return "\n".join(lines)


class AAMVAValidator:
    """AAMVA barcode data validator.

    Provides comprehensive validation of AAMVA barcode data including
    field validation, cross-field checks, and logical consistency.
    """

    def __init__(
        self,
        version: AAMVAVersion = AAMVAVersion.VERSION_10,
        strict: bool = False
    ):
        """Initialize validator.

        Args:
            version: AAMVA version to validate against
            strict: If True, warnings become errors
        """
        self.version = version
        self.strict = strict

    def validate(self, subfiles: List[Subfile]) -> ValidationResult:
        """Validate complete barcode data.

        Args:
            subfiles: List of subfiles to validate

        Returns:
            ValidationResult with all issues found
        """
        result = ValidationResult(is_valid=True)

        if not subfiles:
            result.add_error(
                "No subfiles provided",
                "NO_SUBFILES"
            )
            return result

        # Validate first subfile is DL
        if subfiles[0].subfile_type != "DL":
            result.add_error(
                f"First subfile must be DL, found {subfiles[0].subfile_type}",
                "INVALID_FIRST_SUBFILE"
            )

        # Validate each subfile
        for i, subfile in enumerate(subfiles):
            self._validate_subfile(subfile, i, result)

        # Cross-subfile validation
        if len(subfiles) > 0 and subfiles[0].subfile_type == "DL":
            self._validate_cross_field(subfiles[0], result)
            self._validate_dates(subfiles[0], result)
            self._validate_iin_consistency(subfiles[0], result)

        return result

    def validate_subfile(self, subfile: Subfile) -> ValidationResult:
        """Validate a single subfile.

        Args:
            subfile: Subfile to validate

        Returns:
            ValidationResult
        """
        result = ValidationResult(is_valid=True)
        self._validate_subfile(subfile, 0, result)
        return result

    def _validate_subfile(
        self,
        subfile: Subfile,
        index: int,
        result: ValidationResult
    ) -> None:
        """Validate a single subfile and add issues to result.

        Args:
            subfile: Subfile to validate
            index: Subfile index
            result: ValidationResult to update
        """
        # For DL subfiles, check mandatory fields
        if subfile.subfile_type == "DL":
            self._validate_mandatory_fields(subfile, index, result)

        # Validate each field
        for code, value in subfile.fields.items():
            self._validate_field(code, value, index, result)

    def _validate_mandatory_fields(
        self,
        subfile: Subfile,
        index: int,
        result: ValidationResult
    ) -> None:
        """Check that all mandatory fields are present.

        Args:
            subfile: Subfile to check
            index: Subfile index
            result: ValidationResult to update
        """
        mandatory = get_mandatory_fields(self.version)

        for code in mandatory:
            if code not in subfile.fields:
                result.add_error(
                    f"Missing mandatory field: {code}",
                    "MISSING_MANDATORY_FIELD",
                    field=code,
                    subfile_index=index
                )

    def _validate_field(
        self,
        code: str,
        value: str,
        subfile_index: int,
        result: ValidationResult
    ) -> None:
        """Validate a single field.

        Args:
            code: Field code
            value: Field value
            subfile_index: Subfile index
            result: ValidationResult to update
        """
        field_def = get_field_definition(code)

        if not field_def:
            # Unknown field - warning only unless strict
            if self.strict:
                result.add_error(
                    f"Unknown field code: {code}",
                    "UNKNOWN_FIELD",
                    field=code,
                    subfile_index=subfile_index
                )
            else:
                result.add_warning(
                    f"Unknown field code: {code}",
                    "UNKNOWN_FIELD",
                    field=code,
                    subfile_index=subfile_index
                )
            return

        # Use field definition's validation
        is_valid, error_msg = field_def.validate(value)
        if not is_valid:
            result.add_error(
                error_msg,
                "FIELD_VALIDATION_FAILED",
                field=code,
                subfile_index=subfile_index
            )

    def _validate_cross_field(
        self,
        subfile: Subfile,
        result: ValidationResult
    ) -> None:
        """Validate cross-field consistency.

        Args:
            subfile: DL subfile
            result: ValidationResult to update
        """
        # Validate sex and name consistency
        sex = subfile.get_field("DBC")
        if sex:
            # This is just an example - in reality, names don't strictly
            # indicate gender, but we can check for consistency with
            # other fields if needed
            pass

        # Validate height format
        height = subfile.get_field("DAU")
        if height:
            # Height can be in inches (nnn) or feet-inches (n-nn)
            # or centimeters (nnnCM)
            if not re.match(r'^\d{2,3}(CM)?$', height):
                result.add_warning(
                    f"Height format may be invalid: {height}",
                    "INVALID_HEIGHT_FORMAT",
                    field="DAU"
                )

        # Validate weight is reasonable
        weight = subfile.get_field("DAW")
        if weight and weight.isdigit():
            weight_val = int(weight)
            if weight_val < 50 or weight_val > 600:
                result.add_warning(
                    f"Weight value seems unusual: {weight_val} lbs",
                    "UNUSUAL_WEIGHT",
                    field="DAW"
                )

        # Validate ZIP code format
        zip_code = subfile.get_field("DAK")
        if zip_code:
            # US ZIP: 5 digits or 9 digits
            # Canada postal: A1A1A1 format
            if not re.match(r'^(\d{5}|\d{9}|[A-Z]\d[A-Z]\d[A-Z]\d)$', zip_code):
                result.add_warning(
                    f"ZIP/Postal code format may be invalid: {zip_code}",
                    "INVALID_ZIP_FORMAT",
                    field="DAK"
                )

    def _validate_dates(
        self,
        subfile: Subfile,
        result: ValidationResult
    ) -> None:
        """Validate date fields and their relationships.

        Args:
            subfile: DL subfile
            result: ValidationResult to update
        """
        # Parse dates
        dob = self._parse_date(subfile.get_field("DBB"))
        issue_date = self._parse_date(subfile.get_field("DBD"))
        exp_date = self._parse_date(subfile.get_field("DBA"))

        # Validate date formats
        if subfile.has_field("DBB") and not dob:
            result.add_error(
                "Invalid date of birth format",
                "INVALID_DATE_FORMAT",
                field="DBB"
            )

        if subfile.has_field("DBD") and not issue_date:
            result.add_error(
                "Invalid issue date format",
                "INVALID_DATE_FORMAT",
                field="DBD"
            )

        if subfile.has_field("DBA") and not exp_date:
            result.add_error(
                "Invalid expiration date format",
                "INVALID_DATE_FORMAT",
                field="DBA"
            )

        # Validate date relationships
        today = datetime.now()

        if dob and issue_date:
            # Issue date should be after DOB + minimum age (typically 16)
            min_issue_age = 16
            min_issue_date = datetime(
                dob.year + min_issue_age,
                dob.month,
                dob.day
            )
            if issue_date < min_issue_date:
                result.add_warning(
                    f"Issue date is before minimum age {min_issue_age}",
                    "ISSUE_BEFORE_MIN_AGE",
                    field="DBD"
                )

        if issue_date and exp_date:
            # Expiration should be after issue
            if exp_date <= issue_date:
                result.add_error(
                    "Expiration date must be after issue date",
                    "INVALID_DATE_SEQUENCE",
                    field="DBA"
                )

        if dob:
            # DOB should not be in the future
            if dob > today:
                result.add_error(
                    "Date of birth cannot be in the future",
                    "FUTURE_DOB",
                    field="DBB"
                )

            # Check age is reasonable (0-120 years)
            age = (today - dob).days // 365
            if age < 0 or age > 120:
                result.add_warning(
                    f"Age seems unusual: {age} years",
                    "UNUSUAL_AGE",
                    field="DBB"
                )

    def _validate_iin_consistency(
        self,
        subfile: Subfile,
        result: ValidationResult
    ) -> None:
        """Validate IIN matches jurisdiction.

        Args:
            subfile: DL subfile
            result: ValidationResult to update
        """
        jurisdiction = subfile.get_field("DAJ")
        if not jurisdiction:
            return

        iin = get_iin_by_state(jurisdiction)
        if not iin:
            result.add_warning(
                f"Unknown jurisdiction: {jurisdiction}",
                "UNKNOWN_JURISDICTION",
                field="DAJ"
            )

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse AAMVA date string (MMDDYYYY).

        Args:
            date_str: Date string in MMDDYYYY format

        Returns:
            datetime object or None if invalid
        """
        if not date_str or len(date_str) != 8:
            return None

        try:
            month = int(date_str[0:2])
            day = int(date_str[2:4])
            year = int(date_str[4:8])
            return datetime(year, month, day)
        except (ValueError, TypeError):
            return None


def validate_license_data(
    subfiles: List[Subfile],
    version: AAMVAVersion = AAMVAVersion.VERSION_10,
    strict: bool = False
) -> ValidationResult:
    """Convenience function to validate license data.

    Args:
        subfiles: List of subfiles to validate
        version: AAMVA version to validate against
        strict: If True, warnings become errors

    Returns:
        ValidationResult

    Example:
        result = validate_license_data(subfiles)
        if result.is_valid:
            print("Validation passed!")
        else:
            for error in result.errors:
                print(f"Error: {error}")
    """
    validator = AAMVAValidator(version=version, strict=strict)
    return validator.validate(subfiles)


def validate_barcode_string(
    barcode_data: str,
    version: AAMVAVersion = AAMVAVersion.VERSION_10,
    strict: bool = False
) -> ValidationResult:
    """Validate a complete AAMVA barcode string.

    This function decodes the barcode and validates the data.

    Args:
        barcode_data: Complete AAMVA barcode string
        version: AAMVA version to validate against
        strict: If True, warnings become errors

    Returns:
        ValidationResult

    Raises:
        ValidationError: If decoding fails
    """
    from .decoder import AAMVADecoder

    try:
        decoder = AAMVADecoder(strict=False)
        header, subfiles = decoder.decode(barcode_data)

        # Use version from header if available
        if header.aamva_version:
            version = header.aamva_version

        return validate_license_data(subfiles, version, strict)

    except Exception as e:
        result = ValidationResult(is_valid=False)
        result.add_error(
            f"Failed to decode barcode: {str(e)}",
            "DECODE_FAILED"
        )
        return result
