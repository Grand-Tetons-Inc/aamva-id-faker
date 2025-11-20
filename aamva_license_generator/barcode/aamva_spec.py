"""
AAMVA DL/ID Card Design Standard Specification Module.

This module contains complete field definitions, data types, validation rules,
and version specifications for the AAMVA DL/ID Card Design Standard.

Primary support for AAMVA DL/ID-2020 (Version 10) with extensibility
for other versions.

References:
    - AAMVA DL/ID Card Design Standard (2020)
    - https://www.aamva.org/identity/issuer-identification-numbers-(iin)

Author: Refactored from generate_licenses.py
License: MIT
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import re


class AAMVAVersion(Enum):
    """AAMVA DL/ID specification versions."""
    VERSION_01 = "01"  # AAMVA DL/ID-2000
    VERSION_02 = "02"  # AAMVA DL/ID-2003
    VERSION_03 = "03"  # AAMVA DL/ID-2005
    VERSION_04 = "04"  # AAMVA DL/ID-2009
    VERSION_05 = "05"  # AAMVA DL/ID-2010
    VERSION_06 = "06"  # AAMVA DL/ID-2011
    VERSION_07 = "07"  # AAMVA DL/ID-2012
    VERSION_08 = "08"  # AAMVA DL/ID-2013
    VERSION_09 = "09"  # AAMVA DL/ID-2016
    VERSION_10 = "10"  # AAMVA DL/ID-2020 (Current)


class SubfileType(Enum):
    """AAMVA subfile type identifiers."""
    DL = "DL"  # Driver License data
    ZA = "ZA"  # Jurisdiction-specific: Alaska
    ZC = "ZC"  # Jurisdiction-specific: Colorado
    ZF = "ZF"  # Jurisdiction-specific: Florida
    ZI = "ZI"  # Jurisdiction-specific: Illinois
    ZN = "ZN"  # Jurisdiction-specific: New York
    ZO = "ZO"  # Jurisdiction-specific: Ohio
    ZT = "ZT"  # Jurisdiction-specific: Texas
    ZV = "ZV"  # Jurisdiction-specific: Virginia
    # Generic jurisdiction-specific subfiles (first letter of state)
    # Will be dynamically determined based on state


class FieldDataType(Enum):
    """Data types for AAMVA fields."""
    ALPHA = "alpha"            # Alphabetic characters only
    NUMERIC = "numeric"        # Numeric characters only
    ALPHANUMERIC = "alphanumeric"  # Alphanumeric characters
    SPECIAL = "special"        # Special characters allowed
    DATE = "date"              # Date in MMDDYYYY format
    BINARY = "binary"          # Binary data


class FieldCategory(Enum):
    """Categories of AAMVA fields."""
    MANDATORY = "mandatory"
    OPTIONAL = "optional"
    CONDITIONAL = "conditional"


@dataclass
class FieldDefinition:
    """Definition of an AAMVA data field.

    Attributes:
        code: Three-character field identifier (e.g., 'DAC', 'DBA')
        name: Human-readable field name
        data_type: Type of data (alpha, numeric, date, etc.)
        max_length: Maximum field length (None for variable)
        min_length: Minimum field length
        category: Whether field is mandatory, optional, or conditional
        description: Field description
        valid_values: List of valid values (for enumerated fields)
        pattern: Regex pattern for validation
        version_added: AAMVA version when field was introduced
        version_deprecated: AAMVA version when field was deprecated
    """
    code: str
    name: str
    data_type: FieldDataType
    max_length: Optional[int] = None
    min_length: int = 0
    category: FieldCategory = FieldCategory.OPTIONAL
    description: str = ""
    valid_values: Optional[List[str]] = None
    pattern: Optional[str] = None
    version_added: AAMVAVersion = AAMVAVersion.VERSION_01
    version_deprecated: Optional[AAMVAVersion] = None

    def validate(self, value: str) -> tuple[bool, Optional[str]]:
        """Validate a field value against this definition.

        Args:
            value: The value to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(value, str):
            return False, f"Value must be string, got {type(value).__name__}"

        # Length validation
        if self.max_length and len(value) > self.max_length:
            return False, f"Value exceeds maximum length {self.max_length}"
        if len(value) < self.min_length:
            return False, f"Value below minimum length {self.min_length}"

        # Valid values check
        if self.valid_values and value not in self.valid_values:
            return False, f"Invalid value '{value}'; must be one of {self.valid_values}"

        # Pattern validation
        if self.pattern and not re.match(self.pattern, value):
            return False, f"Value '{value}' does not match required pattern"

        # Data type validation
        if self.data_type == FieldDataType.NUMERIC:
            if not value.isdigit():
                return False, "Value must contain only digits"
        elif self.data_type == FieldDataType.ALPHA:
            if not value.isalpha():
                return False, "Value must contain only letters"
        elif self.data_type == FieldDataType.DATE:
            if not re.match(r'^\d{8}$', value):
                return False, "Date must be in MMDDYYYY format"
            # Further date validation could be added here

        return True, None


