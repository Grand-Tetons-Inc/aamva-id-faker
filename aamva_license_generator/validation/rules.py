"""
Validation rule definitions and rule engine.

Provides a flexible, extensible rule system for defining and executing
validation rules on license data.
"""

from typing import Callable, Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime, date
import re
from .schemas import ValidationLevel, FieldValidationResult


@dataclass
class ValidationRule:
    """
    A single validation rule.

    Attributes:
        field_name: Name of the field to validate
        validator: Function that takes a value and returns (is_valid, message)
        level: Severity level (error, warning, info)
        message_template: Template for error message (supports {value}, {field_name}, etc.)
        suggestions_fn: Optional function to generate suggestions
        auto_fix_fn: Optional function to auto-fix the value
    """
    field_name: str
    validator: Callable[[Any], tuple[bool, str]]
    level: ValidationLevel = ValidationLevel.ERROR
    message_template: str = "Validation failed for {field_name}"
    suggestions_fn: Optional[Callable[[Any], List[str]]] = None
    auto_fix_fn: Optional[Callable[[Any], str]] = None
    description: str = ""

    def validate(self, value: Any) -> FieldValidationResult:
        """Execute the validation rule."""
        is_valid, message = self.validator(value)

        # Generate suggestions if provided
        suggestions = []
        if not is_valid and self.suggestions_fn:
            suggestions = self.suggestions_fn(value)

        # Generate auto-fix if provided
        auto_fix = None
        if not is_valid and self.auto_fix_fn:
            auto_fix = self.auto_fix_fn(value)

        # Format message
        formatted_message = message or self.message_template.format(
            field_name=self.field_name,
            value=value
        )

        return FieldValidationResult(
            field_name=self.field_name,
            is_valid=is_valid,
            level=self.level,
            message=formatted_message,
            suggestions=suggestions,
            auto_fix=auto_fix
        )


class ValidationRuleSet:
    """Collection of validation rules with execution engine."""

    def __init__(self):
        self.rules: List[ValidationRule] = []
        self.cross_field_rules: List[Callable] = []

    def add_rule(self, rule: ValidationRule):
        """Add a validation rule to the set."""
        self.rules.append(rule)

    def add_cross_field_rule(self, rule_fn: Callable):
        """Add a cross-field validation rule."""
        self.cross_field_rules.append(rule_fn)

    def validate_field(self, field_name: str, value: Any) -> List[FieldValidationResult]:
        """Validate a single field against all applicable rules."""
        results = []
        for rule in self.rules:
            if rule.field_name == field_name:
                results.append(rule.validate(value))
        return results

    def validate_all(self, data: Dict[str, Any]) -> List[FieldValidationResult]:
        """Validate all fields in the data dictionary."""
        results = []

        # Field-level validation
        for field_name, value in data.items():
            field_results = self.validate_field(field_name, value)
            results.extend(field_results)

        # Cross-field validation
        for rule_fn in self.cross_field_rules:
            cross_result = rule_fn(data)
            if cross_result:
                results.append(cross_result)

        return results


# === COMMON VALIDATION FUNCTIONS ===

def create_length_validator(min_length: Optional[int] = None,
                            max_length: Optional[int] = None) -> Callable:
    """Create a length validator function."""
    def validator(value: str) -> tuple[bool, str]:
        if not isinstance(value, str):
            return False, f"Expected string, got {type(value).__name__}"

        length = len(value)

        if min_length and length < min_length:
            return False, f"Minimum length is {min_length}, got {length}"

        if max_length and length > max_length:
            return False, f"Maximum length is {max_length}, got {length}"

        return True, ""

    return validator


def create_pattern_validator(pattern: str, description: str = "valid format") -> Callable:
    """Create a regex pattern validator."""
    compiled_pattern = re.compile(pattern)

    def validator(value: str) -> tuple[bool, str]:
        if not isinstance(value, str):
            return False, f"Expected string, got {type(value).__name__}"

        if not compiled_pattern.match(value):
            return False, f"Value does not match {description}"

        return True, ""

    return validator


def create_range_validator(min_val: Optional[float] = None,
                          max_val: Optional[float] = None,
                          value_type: type = int) -> Callable:
    """Create a numeric range validator."""
    def validator(value: Any) -> tuple[bool, str]:
        try:
            # Convert string to number if needed
            if isinstance(value, str):
                num_value = value_type(value)
            elif isinstance(value, (int, float)):
                num_value = value_type(value)
            else:
                return False, f"Expected {value_type.__name__}, got {type(value).__name__}"

            if min_val is not None and num_value < min_val:
                return False, f"Value {num_value} is below minimum {min_val}"

            if max_val is not None and num_value > max_val:
                return False, f"Value {num_value} exceeds maximum {max_val}"

            return True, ""

        except (ValueError, TypeError) as e:
            return False, f"Invalid {value_type.__name__}: {str(e)}"

    return validator


