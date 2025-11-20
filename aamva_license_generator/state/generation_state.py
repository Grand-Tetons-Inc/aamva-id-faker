"""
License Generation State Tracking

Manages the state of license generation operations including progress,
status, and individual license tracking.

Features:
- Real-time progress tracking
- Per-license status tracking
- Thread-safe operations
- Cancellation support
- Statistics collection
"""

import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional
import logging

from ..events import Event, EventType, emit

logger = logging.getLogger(__name__)


class GenerationStatus(Enum):
    """Status of license generation operation"""
    IDLE = auto()           # Not generating
    INITIALIZING = auto()   # Preparing to generate
    GENERATING = auto()     # Currently generating
    PAUSED = auto()         # Generation paused
    COMPLETED = auto()      # Successfully completed
    FAILED = auto()         # Failed with errors
    CANCELLED = auto()      # Cancelled by user


class LicenseStatus(Enum):
    """Status of individual license"""
    PENDING = auto()        # Not started
    PROCESSING = auto()     # Currently processing
    COMPLETED = auto()      # Successfully created
    FAILED = auto()         # Failed to create
    SKIPPED = auto()        # Skipped due to error


@dataclass
class LicenseGenerationItem:
    """
    Represents a single license in a generation batch

    Tracks the state and result of generating one license.
    """
    index: int                              # Index in batch (0-based)
    status: LicenseStatus = LicenseStatus.PENDING
    state_code: Optional[str] = None        # State code (e.g., "CA")
    license_number: Optional[str] = None    # Generated license number
    name: Optional[str] = None              # Generated name
    error: Optional[str] = None             # Error message if failed
    start_time: Optional[datetime] = None   # When processing started
    end_time: Optional[datetime] = None     # When processing completed
    output_files: List[str] = field(default_factory=list)  # Generated file paths

    @property
    def duration(self) -> Optional[float]:
        """Get processing duration in seconds"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

    @property
    def is_complete(self) -> bool:
        """Check if processing is complete (success or failure)"""
        return self.status in (
            LicenseStatus.COMPLETED,
            LicenseStatus.FAILED,
            LicenseStatus.SKIPPED
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'index': self.index,
            'status': self.status.name,
            'state_code': self.state_code,
            'license_number': self.license_number,
            'name': self.name,
            'error': self.error,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration': self.duration,
            'output_files': self.output_files
        }


class GenerationState:
    """
    Manages the state of a license generation operation

    Thread-safe tracking of generation progress, individual licenses,
    and overall statistics.

    Example:
        >>> state = GenerationState(total_count=50)
        >>> state.start()
        >>> for i in range(50):
        ...     state.start_license(i)
        ...     # ... generate license ...
        ...     state.complete_license(i, files=['license.bmp'])
        >>> state.complete()
    """

    def __init__(self, total_count: int):
        """
        Initialize generation state

        Args:
            total_count: Total number of licenses to generate
        """
        self.total_count = total_count
        self._lock = threading.RLock()

        # Overall status
        self.status = GenerationStatus.IDLE
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.cancelled = False

        # Individual licenses
        self.licenses: List[LicenseGenerationItem] = [
            LicenseGenerationItem(index=i)
            for i in range(total_count)
        ]

        # Progress tracking
        self.current_index = 0
        self.completed_count = 0
        self.failed_count = 0
        self.skipped_count = 0

        # Stage tracking
        self.current_stage = "Initializing"
        self.stage_progress = 0.0  # 0.0 to 1.0

        # Output tracking
        self.output_directory: Optional[str] = None
        self.output_files: List[str] = []

        # Error tracking
        self.errors: List[Dict[str, Any]] = []

    # Status management

    def start(self):
        """Mark generation as started"""
        with self._lock:
            self.status = GenerationStatus.GENERATING
            self.start_time = datetime.now()
            self.current_index = 0

            emit(Event(
                EventType.GENERATION_STARTED,
                source=self,
                data={
                    'total_count': self.total_count,
                    'start_time': self.start_time.isoformat()
                }
            ))

            logger.info(f"Generation started: {self.total_count} licenses")

    def complete(self):
        """Mark generation as completed"""
        with self._lock:
            self.status = GenerationStatus.COMPLETED
            self.end_time = datetime.now()

            emit(Event(
                EventType.GENERATION_COMPLETED,
                source=self,
                data={
                    'total_count': self.total_count,
                    'completed_count': self.completed_count,
                    'failed_count': self.failed_count,
                    'skipped_count': self.skipped_count,
                    'duration': self.duration,
                    'output_files': len(self.output_files)
                }
            ))

            logger.info(
                f"Generation completed: {self.completed_count}/{self.total_count} "
                f"successful, {self.failed_count} failed, {self.skipped_count} skipped "
                f"in {self.duration:.1f}s"
            )

    def fail(self, error: str):
        """Mark generation as failed"""
        with self._lock:
            self.status = GenerationStatus.FAILED
            self.end_time = datetime.now()

            emit(Event(
                EventType.GENERATION_FAILED,
                source=self,
                data={
                    'error': error,
                    'completed_count': self.completed_count,
                    'total_count': self.total_count
                }
            ))

            logger.error(f"Generation failed: {error}")

    def cancel(self):
        """Cancel generation"""
        with self._lock:
            self.cancelled = True
            self.status = GenerationStatus.CANCELLED
            self.end_time = datetime.now()

            emit(Event(
                EventType.GENERATION_CANCELLED,
                source=self,
                data={
                    'completed_count': self.completed_count,
                    'total_count': self.total_count
                }
            ))

            logger.info(
                f"Generation cancelled: {self.completed_count}/{self.total_count} "
                f"completed"
            )

    def pause(self):
        """Pause generation"""
        with self._lock:
            if self.status == GenerationStatus.GENERATING:
                self.status = GenerationStatus.PAUSED
                logger.info("Generation paused")

    def resume(self):
        """Resume generation"""
        with self._lock:
            if self.status == GenerationStatus.PAUSED:
                self.status = GenerationStatus.GENERATING
                logger.info("Generation resumed")

    # License tracking

    def start_license(
        self,
        index: int,
        state_code: Optional[str] = None
    ):
        """
        Mark license as started

        Args:
            index: License index (0-based)
            state_code: State code for this license
        """
        with self._lock:
            if index >= len(self.licenses):
                logger.warning(f"Invalid license index: {index}")
                return

            license_item = self.licenses[index]
            license_item.status = LicenseStatus.PROCESSING
            license_item.state_code = state_code
            license_item.start_time = datetime.now()

            self.current_index = index

            emit(Event(
                EventType.LICENSE_CREATED,
                source=self,
                data={
                    'index': index,
                    'state_code': state_code,
                    'progress': self.progress
                }
            ))

    def complete_license(
        self,
        index: int,
        license_number: Optional[str] = None,
        name: Optional[str] = None,
        files: Optional[List[str]] = None
    ):
        """
        Mark license as completed

        Args:
            index: License index
            license_number: Generated license number
            name: Generated name
            files: List of generated file paths
        """
        with self._lock:
            if index >= len(self.licenses):
                logger.warning(f"Invalid license index: {index}")
                return

            license_item = self.licenses[index]
            license_item.status = LicenseStatus.COMPLETED
            license_item.license_number = license_number
            license_item.name = name
            license_item.end_time = datetime.now()

            if files:
                license_item.output_files = files
                self.output_files.extend(files)

            self.completed_count += 1

            # Emit progress event
            self._emit_progress()

    def fail_license(
        self,
        index: int,
        error: str
    ):
        """
        Mark license as failed

        Args:
            index: License index
            error: Error message
        """
        with self._lock:
            if index >= len(self.licenses):
                logger.warning(f"Invalid license index: {index}")
                return

            license_item = self.licenses[index]
            license_item.status = LicenseStatus.FAILED
            license_item.error = error
            license_item.end_time = datetime.now()

            self.failed_count += 1

            # Track error
            self.errors.append({
                'index': index,
                'error': error,
                'timestamp': datetime.now().isoformat()
            })

            emit(Event(
                EventType.LICENSE_FAILED,
                source=self,
                data={
                    'index': index,
                    'error': error
                }
            ))

            # Emit progress event
            self._emit_progress()

    def skip_license(
        self,
        index: int,
        reason: str
    ):
        """
        Mark license as skipped

        Args:
            index: License index
            reason: Reason for skipping
        """
        with self._lock:
            if index >= len(self.licenses):
                logger.warning(f"Invalid license index: {index}")
                return

            license_item = self.licenses[index]
            license_item.status = LicenseStatus.SKIPPED
            license_item.error = reason
            license_item.end_time = datetime.now()

            self.skipped_count += 1

            # Emit progress event
            self._emit_progress()

    def _emit_progress(self):
        """Emit progress update event"""
        emit(Event(
            EventType.GENERATION_PROGRESS,
            source=self,
            data={
                'progress': self.progress,
                'current_index': self.current_index,
                'completed_count': self.completed_count,
                'failed_count': self.failed_count,
                'skipped_count': self.skipped_count,
                'total_count': self.total_count,
                'estimated_remaining': self.estimated_remaining_time
            }
        ))

    # Stage management

    def set_stage(self, stage: str, progress: float = 0.0):
        """
        Set current processing stage

        Args:
            stage: Stage name (e.g., "Generating barcodes")
            progress: Stage progress (0.0 to 1.0)
        """
        with self._lock:
            self.current_stage = stage
            self.stage_progress = progress

            logger.debug(f"Stage: {stage} ({progress*100:.0f}%)")

    # Properties

    @property
    def progress(self) -> float:
        """Get overall progress (0.0 to 1.0)"""
        with self._lock:
            if self.total_count == 0:
                return 1.0

            completed = self.completed_count + self.failed_count + self.skipped_count
            return completed / self.total_count

    @property
    def duration(self) -> float:
        """Get total duration in seconds"""
        with self._lock:
            if not self.start_time:
                return 0.0

            end = self.end_time or datetime.now()
            return (end - self.start_time).total_seconds()

    @property
    def estimated_remaining_time(self) -> Optional[float]:
        """Estimate remaining time in seconds"""
        with self._lock:
            if self.completed_count == 0:
                return None

            elapsed = self.duration
            avg_time = elapsed / self.completed_count
            remaining_count = self.total_count - (
                self.completed_count + self.failed_count + self.skipped_count
            )

            return avg_time * remaining_count

    @property
    def licenses_per_second(self) -> float:
        """Get average licenses processed per second"""
        with self._lock:
            if self.duration == 0:
                return 0.0

            completed = self.completed_count + self.failed_count + self.skipped_count
            return completed / self.duration

    @property
    def is_complete(self) -> bool:
        """Check if generation is complete"""
        with self._lock:
            return self.status in (
                GenerationStatus.COMPLETED,
                GenerationStatus.FAILED,
                GenerationStatus.CANCELLED
            )

    @property
    def is_running(self) -> bool:
        """Check if generation is running"""
        with self._lock:
            return self.status == GenerationStatus.GENERATING

    # Query methods

    def get_license(self, index: int) -> Optional[LicenseGenerationItem]:
        """Get license item by index"""
        with self._lock:
            if 0 <= index < len(self.licenses):
                return self.licenses[index]
            return None

    def get_completed_licenses(self) -> List[LicenseGenerationItem]:
        """Get all completed licenses"""
        with self._lock:
            return [
                lic for lic in self.licenses
                if lic.status == LicenseStatus.COMPLETED
            ]

    def get_failed_licenses(self) -> List[LicenseGenerationItem]:
        """Get all failed licenses"""
        with self._lock:
            return [
                lic for lic in self.licenses
                if lic.status == LicenseStatus.FAILED
            ]

    def get_pending_licenses(self) -> List[LicenseGenerationItem]:
        """Get all pending licenses"""
        with self._lock:
            return [
                lic for lic in self.licenses
                if lic.status == LicenseStatus.PENDING
            ]

    # Statistics

    def get_statistics(self) -> Dict[str, Any]:
        """Get detailed statistics"""
        with self._lock:
            return {
                'status': self.status.name,
                'total_count': self.total_count,
                'completed_count': self.completed_count,
                'failed_count': self.failed_count,
                'skipped_count': self.skipped_count,
                'progress': self.progress,
                'duration': self.duration,
                'estimated_remaining': self.estimated_remaining_time,
                'licenses_per_second': self.licenses_per_second,
                'current_stage': self.current_stage,
                'stage_progress': self.stage_progress,
                'output_files_count': len(self.output_files),
                'errors_count': len(self.errors),
                'cancelled': self.cancelled
            }

    # Serialization

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        with self._lock:
            return {
                'status': self.status.name,
                'total_count': self.total_count,
                'completed_count': self.completed_count,
                'failed_count': self.failed_count,
                'skipped_count': self.skipped_count,
                'start_time': self.start_time.isoformat() if self.start_time else None,
                'end_time': self.end_time.isoformat() if self.end_time else None,
                'duration': self.duration,
                'progress': self.progress,
                'current_stage': self.current_stage,
                'output_directory': self.output_directory,
                'output_files': self.output_files,
                'licenses': [lic.to_dict() for lic in self.licenses],
                'errors': self.errors
            }

    def __str__(self):
        return (
            f"GenerationState(status={self.status.name}, "
            f"progress={self.progress*100:.1f}%, "
            f"completed={self.completed_count}/{self.total_count})"
        )
