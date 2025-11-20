#!/usr/bin/env python3
"""
State Management System - Comprehensive Example

Demonstrates all features of the state management system:
- Observable state pattern
- Event system
- Command pattern (undo/redo)
- Settings persistence
- History tracking
- Draft system
- Auto-save functionality
"""

import time
from datetime import datetime

from aamva_license_generator.events import (
    Event,
    EventType,
    EventPriority,
    get_event_bus,
    subscribe
)
from aamva_license_generator.commands import (
    FunctionCommand,
    MacroCommand,
    get_command_history,
    Transaction
)
from aamva_license_generator.state import (
    AppState,
    get_app_state,
    GenerationState,
    GenerationStatus,
    get_settings,
    get_history_manager
)


def example_1_basic_state_management():
    """
    Example 1: Basic State Management

    Demonstrates:
    - Getting the global app state
    - Setting configuration values
    - Automatic command creation for undo/redo
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 1: Basic State Management")
    print("=" * 60)

    # Get the global app state (singleton)
    state = get_app_state()

    print(f"\nInitial state: {state.config}")

    # Set state code (automatically creates undo command)
    print("\n1. Setting state code to 'NY'...")
    state.set_state_code("NY")
    print(f"   Current config: {state.config}")

    # Set quantity
    print("\n2. Setting quantity to 25...")
    state.set_quantity(25)
    print(f"   Current config: {state.config}")

    # Set output directory
    print("\n3. Setting output directory...")
    state.set_output_directory("/tmp/licenses")
    print(f"   Current config: {state.config}")

    # Get command history
    history = get_command_history()
    print(f"\n4. Command history has {history.get_undo_count()} undoable commands")


def example_2_undo_redo():
    """
    Example 2: Undo/Redo Operations

    Demonstrates:
    - Undoing changes
    - Redoing changes
    - Command history inspection
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Undo/Redo Operations")
    print("=" * 60)

    state = get_app_state()
    history = get_command_history()

    print(f"\nCurrent state: {state.config}")

    # Make some changes
    print("\n1. Making changes...")
    state.set_state_code("TX")
    state.set_quantity(50)
    print(f"   After changes: {state.config}")

    # Undo last change
    print("\n2. Undoing last change (quantity)...")
    history.undo()
    print(f"   After undo: {state.config}")

    # Undo another change
    print("\n3. Undoing another change (state code)...")
    history.undo()
    print(f"   After undo: {state.config}")

    # Redo a change
    print("\n4. Redoing last undo...")
    history.redo()
    print(f"   After redo: {state.config}")

    print(f"\n5. Can undo? {history.can_undo()}")
    print(f"   Can redo? {history.can_redo()}")
    print(f"   Next undo would be: {history.get_undo_description()}")
    print(f"   Next redo would be: {history.get_redo_description()}")


def example_3_event_system():
    """
    Example 3: Event System

    Demonstrates:
    - Subscribing to events
    - Event emission
    - Event handlers with priorities
    - Event filtering
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Event System")
    print("=" * 60)

    bus = get_event_bus()
    state = get_app_state()

    # Subscribe to state change events
    def on_state_changed(event: Event):
        print(f"   [Event Handler] State changed: {event.data}")

    def on_settings_changed(event: Event):
        print(f"   [Event Handler] Settings changed")

    print("\n1. Subscribing to events...")
    handler1 = subscribe(EventType.STATE_CHANGED, on_state_changed)
    handler2 = subscribe(EventType.SETTINGS_CHANGED, on_settings_changed)

    print("\n2. Making changes (triggers events)...")
    state.set_state_code("FL")
    state.set_quantity(100)

    print("\n3. Event bus statistics:")
    stats = bus.get_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")

    # Unsubscribe
    print("\n4. Unsubscribing from events...")
    bus.unsubscribe(EventType.STATE_CHANGED, handler1)


def example_4_transactions():
    """
    Example 4: Transactions

    Demonstrates:
    - Grouping multiple commands into one
    - Atomic operations
    - Transaction commit/rollback
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Transactions")
    print("=" * 60)

    state = get_app_state()
    history = get_command_history()

    print(f"\nInitial config: {state.config}")

    # Use transaction context manager
    print("\n1. Starting transaction...")
    try:
        with Transaction(history, "Configure for batch generation"):
            state.set_state_code("CA")
            state.set_quantity(100)
            state.set_output_directory("/tmp/batch_output")
            state.set_format_flags(pdf=True, docx=True, images=True)
            print("   All changes made within transaction")

        print(f"\n2. Transaction committed successfully!")
        print(f"   New config: {state.config}")

        # Undo the entire transaction
        print("\n3. Undoing entire transaction...")
        history.undo()
        print(f"   After undo: {state.config}")

    except Exception as e:
        print(f"   Transaction failed: {e}")