# AAMVA Field Definitions (Version 10 / DL/ID-2020)
# Based on AAMVA DL/ID Card Design Standard
AAMVA_FIELDS: Dict[str, FieldDefinition] = {
    # Mandatory Fields
    "DCA": FieldDefinition(
        code="DCA",
        name="Jurisdiction-specific vehicle class",
        data_type=FieldDataType.ALPHANUMERIC,
        max_length=6,
        category=FieldCategory.MANDATORY,
        description="Jurisdiction-specific vehicle class / group code",
        version_added=AAMVAVersion.VERSION_01
    ),
    "DCB": FieldDefinition(
        code="DCB",
        name="Jurisdiction-specific restriction codes",
        data_type=FieldDataType.ALPHANUMERIC,
        max_length=12,
        category=FieldCategory.MANDATORY,
        description="Jurisdiction-specific restriction codes",
        version_added=AAMVAVersion.VERSION_01
    ),
    "DCD": FieldDefinition(
        code="DCD",
        name="Jurisdiction-specific endorsement codes",
        data_type=FieldDataType.ALPHANUMERIC,
        max_length=5,
        category=FieldCategory.MANDATORY,
        description="Jurisdiction-specific endorsement codes",
        version_added=AAMVAVersion.VERSION_01
    ),
    "DBA": FieldDefinition(
        code="DBA",
        name="Document Expiration Date",
        data_type=FieldDataType.DATE,
        max_length=8,
        min_length=8,
        category=FieldCategory.MANDATORY,
        description="Document expiration date in MMDDYYYY format",
        pattern=r'^\d{8}$',
        version_added=AAMVAVersion.VERSION_01
    ),
    "DCS": FieldDefinition(
        code="DCS",
        name="Customer Family Name",
        data_type=FieldDataType.ALPHA,
        max_length=40,
        min_length=1,
        category=FieldCategory.MANDATORY,
        description="Last name / family name / surname",
        version_added=AAMVAVersion.VERSION_01
    ),
    "DAC": FieldDefinition(
        code="DAC",
        name="Customer First Name",
        data_type=FieldDataType.ALPHA,
        max_length=40,
        min_length=1,
        category=FieldCategory.MANDATORY,
        description="First name / given name",
        version_added=AAMVAVersion.VERSION_01
    ),
    "DAD": FieldDefinition(
        code="DAD",
        name="Customer Middle Name",
        data_type=FieldDataType.ALPHA,
        max_length=40,
        category=FieldCategory.OPTIONAL,
        description="Middle name or middle initial",
        version_added=AAMVAVersion.VERSION_01
    ),
    "DBD": FieldDefinition(
        code="DBD",
        name="Document Issue Date",
        data_type=FieldDataType.DATE,
        max_length=8,
        min_length=8,
        category=FieldCategory.MANDATORY,
        description="Document issue date in MMDDYYYY format",
        pattern=r'^\d{8}$',
        version_added=AAMVAVersion.VERSION_01
    ),
    "DBB": FieldDefinition(
        code="DBB",
        name="Date of Birth",
        data_type=FieldDataType.DATE,
        max_length=8,
        min_length=8,
        category=FieldCategory.MANDATORY,
        description="Date of birth in MMDDYYYY format",
        pattern=r'^\d{8}$',
        version_added=AAMVAVersion.VERSION_01
    ),
    "DBC": FieldDefinition(
        code="DBC",
        name="Physical Description - Sex",
        data_type=FieldDataType.NUMERIC,
        max_length=1,
        min_length=1,
        category=FieldCategory.MANDATORY,
        description="Sex: 1=Male, 2=Female, 9=Not specified",
        valid_values=["1", "2", "9"],
        version_added=AAMVAVersion.VERSION_01
    ),
    "DAY": FieldDefinition(
        code="DAY",
        name="Physical Description - Eye Color",
        data_type=FieldDataType.ALPHA,
        max_length=3,
        min_length=3,
        category=FieldCategory.MANDATORY,
        description="Eye color code",
        valid_values=["BLK", "BLU", "BRO", "GRY", "GRN", "HAZ", "MAR", "PNK", "DIC", "UNK"],
        version_added=AAMVAVersion.VERSION_01
    ),
    "DAU": FieldDefinition(
        code="DAU",
        name="Height",
        data_type=FieldDataType.ALPHANUMERIC,
        max_length=6,
        category=FieldCategory.MANDATORY,
        description="Height in format: FT-IN (e.g., 509 = 5'9\"), or CM",
        version_added=AAMVAVersion.VERSION_01
    ),
    "DAG": FieldDefinition(
        code="DAG",
        name="Address - Street 1",
        data_type=FieldDataType.ALPHANUMERIC,
        max_length=35,
        category=FieldCategory.MANDATORY,
        description="Street address line 1",
        version_added=AAMVAVersion.VERSION_01
    ),
    "DAI": FieldDefinition(
        code="DAI",
        name="Address - City",
        data_type=FieldDataType.ALPHANUMERIC,
        max_length=20,
        category=FieldCategory.MANDATORY,
        description="City",
        version_added=AAMVAVersion.VERSION_01
    ),
    "DAJ": FieldDefinition(
        code="DAJ",
        name="Address - Jurisdiction Code",
        data_type=FieldDataType.ALPHA,
        max_length=2,
        min_length=2,
        category=FieldCategory.MANDATORY,
        description="State/Province/Territory abbreviation",
        version_added=AAMVAVersion.VERSION_01
    ),
    "DAK": FieldDefinition(
        code="DAK",
        name="Address - Postal Code",
        data_type=FieldDataType.ALPHANUMERIC,
        max_length=11,
        category=FieldCategory.MANDATORY,
        description="ZIP or Postal Code",
        version_added=AAMVAVersion.VERSION_01
    ),
    "DAQ": FieldDefinition(
        code="DAQ",
        name="Customer ID Number",
        data_type=FieldDataType.ALPHANUMERIC,
        max_length=25,
        min_length=1,
        category=FieldCategory.MANDATORY,
        description="Driver license or ID number",
        version_added=AAMVAVersion.VERSION_01
    ),
    "DCF": FieldDefinition(
        code="DCF",
        name="Document Discriminator",
        data_type=FieldDataType.ALPHANUMERIC,
        max_length=25,
        category=FieldCategory.MANDATORY,
        description="Unique document control number",
        version_added=AAMVAVersion.VERSION_01
    ),
    "DCG": FieldDefinition(
        code="DCG",
        name="Country Identification",
        data_type=FieldDataType.ALPHA,
        max_length=3,
        min_length=3,
        category=FieldCategory.MANDATORY,
        description="Country of issuance (ISO 3166)",
        valid_values=["USA", "CAN"],
        version_added=AAMVAVersion.VERSION_01
    ),

    # Optional but Common Fields
    "DAW": FieldDefinition(
        code="DAW",
        name="Weight (pounds)",
        data_type=FieldDataType.NUMERIC,
        max_length=3,
        category=FieldCategory.OPTIONAL,
        description="Weight in pounds",
        version_added=AAMVAVersion.VERSION_01
    ),
    "DAZ": FieldDefinition(
        code="DAZ",
        name="Hair Color",
        data_type=FieldDataType.ALPHA,
        max_length=3,
        min_length=3,
        category=FieldCategory.OPTIONAL,
        description="Hair color code",
        valid_values=["BLK", "BLN", "BRO", "GRY", "RED", "WHI", "SDY", "UNK", "BAL"],
        version_added=AAMVAVersion.VERSION_01
    ),
    "DCL": FieldDefinition(
        code="DCL",
        name="Race / Ethnicity",
        data_type=FieldDataType.ALPHA,
        max_length=2,
        category=FieldCategory.OPTIONAL,
        description="Race/Ethnicity: AI=Alaskan/American Indian, AP=Asian/Pacific Islander, "
                    "BK=Black, H=Hispanic Origin, O=Other, U=Unknown, W=White",
        valid_values=["AI", "AP", "BK", "H", "O", "U", "W", "A", "B", "I"],
        version_added=AAMVAVersion.VERSION_01
    ),

    # AAMVA Version 2+ Fields
    "DDE": FieldDefinition(
        code="DDE",
        name="Family Name Truncation",
        data_type=FieldDataType.ALPHA,
        max_length=1,
        min_length=1,
        category=FieldCategory.OPTIONAL,
        description="Family name truncation: N=None, T=Truncated, U=Unknown",
        valid_values=["N", "T", "U"],
        version_added=AAMVAVersion.VERSION_02
    ),
    "DDF": FieldDefinition(
        code="DDF",
        name="First Name Truncation",
        data_type=FieldDataType.ALPHA,
        max_length=1,
        min_length=1,
        category=FieldCategory.OPTIONAL,
        description="First name truncation: N=None, T=Truncated, U=Unknown",
        valid_values=["N", "T", "U"],
        version_added=AAMVAVersion.VERSION_02
    ),
    "DDG": FieldDefinition(
        code="DDG",
        name="Middle Name Truncation",
        data_type=FieldDataType.ALPHA,
        max_length=1,
        min_length=1,
        category=FieldCategory.OPTIONAL,
        description="Middle name truncation: N=None, T=Truncated, U=Unknown",
        valid_values=["N", "T", "U"],
        version_added=AAMVAVersion.VERSION_02
    ),

    # AAMVA Version 4+ Fields (2009+)
    "DDA": FieldDefinition(
        code="DDA",
        name="Compliance Type",
        data_type=FieldDataType.ALPHA,
        max_length=1,
        min_length=1,
        category=FieldCategory.OPTIONAL,
        description="Compliance type: F=Fully Compliant, N=Non-Compliant",
        valid_values=["F", "N", "M"],
        version_added=AAMVAVersion.VERSION_04
    ),
    "DDB": FieldDefinition(
        code="DDB",
        name="Card Revision Date",
        data_type=FieldDataType.DATE,
        max_length=8,
        min_length=8,
        category=FieldCategory.OPTIONAL,
        description="Date card was revised in MMDDYYYY format",
        pattern=r'^\d{8}$',
        version_added=AAMVAVersion.VERSION_04
    ),
    "DDC": FieldDefinition(
        code="DDC",
        name="Hazmat Endorsement Expiry",
        data_type=FieldDataType.DATE,
        max_length=8,
        min_length=8,
        category=FieldCategory.CONDITIONAL,
        description="Hazmat endorsement expiration date in MMDDYYYY format",
        pattern=r'^\d{8}$',
        version_added=AAMVAVersion.VERSION_04
    ),
    "DDD": FieldDefinition(
        code="DDD",
        name="Limited Duration Document Indicator",
        data_type=FieldDataType.NUMERIC,
        max_length=1,
        min_length=1,
        category=FieldCategory.OPTIONAL,
        description="Limited duration document: 1=Yes, 0=No",
        valid_values=["0", "1"],
        version_added=AAMVAVersion.VERSION_04
    ),

    # AAMVA Version 8+ Fields (2013+)
    "DDK": FieldDefinition(
        code="DDK",
        name="Organ Donor Indicator",
        data_type=FieldDataType.NUMERIC,
        max_length=1,
        min_length=1,
        category=FieldCategory.OPTIONAL,
        description="Organ donor: 1=Yes, 0=No",
        valid_values=["0", "1"],
        version_added=AAMVAVersion.VERSION_08
    ),
    "DDL": FieldDefinition(
        code="DDL",
        name="Veteran Indicator",
        data_type=FieldDataType.NUMERIC,
        max_length=1,
        min_length=1,
        category=FieldCategory.OPTIONAL,
        description="Veteran: 1=Yes, 0=No",
        valid_values=["0", "1"],
        version_added=AAMVAVersion.VERSION_08
    ),

    # Additional optional fields
    "DAH": FieldDefinition(
        code="DAH",
        name="Address - Street 2",
        data_type=FieldDataType.ALPHANUMERIC,
        max_length=35,
        category=FieldCategory.OPTIONAL,
        description="Street address line 2",
        version_added=AAMVAVersion.VERSION_01
    ),
    "DAL": FieldDefinition(
        code="DAL",
        name="Address - Street 3",
        data_type=FieldDataType.ALPHANUMERIC,
        max_length=35,
        category=FieldCategory.OPTIONAL,
        description="Street address line 3 (Canada only)",
        version_added=AAMVAVersion.VERSION_01
    ),
    "DAO": FieldDefinition(
        code="DAO",
        name="Name Suffix",
        data_type=FieldDataType.ALPHANUMERIC,
        max_length=10,
        category=FieldCategory.OPTIONAL,
        description="Name suffix (Jr, Sr, III, etc.)",
        version_added=AAMVAVersion.VERSION_01
    ),
    "DAP": FieldDefinition(
        code="DAP",
        name="Name Prefix",
        data_type=FieldDataType.ALPHANUMERIC,
        max_length=10,
        category=FieldCategory.OPTIONAL,
        description="Name prefix (Dr, Mr, Ms, etc.)",
        version_added=AAMVAVersion.VERSION_01
    ),
    "DAR": FieldDefinition(
        code="DAR",
        name="Name Suffix",  # Duplicate - kept for compatibility
        data_type=FieldDataType.ALPHANUMERIC,
        max_length=5,
        category=FieldCategory.OPTIONAL,
        description="Name suffix (alternate field)",
        version_added=AAMVAVersion.VERSION_01
    ),
    "DAS": FieldDefinition(
        code="DAS",
        name="Name Prefix",  # Duplicate - kept for compatibility
        data_type=FieldDataType.ALPHANUMERIC,
        max_length=5,
        category=FieldCategory.OPTIONAL,
        description="Name prefix (alternate field)",
        version_added=AAMVAVersion.VERSION_01
    ),
    "DAT": FieldDefinition(
        code="DAT",
        name="Name - Full",
        data_type=FieldDataType.ALPHANUMERIC,
        max_length=200,
        category=FieldCategory.OPTIONAL,
        description="Full name",
        version_added=AAMVAVersion.VERSION_01
    ),
}


