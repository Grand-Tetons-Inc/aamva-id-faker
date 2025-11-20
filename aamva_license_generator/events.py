"""
Event System for State Changes

Provides a robust observer pattern implementation for state change notifications.
Thread-safe, efficient, and decoupled from business logic.

Features:
- Type-safe event system
- Weak references to prevent memory leaks
- Priority-based event handlers
- Event filtering and batching
- Thread-safe event dispatch
- Async event support
"""

import threading
import weakref
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Set
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class EventPriority(Enum):
    """Event handler priority levels"""
    CRITICAL = 0    # Execute first (logging, error handling)
    HIGH = 1        # Important operations (validation)
    NORMAL = 2      # Standard operations (UI updates)
    LOW = 3         # Optional operations (analytics)


class EventType(Enum):
    """Standard event types for the application"""
    # Application lifecycle
    APP_STARTED = auto()
    APP_SHUTDOWN = auto()

    # State changes
    STATE_CHANGED = auto()
    STATE_LOADED = auto()
    STATE_SAVED = auto()
    STATE_RESET = auto()

    # Generation events
    GENERATION_STARTED = auto()
    GENERATION_PROGRESS = auto()
    GENERATION_COMPLETED = auto()
    GENERATION_FAILED = auto()
    GENERATION_CANCELLED = auto()

    # License events
    LICENSE_CREATED = auto()
    LICENSE_FAILED = auto()

    # Settings events
    SETTINGS_CHANGED = auto()
    SETTINGS_LOADED = auto()
    SETTINGS_SAVED = auto()

    # History events
    HISTORY_ADDED = auto()
    HISTORY_CLEARED = auto()
    HISTORY_LOADED = auto()

    # Command events (undo/redo)
    COMMAND_EXECUTED = auto()
    COMMAND_UNDONE = auto()
    COMMAND_REDONE = auto()

    # Draft events
    DRAFT_SAVED = auto()
    DRAFT_LOADED = auto()
    DRAFT_DELETED = auto()

    # Error events
    ERROR_OCCURRED = auto()
    WARNING_OCCURRED = auto()

    # Custom events
    CUSTOM = auto()


@dataclass
class Event:
    """
    Immutable event object containing event data

    Attributes:
        event_type: Type of event
        source: Object that triggered the event
        data: Additional event data
        timestamp: When the event occurred
        priority: Event priority level
    """
    event_type: EventType
    source: Any
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    priority: EventPriority = EventPriority.NORMAL

    def __str__(self):
        return f"Event({self.event_type.name}, source={type(self.source).__name__}, data={self.data})"


class EventHandler:
    """
    Wrapper for event handler callbacks with metadata

    Uses weak references to prevent memory leaks when handlers are deleted.
    """

    def __init__(
        self,
        callback: Callable[[Event], None],
        priority: EventPriority = EventPriority.NORMAL,
        filters: Optional[Dict[str, Any]] = None,
        once: bool = False
    ):
        """
        Initialize event handler

        Args:
            callback: Function to call when event occurs
            priority: Handler priority (lower executes first)
            filters: Optional filters (e.g., {'source_type': 'AppState'})
            once: If True, handler is removed after first execution
        """
        # Use weak reference if callback is a method
        if hasattr(callback, '__self__'):
            self._callback_ref = weakref.WeakMethod(callback)
        else:
            self._callback_ref = weakref.ref(callback)

        self.priority = priority
        self.filters = filters or {}
        self.once = once
        self.call_count = 0
        self.last_called = None

    def matches_filters(self, event: Event) -> bool:
        """Check if event matches handler filters"""
        if not self.filters:
            return True

        for key, value in self.filters.items():
            if key == 'source_type':
                if not isinstance(event.source, value):
                    return False
            elif key in event.data:
                if event.data[key] != value:
                    return False
            else:
                return False

        return True

    def __call__(self, event: Event) -> bool:
        """
        Execute handler callback

        Returns:
            True if handler should be kept, False if it should be removed
        """
        callback = self._callback_ref()

        # Handler was garbage collected
        if callback is None:
            return False

        # Check filters
        if not self.matches_filters(event):
            return True

        try:
            callback(event)
            self.call_count += 1
            self.last_called = datetime.now()

            # Remove if 'once' handler
            return not self.once

        except Exception as e:
            logger.error(f"Error in event handler: {e}", exc_info=True)
            return True  # Keep handler even on error

    def __eq__(self, other):
        if not isinstance(other, EventHandler):
            return False
        return self._callback_ref() == other._callback_ref()

    def __hash__(self):
        callback = self._callback_ref()
        return hash(callback) if callback else 0


