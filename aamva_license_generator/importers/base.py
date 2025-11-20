"""
Abstract Base Classes for Import Operations

Defines the interface that all importers must implement.
Provides common functionality for validation, error handling, and progress tracking.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import time


class ImportFormat(Enum):
    """Supported import formats"""
    JSON = "json"
    CSV = "csv"
    TXT = "txt"


class ImportError(Exception):
    """Base exception for import operations"""
    pass


class ParseError(ImportError):
    """Raised when file parsing fails"""
    pass


class SchemaError(ImportError):
    """Raised when imported data doesn't match expected schema"""
    pass


@dataclass
class ImportProgress:
    """Progress information for import operations"""
    current: int = 0
    total: int = 0
    stage: str = "initializing"
    message: str = ""
    elapsed_seconds: float = 0.0

    @property
    def percent_complete(self) -> float:
        """Calculate percentage complete"""
        return (self.current / self.total * 100) if self.total > 0 else 0.0

    @property
    def is_complete(self) -> bool:
        """Check if import is complete"""
        return self.current >= self.total


@dataclass
class ImportResult:
    """Result of an import operation"""
    success: bool
    data: List[Any] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    items_imported: int = 0
    items_skipped: int = 0
    duration_seconds: float = 0.0

    @property
    def has_errors(self) -> bool:
        """Check if import had errors"""
        return len(self.errors) > 0

    @property
    def has_warnings(self) -> bool:
        """Check if import had warnings"""
        return len(self.warnings) > 0

    @property
    def items_total(self) -> int:
        """Total items processed"""
        return self.items_imported + self.items_skipped


@dataclass
class ImportOptions:
    """Common options for import operations"""
    input_path: Union[str, Path]
    validate_schema: bool = True
    skip_invalid: bool = False  # Skip invalid items or fail immediately
    max_errors: int = 10  # Maximum errors before aborting
    progress_callback: Optional[Callable[[ImportProgress], None]] = None
    strict: bool = False  # Strict validation mode


class BaseImporter(ABC):
    """
    Abstract base class for all importers

    All importer implementations must inherit from this class and implement
    the required abstract methods.
    """

    def __init__(self, options: ImportOptions):
        """
        Initialize importer

        Args:
            options: Import options
        """
        self.options = options
        self._start_time: Optional[float] = None
        self._progress = ImportProgress()

    @property
    @abstractmethod
    def format(self) -> ImportFormat:
        """Return the import format this importer handles"""
        pass

    @property
    @abstractmethod
    def supported_extensions(self) -> List[str]:
        """Return list of supported file extensions"""
        pass

    @abstractmethod
    def validate_file(self, filepath: Path) -> None:
        """
        Validate file before import

        Args:
            filepath: File to validate

        Raises:
            ImportError: If file is invalid
        """
        pass

    @abstractmethod
    def _import_impl(self) -> ImportResult:
        """
        Implementation-specific import logic

        Returns:
            ImportResult with imported data

        Raises:
            ImportError: On import failure
        """
        pass

    def import_data(self) -> ImportResult:
        """
        Import data from file

        This is the main entry point for importing. It handles:
        - File validation
        - Progress tracking
        - Error handling
        - Timing

        Returns:
            ImportResult with imported data
        """
        self._start_time = time.time()
        filepath = Path(self.options.input_path)

        try:
            # Validate file exists
            if not filepath.exists():
                return ImportResult(
                    success=False,
                    errors=[f"File not found: {filepath}"]
                )

            # Check file extension
            if filepath.suffix.lstrip('.') not in self.supported_extensions:
                return ImportResult(
                    success=False,
                    errors=[
                        f"Unsupported file extension '{filepath.suffix}'. "
                        f"Expected one of: {', '.join(self.supported_extensions)}"
                    ]
                )

            # Validate file
            self._update_progress(0, 0, "validating", "Validating file...")
            self.validate_file(filepath)

            # Perform import
            result = self._import_impl()

            # Update result with timing
            result.duration_seconds = time.time() - self._start_time

            return result

        except (ParseError, SchemaError) as e:
            return ImportResult(
                success=False,
                errors=[str(e)],
                duration_seconds=time.time() - self._start_time
            )
        except Exception as e:
            return ImportResult(
                success=False,
                errors=[f"Import failed: {e}"],
                duration_seconds=time.time() - self._start_time
            )

    def _update_progress(self, current: int, total: int, stage: str, message: str):
        """
        Update progress and notify callback

        Args:
            current: Current item number
            total: Total items
            stage: Current stage name
            message: Progress message
        """
        self._progress.current = current
        self._progress.total = total
        self._progress.stage = stage
        self._progress.message = message

        if self._start_time:
            self._progress.elapsed_seconds = time.time() - self._start_time

        # Notify callback
        if self.options.progress_callback:
            try:
                self.options.progress_callback(self._progress)
            except Exception as e:
                # Don't let callback errors break import
                print(f"Warning: Progress callback failed: {e}")

    @abstractmethod
    def validate_item_schema(self, item: Any) -> Optional[str]:
        """
        Validate a single imported item

        Args:
            item: Item to validate

        Returns:
            Error message if invalid, None if valid
        """
        pass


class StreamingImporter(BaseImporter):
    """
    Base class for importers that support streaming large files

    Useful for importing large datasets without loading everything
    into memory at once.
    """

    @abstractmethod
    def _open_stream(self) -> None:
        """
        Open the input stream

        Raises:
            ImportError: On stream open failure
        """
        pass

    @abstractmethod
    def _read_item(self) -> Optional[Any]:
        """
        Read next item from stream

        Returns:
            Next item, or None if stream is exhausted

        Raises:
            ParseError: On parse error
        """
        pass

    @abstractmethod
    def _close_stream(self) -> None:
        """
        Close the input stream

        Should be safe to call multiple times.
        """
        pass

    def _import_impl(self) -> ImportResult:
        """
        Import data using streaming

        Returns:
            ImportResult with imported data
        """
        result = ImportResult(success=True)
        error_count = 0

        try:
            # Open stream
            self._update_progress(0, 0, "opening", "Opening file stream...")
            self._open_stream()

            # Read items
            item_count = 0
            while True:
                try:
                    item = self._read_item()
                    if item is None:
                        break  # End of stream

                    item_count += 1
                    self._update_progress(
                        item_count,
                        0,  # Unknown total for streaming
                        "importing",
                        f"Imported {item_count} items..."
                    )

                    # Validate schema if requested
                    if self.options.validate_schema:
                        error = self.validate_item_schema(item)
                        if error:
                            result.warnings.append(f"Item {item_count}: {error}")

                            if self.options.skip_invalid:
                                result.items_skipped += 1
                                continue
                            else:
                                result.errors.append(f"Item {item_count}: {error}")
                                error_count += 1

                                if error_count >= self.options.max_errors:
                                    result.errors.append("Too many errors, aborting import")
                                    result.success = False
                                    break

                    # Add to results
                    result.data.append(item)
                    result.items_imported += 1

                except ParseError as e:
                    result.errors.append(f"Item {item_count + 1}: Parse error: {e}")
                    error_count += 1

                    if not self.options.skip_invalid or error_count >= self.options.max_errors:
                        result.success = False
                        break

                    result.items_skipped += 1

            # Check if we imported anything
            if result.items_imported == 0 and error_count > 0:
                result.success = False

        except Exception as e:
            result.success = False
            result.errors.append(f"Stream error: {e}")

        finally:
            # Always close stream
            try:
                self._close_stream()
            except Exception as e:
                print(f"Warning: Failed to close stream: {e}")

        return result
