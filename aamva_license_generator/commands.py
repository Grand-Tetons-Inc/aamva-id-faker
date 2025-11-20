"""
Command Pattern Implementation for Undo/Redo

Provides a robust command pattern with undo/redo capabilities,
command composition, and transaction support.

Features:
- Undo/redo stack with configurable limits
- Command composition (macro commands)
- Transaction support (atomic operations)
- Command history persistence
- Thread-safe operations
"""

import threading
from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Deque, Dict, List, Optional
import json
import logging

from .events import Event, EventType, emit

logger = logging.getLogger(__name__)


class Command(ABC):
    """
    Abstract base class for all commands

    Commands encapsulate operations that can be executed, undone, and redone.
    Each command should be self-contained and reversible.
    """

    def __init__(self, description: str = ""):
        """
        Initialize command

        Args:
            description: Human-readable description of the command
        """
        self.description = description
        self.timestamp = datetime.now()
        self.executed = False

    @abstractmethod
    def execute(self) -> bool:
        """
        Execute the command

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def undo(self) -> bool:
        """
        Undo the command (reverse the operation)

        Returns:
            True if successful, False otherwise
        """
        pass

    def redo(self) -> bool:
        """
        Redo the command (re-execute)

        Default implementation just calls execute()

        Returns:
            True if successful, False otherwise
        """
        return self.execute()

    def can_undo(self) -> bool:
        """Check if command can be undone"""
        return self.executed

    def can_merge(self, other: 'Command') -> bool:
        """
        Check if this command can be merged with another

        Used to combine similar consecutive commands (e.g., typing)

        Args:
            other: Another command to potentially merge with

        Returns:
            True if commands can be merged
        """
        return False

    def merge(self, other: 'Command') -> 'Command':
        """
        Merge this command with another

        Args:
            other: Command to merge with

        Returns:
            New merged command
        """
        raise NotImplementedError("Merge not supported for this command")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize command to dictionary"""
        return {
            'type': self.__class__.__name__,
            'description': self.description,
            'timestamp': self.timestamp.isoformat(),
            'executed': self.executed
        }

    def __str__(self):
        return f"{self.__class__.__name__}({self.description})"


class FunctionCommand(Command):
    """
    Simple command that executes functions

    Useful for simple operations that don't need custom command classes.

    Example:
        >>> cmd = FunctionCommand(
        ...     execute_fn=lambda: obj.set_value(5),
        ...     undo_fn=lambda: obj.set_value(old_value),
        ...     description="Set value to 5"
        ... )
    """

    def __init__(
        self,
        execute_fn: Callable[[], bool],
        undo_fn: Callable[[], bool],
        description: str = "",
        redo_fn: Optional[Callable[[], bool]] = None
    ):
        """
        Initialize function command

        Args:
            execute_fn: Function to execute
            undo_fn: Function to undo
            description: Command description
            redo_fn: Optional custom redo function
        """
        super().__init__(description)
        self._execute_fn = execute_fn
        self._undo_fn = undo_fn
        self._redo_fn = redo_fn

    def execute(self) -> bool:
        try:
            result = self._execute_fn()
            self.executed = True
            return result if isinstance(result, bool) else True
        except Exception as e:
            logger.error(f"Command execution failed: {e}", exc_info=True)
            return False

    def undo(self) -> bool:
        try:
            result = self._undo_fn()
            return result if isinstance(result, bool) else True
        except Exception as e:
            logger.error(f"Command undo failed: {e}", exc_info=True)
            return False

    def redo(self) -> bool:
        if self._redo_fn:
            try:
                result = self._redo_fn()
                return result if isinstance(result, bool) else True
            except Exception as e:
                logger.error(f"Command redo failed: {e}", exc_info=True)
                return False
        return super().redo()


