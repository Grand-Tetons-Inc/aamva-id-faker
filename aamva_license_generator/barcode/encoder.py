"""
AAMVA Data Encoding Module.

This module provides functionality for encoding structured license data
into AAMVA-compliant barcode strings.

The encoding process:
1. Validate input data
2. Encode each subfile's fields
3. Calculate subfile offsets and lengths
4. Build complete barcode string with header

Author: Refactored from generate_licenses.py
License: MIT
"""

from typing import List, Dict, Optional, Any
from .aamva_spec import (
    AAMVAVersion,
    COMPLIANCE_INDICATOR,
    FILE_TYPE,
    FIELD_SEPARATOR,
    SEGMENT_TERMINATOR,
    SUBFILE_DESIGNATOR_LENGTH,
    get_iin_by_state,
)
from .subfiles import Subfile, DLSubfile, JurisdictionSubfile


class EncodingError(Exception):
    """Base exception for encoding errors."""
    pass


class AAMVAEncoder:
    """AAMVA barcode data encoder.

    This class handles the encoding of structured license data into
    AAMVA-compliant barcode strings following the DL/ID Card Design Standard.
    """

    def __init__(
        self,
        version: AAMVAVersion = AAMVAVersion.VERSION_10,
        jurisdiction_version: str = "00"
    ):
        """Initialize encoder.

        Args:
            version: AAMVA version to use for encoding
            jurisdiction_version: Jurisdiction-specific version code (2 digits)
        """
        self.version = version
        self.jurisdiction_version = jurisdiction_version

        if len(jurisdiction_version) != 2 or not jurisdiction_version.isdigit():
            raise EncodingError(
                f"Jurisdiction version must be 2 digits, got '{jurisdiction_version}'"
            )

    def encode(
        self,
        subfiles: List[Subfile],
        iin: Optional[str] = None,
        validate: bool = True
    ) -> str:
        """Encode subfiles into complete AAMVA barcode string.

        Args:
            subfiles: List of subfiles to encode (DL must be first)
            iin: Issuer Identification Number (6 digits). If None, extracted from DL data
            validate: If True, validate subfiles before encoding

        Returns:
            Complete AAMVA-compliant barcode string

        Raises:
            EncodingError: If encoding fails
        """
        if not subfiles:
            raise EncodingError("At least one subfile required")

        # First subfile must be DL
        if subfiles[0].subfile_type != "DL":
            raise EncodingError("First subfile must be type 'DL'")

        # Validate subfiles if requested
        if validate:
            self._validate_subfiles(subfiles)

        # Determine IIN
        if iin is None:
            iin = self._extract_iin(subfiles[0])

        if not iin or len(iin) != 6 or not iin.isdigit():
            raise EncodingError(f"Invalid IIN: '{iin}'. Must be 6 digits.")

        # Build header
        header_base = self._build_header_base(iin, len(subfiles))

        # Encode subfiles and build designators
        encoded_subfiles = []
        designators = []

        # Calculate initial offset (header + all designators)
        designators_total_length = SUBFILE_DESIGNATOR_LENGTH * len(subfiles)
        current_offset = len(header_base.encode('ascii')) + designators_total_length

        for subfile in subfiles:
            # Encode the subfile data
            encoded_data = subfile.encode()
            encoded_bytes = encoded_data.encode('ascii')
            subfile_length = len(encoded_bytes)

            # Update subfile metadata
            subfile.offset = current_offset
            subfile.length = subfile_length

            # Build designator: TYPE (2) + OFFSET (4) + LENGTH (4)
            designator = f"{subfile.subfile_type}{current_offset:04d}{subfile_length:04d}"
            designators.append(designator)

            # Store encoded data
            encoded_subfiles.append(encoded_data)

            # Update offset for next subfile
            current_offset += subfile_length

        # Build complete barcode
        header = header_base + "".join(designators)
        complete_barcode = header + "".join(encoded_subfiles)

        return complete_barcode

    def encode_from_dict(
        self,
        data: Dict[str, Any],
        validate: bool = True
    ) -> str:
        """Encode barcode data from dictionary format.

        This is a convenience method that accepts data in dictionary format
        and converts it to subfiles before encoding.

        Args:
            data: Dictionary with 'subfiles' list
            validate: If True, validate subfiles before encoding

        Returns:
            Complete AAMVA-compliant barcode string

        Example:
            data = {
                'subfiles': [
                    {
                        'subfile_type': 'DL',
                        'fields': {
                            'DAQ': 'D1234567',
                            'DCS': 'SMITH',
                            'DAC': 'JOHN',
                            ...
                        }
                    }
                ]
            }
        """
        if 'subfiles' not in data:
            raise EncodingError("Data must contain 'subfiles' key")

        subfiles = []
        for subfile_data in data['subfiles']:
            subfile = Subfile.from_dict(subfile_data)
            subfiles.append(subfile)

        return self.encode(subfiles, validate=validate)

    def _build_header_base(self, iin: str, num_entries: int) -> str:
        """Build the AAMVA header (without subfile designators).

        Header format:
        - Compliance indicator: @ LF RS CR
        - File type: "ANSI "
        - IIN: 6 digits
        - Version: 2 digits
        - Jurisdiction version: 2 digits
        - Number of entries: 2 digits

        Args:
            iin: Issuer Identification Number
            num_entries: Number of subfiles

        Returns:
            Header base string
        """
        if num_entries > 99:
            raise EncodingError(f"Too many subfiles: {num_entries} (max 99)")

        header = (
            COMPLIANCE_INDICATOR +
            FILE_TYPE +
            iin +
            self.version.value +
            self.jurisdiction_version +
            f"{num_entries:02d}"
        )

        return header

    def _extract_iin(self, dl_subfile: Subfile) -> Optional[str]:
        """Extract IIN from DL subfile data.

        Attempts to determine IIN from the jurisdiction field (DAJ).

        Args:
            dl_subfile: DL subfile

        Returns:
            IIN string or None if not found
        """
        jurisdiction = dl_subfile.get_field("DAJ")
        if not jurisdiction:
            return None

        iin = get_iin_by_state(jurisdiction)
        return iin

    def _validate_subfiles(self, subfiles: List[Subfile]) -> None:
        """Validate all subfiles before encoding.

        Args:
            subfiles: List of subfiles to validate

        Raises:
            EncodingError: If validation fails
        """
        for i, subfile in enumerate(subfiles):
            # Only validate DL subfile strictly
            strict = (subfile.subfile_type == "DL")

            is_valid, errors = subfile.validate(strict=strict)
            if not is_valid:
                error_list = "\n  - ".join(errors)
                raise EncodingError(
                    f"Subfile {i} ({subfile.subfile_type}) validation failed:\n  - {error_list}"
                )


