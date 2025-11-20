"""
Global Application State

Central state management for the AAMVA License Generator application.

Features:
- Observable state pattern
- Draft system for unsaved work
- Configuration persistence
- Thread-safe operations
- Integrated with event bus and command history
"""

import json
import threading
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import logging

from ..events import Event, EventType, emit
from ..commands import Command, FunctionCommand, get_command_history
from .generation_state import GenerationState
from .history_manager import HistoryEntry, get_history_manager
from .settings import get_settings

logger = logging.getLogger(__name__)


@dataclass
class GenerationConfig:
    """Configuration for license generation"""
    state_code: Optional[str] = "CA"    # State code or None for all states
    quantity: int = 10                   # Number of licenses to generate
    output_directory: str = "./output"   # Output directory path
    generate_pdf: bool = True            # Generate PDF output
    generate_docx: bool = True           # Generate DOCX output
    generate_odt: bool = False           # Generate ODT output
    generate_images: bool = True         # Generate individual images
    dpi: int = 300                       # Image DPI
    all_states: bool = False             # Generate for all states

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GenerationConfig':
        """Create from dictionary"""
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})

    def validate(self) -> List[str]:
        """
        Validate configuration

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Validate quantity
        if self.quantity < 1:
            errors.append("Quantity must be at least 1")
        if self.quantity > 10000:
            errors.append("Quantity cannot exceed 10,000")

        # Validate state code
        if not self.all_states and not self.state_code:
            errors.append("State code is required")

        # Validate output directory
        if not self.output_directory:
            errors.append("Output directory is required")

        # Validate at least one output format
        if not any([
            self.generate_pdf,
            self.generate_docx,
            self.generate_odt,
            self.generate_images
        ]):
            errors.append("At least one output format must be selected")

        # Validate DPI
        if self.dpi < 72 or self.dpi > 600:
            errors.append("DPI must be between 72 and 600")

        return errors

    def is_valid(self) -> bool:
        """Check if configuration is valid"""
        return len(self.validate()) == 0

    def __str__(self):
        state = "ALL" if self.all_states else (self.state_code or "UNKNOWN")
        return f"GenerationConfig({state}, {self.quantity} licenses)"


@dataclass
class Draft:
    """
    Draft configuration for resuming work

    Represents saved work-in-progress configuration.
    """
    name: str                               # Draft name
    config: GenerationConfig                # Generation configuration
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    description: str = ""                   # Optional description

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'config': self.config.to_dict(),
            'created_at': self.created_at.isoformat(),
            'modified_at': self.modified_at.isoformat(),
            'description': self.description
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Draft':
        """Create from dictionary"""
        return cls(
            name=data['name'],
            config=GenerationConfig.from_dict(data['config']),
            created_at=datetime.fromisoformat(data['created_at']),
            modified_at=datetime.fromisoformat(data['modified_at']),
            description=data.get('description', '')
        )

    def __str__(self):
        return f"Draft({self.name}, {self.config})"


class AppState:
    """
    Global application state manager

    Central state management with observable pattern, command integration,
    and automatic persistence.

    Example:
        >>> state = get_app_state()
        >>> state.set_state_code("NY")  # Creates undo command
        >>> state.set_quantity(50)
        >>> state.save_draft("my_config")
    """

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize application state

        Args:
            config_dir: Directory for state files
        """
        # Config directory
        if config_dir is None:
            config_dir = Path.home() / ".aamva-generator"
        self.config_dir = Path(config_dir)
        self.state_file = self.config_dir / "state.json"
        self.drafts_file = self.config_dir / "drafts.json"

        # Thread safety
        self._lock = threading.RLock()

        # Current configuration
        self.config = GenerationConfig()

        # Generation state (current operation)
        self.current_generation: Optional[GenerationState] = None

        # Drafts
        self.drafts: Dict[str, Draft] = {}

        # Auto-save
        self._auto_save_enabled = True
        self._auto_save_timer: Optional[threading.Timer] = None
        self._dirty = False  # Track unsaved changes

        # Integrations
        self.settings = get_settings()
        self.history = get_history_manager()
        self.commands = get_command_history()

        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Load state
        self.load()
        self._load_drafts()

    # Configuration management

    def set_state_code(self, state_code: Optional[str], create_command: bool = True):
        """
        Set state code

        Args:
            state_code: State code (e.g., "CA") or None for all states
            create_command: Whether to create undo command
        """
        with self._lock:
            old_value = self.config.state_code

            if old_value == state_code:
                return  # No change

            # Create undo command
            if create_command:
                cmd = FunctionCommand(
                    execute_fn=lambda: self._set_state_code_internal(state_code),
                    undo_fn=lambda: self._set_state_code_internal(old_value),
                    description=f"Change state to {state_code or 'ALL'}"
                )
                self.commands.execute(cmd)
            else:
                self._set_state_code_internal(state_code)

    def _set_state_code_internal(self, state_code: Optional[str]) -> bool:
        """Internal state code setter (no command)"""
        self.config.state_code = state_code
        self._mark_dirty()
        self._notify_change('state_code', state_code)
        return True

    def set_quantity(self, quantity: int, create_command: bool = True):
        """
        Set quantity

        Args:
            quantity: Number of licenses to generate
            create_command: Whether to create undo command
        """
        with self._lock:
            old_value = self.config.quantity

            if old_value == quantity:
                return  # No change

            # Create undo command
            if create_command:
                cmd = FunctionCommand(
                    execute_fn=lambda: self._set_quantity_internal(quantity),
                    undo_fn=lambda: self._set_quantity_internal(old_value),
                    description=f"Change quantity to {quantity}"
                )
                self.commands.execute(cmd)
            else:
                self._set_quantity_internal(quantity)

    def _set_quantity_internal(self, quantity: int) -> bool:
        """Internal quantity setter (no command)"""
        self.config.quantity = quantity
        self._mark_dirty()
        self._notify_change('quantity', quantity)
        return True

    def set_output_directory(self, directory: str, create_command: bool = True):
        """
        Set output directory

        Args:
            directory: Output directory path
            create_command: Whether to create undo command
        """
        with self._lock:
            old_value = self.config.output_directory

            if old_value == directory:
                return  # No change

            # Create undo command
            if create_command:
                cmd = FunctionCommand(
                    execute_fn=lambda: self._set_output_directory_internal(directory),
                    undo_fn=lambda: self._set_output_directory_internal(old_value),
                    description=f"Change output directory to {directory}"
                )
                self.commands.execute(cmd)
            else:
                self._set_output_directory_internal(directory)

    def _set_output_directory_internal(self, directory: str) -> bool:
        """Internal output directory setter (no command)"""
        self.config.output_directory = directory
        self._mark_dirty()
        self._notify_change('output_directory', directory)
        return True

    def set_format_flags(
        self,
        pdf: Optional[bool] = None,
        docx: Optional[bool] = None,
        odt: Optional[bool] = None,
        images: Optional[bool] = None,
        create_command: bool = True
    ):
        """
        Set output format flags

        Args:
            pdf: Generate PDF
            docx: Generate DOCX
            odt: Generate ODT
            images: Generate images
            create_command: Whether to create undo command
        """
        with self._lock:
            old_values = (
                self.config.generate_pdf,
                self.config.generate_docx,
                self.config.generate_odt,
                self.config.generate_images
            )

            new_values = (
                pdf if pdf is not None else old_values[0],
                docx if docx is not None else old_values[1],
                odt if odt is not None else old_values[2],
                images if images is not None else old_values[3]
            )

            if old_values == new_values:
                return  # No change

            # Create undo command
            if create_command:
                cmd = FunctionCommand(
                    execute_fn=lambda: self._set_format_flags_internal(*new_values),
                    undo_fn=lambda: self._set_format_flags_internal(*old_values),
                    description="Change output formats"
                )
                self.commands.execute(cmd)
            else:
                self._set_format_flags_internal(*new_values)

    def _set_format_flags_internal(
        self,
        pdf: bool,
        docx: bool,
        odt: bool,
        images: bool
    ) -> bool:
        """Internal format flags setter (no command)"""
        self.config.generate_pdf = pdf
        self.config.generate_docx = docx
        self.config.generate_odt = odt
        self.config.generate_images = images
        self._mark_dirty()
        self._notify_change('format_flags', {
            'pdf': pdf, 'docx': docx, 'odt': odt, 'images': images
        })
        return True

    def set_all_states(self, all_states: bool, create_command: bool = True):
        """
        Set all states flag

        Args:
            all_states: Generate for all states
            create_command: Whether to create undo command
        """
        with self._lock:
            old_value = self.config.all_states

            if old_value == all_states:
                return  # No change

            # Create undo command
            if create_command:
                cmd = FunctionCommand(
                    execute_fn=lambda: self._set_all_states_internal(all_states),
                    undo_fn=lambda: self._set_all_states_internal(old_value),
                    description=f"Set all states to {all_states}"
                )
                self.commands.execute(cmd)
            else:
                self._set_all_states_internal(all_states)

    def _set_all_states_internal(self, all_states: bool) -> bool:
        """Internal all states setter (no command)"""
        self.config.all_states = all_states
        self._mark_dirty()
        self._notify_change('all_states', all_states)
        return True

    def get_config(self) -> GenerationConfig:
        """Get current configuration (copy)"""
        with self._lock:
            return GenerationConfig(
                state_code=self.config.state_code,
                quantity=self.config.quantity,
                output_directory=self.config.output_directory,
                generate_pdf=self.config.generate_pdf,
                generate_docx=self.config.generate_docx,
                generate_odt=self.config.generate_odt,
                generate_images=self.config.generate_images,
                dpi=self.config.dpi,
                all_states=self.config.all_states
            )

    def set_config(self, config: GenerationConfig, create_command: bool = True):
        """
        Set entire configuration

        Args:
            config: New configuration
            create_command: Whether to create undo command
        """
        with self._lock:
            old_config = self.get_config()

            # Create undo command
            if create_command:
                cmd = FunctionCommand(
                    execute_fn=lambda: self._set_config_internal(config),
                    undo_fn=lambda: self._set_config_internal(old_config),
                    description="Change configuration"
                )
                self.commands.execute(cmd)
            else:
                self._set_config_internal(config)

    def _set_config_internal(self, config: GenerationConfig) -> bool:
        """Internal config setter (no command)"""
        self.config = GenerationConfig(
            state_code=config.state_code,
            quantity=config.quantity,
            output_directory=config.output_directory,
            generate_pdf=config.generate_pdf,
            generate_docx=config.generate_docx,
            generate_odt=config.generate_odt,
            generate_images=config.generate_images,
            dpi=config.dpi,
            all_states=config.all_states
        )
        self._mark_dirty()
        self._notify_change('config', config.to_dict())
        return True

    # Generation state management

    def start_generation(self) -> GenerationState:
        """
        Start a new generation operation

        Returns:
            New GenerationState instance
        """
        with self._lock:
            self.current_generation = GenerationState(self.config.quantity)
            self.current_generation.output_directory = self.config.output_directory
            self.current_generation.start()
            return self.current_generation

    def get_generation_state(self) -> Optional[GenerationState]:
        """Get current generation state"""
        return self.current_generation

    def complete_generation(self, success: bool, error: Optional[str] = None):
        """
        Complete current generation

        Args:
            success: Whether generation succeeded
            error: Error message if failed
        """
        with self._lock:
            if not self.current_generation:
                return

            gen = self.current_generation

            # Complete the generation state
            if success:
                gen.complete()
            else:
                gen.fail(error or "Unknown error")

            # Add to history
            entry = HistoryEntry(
                timestamp=datetime.now(),
                state_code=self.config.state_code,
                total_count=gen.total_count,
                completed_count=gen.completed_count,
                failed_count=gen.failed_count,
                skipped_count=gen.skipped_count,
                duration=gen.duration,
                output_directory=gen.output_directory or self.config.output_directory,
                output_files=gen.output_files,
                formats=[],  # TODO: Track actual formats
                success=success,
                error=error,
                cancelled=gen.cancelled
            )
            self.history.add_entry(entry)

            # Clear current generation
            self.current_generation = None

    # Draft system

    def save_draft(self, name: str, description: str = "") -> bool:
        """
        Save current configuration as a draft

        Args:
            name: Draft name
            description: Optional description

        Returns:
            True if saved successfully
        """
        with self._lock:
            try:
                # Create or update draft
                if name in self.drafts:
                    draft = self.drafts[name]
                    draft.config = self.get_config()
                    draft.modified_at = datetime.now()
                    draft.description = description
                else:
                    draft = Draft(
                        name=name,
                        config=self.get_config(),
                        description=description
                    )
                    self.drafts[name] = draft

                # Save drafts
                self._save_drafts()

                emit(Event(
                    EventType.DRAFT_SAVED,
                    source=self,
                    data={'name': name}
                ))

                logger.info(f"Draft saved: {name}")
                return True

            except Exception as e:
                logger.error(f"Failed to save draft: {e}", exc_info=True)
                return False

    def load_draft(self, name: str) -> bool:
        """
        Load a draft

        Args:
            name: Draft name

        Returns:
            True if loaded successfully
        """
        with self._lock:
            if name not in self.drafts:
                logger.warning(f"Draft not found: {name}")
                return False

            try:
                draft = self.drafts[name]
                self.set_config(draft.config, create_command=True)

                emit(Event(
                    EventType.DRAFT_LOADED,
                    source=self,
                    data={'name': name}
                ))

                logger.info(f"Draft loaded: {name}")
                return True

            except Exception as e:
                logger.error(f"Failed to load draft: {e}", exc_info=True)
                return False

    def delete_draft(self, name: str) -> bool:
        """
        Delete a draft

        Args:
            name: Draft name

        Returns:
            True if deleted successfully
        """
        with self._lock:
            if name not in self.drafts:
                return False

            try:
                del self.drafts[name]
                self._save_drafts()

                emit(Event(
                    EventType.DRAFT_DELETED,
                    source=self,
                    data={'name': name}
                ))

                logger.info(f"Draft deleted: {name}")
                return True

            except Exception as e:
                logger.error(f"Failed to delete draft: {e}", exc_info=True)
                return False

    def get_drafts(self) -> List[Draft]:
        """Get all drafts"""
        with self._lock:
            return list(self.drafts.values())

    def get_draft_names(self) -> List[str]:
        """Get all draft names"""
        with self._lock:
            return list(self.drafts.keys())

    # Persistence

    def load(self) -> bool:
        """Load state from disk"""
        with self._lock:
            try:
                if not self.state_file.exists():
                    logger.info("No state file found, using defaults")
                    return False

                with open(self.state_file, 'r') as f:
                    data = json.load(f)

                # Load configuration
                if 'config' in data:
                    self.config = GenerationConfig.from_dict(data['config'])

                emit(Event(EventType.STATE_LOADED, source=self))

                logger.info(f"State loaded from {self.state_file}")
                return True

            except Exception as e:
                logger.error(f"Failed to load state: {e}", exc_info=True)
                return False

    def save(self) -> bool:
        """Save state to disk"""
        with self._lock:
            try:
                data = {
                    'version': '1.0',
                    'config': self.config.to_dict(),
                    'saved_at': datetime.now().isoformat()
                }

                with open(self.state_file, 'w') as f:
                    json.dump(data, f, indent=2)

                self._dirty = False

                emit(Event(EventType.STATE_SAVED, source=self))

                logger.debug(f"State saved to {self.state_file}")
                return True

            except Exception as e:
                logger.error(f"Failed to save state: {e}", exc_info=True)
                return False

    def _load_drafts(self) -> bool:
        """Load drafts from disk"""
        with self._lock:
            try:
                if not self.drafts_file.exists():
                    return False

                with open(self.drafts_file, 'r') as f:
                    data = json.load(f)

                self.drafts = {
                    name: Draft.from_dict(draft_data)
                    for name, draft_data in data.get('drafts', {}).items()
                }

                logger.info(f"Loaded {len(self.drafts)} drafts")
                return True

            except Exception as e:
                logger.error(f"Failed to load drafts: {e}", exc_info=True)
                return False

    def _save_drafts(self) -> bool:
        """Save drafts to disk"""
        with self._lock:
            try:
                data = {
                    'version': '1.0',
                    'drafts': {
                        name: draft.to_dict()
                        for name, draft in self.drafts.items()
                    }
                }

                with open(self.drafts_file, 'w') as f:
                    json.dump(data, f, indent=2)

                logger.debug(f"Saved {len(self.drafts)} drafts")
                return True

            except Exception as e:
                logger.error(f"Failed to save drafts: {e}", exc_info=True)
                return False

    # Auto-save

    def _mark_dirty(self):
        """Mark state as dirty (unsaved changes)"""
        self._dirty = True
        self._schedule_auto_save()

    def _schedule_auto_save(self):
        """Schedule automatic save"""
        if not self._auto_save_enabled:
            return

        # Cancel existing timer
        if self._auto_save_timer:
            self._auto_save_timer.cancel()

        # Schedule new save
        self._auto_save_timer = threading.Timer(
            self.settings.advanced.auto_save_interval,
            self._auto_save_callback
        )
        self._auto_save_timer.daemon = True
        self._auto_save_timer.start()

    def _auto_save_callback(self):
        """Auto-save callback"""
        if self._dirty:
            self.save()

    def enable_auto_save(self):
        """Enable automatic saving"""
        self._auto_save_enabled = True

    def disable_auto_save(self):
        """Disable automatic saving"""
        self._auto_save_enabled = False
        if self._auto_save_timer:
            self._auto_save_timer.cancel()

    # Change notification

    def _notify_change(self, field: str, value: Any):
        """Notify about state change"""
        emit(Event(
            EventType.STATE_CHANGED,
            source=self,
            data={'field': field, 'value': value}
        ))

    # Utility methods

    def reset(self):
        """Reset to default configuration"""
        with self._lock:
            self.config = GenerationConfig()
            self.save()
            emit(Event(EventType.STATE_RESET, source=self))
            logger.info("State reset to defaults")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        with self._lock:
            return {
                'config': self.config.to_dict(),
                'drafts': [draft.to_dict() for draft in self.drafts.values()],
                'has_unsaved_changes': self._dirty
            }

    def __str__(self):
        return f"AppState({self.config})"


# Global app state instance
_app_state: Optional[AppState] = None
_app_state_lock = threading.Lock()


def get_app_state() -> AppState:
    """
    Get the global app state instance (singleton)

    Returns:
        Global AppState instance
    """
    global _app_state

    if _app_state is None:
        with _app_state_lock:
            if _app_state is None:
                _app_state = AppState()

    return _app_state


def initialize_app_state(config_dir: Optional[Path] = None) -> AppState:
    """
    Initialize app state with custom config directory

    Args:
        config_dir: Custom configuration directory

    Returns:
        Initialized AppState instance
    """
    global _app_state

    with _app_state_lock:
        _app_state = AppState(config_dir)
        return _app_state
