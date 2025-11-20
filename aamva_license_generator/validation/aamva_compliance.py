"""
AAMVA Standard Compliance Validation.

Validates license data against AAMVA (American Association of Motor Vehicle
Administrators) standards including:
- Data element format compliance
- Barcode encoding requirements
- Field length restrictions
- Character set validation
- Subfile structure validation
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, date
import re
from .schemas import ValidationResult, ValidationLevel, FieldValidationResult


class AAMVACompliance:
    """
    AAMVA DL/ID standard compliance validator.

    Based on AAMVA DL/ID Card Design Standard (2020 version).
    """

    # AAMVA field specifications
    AAMVA_FIELDS = {
        # Mandatory fields
        "DAQ": {"name": "License/ID Number", "max_length": 25, "mandatory": True},
        "DCS": {"name": "Family Name", "max_length": 40, "mandatory": True},
        "DAC": {"name": "First Name", "max_length": 40, "mandatory": True},
        "DBD": {"name": "Issue Date", "format": "MMDDYYYY", "mandatory": True},
        "DBB": {"name": "Date of Birth", "format": "MMDDYYYY", "mandatory": True},
        "DBA": {"name": "Expiration Date", "format": "MMDDYYYY", "mandatory": True},
        "DBC": {"name": "Sex", "values": ["1", "2", "9"], "mandatory": True},
        "DAY": {"name": "Eye Color", "values": ["BLK", "BLU", "BRO", "GRY", "GRN", "HAZ", "MAR", "PNK", "DIC", "UNK"], "mandatory": True},
        "DAU": {"name": "Height", "format": "inches", "mandatory": True},
        "DAG": {"name": "Street Address", "max_length": 35, "mandatory": True},
        "DAI": {"name": "City", "max_length": 20, "mandatory": True},
        "DAJ": {"name": "Jurisdiction Code", "max_length": 2, "mandatory": True},
        "DAK": {"name": "Postal Code", "format": "ZIP+4", "mandatory": True},

        # Optional but common fields
        "DAD": {"name": "Middle Name", "max_length": 40, "mandatory": False},
        "DCA": {"name": "Vehicle Class", "max_length": 4, "mandatory": False},
        "DCB": {"name": "Restrictions", "max_length": 12, "mandatory": False},
        "DCD": {"name": "Endorsements", "max_length": 5, "mandatory": False},
        "DCF": {"name": "Document Discriminator", "max_length": 25, "mandatory": False},
        "DCG": {"name": "Country", "max_length": 3, "mandatory": False},
        "DAW": {"name": "Weight", "format": "pounds", "mandatory": False},
        "DAZ": {"name": "Hair Color", "values": ["BLK", "BLN", "BRO", "GRY", "RED", "WHI", "SDY", "UNK"], "mandatory": False},
        "DCL": {"name": "Race", "values": ["W", "B", "A", "I", "U"], "mandatory": False},

        # Compliance fields (REAL ID)
        "DDA": {"name": "Compliance Type", "values": ["F", "N"], "mandatory": False},
        "DDB": {"name": "Card Revision Date", "format": "MMDDYYYY", "mandatory": False},
        "DDC": {"name": "HazMat Endorsement Expiry", "format": "MMDDYYYY", "mandatory": False},
        "DDD": {"name": "Limited Duration Document", "values": ["0", "1"], "mandatory": False},

        # Truncation indicators
        "DDE": {"name": "Family Name Truncation", "values": ["N", "T", "U"], "mandatory": False},
        "DDF": {"name": "First Name Truncation", "values": ["N", "T", "U"], "mandatory": False},
        "DDG": {"name": "Middle Name Truncation", "values": ["N", "T", "U"], "mandatory": False},

        # Additional optional fields
        "DDK": {"name": "Organ Donor", "values": ["0", "1"], "mandatory": False},
        "DDL": {"name": "Veteran", "values": ["0", "1"], "mandatory": False},
    }

    # Valid IIN (Issuer Identification Number) prefixes
    VALID_IIN_PREFIXES = [
        "604426", "604427", "604428", "604429", "604430", "604431", "604432", "604433", "604434",
        "636000", "636001", "636002", "636003", "636004", "636005", "636006", "636007", "636008",
        "636009", "636010", "636011", "636012", "636013", "636014", "636015", "636016", "636017",
        "636018", "636019", "636020", "636021", "636022", "636023", "636024", "636025", "636026",
        "636028", "636029", "636030", "636031", "636032", "636033", "636034", "636035", "636036",
        "636037", "636038", "636039", "636040", "636041", "636042", "636043", "636044", "636045",
        "636046", "636047", "636048", "636049", "636050", "636051", "636052", "636053", "636054",
        "636055",
    ]

    # Maximum barcode data length (varies by encoding, but 2D PDF417 can handle ~2700 bytes)
    MAX_BARCODE_LENGTH = 2700

    def __init__(self):
        self.results: List[FieldValidationResult] = []

    def validate_field_format(self, field_code: str, value: str) -> FieldValidationResult:
        """
        Validate a single AAMVA field against specification.

        Args:
            field_code: AAMVA field code (e.g., "DAQ", "DCS")
            value: Field value

        Returns:
            FieldValidationResult
        """
        if field_code not in self.AAMVA_FIELDS:
            return FieldValidationResult(
                field_name=field_code,
                is_valid=True,
                level=ValidationLevel.WARNING,
                message=f"Field {field_code} is not in AAMVA standard specification"
            )

        spec = self.AAMVA_FIELDS[field_code]
        field_name = spec["name"]

        # Check mandatory fields
        if spec.get("mandatory", False) and not value:
            return FieldValidationResult(
                field_name=field_code,
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"{field_name} ({field_code}) is mandatory but empty"
            )

        if not value:  # Empty optional field
            return FieldValidationResult(
                field_name=field_code,
                is_valid=True,
                level=ValidationLevel.INFO,
                message=f"{field_name} ({field_code}) is optional and empty"
            )

        # Check maximum length
        if "max_length" in spec:
            max_len = spec["max_length"]
            if len(value) > max_len:
                return FieldValidationResult(
                    field_name=field_code,
                    is_valid=False,
                    level=ValidationLevel.ERROR,
                    message=f"{field_name} ({field_code}) exceeds maximum length "
                            f"({len(value)} > {max_len} chars)",
                    auto_fix=value[:max_len]
                )

        # Check valid values (enum)
        if "values" in spec:
            valid_values = spec["values"]
            if value not in valid_values:
                return FieldValidationResult(
                    field_name=field_code,
                    is_valid=False,
                    level=ValidationLevel.ERROR,
                    message=f"{field_name} ({field_code}) has invalid value '{value}'. "
                            f"Must be one of: {', '.join(valid_values)}",
                    suggestions=valid_values
                )

        # Check date format
        if "format" in spec and spec["format"] == "MMDDYYYY":
            if not re.match(r'^\d{8}$', value):
                return FieldValidationResult(
                    field_name=field_code,
                    is_valid=False,
                    level=ValidationLevel.ERROR,
                    message=f"{field_name} ({field_code}) must be in MMDDYYYY format, got '{value}'"
                )

            # Validate it's a real date
            try:
                month = int(value[0:2])
                day = int(value[2:4])
                year = int(value[4:8])
                date(year, month, day)  # Will raise ValueError if invalid
            except ValueError:
                return FieldValidationResult(
                    field_name=field_code,
                    is_valid=False,
                    level=ValidationLevel.ERROR,
                    message=f"{field_name} ({field_code}) contains invalid date: {value}"
                )

        # Check character set (should be ASCII printable for barcode)
        if not all(32 <= ord(c) <= 126 for c in value):
            return FieldValidationResult(
                field_name=field_code,
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"{field_name} ({field_code}) contains non-ASCII characters"
            )

        return FieldValidationResult(
            field_name=field_code,
            is_valid=True,
            level=ValidationLevel.INFO,
            message=f"{field_name} ({field_code}) complies with AAMVA standard"
        )

    def validate_barcode_length(self, data_dict: Dict[str, str]) -> FieldValidationResult:
        """
        Validate that the total barcode data doesn't exceed maximum length.

        Args:
            data_dict: Dictionary of AAMVA field codes to values

        Returns:
            FieldValidationResult
        """
        # Calculate total encoded length
        total_length = 0

        # Header overhead (~30 bytes)
        total_length += 30

        # Each field: 3 chars for code + value + 1 for newline
        for field_code, value in data_dict.items():
            total_length += 3  # Field code (e.g., "DAQ")
            total_length += len(str(value))
            total_length += 1  # Newline separator

        if total_length > self.MAX_BARCODE_LENGTH:
            return FieldValidationResult(
                field_name="barcode_data",
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"Total barcode data length ({total_length} bytes) exceeds "
                        f"maximum ({self.MAX_BARCODE_LENGTH} bytes). "
                        f"Consider truncating long fields."
            )

        # Warning for large barcodes
        if total_length > 1500:
            return FieldValidationResult(
                field_name="barcode_data",
                is_valid=True,
                level=ValidationLevel.WARNING,
                message=f"Barcode data is large ({total_length} bytes). "
                        f"May be difficult to scan on low-quality printers."
            )

        return FieldValidationResult(
            field_name="barcode_data",
            is_valid=True,
            level=ValidationLevel.INFO,
            message=f"Barcode data length ({total_length} bytes) is within acceptable range"
        )

    def validate_name_truncation(self, data_dict: Dict[str, str]) -> List[FieldValidationResult]:
        """
        Validate name truncation indicators match actual name lengths.

        Args:
            data_dict: Dictionary of AAMVA field codes to values

        Returns:
            List of FieldValidationResults
        """
        results = []

        name_fields = [
            ("DCS", "DDE", "Family Name", 30),
            ("DAC", "DDF", "First Name", 30),
            ("DAD", "DDG", "Middle Name", 30),
        ]

        for name_code, trunc_code, name_type, max_barcode_len in name_fields:
            name_value = data_dict.get(name_code, "")
            trunc_value = data_dict.get(trunc_code, "N")

            if not name_value:
                continue

            name_len = len(name_value)

            # Check if truncation flag is appropriate
            if name_len > max_barcode_len and trunc_value == "N":
                results.append(FieldValidationResult(
                    field_name=trunc_code,
                    is_valid=False,
                    level=ValidationLevel.WARNING,
                    message=f"{name_type} is {name_len} characters (exceeds barcode limit of {max_barcode_len}), "
                            f"but truncation flag is 'N' (not truncated). Should be 'T'.",
                    auto_fix="T"
                ))

            elif name_len <= max_barcode_len and trunc_value == "T":
                results.append(FieldValidationResult(
                    field_name=trunc_code,
                    is_valid=False,
                    level=ValidationLevel.WARNING,
                    message=f"{name_type} is {name_len} characters (within barcode limit of {max_barcode_len}), "
                            f"but truncation flag is 'T' (truncated). Should be 'N'.",
                    auto_fix="N"
                ))

        return results

    def validate_iin(self, state_code: str) -> FieldValidationResult:
        """
        Validate that state has a valid IIN (Issuer Identification Number).

        Args:
            state_code: Two-letter state/jurisdiction code

        Returns:
            FieldValidationResult
        """
        from generate_licenses import IIN_JURISDICTIONS, get_iin_by_state

        iin = get_iin_by_state(state_code)

        if not iin:
            return FieldValidationResult(
                field_name="state",
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"State '{state_code}' does not have a valid AAMVA IIN"
            )

        if iin not in self.VALID_IIN_PREFIXES:
            return FieldValidationResult(
                field_name="state",
                is_valid=False,
                level=ValidationLevel.WARNING,
                message=f"State '{state_code}' IIN '{iin}' is not in standard AAMVA IIN list"
            )

        jurisdiction_info = IIN_JURISDICTIONS.get(iin, {})
        jurisdiction_name = jurisdiction_info.get("jurisdiction", "Unknown")

        return FieldValidationResult(
            field_name="state",
            is_valid=True,
            level=ValidationLevel.INFO,
            message=f"Valid AAMVA IIN: {iin} ({jurisdiction_name})"
        )

    def validate_compliance_type(self, data_dict: Dict[str, str]) -> List[FieldValidationResult]:
        """
        Validate REAL ID compliance indicators.

        Args:
            data_dict: Dictionary of AAMVA field codes to values

        Returns:
            List of FieldValidationResults
        """
        results = []

        compliance_type = data_dict.get("DDA", "N")

        if compliance_type == "F":
            # Full REAL ID compliance
            results.append(FieldValidationResult(
                field_name="DDA",
                is_valid=True,
                level=ValidationLevel.INFO,
                message="Document is REAL ID compliant (Full compliance)"
            ))

            # Check that required fields are present for REAL ID
            required_for_real_id = ["DAQ", "DCS", "DAC", "DBB", "DAG", "DAI", "DAJ", "DAK"]
            missing_fields = [f for f in required_for_real_id if not data_dict.get(f)]

            if missing_fields:
                results.append(FieldValidationResult(
                    field_name="DDA",
                    is_valid=False,
                    level=ValidationLevel.WARNING,
                    message=f"REAL ID compliance requires all mandatory fields, "
                            f"but missing: {', '.join(missing_fields)}"
                ))

        elif compliance_type == "N":
            results.append(FieldValidationResult(
                field_name="DDA",
                is_valid=True,
                level=ValidationLevel.INFO,
                message="Document is NOT REAL ID compliant (Non-compliant)"
            ))

        return results

    def validate_all(self, data_dict: Dict[str, str]) -> ValidationResult:
        """
        Perform comprehensive AAMVA compliance validation.

        Args:
            data_dict: Dictionary of AAMVA field codes to values

        Returns:
            ValidationResult with all compliance checks
        """
        result = ValidationResult(is_valid=True)

        # Validate each field
        for field_code, value in data_dict.items():
            field_result = self.validate_field_format(field_code, str(value))
            result.add_result(field_result)
            if not field_result.is_valid and field_result.level == ValidationLevel.ERROR:
                result.is_valid = False

        # Check mandatory fields are present
        for field_code, spec in self.AAMVA_FIELDS.items():
            if spec.get("mandatory", False) and field_code not in data_dict:
                result.add_result(FieldValidationResult(
                    field_name=field_code,
                    is_valid=False,
                    level=ValidationLevel.ERROR,
                    message=f"Mandatory field {spec['name']} ({field_code}) is missing"
                ))
                result.is_valid = False

        # Validate barcode length
        barcode_result = self.validate_barcode_length(data_dict)
        result.add_result(barcode_result)
        if not barcode_result.is_valid and barcode_result.level == ValidationLevel.ERROR:
            result.is_valid = False

        # Validate name truncation
        truncation_results = self.validate_name_truncation(data_dict)
        for tr in truncation_results:
            result.add_result(tr)

        # Validate IIN
        if "DAJ" in data_dict:
            iin_result = self.validate_iin(data_dict["DAJ"])
            result.add_result(iin_result)
            if not iin_result.is_valid and iin_result.level == ValidationLevel.ERROR:
                result.is_valid = False

        # Validate REAL ID compliance
        compliance_results = self.validate_compliance_type(data_dict)
        for cr in compliance_results:
            result.add_result(cr)

        return result


def check_aamva_compliance(license_data: Dict[str, Any]) -> ValidationResult:
    """
    Convenience function to check AAMVA compliance.

    Args:
        license_data: Dictionary of license data (can use friendly field names)

    Returns:
        ValidationResult with compliance check results
    """
    # Convert friendly names to AAMVA codes if needed
    aamva_dict = {}

    field_mapping = {
        "license_number": "DAQ",
        "last_name": "DCS",
        "first_name": "DAC",
        "middle_name": "DAD",
        "date_of_birth": "DBB",
        "issue_date": "DBD",
        "expiration_date": "DBA",
        "sex": "DBC",
        "eye_color": "DAY",
        "hair_color": "DAZ",
        "height": "DAU",
        "weight": "DAW",
        "address": "DAG",
        "city": "DAI",
        "state": "DAJ",
        "postal_code": "DAK",
        "vehicle_class": "DCA",
        "restrictions": "DCB",
        "endorsements": "DCD",
        "document_discriminator": "DCF",
        "country_of_issuance": "DCG",
        "truncation_last_name": "DDE",
        "truncation_first_name": "DDF",
        "truncation_middle_name": "DDG",
        "compliance_type": "DDA",
        "limited_duration": "DDD",
        "organ_donor": "DDK",
        "veteran": "DDL",
        "race": "DCL",
    }

    for friendly_name, aamva_code in field_mapping.items():
        if friendly_name in license_data:
            value = license_data[friendly_name]

            # Convert dates to AAMVA format (MMDDYYYY)
            if friendly_name in ["date_of_birth", "issue_date", "expiration_date"]:
                if isinstance(value, (date, datetime)):
                    value = value.strftime("%m%d%Y")
                elif isinstance(value, str) and "-" in value:
                    # Convert from YYYY-MM-DD to MMDDYYYY
                    try:
                        dt = datetime.strptime(value, "%Y-%m-%d")
                        value = dt.strftime("%m%d%Y")
                    except ValueError:
                        pass

            aamva_dict[aamva_code] = str(value) if value else ""

    # Also allow direct AAMVA codes
    for key, value in license_data.items():
        if key.startswith("D") and key.upper() in AAMVACompliance.AAMVA_FIELDS:
            aamva_dict[key.upper()] = str(value) if value else ""

    # Run validation
    validator = AAMVACompliance()
    return validator.validate_all(aamva_dict)
