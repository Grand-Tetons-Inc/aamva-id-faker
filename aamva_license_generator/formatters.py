"""
AAMVA barcode formatting logic.

This module provides formatters for encoding license data into
AAMVA DL/ID-2020 compliant barcode format (PDF417).
"""

from typing import Protocol, Any
from datetime import date

from .models import License, LicenseSubfile, StateSubfile


class BarcodeFormatterProtocol(Protocol):
    """Protocol for barcode formatters."""

    def format(self, license_data: License) -> str:
        """Format license data into barcode string.

        Args:
            license_data: Complete license data

        Returns:
            AAMVA-compliant barcode string ready for PDF417 encoding
        """
        ...


class AAMVABarcodeFormatter:
    """Formatter for AAMVA DL/ID-2020 standard barcodes.

    This formatter converts License objects into properly formatted
    AAMVA barcode strings that can be encoded as PDF417 barcodes.

    Reference: AAMVA DL/ID Card Design Standard (2020)
    """

    # AAMVA Standard Constants
    COMPLIANCE_INDICATOR = "@\n\x1E\r"  # @ + LF + RS + CR
    FILE_TYPE = "ANSI "
    VERSION_NUMBER = "10"  # AAMVA 2020 version
    JURISDICTION_VERSION = "00"  # Default jurisdiction version

    @staticmethod
    def format_date(d: date) -> str:
        """Format date as MMDDYYYY per AAMVA standard.

        Args:
            d: Date to format

        Returns:
            Date string in MMDDYYYY format (e.g., "01152025")
        """
        return d.strftime("%m%d%Y")

    def format(self, license_data: License) -> str:
        """Format complete license data into AAMVA barcode string.

        Args:
            license_data: Complete license data including all subfiles

        Returns:
            AAMVA-compliant barcode string

        The barcode format is:
        1. Compliance indicator (@LF RS CR)
        2. File type (ANSI )
        3. IIN (6 digits)
        4. AAMVA version (2 digits)
        5. Jurisdiction version (2 digits)
        6. Number of entries (2 digits)
        7. Subfile designators (10 bytes each)
        8. Subfile data
        """
        # Build header
        header = self._build_header(license_data)

        # Build subfiles
        dl_subfile_data = self._format_dl_subfile(license_data.dl_subfile)
        state_subfile_data = self._format_state_subfile(license_data.state_subfile)

        # Calculate offsets and lengths
        num_subfiles = 2
        subfile_designators_length = 10 * num_subfiles

        # DL subfile designator
        dl_offset = len(
            (
                self.COMPLIANCE_INDICATOR
                + self.FILE_TYPE
                + license_data.jurisdiction_iin
                + self.VERSION_NUMBER
                + self.JURISDICTION_VERSION
                + f"{num_subfiles:02d}"
                + ("X" * subfile_designators_length)  # Placeholder
            ).encode("ascii")
        )
        dl_length = len(dl_subfile_data.encode("ascii"))
        dl_designator = f"DL{dl_offset:04d}{dl_length:04d}"

        # State subfile designator
        state_offset = dl_offset + dl_length
        state_length = len(state_subfile_data.encode("ascii"))
        state_designator = (
            f"{license_data.state_subfile.subfile_type}"
            f"{state_offset:04d}{state_length:04d}"
        )

        # Assemble complete barcode
        barcode = (
            self.COMPLIANCE_INDICATOR
            + self.FILE_TYPE
            + license_data.jurisdiction_iin
            + self.VERSION_NUMBER
            + self.JURISDICTION_VERSION
            + f"{num_subfiles:02d}"
            + dl_designator
            + state_designator
            + dl_subfile_data
            + state_subfile_data
        )

        return barcode

    def _build_header(self, license_data: License) -> str:
        """Build AAMVA barcode header.

        Args:
            license_data: Complete license data

        Returns:
            Formatted header string
        """
        return (
            self.COMPLIANCE_INDICATOR
            + self.FILE_TYPE
            + license_data.jurisdiction_iin
            + self.VERSION_NUMBER
            + self.JURISDICTION_VERSION
        )

    def _format_dl_subfile(self, dl_subfile: LicenseSubfile) -> str:
        """Format DL subfile data.

        Args:
            dl_subfile: DL subfile data

        Returns:
            Formatted DL subfile string with all fields

        Field order matters: DAQ (license number) comes first per convention.
        """
        fields: dict[str, str] = {}

        # Person data
        fields["DCS"] = dl_subfile.person.last_name
        fields["DAC"] = dl_subfile.person.first_name
        fields["DAD"] = dl_subfile.person.middle_name
        fields["DBB"] = self.format_date(dl_subfile.person.date_of_birth)
        fields["DBC"] = dl_subfile.person.sex.value

        # Physical attributes
        fields["DAY"] = dl_subfile.physical.eye_color.value
        fields["DAU"] = f"{dl_subfile.physical.height_inches:03d}"  # Zero-padded
        fields["DAW"] = f"{dl_subfile.physical.weight_pounds:03d}"  # Zero-padded
        fields["DAZ"] = dl_subfile.physical.hair_color.value
        fields["DCL"] = dl_subfile.physical.race.value

        # Address
        fields["DAG"] = dl_subfile.address.street
        fields["DAI"] = dl_subfile.address.city
        fields["DAJ"] = dl_subfile.address.state
        fields["DAK"] = dl_subfile.address.postal_code

        # License info
        fields["DCA"] = dl_subfile.vehicle_class
        fields["DCB"] = dl_subfile.restrictions
        fields["DCD"] = dl_subfile.endorsements
        fields["DBA"] = self.format_date(dl_subfile.expiration_date)
        fields["DBD"] = self.format_date(dl_subfile.issue_date)
        fields["DCF"] = dl_subfile.document_discriminator
        fields["DCG"] = dl_subfile.country_code

        # Truncation fields
        fields["DDE"] = dl_subfile.person.last_name_truncated.value
        fields["DDF"] = dl_subfile.person.first_name_truncated.value
        fields["DDG"] = dl_subfile.person.middle_name_truncated.value

        # Compliance fields
        fields["DDA"] = dl_subfile.compliance_type.value
        fields["DDB"] = self.format_date(dl_subfile.issue_date)  # Card revision date
        fields["DDC"] = self.format_date(dl_subfile.expiration_date)  # HazMat expiry
        fields["DDD"] = "1" if dl_subfile.limited_duration else "0"

        # Organ donor and veteran status
        fields["DDK"] = "1" if dl_subfile.organ_donor else "0"
        fields["DDL"] = "1" if dl_subfile.veteran else "0"

        # Build subfile string
        # DAQ comes first by convention
        subfile = f"DLDAQ{dl_subfile.license_number}\n"

        # Add all other fields
        for field_code, field_value in sorted(fields.items()):
            if field_value:  # Only include non-empty fields
                subfile += f"{field_code}{field_value}\n"

        # Terminate with carriage return
        subfile += "\r"

        return subfile

    def _format_state_subfile(self, state_subfile: StateSubfile) -> str:
        """Format state-specific subfile data.

        Args:
            state_subfile: State subfile data

        Returns:
            Formatted state subfile string
        """
        # Start with subfile type designator
        subfile = state_subfile.subfile_type

        # Add all custom fields in sorted order
        for field_code, field_value in sorted(state_subfile.custom_fields.items()):
            if field_value:  # Only include non-empty fields
                subfile += f"{field_code}{field_value}\n"

        # Terminate with carriage return
        subfile += "\r"

        return subfile

    def validate_barcode_string(self, barcode: str) -> bool:
        """Validate that a barcode string is properly formatted.

        Args:
            barcode: Barcode string to validate

        Returns:
            True if valid, False otherwise
        """
        # Check minimum length
        if len(barcode) < 50:
            return False

        # Check compliance indicator
        if not barcode.startswith(self.COMPLIANCE_INDICATOR):
            return False

        # Check file type
        if self.FILE_TYPE not in barcode[:20]:
            return False

        # Check for required markers
        if "\r" not in barcode:
            return False

        # Check that barcode is ASCII-encodable
        try:
            barcode.encode("ascii")
        except UnicodeEncodeError:
            return False

        return True


