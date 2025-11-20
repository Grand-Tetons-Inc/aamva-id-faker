"""
Generation History Management

Manages the history of license generation operations with persistence.

Features:
- Track last 100 generations
- JSON persistence
- Search and filtering
- Statistics aggregation
- Thread-safe operations
"""

import json
import threading
from collections import deque
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Deque, Dict, List, Optional
import logging

from ..events import Event, EventType, emit

logger = logging.getLogger(__name__)


@dataclass
class HistoryEntry:
    """
    Represents a single generation operation in history

    Stores metadata about a completed generation for later reference.
    """
    timestamp: datetime
    state_code: Optional[str]               # State code or None for all states
    total_count: int                        # Number of licenses requested
    completed_count: int                    # Number successfully completed
    failed_count: int                       # Number that failed
    skipped_count: int                      # Number skipped
    duration: float                         # Duration in seconds
    output_directory: str                   # Where files were saved
    output_files: List[str] = field(default_factory=list)  # Generated file paths
    formats: List[str] = field(default_factory=list)       # Output formats (PDF, DOCX, etc.)
    success: bool = True                    # Overall success
    error: Optional[str] = None             # Error message if failed
    cancelled: bool = False                 # Whether generation was cancelled

    @property
    def success_rate(self) -> float:
        """Calculate success rate (0.0 to 1.0)"""
        if self.total_count == 0:
            return 0.0
        return self.completed_count / self.total_count

    @property
    def licenses_per_second(self) -> float:
        """Calculate generation speed"""
        if self.duration == 0:
            return 0.0
        return self.completed_count / self.duration

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'state_code': self.state_code,
            'total_count': self.total_count,
            'completed_count': self.completed_count,
            'failed_count': self.failed_count,
            'skipped_count': self.skipped_count,
            'duration': self.duration,
            'output_directory': self.output_directory,
            'output_files': self.output_files,
            'formats': self.formats,
            'success': self.success,
            'error': self.error,
            'cancelled': self.cancelled,
            'success_rate': self.success_rate,
            'licenses_per_second': self.licenses_per_second
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HistoryEntry':
        """Create from dictionary"""
        # Parse timestamp
        timestamp = data.get('timestamp')
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)

        return cls(
            timestamp=timestamp,
            state_code=data.get('state_code'),
            total_count=data.get('total_count', 0),
            completed_count=data.get('completed_count', 0),
            failed_count=data.get('failed_count', 0),
            skipped_count=data.get('skipped_count', 0),
            duration=data.get('duration', 0.0),
            output_directory=data.get('output_directory', ''),
            output_files=data.get('output_files', []),
            formats=data.get('formats', []),
            success=data.get('success', True),
            error=data.get('error'),
            cancelled=data.get('cancelled', False)
        )

    def __str__(self):
        status = "Cancelled" if self.cancelled else ("Success" if self.success else "Failed")
        return (
            f"HistoryEntry({status}, {self.state_code or 'ALL'}, "
            f"{self.completed_count}/{self.total_count} in {self.duration:.1f}s)"
        )