def create_enum_validator(valid_values: List[Any],
                         case_sensitive: bool = False) -> Callable:
    """Create an enum validator that checks against a list of valid values."""
    if not case_sensitive:
        valid_values = [str(v).upper() for v in valid_values]

    def validator(value: Any) -> tuple[bool, str]:
        check_value = value if case_sensitive else str(value).upper()

        if check_value not in valid_values:
            return False, f"Value '{value}' is not in valid list: {', '.join(map(str, valid_values))}"

        return True, ""

    return validator


def create_date_validator(min_date: Optional[date] = None,
                         max_date: Optional[date] = None) -> Callable:
    """Create a date range validator."""
    def validator(value: Any) -> tuple[bool, str]:
        # Handle string dates
        if isinstance(value, str):
            try:
                # Try multiple date formats
                for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%m%d%Y"]:
                    try:
                        date_value = datetime.strptime(value, fmt).date()
                        break
                    except ValueError:
                        continue
                else:
                    return False, f"Invalid date format: {value}"
            except Exception as e:
                return False, f"Invalid date: {str(e)}"
        elif isinstance(value, datetime):
            date_value = value.date()
        elif isinstance(value, date):
            date_value = value
        else:
            return False, f"Expected date, got {type(value).__name__}"

        if min_date and date_value < min_date:
            return False, f"Date {date_value} is before minimum {min_date}"

        if max_date and date_value > max_date:
            return False, f"Date {date_value} is after maximum {max_date}"

        return True, ""

    return validator


# === DEFAULT RULE SET FACTORY ===