class CompactBarcodeFormatter(AAMVABarcodeFormatter):
    """Compact formatter that omits optional fields.

    This formatter creates smaller barcodes by excluding optional
    fields while maintaining AAMVA compliance.
    """

    def _format_dl_subfile(self, dl_subfile: LicenseSubfile) -> str:
        """Format DL subfile with only required fields.

        Args:
            dl_subfile: DL subfile data

        Returns:
            Formatted DL subfile string with minimal fields
        """
        # Only include mandatory fields per AAMVA standard
        mandatory_fields: dict[str, str] = {
            "DAQ": dl_subfile.license_number,
            "DCS": dl_subfile.person.last_name,
            "DAC": dl_subfile.person.first_name,
            "DBB": self.format_date(dl_subfile.person.date_of_birth),
            "DBA": self.format_date(dl_subfile.expiration_date),
            "DBC": dl_subfile.person.sex.value,
            "DAY": dl_subfile.physical.eye_color.value,
            "DAU": f"{dl_subfile.physical.height_inches:03d}",
            "DAG": dl_subfile.address.street,
            "DAI": dl_subfile.address.city,
            "DAJ": dl_subfile.address.state,
            "DAK": dl_subfile.address.postal_code,
        }

        # Build subfile string
        subfile = "DL"
        for field_code, field_value in sorted(mandatory_fields.items()):
            subfile += f"{field_code}{field_value}\n"

        subfile += "\r"
        return subfile


class VerboseBarcodeFormatter(AAMVABarcodeFormatter):
    """Verbose formatter that includes all possible fields.

    This formatter creates larger barcodes by including all available
    data fields, useful for testing and maximum information storage.
    """

    def _format_dl_subfile(self, dl_subfile: LicenseSubfile) -> str:
        """Format DL subfile with all possible fields.

        Args:
            dl_subfile: DL subfile data

        Returns:
            Formatted DL subfile string with all fields
        """
        # Use parent implementation which includes all fields
        return super()._format_dl_subfile(dl_subfile)


def create_barcode_formatter(
    formatter_type: str = "standard",
) -> BarcodeFormatterProtocol:
    """Factory function for creating barcode formatters.

    Args:
        formatter_type: Type of formatter ('standard', 'compact', or 'verbose')

    Returns:
        Appropriate barcode formatter instance

    Raises:
        ValueError: If formatter_type is invalid
    """
    formatters = {
        "standard": AAMVABarcodeFormatter,
        "compact": CompactBarcodeFormatter,
        "verbose": VerboseBarcodeFormatter,
    }

    formatter_class = formatters.get(formatter_type.lower())
    if formatter_class is None:
        raise ValueError(
            f"Unknown formatter type: {formatter_type}. "
            f"Valid types: {', '.join(formatters.keys())}"
        )

    return formatter_class()
