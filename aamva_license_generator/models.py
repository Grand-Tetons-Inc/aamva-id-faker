"""
Data models for AAMVA license generation.

This module defines the core data structures used throughout the license
generation system using Python dataclasses with comprehensive type hints.
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, Literal
from enum import Enum


class Sex(str, Enum):
    """Biological sex codes per AAMVA standard."""

    MALE = "1"
    FEMALE = "2"
    OTHER = "9"  # Future: Non-binary support


class EyeColor(str, Enum):
    """Eye color codes per AAMVA standard."""

    BLACK = "BLK"
    BLUE = "BLU"
    BROWN = "BRO"
    GRAY = "GRY"
    GREEN = "GRN"
    HAZEL = "HAZ"
    MAROON = "MAR"
    PINK = "PNK"
    DICHROMATIC = "DIC"
    UNKNOWN = "UNK"


class HairColor(str, Enum):
    """Hair color codes per AAMVA standard."""

    BLACK = "BLK"
    BLOND = "BLN"
    BROWN = "BRO"
    GRAY = "GRY"
    RED = "RED"
    WHITE = "WHI"
    SANDY = "SDY"
    BALD = "BAL"
    UNKNOWN = "UNK"


class Race(str, Enum):
    """Race codes per AAMVA standard."""

    WHITE = "W"
    BLACK = "B"
    ASIAN = "A"
    INDIGENOUS = "I"
    UNKNOWN = "U"


class TruncationStatus(str, Enum):
    """Name truncation status codes."""

    NOT_TRUNCATED = "N"
    TRUNCATED = "T"
    UNKNOWN = "U"


class ComplianceType(str, Enum):
    """DHS compliance type codes."""

    FULLY_COMPLIANT = "F"
    NON_COMPLIANT = "N"
    UNKNOWN = "U"


@dataclass(frozen=True)
class PhysicalAttributes:
    """Physical characteristics of the license holder.

    Attributes:
        height_inches: Height in inches (58-78 typical range, 4'10" to 6'6")
        weight_pounds: Weight in pounds (100-400 typical range)
        eye_color: Eye color code from AAMVA standard
        hair_color: Hair color code from AAMVA standard
        race: Race/ethnicity code from AAMVA standard
    """

    height_inches: int
    weight_pounds: int
    eye_color: EyeColor
    hair_color: HairColor
    race: Race

    def __post_init__(self) -> None:
        """Validate physical attributes are within reasonable ranges."""
        if not 40 <= self.height_inches <= 96:
            raise ValueError(f"Height {self.height_inches}\" outside valid range (40-96)")

        if not 80 <= self.weight_pounds <= 500:
            raise ValueError(f"Weight {self.weight_pounds}lbs outside valid range (80-500)")


@dataclass(frozen=True)
class Address:
    """Mailing address for the license holder.

    Attributes:
        street: Street address (e.g., "123 MAIN STREET")
        city: City name (e.g., "LOS ANGELES")
        state: Two-letter state code (e.g., "CA")
        postal_code: 9-digit ZIP code (e.g., "900120000")
    """

    street: str
    city: str
    state: str
    postal_code: str

    def __post_init__(self) -> None:
        """Validate address fields."""
        if not self.street:
            raise ValueError("Street address cannot be empty")

        if not self.city:
            raise ValueError("City cannot be empty")

        if len(self.state) != 2:
            raise ValueError(f"State code must be 2 characters, got: {self.state}")

        if len(self.postal_code) != 9:
            raise ValueError(f"Postal code must be 9 digits, got: {self.postal_code}")

        if not self.postal_code.isdigit():
            raise ValueError(f"Postal code must be numeric, got: {self.postal_code}")


@dataclass(frozen=True)
class Person:
    """Personal information for the license holder.

    Attributes:
        first_name: Legal first name (uppercase)
        middle_name: Legal middle name (uppercase)
        last_name: Legal last name/surname (uppercase)
        date_of_birth: Date of birth
        sex: Biological sex code
        first_name_truncated: Whether first name was truncated to fit
        middle_name_truncated: Whether middle name was truncated
        last_name_truncated: Whether last name was truncated
    """

    first_name: str
    middle_name: str
    last_name: str
    date_of_birth: date
    sex: Sex
    first_name_truncated: TruncationStatus = TruncationStatus.NOT_TRUNCATED
    middle_name_truncated: TruncationStatus = TruncationStatus.NOT_TRUNCATED
    last_name_truncated: TruncationStatus = TruncationStatus.NOT_TRUNCATED

    def __post_init__(self) -> None:
        """Validate person data."""
        if not self.first_name or not self.first_name.strip():
            raise ValueError("First name cannot be empty")

        if not self.last_name or not self.last_name.strip():
            raise ValueError("Last name cannot be empty")

        # Validate date of birth is in the past
        if self.date_of_birth >= date.today():
            raise ValueError(f"Date of birth {self.date_of_birth} cannot be in the future")

        # Validate minimum age (must be at least 15 for learner's permit)
        age_days = (date.today() - self.date_of_birth).days
        age_years = age_days / 365.25
        if age_years < 15:
            raise ValueError(f"Person must be at least 15 years old, got {age_years:.1f}")

    @property
    def age(self) -> float:
        """Calculate current age in years."""
        age_days = (date.today() - self.date_of_birth).days
        return age_days / 365.25

    @property
    def full_name(self) -> str:
        """Get full name in 'First Middle Last' format."""
        return f"{self.first_name} {self.middle_name} {self.last_name}"


@dataclass(frozen=True)
class LicenseSubfile:
    """AAMVA DL subfile data structure.

    This represents the primary DL subfile containing driver's license information
    per AAMVA DL/ID Card Design Standard - 2020.

    Attributes:
        license_number: Unique license number (DAQ)
        vehicle_class: Vehicle class code (DCA)
        restrictions: License restrictions (DCB)
        endorsements: License endorsements (DCD)
        expiration_date: License expiration date (DBA)
        issue_date: License issue date (DBD)
        document_discriminator: Unique document ID (DCF)
        country_code: Issuing country code (DCG)
        compliance_type: DHS compliance status (DDA)
        limited_duration: Temporary lawful status indicator (DDD)
        organ_donor: Organ donor status (DDK)
        veteran: Veteran status (DDL)
    """

    # Required fields
    license_number: str  # DAQ
    vehicle_class: str  # DCA
    restrictions: str  # DCB
    endorsements: str  # DCD
    expiration_date: date  # DBA
    issue_date: date  # DBD
    document_discriminator: str  # DCF
    country_code: str  # DCG
    compliance_type: ComplianceType  # DDA
    limited_duration: bool  # DDD
    organ_donor: bool  # DDK
    veteran: bool  # DDL

    # Person info
    person: Person

    # Physical attributes
    physical: PhysicalAttributes

    # Address
    address: Address

    def __post_init__(self) -> None:
        """Validate license subfile data."""
        if not self.license_number:
            raise ValueError("License number cannot be empty")

        if len(self.vehicle_class) == 0:
            raise ValueError("Vehicle class cannot be empty")

        # Validate dates are logical
        if self.issue_date > self.expiration_date:
            raise ValueError(
                f"Issue date {self.issue_date} cannot be after "
                f"expiration {self.expiration_date}"
            )

        if self.issue_date < self.person.date_of_birth:
            raise ValueError(
                f"Issue date {self.issue_date} cannot be before "
                f"birth date {self.person.date_of_birth}"
            )

        # Validate country code
        if len(self.country_code) != 3:
            raise ValueError(f"Country code must be 3 characters, got: {self.country_code}")


@dataclass(frozen=True)
class StateSubfile:
    """State-specific subfile for additional jurisdiction data.

    This represents jurisdiction-specific fields that don't fit in the
    standard DL subfile format.

    Attributes:
        state_code: Two-letter state code (e.g., "CA")
        subfile_type: Subfile designator (e.g., "ZC" for California)
        custom_fields: Dictionary of state-specific field codes and values
    """

    state_code: str
    subfile_type: str
    custom_fields: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate state subfile data."""
        if len(self.state_code) != 2:
            raise ValueError(f"State code must be 2 characters, got: {self.state_code}")

        if not self.subfile_type.startswith("Z"):
            raise ValueError(f"State subfile type must start with 'Z', got: {self.subfile_type}")

        # Validate all field codes are 3 characters (e.g., "ZCA", "ZCB")
        for field_code in self.custom_fields.keys():
            if len(field_code) != 3:
                raise ValueError(
                    f"State field code must be 3 characters, got: {field_code}"
                )


@dataclass(frozen=True)
class License:
    """Complete license data including all subfiles.

    This is the top-level model representing a complete driver's license
    or identification card with all AAMVA-compliant data.

    Attributes:
        dl_subfile: Primary DL subfile data
        state_subfile: State-specific subfile data
        jurisdiction_iin: Issuer Identification Number (6 digits)
    """

    dl_subfile: LicenseSubfile
    state_subfile: StateSubfile
    jurisdiction_iin: str

    def __post_init__(self) -> None:
        """Validate complete license data."""
        # Validate IIN is 6 digits
        if len(self.jurisdiction_iin) != 6:
            raise ValueError(f"IIN must be 6 digits, got: {self.jurisdiction_iin}")

        if not self.jurisdiction_iin.isdigit():
            raise ValueError(f"IIN must be numeric, got: {self.jurisdiction_iin}")

        # Validate state codes match
        if self.dl_subfile.address.state != self.state_subfile.state_code:
            raise ValueError(
                f"DL state {self.dl_subfile.address.state} doesn't match "
                f"state subfile {self.state_subfile.state_code}"
            )

    @property
    def holder_name(self) -> str:
        """Get the license holder's full name."""
        return self.dl_subfile.person.full_name

    @property
    def is_expired(self) -> bool:
        """Check if the license is expired."""
        return date.today() > self.dl_subfile.expiration_date

    @property
    def days_until_expiration(self) -> int:
        """Calculate days until expiration (negative if expired)."""
        delta = self.dl_subfile.expiration_date - date.today()
        return delta.days