class AAMVAEncoderBuilder:
    """Builder class for creating AAMVA encoder with fluent interface.

    Example:
        encoder = (AAMVAEncoderBuilder()
                  .with_version(AAMVAVersion.VERSION_10)
                  .with_jurisdiction_version("00")
                  .build())
    """

    def __init__(self):
        """Initialize builder with defaults."""
        self._version = AAMVAVersion.VERSION_10
        self._jurisdiction_version = "00"

    def with_version(self, version: AAMVAVersion) -> 'AAMVAEncoderBuilder':
        """Set AAMVA version.

        Args:
            version: AAMVA version

        Returns:
            Self for chaining
        """
        self._version = version
        return self

    def with_jurisdiction_version(self, version: str) -> 'AAMVAEncoderBuilder':
        """Set jurisdiction version.

        Args:
            version: Jurisdiction version (2 digits)

        Returns:
            Self for chaining
        """
        self._jurisdiction_version = version
        return self

    def build(self) -> AAMVAEncoder:
        """Build the encoder.

        Returns:
            AAMVAEncoder instance
        """
        return AAMVAEncoder(
            version=self._version,
            jurisdiction_version=self._jurisdiction_version
        )


def encode_license_data(
    dl_data: Dict[str, str],
    jurisdiction_data: Optional[Dict[str, str]] = None,
    jurisdiction: Optional[str] = None,
    version: AAMVAVersion = AAMVAVersion.VERSION_10,
    validate: bool = True
) -> str:
    """Convenience function to encode license data from dictionaries.

    Args:
        dl_data: DL subfile field data
        jurisdiction_data: Optional jurisdiction-specific subfile data
        jurisdiction: Jurisdiction abbreviation (required if jurisdiction_data provided)
        version: AAMVA version to use
        validate: If True, validate before encoding

    Returns:
        Encoded AAMVA barcode string

    Raises:
        EncodingError: If encoding fails

    Example:
        dl_data = {
            'DAQ': 'D1234567',
            'DCS': 'SMITH',
            'DAC': 'JOHN',
            'DBB': '01011990',
            ...
        }
        barcode = encode_license_data(dl_data)
    """
    subfiles = []

    # Create DL subfile
    dl_subfile = DLSubfile(fields=dl_data.copy())
    subfiles.append(dl_subfile)

    # Create jurisdiction subfile if data provided
    if jurisdiction_data:
        if not jurisdiction:
            jurisdiction = dl_data.get('DAJ')
            if not jurisdiction:
                raise EncodingError(
                    "Jurisdiction abbreviation required for jurisdiction subfile"
                )

        juris_subfile = JurisdictionSubfile(
            jurisdiction=jurisdiction,
            fields=jurisdiction_data.copy()
        )
        subfiles.append(juris_subfile)

    # Encode
    encoder = AAMVAEncoder(version=version)
    return encoder.encode(subfiles, validate=validate)