# Issuer Identification Numbers (IINs)
# Source: https://www.aamva.org/identity/issuer-identification-numbers-(iin)
IIN_JURISDICTIONS: Dict[str, Dict[str, str]] = {
    "604426": {"jurisdiction": "Prince Edward Island", "abbr": "PE", "country": "Canada"},
    "604427": {"jurisdiction": "American Samoa", "abbr": "AS", "country": "USA"},
    "604428": {"jurisdiction": "Quebec", "abbr": "QC", "country": "Canada"},
    "604429": {"jurisdiction": "Yukon", "abbr": "YT", "country": "Canada"},
    "604430": {"jurisdiction": "Northern Marianna Islands", "abbr": "MP", "country": "USA"},
    "604431": {"jurisdiction": "Puerto Rico", "abbr": "PR", "country": "USA"},
    "604432": {"jurisdiction": "Alberta", "abbr": "AB", "country": "Canada"},
    "604433": {"jurisdiction": "Nunavut", "abbr": "NU", "country": "Canada"},
    "604434": {"jurisdiction": "Northwest Territories", "abbr": "NT", "country": "Canada"},
    "636000": {"jurisdiction": "Virginia", "abbr": "VA", "country": "USA"},
    "636001": {"jurisdiction": "New York", "abbr": "NY", "country": "USA"},
    "636002": {"jurisdiction": "Massachusetts", "abbr": "MA", "country": "USA"},
    "636003": {"jurisdiction": "Maryland", "abbr": "MD", "country": "USA"},
    "636004": {"jurisdiction": "North Carolina", "abbr": "NC", "country": "USA"},
    "636005": {"jurisdiction": "South Carolina", "abbr": "SC", "country": "USA"},
    "636006": {"jurisdiction": "Connecticut", "abbr": "CT", "country": "USA"},
    "636007": {"jurisdiction": "Louisiana", "abbr": "LA", "country": "USA"},
    "636008": {"jurisdiction": "Montana", "abbr": "MT", "country": "USA"},
    "636009": {"jurisdiction": "New Mexico", "abbr": "NM", "country": "USA"},
    "636010": {"jurisdiction": "Florida", "abbr": "FL", "country": "USA"},
    "636011": {"jurisdiction": "Delaware", "abbr": "DE", "country": "USA"},
    "636012": {"jurisdiction": "Ontario", "abbr": "ON", "country": "Canada"},
    "636013": {"jurisdiction": "Nova Scotia", "abbr": "NS", "country": "Canada"},
    "636014": {"jurisdiction": "California", "abbr": "CA", "country": "USA"},
    "636015": {"jurisdiction": "Texas", "abbr": "TX", "country": "USA"},
    "636016": {"jurisdiction": "Newfoundland", "abbr": "NF", "country": "Canada"},
    "636017": {"jurisdiction": "New Brunswick", "abbr": "NB", "country": "Canada"},
    "636018": {"jurisdiction": "Iowa", "abbr": "IA", "country": "USA"},
    "636019": {"jurisdiction": "Guam", "abbr": "GU", "country": "USA"},
    "636020": {"jurisdiction": "Colorado", "abbr": "CO", "country": "USA"},
    "636021": {"jurisdiction": "Arkansas", "abbr": "AR", "country": "USA"},
    "636022": {"jurisdiction": "Kansas", "abbr": "KS", "country": "USA"},
    "636023": {"jurisdiction": "Ohio", "abbr": "OH", "country": "USA"},
    "636024": {"jurisdiction": "Vermont", "abbr": "VT", "country": "USA"},
    "636025": {"jurisdiction": "Pennsylvania", "abbr": "PA", "country": "USA"},
    "636026": {"jurisdiction": "Arizona", "abbr": "AZ", "country": "USA"},
    "636027": {"jurisdiction": "State Dept. (Diplomatic)", "abbr": "SD", "country": "USA"},
    "636028": {"jurisdiction": "British Columbia", "abbr": "BC", "country": "Canada"},
    "636029": {"jurisdiction": "Oregon", "abbr": "OR", "country": "USA"},
    "636030": {"jurisdiction": "Missouri", "abbr": "MO", "country": "USA"},
    "636031": {"jurisdiction": "Wisconsin", "abbr": "WI", "country": "USA"},
    "636032": {"jurisdiction": "Michigan", "abbr": "MI", "country": "USA"},
    "636033": {"jurisdiction": "Alabama", "abbr": "AL", "country": "USA"},
    "636034": {"jurisdiction": "North Dakota", "abbr": "ND", "country": "USA"},
    "636035": {"jurisdiction": "Illinois", "abbr": "IL", "country": "USA"},
    "636036": {"jurisdiction": "New Jersey", "abbr": "NJ", "country": "USA"},
    "636037": {"jurisdiction": "Indiana", "abbr": "IN", "country": "USA"},
    "636038": {"jurisdiction": "Minnesota", "abbr": "MN", "country": "USA"},
    "636039": {"jurisdiction": "New Hampshire", "abbr": "NH", "country": "USA"},
    "636040": {"jurisdiction": "Utah", "abbr": "UT", "country": "USA"},
    "636041": {"jurisdiction": "Maine", "abbr": "ME", "country": "USA"},
    "636042": {"jurisdiction": "South Dakota", "abbr": "SD", "country": "USA"},
    "636043": {"jurisdiction": "District of Columbia", "abbr": "DC", "country": "USA"},
    "636044": {"jurisdiction": "Saskatchewan", "abbr": "SK", "country": "Canada"},
    "636045": {"jurisdiction": "Washington", "abbr": "WA", "country": "USA"},
    "636046": {"jurisdiction": "Kentucky", "abbr": "KY", "country": "USA"},
    "636047": {"jurisdiction": "Hawaii", "abbr": "HI", "country": "USA"},
    "636048": {"jurisdiction": "Manitoba", "abbr": "MB", "country": "Canada"},
    "636049": {"jurisdiction": "Nevada", "abbr": "NV", "country": "USA"},
    "636050": {"jurisdiction": "Idaho", "abbr": "ID", "country": "USA"},
    "636051": {"jurisdiction": "Mississippi", "abbr": "MS", "country": "USA"},
    "636052": {"jurisdiction": "Rhode Island", "abbr": "RI", "country": "USA"},
    "636053": {"jurisdiction": "Tennessee", "abbr": "TN", "country": "USA"},
    "636054": {"jurisdiction": "Nebraska", "abbr": "NE", "country": "USA"},
    "636055": {"jurisdiction": "Georgia", "abbr": "GA", "country": "USA"},
}


