"""
Import Service - License Data Import Orchestration

Handles importing license data from various formats:
- JSON files
- CSV files
- AAMVA text format
- Configuration files
"""

import os
import json
import csv
import re
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

# Configure logging
logger = logging.getLogger(__name__)


class ImportError(Exception):
    """Raised when import operation fails"""
    pass


class ImportResult:
    """
    Result of an import operation.

    Attributes:
        success: Whether import succeeded
        data: Imported license data
        count: Number of licenses imported
        errors: List of error messages
        warnings: List of warning messages
    """

    def __init__(self):
        self.success = True
        self.data: List[List[Dict[str, str]]] = []
        self.count = 0
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def add_license(self, license_data: List[Dict[str, str]]):
        """Add imported license data."""
        self.data.append(license_data)
        self.count += 1

    def add_error(self, message: str):
        """Add an error message."""
        self.success = False
        self.errors.append(message)

    def add_warning(self, message: str):
        """Add a warning message."""
        self.warnings.append(message)

    def __str__(self) -> str:
        """String representation."""
        if self.success:
            return f"✓ Import successful: {self.count} licenses"
        else:
            return f"✗ Import failed: {len(self.errors)} errors"

    def __bool__(self) -> bool:
        """Boolean representation."""
        return self.success


class ImportService:
    """
    Service for importing license data from various formats.

    Supports:
    - JSON files (structured license data)
    - CSV files (flattened DL data)
    - AAMVA text format (raw barcode data)
    - Configuration files (IIN mappings, state formats)
    """

    def __init__(self):
        """Initialize the ImportService."""
        pass

    def import_json(self, filepath: str) -> ImportResult:
        """
        Import licenses from JSON file.

        Args:
            filepath: Path to JSON file

        Returns:
            ImportResult object

        Expected JSON format:
        [
            [
                {"subfile_type": "DL", "DAQ": "...", ...},
                {"subfile_type": "ZC", ...}
            ],
            ...
        ]
        """
        result = ImportResult()

        try:
            if not os.path.exists(filepath):
                result.add_error(f"File not found: {filepath}")
                return result

            with open(filepath, 'r') as f:
                data = json.load(f)

            if not isinstance(data, list):
                result.add_error("JSON must contain an array of licenses")
                return result

            for i, license_data in enumerate(data):
                if not isinstance(license_data, list):
                    result.add_warning(f"License {i} is not an array, skipping")
                    continue

                if len(license_data) < 1:
                    result.add_warning(f"License {i} is empty, skipping")
                    continue

                # Validate basic structure
                dl_data = license_data[0]
                if not isinstance(dl_data, dict):
                    result.add_warning(f"License {i} DL data is not a dict, skipping")
                    continue

                result.add_license(license_data)

            logger.info(f"Imported {result.count} licenses from JSON: {filepath}")

        except json.JSONDecodeError as e:
            result.add_error(f"Invalid JSON: {e}")
        except Exception as e:
            result.add_error(f"Import failed: {e}")

        return result

    def import_csv(self, filepath: str) -> ImportResult:
        """
        Import licenses from CSV file.

        Args:
            filepath: Path to CSV file

        Returns:
            ImportResult object

        Expected CSV format:
        DAQ,DCS,DAC,DAD,DBB,DBA,...
        A1234567,DOE,JOHN,M,05151990,08142032,...
        """
        result = ImportResult()

        try:
            if not os.path.exists(filepath):
                result.add_error(f"File not found: {filepath}")
                return result

            with open(filepath, 'r') as f:
                reader = csv.DictReader(f)

                for i, row in enumerate(reader):
                    # Convert CSV row to DL subfile
                    dl_data = {"subfile_type": "DL"}
                    dl_data.update(row)

                    # Create license data (DL only, no state subfile from CSV)
                    license_data = [dl_data]
                    result.add_license(license_data)

            logger.info(f"Imported {result.count} licenses from CSV: {filepath}")

        except Exception as e:
            result.add_error(f"Import failed: {e}")

        return result

    def parse_aamva_barcode(self, barcode_data: str) -> ImportResult:
        """
        Parse AAMVA barcode text format.

        Args:
            barcode_data: Raw AAMVA barcode string

        Returns:
            ImportResult object with single license
        """
        result = ImportResult()

        try:
            # Check compliance markers
            if not barcode_data.startswith("@\n\x1E\r"):
                result.add_warning("Missing AAMVA compliance markers")

            # Find ANSI header
            if "ANSI " not in barcode_data:
                result.add_error("Invalid AAMVA format: missing ANSI header")
                return result

            # Parse subfiles
            subfiles = []

            # Find DL subfile
            dl_match = re.search(r'DL([^\r]+)\r', barcode_data)
            if dl_match:
                dl_fields_str = dl_match.group(1)
                dl_data = self._parse_subfile_fields(dl_fields_str)
                dl_data["subfile_type"] = "DL"
                subfiles.append(dl_data)
            else:
                result.add_error("No DL subfile found")
                return result

            # Find state subfiles (Z[A-Z])
            state_matches = re.finditer(r'(Z[A-Z])([^\r]+)\r', barcode_data)
            for match in state_matches:
                subfile_type = match.group(1)
                fields_str = match.group(2)
                state_data = self._parse_subfile_fields(fields_str)
                state_data["subfile_type"] = subfile_type
                subfiles.append(state_data)

            if subfiles:
                result.add_license(subfiles)
                logger.info("Parsed AAMVA barcode successfully")

        except Exception as e:
            result.add_error(f"Parse failed: {e}")

        return result

    def _parse_subfile_fields(self, fields_str: str) -> Dict[str, str]:
        """
        Parse AAMVA subfile fields from string.

        Args:
            fields_str: Field string (e.g., "DAQA1234567\nDCSDOE\n...")

        Returns:
            Dictionary of field codes to values
        """
        fields = {}
        lines = fields_str.split('\n')

        for line in lines:
            if len(line) >= 3:
                # Field code is first 3 characters
                field_code = line[:3]
                field_value = line[3:]
                fields[field_code] = field_value

        return fields

    def import_aamva_file(self, filepath: str) -> ImportResult:
        """
        Import license from AAMVA text file.

        Args:
            filepath: Path to text file containing AAMVA barcode data

        Returns:
            ImportResult object
        """
        result = ImportResult()

        try:
            if not os.path.exists(filepath):
                result.add_error(f"File not found: {filepath}")
                return result

            with open(filepath, 'r') as f:
                barcode_data = f.read()

            return self.parse_aamva_barcode(barcode_data)

        except Exception as e:
            result.add_error(f"Import failed: {e}")

        return result

    def import_config(self, filepath: str) -> Dict[str, Any]:
        """
        Import configuration from JSON file.

        Args:
            filepath: Path to config JSON file

        Returns:
            Configuration dictionary

        Raises:
            ImportError: If import fails

        Expected format:
        {
            "iin_jurisdictions": {...},
            "state_formats": {...},
            "validation_rules": {...}
        }
        """
        try:
            if not os.path.exists(filepath):
                raise ImportError(f"Config file not found: {filepath}")

            with open(filepath, 'r') as f:
                config = json.load(f)

            if not isinstance(config, dict):
                raise ImportError("Config must be a JSON object")

            logger.info(f"Loaded configuration from: {filepath}")
            return config

        except json.JSONDecodeError as e:
            raise ImportError(f"Invalid JSON in config: {e}") from e
        except Exception as e:
            raise ImportError(f"Failed to load config: {e}") from e

    def import_iin_mappings(self, filepath: str) -> Dict[str, Dict[str, str]]:
        """
        Import IIN jurisdiction mappings from CSV or JSON.

        Args:
            filepath: Path to IIN mappings file

        Returns:
            Dictionary mapping IIN codes to jurisdiction info

        Raises:
            ImportError: If import fails

        CSV format:
        IIN,jurisdiction,abbr,country
        636014,California,CA,USA

        JSON format:
        {
            "636014": {"jurisdiction": "California", "abbr": "CA", "country": "USA"},
            ...
        }
        """
        try:
            if not os.path.exists(filepath):
                raise ImportError(f"IIN mappings file not found: {filepath}")

            ext = Path(filepath).suffix.lower()

            if ext == '.json':
                with open(filepath, 'r') as f:
                    mappings = json.load(f)

                if not isinstance(mappings, dict):
                    raise ImportError("JSON IIN mappings must be an object")

                return mappings

            elif ext == '.csv':
                mappings = {}

                with open(filepath, 'r') as f:
                    reader = csv.DictReader(f)

                    for row in reader:
                        iin = row.get('IIN', '')
                        if not iin:
                            continue

                        mappings[iin] = {
                            'jurisdiction': row.get('jurisdiction', ''),
                            'abbr': row.get('abbr', ''),
                            'country': row.get('country', '')
                        }

                return mappings

            else:
                raise ImportError(f"Unsupported file format: {ext}")

        except Exception as e:
            raise ImportError(f"Failed to import IIN mappings: {e}") from e

    def import_state_formats(self, filepath: str) -> Dict[str, str]:
        """
        Import state license format specifications from JSON.

        Args:
            filepath: Path to state formats JSON file

        Returns:
            Dictionary mapping state codes to format patterns

        Raises:
            ImportError: If import fails

        Expected format:
        {
            "CA": "?#######",
            "TX": "#7-8",
            "FL": "?############",
            ...
        }
        """
        try:
            if not os.path.exists(filepath):
                raise ImportError(f"State formats file not found: {filepath}")

            with open(filepath, 'r') as f:
                formats = json.load(f)

            if not isinstance(formats, dict):
                raise ImportError("State formats must be a JSON object")

            logger.info(f"Loaded state formats from: {filepath}")
            return formats

        except json.JSONDecodeError as e:
            raise ImportError(f"Invalid JSON: {e}") from e
        except Exception as e:
            raise ImportError(f"Failed to import state formats: {e}") from e

    def auto_detect_format(self, filepath: str) -> str:
        """
        Auto-detect file format.

        Args:
            filepath: Path to file

        Returns:
            Detected format: 'json', 'csv', 'aamva', or 'unknown'
        """
        ext = Path(filepath).suffix.lower()

        if ext == '.json':
            return 'json'
        elif ext == '.csv':
            return 'csv'
        elif ext in ['.txt', '.dat']:
            # Try to detect AAMVA format by content
            try:
                with open(filepath, 'r') as f:
                    content = f.read(100)
                    if "@\n\x1E\r" in content or "ANSI " in content:
                        return 'aamva'
            except:
                pass

        return 'unknown'

    def import_auto(self, filepath: str) -> ImportResult:
        """
        Auto-detect format and import.

        Args:
            filepath: Path to file

        Returns:
            ImportResult object
        """
        format_type = self.auto_detect_format(filepath)

        if format_type == 'json':
            return self.import_json(filepath)
        elif format_type == 'csv':
            return self.import_csv(filepath)
        elif format_type == 'aamva':
            return self.import_aamva_file(filepath)
        else:
            result = ImportResult()
            result.add_error(f"Unknown file format: {filepath}")
            return result
