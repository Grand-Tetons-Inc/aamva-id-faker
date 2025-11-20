"""
AAMVA Data Decoding Module.

This module provides functionality for decoding AAMVA-compliant barcode
strings back into structured data.

This is NEW functionality not present in the original implementation,
enabling full round-trip encoding/decoding capability.

The decoding process:
1. Parse and validate header
2. Extract subfile designators
3. Decode each subfile's fields
4. Return structured data

Author: New implementation
License: MIT
"""

from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
import re

from .aamva_spec import (
    AAMVAVersion,
    COMPLIANCE_INDICATOR,
    FILE_TYPE,
    FIELD_SEPARATOR,
    SEGMENT_TERMINATOR,
    SUBFILE_DESIGNATOR_LENGTH,
    get_state_by_iin,
    get_field_definition,
)
from .subfiles import Subfile, DLSubfile, JurisdictionSubfile


class DecodingError(Exception):
    """Base exception for decoding errors."""
    pass


@dataclass
class AAMVAHeader:
    """Parsed AAMVA barcode header information.

    Attributes:
        compliance: Compliance indicator
        file_type: File type (should be "ANSI ")
        iin: Issuer Identification Number (6 digits)
        version: AAMVA version number (2 digits)
        jurisdiction_version: Jurisdiction version (2 digits)
        number_of_entries: Number of subfiles
        jurisdiction_info: Jurisdiction information from IIN
    """
    compliance: str
    file_type: str
    iin: str
    version: str
    jurisdiction_version: str
    number_of_entries: int
    jurisdiction_info: Optional[Dict[str, str]] = None

    @property
    def aamva_version(self) -> Optional[AAMVAVersion]:
        """Get AAMVAVersion enum from version string."""
        try:
            return AAMVAVersion(self.version)
        except ValueError:
            return None


@dataclass
class SubfileDesignator:
    """Subfile designator information.

    Attributes:
        subfile_type: Two-character subfile type
        offset: Byte offset in barcode data
        length: Length of subfile data in bytes
    """
    subfile_type: str
    offset: int
    length: int


