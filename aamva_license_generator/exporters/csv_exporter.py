"""
CSV Export for License Data

Exports license data in CSV format with:
- Configurable columns
- Header row
- Proper escaping
- Streaming for large datasets
"""

import csv
from pathlib import Path
from typing import List, Dict, Any, Optional, Set

from .base import (
    StreamingExporter, ExportFormat, ExportOptions, ExportResult,
    ValidationError
)
from ..storage import SafeFileOperations


class CSVExporter(StreamingExporter):
    """
    Export license data to CSV format

    Flattens nested license data structure into CSV rows.
    Handles multiple subfiles by prefixing column names.
    """

    def __init__(self, options: 'CSVExportOptions'):
        super().__init__(options)
        self._file_handle = None
        self._csv_writer = None
        self._columns: Optional[List[str]] = None

    @property
    def format(self) -> ExportFormat:
        return ExportFormat.CSV

    @property
    def file_extension(self) -> str:
        return "csv"

    def validate_data(self, data: Any) -> None:
        """
        Validate data for CSV export

        Args:
            data: License data to validate

        Raises:
            ValidationError: If data structure is invalid
        """
        if not isinstance(data, list):
            raise ValidationError("Data must be a list")

        if len(data) == 0:
            raise ValidationError("No data to export")

        # Validate first item structure
        first_item = data[0]
        if not isinstance(first_item, list):
            raise ValidationError("Each item must be a list of subfiles")

    def _begin_stream(self) -> None:
        """Initialize CSV file and write header"""
        output_path = Path(self.options.output_path)

        # Open file
        self._file_handle = open(output_path, 'w', newline='', encoding='utf-8')
        self._csv_writer = csv.writer(self._file_handle)

        # Determine columns if not specified
        if isinstance(self.options, CSVExportOptions):
            self._columns = self.options.columns
        else:
            self._columns = None

        # Header will be written after seeing first item
        # (so we can auto-detect columns if needed)

    def _write_item(self, item: List[Dict[str, Any]]) -> None:
        """
        Write a single license record to CSV

        Args:
            item: License data (list of subfiles)
        """
        if not self._csv_writer:
            raise RuntimeError("Stream not initialized")

        # Flatten subfiles into single row
        row_data = self._flatten_license_data(item)

        # Auto-detect columns from first row if needed
        if self._columns is None:
            self._columns = sorted(row_data.keys())
            # Write header
            self._csv_writer.writerow(self._columns)

        # Write data row
        row = [row_data.get(col, "") for col in self._columns]
        self._csv_writer.writerow(row)

    def _end_stream(self) -> None:
        """Close CSV file"""
        if self._file_handle:
            self._file_handle.close()
            self._file_handle = None
            self._csv_writer = None

    def _flatten_license_data(self, license_data: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Flatten nested license data into single dictionary

        Args:
            license_data: List of subfiles

        Returns:
            Flattened dictionary with prefixed keys
        """
        flattened = {}

        for subfile_index, subfile in enumerate(license_data):
            subfile_type = subfile.get("subfile_type", f"subfile_{subfile_index}")

            for key, value in subfile.items():
                if key == "subfile_type":
                    continue

                # Create prefixed column name
                column_name = f"{subfile_type}_{key}"

                # Convert value to string
                flattened[column_name] = str(value)

        return flattened


class CSVExportOptions(ExportOptions):
    """Extended options for CSV export"""

    def __init__(self, output_path: str, **kwargs):
        super().__init__(output_path, **kwargs)
        self.columns: Optional[List[str]] = None  # Auto-detect if None
        self.include_header: bool = True
        self.delimiter: str = ","
        self.quoting: int = csv.QUOTE_MINIMAL
        self.line_terminator: str = "\n"
