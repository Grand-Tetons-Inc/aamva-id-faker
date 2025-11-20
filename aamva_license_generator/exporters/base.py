"""
Abstract Base Classes for Export Operations

Defines the interface that all exporters must implement.
Provides common functionality for progress tracking, error handling, and validation.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import time


class ExportFormat(Enum):
    """Supported export formats"""
    PDF = "pdf"
    DOCX = "docx"
    ODT = "odt"
    PNG = "png"
    JPEG = "jpeg"
    BMP = "bmp"
    JSON = "json"
    CSV = "csv"
    TXT = "txt"


class ExportError(Exception):
    """Base exception for export operations"""
    pass


class ValidationError(ExportError):
    """Raised when export data validation fails"""
    pass


class EncodingError(ExportError):
    """Raised when data encoding fails"""
    pass


class RenderError(ExportError):
    """Raised when rendering/generation fails"""
    pass


@dataclass
class ExportProgress:
    """Progress information for export operations"""
    current: int = 0
    total: int = 0
    stage: str = "initializing"
    message: str = ""
    elapsed_seconds: float = 0.0
    estimated_remaining: float = 0.0

    @property
    def percent_complete(self) -> float:
        """Calculate percentage complete"""
        return (self.current / self.total * 100) if self.total > 0 else 0.0

    @property
    def is_complete(self) -> bool:
        """Check if export is complete"""
        return self.current >= self.total


@dataclass
class ExportResult:
    """Result of an export operation"""
    success: bool
    output_path: Optional[Path] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    items_processed: int = 0
    items_failed: int = 0
    duration_seconds: float = 0.0
    file_size_bytes: int = 0

    @property
    def has_errors(self) -> bool:
        """Check if export had errors"""
        return len(self.errors) > 0

    @property
    def has_warnings(self) -> bool:
        """Check if export had warnings"""
        return len(self.warnings) > 0

    @property
    def items_total(self) -> int:
        """Total items attempted"""
        return self.items_processed + self.items_failed


@dataclass
class ExportOptions:
    """Common options for export operations"""
    output_path: Union[str, Path]
    overwrite: bool = False
    verify: bool = False
    compress: bool = False
    quality: int = 100  # For image exports (1-100)
    dpi: int = 300  # For image/document exports
    progress_callback: Optional[Callable[[ExportProgress], None]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseExporter(ABC):
    """
    Abstract base class for all exporters

    All exporter implementations must inherit from this class and implement
    the required abstract methods. Provides common functionality for:
    - Progress tracking
    - Error handling
    - Validation
    - Resource management
    """

    def __init__(self, options: ExportOptions):
        """
        Initialize exporter

        Args:
            options: Export options
        """
        self.options = options
        self._start_time: Optional[float] = None
        self._progress = ExportProgress()

    @property
    @abstractmethod
    def format(self) -> ExportFormat:
        """Return the export format this exporter handles"""
        pass

    @property
    @abstractmethod
    def file_extension(self) -> str:
        """Return the file extension for this format (without dot)"""
        pass

    @abstractmethod
    def validate_data(self, data: Any) -> None:
        """
        Validate data before export

        Args:
            data: Data to validate

        Raises:
            ValidationError: If data is invalid
        """
        pass

    @abstractmethod
    def _export_impl(self, data: Any) -> ExportResult:
        """
        Implementation-specific export logic

        This is the main method that subclasses must implement.

        Args:
            data: Data to export

        Returns:
            ExportResult with details of the operation

        Raises:
            ExportError: On export failure
        """
        pass

    def export(self, data: Any) -> ExportResult:
        """
        Export data to file

        This is the main entry point for exporting. It handles:
        - Validation
        - Progress tracking
        - Error handling
        - Timing

        Args:
            data: Data to export

        Returns:
            ExportResult with details of the operation
        """
        self._start_time = time.time()

        try:
            # Validate data
            self._update_progress(0, 0, "validating", "Validating data...")
            self.validate_data(data)

            # Perform export
            result = self._export_impl(data)

            # Update result with timing
            result.duration_seconds = time.time() - self._start_time

            # Get file size if available
            if result.output_path and result.output_path.exists():
                result.file_size_bytes = result.output_path.stat().st_size

            return result

        except ValidationError as e:
            return ExportResult(
                success=False,
                errors=[f"Validation failed: {e}"],
                duration_seconds=time.time() - self._start_time
            )
        except Exception as e:
            return ExportResult(
                success=False,
                errors=[f"Export failed: {e}"],
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

            # Estimate remaining time
            if current > 0 and total > 0:
                avg_time_per_item = self._progress.elapsed_seconds / current
                remaining_items = total - current
                self._progress.estimated_remaining = avg_time_per_item * remaining_items

        # Notify callback
        if self.options.progress_callback:
            try:
                self.options.progress_callback(self._progress)
            except Exception as e:
                # Don't let callback errors break export
                print(f"Warning: Progress callback failed: {e}")

    def _add_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge user metadata with automatic metadata

        Args:
            metadata: User-provided metadata

        Returns:
            Combined metadata dictionary
        """
        auto_metadata = {
            "generator": "AAMVA License Generator",
            "format": self.format.value,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        return {**auto_metadata, **self.options.metadata, **metadata}


class BatchExporter(BaseExporter):
    """
    Base class for exporters that process items in batches

    Provides additional functionality for:
    - Per-item progress tracking
    - Partial success handling
    - Item-level error reporting
    """

    @abstractmethod
    def _export_item(self, item: Any, index: int) -> Optional[str]:
        """
        Export a single item

        Args:
            item: Item to export
            index: Item index in batch

        Returns:
            Error message if failed, None if successful

        Raises:
            ExportError: On unrecoverable error
        """
        pass

    def _export_impl(self, data: List[Any]) -> ExportResult:
        """
        Export a batch of items

        Args:
            data: List of items to export

        Returns:
            ExportResult with batch statistics
        """
        result = ExportResult(success=True, output_path=Path(self.options.output_path))
        total = len(data)

        for index, item in enumerate(data):
            self._update_progress(
                index,
                total,
                "exporting",
                f"Processing item {index + 1} of {total}..."
            )

            try:
                error = self._export_item(item, index)
                if error:
                    result.errors.append(f"Item {index}: {error}")
                    result.items_failed += 1
                else:
                    result.items_processed += 1

            except Exception as e:
                result.errors.append(f"Item {index}: Unexpected error: {e}")
                result.items_failed += 1

        # Mark as failed if too many items failed
        if result.items_failed > 0:
            failure_rate = result.items_failed / total
            if failure_rate > 0.5:  # More than 50% failed
                result.success = False
            else:
                # Partial success - add warning
                result.warnings.append(
                    f"{result.items_failed} of {total} items failed"
                )

        self._update_progress(total, total, "complete", "Export complete")

        return result


class StreamingExporter(BaseExporter):
    """
    Base class for exporters that support streaming large datasets

    Useful for exporting large amounts of data without loading everything
    into memory at once.
    """

    @abstractmethod
    def _begin_stream(self) -> None:
        """
        Initialize the stream

        Called once before processing any items.

        Raises:
            ExportError: On initialization failure
        """
        pass

    @abstractmethod
    def _write_item(self, item: Any) -> None:
        """
        Write a single item to the stream

        Args:
            item: Item to write

        Raises:
            ExportError: On write failure
        """
        pass

    @abstractmethod
    def _end_stream(self) -> None:
        """
        Finalize the stream

        Called once after all items are processed.

        Raises:
            ExportError: On finalization failure
        """
        pass

    def _export_impl(self, data: List[Any]) -> ExportResult:
        """
        Export data using streaming

        Args:
            data: Items to export

        Returns:
            ExportResult with operation details
        """
        result = ExportResult(success=True, output_path=Path(self.options.output_path))
        total = len(data)

        try:
            # Initialize stream
            self._update_progress(0, total, "initializing", "Initializing stream...")
            self._begin_stream()

            # Write items
            for index, item in enumerate(data):
                self._update_progress(
                    index,
                    total,
                    "streaming",
                    f"Writing item {index + 1} of {total}..."
                )

                try:
                    self._write_item(item)
                    result.items_processed += 1
                except Exception as e:
                    result.errors.append(f"Item {index}: {e}")
                    result.items_failed += 1

            # Finalize stream
            self._update_progress(total, total, "finalizing", "Finalizing export...")
            self._end_stream()

            # Check success
            if result.items_failed > 0:
                failure_rate = result.items_failed / total
                if failure_rate > 0.5:
                    result.success = False
                else:
                    result.warnings.append(
                        f"{result.items_failed} of {total} items failed"
                    )

        except Exception as e:
            result.success = False
            result.errors.append(f"Stream error: {e}")

        return result