class MacroCommand(Command):
    """
    Composite command that executes multiple commands as one

    All sub-commands are executed together and can be undone together.

    Example:
        >>> macro = MacroCommand([
        ...     SetStateCommand("CA"),
        ...     SetQuantityCommand(10),
        ...     SetOutputCommand("/tmp/output")
        ... ], description="Configure generation")
    """

    def __init__(self, commands: List[Command], description: str = "Macro"):
        """
        Initialize macro command

        Args:
            commands: List of commands to execute
            description: Macro description
        """
        super().__init__(description)
        self.commands = commands

    def execute(self) -> bool:
        """Execute all commands in order"""
        executed = []

        try:
            for cmd in self.commands:
                if cmd.execute():
                    executed.append(cmd)
                else:
                    # Rollback on failure
                    for executed_cmd in reversed(executed):
                        executed_cmd.undo()
                    return False

            self.executed = True
            return True

        except Exception as e:
            logger.error(f"Macro command execution failed: {e}", exc_info=True)
            # Rollback
            for executed_cmd in reversed(executed):
                executed_cmd.undo()
            return False

    def undo(self) -> bool:
        """Undo all commands in reverse order"""
        try:
            for cmd in reversed(self.commands):
                if cmd.can_undo():
                    if not cmd.undo():
                        logger.warning(f"Failed to undo command: {cmd}")
                        # Continue undoing other commands
            return True

        except Exception as e:
            logger.error(f"Macro command undo failed: {e}", exc_info=True)
            return False

    def redo(self) -> bool:
        """Redo all commands in order"""
        return self.execute()

    def add_command(self, command: Command):
        """Add a command to the macro"""
        self.commands.append(command)

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data['commands'] = [cmd.to_dict() for cmd in self.commands]
        return data


