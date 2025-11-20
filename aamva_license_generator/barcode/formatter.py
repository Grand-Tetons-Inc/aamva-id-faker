"""
AAMVA Barcode Formatting Module.

This module provides utilities for formatting AAMVA barcode data,
including pretty-printing, debugging output, and human-readable representations.

This separates formatting concerns from encoding logic, providing better
maintainability and testability.

Author: New implementation
License: MIT
"""

from typing import List, Dict, Optional, Any
from io import StringIO

from .aamva_spec import (
    AAMVAVersion,
    get_field_definition,
    get_state_by_iin,
    FIELD_SEPARATOR,
    SEGMENT_TERMINATOR,
)
from .subfiles import Subfile


class BarcodeFormatter:
    """Utility class for formatting AAMVA barcode data for display."""

    @staticmethod
    def format_subfile(subfile: Subfile, include_descriptions: bool = True) -> str:
        """Format a subfile for human-readable display.

        Args:
            subfile: Subfile to format
            include_descriptions: If True, include field descriptions

        Returns:
            Formatted string
        """
        lines = []
        lines.append(f"{'='*60}")
        lines.append(f"Subfile Type: {subfile.subfile_type}")
        if subfile.jurisdiction:
            lines.append(f"Jurisdiction: {subfile.jurisdiction}")
        lines.append(f"Fields: {len(subfile.fields)}")
        lines.append(f"{'='*60}")

        # Format each field
        for code in sorted(subfile.fields.keys()):
            value = subfile.fields[code]
            field_def = get_field_definition(code)

            if include_descriptions and field_def:
                lines.append(f"{code}: {value}")
                lines.append(f"     ({field_def.name})")
            else:
                name = field_def.name if field_def else "Unknown"
                lines.append(f"{code} ({name}): {value}")

        return "\n".join(lines)

    @staticmethod
    def format_barcode_data(
        subfiles: List[Subfile],
        iin: Optional[str] = None,
        version: AAMVAVersion = AAMVAVersion.VERSION_10
    ) -> str:
        """Format complete barcode data for display.

        Args:
            subfiles: List of subfiles
            iin: Optional IIN to display
            version: AAMVA version

        Returns:
            Formatted string
        """
        lines = []
        lines.append("="*60)
        lines.append("AAMVA DL/ID BARCODE DATA")
        lines.append("="*60)

        # Header info
        if iin:
            juris_info = get_state_by_iin(iin)
            if juris_info:
                lines.append(f"Jurisdiction: {juris_info['jurisdiction']} ({juris_info['abbr']})")
            lines.append(f"IIN: {iin}")

        lines.append(f"AAMVA Version: {version.value}")
        lines.append(f"Number of Subfiles: {len(subfiles)}")
        lines.append("")

        # Format each subfile
        for i, subfile in enumerate(subfiles):
            lines.append(BarcodeFormatter.format_subfile(subfile, include_descriptions=False))
            if i < len(subfiles) - 1:
                lines.append("")

        return "\n".join(lines)

    @staticmethod
    def format_raw_barcode(barcode_str: str, show_invisible: bool = True) -> str:
        """Format raw barcode string showing control characters.

        Args:
            barcode_str: Raw barcode string
            show_invisible: If True, show invisible characters

        Returns:
            Formatted string with control characters visible
        """
        if not show_invisible:
            return barcode_str

        # Replace control characters with visible representations
        output = barcode_str
        output = output.replace('\n', '<LF>\n')
        output = output.replace('\r', '<CR>')
        output = output.replace('\x1E', '<RS>')
        output = output.replace('@', '@<COMPLIANCE>')

        return output

    @staticmethod
    def format_hex_dump(barcode_str: str, bytes_per_line: int = 16) -> str:
        """Format barcode as hex dump for debugging.

        Args:
            barcode_str: Barcode string
            bytes_per_line: Number of bytes to show per line

        Returns:
            Hex dump string
        """
        lines = []
        barcode_bytes = barcode_str.encode('ascii')

        for i in range(0, len(barcode_bytes), bytes_per_line):
            chunk = barcode_bytes[i:i+bytes_per_line]

            # Hex representation
            hex_str = ' '.join(f'{b:02X}' for b in chunk)

            # ASCII representation
            ascii_str = ''.join(
                chr(b) if 32 <= b < 127 else '.'
                for b in chunk
            )

            # Format line
            lines.append(f"{i:04X}  {hex_str:<{bytes_per_line*3}}  {ascii_str}")

        return '\n'.join(lines)

    @staticmethod
    def format_compact(subfile: Subfile) -> str:
        """Format subfile in compact single-line format.

        Args:
            subfile: Subfile to format

        Returns:
            Compact formatted string
        """
        field_strs = [f"{k}={v}" for k, v in sorted(subfile.fields.items())]
        return f"{subfile.subfile_type}[{', '.join(field_strs)}]"

    @staticmethod
    def format_json(subfiles: List[Subfile], indent: int = 2) -> str:
        """Format subfiles as JSON.

        Args:
            subfiles: List of subfiles
            indent: JSON indentation level

        Returns:
            JSON string
        """
        import json

        data = {
            'subfiles': [subfile.to_dict() for subfile in subfiles]
        }

        return json.dumps(data, indent=indent)

    @staticmethod
    def format_table(subfile: Subfile, max_value_width: int = 40) -> str:
        """Format subfile as ASCII table.

        Args:
            subfile: Subfile to format
            max_value_width: Maximum width for value column

        Returns:
            ASCII table string
        """
        lines = []

        # Table header
        lines.append(f"Subfile: {subfile.subfile_type}")
        lines.append("-" * 80)
        lines.append(f"{'Code':<6} {'Name':<30} {'Value':<40}")
        lines.append("-" * 80)

        # Table rows
        for code in sorted(subfile.fields.keys()):
            value = subfile.fields[code]
            field_def = get_field_definition(code)
            name = field_def.name if field_def else "Unknown"

            # Truncate value if too long
            if len(value) > max_value_width:
                display_value = value[:max_value_width-3] + "..."
            else:
                display_value = value

            lines.append(f"{code:<6} {name:<30} {display_value:<40}")

        lines.append("-" * 80)

        return "\n".join(lines)