def example_5_settings_persistence():
    """
    Example 5: Settings Persistence

    Demonstrates:
    - Reading/writing settings
    - Auto-save functionality
    - Settings groups (window, generation, UI, advanced)
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Settings Persistence")
    print("=" * 60)

    settings = get_settings()

    print("\n1. Current settings:")
    print(f"   Window size: {settings.window.width}x{settings.window.height}")
    print(f"   Theme: {settings.ui.theme}")
    print(f"   Default state: {settings.generation.state_code}")
    print(f"   Default quantity: {settings.generation.quantity}")

    # Modify settings
    print("\n2. Modifying settings...")
    settings.generation.state_code = "TX"
    settings.generation.quantity = 25
    settings.ui.theme = "light"
    settings.window.width = 1400

    # Settings are auto-saved after delay
    print(f"   Auto-save enabled: {settings.is_auto_save_enabled()}")
    print(f"   Auto-save interval: {settings.advanced.auto_save_interval}s")

    # Manual save
    print("\n3. Manually saving settings...")
    settings.save()
    print("   Settings saved!")

    # Recent items
    print("\n4. Recent items:")
    settings.add_recent_output_dir("/tmp/output1")
    settings.add_recent_output_dir("/tmp/output2")
    settings.add_recent_state("CA")
    settings.add_recent_state("NY")

    print(f"   Recent directories: {settings.get_recent_output_dirs()[:3]}")
    print(f"   Recent states: {settings.get_recent_states()[:5]}")


def example_6_draft_system():
    """
    Example 6: Draft System

    Demonstrates:
    - Saving drafts
    - Loading drafts
    - Managing multiple drafts
    - Draft metadata
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 6: Draft System")
    print("=" * 60)

    state = get_app_state()

    # Create a configuration
    print("\n1. Creating configuration...")
    state.set_state_code("CA")
    state.set_quantity(50)
    state.set_output_directory("/tmp/california_batch")
    print(f"   Config: {state.config}")

    # Save as draft
    print("\n2. Saving as draft 'California Batch'...")
    state.save_draft("California Batch", "50 CA licenses for testing")

    # Create another configuration
    print("\n3. Creating different configuration...")
    state.set_state_code("NY")
    state.set_quantity(25)
    state.set_output_directory("/tmp/newyork_batch")
    print(f"   Config: {state.config}")

    # Save as another draft
    print("\n4. Saving as draft 'New York Batch'...")
    state.save_draft("New York Batch", "25 NY licenses")

    # List all drafts
    print("\n5. Available drafts:")
    for draft in state.get_drafts():
        print(f"   - {draft.name}")
        print(f"     Config: {draft.config}")
        print(f"     Created: {draft.created_at.strftime('%Y-%m-%d %H:%M')}")
        print(f"     Description: {draft.description}")

    # Load a draft
    print("\n6. Loading draft 'California Batch'...")
    state.load_draft("California Batch")
    print(f"   Loaded config: {state.config}")


