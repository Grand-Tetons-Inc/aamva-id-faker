"""
CSV Import for License Data

Imports license data from CSV files with:
- Header detection
- Type inference
- Subfile reconstruction
- Error recovery
"""

import csv
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from collections import defaultdict

from .base import (
    StreamingImporter, ImportFormat, ImportOptions, ImportResult,
    ParseError, SchemaError
)
from ..storage import FileSystemValidator


class CSVImporter(StreamingImporter):
    """
    Import license data from CSV file

    Reconstructs nested license structure from flattened CSV rows.
    Columns are expected to be in format: SUBFILE_FIELD (e.g., DL_DAQ, ZC_ZCW)
    """

    def __init__(self, options: 'CSVImportOptions'):
        super().__init__(options)
        self._file_handle = None
        self._csv_reader = None
        self._headers: Optional[List[str]] = None

    @property
    def format(self) -> ImportFormat:
        return ImportFormat.CSV

    @property
    def supported_extensions(self) -> List[str]:
        return ["csv", "tsv"]

    def validate_file(self, filepath: Path) -> None:
        """
        Validate CSV file

        Args:
            filepath: File to validate

        Raises:
            ParseError: If file is invalid
        """
        if not FileSystemValidator.check_readable(filepath):
            raise ParseError(f"Cannot read file: {filepath}")

        # Try to read first few rows
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader, None)

                if not header:
                    raise ParseError("CSV file is empty")

                # Check for reasonable number of columns
                if len(header) < 5:
                    raise ParseError("CSV file has too few columns (expected license data)")

        except UnicodeDecodeError as e:
            raise ParseError(f"File encoding error: {e}")
        except Exception as e:
            raise ParseError(f"Failed to read CSV: {e}")

    def _open_stream(self) -> None:
        """Open CSV file for reading"""
        filepath = Path(self.options.input_path)

        # Determine delimiter
        delimiter = ','
        if isinstance(self.options, CSVImportOptions):
            delimiter = self.options.delimiter
        elif filepath.suffix.lower() == '.tsv':
            delimiter = '\t'

        try:
            self._file_handle = open(filepath, 'r', encoding='utf-8', newline='')
            self._csv_reader = csv.reader(self._file_handle, delimiter=delimiter)

            # Read header
            self._headers = next(self._csv_reader)

            # Validate header format
            if not self._validate_headers():
                if isinstance(self.options, CSVImportOptions) and self.options.auto_detect_format:
                    # Try to auto-detect column format
                    self._headers = self._normalize_headers(self._headers)
                else:
                    raise ParseError(
                        "CSV headers don't match expected format. "
                        "Expected format: SUBFILE_FIELD (e.g., DL_DAQ)"
                    )

        except StopIteration:
            raise ParseError("CSV file has no data rows")
        except Exception as e:
            raise ParseError(f"Failed to open CSV: {e}")

    def _read_item(self) -> Optional[Any]:
        """Read next row from CSV and reconstruct license structure"""
        if not self._csv_reader or not self._headers:
            return None

        try:
            row = next(self._csv_reader)

            # Convert row to dictionary
            row_dict = dict(zip(self._headers, row))

            # Reconstruct license structure
            license_data = self._reconstruct_license(row_dict)

            return license_data

        except StopIteration:
            return None
        except Exception as e:
            raise ParseError(f"Failed to parse CSV row: {e}")

    def _close_stream(self) -> None:
        """Close CSV file"""
        if self._file_handle:
            try:
                self._file_handle.close()
            except Exception:
                pass
            self._file_handle = None

        self._csv_reader = None
        self._headers = None

    def _validate_headers(self) -> bool:
        """
        Check if headers follow expected format

        Returns:
            True if headers are valid
        """
        if not self._headers:
            return False

        # Check if headers contain underscore (SUBFILE_FIELD format)
        has_underscore = any('_' in h for h in self._headers)
        return has_underscore

    def _normalize_headers(self, headers: List[str]) -> List[str]:
        """
        Normalize headers to SUBFILE_FIELD format

        Args:
            headers: Original headers

        Returns:
            Normalized headers
        """
        normalized = []

        for header in headers:
            # If already in correct format, keep as-is
            if '_' in header:
                normalized.append(header)
            else:
                # Assume DL subfile for standard AAMVA fields
                if header.startswith('D') and len(header) == 3:
                    normalized.append(f"DL_{header}")
                else:
                    # Keep as-is and hope for the best
                    normalized.append(header)

        return normalized

    def _reconstruct_license(self, row_dict: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Reconstruct nested license structure from flat CSV row

        Args:
            row_dict: Dictionary of column_name -> value

        Returns:
            List of subfiles
        """
        # Group fields by subfile
        subfiles: Dict[str, Dict[str, str]] = defaultdict(dict)

        for column, value in row_dict.items():
            # Skip empty values
            if not value or value.strip() == '':
                continue

            # Parse column name
            if '_' in column:
                subfile_type, field_name = column.split('_', 1)
            else:
                # Default to DL subfile
                subfile_type = 'DL'
                field_name = column

            subfiles[subfile_type][field_name] = value

        # Convert to list of subfiles
        result = []

        # Ensure DL subfile comes first
        if 'DL' in subfiles:
            dl_data = subfiles.pop('DL')
            dl_data['subfile_type'] = 'DL'
            result.append(dl_data)

        # Add other subfiles
        for subfile_type, fields in sorted(subfiles.items()):
            fields['subfile_type'] = subfile_type
            result.append(fields)

        return result

    def validate_item_schema(self, item: Any) -> Optional[str]:
        """
        Validate reconstructed license item

        Args:
            item: License data (list of subfiles)

        Returns:
            Error message if invalid, None if valid
        """
        if not isinstance(item, list):
            return "Item must be a list of subfiles"

        if len(item) == 0:
            return "Item must contain at least one subfile"

        # Validate DL subfile
        dl_data = item[0]
        if not isinstance(dl_data, dict):
            return "First subfile must be a dictionary"

        # Check required fields
        required_fields = ['DAQ', 'DCS', 'DAC']
        missing_fields = [f for f in required_fields if f not in dl_data]

        if missing_fields:
            return f"Missing required DL fields: {', '.join(missing_fields)}"

        return None


class CSVImportOptions(ImportOptions):
    """Extended options for CSV import"""

    def __init__(self, input_path: str, **kwargs):
        super().__init__(input_path, **kwargs)
        self.delimiter: str = ","
        self.has_header: bool = True
        self.auto_detect_format: bool = True  # Auto-detect column format
        self.column_mapping: Optional[Dict[str, str]] = None  # Custom column mapping