def format_license_summary(dl_fields: Dict[str, str]) -> str:
    """Format DL fields as human-readable license summary.

    Args:
        dl_fields: Dictionary of DL field codes and values

    Returns:
        Formatted license summary

    Example output:
        License Number: D1234567
        Name: SMITH, JOHN MICHAEL
        DOB: 01/01/1990 (Age: 33)
        Address: 123 MAIN ST, ANYTOWN, CA 12345
        ...
    """
    lines = []

    # License number
    if 'DAQ' in dl_fields:
        lines.append(f"License Number: {dl_fields['DAQ']}")

    # Name
    name_parts = []
    if 'DCS' in dl_fields:
        name_parts.append(dl_fields['DCS'])
    if 'DAC' in dl_fields:
        first = dl_fields['DAC']
        if 'DAD' in dl_fields and dl_fields['DAD']:
            first += f" {dl_fields['DAD']}"
        name_parts.insert(0, first)

    if name_parts:
        lines.append(f"Name: {', '.join(name_parts)}")

    # DOB and age
    if 'DBB' in dl_fields:
        dob_str = dl_fields['DBB']
        # Format as MM/DD/YYYY
        if len(dob_str) == 8:
            formatted_dob = f"{dob_str[0:2]}/{dob_str[2:4]}/{dob_str[4:8]}"

            # Calculate age
            from datetime import datetime
            try:
                dob = datetime.strptime(dob_str, "%m%d%Y")
                age = (datetime.now() - dob).days // 365
                lines.append(f"DOB: {formatted_dob} (Age: {age})")
            except ValueError:
                lines.append(f"DOB: {formatted_dob}")
        else:
            lines.append(f"DOB: {dob_str}")

    # Address
    addr_parts = []
    if 'DAG' in dl_fields:
        addr_parts.append(dl_fields['DAG'])
    if 'DAI' in dl_fields and 'DAJ' in dl_fields:
        city_state = f"{dl_fields['DAI']}, {dl_fields['DAJ']}"
        if 'DAK' in dl_fields:
            city_state += f" {dl_fields['DAK']}"
        addr_parts.append(city_state)

    if addr_parts:
        lines.append(f"Address: {', '.join(addr_parts)}")

    # Physical description
    phys_parts = []
    if 'DBC' in dl_fields:
        sex = "Male" if dl_fields['DBC'] == "1" else "Female" if dl_fields['DBC'] == "2" else "Unspecified"
        phys_parts.append(sex)

    if 'DAY' in dl_fields:
        phys_parts.append(f"Eyes: {dl_fields['DAY']}")

    if 'DAZ' in dl_fields:
        phys_parts.append(f"Hair: {dl_fields['DAZ']}")

    if 'DAU' in dl_fields:
        height = dl_fields['DAU']
        # Convert to feet/inches if needed
        if height.isdigit() and len(height) <= 3:
            inches = int(height)
            feet = inches // 12
            remaining_inches = inches % 12
            height = f"{feet}'{remaining_inches}\""
        phys_parts.append(f"Height: {height}")

    if 'DAW' in dl_fields:
        phys_parts.append(f"Weight: {dl_fields['DAW']} lbs")

    if phys_parts:
        lines.append(f"Physical: {', '.join(phys_parts)}")

    # Dates
    if 'DBD' in dl_fields:
        issue_str = dl_fields['DBD']
        if len(issue_str) == 8:
            formatted = f"{issue_str[0:2]}/{issue_str[2:4]}/{issue_str[4:8]}"
            lines.append(f"Issue Date: {formatted}")

    if 'DBA' in dl_fields:
        exp_str = dl_fields['DBA']
        if len(exp_str) == 8:
            formatted = f"{exp_str[0:2]}/{exp_str[2:4]}/{exp_str[4:8]}"
            lines.append(f"Expiration: {formatted}")

    # Class and endorsements
    if 'DCA' in dl_fields:
        lines.append(f"Class: {dl_fields['DCA']}")

    if 'DCD' in dl_fields and dl_fields['DCD']:
        lines.append(f"Endorsements: {dl_fields['DCD']}")

    if 'DCB' in dl_fields and dl_fields['DCB']:
        lines.append(f"Restrictions: {dl_fields['DCB']}")

    # Additional info
    if 'DDK' in dl_fields:
        organ_donor = "Yes" if dl_fields['DDK'] == "1" else "No"
        lines.append(f"Organ Donor: {organ_donor}")

    if 'DDL' in dl_fields:
        veteran = "Yes" if dl_fields['DDL'] == "1" else "No"
        lines.append(f"Veteran: {veteran}")

    return "\n".join(lines)