class AAMVADecoder:
    """AAMVA barcode data decoder.

    This class handles the decoding of AAMVA-compliant barcode strings
    back into structured data.
    """

    def __init__(self, strict: bool = False):
        """Initialize decoder.

        Args:
            strict: If True, perform strict validation during decoding
        """
        self.strict = strict

    def decode(self, barcode_data: str) -> Tuple[AAMVAHeader, List[Subfile]]:
        """Decode complete AAMVA barcode string.

        Args:
            barcode_data: Complete AAMVA barcode string

        Returns:
            Tuple of (header, list of subfiles)

        Raises:
            DecodingError: If decoding fails
        """
        if not barcode_data:
            raise DecodingError("Empty barcode data")

        # Convert to bytes for accurate offset calculations
        barcode_bytes = barcode_data.encode('ascii')

        # Parse header
        header, header_length = self._parse_header(barcode_data)

        # Parse subfile designators
        designators = self._parse_designators(
            barcode_data,
            header_length,
            header.number_of_entries
        )

        # Decode each subfile
        subfiles = []
        for designator in designators:
            subfile = self._decode_subfile(
                barcode_data,
                designator,
                header.iin
            )
            subfiles.append(subfile)

        return header, subfiles

    def decode_to_dict(self, barcode_data: str) -> Dict[str, Any]:
        """Decode barcode data to dictionary format.

        Args:
            barcode_data: Complete AAMVA barcode string

        Returns:
            Dictionary with header and subfiles data

        Example return:
            {
                'header': {
                    'iin': '636026',
                    'version': '10',
                    'jurisdiction_version': '00',
                    'jurisdiction_info': {...}
                },
                'subfiles': [
                    {
                        'subfile_type': 'DL',
                        'fields': {
                            'DAQ': 'D1234567',
                            'DCS': 'SMITH',
                            ...
                        }
                    }
                ]
            }
        """
        header, subfiles = self.decode(barcode_data)

        result = {
            'header': {
                'compliance': header.compliance,
                'file_type': header.file_type,
                'iin': header.iin,
                'version': header.version,
                'jurisdiction_version': header.jurisdiction_version,
                'number_of_entries': header.number_of_entries,
                'jurisdiction_info': header.jurisdiction_info,
            },
            'subfiles': [subfile.to_dict() for subfile in subfiles]
        }

        return result

    def _parse_header(self, barcode_data: str) -> Tuple[AAMVAHeader, int]:
        """Parse AAMVA header from barcode data.

        Header format:
        - Compliance: @ LF RS CR (4 bytes)
        - File type: "ANSI " (5 bytes)
        - IIN: 6 digits
        - Version: 2 digits
        - Jurisdiction version: 2 digits
        - Number of entries: 2 digits

        Args:
            barcode_data: Barcode string

        Returns:
            Tuple of (AAMVAHeader, header_length_in_bytes)

        Raises:
            DecodingError: If header parsing fails
        """
        # Check minimum length
        min_header_length = 21  # 4 + 5 + 6 + 2 + 2 + 2
        if len(barcode_data) < min_header_length:
            raise DecodingError(
                f"Barcode too short: {len(barcode_data)} bytes (minimum {min_header_length})"
            )

        pos = 0

        # Parse compliance indicator
        compliance = barcode_data[pos:pos+4]
        if compliance != COMPLIANCE_INDICATOR:
            if self.strict:
                raise DecodingError(f"Invalid compliance indicator: {repr(compliance)}")
        pos += 4

        # Parse file type
        file_type = barcode_data[pos:pos+5]
        if file_type != FILE_TYPE:
            if self.strict:
                raise DecodingError(f"Invalid file type: '{file_type}' (expected 'ANSI ')")
        pos += 5

        # Parse IIN
        iin = barcode_data[pos:pos+6]
        if not iin.isdigit():
            raise DecodingError(f"Invalid IIN: '{iin}' (must be 6 digits)")
        jurisdiction_info = get_state_by_iin(iin)
        pos += 6

        # Parse version
        version = barcode_data[pos:pos+2]
        if not version.isdigit():
            raise DecodingError(f"Invalid version: '{version}' (must be 2 digits)")
        pos += 2

        # Parse jurisdiction version
        jurisdiction_version = barcode_data[pos:pos+2]
        if not jurisdiction_version.isdigit():
            raise DecodingError(
                f"Invalid jurisdiction version: '{jurisdiction_version}' (must be 2 digits)"
            )
        pos += 2

        # Parse number of entries
        num_entries_str = barcode_data[pos:pos+2]
        if not num_entries_str.isdigit():
            raise DecodingError(
                f"Invalid number of entries: '{num_entries_str}' (must be 2 digits)"
            )
        num_entries = int(num_entries_str)
        pos += 2

        header = AAMVAHeader(
            compliance=compliance,
            file_type=file_type,
            iin=iin,
            version=version,
            jurisdiction_version=jurisdiction_version,
            number_of_entries=num_entries,
            jurisdiction_info=jurisdiction_info
        )

        return header, pos

    def _parse_designators(
        self,
        barcode_data: str,
        offset: int,
        count: int
    ) -> List[SubfileDesignator]:
        """Parse subfile designators from header.

        Each designator is 10 bytes:
        - Subfile type: 2 characters
        - Offset: 4 digits
        - Length: 4 digits

        Args:
            barcode_data: Barcode string
            offset: Starting offset for designators
            count: Number of designators to parse

        Returns:
            List of SubfileDesignator objects

        Raises:
            DecodingError: If parsing fails
        """
        designators = []

        for i in range(count):
            start = offset + (i * SUBFILE_DESIGNATOR_LENGTH)
            end = start + SUBFILE_DESIGNATOR_LENGTH

            if end > len(barcode_data):
                raise DecodingError(
                    f"Designator {i} extends beyond barcode data"
                )

            designator_str = barcode_data[start:end]

            # Parse components
            subfile_type = designator_str[0:2]
            offset_str = designator_str[2:6]
            length_str = designator_str[6:10]

            # Validate
            if not offset_str.isdigit():
                raise DecodingError(
                    f"Invalid offset in designator {i}: '{offset_str}'"
                )
            if not length_str.isdigit():
                raise DecodingError(
                    f"Invalid length in designator {i}: '{length_str}'"
                )

            designator = SubfileDesignator(
                subfile_type=subfile_type,
                offset=int(offset_str),
                length=int(length_str)
            )

            designators.append(designator)

        return designators

    def _decode_subfile(
        self,
        barcode_data: str,
        designator: SubfileDesignator,
        iin: str
    ) -> Subfile:
        """Decode a single subfile.

        Args:
            barcode_data: Complete barcode string
            designator: Subfile designator
            iin: IIN from header (for context)

        Returns:
            Decoded Subfile

        Raises:
            DecodingError: If decoding fails
        """
        # Extract subfile data
        start = designator.offset
        end = start + designator.length

        if end > len(barcode_data):
            raise DecodingError(
                f"Subfile {designator.subfile_type} extends beyond barcode data"
            )

        subfile_data = barcode_data[start:end]

        # Verify subfile type matches
        if not subfile_data.startswith(designator.subfile_type):
            raise DecodingError(
                f"Subfile type mismatch: expected '{designator.subfile_type}', "
                f"found '{subfile_data[0:2]}'"
            )

        # Parse fields
        fields = self._parse_fields(subfile_data[2:])  # Skip type prefix

        # Create appropriate subfile object
        if designator.subfile_type == "DL":
            subfile = DLSubfile(fields=fields)
        elif designator.subfile_type.startswith("Z"):
            # Jurisdiction-specific subfile
            jurisdiction = fields.get("DAJ")  # Try to get from DL data
            if not jurisdiction and iin:
                # Try to get from IIN
                juris_info = get_state_by_iin(iin)
                jurisdiction = juris_info.get("abbr") if juris_info else None

            subfile = JurisdictionSubfile(
                jurisdiction=jurisdiction or "XX",
                fields=fields,
                custom_type=designator.subfile_type
            )
        else:
            # Generic subfile
            subfile = Subfile(
                subfile_type=designator.subfile_type,
                fields=fields
            )

        subfile.offset = designator.offset
        subfile.length = designator.length

        return subfile

    def _parse_fields(self, data: str) -> Dict[str, str]:
        """Parse fields from subfile data.

        Fields are encoded as: CODE + VALUE + SEPARATOR
        Terminated by SEGMENT_TERMINATOR

        Args:
            data: Subfile data (without type prefix)

        Returns:
            Dictionary of field code -> value

        Raises:
            DecodingError: If parsing fails
        """
        fields = {}

        # Remove segment terminator
        if data.endswith(SEGMENT_TERMINATOR):
            data = data[:-1]

        # Split by field separator
        field_strings = data.split(FIELD_SEPARATOR)

        for field_str in field_strings:
            if not field_str:
                continue  # Skip empty strings

            # Field code is first 3 characters
            if len(field_str) < 3:
                if self.strict:
                    raise DecodingError(f"Invalid field: '{field_str}' (too short)")
                continue

            code = field_str[0:3]
            value = field_str[3:]

            # Validate field code format (3 uppercase alphanumeric)
            if not code.isupper():
                if self.strict:
                    raise DecodingError(f"Invalid field code: '{code}' (must be uppercase)")

            fields[code] = value

        return fields


def decode_license_data(barcode_data: str, strict: bool = False) -> Dict[str, Any]:
    """Convenience function to decode AAMVA barcode data.

    Args:
        barcode_data: Complete AAMVA barcode string
        strict: If True, perform strict validation

    Returns:
        Dictionary with decoded data

    Raises:
        DecodingError: If decoding fails

    Example:
        data = decode_license_data(barcode_string)
        print(data['subfiles'][0]['fields']['DCS'])  # Last name
    """
    decoder = AAMVADecoder(strict=strict)
    return decoder.decode_to_dict(barcode_data)


def extract_dl_fields(barcode_data: str) -> Dict[str, str]:
    """Extract just the DL subfile fields from barcode data.

    This is a convenience function for quickly getting the main
    driver license fields without the full structure.

    Args:
        barcode_data: Complete AAMVA barcode string

    Returns:
        Dictionary of DL field codes and values

    Raises:
        DecodingError: If decoding fails
    """
    data = decode_license_data(barcode_data)

    # Find DL subfile
    for subfile in data['subfiles']:
        if subfile['subfile_type'] == 'DL':
            return subfile['fields']

    raise DecodingError("No DL subfile found in barcode data")
