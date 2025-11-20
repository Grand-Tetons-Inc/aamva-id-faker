"""
Validation rules and logic for AAMVA license data.

This module provides comprehensive validation for all license data structures
to ensure compliance with AAMVA standards and logical consistency.
"""

from datetime import date, timedelta
from typing import Optional
import re

from .models import (
    License,
    LicenseSubfile,
    Person,
    Address,
    PhysicalAttributes,
    Sex,
    EyeColor,
    HairColor,
    Race,
)


class ValidationError(Exception):
    """Exception raised when validation fails.

    Attributes:
        field: The field that failed validation
        value: The invalid value
        message: Human-readable error message
    """

    def __init__(self, field: str, value: any, message: str) -> None:
        self.field = field
        self.value = value
        self.message = message
        super().__init__(f"Validation error for {field}: {message}")


class LicenseValidator:
    """Comprehensive validator for license data structures.

    This class provides static methods for validating all aspects of license
    data to ensure AAMVA compliance and logical consistency.
    """

    # AAMVA field constraints
    MAX_NAME_LENGTH = 40
    MAX_ADDRESS_LENGTH = 35
    MAX_CITY_LENGTH = 20
    MIN_DRIVER_AGE = 16
    MAX_LICENSE_VALIDITY_YEARS = 10
    MIN_LICENSE_VALIDITY_YEARS = 1

    @staticmethod
    def validate_person(person: Person) -> None:
        """Validate person data meets AAMVA requirements.

        Args:
            person: Person object to validate

        Raises:
            ValidationError: If validation fails
        """
        # Validate name lengths
        if len(person.first_name) > LicenseValidator.MAX_NAME_LENGTH:
            raise ValidationError(
                "first_name",
                person.first_name,
                f"Exceeds maximum length of {LicenseValidator.MAX_NAME_LENGTH}",
            )

        if len(person.middle_name) > LicenseValidator.MAX_NAME_LENGTH:
            raise ValidationError(
                "middle_name",
                person.middle_name,
                f"Exceeds maximum length of {LicenseValidator.MAX_NAME_LENGTH}",
            )

        if len(person.last_name) > LicenseValidator.MAX_NAME_LENGTH:
            raise ValidationError(
                "last_name",
                person.last_name,
                f"Exceeds maximum length of {LicenseValidator.MAX_NAME_LENGTH}",
            )

        # Validate all names are uppercase
        if person.first_name != person.first_name.upper():
            raise ValidationError(
                "first_name", person.first_name, "Must be uppercase"
            )

        if person.middle_name != person.middle_name.upper():
            raise ValidationError(
                "middle_name", person.middle_name, "Must be uppercase"
            )

        if person.last_name != person.last_name.upper():
            raise ValidationError(
                "last_name", person.last_name, "Must be uppercase"
            )

        # Validate no special characters in names (alphanumeric and spaces only)
        name_pattern = re.compile(r"^[A-Z\s\-\']+$")
        if not name_pattern.match(person.first_name):
            raise ValidationError(
                "first_name",
                person.first_name,
                "Contains invalid characters (only A-Z, space, hyphen, apostrophe)",
            )

        if not name_pattern.match(person.last_name):
            raise ValidationError(
                "last_name",
                person.last_name,
                "Contains invalid characters (only A-Z, space, hyphen, apostrophe)",
            )

        # Validate age is appropriate for driver
        age = person.age
        if age < LicenseValidator.MIN_DRIVER_AGE:
            raise ValidationError(
                "date_of_birth",
                person.date_of_birth,
                f"Driver must be at least {LicenseValidator.MIN_DRIVER_AGE} years old",
            )

        if age > 120:
            raise ValidationError(
                "date_of_birth",
                person.date_of_birth,
                "Unrealistic age (>120 years)",
            )

    @staticmethod
    def validate_physical_attributes(physical: PhysicalAttributes) -> None:
        """Validate physical attributes are reasonable.

        Args:
            physical: PhysicalAttributes object to validate

        Raises:
            ValidationError: If validation fails
        """
        # Height validation (4'0" to 8'0")
        if physical.height_inches < 48:
            raise ValidationError(
                "height_inches",
                physical.height_inches,
                "Height below 48 inches (4 feet) is unrealistic for adult driver",
            )

        if physical.height_inches > 96:
            raise ValidationError(
                "height_inches",
                physical.height_inches,
                "Height above 96 inches (8 feet) is unrealistic",
            )

        # Weight validation (80-500 lbs)
        if physical.weight_pounds < 80:
            raise ValidationError(
                "weight_pounds",
                physical.weight_pounds,
                "Weight below 80 lbs is unrealistic for adult driver",
            )

        if physical.weight_pounds > 500:
            raise ValidationError(
                "weight_pounds",
                physical.weight_pounds,
                "Weight above 500 lbs is outside typical range",
            )

        # Validate enum values are from standard sets
        if not isinstance(physical.eye_color, EyeColor):
            raise ValidationError(
                "eye_color", physical.eye_color, "Not a valid AAMVA eye color code"
            )

        if not isinstance(physical.hair_color, HairColor):
            raise ValidationError(
                "hair_color", physical.hair_color, "Not a valid AAMVA hair color code"
            )

        if not isinstance(physical.race, Race):
            raise ValidationError(
                "race", physical.race, "Not a valid AAMVA race code"
            )

    @staticmethod
    def validate_address(address: Address) -> None:
        """Validate address meets AAMVA requirements.

        Args:
            address: Address object to validate

        Raises:
            ValidationError: If validation fails
        """
        # Validate field lengths
        if len(address.street) > LicenseValidator.MAX_ADDRESS_LENGTH:
            raise ValidationError(
                "street",
                address.street,
                f"Exceeds maximum length of {LicenseValidator.MAX_ADDRESS_LENGTH}",
            )

        if len(address.city) > LicenseValidator.MAX_CITY_LENGTH:
            raise ValidationError(
                "city",
                address.city,
                f"Exceeds maximum length of {LicenseValidator.MAX_CITY_LENGTH}",
            )

        # Validate all uppercase
        if address.street != address.street.upper():
            raise ValidationError("street", address.street, "Must be uppercase")

        if address.city != address.city.upper():
            raise ValidationError("city", address.city, "Must be uppercase")

        if address.state != address.state.upper():
            raise ValidationError("state", address.state, "Must be uppercase")

        # Validate state code is alphabetic
        if not address.state.isalpha():
            raise ValidationError(
                "state", address.state, "Must contain only letters"
            )

        # Validate ZIP code format
        if not address.postal_code.isdigit():
            raise ValidationError(
                "postal_code", address.postal_code, "Must contain only digits"
            )

        if len(address.postal_code) != 9:
            raise ValidationError(
                "postal_code",
                address.postal_code,
                "Must be exactly 9 digits (5-digit ZIP + 4-digit extension)",
            )

    @staticmethod
    def validate_license_subfile(subfile: LicenseSubfile) -> None:
        """Validate license subfile data.

        Args:
            subfile: LicenseSubfile object to validate

        Raises:
            ValidationError: If validation fails
        """
        # Validate nested objects
        LicenseValidator.validate_person(subfile.person)
        LicenseValidator.validate_physical_attributes(subfile.physical)
        LicenseValidator.validate_address(subfile.address)

        # Validate license number is not empty
        if not subfile.license_number.strip():
            raise ValidationError(
                "license_number", subfile.license_number, "Cannot be empty"
            )

        # Validate dates are in logical order
        if subfile.issue_date > subfile.expiration_date:
            raise ValidationError(
                "issue_date",
                subfile.issue_date,
                f"Cannot be after expiration date {subfile.expiration_date}",
            )

        # Validate issue date is not in the future
        if subfile.issue_date > date.today():
            raise ValidationError(
                "issue_date", subfile.issue_date, "Cannot be in the future"
            )

        # Validate license validity period
        validity_days = (subfile.expiration_date - subfile.issue_date).days
        validity_years = validity_days / 365.25

        if validity_years < LicenseValidator.MIN_LICENSE_VALIDITY_YEARS:
            raise ValidationError(
                "expiration_date",
                subfile.expiration_date,
                f"License validity period ({validity_years:.1f} years) is too short",
            )

        if validity_years > LicenseValidator.MAX_LICENSE_VALIDITY_YEARS:
            raise ValidationError(
                "expiration_date",
                subfile.expiration_date,
                f"License validity period ({validity_years:.1f} years) is too long",
            )

        # Validate person was legal age at issue
        age_at_issue = (
            subfile.issue_date - subfile.person.date_of_birth
        ).days / 365.25
        if age_at_issue < LicenseValidator.MIN_DRIVER_AGE:
            raise ValidationError(
                "issue_date",
                subfile.issue_date,
                f"Person was only {age_at_issue:.1f} years old at issue "
                f"(minimum {LicenseValidator.MIN_DRIVER_AGE})",
            )

        # Validate country code
        if len(subfile.country_code) != 3:
            raise ValidationError(
                "country_code",
                subfile.country_code,
                "Must be exactly 3 characters (ISO 3166-1 alpha-3)",
            )

        if not subfile.country_code.isalpha():
            raise ValidationError(
                "country_code", subfile.country_code, "Must contain only letters"
            )

        if subfile.country_code != subfile.country_code.upper():
            raise ValidationError(
                "country_code", subfile.country_code, "Must be uppercase"
            )

        # Validate document discriminator uniqueness (should be alphanumeric)
        if not re.match(r"^[A-Z0-9]+$", subfile.document_discriminator):
            raise ValidationError(
                "document_discriminator",
                subfile.document_discriminator,
                "Must contain only uppercase letters and digits",
            )

    @staticmethod
    def validate_license(license_obj: License) -> None:
        """Validate complete license data structure.

        Args:
            license_obj: License object to validate

        Raises:
            ValidationError: If validation fails
        """
        # Validate DL subfile
        LicenseValidator.validate_license_subfile(license_obj.dl_subfile)

        # Validate IIN format
        if len(license_obj.jurisdiction_iin) != 6:
            raise ValidationError(
                "jurisdiction_iin",
                license_obj.jurisdiction_iin,
                "IIN must be exactly 6 digits",
            )

        if not license_obj.jurisdiction_iin.isdigit():
            raise ValidationError(
                "jurisdiction_iin",
                license_obj.jurisdiction_iin,
                "IIN must contain only digits",
            )

        # Validate state codes match across subfiles
        dl_state = license_obj.dl_subfile.address.state
        state_subfile_state = license_obj.state_subfile.state_code

        if dl_state != state_subfile_state:
            raise ValidationError(
                "state",
                dl_state,
                f"DL state '{dl_state}' doesn't match "
                f"state subfile state '{state_subfile_state}'",
            )

        # Validate state subfile type matches state code
        expected_subfile_type = f"Z{state_subfile_state[0]}"
        if license_obj.state_subfile.subfile_type != expected_subfile_type:
            raise ValidationError(
                "subfile_type",
                license_obj.state_subfile.subfile_type,
                f"Expected '{expected_subfile_type}' for state {state_subfile_state}",
            )

    @staticmethod
    def validate_all(license_obj: License) -> list[str]:
        """Validate license and return list of warnings (non-fatal issues).

        Args:
            license_obj: License object to validate

        Returns:
            List of warning messages (empty if no warnings)

        Raises:
            ValidationError: If validation fails
        """
        warnings: list[str] = []

        # Perform all validation
        LicenseValidator.validate_license(license_obj)

        # Check for potential warnings
        subfile = license_obj.dl_subfile

        # Warn if license expires soon
        days_to_expiry = (subfile.expiration_date - date.today()).days
        if 0 < days_to_expiry < 30:
            warnings.append(f"License expires in {days_to_expiry} days")

        # Warn if person is very old
        if subfile.person.age > 100:
            warnings.append(
                f"Unusual age: {subfile.person.age:.0f} years old"
            )

        # Warn if height/weight seem mismatched (very rough BMI check)
        height_m = subfile.physical.height_inches * 0.0254
        weight_kg = subfile.physical.weight_pounds * 0.453592
        bmi = weight_kg / (height_m * height_m)

        if bmi < 15:
            warnings.append(f"Very low BMI: {bmi:.1f} (possible data issue)")
        elif bmi > 50:
            warnings.append(f"Very high BMI: {bmi:.1f} (possible data issue)")

        return warnings
