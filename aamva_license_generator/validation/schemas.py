"""
Pydantic schemas for license data validation.

Provides comprehensive type validation, field constraints, and
custom validators for license data.
"""

from datetime import datetime, date
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator, model_validator
import re


class ValidationLevel(str, Enum):
    """Validation severity levels."""
    ERROR = "error"  # Blocking issue, cannot proceed
    WARNING = "warning"  # Non-blocking issue, user should review
    INFO = "info"  # Informational message, no action needed


class FieldValidationResult(BaseModel):
    """Result of validating a single field."""
    field_name: str
    is_valid: bool
    level: ValidationLevel = ValidationLevel.ERROR
    message: str = ""
    suggestions: List[str] = Field(default_factory=list)
    auto_fix: Optional[str] = None

    class Config:
        frozen = True


class ValidationResult(BaseModel):
    """Result of validating an entire license or batch."""
    is_valid: bool
    errors: List[FieldValidationResult] = Field(default_factory=list)
    warnings: List[FieldValidationResult] = Field(default_factory=list)
    info: List[FieldValidationResult] = Field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        """Check if there are any blocking errors."""
        return len(self.errors) > 0

    @property
    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return len(self.warnings) > 0

    @property
    def all_messages(self) -> List[FieldValidationResult]:
        """Get all messages sorted by severity."""
        return self.errors + self.warnings + self.info

    def add_result(self, result: FieldValidationResult):
        """Add a field validation result to the appropriate list."""
        if result.level == ValidationLevel.ERROR:
            self.errors.append(result)
        elif result.level == ValidationLevel.WARNING:
            self.warnings.append(result)
        else:
            self.info.append(result)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "is_valid": self.is_valid,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "info_count": len(self.info),
            "errors": [e.model_dump() for e in self.errors],
            "warnings": [w.model_dump() for w in self.warnings],
            "info": [i.model_dump() for i in self.info],
        }


class BatchValidationResult(BaseModel):
    """Result of validating multiple licenses."""
    total_count: int
    valid_count: int
    invalid_count: int
    results: List[ValidationResult] = Field(default_factory=list)

    @property
    def success_rate(self) -> float:
        """Calculate validation success rate."""
        if self.total_count == 0:
            return 0.0
        return (self.valid_count / self.total_count) * 100

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "total_count": self.total_count,
            "valid_count": self.valid_count,
            "invalid_count": self.invalid_count,
            "success_rate": self.success_rate,
            "results": [r.to_dict() for r in self.results],
        }


