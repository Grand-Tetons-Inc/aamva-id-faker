"""
JSON Import for License Data

Imports license data from JSON files with:
- Schema validation
- Error recovery
- Support for both array and JSON Lines format
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional

from .base import (
    StreamingImporter, ImportFormat, ImportOptions, ImportResult,
    ParseError, SchemaError
)
from ..storage import FileSystemValidator, SafeFileOperations


class JSONImporter(StreamingImporter):
    """
    Import license data from JSON file

    Supports two formats:
    1. Standard JSON array: [item1, item2, ...]
    2. Object with metadata: {"metadata": {...}, "licenses": [...]}
    """

    def __init__(self, options: ImportOptions):
        super().__init__(options)
        self._file_handle = None
        self._data_iterator = None
        self._is_object_format = False

    @property
    def format(self) -> ImportFormat:
        return ImportFormat.JSON

    @property
    def supported_extensions(self) -> List[str]:
        return ["json"]

    def validate_file(self, filepath: Path) -> None:
        """
        Validate JSON file

        Args:
            filepath: File to validate

        Raises:
            ParseError: If file is not valid JSON
        """
        # Check readable
        if not FileSystemValidator.check_readable(filepath):
            raise ParseError(f"Cannot read file: {filepath}")

        # Try to parse JSON
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                # Read first character to determine format
                first_char = f.read(1)
                if first_char not in ['{', '[']:
                    raise ParseError(f"File does not appear to be JSON: {filepath}")
        except UnicodeDecodeError as e:
            raise ParseError(f"File encoding error: {e}")
        except Exception as e:
            raise ParseError(f"Failed to read file: {e}")

    def _open_stream(self) -> None:
        """Open JSON file and prepare for reading"""
        filepath = Path(self.options.input_path)

        try:
            self._file_handle = open(filepath, 'r', encoding='utf-8')

            # Load entire JSON (for small-medium files)
            # For very large files, would use ijson for streaming
            data = json.load(self._file_handle)

            # Determine format
            if isinstance(data, dict) and "licenses" in data:
                # Object format with metadata
                self._is_object_format = True
                items = data.get("licenses", [])
            elif isinstance(data, list):
                # Array format
                items = data
            else:
                raise ParseError("JSON must be array or object with 'licenses' key")

            # Create iterator
            self._data_iterator = iter(items)

        except json.JSONDecodeError as e:
            raise ParseError(f"Invalid JSON: {e}")
        except Exception as e:
            raise ParseError(f"Failed to open JSON: {e}")

    def _read_item(self) -> Optional[Any]:
        """Read next item from JSON data"""
        if self._data_iterator is None:
            return None

        try:
            return next(self._data_iterator)
        except StopIteration:
            return None

    def _close_stream(self) -> None:
        """Close JSON file"""
        if self._file_handle:
            try:
                self._file_handle.close()
            except Exception:
                pass
            self._file_handle = None

        self._data_iterator = None

    def validate_item_schema(self, item: Any) -> Optional[str]:
        """
        Validate license item schema

        Args:
            item: Item to validate

        Returns:
            Error message if invalid, None if valid
        """
        # Item should be a list of subfiles
        if not isinstance(item, list):
            return "Item must be a list of subfiles"

        if len(item) == 0:
            return "Item must contain at least one subfile"

        # Validate first subfile (DL data)
        dl_data = item[0]
        if not isinstance(dl_data, dict):
            return "First subfile must be a dictionary"

        # Check required fields
        required_fields = ['DAQ', 'DCS', 'DAC', 'DBB', 'DBA', 'DAJ']
        missing_fields = [f for f in required_fields if f not in dl_data]

        if missing_fields:
            return f"Missing required fields: {', '.join(missing_fields)}"

        return None


class JSONLinesImporter(StreamingImporter):
    """
    Import license data from JSON Lines file (.jsonl)

    Each line is a separate JSON object.
    Efficient for very large datasets.
    """

    def __init__(self, options: ImportOptions):
        super().__init__(options)
        self._file_handle = None

    @property
    def format(self) -> ImportFormat:
        return ImportFormat.JSON

    @property
    def supported_extensions(self) -> List[str]:
        return ["jsonl", "ndjson"]

    def validate_file(self, filepath: Path) -> None:
        """Validate JSON Lines file"""
        if not FileSystemValidator.check_readable(filepath):
            raise ParseError(f"Cannot read file: {filepath}")

        # Try to parse first line
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                if first_line:
                    json.loads(first_line)
        except json.JSONDecodeError as e:
            raise ParseError(f"First line is not valid JSON: {e}")
        except Exception as e:
            raise ParseError(f"Failed to read file: {e}")

    def _open_stream(self) -> None:
        """Open JSON Lines file"""
        filepath = Path(self.options.input_path)
        self._file_handle = open(filepath, 'r', encoding='utf-8')

    def _read_item(self) -> Optional[Any]:
        """Read next line from file"""
        if not self._file_handle:
            return None

        while True:
            line = self._file_handle.readline()
            if not line:
                return None  # End of file

            line = line.strip()
            if not line:
                continue  # Skip empty lines

            try:
                return json.loads(line)
            except json.JSONDecodeError as e:
                raise ParseError(f"Invalid JSON line: {e}")

    def _close_stream(self) -> None:
        """Close file"""
        if self._file_handle:
            try:
                self._file_handle.close()
            except Exception:
                pass
            self._file_handle = None

    def validate_item_schema(self, item: Any) -> Optional[str]:
        """Validate item schema (same as JSONImporter)"""
        if not isinstance(item, list):
            return "Item must be a list of subfiles"

        if len(item) == 0:
            return "Item must contain at least one subfile"

        dl_data = item[0]
        if not isinstance(dl_data, dict):
            return "First subfile must be a dictionary"

        required_fields = ['DAQ', 'DCS', 'DAC', 'DBB', 'DBA', 'DAJ']
        missing_fields = [f for f in required_fields if f not in dl_data]

        if missing_fields:
            return f"Missing required fields: {', '.join(missing_fields)}"

        return None


class JSONImportOptions(ImportOptions):
    """Extended options for JSON import"""

    def __init__(self, input_path: str, **kwargs):
        super().__init__(input_path, **kwargs)
        self.extract_metadata: bool = True  # Extract metadata if present
        self.metadata: Dict[str, Any] = {}  # Will be populated during import