def example_7_generation_tracking():
    """
    Example 7: Generation State Tracking

    Demonstrates:
    - Starting generation
    - Tracking progress
    - Per-license status
    - Statistics collection
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 7: Generation State Tracking")
    print("=" * 60)

    state = get_app_state()

    # Configure for generation
    state.set_state_code("CA")
    state.set_quantity(10)

    # Start generation
    print("\n1. Starting generation...")
    gen_state = state.start_generation()
    print(f"   Status: {gen_state.status.name}")
    print(f"   Total count: {gen_state.total_count}")

    # Simulate processing licenses
    print("\n2. Processing licenses...")
    for i in range(10):
        # Start license
        gen_state.start_license(i, state_code="CA")
        print(f"   Processing license #{i+1}...")

        # Simulate work
        time.sleep(0.1)

        # Complete license (90% success rate for demo)
        if i < 9:
            gen_state.complete_license(
                i,
                license_number=f"CA{12345678 + i}",
                name="John Doe",
                files=[f"/tmp/license_{i}.bmp"]
            )
            print(f"     ✓ Completed")
        else:
            gen_state.fail_license(i, "Barcode encoding error")
            print(f"     ✗ Failed")

        print(f"     Progress: {gen_state.progress*100:.1f}%")

    # Complete generation
    print("\n3. Completing generation...")
    state.complete_generation(success=True)

    # Show statistics
    print("\n4. Generation statistics:")
    stats = gen_state.get_statistics()
    for key, value in stats.items():
        if key in ['duration', 'licenses_per_second']:
            print(f"   {key}: {value:.2f}")
        elif key in ['progress', 'stage_progress']:
            print(f"   {key}: {value*100:.1f}%")
        else:
            print(f"   {key}: {value}")


def example_8_history_management():
    """
    Example 8: History Management

    Demonstrates:
    - Tracking generation history
    - Querying history
    - Statistics aggregation
    - History persistence
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 8: History Management")
    print("=" * 60)

    history_mgr = get_history_manager()

    print("\n1. Current history:")
    entries = history_mgr.get_entries(limit=5)
    print(f"   Total entries: {history_mgr.get_entry_count()}")
    print(f"   Showing last {len(entries)} entries:")

    for entry in entries:
        status = "✓" if entry.success else "✗"
        print(f"\n   {status} {entry.timestamp.strftime('%Y-%m-%d %H:%M')}")
        print(f"     State: {entry.state_code or 'ALL'}")
        print(f"     Licenses: {entry.completed_count}/{entry.total_count}")
        print(f"     Duration: {entry.duration:.1f}s")
        print(f"     Success rate: {entry.success_rate*100:.1f}%")

    # Get statistics
    print("\n2. Overall statistics:")
    stats = history_mgr.get_statistics()
    print(f"   Total generations: {stats['total_generations']}")
    print(f"   Total licenses: {stats['total_licenses']}")
    print(f"   Success rate: {stats['success_rate']*100:.1f}%")
    print(f"   Average duration: {stats['avg_duration']:.1f}s")
    print(f"   Average speed: {stats['avg_licenses_per_second']:.2f} licenses/sec")

    # State-specific statistics
    print("\n3. Statistics by state:")
    state_stats = history_mgr.get_state_statistics()
    for state_code, state_data in list(state_stats.items())[:3]:
        print(f"\n   {state_code}:")
        print(f"     Generations: {state_data['count']}")
        print(f"     Total licenses: {state_data['total_licenses']}")
        print(f"     Avg duration: {state_data['avg_duration']:.1f}s")
        print(f"     Success rate: {state_data['success_rate']*100:.1f}%")