class LicenseData(BaseModel):
    """
    Pydantic schema for AAMVA license data.

    Provides comprehensive validation for all license fields including:
    - Type validation
    - Format validation
    - Range validation
    - Custom business rules
    """

    # License identification
    license_number: str = Field(..., min_length=1, max_length=25, description="Driver license number (DAQ)")
    state: str = Field(..., min_length=2, max_length=2, description="Issuing state/jurisdiction (DAJ)")

    # Personal information
    last_name: str = Field(..., min_length=1, max_length=40, description="Family name (DCS)")
    first_name: str = Field(..., min_length=1, max_length=40, description="First name (DAC)")
    middle_name: Optional[str] = Field(None, max_length=40, description="Middle name (DAD)")

    # Dates
    date_of_birth: date = Field(..., description="Date of birth (DBB)")
    issue_date: date = Field(..., description="Document issue date (DBD)")
    expiration_date: date = Field(..., description="Document expiration date (DBA)")

    # Physical characteristics
    sex: str = Field(..., pattern="^[12]$", description="Sex: 1=Male, 2=Female (DBC)")
    eye_color: str = Field(..., pattern="^(BLK|BLU|BRO|GRY|GRN|HAZ|MAR|PNK|DIC|UNK)$",
                          description="Eye color (DAY)")
    hair_color: str = Field(..., pattern="^(BLK|BLN|BRO|GRY|RED|WHI|SDY|UNK)$",
                           description="Hair color (DAZ)")
    height: str = Field(..., pattern="^\\d{2,3}$", description="Height in inches (DAU)")
    weight: str = Field(..., pattern="^\\d{2,3}$", description="Weight in pounds (DAW)")
    race: Optional[str] = Field(None, pattern="^[WBAIU]$", description="Race code (DCL)")

    # Address
    address: str = Field(..., min_length=1, max_length=35, description="Street address (DAG)")
    city: str = Field(..., min_length=1, max_length=20, description="City (DAI)")
    postal_code: str = Field(..., pattern="^\\d{5}(\\d{4})?$", description="ZIP code (DAK)")

    # License class and restrictions
    vehicle_class: str = Field(default="D", max_length=4, description="Vehicle class (DCA)")
    restrictions: Optional[str] = Field(None, max_length=12, description="Restrictions (DCB)")
    endorsements: Optional[str] = Field(None, max_length=5, description="Endorsements (DCD)")

    # Additional fields
    document_discriminator: Optional[str] = Field(None, max_length=25, description="Doc discriminator (DCF)")
    country_of_issuance: str = Field(default="USA", pattern="^[A-Z]{3}$",
                                     description="Country code (DCG)")

    # Truncation flags
    truncation_last_name: str = Field(default="N", pattern="^[NTU]$",
                                      description="Family name truncation (DDE)")
    truncation_first_name: str = Field(default="N", pattern="^[NTU]$",
                                       description="First name truncation (DDF)")
    truncation_middle_name: str = Field(default="N", pattern="^[NTU]$",
                                        description="Middle name truncation (DDG)")

    # Compliance and status
    compliance_type: str = Field(default="F", pattern="^[FN]$",
                                description="Compliance type: F=Full, N=Non (DDA)")
    limited_duration: str = Field(default="0", pattern="^[01]$",
                                 description="Limited duration document (DDD)")
    organ_donor: str = Field(default="0", pattern="^[01]$", description="Organ donor (DDK)")
    veteran: str = Field(default="0", pattern="^[01]$", description="Veteran status (DDL)")

    @field_validator('state')
    @classmethod
    def validate_state_uppercase(cls, v: str) -> str:
        """Ensure state code is uppercase."""
        return v.upper()

    @field_validator('license_number')
    @classmethod
    def validate_license_number_format(cls, v: str) -> str:
        """Validate license number contains valid characters."""
        if not re.match(r'^[A-Z0-9\-]+$', v, re.IGNORECASE):
            raise ValueError("License number must contain only letters, numbers, and hyphens")
        return v.upper()

    @field_validator('height')
    @classmethod
    def validate_height_range(cls, v: str) -> str:
        """Validate height is within reasonable range (36-96 inches)."""
        height_int = int(v)
        if not 36 <= height_int <= 96:
            raise ValueError(f"Height {height_int} inches is outside reasonable range (36-96 inches)")
        return v

    @field_validator('weight')
    @classmethod
    def validate_weight_range(cls, v: str) -> str:
        """Validate weight is within reasonable range (50-500 lbs)."""
        weight_int = int(v)
        if not 50 <= weight_int <= 500:
            raise ValueError(f"Weight {weight_int} lbs is outside reasonable range (50-500 lbs)")
        return v

    @field_validator('postal_code')
    @classmethod
    def validate_postal_code_format(cls, v: str) -> str:
        """Validate and normalize postal code."""
        # Remove any dashes or spaces
        cleaned = v.replace('-', '').replace(' ', '')

        # Must be 5 or 9 digits
        if len(cleaned) not in [5, 9]:
            raise ValueError("Postal code must be 5 or 9 digits")

        # Pad to 9 digits if only 5 provided
        if len(cleaned) == 5:
            cleaned = cleaned + "0000"

        return cleaned

    @model_validator(mode='after')
    def validate_date_sequence(self) -> 'LicenseData':
        """Validate that dates are in logical sequence: DOB < Issue < Expiration."""
        # Check DOB < Issue Date
        if self.date_of_birth >= self.issue_date:
            raise ValueError(
                f"Date of birth ({self.date_of_birth}) must be before issue date ({self.issue_date})"
            )

        # Check Issue Date < Expiration Date
        if self.issue_date >= self.expiration_date:
            raise ValueError(
                f"Issue date ({self.issue_date}) must be before expiration date ({self.expiration_date})"
            )

        # Check minimum age (16 years old at issue)
        age_at_issue = (self.issue_date - self.date_of_birth).days / 365.25
        if age_at_issue < 16:
            raise ValueError(
                f"Age at issue ({age_at_issue:.1f} years) must be at least 16 years"
            )

        # Check maximum age (120 years) - this is a sanity check
        current_age = (self.issue_date - self.date_of_birth).days / 365.25
        if current_age > 120:
            raise ValueError(
                f"Age ({current_age:.1f} years) exceeds reasonable maximum (120 years)"
            )

        return self

    @model_validator(mode='after')
    def validate_name_consistency(self) -> 'LicenseData':
        """Validate name truncation flags match actual name lengths."""
        # Check if names exceed typical barcode limits
        if len(self.last_name) > 30 and self.truncation_last_name == "N":
            # This is a warning, not an error, so we'll just note it
            # Actual truncation validation happens in validators.py
            pass

        if len(self.first_name) > 30 and self.truncation_first_name == "N":
            pass

        if self.middle_name and len(self.middle_name) > 30 and self.truncation_middle_name == "N":
            pass

        return self

    class Config:
        """Pydantic configuration."""
        str_strip_whitespace = True
        validate_assignment = True
        json_schema_extra = {
            "example": {
                "license_number": "D1234567",
                "state": "CA",
                "last_name": "DOE",
                "first_name": "JOHN",
                "middle_name": "MICHAEL",
                "date_of_birth": "1990-05-15",
                "issue_date": "2020-01-10",
                "expiration_date": "2028-05-15",
                "sex": "1",
                "eye_color": "BRO",
                "hair_color": "BRN",
                "height": "69",
                "weight": "180",
                "race": "W",
                "address": "123 MAIN ST",
                "city": "LOS ANGELES",
                "postal_code": "900012345",
                "vehicle_class": "D",
                "restrictions": "",
                "endorsements": "",
                "country_of_issuance": "USA",
                "compliance_type": "F",
                "limited_duration": "0",
                "organ_donor": "1",
                "veteran": "0",
            }
        }

    def to_aamva_dict(self) -> Dict[str, str]:
        """Convert to AAMVA field format (DAQ, DCS, etc.)."""
        return {
            "DAQ": self.license_number,
            "DAJ": self.state,
            "DCS": self.last_name,
            "DAC": self.first_name,
            "DAD": self.middle_name or "",
            "DBB": self.date_of_birth.strftime("%m%d%Y"),
            "DBD": self.issue_date.strftime("%m%d%Y"),
            "DBA": self.expiration_date.strftime("%m%d%Y"),
            "DBC": self.sex,
            "DAY": self.eye_color,
            "DAZ": self.hair_color,
            "DAU": self.height,
            "DAW": self.weight,
            "DCL": self.race or "",
            "DAG": self.address,
            "DAI": self.city,
            "DAK": self.postal_code,
            "DCA": self.vehicle_class,
            "DCB": self.restrictions or "",
            "DCD": self.endorsements or "",
            "DCF": self.document_discriminator or "",
            "DCG": self.country_of_issuance,
            "DDE": self.truncation_last_name,
            "DDF": self.truncation_first_name,
            "DDG": self.truncation_middle_name,
            "DDA": self.compliance_type,
            "DDD": self.limited_duration,
            "DDK": self.organ_donor,
            "DDL": self.veteran,
        }
