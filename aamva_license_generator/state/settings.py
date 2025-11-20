"""
Settings Management

Handles user settings and preferences with automatic persistence.

Features:
- JSON-based persistence
- Type-safe settings access
- Default values
- Auto-save on changes
- Thread-safe operations
- Settings validation
"""

import json
import os
import threading
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import logging

from ..events import Event, EventType, emit

logger = logging.getLogger(__name__)


@dataclass
class WindowSettings:
    """GUI window settings"""
    width: int = 1200
    height: int = 800
    x: Optional[int] = None
    y: Optional[int] = None
    maximized: bool = False


@dataclass
class GenerationDefaults:
    """Default values for license generation"""
    state_code: str = "CA"
    quantity: int = 10
    output_directory: str = "./output"
    generate_pdf: bool = True
    generate_docx: bool = True
    generate_odt: bool = False
    generate_images: bool = True
    dpi: int = 300
    all_states: bool = False


@dataclass
class UIPreferences:
    """UI behavior preferences"""
    theme: str = "dark"  # "dark", "light", "system"
    color_scheme: str = "blue"  # "blue", "green", "dark-blue"
    show_tooltips: bool = True
    show_progress_details: bool = True
    confirm_before_generate: bool = False
    confirm_before_quit: bool = True
    auto_open_output: bool = False
    remember_window_position: bool = True


@dataclass
class AdvancedSettings:
    """Advanced application settings"""
    auto_save_interval: int = 30  # seconds
    max_history_entries: int = 100
    max_undo_stack: int = 50
    enable_logging: bool = True
    log_level: str = "INFO"
    check_updates: bool = True
    send_analytics: bool = False


