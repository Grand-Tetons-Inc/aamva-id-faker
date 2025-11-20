"""
State Management Package

Provides comprehensive state management for the AAMVA License Generator GUI.

Modules:
- app_state: Global application state
- generation_state: License generation state tracking
- history_manager: Generation history management
- settings: User settings and preferences

Features:
- Observable state pattern
- Thread-safe operations
- Automatic persistence
- Change notifications via event bus
"""

from .app_state import AppState, get_app_state
from .generation_state import (
    GenerationState,
    GenerationStatus,
    LicenseGenerationItem
)
from .history_manager import (
    HistoryManager,
    HistoryEntry,
    get_history_manager
)
from .settings import Settings, get_settings

__all__ = [
    # App State
    'AppState',
    'get_app_state',

    # Generation State
    'GenerationState',
    'GenerationStatus',
    'LicenseGenerationItem',

    # History
    'HistoryManager',
    'HistoryEntry',
    'get_history_manager',

    # Settings
    'Settings',
    'get_settings',
]