def get_iin_by_state(state_abbr: str) -> Optional[str]:
    """Get IIN by state/jurisdiction abbreviation.

    Args:
        state_abbr: Two-letter state/jurisdiction abbreviation

    Returns:
        Six-digit IIN string, or None if not found
    """
    state_abbr_upper = state_abbr.upper()
    for iin, info in IIN_JURISDICTIONS.items():
        if info['abbr'].upper() == state_abbr_upper:
            return iin
    return None


def get_state_by_iin(iin: str) -> Optional[Dict[str, str]]:
    """Get jurisdiction information by IIN.

    Args:
        iin: Six-digit IIN string

    Returns:
        Dictionary with jurisdiction info, or None if not found
    """
    return IIN_JURISDICTIONS.get(iin)


# Format control characters
COMPLIANCE_INDICATOR = "@\n\x1E\r"  # @ LF RS CR
FILE_TYPE = "ANSI "
FIELD_SEPARATOR = "\n"  # LF (Line Feed)
SEGMENT_TERMINATOR = "\r"  # CR (Carriage Return)
SUBFILE_DESIGNATOR_LENGTH = 10  # 2 (type) + 4 (offset) + 4 (length)


def get_mandatory_fields(version: AAMVAVersion = AAMVAVersion.VERSION_10) -> List[str]:
    """Get list of mandatory field codes for a given AAMVA version.

    Args:
        version: AAMVA version

    Returns:
        List of mandatory field codes
    """
    mandatory = []
    for code, field_def in AAMVA_FIELDS.items():
        if (field_def.category == FieldCategory.MANDATORY and
            field_def.version_added.value <= version.value and
            (field_def.version_deprecated is None or
             field_def.version_deprecated.value > version.value)):
            mandatory.append(code)
    return mandatory


def get_field_definition(code: str) -> Optional[FieldDefinition]:
    """Get field definition by code.

    Args:
        code: Three-character field code

    Returns:
        FieldDefinition object, or None if not found
    """
    return AAMVA_FIELDS.get(code.upper())