class Settings:
    """
    Manages application settings with automatic persistence

    Thread-safe singleton that handles all application preferences.

    Example:
        >>> settings = get_settings()
        >>> settings.generation.state_code = "NY"
        >>> settings.save()  # Auto-saved
    """

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize settings

        Args:
            config_dir: Directory to store config files (default: ~/.aamva-generator)
        """
        # Config directory
        if config_dir is None:
            config_dir = Path.home() / ".aamva-generator"
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "settings.json"

        # Thread safety
        self._lock = threading.RLock()

        # Auto-save
        self._auto_save_enabled = True
        self._auto_save_timer: Optional[threading.Timer] = None

        # Settings groups
        self.window = WindowSettings()
        self.generation = GenerationDefaults()
        self.ui = UIPreferences()
        self.advanced = AdvancedSettings()

        # Recent items
        self.recent_output_dirs: List[str] = []
        self.recent_states: List[str] = ["CA", "NY", "TX", "FL"]

        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Load settings
        self.load()

    def _schedule_auto_save(self):
        """Schedule automatic save"""
        if not self._auto_save_enabled:
            return

        # Cancel existing timer
        if self._auto_save_timer:
            self._auto_save_timer.cancel()

        # Schedule new save
        self._auto_save_timer = threading.Timer(
            self.advanced.auto_save_interval,
            self._auto_save_callback
        )
        self._auto_save_timer.daemon = True
        self._auto_save_timer.start()

    def _auto_save_callback(self):
        """Auto-save callback"""
        try:
            self.save()
            logger.debug("Settings auto-saved")
        except Exception as e:
            logger.error(f"Auto-save failed: {e}", exc_info=True)

    def load(self) -> bool:
        """
        Load settings from disk

        Returns:
            True if loaded successfully, False otherwise
        """
        with self._lock:
            try:
                if not self.config_file.exists():
                    logger.info("No settings file found, using defaults")
                    return False

                with open(self.config_file, 'r') as f:
                    data = json.load(f)

                # Load settings groups
                if 'window' in data:
                    self.window = WindowSettings(**data['window'])
                if 'generation' in data:
                    self.generation = GenerationDefaults(**data['generation'])
                if 'ui' in data:
                    self.ui = UIPreferences(**data['ui'])
                if 'advanced' in data:
                    self.advanced = AdvancedSettings(**data['advanced'])

                # Load recent items
                self.recent_output_dirs = data.get('recent_output_dirs', [])
                self.recent_states = data.get('recent_states', ["CA", "NY", "TX", "FL"])

                # Emit event
                emit(Event(
                    EventType.SETTINGS_LOADED,
                    source=self,
                    data={'config_file': str(self.config_file)}
                ))

                logger.info(f"Settings loaded from {self.config_file}")
                return True

            except Exception as e:
                logger.error(f"Failed to load settings: {e}", exc_info=True)
                return False

    def save(self) -> bool:
        """
        Save settings to disk

        Returns:
            True if saved successfully, False otherwise
        """
        with self._lock:
            try:
                # Build data dictionary
                data = {
                    'window': asdict(self.window),
                    'generation': asdict(self.generation),
                    'ui': asdict(self.ui),
                    'advanced': asdict(self.advanced),
                    'recent_output_dirs': self.recent_output_dirs,
                    'recent_states': self.recent_states,
                }

                # Write to file
                with open(self.config_file, 'w') as f:
                    json.dump(data, f, indent=2)

                # Emit event
                emit(Event(
                    EventType.SETTINGS_SAVED,
                    source=self,
                    data={'config_file': str(self.config_file)}
                ))

                logger.debug(f"Settings saved to {self.config_file}")
                return True

            except Exception as e:
                logger.error(f"Failed to save settings: {e}", exc_info=True)
                return False

    def reset(self):
        """Reset all settings to defaults"""
        with self._lock:
            self.window = WindowSettings()
            self.generation = GenerationDefaults()
            self.ui = UIPreferences()
            self.advanced = AdvancedSettings()
            self.recent_output_dirs = []
            self.recent_states = ["CA", "NY", "TX", "FL"]

            self.save()

            emit(Event(EventType.SETTINGS_CHANGED, source=self))
            logger.info("Settings reset to defaults")

    # Window settings helpers

    def get_window_geometry(self) -> Tuple[int, int, Optional[int], Optional[int]]:
        """
        Get window geometry

        Returns:
            Tuple of (width, height, x, y)
        """
        with self._lock:
            return (
                self.window.width,
                self.window.height,
                self.window.x,
                self.window.y
            )

    def set_window_geometry(
        self,
        width: int,
        height: int,
        x: Optional[int] = None,
        y: Optional[int] = None
    ):
        """Set window geometry"""
        with self._lock:
            self.window.width = width
            self.window.height = height
            self.window.x = x
            self.window.y = y
            self._schedule_auto_save()

    def get_window_maximized(self) -> bool:
        """Check if window should be maximized"""
        return self.window.maximized

    def set_window_maximized(self, maximized: bool):
        """Set window maximized state"""
        with self._lock:
            self.window.maximized = maximized
            self._schedule_auto_save()

    # Recent items helpers

    def add_recent_output_dir(self, directory: str):
        """
        Add directory to recent outputs list

        Args:
            directory: Directory path to add
        """
        with self._lock:
            # Remove if already exists
            if directory in self.recent_output_dirs:
                self.recent_output_dirs.remove(directory)

            # Add to front
            self.recent_output_dirs.insert(0, directory)

            # Keep only last 10
            self.recent_output_dirs = self.recent_output_dirs[:10]

            self._schedule_auto_save()

    def get_recent_output_dirs(self) -> List[str]:
        """Get list of recent output directories"""
        with self._lock:
            # Filter out non-existent directories
            return [d for d in self.recent_output_dirs if os.path.exists(d)]

    def add_recent_state(self, state_code: str):
        """
        Add state code to recent states list

        Args:
            state_code: State code to add
        """
        with self._lock:
            # Remove if already exists
            if state_code in self.recent_states:
                self.recent_states.remove(state_code)

            # Add to front
            self.recent_states.insert(0, state_code)

            # Keep only last 10
            self.recent_states = self.recent_states[:10]

            self._schedule_auto_save()

    def get_recent_states(self) -> List[str]:
        """Get list of recent state codes"""
        with self._lock:
            return self.recent_states.copy()

    # Settings change notification

    def notify_changed(self):
        """Notify that settings have changed"""
        emit(Event(EventType.SETTINGS_CHANGED, source=self))
        self._schedule_auto_save()

    # Auto-save control

    def enable_auto_save(self):
        """Enable automatic saving"""
        with self._lock:
            self._auto_save_enabled = True
            self._schedule_auto_save()
            logger.info("Auto-save enabled")

    def disable_auto_save(self):
        """Disable automatic saving"""
        with self._lock:
            self._auto_save_enabled = False
            if self._auto_save_timer:
                self._auto_save_timer.cancel()
                self._auto_save_timer = None
            logger.info("Auto-save disabled")

    def is_auto_save_enabled(self) -> bool:
        """Check if auto-save is enabled"""
        return self._auto_save_enabled

    # Export/Import

    def export_to_file(self, file_path: Path) -> bool:
        """
        Export settings to a file

        Args:
            file_path: Path to export to

        Returns:
            True if successful
        """
        with self._lock:
            try:
                data = {
                    'window': asdict(self.window),
                    'generation': asdict(self.generation),
                    'ui': asdict(self.ui),
                    'advanced': asdict(self.advanced),
                    'recent_output_dirs': self.recent_output_dirs,
                    'recent_states': self.recent_states,
                }

                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2)

                logger.info(f"Settings exported to {file_path}")
                return True

            except Exception as e:
                logger.error(f"Failed to export settings: {e}", exc_info=True)
                return False

    def import_from_file(self, file_path: Path) -> bool:
        """
        Import settings from a file

        Args:
            file_path: Path to import from

        Returns:
            True if successful
        """
        with self._lock:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)

                # Load settings groups
                if 'window' in data:
                    self.window = WindowSettings(**data['window'])
                if 'generation' in data:
                    self.generation = GenerationDefaults(**data['generation'])
                if 'ui' in data:
                    self.ui = UIPreferences(**data['ui'])
                if 'advanced' in data:
                    self.advanced = AdvancedSettings(**data['advanced'])

                # Load recent items
                self.recent_output_dirs = data.get('recent_output_dirs', [])
                self.recent_states = data.get('recent_states', [])

                # Save imported settings
                self.save()

                emit(Event(EventType.SETTINGS_LOADED, source=self))
                logger.info(f"Settings imported from {file_path}")
                return True

            except Exception as e:
                logger.error(f"Failed to import settings: {e}", exc_info=True)
                return False

    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary"""
        with self._lock:
            return {
                'window': asdict(self.window),
                'generation': asdict(self.generation),
                'ui': asdict(self.ui),
                'advanced': asdict(self.advanced),
                'recent_output_dirs': self.recent_output_dirs,
                'recent_states': self.recent_states,
            }

    def __str__(self):
        return f"Settings(config_file={self.config_file})"


# Global settings instance
_settings: Optional[Settings] = None
_settings_lock = threading.Lock()


def get_settings() -> Settings:
    """
    Get the global settings instance (singleton)

    Returns:
        Global Settings instance
    """
    global _settings

    if _settings is None:
        with _settings_lock:
            if _settings is None:
                _settings = Settings()

    return _settings


def initialize_settings(config_dir: Optional[Path] = None) -> Settings:
    """
    Initialize settings with custom config directory

    Args:
        config_dir: Custom configuration directory

    Returns:
        Initialized Settings instance
    """
    global _settings

    with _settings_lock:
        _settings = Settings(config_dir)
        return _settings