def create_default_rules() -> ValidationRuleSet:
    """Create the default set of validation rules for license data."""
    ruleset = ValidationRuleSet()

    # === STATE CODE RULES ===
    from generate_licenses import IIN_JURISDICTIONS

    # Extract valid state codes
    valid_states = sorted(set(info['abbr'] for info in IIN_JURISDICTIONS.values()))

    ruleset.add_rule(ValidationRule(
        field_name="state",
        validator=create_enum_validator(valid_states, case_sensitive=False),
        level=ValidationLevel.ERROR,
        message_template="Invalid state code '{value}'. Must be a valid US state or Canadian province.",
        description="State code must be valid 2-letter abbreviation"
    ))

    # === LICENSE NUMBER RULES ===
    ruleset.add_rule(ValidationRule(
        field_name="license_number",
        validator=create_length_validator(min_length=1, max_length=25),
        level=ValidationLevel.ERROR,
        message_template="License number must be 1-25 characters",
        description="License number length validation"
    ))

    ruleset.add_rule(ValidationRule(
        field_name="license_number",
        validator=create_pattern_validator(r'^[A-Z0-9\-]+$', "alphanumeric with hyphens"),
        level=ValidationLevel.ERROR,
        message_template="License number must contain only letters, numbers, and hyphens",
        description="License number format validation"
    ))

    # === NAME RULES ===
    for name_field in ["first_name", "last_name"]:
        ruleset.add_rule(ValidationRule(
            field_name=name_field,
            validator=create_length_validator(min_length=1, max_length=40),
            level=ValidationLevel.ERROR,
            message_template=f"{name_field.replace('_', ' ').title()} must be 1-40 characters",
            description=f"{name_field} length validation"
        ))

        ruleset.add_rule(ValidationRule(
            field_name=name_field,
            validator=create_pattern_validator(r'^[A-Z\s\'\-\.]+$', "letters, spaces, hyphens, apostrophes"),
            level=ValidationLevel.ERROR,
            message_template=f"{name_field.replace('_', ' ').title()} contains invalid characters",
            description=f"{name_field} character validation"
        ))

    # Middle name (optional)
    ruleset.add_rule(ValidationRule(
        field_name="middle_name",
        validator=create_length_validator(max_length=40),
        level=ValidationLevel.ERROR,
        message_template="Middle name must not exceed 40 characters",
        description="Middle name length validation"
    ))

    # === DATE RULES ===
    today = date.today()
    min_dob = date(today.year - 120, 1, 1)  # Maximum age 120 years
    max_dob = date(today.year - 16, today.month, today.day)  # Minimum age 16 years

    ruleset.add_rule(ValidationRule(
        field_name="date_of_birth",
        validator=create_date_validator(min_date=min_dob, max_date=max_dob),
        level=ValidationLevel.ERROR,
        message_template="Date of birth must be between {min_date} and {max_date}",
        description="Date of birth range validation"
    ))

    # Issue date should be reasonable (not too far in past or future)
    min_issue = date(1990, 1, 1)
    max_issue = date(today.year + 1, 12, 31)

    ruleset.add_rule(ValidationRule(
        field_name="issue_date",
        validator=create_date_validator(min_date=min_issue, max_date=max_issue),
        level=ValidationLevel.WARNING,
        message_template="Issue date should be between {min_date} and {max_date}",
        description="Issue date range validation"
    ))

    # Expiration should be in future (for real licenses)
    ruleset.add_rule(ValidationRule(
        field_name="expiration_date",
        validator=create_date_validator(min_date=today),
        level=ValidationLevel.WARNING,
        message_template="Expiration date should be in the future",
        description="Expiration date validation"
    ))

    # === PHYSICAL CHARACTERISTICS ===
    ruleset.add_rule(ValidationRule(
        field_name="sex",
        validator=create_enum_validator(["1", "2"]),
        level=ValidationLevel.ERROR,
        message_template="Sex must be '1' (Male) or '2' (Female)",
        description="Sex code validation"
    ))

    ruleset.add_rule(ValidationRule(
        field_name="eye_color",
        validator=create_enum_validator(["BLK", "BLU", "BRO", "GRY", "GRN", "HAZ", "MAR", "PNK", "DIC", "UNK"]),
        level=ValidationLevel.ERROR,
        message_template="Invalid eye color code '{value}'",
        description="Eye color validation"
    ))

    ruleset.add_rule(ValidationRule(
        field_name="hair_color",
        validator=create_enum_validator(["BLK", "BLN", "BRO", "GRY", "RED", "WHI", "SDY", "UNK"]),
        level=ValidationLevel.ERROR,
        message_template="Invalid hair color code '{value}'",
        description="Hair color validation"
    ))

    ruleset.add_rule(ValidationRule(
        field_name="height",
        validator=create_range_validator(min_val=36, max_val=96, value_type=int),
        level=ValidationLevel.WARNING,
        message_template="Height should be between 36-96 inches (3-8 feet)",
        description="Height range validation"
    ))

    ruleset.add_rule(ValidationRule(
        field_name="weight",
        validator=create_range_validator(min_val=50, max_val=500, value_type=int),
        level=ValidationLevel.WARNING,
        message_template="Weight should be between 50-500 pounds",
        description="Weight range validation"
    ))

    # === ADDRESS RULES ===
    ruleset.add_rule(ValidationRule(
        field_name="address",
        validator=create_length_validator(min_length=1, max_length=35),
        level=ValidationLevel.ERROR,
        message_template="Address must be 1-35 characters",
        description="Address length validation"
    ))

    ruleset.add_rule(ValidationRule(
        field_name="city",
        validator=create_length_validator(min_length=1, max_length=20),
        level=ValidationLevel.ERROR,
        message_template="City must be 1-20 characters",
        description="City length validation"
    ))

    ruleset.add_rule(ValidationRule(
        field_name="postal_code",
        validator=create_pattern_validator(r'^\d{5}(\d{4})?$', "ZIP code (5 or 9 digits)"),
        level=ValidationLevel.ERROR,
        message_template="Postal code must be 5 or 9 digits",
        description="Postal code format validation"
    ))

    # === CROSS-FIELD VALIDATION ===

    def validate_date_sequence(data: Dict[str, Any]) -> Optional[FieldValidationResult]:
        """Validate DOB < Issue < Expiration."""
        try:
            dob = data.get("date_of_birth")
            issue = data.get("issue_date")
            exp = data.get("expiration_date")

            if not all([dob, issue, exp]):
                return None

            # Convert strings to dates if needed
            if isinstance(dob, str):
                dob = datetime.strptime(dob, "%Y-%m-%d").date()
            if isinstance(issue, str):
                issue = datetime.strptime(issue, "%Y-%m-%d").date()
            if isinstance(exp, str):
                exp = datetime.strptime(exp, "%Y-%m-%d").date()

            if dob >= issue:
                return FieldValidationResult(
                    field_name="date_of_birth",
                    is_valid=False,
                    level=ValidationLevel.ERROR,
                    message=f"Date of birth ({dob}) must be before issue date ({issue})"
                )

            if issue >= exp:
                return FieldValidationResult(
                    field_name="issue_date",
                    is_valid=False,
                    level=ValidationLevel.ERROR,
                    message=f"Issue date ({issue}) must be before expiration date ({exp})"
                )

            return None

        except Exception:
            return None

    ruleset.add_cross_field_rule(validate_date_sequence)

    return ruleset