class HistoryManager:
    """
    Manages generation history with persistence

    Thread-safe manager for tracking generation operations.
    Keeps last N entries and provides search/statistics.

    Example:
        >>> manager = get_history_manager()
        >>> entry = HistoryEntry(
        ...     timestamp=datetime.now(),
        ...     state_code="CA",
        ...     total_count=50,
        ...     completed_count=50,
        ...     duration=25.3
        ... )
        >>> manager.add_entry(entry)
    """

    def __init__(
        self,
        max_entries: int = 100,
        config_dir: Optional[Path] = None
    ):
        """
        Initialize history manager

        Args:
            max_entries: Maximum number of entries to keep
            config_dir: Directory for history file
        """
        self.max_entries = max_entries
        self._lock = threading.RLock()

        # History storage (deque for efficient size limiting)
        self._history: Deque[HistoryEntry] = deque(maxlen=max_entries)

        # Config directory
        if config_dir is None:
            config_dir = Path.home() / ".aamva-generator"
        self.config_dir = Path(config_dir)
        self.history_file = self.config_dir / "history.json"

        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Auto-save
        self._auto_save_enabled = True

        # Load history
        self.load()

    def add_entry(self, entry: HistoryEntry) -> bool:
        """
        Add entry to history

        Args:
            entry: History entry to add

        Returns:
            True if added successfully
        """
        with self._lock:
            try:
                self._history.append(entry)

                # Auto-save
                if self._auto_save_enabled:
                    self.save()

                # Emit event
                emit(Event(
                    EventType.HISTORY_ADDED,
                    source=self,
                    data={
                        'state_code': entry.state_code,
                        'total_count': entry.total_count,
                        'completed_count': entry.completed_count,
                        'success': entry.success
                    }
                ))

                logger.debug(f"Added history entry: {entry}")
                return True

            except Exception as e:
                logger.error(f"Failed to add history entry: {e}", exc_info=True)
                return False

    def get_entries(
        self,
        limit: Optional[int] = None,
        state_code: Optional[str] = None,
        success_only: bool = False,
        since: Optional[datetime] = None
    ) -> List[HistoryEntry]:
        """
        Get history entries with optional filtering

        Args:
            limit: Maximum number of entries to return
            state_code: Filter by state code
            success_only: Only return successful generations
            since: Only return entries after this date

        Returns:
            List of matching history entries
        """
        with self._lock:
            entries = list(self._history)

            # Apply filters
            if state_code:
                entries = [e for e in entries if e.state_code == state_code]

            if success_only:
                entries = [e for e in entries if e.success]

            if since:
                entries = [e for e in entries if e.timestamp >= since]

            # Sort by timestamp (newest first)
            entries.sort(key=lambda e: e.timestamp, reverse=True)

            # Apply limit
            if limit:
                entries = entries[:limit]

            return entries

    def get_latest(self) -> Optional[HistoryEntry]:
        """Get most recent history entry"""
        with self._lock:
            return self._history[-1] if self._history else None

    def get_entry_count(self) -> int:
        """Get total number of entries"""
        with self._lock:
            return len(self._history)

    def clear(self) -> bool:
        """
        Clear all history

        Returns:
            True if cleared successfully
        """
        with self._lock:
            try:
                self._history.clear()

                if self._auto_save_enabled:
                    self.save()

                emit(Event(EventType.HISTORY_CLEARED, source=self))

                logger.info("History cleared")
                return True

            except Exception as e:
                logger.error(f"Failed to clear history: {e}", exc_info=True)
                return False

    # Statistics

    def get_statistics(
        self,
        state_code: Optional[str] = None,
        since: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get aggregated statistics

        Args:
            state_code: Filter by state code
            since: Only include entries after this date

        Returns:
            Dictionary of statistics
        """
        with self._lock:
            entries = self.get_entries(
                state_code=state_code,
                since=since
            )

            if not entries:
                return {
                    'total_generations': 0,
                    'total_licenses': 0,
                    'successful_generations': 0,
                    'failed_generations': 0,
                    'cancelled_generations': 0,
                    'success_rate': 0.0,
                    'total_duration': 0.0,
                    'avg_duration': 0.0,
                    'avg_licenses_per_second': 0.0
                }

            total_licenses = sum(e.completed_count for e in entries)
            successful = sum(1 for e in entries if e.success)
            failed = sum(1 for e in entries if not e.success and not e.cancelled)
            cancelled = sum(1 for e in entries if e.cancelled)
            total_duration = sum(e.duration for e in entries)

            return {
                'total_generations': len(entries),
                'total_licenses': total_licenses,
                'successful_generations': successful,
                'failed_generations': failed,
                'cancelled_generations': cancelled,
                'success_rate': successful / len(entries) if entries else 0.0,
                'total_duration': total_duration,
                'avg_duration': total_duration / len(entries) if entries else 0.0,
                'avg_licenses_per_second': (
                    total_licenses / total_duration if total_duration > 0 else 0.0
                ),
                'most_common_state': self._get_most_common_state(entries),
                'fastest_generation': min(entries, key=lambda e: e.duration) if entries else None,
                'largest_batch': max(entries, key=lambda e: e.total_count) if entries else None
            }

    def _get_most_common_state(self, entries: List[HistoryEntry]) -> Optional[str]:
        """Get most commonly generated state"""
        if not entries:
            return None

        state_counts: Dict[str, int] = {}
        for entry in entries:
            if entry.state_code:
                state_counts[entry.state_code] = state_counts.get(entry.state_code, 0) + 1

        if not state_counts:
            return None

        return max(state_counts.items(), key=lambda x: x[1])[0]

    def get_state_statistics(self) -> Dict[str, Dict[str, Any]]:
        """
        Get statistics grouped by state

        Returns:
            Dictionary mapping state codes to statistics
        """
        with self._lock:
            entries = list(self._history)
            state_stats: Dict[str, List[HistoryEntry]] = {}

            # Group by state
            for entry in entries:
                if entry.state_code:
                    if entry.state_code not in state_stats:
                        state_stats[entry.state_code] = []
                    state_stats[entry.state_code].append(entry)

            # Calculate statistics for each state
            result = {}
            for state, state_entries in state_stats.items():
                total_licenses = sum(e.completed_count for e in state_entries)
                total_duration = sum(e.duration for e in state_entries)

                result[state] = {
                    'count': len(state_entries),
                    'total_licenses': total_licenses,
                    'total_duration': total_duration,
                    'avg_duration': total_duration / len(state_entries),
                    'avg_licenses': total_licenses / len(state_entries),
                    'success_rate': sum(1 for e in state_entries if e.success) / len(state_entries)
                }

            return result

    # Persistence

    def load(self) -> bool:
        """
        Load history from disk

        Returns:
            True if loaded successfully
        """
        with self._lock:
            try:
                if not self.history_file.exists():
                    logger.info("No history file found")
                    return False

                with open(self.history_file, 'r') as f:
                    data = json.load(f)

                # Clear existing history
                self._history.clear()

                # Load entries
                for entry_data in data.get('entries', []):
                    entry = HistoryEntry.from_dict(entry_data)
                    self._history.append(entry)

                emit(Event(
                    EventType.HISTORY_LOADED,
                    source=self,
                    data={'count': len(self._history)}
                ))

                logger.info(f"Loaded {len(self._history)} history entries from {self.history_file}")
                return True

            except Exception as e:
                logger.error(f"Failed to load history: {e}", exc_info=True)
                return False

    def save(self) -> bool:
        """
        Save history to disk

        Returns:
            True if saved successfully
        """
        with self._lock:
            try:
                data = {
                    'version': '1.0',
                    'max_entries': self.max_entries,
                    'entries': [entry.to_dict() for entry in self._history]
                }

                with open(self.history_file, 'w') as f:
                    json.dump(data, f, indent=2)

                logger.debug(f"Saved {len(self._history)} history entries to {self.history_file}")
                return True

            except Exception as e:
                logger.error(f"Failed to save history: {e}", exc_info=True)
                return False

    def export_to_file(self, file_path: Path) -> bool:
        """
        Export history to a file

        Args:
            file_path: Path to export to

        Returns:
            True if successful
        """
        with self._lock:
            try:
                data = {
                    'version': '1.0',
                    'exported_at': datetime.now().isoformat(),
                    'max_entries': self.max_entries,
                    'entries': [entry.to_dict() for entry in self._history]
                }

                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2)

                logger.info(f"History exported to {file_path}")
                return True

            except Exception as e:
                logger.error(f"Failed to export history: {e}", exc_info=True)
                return False

    def import_from_file(self, file_path: Path) -> bool:
        """
        Import history from a file

        Args:
            file_path: Path to import from

        Returns:
            True if successful
        """
        with self._lock:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)

                # Clear existing history
                self._history.clear()

                # Load entries
                for entry_data in data.get('entries', []):
                    entry = HistoryEntry.from_dict(entry_data)
                    self._history.append(entry)

                # Save imported history
                self.save()

                emit(Event(
                    EventType.HISTORY_LOADED,
                    source=self,
                    data={'count': len(self._history)}
                ))

                logger.info(f"History imported from {file_path}")
                return True

            except Exception as e:
                logger.error(f"Failed to import history: {e}", exc_info=True)
                return False

    # Auto-save control

    def enable_auto_save(self):
        """Enable automatic saving"""
        self._auto_save_enabled = True
        logger.info("History auto-save enabled")

    def disable_auto_save(self):
        """Disable automatic saving"""
        self._auto_save_enabled = False
        logger.info("History auto-save disabled")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        with self._lock:
            return {
                'max_entries': self.max_entries,
                'entry_count': len(self._history),
                'entries': [entry.to_dict() for entry in self._history]
            }

    def __str__(self):
        return f"HistoryManager({len(self._history)} entries, max={self.max_entries})"


# Global history manager instance
_history_manager: Optional[HistoryManager] = None
_history_lock = threading.Lock()


def get_history_manager() -> HistoryManager:
    """
    Get the global history manager instance (singleton)

    Returns:
        Global HistoryManager instance
    """
    global _history_manager

    if _history_manager is None:
        with _history_lock:
            if _history_manager is None:
                _history_manager = HistoryManager()

    return _history_manager


def initialize_history_manager(
    max_entries: int = 100,
    config_dir: Optional[Path] = None
) -> HistoryManager:
    """
    Initialize history manager with custom settings

    Args:
        max_entries: Maximum number of entries to keep
        config_dir: Custom configuration directory

    Returns:
        Initialized HistoryManager instance
    """
    global _history_manager

    with _history_lock:
        _history_manager = HistoryManager(max_entries, config_dir)
        return _history_manager
