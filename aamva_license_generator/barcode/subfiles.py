"""
AAMVA Subfile Handling Module.

This module provides classes and utilities for handling different AAMVA
subfile types (DL, ZA, ZC, etc.) including validation and data management.

AAMVA DL/ID cards can contain multiple subfiles:
- DL: Driver License data (mandatory)
- ZX: Jurisdiction-specific additional data

Author: Refactored from generate_licenses.py
License: MIT
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from .aamva_spec import (
    SubfileType,
    FieldDefinition,
    AAMVA_FIELDS,
    get_field_definition,
    FIELD_SEPARATOR,
    SEGMENT_TERMINATOR,
)


class SubfileError(Exception):
    """Base exception for subfile-related errors."""
    pass


class SubfileValidationError(SubfileError):
    """Exception raised when subfile validation fails."""
    pass


@dataclass
class Subfile:
    """Represents an AAMVA subfile with data fields.

    Attributes:
        subfile_type: Type identifier (DL, ZA, ZC, etc.)
        fields: Dictionary of field code -> value mappings
        jurisdiction: Optional jurisdiction abbreviation
        offset: Byte offset in the complete barcode data (set during formatting)
        length: Length of the subfile data in bytes (set during formatting)
    """
    subfile_type: str
    fields: Dict[str, str] = field(default_factory=dict)
    jurisdiction: Optional[str] = None
    offset: int = 0
    length: int = 0

    def __post_init__(self):
        """Validate subfile type."""
        # Normalize subfile type to uppercase
        self.subfile_type = self.subfile_type.upper()

        # Validate it's a valid subfile type or jurisdiction-specific
        if len(self.subfile_type) != 2:
            raise SubfileError(
                f"Subfile type must be 2 characters, got '{self.subfile_type}'"
            )

        # Check if it's a known type or starts with Z (jurisdiction-specific)
        valid_types = [st.value for st in SubfileType]
        if self.subfile_type not in valid_types and not self.subfile_type.startswith('Z'):
            raise SubfileError(
                f"Invalid subfile type '{self.subfile_type}'. "
                f"Must be one of {valid_types} or start with 'Z' for jurisdiction-specific."
            )

    def add_field(self, code: str, value: str) -> None:
        """Add a field to the subfile.

        Args:
            code: Three-character field code
            value: Field value

        Raises:
            SubfileValidationError: If field validation fails
        """
        code = code.upper()

        # For DL subfile, validate against known fields
        if self.subfile_type == "DL":
            field_def = get_field_definition(code)
            if field_def:
                is_valid, error_msg = field_def.validate(value)
                if not is_valid:
                    raise SubfileValidationError(
                        f"Field {code} validation failed: {error_msg}"
                    )

        self.fields[code] = value

    def get_field(self, code: str, default: Optional[str] = None) -> Optional[str]:
        """Get a field value by code.

        Args:
            code: Three-character field code
            default: Default value if field not found

        Returns:
            Field value or default
        """
        return self.fields.get(code.upper(), default)

    def has_field(self, code: str) -> bool:
        """Check if subfile contains a field.

        Args:
            code: Three-character field code

        Returns:
            True if field exists
        """
        return code.upper() in self.fields

    def remove_field(self, code: str) -> Optional[str]:
        """Remove a field from the subfile.

        Args:
            code: Three-character field code

        Returns:
            The removed value, or None if field didn't exist
        """
        return self.fields.pop(code.upper(), None)

    def validate(self, strict: bool = False) -> tuple[bool, List[str]]:
        """Validate all fields in the subfile.

        Args:
            strict: If True, enforce all mandatory fields are present

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []

        # Validate each field
        for code, value in self.fields.items():
            field_def = get_field_definition(code)
            if field_def:
                is_valid, error_msg = field_def.validate(value)
                if not is_valid:
                    errors.append(f"{code}: {error_msg}")

        # Check for mandatory fields if strict mode
        if strict and self.subfile_type == "DL":
            from .aamva_spec import get_mandatory_fields, AAMVAVersion

            mandatory = get_mandatory_fields(AAMVAVersion.VERSION_10)
            for code in mandatory:
                if code not in self.fields:
                    errors.append(f"Missing mandatory field: {code}")

        return len(errors) == 0, errors

    def to_dict(self) -> Dict[str, Any]:
        """Convert subfile to dictionary representation.

        Returns:
            Dictionary with subfile data
        """
        return {
            "subfile_type": self.subfile_type,
            "jurisdiction": self.jurisdiction,
            "offset": self.offset,
            "length": self.length,
            "fields": self.fields.copy(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Subfile':
        """Create subfile from dictionary representation.

        Args:
            data: Dictionary with subfile data

        Returns:
            Subfile instance
        """
        subfile = cls(
            subfile_type=data["subfile_type"],
            jurisdiction=data.get("jurisdiction"),
        )
        subfile.offset = data.get("offset", 0)
        subfile.length = data.get("length", 0)
        subfile.fields = data.get("fields", {}).copy()
        return subfile

    def encode(self, include_daq_first: bool = True) -> str:
        """Encode subfile data to AAMVA string format.

        The subfile data is encoded as:
        - Subfile type (2 chars)
        - Field data (code + value + separator for each field)
        - Segment terminator

        Args:
            include_daq_first: If True and DAQ exists, put it first (common practice)

        Returns:
            Encoded subfile data string
        """
        result = self.subfile_type

        # For DL subfiles, DAQ (license number) often comes first
        if include_daq_first and "DAQ" in self.fields:
            result += f"DAQ{self.fields['DAQ']}{FIELD_SEPARATOR}"

        # Add remaining fields
        for code, value in sorted(self.fields.items()):
            if code == "DAQ" and include_daq_first:
                continue  # Already added
            result += f"{code}{value}{FIELD_SEPARATOR}"

        # Add segment terminator
        result += SEGMENT_TERMINATOR

        return result

    def __repr__(self) -> str:
        """String representation of subfile."""
        field_count = len(self.fields)
        return f"Subfile(type={self.subfile_type}, fields={field_count})"

    def __str__(self) -> str:
        """Human-readable string representation."""
        lines = [f"Subfile Type: {self.subfile_type}"]
        if self.jurisdiction:
            lines.append(f"Jurisdiction: {self.jurisdiction}")
        lines.append(f"Fields ({len(self.fields)}):")
        for code, value in sorted(self.fields.items()):
            field_def = get_field_definition(code)
            name = field_def.name if field_def else "Unknown"
            lines.append(f"  {code} ({name}): {value}")
        return "\n".join(lines)


class DLSubfile(Subfile):
    """Driver License subfile (DL) with specific validation."""

    def __init__(self, fields: Optional[Dict[str, str]] = None):
        """Initialize DL subfile.

        Args:
            fields: Optional initial fields
        """
        super().__init__(subfile_type="DL", fields=fields or {})

    def validate(self, strict: bool = True) -> tuple[bool, List[str]]:
        """Validate DL subfile with mandatory field checks by default.

        Args:
            strict: If True, enforce all mandatory fields are present

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        return super().validate(strict=strict)


class JurisdictionSubfile(Subfile):
    """Jurisdiction-specific subfile (ZX) with flexible field validation."""

    def __init__(
        self,
        jurisdiction: str,
        fields: Optional[Dict[str, str]] = None,
        custom_type: Optional[str] = None
    ):
        """Initialize jurisdiction-specific subfile.

        Args:
            jurisdiction: Two-letter jurisdiction abbreviation
            fields: Optional initial fields
            custom_type: Optional custom subfile type (defaults to Z + first letter of jurisdiction)
        """
        if custom_type:
            subfile_type = custom_type.upper()
        else:
            # Default: Z + first letter of jurisdiction (e.g., "ZC" for Colorado)
            subfile_type = f"Z{jurisdiction[0].upper()}"

        super().__init__(
            subfile_type=subfile_type,
            fields=fields or {},
            jurisdiction=jurisdiction.upper()
        )

    def add_custom_field(self, field_label: str, value: str) -> None:
        """Add a custom jurisdiction-specific field.

        For jurisdiction subfiles, fields typically follow the pattern:
        ZX + letter (e.g., ZCW, ZCT for Colorado)

        Args:
            field_label: Custom field label (3 characters)
            value: Field value
        """
        if len(field_label) != 3:
            raise SubfileValidationError(
                f"Field label must be 3 characters, got '{field_label}'"
            )

        field_label = field_label.upper()

        # Verify it starts with the subfile type prefix
        if not field_label.startswith(self.subfile_type):
            raise SubfileValidationError(
                f"Field label '{field_label}' should start with '{self.subfile_type}'"
            )

        self.fields[field_label] = value

    def validate(self, strict: bool = False) -> tuple[bool, List[str]]:
        """Validate jurisdiction subfile (non-strict by default).

        Args:
            strict: If True, perform stricter validation

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        # Jurisdiction subfiles have custom fields, so we don't enforce
        # strict validation by default
        return super().validate(strict=False)


def create_dl_subfile(data: Dict[str, str]) -> DLSubfile:
    """Create a DL subfile from data dictionary.

    Args:
        data: Dictionary of field codes and values

    Returns:
        DLSubfile instance

    Raises:
        SubfileValidationError: If validation fails
    """
    subfile = DLSubfile()

    for code, value in data.items():
        subfile.add_field(code, value)

    return subfile


def create_jurisdiction_subfile(
    jurisdiction: str,
    data: Dict[str, str],
    custom_type: Optional[str] = None
) -> JurisdictionSubfile:
    """Create a jurisdiction-specific subfile from data dictionary.

    Args:
        jurisdiction: Two-letter jurisdiction abbreviation
        data: Dictionary of field codes and values
        custom_type: Optional custom subfile type

    Returns:
        JurisdictionSubfile instance

    Raises:
        SubfileValidationError: If validation fails
    """
    subfile = JurisdictionSubfile(
        jurisdiction=jurisdiction,
        custom_type=custom_type
    )

    for code, value in data.items():
        # Use add_custom_field for fields starting with Z
        if code.startswith('Z'):
            subfile.add_custom_field(code, value)
        else:
            subfile.add_field(code, value)

    return subfile
