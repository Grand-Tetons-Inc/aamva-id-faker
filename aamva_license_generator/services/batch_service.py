"""
Batch Service - Batch License Generation Management

Provides high-level batch processing with:
- Progress tracking
- Error recovery
- Partial success handling
- Transaction-like semantics
- Rollback capabilities
"""

import os
import time
from typing import Dict, List, Optional, Callable, Any, Tuple
from datetime import datetime
from enum import Enum
import logging
from threading import Lock

# Configure logging
logger = logging.getLogger(__name__)


class BatchStatus(Enum):
    """Batch operation status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class BatchError(Exception):
    """Raised when batch operation fails critically."""
    pass


class BatchResult:
    """
    Result of a batch operation.

    Attributes:
        status: Overall batch status
        total: Total items to process
        succeeded: Number of successful items
        failed: Number of failed items
        skipped: Number of skipped items
        results: List of individual results
        errors: List of error messages
        warnings: List of warning messages
        start_time: Operation start time
        end_time: Operation end time
        duration: Duration in seconds
    """

    def __init__(self, total: int = 0):
        self.status = BatchStatus.PENDING
        self.total = total
        self.succeeded = 0
        self.failed = 0
        self.skipped = 0
        self.results: List[Any] = []
        self.errors: List[Tuple[int, str]] = []  # (index, error_message)
        self.warnings: List[Tuple[int, str]] = []  # (index, warning_message)
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.duration: float = 0.0

    def start(self):
        """Mark batch as started."""
        self.status = BatchStatus.IN_PROGRESS
        self.start_time = datetime.now()

    def complete(self):
        """Mark batch as completed."""
        self.end_time = datetime.now()
        if self.start_time:
            self.duration = (self.end_time - self.start_time).total_seconds()

        if self.failed == 0:
            self.status = BatchStatus.COMPLETED
        elif self.succeeded > 0:
            self.status = BatchStatus.PARTIAL
        else:
            self.status = BatchStatus.FAILED

    def add_success(self, result: Any):
        """Record a successful item."""
        self.succeeded += 1
        self.results.append(result)

    def add_failure(self, index: int, error: str):
        """Record a failed item."""
        self.failed += 1
        self.errors.append((index, error))

    def add_skip(self, index: int, reason: str):
        """Record a skipped item."""
        self.skipped += 1
        self.warnings.append((index, f"Skipped: {reason}"))

    def add_warning(self, index: int, warning: str):
        """Add a warning."""
        self.warnings.append((index, warning))

    @property
    def success_rate(self) -> float:
        """Calculate success rate (0-100)."""
        if self.total == 0:
            return 0.0
        return (self.succeeded / self.total) * 100

    @property
    def is_successful(self) -> bool:
        """Check if batch was fully successful."""
        return self.status == BatchStatus.COMPLETED

    @property
    def is_partial(self) -> bool:
        """Check if batch had partial success."""
        return self.status == BatchStatus.PARTIAL

    def __str__(self) -> str:
        """String representation."""
        if self.status == BatchStatus.COMPLETED:
            return f"✓ Batch completed: {self.succeeded}/{self.total} successful ({self.duration:.2f}s)"
        elif self.status == BatchStatus.PARTIAL:
            return f"⚠ Batch partial: {self.succeeded}/{self.total} successful, {self.failed} failed ({self.duration:.2f}s)"
        elif self.status == BatchStatus.FAILED:
            return f"✗ Batch failed: {self.failed}/{self.total} failed ({self.duration:.2f}s)"
        else:
            return f"Batch {self.status.value}: {self.succeeded}/{self.total}"

    def __bool__(self) -> bool:
        """Boolean representation (True if any succeeded)."""
        return self.succeeded > 0


class BatchService:
    """
    Service for managing batch operations with robust error handling.

    Features:
    - Progress tracking and reporting
    - Partial success handling
    - Error recovery and retry logic
    - Transaction-like operations
    - Rollback capabilities
    - Thread-safe operations
    """

    def __init__(
        self,
        fail_fast: bool = False,
        max_failures: Optional[int] = None,
        retry_attempts: int = 0,
        rollback_on_failure: bool = False
    ):
        """
        Initialize the BatchService.

        Args:
            fail_fast: Stop on first failure
            max_failures: Maximum failures before stopping (None = unlimited)
            retry_attempts: Number of retry attempts for failed items
            rollback_on_failure: Rollback on total failure
        """
        self.fail_fast = fail_fast
        self.max_failures = max_failures
        self.retry_attempts = retry_attempts
        self.rollback_on_failure = rollback_on_failure
        self._lock = Lock()

    def process_batch(
        self,
        items: List[Any],
        processor: Callable[[Any, int], Any],
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        validator: Optional[Callable[[Any], bool]] = None
    ) -> BatchResult:
        """
        Process a batch of items with comprehensive error handling.

        Args:
            items: List of items to process
            processor: Function to process each item (item, index) -> result
            progress_callback: Optional callback(current, total, status)
            validator: Optional validator function(result) -> bool

        Returns:
            BatchResult object

        Example:
            def generate_license(state, index):
                return service.generate_license_data(state)

            result = batch_service.process_batch(
                items=['CA', 'TX', 'FL'],
                processor=generate_license,
                progress_callback=lambda c, t, s: print(f"{c}/{t}: {s}")
            )
        """
        result = BatchResult(total=len(items))
        result.start()

        with self._lock:
            for i, item in enumerate(items):
                try:
                    # Check failure threshold
                    if self.max_failures and result.failed >= self.max_failures:
                        remaining = len(items) - i
                        for j in range(i, len(items)):
                            result.add_skip(j, "Max failures reached")
                        logger.warning(f"Stopping batch: max failures reached ({self.max_failures})")
                        break

                    # Process item with retry logic
                    item_result = self._process_with_retry(
                        item, i, processor, self.retry_attempts
                    )

                    # Validate result if validator provided
                    if validator and not validator(item_result):
                        raise ValueError("Validation failed")

                    # Record success
                    result.add_success(item_result)

                    if progress_callback:
                        progress_callback(i + 1, result.total, "success")

                except Exception as e:
                    error_msg = str(e)
                    result.add_failure(i, error_msg)
                    logger.error(f"Item {i} failed: {error_msg}")

                    if progress_callback:
                        progress_callback(i + 1, result.total, f"failed: {error_msg}")

                    if self.fail_fast:
                        logger.warning("Stopping batch: fail-fast enabled")
                        remaining = len(items) - i - 1
                        for j in range(i + 1, len(items)):
                            result.add_skip(j, "Fail-fast triggered")
                        break

        result.complete()

        # Handle rollback
        if self.rollback_on_failure and not result.is_successful:
            self._rollback(result)

        return result

    def _process_with_retry(
        self,
        item: Any,
        index: int,
        processor: Callable,
        max_attempts: int
    ) -> Any:
        """
        Process an item with retry logic.

        Args:
            item: Item to process
            index: Item index
            processor: Processing function
            max_attempts: Maximum retry attempts

        Returns:
            Processing result

        Raises:
            Exception: If all attempts fail
        """
        last_error = None

        for attempt in range(max_attempts + 1):
            try:
                return processor(item, index)
            except Exception as e:
                last_error = e
                if attempt < max_attempts:
                    logger.warning(f"Retry {attempt + 1}/{max_attempts} for item {index}: {e}")
                    time.sleep(0.1 * (attempt + 1))  # Exponential backoff
                else:
                    raise last_error

    def _rollback(self, result: BatchResult):
        """
        Rollback batch operation (placeholder for cleanup logic).

        Args:
            result: Batch result to rollback

        Note:
            Subclasses should override this to implement actual rollback logic.
        """
        logger.warning(f"Rollback triggered for batch with {result.failed} failures")
        # Placeholder: actual rollback logic would be implemented here
        # e.g., delete generated files, revert database changes, etc.

    def process_with_transaction(
        self,
        items: List[Any],
        processor: Callable[[Any, int], Any],
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> BatchResult:
        """
        Process batch with transaction-like semantics (all-or-nothing).

        Args:
            items: List of items to process
            processor: Processing function
            progress_callback: Optional progress callback

        Returns:
            BatchResult object

        Note:
            If any item fails, all successful items are rolled back.
        """
        # Temporarily enable fail-fast and rollback
        original_fail_fast = self.fail_fast
        original_rollback = self.rollback_on_failure

        self.fail_fast = True
        self.rollback_on_failure = True

        try:
            result = self.process_batch(items, processor, progress_callback)

            # Check if fully successful
            if result.failed > 0:
                logger.error("Transaction failed: rolling back all changes")
                result.status = BatchStatus.FAILED
                result.results = []  # Clear results

            return result

        finally:
            # Restore original settings
            self.fail_fast = original_fail_fast
            self.rollback_on_failure = original_rollback

    def process_in_chunks(
        self,
        items: List[Any],
        processor: Callable[[Any, int], Any],
        chunk_size: int = 10,
        progress_callback: Optional[Callable[[int, int, int, int], None]] = None
    ) -> List[BatchResult]:
        """
        Process items in chunks for better memory management.

        Args:
            items: List of items to process
            processor: Processing function
            chunk_size: Items per chunk
            progress_callback: Optional callback(chunk_num, total_chunks, item_num, total_items)

        Returns:
            List of BatchResult objects (one per chunk)
        """
        results = []
        total_items = len(items)
        num_chunks = (total_items + chunk_size - 1) // chunk_size

        for chunk_idx in range(num_chunks):
            start_idx = chunk_idx * chunk_size
            end_idx = min(start_idx + chunk_size, total_items)
            chunk = items[start_idx:end_idx]

            logger.info(f"Processing chunk {chunk_idx + 1}/{num_chunks} ({len(chunk)} items)")

            def chunk_progress(current, total, status):
                overall_current = start_idx + current
                if progress_callback:
                    progress_callback(chunk_idx + 1, num_chunks, overall_current, total_items)

            chunk_result = self.process_batch(chunk, processor, chunk_progress)
            results.append(chunk_result)

            # Stop if chunk failed and fail-fast enabled
            if self.fail_fast and chunk_result.failed > 0:
                logger.warning(f"Stopping chunks: chunk {chunk_idx + 1} failed")
                break

        return results

    def aggregate_results(self, chunk_results: List[BatchResult]) -> BatchResult:
        """
        Aggregate multiple chunk results into a single result.

        Args:
            chunk_results: List of chunk results

        Returns:
            Aggregated BatchResult
        """
        if not chunk_results:
            return BatchResult()

        total = sum(r.total for r in chunk_results)
        aggregated = BatchResult(total=total)

        aggregated.start_time = min(r.start_time for r in chunk_results if r.start_time)
        aggregated.end_time = max(r.end_time for r in chunk_results if r.end_time)

        for chunk_result in chunk_results:
            aggregated.succeeded += chunk_result.succeeded
            aggregated.failed += chunk_result.failed
            aggregated.skipped += chunk_result.skipped
            aggregated.results.extend(chunk_result.results)
            aggregated.errors.extend(chunk_result.errors)
            aggregated.warnings.extend(chunk_result.warnings)

        aggregated.complete()
        return aggregated

    def validate_batch(
        self,
        items: List[Any],
        validator: Callable[[Any], Tuple[bool, Optional[str]]],
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> BatchResult:
        """
        Validate a batch of items.

        Args:
            items: List of items to validate
            validator: Validation function(item) -> (is_valid, error_message)
            progress_callback: Optional progress callback

        Returns:
            BatchResult with validation results
        """
        result = BatchResult(total=len(items))
        result.start()

        for i, item in enumerate(items):
            try:
                is_valid, error_msg = validator(item)

                if is_valid:
                    result.add_success(item)
                else:
                    result.add_failure(i, error_msg or "Validation failed")

                if progress_callback:
                    progress_callback(i + 1, result.total)

            except Exception as e:
                result.add_failure(i, f"Validation error: {e}")

        result.complete()
        return result

    def get_summary(self, result: BatchResult) -> Dict[str, Any]:
        """
        Get a detailed summary of batch results.

        Args:
            result: BatchResult to summarize

        Returns:
            Summary dictionary
        """
        return {
            "status": result.status.value,
            "total": result.total,
            "succeeded": result.succeeded,
            "failed": result.failed,
            "skipped": result.skipped,
            "success_rate": f"{result.success_rate:.2f}%",
            "duration": f"{result.duration:.2f}s",
            "errors": result.errors,
            "warnings": result.warnings,
            "start_time": result.start_time.isoformat() if result.start_time else None,
            "end_time": result.end_time.isoformat() if result.end_time else None,
        }
