# Error Handling & Validation Specification
## AAMVA License Generator GUI

**Version:** 1.0
**Date:** 2025-11-20
**Author:** UX Architecture Team
**Status:** Design Specification

---

## Table of Contents

1. [Philosophy: Beyond Error Popups](#philosophy-beyond-error-popups)
2. [Error Taxonomy](#error-taxonomy)
3. [Validation Architecture](#validation-architecture)
4. [Feedback Mechanisms](#feedback-mechanisms)
5. [Recovery Workflows](#recovery-workflows)
6. [Progress & Status Communication](#progress--status-communication)
7. [State Persistence & Autosave](#state-persistence--autosave)
8. [Implementation Examples](#implementation-examples)
9. [Anti-Patterns to Avoid](#anti-patterns-to-avoid)

---

## Philosophy: Beyond Error Popups

### The Problem with Traditional Error Handling

**Traditional approach:**
```
User fills form → Clicks "Generate" → ❌ ERROR POPUP → User confused → Starts over
```

**Problems:**
1. **Context Loss**: Modal dialogs break user flow and hide the problematic field
2. **Batch Validation**: All errors shown at once overwhelms users
3. **Technical Language**: "ValueError: Invalid state code" means nothing to non-developers
4. **No Guidance**: Errors tell what's wrong, not how to fix it
5. **Interruption**: Forces user to stop and deal with error immediately

### Our Approach: Progressive, Contextual, Graceful

**Our philosophy:**
```
User types → Real-time feedback → Suggestions appear → Auto-correction offered →
Graceful degradation → Background validation → Recovery options → Success paths
```

**Principles:**
1. **Prevent errors before they happen** (constrained inputs, smart defaults)
2. **Detect errors as they occur** (real-time validation)
3. **Guide users to correction** (inline suggestions, examples)
4. **Enable graceful continuation** (partial success, recovery workflows)
5. **Learn from patterns** (smart defaults from previous sessions)

---

## Error Taxonomy

### 1. Input Validation Errors (User-Facing)

#### 1.1 State Code Errors
```yaml
Error Type: INVALID_STATE_CODE
Severity: ERROR
When: User enters non-existent state abbreviation
Examples:
  - "XX" (invalid)
  - "ZZ" (invalid)
  - "Calif" (wrong format)

User Experience:
  Traditional: ❌ "Error: Invalid state code 'XX'"
  Our Approach:
    - Real-time: Input field shows red underline as user types "X"
    - After "XX": Inline message: "No state matches 'XX'. Did you mean: CA, CT, CO?"
    - Autocomplete: Dropdown appears with fuzzy matches
    - Visual aid: Mini US map highlights available states
    - Graceful fallback: "Use random state instead?"
```

#### 1.2 Quantity/Count Errors
```yaml
Error Type: INVALID_QUANTITY
Severity: WARNING → ERROR
When: User requests unreasonable number of licenses

Scenarios:
  - Zero licenses: "Generate at least 1 license"
  - Negative: Auto-corrects to absolute value
  - Too many (>1000): "Generating 5000 licenses will take ~4 minutes. Continue?"
  - Non-numeric: "Please enter a number"

Progressive Feedback:
  1-100:   ✓ Green indicator
  101-500: ⚠️ Yellow "This may take a minute"
  501-1000: 🟠 Orange "Large batch - estimated 2 minutes"
  1001+:   🔴 Red "Very large batch - confirm to continue"
```

#### 1.3 File Path Errors
```yaml
Error Type: OUTPUT_PATH_INVALID
Severity: ERROR (blocking)
When: User specifies invalid output directory

Sub-types:
  - Non-existent parent: Offer to create it
  - No permissions: Suggest alternative location
  - Path too long: Suggest shorter path
  - Invalid characters: Auto-sanitize with preview
  - Network path unavailable: Offer local fallback

User Experience:
  - Path field validates on blur
  - Browse button pre-checks permissions
  - Smart defaults: ~/Documents/AAMVA_Output
  - Recent paths dropdown
  - Auto-create with confirmation: "Create folder '/output'?"
```

### 2. Dependency Errors (System-Level)

#### 2.1 Missing Python Libraries
```yaml
Error Type: DEPENDENCY_MISSING
Severity: CRITICAL (app cannot run)
When: Required libraries not installed

Recovery Workflow:
  1. On app launch: Check all dependencies
  2. If missing: Show friendly setup wizard (not error)
  3. Wizard content:
     "Let's set up your environment"
     [ ] faker (for realistic data)      [Install]
     [ ] pdf417 (for barcodes)           [Install]
     [ ] pillow (for images)             [Install]
     [Install All] button
  4. Progress bar during installation
  5. Verify installation with checkmarks
  6. Automatic restart when ready

Prevention:
  - Bundled installer that includes dependencies
  - Docker container option
  - Portable executable with embedded Python
```

#### 2.2 Font File Missing
```yaml
Error Type: FONT_FILE_MISSING
Severity: WARNING (degraded experience)
When: LiberationMono-Bold.ttf not found

Graceful Degradation:
  1. Check for font on startup
  2. If missing:
     - Use system default font
     - Show banner: "Using system font. Download Liberation Mono for better quality"
     - Offer download button
  3. Continue generation (don't block)
  4. Generated licenses show "Default Font" watermark in corner

Prevention:
  - Bundle font in resources
  - Fallback chain: LiberationMono → DejaVu → System Default
```

### 3. Runtime Errors (Process-Level)

#### 3.1 Barcode Encoding Failures
```yaml
Error Type: BARCODE_ENCODE_ERROR
Severity: ERROR (per-license)
When: PDF417 encoding fails for specific data

Causes:
  - Data exceeds barcode capacity
  - Invalid characters in fields
  - Encoding library crash

Recovery Workflow:
  1. Catch exception at per-license level
  2. Log problematic data
  3. Show inline error in license list: "License #7: Barcode failed"
  4. Offer actions:
     [View Details] [Skip] [Retry with shorter data] [Generate without barcode]
  5. Continue processing remaining licenses
  6. Final summary: "Generated 9 of 10 licenses (1 failed)"
  7. Export error report with details

User Feedback:
  - Real-time progress: "Processing license 7... issue detected"
  - Non-blocking: Don't stop entire batch
  - Actionable: Offer to regenerate with adjusted parameters
```

#### 3.2 Image Generation Failures
```yaml
Error Type: IMAGE_GENERATION_ERROR
Severity: ERROR
When: PIL/Pillow fails to create card image

Scenarios:
  - Out of memory (large batch)
  - Corrupted barcode image
  - Invalid dimensions
  - Font rendering failure

Recovery Strategies:
  1. Reduce DPI: "Try 150 DPI instead of 300?"
  2. Simplify card: "Generate text-only version?"
  3. Process in smaller batches: "Split into 5 batches of 20?"
  4. Use fallback renderer: "Use basic image generator?"

Visual Feedback:
  - Memory usage meter in status bar
  - Warning at 80% memory: "Consider smaller batch"
  - Auto-batch splitting offered at 90% memory
```

#### 3.3 PDF/DOCX Creation Errors
```yaml
Error Type: DOCUMENT_GENERATION_ERROR
Severity: ERROR (format-specific)
When: ReportLab or python-docx fails

Failure Modes:
  - Disk full: Show available space, suggest cleanup
  - File locked: Offer alternate filename
  - Permissions: Suggest different location
  - Library crash: Offer alternative format

Resilience Strategy:
  - Independent format generation (PDF failure doesn't block DOCX)
  - Parallel generation with status indicators:
    [PDF ✓] [DOCX ⚠️] [ODT —] [Images ✓]
  - Partial success: "Generated PDF and images. DOCX failed (file locked)"
  - Export options: Let user choose which formats before starting
```

### 4. Data Quality Warnings (Non-Blocking)

#### 4.1 Data Validation Issues
```yaml
Error Type: DATA_QUALITY_WARNING
Severity: WARNING (informational)
When: Generated data has potential issues

Examples:
  - Name too long for barcode: "Truncating 'CHRISTOPHER' to 'CHRIST'"
  - Address contains special chars: "Removing emoji from address"
  - Unusual age: "Generated DOB results in age 89 (edge case)"
  - Duplicate license number: "Regenerating to avoid duplicate"

User Experience:
  - Collapsible warning panel
  - Grouped by type: "3 names truncated, 1 address sanitized"
  - Detail view shows specific licenses affected
  - Option to regenerate affected licenses
  - Not shown if user disabled warnings in settings
```

#### 4.2 State-Specific Format Warnings
```yaml
Error Type: STATE_FORMAT_WARNING
Severity: INFO
When: State format may not be complete

Scenario:
  User generates Montana license, but we only have generic format

Message:
  "ℹ️ Montana (MT): Using generic format. We don't have state-specific
   validation for this jurisdiction. License may not match real format."

Options:
  [Continue] [Choose different state] [More info about formats]

Prevention:
  - State dropdown shows coverage indicator:
    "California (CA) ✓ Full support"
    "Montana (MT) ⚠️ Generic format"
    "State Dept ❌ Not supported"
```

---

## Validation Architecture

### Three-Layer Validation Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                    VALIDATION LAYERS                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Layer 1: PREVENTION (UI Constraints)                      │
│  ├─ Dropdowns for limited choices (state, class)           │
│  ├─ Spinboxes for numeric ranges (quantity: 1-1000)        │
│  ├─ File pickers for paths (auto-validation)               │
│  ├─ Date pickers for dates (no manual entry)               │
│  └─ Disabled options for unsupported features              │
│                                                             │
│  Layer 2: REAL-TIME VALIDATION (As User Types)             │
│  ├─ Instant feedback (visual indicators)                   │
│  ├─ Debounced validation (300ms after typing stops)        │
│  ├─ Progressive disclosure (hints → warnings → errors)     │
│  ├─ Autocomplete/suggestions                               │
│  └─ Character counters and limits                          │
│                                                             │
│  Layer 3: PRE-SUBMISSION VALIDATION (Before Generate)      │
│  ├─ Comprehensive check of all inputs                      │
│  ├─ System requirements verification                       │
│  ├─ Resource availability check                            │
│  ├─ Dependency validation                                  │
│  └─ Final confirmation with summary                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Validation State Machine

```python
"""
Input State Flow:

UNTOUCHED → TYPING → VALIDATING → VALID/INVALID → CORRECTING → VALID
    ↓         ↓          ↓            ↓              ↓           ↓
 (gray)   (blue)    (yellow)    (green/red)     (orange)    (green)

State Behaviors:
- UNTOUCHED: Placeholder text, no border
- TYPING: Blue border, no validation yet
- VALIDATING: Yellow spinner, async check
- VALID: Green checkmark, subtle border
- INVALID: Red border, inline error, suggestions
- CORRECTING: Orange border, showing auto-fix preview
"""

class ValidationState(Enum):
    UNTOUCHED = "untouched"
    TYPING = "typing"
    VALIDATING = "validating"
    VALID = "valid"
    INVALID = "invalid"
    CORRECTING = "correcting"
    DISABLED = "disabled"

class ValidationResult:
    state: ValidationState
    message: str = ""
    suggestions: List[str] = []
    auto_fix: Optional[str] = None
    severity: Severity = Severity.INFO
    can_proceed: bool = True
```

### Real-Time Validation Rules

#### State Code Field
```python
"""
Validation Flow:

User types: "C"
  → Show dropdown: CA, CO, CT...
  → Gray helper: "Type to search states"

User types: "CA"
  → Instant match: California
  → Green checkmark
  → Preview: "California (636014)"

User types: "CAT"
  → No exact match
  → Orange warning: "No state 'CAT'. Did you mean: CA, CT?"
  → Suggestions dropdown appears

User types: "XX"
  → Red error: "Invalid state code"
  → Show all states in dropdown
  → Offer: "Use random state?"
"""

VALIDATION_RULES = {
    "state_code": {
        "type": "enum",
        "valid_values": list(IIN_JURISDICTIONS.values()),
        "allow_empty": False,
        "fuzzy_match": True,
        "suggestions_on_error": True,
        "auto_complete": True,
        "validation_delay_ms": 300
    }
}
```

#### Quantity Field
```python
"""
Validation Flow:

User types: "5"
  → Green checkmark
  → Preview: "Will generate in ~3 seconds"

User types: "500"
  → Yellow warning icon
  → Message: "Large batch (~25 seconds)"
  → Still valid, just informational

User types: "5000"
  → Orange warning
  → Message: "Very large batch (~4 minutes). Recommend max 1000."
  → Show: "Continue anyway?" button
  → Still allows proceeding

User types: "abc"
  → Red error
  → Message: "Please enter a number between 1 and 10,000"
  → Generate button disabled

User types: "0"
  → Red error
  → Message: "Minimum: 1 license"
  → Auto-suggest: Change to "1"?
"""

VALIDATION_RULES = {
    "quantity": {
        "type": "integer",
        "min": 1,
        "max": 10000,
        "soft_max": 1000,  # Warning above this
        "auto_correct": True,
        "preview_time_estimate": True
    }
}
```

#### Output Directory Field
```python
"""
Validation Flow:

Field focused:
  → Show browse button
  → Show recent paths dropdown
  → Show default suggestion

User types: "/tmp/output"
  → Validation starts after 500ms pause
  → Check: Path exists? Writable? Space available?
  → Results:
     - Exists + Writable: Green checkmark
     - Doesn't exist: Yellow "Create folder?"
     - No permission: Red "Cannot write to this location"
     - No space: Orange "Only 100MB available"

User clicks browse:
  → File picker opens to last used location
  → After selection: Immediate validation
  → Show checkmarks: ✓ Writable ✓ 50GB available
"""

VALIDATION_RULES = {
    "output_path": {
        "type": "path",
        "must_exist": False,
        "must_be_writable": True,
        "check_space": True,
        "min_space_mb": 100,
        "offer_create": True,
        "validation_delay_ms": 500,
        "async_validation": True
    }
}
```

### Pre-Generation Validation Checklist

Before starting generation, show comprehensive checklist modal:

```
┌─────────────────────────────────────────────────┐
│  Ready to Generate?                             │
├─────────────────────────────────────────────────┤
│                                                 │
│  Configuration:                                 │
│  ✓ State: California (CA)                       │
│  ✓ Quantity: 50 licenses                        │
│  ✓ Output: /home/user/output                    │
│                                                 │
│  System Check:                                  │
│  ✓ All dependencies installed                   │
│  ✓ Output directory writable                    │
│  ✓ 2.5 GB available space                       │
│  ✓ Font file found                              │
│                                                 │
│  Estimates:                                     │
│  ⏱ Generation time: ~25 seconds                 │
│  📦 Output size: ~5 MB                          │
│  📄 Files: 50 BMPs, 50 TXTs, 1 PDF, 1 DOCX     │
│                                                 │
│  Output Formats:                                │
│  ☑ PDF (Avery template)                         │
│  ☑ DOCX (Word document)                         │
│  ☐ ODT (OpenDocument)                           │
│  ☑ Individual images                            │
│                                                 │
│  [Generate] [Cancel] [Save Settings]            │
└─────────────────────────────────────────────────┘
```

---

## Feedback Mechanisms

### Visual Feedback System

#### Color-Coded Feedback
```
State           Color       Icon    Border      Background
─────────────────────────────────────────────────────────────
Normal          Gray        —       1px gray    White
Focus           Blue        —       2px blue    White
Typing          Blue        ~       2px blue    Light blue
Validating      Yellow      ⟳       2px yellow  White
Valid           Green       ✓       2px green   Light green
Warning         Orange      ⚠️      2px orange  Light orange
Error           Red         ✗       2px red     Light pink
Disabled        Gray        —       1px gray    Light gray
```

#### Progressive Disclosure of Messages

```
Level 1: HINTS (Proactive guidance)
  Location: Below field, small gray text
  When: Field is focused but empty
  Example: "Enter 2-letter state code (e.g., CA, NY, TX)"
  Style: font-size: 12px, color: #666, icon: 💡

Level 2: SUGGESTIONS (Helpful info)
  Location: Inline below field
  When: Valid input, but there's a better option
  Example: "✓ Valid. Tip: Use --all-states to generate one per state"
  Style: font-size: 13px, color: #0066cc, icon: ℹ️

Level 3: WARNINGS (Attention needed)
  Location: Inline below field with icon
  When: Input valid but may cause issues
  Example: "⚠️ Large batch (500 licenses) will take ~25 seconds"
  Style: font-size: 14px, color: #ff9900, icon: ⚠️

Level 4: ERRORS (Must fix)
  Location: Inline below field, prominently styled
  When: Input invalid, cannot proceed
  Example: "✗ State code 'XX' not recognized. Choose from dropdown."
  Style: font-size: 14px, color: #cc0000, bold, icon: ✗

Level 5: CRITICAL (System issue)
  Location: Banner at top of app
  When: System-level problem
  Example: "⛔ Missing dependency: pdf417. Click to install."
  Style: Full-width banner, red background, white text
```

#### Context-Sensitive Help

```
Every field has a "?" icon that shows:

┌─────────────────────────────────────────────┐
│  State Code                            [?]  │
├─────────────────────────────────────────────┤
│  What it is:                                │
│  Two-letter abbreviation for US state or    │
│  Canadian province (e.g., CA, NY, ON)       │
│                                             │
│  Why it matters:                            │
│  Determines license format, IIN, and        │
│  specific validation rules                  │
│                                             │
│  Valid options:                             │
│  • 50 US states + DC                        │
│  • 13 Canadian provinces                    │
│  • 4 US territories                         │
│                                             │
│  Examples:                                  │
│  CA (California), TX (Texas), ON (Ontario)  │
│                                             │
│  [View full list]                           │
└─────────────────────────────────────────────┘
```

### Feedback Timing

```python
"""
Feedback Delay Strategy:

Immediate (0ms):
- Color changes on focus/blur
- Icon appearance
- Dropdown opening
- Checkmarks for valid states

Fast (100ms):
- Character counter updates
- Preview updates
- Auto-complete suggestions

Debounced (300ms):
- Validation of text inputs
- Fuzzy matching
- Suggestion generation

Slow (500ms):
- Async validations (file system checks)
- API calls (if any)
- Resource availability checks

Background (continuous):
- Dependency checks
- Disk space monitoring
- Memory usage tracking
"""

TIMING_CONFIG = {
    "instant_feedback": ["focus", "blur", "click"],
    "fast_feedback": ["typing", "counter_update"],
    "debounced_validation": {
        "text_inputs": 300,
        "numeric_inputs": 200
    },
    "async_validation": {
        "file_paths": 500,
        "network_paths": 1000
    }
}
```

### Accessibility

```yaml
Screen Reader Support:
  - ARIA labels on all inputs
  - Live regions for validation messages
  - Error announcements: "Error: State code invalid"
  - Success announcements: "Validation passed"

Keyboard Navigation:
  - Tab order follows logical flow
  - Enter submits form
  - Escape closes modals
  - Arrow keys navigate suggestions
  - Space toggles checkboxes

Visual Indicators:
  - Not color-only (icons + borders + text)
  - High contrast mode support
  - Focus indicators clearly visible
  - Error messages have sufficient contrast (4.5:1)

Motor Impairment:
  - Large click targets (minimum 44x44px)
  - Generous field spacing
  - No time-based dismissals
  - Click or keyboard for all actions
```

---

## Recovery Workflows

### Per-Error Recovery Strategies

#### 1. Invalid State Code
```
┌─────────────────────────────────────────────┐
│  ⚠️ State Code Issue                        │
├─────────────────────────────────────────────┤
│  You entered: "XX"                          │
│  This state code is not recognized.         │
│                                             │
│  Quick fixes:                               │
│  • [Use California (CA)]                    │
│  • [Use New York (NY)]                      │
│  • [Use Random State]                       │
│  • [Choose from full list ▼]                │
│                                             │
│  Or correct manually: [XX____________]      │
│                                             │
│  [Apply Fix] [Cancel]                       │
└─────────────────────────────────────────────┘
```

#### 2. Missing Dependencies
```
┌─────────────────────────────────────────────┐
│  🔧 Setup Required                          │
├─────────────────────────────────────────────┤
│  Some required libraries are missing.       │
│  Let's install them now (takes ~1 minute)   │
│                                             │
│  Missing:                                   │
│  ☐ pdf417 (barcode generation)             │
│  ☐ pillow (image creation)                 │
│                                             │
│  Already installed:                         │
│  ✓ faker (data generation)                  │
│  ✓ reportlab (PDF creation)                 │
│                                             │
│  [Install Missing Libraries]                │
│                                             │
│  Advanced:                                  │
│  [Manual installation instructions]         │
│  [Use system package manager]               │
│  [Download portable version]                │
└─────────────────────────────────────────────┘
```

#### 3. Barcode Generation Failed (Individual License)
```
┌─────────────────────────────────────────────┐
│  ⚠️ License #47 Failed                      │
├─────────────────────────────────────────────┤
│  Barcode encoding error:                    │
│  Data exceeds maximum barcode capacity      │
│  (Name too long: "CHRISTOPHER ALEXANDER...")│
│                                             │
│  Options:                                   │
│  1. [Regenerate with shorter name]          │
│     → Use abbreviated middle name           │
│                                             │
│  2. [Skip barcode for this license]         │
│     → Generate card without barcode         │
│                                             │
│  3. [Skip this license entirely]            │
│     → Continue with remaining licenses      │
│                                             │
│  4. [View technical details]                │
│                                             │
│  [Apply] [Cancel Batch]                     │
└─────────────────────────────────────────────┘
```

#### 4. Disk Space Low
```
┌─────────────────────────────────────────────┐
│  💾 Low Disk Space                          │
├─────────────────────────────────────────────┤
│  Available: 150 MB                          │
│  Needed: 250 MB (estimated)                 │
│  Shortfall: 100 MB                          │
│                                             │
│  Quick solutions:                           │
│                                             │
│  1. [Reduce quantity]                       │
│     Generate 30 licenses instead of 50      │
│     Estimated space: 75 MB                  │
│                                             │
│  2. [Choose different location]             │
│     /media/external (50 GB available)       │
│                                             │
│  3. [Skip some formats]                     │
│     ☑ PDF ☑ DOCX → ☑ PDF only              │
│     Estimated savings: 120 MB               │
│                                             │
│  4. [Clean up old files]                    │
│     Found 500 MB in previous output/        │
│     [Open folder to review]                 │
│                                             │
│  [Apply Solution] [Cancel]                  │
└─────────────────────────────────────────────┘
```

#### 5. Batch Partially Failed
```
┌─────────────────────────────────────────────┐
│  ⚠️ Batch Completed with Issues             │
├─────────────────────────────────────────────┤
│  Generated: 47 of 50 licenses               │
│  Failed: 3 licenses                         │
│                                             │
│  Issues:                                    │
│  • License #12: Barcode encoding error      │
│  • License #34: Image generation timeout    │
│  • License #45: Data validation warning     │
│                                             │
│  Generated files:                           │
│  ✓ PDF with 47 cards                        │
│  ✓ DOCX with 47 cards                       │
│  ✓ 47 barcode images                        │
│  ✓ 47 data files                            │
│                                             │
│  Actions:                                   │
│  [Retry Failed Licenses]                    │
│  [Export Error Report]                      │
│  [View Generated Files]                     │
│  [Start New Batch]                          │
│                                             │
│  [Close]                                    │
└─────────────────────────────────────────────┘
```

### Undo/Redo System

```python
"""
Undo/Redo for Configuration (Not Generation)

What's undoable:
  ✓ Input field changes
  ✓ Checkbox toggles
  ✓ Dropdown selections
  ✓ File path changes

What's NOT undoable:
  ✗ File generation (would require storing all output)
  ✗ File deletion
  ✗ System operations

Implementation:
"""

class UndoableAction:
    timestamp: datetime
    field: str
    old_value: Any
    new_value: Any
    description: str

class UndoRedoManager:
    max_history: int = 50
    history: List[UndoableAction] = []
    current_position: int = 0

    def record_change(field: str, old: Any, new: Any):
        """Record a change for undo"""
        action = UndoableAction(
            timestamp=datetime.now(),
            field=field,
            old_value=old,
            new_value=new,
            description=f"Changed {field} from '{old}' to '{new}'"
        )
        # Clear redo history if we're not at the end
        history = history[:current_position + 1]
        history.append(action)
        current_position += 1

    def undo() -> Optional[UndoableAction]:
        """Undo last action"""
        if current_position > 0:
            current_position -= 1
            return history[current_position]
        return None

    def redo() -> Optional[UndoableAction]:
        """Redo next action"""
        if current_position < len(history) - 1:
            current_position += 1
            return history[current_position]
        return None

"""
UI Implementation:

Menu:
  Edit → Undo (Ctrl+Z)
  Edit → Redo (Ctrl+Shift+Z)

Status bar:
  "Changed quantity to 50" [Undo]

Tooltip on undo button:
  "Undo: Change quantity back to 10"
"""
```

---

## Progress & Status Communication

### Multi-Level Progress System

#### Level 1: Overall Progress Bar
```
┌─────────────────────────────────────────────┐
│  Generating 50 Licenses...                  │
│  [████████████████░░░░░░░░░░░] 68%          │
│  34 of 50 complete                          │
│  Estimated time remaining: 8 seconds        │
└─────────────────────────────────────────────┘
```

#### Level 2: Stage Indicators
```
┌─────────────────────────────────────────────┐
│  Progress                                   │
│                                             │
│  ✓ Data generation      (2.1s)              │
│  ✓ Barcode encoding     (5.3s)              │
│  ⟳ Image creation       (8.2s)  ← Current   │
│  ○ PDF generation                           │
│  ○ DOCX generation                          │
│                                             │
│  [Cancel]                                   │
└─────────────────────────────────────────────┘
```

#### Level 3: Detailed Item List (Expandable)
```
┌─────────────────────────────────────────────┐
│  ▼ Details (50 licenses)                    │
│                                             │
│  ✓ License #1  John Doe       CA  (0.5s)   │
│  ✓ License #2  Jane Smith     NY  (0.4s)   │
│  ✓ License #3  Bob Johnson    TX  (0.5s)   │
│  ...                                        │
│  ⟳ License #34 Alice Chen     FL  ...       │
│  ○ License #35 (pending)                    │
│  ○ License #36 (pending)                    │
│  ...                                        │
│                                             │
│  [Collapse Details]                         │
└─────────────────────────────────────────────┘
```

### Real-Time Status Updates

```python
"""
Status Update Events:

Event Type          Frequency    Message Format
─────────────────────────────────────────────────────
Start               Once         "Starting generation..."
Stage Begin         Per stage    "Generating barcodes..."
Item Progress       Per item     "Processing license #34..."
Item Complete       Per item     "✓ License #34"
Item Failed         On error     "✗ License #12 failed"
Stage Complete      Per stage    "✓ Barcodes complete (5.3s)"
Overall Complete    Once         "✓ Generated 50 licenses (15.2s)"

Status Bar:
  - Left: Current action
  - Center: Progress percentage
  - Right: Time elapsed / remaining
"""

class StatusUpdate:
    level: str  # "info", "success", "warning", "error"
    message: str
    progress: float  # 0.0 to 1.0
    current_item: int
    total_items: int
    elapsed_time: float
    estimated_remaining: float

class ProgressReporter:
    def report(self, update: StatusUpdate):
        """Update all UI elements"""
        # Update progress bar
        self.progress_bar.set_value(update.progress)

        # Update status text
        self.status_label.set_text(update.message)

        # Update detailed list
        self.item_list.update_item(
            update.current_item,
            status="processing"
        )

        # Update time estimates
        self.time_label.set_text(
            f"{format_time(update.elapsed_time)} / "
            f"{format_time(update.estimated_remaining)}"
        )
```

### Cancellation Handling

```
User clicks [Cancel] during generation:

┌─────────────────────────────────────────────┐
│  ⚠️ Cancel Generation?                      │
├─────────────────────────────────────────────┤
│  Current progress: 34 of 50 licenses        │
│                                             │
│  If you cancel:                             │
│  • 34 licenses already generated            │
│  • Partial files will be kept               │
│  • You can continue later                   │
│                                             │
│  Options:                                   │
│                                             │
│  1. [Cancel and Keep Generated]             │
│     → Save the 34 licenses created so far   │
│     → Generate PDF/DOCX with partial batch  │
│                                             │
│  2. [Cancel and Discard All]                │
│     → Delete all generated files            │
│     → Start fresh next time                 │
│                                             │
│  3. [Continue Generation]                   │
│     → Resume and finish the batch           │
│                                             │
│  [Choose Option]                            │
└─────────────────────────────────────────────┘
```

### Background Processing

```yaml
Long Operations as Background Tasks:

Advantages:
  - Non-blocking UI
  - User can prepare next batch
  - View previous results
  - Cancel without freezing

Implementation:
  - Separate thread for generation
  - Queue system for multiple batches
  - Progress polling (not blocking)
  - Notification when complete

UI:
  ┌──────────────────────────────────────┐
  │  Background Tasks                    │
  ├──────────────────────────────────────┤
  │  ⟳ Batch #1: Generating... 45%       │
  │  ○ Batch #2: Queued (50 licenses)    │
  │  ✓ Batch #3: Complete (25 licenses)  │
  │                                      │
  │  [View] [Cancel] [Clear Completed]   │
  └──────────────────────────────────────┘

Notifications:
  - System tray notification: "50 licenses generated"
  - Sound (optional, user preference)
  - Desktop notification (if app minimized)
  - In-app banner if user on different tab
```

---

## State Persistence & Autosave

### Configuration Persistence

```yaml
What to Save:
  ✓ Last used state code
  ✓ Last used quantity
  ✓ Output directory path
  ✓ Format preferences (PDF, DOCX, ODT)
  ✓ Advanced settings (DPI, font)
  ✓ Window size and position
  ✓ UI preferences (theme, layout)

Where to Save:
  Config file: ~/.aamva-generator/config.json

When to Save:
  - On app close (normal exit)
  - After successful generation
  - When user clicks "Save Settings"
  - Autosave every 30 seconds (if changed)

On App Start:
  1. Load last configuration
  2. Validate paths still exist
  3. Check dependencies still available
  4. Restore window position
  5. Show "Restored previous session" message
```

### Draft System

```yaml
Purpose:
  Save incomplete configurations for later

Use Cases:
  - User starts configuring, gets interrupted
  - User wants to prepare multiple different batches
  - User wants to save "template" configurations

Implementation:

UI:
  [Load Draft ▼] button shows:
    ┌───────────────────────────────────┐
    │  California - 50 licenses         │
    │  (Last edited: 2 hours ago)       │
    ├───────────────────────────────────┤
    │  New York - 100 licenses          │
    │  (Last edited: Yesterday)         │
    ├───────────────────────────────────┤
    │  All States Template              │
    │  (Last edited: Last week)         │
    ├───────────────────────────────────┤
    │  [New Draft]  [Manage Drafts]     │
    └───────────────────────────────────┘

Features:
  - Auto-save draft every 30 seconds
  - Name drafts manually or auto-name
  - Export/import drafts as JSON
  - Duplicate drafts for variations
  - Draft versioning (keep last 5)
```

### Session Recovery

```yaml
Crash Recovery:

On Unexpected Exit:
  - Write emergency save file
  - Include all current configuration
  - Include generation progress if running

On Next Launch:
  ┌──────────────────────────────────────┐
  │  ⚠️ Recover Previous Session?        │
  ├──────────────────────────────────────┤
  │  The app closed unexpectedly during  │
  │  your last session.                  │
  │                                      │
  │  Found:                              │
  │  • Configuration: 50 CA licenses     │
  │  • Partial progress: 23 of 50 done   │
  │  • Timestamp: 10 minutes ago         │
  │                                      │
  │  [Restore Session]                   │
  │  [Start Fresh]                       │
  │  [View Details]                      │
  └──────────────────────────────────────┘

Generation Recovery:
  - Resume from last completed license
  - Skip already-generated files
  - Verify integrity of partial output
  - Continue PDF/DOCX from checkpoint
```

---

## Implementation Examples

### Example 1: Real-Time State Code Validation

```python
"""
State Code Input Widget with Real-Time Validation
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, List
import difflib

class StateCodeInput(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Valid state codes from IIN_JURISDICTIONS
        self.valid_states = {
            "CA": "California", "NY": "New York", "TX": "Texas",
            # ... all states
        }

        # Validation state
        self.validation_state = "untouched"
        self.validation_timer = None

        self.create_widgets()

    def create_widgets(self):
        # Label
        self.label = ttk.Label(self, text="State Code:")
        self.label.grid(row=0, column=0, sticky="w")

        # Input with autocomplete
        self.var = tk.StringVar()
        self.var.trace_add("write", self.on_value_change)

        self.entry = ttk.Entry(self, textvariable=self.var, width=10)
        self.entry.grid(row=0, column=1, padx=5)
        self.entry.bind("<FocusIn>", self.on_focus)
        self.entry.bind("<FocusOut>", self.on_blur)

        # Status indicator
        self.status_label = ttk.Label(self, text="")
        self.status_label.grid(row=0, column=2)

        # Help text / Error message
        self.message_label = ttk.Label(
            self, text="", font=("", 9), foreground="gray"
        )
        self.message_label.grid(row=1, column=0, columnspan=3, sticky="w")

        # Suggestions dropdown (initially hidden)
        self.suggestions_listbox = tk.Listbox(self, height=5)
        self.suggestions_listbox.bind("<<ListboxSelect>>", self.on_suggestion_select)

    def on_focus(self, event):
        if self.validation_state == "untouched":
            self.show_hint("Enter 2-letter state code (e.g., CA, NY, TX)")

    def on_blur(self, event):
        # Validate when user leaves field
        self.validate_immediate()

    def on_value_change(self, *args):
        value = self.var.get().upper()

        # Cancel previous timer
        if self.validation_timer:
            self.after_cancel(self.validation_timer)

        # Update state
        if len(value) == 0:
            self.validation_state = "untouched"
            self.update_ui("untouched")
            return

        self.validation_state = "typing"
        self.update_ui("typing")

        # Schedule validation (debounced)
        self.validation_timer = self.after(300, self.validate)

    def validate(self):
        value = self.var.get().upper()

        # Show validating state
        self.validation_state = "validating"
        self.update_ui("validating")

        # Simulate async validation (in real app, this might check IIN)
        self.after(100, lambda: self.complete_validation(value))

    def complete_validation(self, value: str):
        # Check if exact match
        if value in self.valid_states:
            self.validation_state = "valid"
            self.show_success(f"✓ {self.valid_states[value]}")
            self.hide_suggestions()
            return

        # Check if partial match (for autocomplete)
        matches = [s for s in self.valid_states if s.startswith(value)]
        if len(matches) > 0:
            self.validation_state = "typing"
            self.show_suggestions(matches)
            return

        # No match - try fuzzy matching for suggestions
        close_matches = difflib.get_close_matches(
            value, self.valid_states.keys(), n=3, cutoff=0.6
        )

        if close_matches:
            self.validation_state = "invalid"
            suggestions_text = ", ".join(close_matches)
            self.show_error(
                f"✗ No state '{value}'. Did you mean: {suggestions_text}?"
            )
            self.show_suggestions(close_matches)
        else:
            self.validation_state = "invalid"
            self.show_error(f"✗ Invalid state code '{value}'")
            self.offer_random_state()

    def validate_immediate(self):
        """Force immediate validation (on blur)"""
        if self.validation_timer:
            self.after_cancel(self.validation_timer)
        self.validate()

    def update_ui(self, state: str):
        """Update visual appearance based on validation state"""
        style = ttk.Style()

        if state == "untouched":
            self.entry.configure(style="")
            self.status_label.configure(text="")
        elif state == "typing":
            self.entry.configure(style="Typing.TEntry")
            self.status_label.configure(text="⌨️", foreground="blue")
        elif state == "validating":
            self.status_label.configure(text="⟳", foreground="orange")
        elif state == "valid":
            self.entry.configure(style="Valid.TEntry")
            self.status_label.configure(text="✓", foreground="green")
        elif state == "invalid":
            self.entry.configure(style="Invalid.TEntry")
            self.status_label.configure(text="✗", foreground="red")

    def show_hint(self, message: str):
        self.message_label.configure(text=message, foreground="gray")

    def show_success(self, message: str):
        self.message_label.configure(text=message, foreground="green")

    def show_error(self, message: str):
        self.message_label.configure(text=message, foreground="red")

    def show_suggestions(self, suggestions: List[str]):
        """Show dropdown with suggestions"""
        self.suggestions_listbox.delete(0, tk.END)
        for s in suggestions:
            self.suggestions_listbox.insert(
                tk.END, f"{s} - {self.valid_states[s]}"
            )

        # Position below entry
        x = self.entry.winfo_x()
        y = self.entry.winfo_y() + self.entry.winfo_height()
        self.suggestions_listbox.place(x=x, y=y)

    def hide_suggestions(self):
        self.suggestions_listbox.place_forget()

    def on_suggestion_select(self, event):
        selection = self.suggestions_listbox.get(self.suggestions_listbox.curselection())
        state_code = selection.split(" - ")[0]
        self.var.set(state_code)
        self.hide_suggestions()

    def offer_random_state(self):
        """Show button to use random state"""
        # Add button to message area
        self.message_label.configure(
            text="✗ Invalid state code. [Use random state?]",
            foreground="red"
        )

# Usage
root = tk.Tk()
state_input = StateCodeInput(root)
state_input.pack(padx=20, pady=20)
root.mainloop()
```

### Example 2: Progress Dialog with Cancellation

```python
"""
Progress Dialog with Multi-Level Feedback
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
from typing import Callable, Optional

class ProgressDialog(tk.Toplevel):
    def __init__(self, parent, title: str, total_items: int):
        super().__init__(parent)

        self.title(title)
        self.total_items = total_items
        self.current_item = 0
        self.cancelled = False
        self.start_time = time.time()

        # Make modal
        self.transient(parent)
        self.grab_set()

        self.create_widgets()

        # Center on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)

        # Overall status
        self.status_label = ttk.Label(
            main_frame,
            text="Initializing...",
            font=("", 10, "bold")
        )
        self.status_label.pack(pady=(0, 10))

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            main_frame,
            variable=self.progress_var,
            maximum=100,
            length=400,
            mode="determinate"
        )
        self.progress_bar.pack(pady=5)

        # Progress text
        self.progress_label = ttk.Label(
            main_frame,
            text="0 of 0 complete"
        )
        self.progress_label.pack()

        # Time estimate
        self.time_label = ttk.Label(
            main_frame,
            text="Estimating time...",
            foreground="gray"
        )
        self.time_label.pack(pady=(5, 15))

        # Stage indicators frame
        stages_frame = ttk.LabelFrame(main_frame, text="Stages", padding=10)
        stages_frame.pack(fill="x", pady=(0, 15))

        self.stage_labels = {}
        stages = [
            "data_generation",
            "barcode_encoding",
            "image_creation",
            "pdf_generation",
            "docx_generation"
        ]

        for stage in stages:
            frame = ttk.Frame(stages_frame)
            frame.pack(fill="x", pady=2)

            icon = ttk.Label(frame, text="○", width=2)
            icon.pack(side="left")

            label = ttk.Label(frame, text=stage.replace("_", " ").title())
            label.pack(side="left", padx=5)

            time_label = ttk.Label(frame, text="", foreground="gray")
            time_label.pack(side="right")

            self.stage_labels[stage] = {
                "icon": icon,
                "label": label,
                "time": time_label
            }

        # Detailed items (collapsible)
        self.details_frame = ttk.LabelFrame(
            main_frame,
            text="▼ Details",
            padding=10
        )
        self.details_frame.pack(fill="both", expand=True, pady=(0, 15))

        # Scrollable list
        scroll_frame = ttk.Frame(self.details_frame)
        scroll_frame.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(scroll_frame)
        scrollbar.pack(side="right", fill="y")

        self.details_listbox = tk.Listbox(
            scroll_frame,
            yscrollcommand=scrollbar.set,
            height=10
        )
        self.details_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.details_listbox.yview)

        # Populate with pending items
        for i in range(self.total_items):
            self.details_listbox.insert(tk.END, f"○ License #{i+1} (pending)")

        # Cancel button
        self.cancel_button = ttk.Button(
            main_frame,
            text="Cancel",
            command=self.on_cancel
        )
        self.cancel_button.pack()

    def update_progress(
        self,
        current: int,
        total: int,
        message: str,
        current_stage: Optional[str] = None
    ):
        """Update progress from worker thread"""
        def update():
            self.current_item = current

            # Update progress bar
            progress = (current / total) * 100
            self.progress_var.set(progress)

            # Update labels
            self.status_label.configure(text=message)
            self.progress_label.configure(text=f"{current} of {total} complete")

            # Update time estimate
            elapsed = time.time() - self.start_time
            if current > 0:
                avg_time = elapsed / current
                remaining = (total - current) * avg_time
                self.time_label.configure(
                    text=f"Elapsed: {self.format_time(elapsed)} | "
                         f"Remaining: {self.format_time(remaining)}"
                )

            # Update current item in list
            if current > 0 and current <= total:
                self.details_listbox.delete(current - 1)
                self.details_listbox.insert(
                    current - 1,
                    f"⟳ License #{current} (processing...)"
                )
                self.details_listbox.see(current - 1)

        self.after(0, update)

    def mark_item_complete(self, index: int, name: str, duration: float):
        """Mark an item as complete"""
        def update():
            self.details_listbox.delete(index)
            self.details_listbox.insert(
                index,
                f"✓ License #{index+1} {name} ({duration:.1f}s)"
            )
            self.details_listbox.itemconfig(index, foreground="green")

        self.after(0, update)

    def mark_item_failed(self, index: int, error: str):
        """Mark an item as failed"""
        def update():
            self.details_listbox.delete(index)
            self.details_listbox.insert(
                index,
                f"✗ License #{index+1} FAILED: {error}"
            )
            self.details_listbox.itemconfig(index, foreground="red")

        self.after(0, update)

    def update_stage(self, stage: str, status: str, duration: float = 0):
        """Update stage indicator

        Args:
            stage: Stage name
            status: "pending", "active", "complete", "error"
            duration: Time taken (for complete status)
        """
        def update():
            if stage not in self.stage_labels:
                return

            labels = self.stage_labels[stage]

            if status == "pending":
                labels["icon"].configure(text="○", foreground="gray")
            elif status == "active":
                labels["icon"].configure(text="⟳", foreground="blue")
            elif status == "complete":
                labels["icon"].configure(text="✓", foreground="green")
                labels["time"].configure(text=f"({duration:.1f}s)")
            elif status == "error":
                labels["icon"].configure(text="✗", foreground="red")

        self.after(0, update)

    def on_cancel(self):
        """Handle cancel button click"""
        self.cancelled = True
        self.cancel_button.configure(state="disabled", text="Cancelling...")
        self.status_label.configure(text="Cancelling generation...")

    def complete(self, success: bool, message: str):
        """Mark generation as complete"""
        def update():
            self.cancel_button.configure(text="Close")
            self.cancel_button.configure(state="normal")
            self.cancel_button.configure(command=self.destroy)

            if success:
                self.status_label.configure(text="✓ " + message)
                elapsed = time.time() - self.start_time
                self.time_label.configure(
                    text=f"Total time: {self.format_time(elapsed)}"
                )
            else:
                self.status_label.configure(text="✗ " + message)

        self.after(0, update)

    @staticmethod
    def format_time(seconds: float) -> str:
        """Format seconds as human-readable time"""
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            mins = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{mins}m {secs}s"
        else:
            hours = int(seconds // 3600)
            mins = int((seconds % 3600) // 60)
            return f"{hours}h {mins}m"

# Example usage
def simulate_generation(dialog: ProgressDialog):
    """Simulate license generation with progress updates"""
    stages = [
        ("data_generation", 2.0),
        ("barcode_encoding", 5.0),
        ("image_creation", 8.0),
        ("pdf_generation", 2.0),
        ("docx_generation", 3.0)
    ]

    for stage_name, duration in stages:
        if dialog.cancelled:
            dialog.complete(False, "Generation cancelled")
            return

        dialog.update_stage(stage_name, "active")
        time.sleep(duration)
        dialog.update_stage(stage_name, "complete", duration)

    # Simulate per-item processing
    for i in range(dialog.total_items):
        if dialog.cancelled:
            dialog.complete(
                False,
                f"Generation cancelled at {i} of {dialog.total_items}"
            )
            return

        # Simulate processing time
        time.sleep(0.5)

        # Update progress
        dialog.update_progress(
            i + 1,
            dialog.total_items,
            f"Processing license #{i+1}..."
        )

        # Mark complete (or failed randomly for demo)
        import random
        if random.random() < 0.05:  # 5% failure rate
            dialog.mark_item_failed(i, "Barcode encoding error")
        else:
            dialog.mark_item_complete(i, "John Doe", 0.5)

    dialog.complete(True, f"Generated {dialog.total_items} licenses successfully!")

# Demo
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    dialog = ProgressDialog(root, "Generating Licenses", 50)

    # Run generation in background thread
    thread = threading.Thread(
        target=simulate_generation,
        args=(dialog,),
        daemon=True
    )
    thread.start()

    root.mainloop()
```

### Example 3: Error Recovery Dialog

```python
"""
Sophisticated Error Recovery Dialog
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Callable, Optional
from enum import Enum

class RecoveryAction(Enum):
    RETRY = "retry"
    SKIP = "skip"
    MODIFY = "modify"
    CANCEL = "cancel"
    AUTO_FIX = "auto_fix"

class ErrorRecoveryDialog(tk.Toplevel):
    def __init__(
        self,
        parent,
        error_type: str,
        error_message: str,
        details: dict,
        recovery_options: List[dict]
    ):
        super().__init__(parent)

        self.title("Issue Detected")
        self.error_type = error_type
        self.error_message = error_message
        self.details = details
        self.recovery_options = recovery_options
        self.selected_action = None
        self.action_data = None

        # Make modal
        self.transient(parent)
        self.grab_set()

        self.create_widgets()

        # Center on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)

        # Icon and title
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill="x", pady=(0, 15))

        icon_label = ttk.Label(title_frame, text="⚠️", font=("", 24))
        icon_label.pack(side="left", padx=(0, 10))

        title_label = ttk.Label(
            title_frame,
            text=self.error_type,
            font=("", 14, "bold")
        )
        title_label.pack(side="left")

        # Error message
        message_label = ttk.Label(
            main_frame,
            text=self.error_message,
            wraplength=400
        )
        message_label.pack(fill="x", pady=(0, 15))

        # Details (collapsible)
        if self.details:
            details_frame = ttk.LabelFrame(
                main_frame,
                text="▼ Technical Details",
                padding=10
            )
            details_frame.pack(fill="x", pady=(0, 15))

            for key, value in self.details.items():
                detail_frame = ttk.Frame(details_frame)
                detail_frame.pack(fill="x", pady=2)

                ttk.Label(
                    detail_frame,
                    text=f"{key}:",
                    font=("", 9, "bold")
                ).pack(side="left")

                ttk.Label(
                    detail_frame,
                    text=str(value),
                    font=("", 9)
                ).pack(side="left", padx=(5, 0))

        # Recovery options
        options_frame = ttk.LabelFrame(
            main_frame,
            text="Recovery Options",
            padding=10
        )
        options_frame.pack(fill="both", expand=True, pady=(0, 15))

        self.option_var = tk.StringVar()
        self.option_widgets = {}

        for i, option in enumerate(self.recovery_options):
            option_frame = ttk.Frame(options_frame)
            option_frame.pack(fill="x", pady=5)

            # Radio button
            radio = ttk.Radiobutton(
                option_frame,
                text="",
                variable=self.option_var,
                value=option["id"],
                command=lambda opt=option: self.on_option_select(opt)
            )
            radio.pack(side="left")

            # Option content frame
            content_frame = ttk.Frame(option_frame)
            content_frame.pack(side="left", fill="x", expand=True, padx=(5, 0))

            # Title
            title = ttk.Label(
                content_frame,
                text=option["title"],
                font=("", 10, "bold")
            )
            title.pack(anchor="w")

            # Description
            desc = ttk.Label(
                content_frame,
                text=option["description"],
                wraplength=350,
                foreground="gray"
            )
            desc.pack(anchor="w")

            # Additional inputs (if needed)
            if "input" in option:
                input_frame = ttk.Frame(content_frame)
                input_frame.pack(fill="x", pady=(5, 0))

                if option["input"]["type"] == "text":
                    entry = ttk.Entry(
                        input_frame,
                        width=40
                    )
                    entry.insert(0, option["input"].get("default", ""))
                    entry.pack(side="left")
                    self.option_widgets[option["id"]] = entry

                elif option["input"]["type"] == "choice":
                    combo = ttk.Combobox(
                        input_frame,
                        values=option["input"]["choices"],
                        width=37,
                        state="readonly"
                    )
                    combo.current(0)
                    combo.pack(side="left")
                    self.option_widgets[option["id"]] = combo

            # Recommended badge
            if option.get("recommended", False):
                badge = ttk.Label(
                    option_frame,
                    text="RECOMMENDED",
                    font=("", 8),
                    foreground="green"
                )
                badge.pack(side="right", padx=(5, 0))

        # Select first option by default
        if self.recovery_options:
            self.option_var.set(self.recovery_options[0]["id"])

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")

        ttk.Button(
            button_frame,
            text="Cancel",
            command=self.on_cancel
        ).pack(side="right", padx=(5, 0))

        ttk.Button(
            button_frame,
            text="Apply",
            command=self.on_apply,
            style="Accent.TButton"
        ).pack(side="right")

    def on_option_select(self, option: dict):
        """Handle option selection"""
        # Could enable/disable related widgets here
        pass

    def on_apply(self):
        """Apply selected recovery action"""
        selected_id = self.option_var.get()

        if not selected_id:
            return

        # Get selected option
        selected_option = next(
            (opt for opt in self.recovery_options if opt["id"] == selected_id),
            None
        )

        if not selected_option:
            return

        # Get input data if any
        if selected_id in self.option_widgets:
            widget = self.option_widgets[selected_id]
            if isinstance(widget, ttk.Entry):
                self.action_data = widget.get()
            elif isinstance(widget, ttk.Combobox):
                self.action_data = widget.get()

        self.selected_action = selected_option["action"]
        self.destroy()

    def on_cancel(self):
        """Cancel recovery"""
        self.selected_action = RecoveryAction.CANCEL
        self.destroy()

# Example usage
def show_barcode_error_recovery(parent):
    """Show recovery dialog for barcode encoding error"""

    recovery_options = [
        {
            "id": "auto_fix",
            "title": "Regenerate with shorter name",
            "description": "Automatically abbreviate middle name and retry",
            "action": RecoveryAction.AUTO_FIX,
            "recommended": True
        },
        {
            "id": "skip_barcode",
            "title": "Skip barcode for this license",
            "description": "Generate card without barcode (data will still be saved)",
            "action": RecoveryAction.SKIP
        },
        {
            "id": "skip_license",
            "title": "Skip this license entirely",
            "description": "Continue with remaining licenses",
            "action": RecoveryAction.SKIP
        },
        {
            "id": "manual_fix",
            "title": "Manually adjust data",
            "description": "Edit the name to fit",
            "action": RecoveryAction.MODIFY,
            "input": {
                "type": "text",
                "default": "CHRISTOPHER ALEXANDER JOHNSON"
            }
        }
    ]

    dialog = ErrorRecoveryDialog(
        parent,
        error_type="Barcode Encoding Failed",
        error_message=(
            "License #47: The name is too long to fit in the barcode "
            "(maximum 80 characters). The barcode encoder cannot fit "
            "'CHRISTOPHER ALEXANDER JOHNSON' in the available space."
        ),
        details={
            "License": "#47",
            "Name": "CHRISTOPHER ALEXANDER JOHNSON",
            "Length": "33 characters",
            "Maximum": "30 characters",
            "Excess": "3 characters"
        },
        recovery_options=recovery_options
    )

    parent.wait_window(dialog)

    return dialog.selected_action, dialog.action_data

# Demo
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("300x200")

    def show_demo():
        action, data = show_barcode_error_recovery(root)
        print(f"Selected action: {action}")
        print(f"Action data: {data}")

    ttk.Button(
        root,
        text="Show Error Recovery Dialog",
        command=show_demo
    ).pack(expand=True)

    root.mainloop()
```

---

## Anti-Patterns to Avoid

### 1. Modal Error Popups for Everything

**Bad:**
```python
# User generates 50 licenses
# License #23 fails
messagebox.showerror("Error", "License #23 failed: Barcode error")
# Generation stops
# User loses all progress
```

**Good:**
```python
# License #23 fails
# Log error, mark item as failed
# Show inline error in progress list
# Continue with remaining licenses
# Show summary at end with recovery options
```

### 2. Technical Error Messages

**Bad:**
```
ValueError: Expected 2-letter state code, got 'California'
Traceback (most recent call last):
  File "generate.py", line 145, in validate_state
    raise ValueError(...)
```

**Good:**
```
State Code Issue

You entered: "California"
We need the 2-letter code instead.

Did you mean: CA (California)?

[Use CA] [Choose different state]
```

### 3. No Progress Indication

**Bad:**
```python
# Click "Generate"
# Application freezes
# No feedback for 30 seconds
# User thinks it crashed
```

**Good:**
```python
# Click "Generate"
# Immediate feedback: "Starting generation..."
# Progress bar appears
# Real-time updates: "Processing license #23..."
# Time estimate: "~15 seconds remaining"
```

### 4. Losing Data on Error

**Bad:**
```python
# User configures 50 California licenses
# Clicks generate
# Error: "Dependency missing"
# Dialog closes
# User has to re-enter everything
```

**Good:**
```python
# User configures 50 California licenses
# Clicks generate
# Error detected
# Configuration auto-saved as draft
# After fixing dependency, user can resume with [Continue Previous]
```

### 5. Batch Validation Without Context

**Bad:**
```python
messagebox.showerror("Errors",
    "Invalid state code\n"
    "Invalid quantity\n"
    "Invalid output path"
)
# Which field has which error?
# User has to guess
```

**Good:**
```python
# Each field shows inline error
# State field: Red border + "Invalid state 'XX'"
# Quantity field: Red border + "Must be between 1-10000"
# Path field: Red border + "Directory doesn't exist"
# Generate button disabled until all fixed
```

### 6. No Cancellation Option

**Bad:**
```python
# User starts generating 1000 licenses
# Realizes they made a mistake
# No way to stop
# Have to wait 5 minutes
```

**Good:**
```python
# Progress dialog has [Cancel] button
# On cancel, shows options:
#   - Keep generated files
#   - Discard all
#   - Continue anyway
# Graceful cleanup
```

### 7. Silent Failures

**Bad:**
```python
# Generates 50 licenses
# 3 fail silently
# User doesn't notice
# Output has 47 licenses
```

**Good:**
```python
# Generates 50 licenses
# 3 fail with specific errors logged
# Final summary:
#   "Generated 47 of 50 licenses"
#   "3 failed (click for details)"
# Option to retry failed ones
```

### 8. No Undo

**Bad:**
```python
# User accidentally changes state from CA to NY
# No way to undo
# Has to remember what it was
```

**Good:**
```python
# Every change is recorded
# Ctrl+Z to undo
# Ctrl+Shift+Z to redo
# Status bar shows: "Changed state to NY [Undo]"
```

---

## Conclusion

### Key Principles Summary

1. **Prevention > Detection > Recovery**
   - Design inputs that prevent errors
   - Validate in real-time as users type
   - Offer recovery when errors occur

2. **Context > Modality**
   - Show errors inline, not in popups
   - Keep user in their workflow
   - Don't interrupt with modals unless critical

3. **Guidance > Blame**
   - Tell users how to fix, not just what's wrong
   - Offer suggestions and examples
   - Auto-correct when safe

4. **Continuity > Perfection**
   - Allow partial success
   - Save progress frequently
   - Enable resumption after errors

5. **Transparency > Silence**
   - Show what's happening
   - Communicate progress
   - Explain delays

6. **Simplicity > Completeness**
   - Don't show all errors at once
   - Progressive disclosure
   - Prioritize by severity

### Implementation Roadmap

**Phase 1: Foundation (Week 1-2)**
- [ ] Input validation framework
- [ ] Real-time validation for all fields
- [ ] Visual feedback system (colors, icons, borders)
- [ ] Inline error messages

**Phase 2: Advanced Validation (Week 3-4)**
- [ ] Fuzzy matching and suggestions
- [ ] Autocomplete for state codes
- [ ] Path validation with auto-create
- [ ] Dependency checking on startup

**Phase 3: Progress & Status (Week 5-6)**
- [ ] Progress dialog with stages
- [ ] Real-time item-level feedback
- [ ] Time estimation
- [ ] Cancellation handling

**Phase 4: Recovery (Week 7-8)**
- [ ] Error recovery dialogs
- [ ] Per-license error handling
- [ ] Batch partial success
- [ ] Retry mechanisms

**Phase 5: Persistence (Week 9-10)**
- [ ] Configuration autosave
- [ ] Draft system
- [ ] Session recovery
- [ ] Undo/redo

**Phase 6: Polish (Week 11-12)**
- [ ] Accessibility improvements
- [ ] Help system
- [ ] User testing
- [ ] Performance optimization

### Success Metrics

**Measure effectiveness by:**
- Error rate: < 5% of generations fail
- Recovery rate: > 95% of errors recovered without data loss
- User satisfaction: > 4.5/5 rating
- Support tickets: < 2% related to error handling
- Time to resolution: < 30 seconds for common errors

---

**Document Status:** Design Specification - Ready for Review
**Next Steps:** Review with development team, create prototypes, user testing
