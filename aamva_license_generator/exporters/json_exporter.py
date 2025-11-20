"""
JSON Export for License Data

Exports license data in structured JSON format with:
- Pretty printing
- Validation
- Streaming for large datasets
- Metadata inclusion
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from .base import (
    StreamingExporter, ExportFormat, ExportOptions, ExportResult,
    ValidationError
)
from ..storage import SafeFileOperations, StorageError


class JSONExporter(StreamingExporter):
    """
    Export license data to JSON format

    Supports both compact and pretty-printed output.
    Can include metadata and validation information.
    """

    def __init__(self, options: 'JSONExportOptions'):
        super().__init__(options)
        self._file_handle = None
        self._first_item = True

    @property
    def format(self) -> ExportFormat:
        return ExportFormat.JSON

    @property
    def file_extension(self) -> str:
        return "json"

    def validate_data(self, data: Any) -> None:
        """
        Validate data for JSON export

        Args:
            data: Data to validate

        Raises:
            ValidationError: If data is not JSON-serializable
        """
        if not isinstance(data, list):
            raise ValidationError("Data must be a list")

        # Test JSON serialization
        try:
            json.dumps(data[0] if len(data) > 0 else [])
        except (TypeError, ValueError) as e:
            raise ValidationError(f"Data is not JSON-serializable: {e}")

    def _begin_stream(self) -> None:
        """Initialize JSON file and write opening bracket"""
        output_path = Path(self.options.output_path)

        # Open file for writing
        self._file_handle = open(output_path, 'w', encoding='utf-8')
        self._first_item = True

        # Write opening structure
        if isinstance(self.options, JSONExportOptions) and self.options.include_metadata:
            metadata = self._add_metadata({
                "export_date": datetime.now().isoformat(),
                "record_count": 0,  # Will be updated later
            })

            self._file_handle.write("{\n")
            self._file_handle.write(f'  "metadata": {json.dumps(metadata, indent=2)},\n')
            self._file_handle.write('  "licenses": [\n')
        else:
            self._file_handle.write("[\n")

    def _write_item(self, item: Any) -> None:
        """
        Write a single item to JSON stream

        Args:
            item: Item to write
        """
        if not self._file_handle:
            raise RuntimeError("Stream not initialized")

        # Add comma if not first item
        if not self._first_item:
            self._file_handle.write(",\n")
        else:
            self._first_item = False

        # Write item
        indent = 4 if isinstance(self.options, JSONExportOptions) and self.options.pretty_print else None
        item_json = json.dumps(item, indent=indent)

        # Indent the item if pretty printing
        if indent:
            indented = "\n".join(f"    {line}" for line in item_json.split("\n"))
            self._file_handle.write(indented)
        else:
            self._file_handle.write(item_json)

    def _end_stream(self) -> None:
        """Close JSON structure and file"""
        if not self._file_handle:
            return

        # Write closing bracket
        self._file_handle.write("\n")

        if isinstance(self.options, JSONExportOptions) and self.options.include_metadata:
            self._file_handle.write("  ]\n")
            self._file_handle.write("}\n")
        else:
            self._file_handle.write("]\n")

        # Close file
        self._file_handle.close()
        self._file_handle = None


class CompactJSONExporter(StreamingExporter):
    """
    Export license data to compact JSON (one record per line)

    Useful for large datasets that will be processed line-by-line.
    """

    def __init__(self, options: ExportOptions):
        super().__init__(options)
        self._file_handle = None

    @property
    def format(self) -> ExportFormat:
        return ExportFormat.JSON

    @property
    def file_extension(self) -> str:
        return "jsonl"  # JSON Lines format

    def validate_data(self, data: Any) -> None:
        """Validate data for JSON export"""
        if not isinstance(data, list):
            raise ValidationError("Data must be a list")

        # Test serialization
        try:
            json.dumps(data[0] if len(data) > 0 else [])
        except (TypeError, ValueError) as e:
            raise ValidationError(f"Data is not JSON-serializable: {e}")

    def _begin_stream(self) -> None:
        """Open file for writing"""
        output_path = Path(self.options.output_path)
        self._file_handle = open(output_path, 'w', encoding='utf-8')

    def _write_item(self, item: Any) -> None:
        """Write item as single JSON line"""
        if not self._file_handle:
            raise RuntimeError("Stream not initialized")

        item_json = json.dumps(item)
        self._file_handle.write(item_json)
        self._file_handle.write("\n")

    def _end_stream(self) -> None:
        """Close file"""
        if self._file_handle:
            self._file_handle.close()
            self._file_handle = None


class JSONExportOptions(ExportOptions):
    """Extended options for JSON export"""

    def __init__(self, output_path: str, **kwargs):
        super().__init__(output_path, **kwargs)
        self.pretty_print: bool = True
        self.include_metadata: bool = True
        self.indent: int = 2
        self.sort_keys: bool = False
        self.ensure_ascii: bool = False