class CommandHistory:
    """
    Manages command history with undo/redo support

    Features:
    - Configurable history size
    - Command merging for similar consecutive commands
    - Transaction support
    - Thread-safe operations
    - History persistence
    """

    def __init__(self, max_history: int = 100):
        """
        Initialize command history

        Args:
            max_history: Maximum number of commands to keep in history
        """
        self.max_history = max_history
        self._undo_stack: Deque[Command] = deque(maxlen=max_history)
        self._redo_stack: Deque[Command] = deque(maxlen=max_history)
        self._lock = threading.RLock()
        self._transaction_commands: Optional[List[Command]] = None
        self._merge_enabled = True

    def execute(self, command: Command) -> bool:
        """
        Execute a command and add it to history

        Args:
            command: Command to execute

        Returns:
            True if execution succeeded
        """
        with self._lock:
            # Execute the command
            if not command.execute():
                logger.warning(f"Command execution failed: {command}")
                return False

            # In transaction mode, just collect commands
            if self._transaction_commands is not None:
                self._transaction_commands.append(command)
                return True

            # Try to merge with previous command
            if (self._merge_enabled and self._undo_stack and
                self._undo_stack[-1].can_merge(command)):
                merged = self._undo_stack[-1].merge(command)
                self._undo_stack[-1] = merged
                logger.debug(f"Merged commands: {merged}")
            else:
                # Add to undo stack
                self._undo_stack.append(command)

            # Clear redo stack (new command invalidates redo)
            self._redo_stack.clear()

            # Emit event
            emit(Event(
                EventType.COMMAND_EXECUTED,
                source=self,
                data={'command': command.description}
            ))

            logger.debug(f"Executed command: {command}")
            return True

    def undo(self) -> bool:
        """
        Undo the last command

        Returns:
            True if undo succeeded
        """
        with self._lock:
            if not self.can_undo():
                logger.debug("Nothing to undo")
                return False

            command = self._undo_stack.pop()

            if not command.undo():
                # Undo failed, put command back
                self._undo_stack.append(command)
                logger.warning(f"Command undo failed: {command}")
                return False

            # Move to redo stack
            self._redo_stack.append(command)

            # Emit event
            emit(Event(
                EventType.COMMAND_UNDONE,
                source=self,
                data={'command': command.description}
            ))

            logger.debug(f"Undone command: {command}")
            return True

    def redo(self) -> bool:
        """
        Redo the last undone command

        Returns:
            True if redo succeeded
        """
        with self._lock:
            if not self.can_redo():
                logger.debug("Nothing to redo")
                return False

            command = self._redo_stack.pop()

            if not command.redo():
                # Redo failed, put command back
                self._redo_stack.append(command)
                logger.warning(f"Command redo failed: {command}")
                return False

            # Move back to undo stack
            self._undo_stack.append(command)

            # Emit event
            emit(Event(
                EventType.COMMAND_REDONE,
                source=self,
                data={'command': command.description}
            ))

            logger.debug(f"Redone command: {command}")
            return True

    def can_undo(self) -> bool:
        """Check if undo is possible"""
        with self._lock:
            return len(self._undo_stack) > 0

    def can_redo(self) -> bool:
        """Check if redo is possible"""
        with self._lock:
            return len(self._redo_stack) > 0

    def get_undo_description(self) -> Optional[str]:
        """Get description of command that would be undone"""
        with self._lock:
            return self._undo_stack[-1].description if self._undo_stack else None

    def get_redo_description(self) -> Optional[str]:
        """Get description of command that would be redone"""
        with self._lock:
            return self._redo_stack[-1].description if self._redo_stack else None

    def clear(self):
        """Clear all command history"""
        with self._lock:
            self._undo_stack.clear()
            self._redo_stack.clear()
            logger.info("Command history cleared")

    def get_undo_count(self) -> int:
        """Get number of undoable commands"""
        with self._lock:
            return len(self._undo_stack)

    def get_redo_count(self) -> int:
        """Get number of redoable commands"""
        with self._lock:
            return len(self._redo_stack)

    # Transaction support

    def begin_transaction(self):
        """
        Begin a transaction

        Commands executed during a transaction are collected
        and executed as a single macro command when committed.
        """
        with self._lock:
            if self._transaction_commands is not None:
                raise RuntimeError("Transaction already in progress")
            self._transaction_commands = []
            logger.debug("Transaction started")

    def commit_transaction(self, description: str = "Transaction") -> bool:
        """
        Commit the transaction

        Args:
            description: Description for the macro command

        Returns:
            True if commit succeeded
        """
        with self._lock:
            if self._transaction_commands is None:
                raise RuntimeError("No transaction in progress")

            commands = self._transaction_commands
            self._transaction_commands = None

            if not commands:
                logger.debug("Empty transaction, nothing to commit")
                return True

            # Create macro command
            macro = MacroCommand(commands, description)

            # Add to undo stack (already executed)
            macro.executed = True
            self._undo_stack.append(macro)
            self._redo_stack.clear()

            logger.debug(f"Transaction committed: {len(commands)} commands")
            return True

    def rollback_transaction(self):
        """
        Rollback the transaction

        Undo all commands executed during the transaction.
        """
        with self._lock:
            if self._transaction_commands is None:
                raise RuntimeError("No transaction in progress")

            commands = self._transaction_commands
            self._transaction_commands = None

            # Undo all commands in reverse order
            for cmd in reversed(commands):
                cmd.undo()

            logger.debug(f"Transaction rolled back: {len(commands)} commands")

    def is_in_transaction(self) -> bool:
        """Check if currently in a transaction"""
        with self._lock:
            return self._transaction_commands is not None

    # Command merging

    def enable_merging(self):
        """Enable automatic command merging"""
        self._merge_enabled = True

    def disable_merging(self):
        """Disable automatic command merging"""
        self._merge_enabled = False

    # Persistence

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize command history to dictionary

        Returns:
            Dictionary representation of history
        """
        with self._lock:
            return {
                'undo_stack': [cmd.to_dict() for cmd in self._undo_stack],
                'redo_stack': [cmd.to_dict() for cmd in self._redo_stack],
                'max_history': self.max_history
            }

    def to_json(self) -> str:
        """Serialize command history to JSON"""
        return json.dumps(self.to_dict(), indent=2)

    def get_statistics(self) -> Dict[str, Any]:
        """Get command history statistics"""
        with self._lock:
            return {
                'undo_count': len(self._undo_stack),
                'redo_count': len(self._redo_stack),
                'max_history': self.max_history,
                'in_transaction': self.is_in_transaction(),
                'merge_enabled': self._merge_enabled
            }


# Context manager for transactions
class Transaction:
    """
    Context manager for command transactions

    Example:
        >>> history = CommandHistory()
        >>> with Transaction(history, "Batch update"):
        ...     history.execute(SetStateCommand("CA"))
        ...     history.execute(SetQuantityCommand(10))
        ...     # Both commands executed as one
    """

    def __init__(self, history: CommandHistory, description: str = "Transaction"):
        """
        Initialize transaction context

        Args:
            history: CommandHistory to use
            description: Transaction description
        """
        self.history = history
        self.description = description

    def __enter__(self):
        self.history.begin_transaction()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            # Success - commit
            self.history.commit_transaction(self.description)
        else:
            # Error - rollback
            self.history.rollback_transaction()
        return False  # Don't suppress exceptions


# Global command history instance
_command_history = CommandHistory()


def get_command_history() -> CommandHistory:
    """Get the global command history instance"""
    return _command_history


def execute(command: Command) -> bool:
    """Convenience function to execute command on global history"""
    return _command_history.execute(command)


def undo() -> bool:
    """Convenience function to undo on global history"""
    return _command_history.undo()


def redo() -> bool:
    """Convenience function to redo on global history"""
    return _command_history.redo()