def example_9_custom_commands():
    """
    Example 9: Custom Commands

    Demonstrates:
    - Creating custom command classes
    - Function commands
    - Macro commands
    - Command composition
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 9: Custom Commands")
    print("=" * 60)

    history = get_command_history()
    state = get_app_state()

    # Simple function command
    print("\n1. Creating function command...")
    old_quantity = state.config.quantity

    cmd = FunctionCommand(
        execute_fn=lambda: state._set_quantity_internal(75),
        undo_fn=lambda: state._set_quantity_internal(old_quantity),
        description="Set quantity to 75"
    )

    print(f"   Before: quantity = {state.config.quantity}")
    history.execute(cmd)
    print(f"   After: quantity = {state.config.quantity}")

    # Macro command (multiple operations)
    print("\n2. Creating macro command...")

    def setup_state():
        state._set_state_code_internal("FL")
        return True

    def setup_quantity():
        state._set_quantity_internal(30)
        return True

    def setup_directory():
        state._set_output_directory_internal("/tmp/florida")
        return True

    macro = MacroCommand([
        FunctionCommand(setup_state, lambda: True, "Set FL"),
        FunctionCommand(setup_quantity, lambda: True, "Set 30"),
        FunctionCommand(setup_directory, lambda: True, "Set dir"),
    ], description="Configure Florida batch")

    print(f"   Before: {state.config}")
    history.execute(macro)
    print(f"   After: {state.config}")

    # Undo macro (undoes all sub-commands)
    print("\n3. Undoing macro command...")
    history.undo()
    print(f"   After undo: {state.config}")


def example_10_thread_safety():
    """
    Example 10: Thread Safety

    Demonstrates:
    - Thread-safe state operations
    - Concurrent event handling
    - Lock-free reads
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 10: Thread Safety")
    print("=" * 60)

    import threading

    state = get_app_state()
    results = []

    def worker(thread_id, state_code, quantity):
        """Worker thread that modifies state"""
        print(f"   Thread {thread_id} starting...")

        # All operations are thread-safe
        state.set_state_code(state_code, create_command=False)
        state.set_quantity(quantity, create_command=False)

        # Read state (lock-free)
        config = state.get_config()

        results.append((thread_id, config.state_code, config.quantity))
        print(f"   Thread {thread_id} completed")

    print("\n1. Starting 5 worker threads...")
    threads = []
    states_to_test = ["CA", "NY", "TX", "FL", "IL"]

    for i, state_code in enumerate(states_to_test):
        t = threading.Thread(
            target=worker,
            args=(i, state_code, (i+1) * 10)
        )
        threads.append(t)
        t.start()

    # Wait for all threads
    print("\n2. Waiting for threads to complete...")
    for t in threads:
        t.join()

    print(f"\n3. All {len(threads)} threads completed successfully!")
    print(f"   Final state: {state.config}")


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("STATE MANAGEMENT SYSTEM - COMPREHENSIVE EXAMPLES")
    print("=" * 60)

    examples = [
        ("Basic State Management", example_1_basic_state_management),
        ("Undo/Redo Operations", example_2_undo_redo),
        ("Event System", example_3_event_system),
        ("Transactions", example_4_transactions),
        ("Settings Persistence", example_5_settings_persistence),
        ("Draft System", example_6_draft_system),
        ("Generation Tracking", example_7_generation_tracking),
        ("History Management", example_8_history_management),
        ("Custom Commands", example_9_custom_commands),
        ("Thread Safety", example_10_thread_safety),
    ]

    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")

    print("\nRunning all examples...\n")

    for name, example_func in examples:
        try:
            example_func()
            time.sleep(0.5)  # Pause between examples
        except Exception as e:
            print(f"\n❌ Example '{name}' failed: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 60)
    print("ALL EXAMPLES COMPLETED!")
    print("=" * 60)

    # Final statistics
    print("\n📊 Final System Statistics:")
    print("\n1. Event Bus:")
    bus_stats = get_event_bus().get_statistics()
    print(f"   Total events emitted: {bus_stats['total_events']}")
    print(f"   Active handlers: {bus_stats['total_handlers']}")

    print("\n2. Command History:")
    cmd_stats = get_command_history().get_statistics()
    print(f"   Undo count: {cmd_stats['undo_count']}")
    print(f"   Redo count: {cmd_stats['redo_count']}")

    print("\n3. Generation History:")
    hist_mgr = get_history_manager()
    print(f"   Total entries: {hist_mgr.get_entry_count()}")

    print("\n4. Application State:")
    app_state = get_app_state()
    print(f"   Current config: {app_state.config}")
    print(f"   Available drafts: {len(app_state.get_drafts())}")


if __name__ == "__main__":
    main()