class EventBus:
    """
    Thread-safe event bus for application-wide event handling

    Features:
    - Subscribe/unsubscribe to events
    - Priority-based handler execution
    - Event filtering
    - Batch event emission
    - Thread-safe operations
    - Weak references to prevent memory leaks

    Example:
        >>> bus = EventBus()
        >>> def handler(event):
        ...     print(f"Received: {event}")
        >>> bus.subscribe(EventType.STATE_CHANGED, handler)
        >>> bus.emit(Event(EventType.STATE_CHANGED, source=self))
    """

    def __init__(self):
        self._handlers: Dict[EventType, List[EventHandler]] = defaultdict(list)
        self._lock = threading.RLock()
        self._enabled = True
        self._event_queue: List[Event] = []
        self._batching = False

        # Statistics
        self._event_counts: Dict[EventType, int] = defaultdict(int)
        self._total_events = 0

    def subscribe(
        self,
        event_type: EventType,
        callback: Callable[[Event], None],
        priority: EventPriority = EventPriority.NORMAL,
        filters: Optional[Dict[str, Any]] = None,
        once: bool = False
    ) -> EventHandler:
        """
        Subscribe to an event type

        Args:
            event_type: Type of event to subscribe to
            callback: Function to call when event occurs
            priority: Handler priority
            filters: Optional filters
            once: Remove handler after first execution

        Returns:
            EventHandler that can be used to unsubscribe
        """
        with self._lock:
            handler = EventHandler(callback, priority, filters, once)
            self._handlers[event_type].append(handler)

            # Sort by priority (lower priority number = higher priority)
            self._handlers[event_type].sort(key=lambda h: h.priority.value)

            logger.debug(f"Subscribed to {event_type.name}: {callback}")
            return handler

    def subscribe_once(
        self,
        event_type: EventType,
        callback: Callable[[Event], None],
        priority: EventPriority = EventPriority.NORMAL
    ) -> EventHandler:
        """Subscribe to an event that fires only once"""
        return self.subscribe(event_type, callback, priority, once=True)

    def unsubscribe(
        self,
        event_type: EventType,
        handler: Optional[EventHandler] = None,
        callback: Optional[Callable] = None
    ):
        """
        Unsubscribe from an event

        Args:
            event_type: Event type to unsubscribe from
            handler: EventHandler to remove (or None to remove all)
            callback: Callback function to remove
        """
        with self._lock:
            if event_type not in self._handlers:
                return

            if handler is None and callback is None:
                # Remove all handlers for this event type
                del self._handlers[event_type]
                logger.debug(f"Unsubscribed all handlers from {event_type.name}")
                return

            if handler:
                try:
                    self._handlers[event_type].remove(handler)
                    logger.debug(f"Unsubscribed handler from {event_type.name}")
                except ValueError:
                    pass

            if callback:
                # Find and remove handlers with matching callback
                self._handlers[event_type] = [
                    h for h in self._handlers[event_type]
                    if h._callback_ref() != callback
                ]

    def unsubscribe_all(self):
        """Remove all event handlers"""
        with self._lock:
            self._handlers.clear()
            logger.info("Unsubscribed all event handlers")

    def emit(self, event: Event):
        """
        Emit an event to all subscribed handlers

        Args:
            event: Event to emit
        """
        if not self._enabled:
            return

        with self._lock:
            # Add to queue if batching
            if self._batching:
                self._event_queue.append(event)
                return

            # Update statistics
            self._event_counts[event.event_type] += 1
            self._total_events += 1

            # Get handlers for this event type
            handlers = self._handlers.get(event.event_type, [])

            # Execute handlers and collect ones to remove
            handlers_to_remove = []

            for handler in handlers[:]:  # Copy list to allow modification
                should_keep = handler(event)
                if not should_keep:
                    handlers_to_remove.append(handler)

            # Remove handlers marked for removal
            for handler in handlers_to_remove:
                try:
                    self._handlers[event.event_type].remove(handler)
                except ValueError:
                    pass

            logger.debug(f"Emitted event: {event}")

    def emit_async(self, event: Event):
        """
        Emit event asynchronously in a separate thread

        Args:
            event: Event to emit
        """
        thread = threading.Thread(target=self.emit, args=(event,), daemon=True)
        thread.start()

    def start_batch(self):
        """Start batching events (collect without emitting)"""
        with self._lock:
            self._batching = True
            self._event_queue.clear()

    def end_batch(self, emit_all: bool = True):
        """
        End batching and optionally emit all queued events

        Args:
            emit_all: If True, emit all queued events
        """
        with self._lock:
            self._batching = False

            if emit_all and self._event_queue:
                events = self._event_queue[:]
                self._event_queue.clear()

                # Emit all queued events
                for event in events:
                    self.emit(event)

    def enable(self):
        """Enable event emission"""
        self._enabled = True
        logger.info("Event bus enabled")

    def disable(self):
        """Disable event emission (events are dropped)"""
        self._enabled = False
        logger.info("Event bus disabled")

    def get_handler_count(self, event_type: Optional[EventType] = None) -> int:
        """Get number of handlers for an event type"""
        with self._lock:
            if event_type:
                return len(self._handlers.get(event_type, []))
            return sum(len(handlers) for handlers in self._handlers.values())

    def get_statistics(self) -> Dict[str, Any]:
        """Get event bus statistics"""
        with self._lock:
            return {
                'total_events': self._total_events,
                'event_counts': dict(self._event_counts),
                'total_handlers': self.get_handler_count(),
                'handlers_by_type': {
                    et.name: len(handlers)
                    for et, handlers in self._handlers.items()
                },
                'enabled': self._enabled,
                'batching': self._batching,
                'queued_events': len(self._event_queue)
            }

    def clear_statistics(self):
        """Reset event statistics"""
        with self._lock:
            self._event_counts.clear()
            self._total_events = 0


# Global event bus instance
_event_bus = EventBus()


def get_event_bus() -> EventBus:
    """Get the global event bus instance"""
    return _event_bus


def emit(event: Event):
    """Convenience function to emit an event on the global bus"""
    _event_bus.emit(event)


def subscribe(
    event_type: EventType,
    callback: Callable[[Event], None],
    priority: EventPriority = EventPriority.NORMAL,
    filters: Optional[Dict[str, Any]] = None,
    once: bool = False
) -> EventHandler:
    """Convenience function to subscribe to the global bus"""
    return _event_bus.subscribe(event_type, callback, priority, filters, once)


def unsubscribe(
    event_type: EventType,
    handler: Optional[EventHandler] = None,
    callback: Optional[Callable] = None
):
    """Convenience function to unsubscribe from the global bus"""
    _event_bus.unsubscribe(event_type, handler, callback)
