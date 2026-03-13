# Error Handling Visual Architecture Guide
## AAMVA License Generator GUI

**Version:** 1.0
**Date:** 2025-11-20
**Purpose:** Visual reference for error handling system architecture

---

## System Overview Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     AAMVA LICENSE GENERATOR GUI                          │
│                   Error Handling & Validation System                     │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                ┌───────────────────┼───────────────────┐
                │                   │                   │
                ▼                   ▼                   ▼
    ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
    │   PREVENTION     │  │    DETECTION     │  │    RECOVERY      │
    │    LAYER         │  │      LAYER       │  │     LAYER        │
    └──────────────────┘  └──────────────────┘  └──────────────────┘
            │                      │                      │
            │                      │                      │
    ┌───────┴────────┐    ┌────────┴─────────┐   ┌──────┴──────────┐
    │                │    │                  │   │                 │
    ▼                ▼    ▼                  ▼   ▼                 ▼
┌────────┐  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│Const-  │  │Smart     │ │Real-Time │ │Pre-Sub   │ │Graceful  │ │Recovery  │
│rained  │  │Defaults  │ │Validation│ │Validation│ │Degrade   │ │Workflows │
│Inputs  │  │          │ │          │ │          │ │          │ │          │
└────────┘  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘
    │            │            │              │           │             │
    │            │            │              │           │             │
    └────────────┴────────────┴──────────────┴───────────┴─────────────┘
                                    │
                                    ▼
                        ┌───────────────────────┐
                        │  USER FEEDBACK LAYER   │
                        ├───────────────────────┤
                        │ • Inline Messages     │
                        │ • Visual Indicators   │
                        │ • Progress Reports    │
                        │ • Recovery Dialogs    │
                        │ • Status Updates      │
                        └───────────────────────┘
```

---

## Error Flow Diagram

### Scenario 1: Invalid State Code

```
User Action Flow:

1. User focuses state field
   │
   ▼
   [Show hint: "Enter 2-letter code (e.g., CA, NY)"]
   │
   │
2. User types "C"
   │
   ▼
   [Show dropdown: CA, CO, CT...]
   [Blue border, typing indicator]
   │
   │
3. User types "CA"
   │
   ▼
   [Exact match found]
   [Green checkmark appears]
   [Show preview: "California (636014)"]
   │
   │
4. User types "CAT" (continues typing)
   │
   ▼
   [No match found]
   [Orange warning border]
   [Show: "No state 'CAT'. Did you mean: CA, CT?"]
   [Show suggestions dropdown]
   │
   ├──> User clicks suggestion → Corrected ✓
   │
   └──> User deletes back to "CA" → Valid ✓
```

### Scenario 2: Barcode Generation Failure

```
Generation Flow with Error:

1. Start batch (50 licenses)
   │
   ▼
   [Progress dialog appears]
   [Stage: Data Generation ⟳]
   │
   │
2. License #1-46 succeed
   │
   ▼
   [Progress: 46/50 complete]
   [Each marked with ✓]
   │
   │
3. License #47 barcode fails
   │
   ▼
   [Error caught]
   [License #47 marked with ✗]
   [Show recovery dialog]
   │
   ├─────────────────┬──────────────────┬──────────────────┐
   │                 │                  │                  │
   ▼                 ▼                  ▼                  ▼
[Auto-fix]      [Skip barcode]    [Skip license]   [Manual edit]
   │                 │                  │                  │
   ▼                 ▼                  ▼                  ▼
Retry with     Continue without   Move to next     Show edit
shortened         barcode            license         dialog
data                │                  │                  │
   │                 │                  │                  │
   ├─────────────────┴──────────────────┴──────────────────┘
   │
   ▼
4. Continue with licenses #48-50
   │
   ▼
   [Final summary]
   [49 successful, 1 with modified data]
   [All files generated]
   ✓ Success with notes
```

---

## Validation State Machine

```
┌──────────────────────────────────────────────────────────────────┐
│                    FIELD VALIDATION STATES                        │
└──────────────────────────────────────────────────────────────────┘

                    ┌──────────────┐
            ┌──────>│  UNTOUCHED   │<──────┐
            │       └──────────────┘       │
            │       No interaction         │
            │       Gray placeholder       │
            │                              │
        [Clear]                        [Focus]
            │                              │
            │       ┌──────────────┐       │
            └───────│    TYPING    │<──────┘
                    └──────────────┘
                    Blue border
                    Active input
                         │
                    [Debounce 300ms]
                         │
                         ▼
                    ┌──────────────┐
                    │  VALIDATING  │
                    └──────────────┘
                    Yellow spinner
                    Checking rules
                         │
            ┌────────────┴────────────┐
            │                         │
       [Valid Rules]            [Invalid Rules]
            │                         │
            ▼                         ▼
     ┌──────────────┐          ┌──────────────┐
     │    VALID     │          │   INVALID    │
     └──────────────┘          └──────────────┘
     Green checkmark           Red X
     Success message           Error message
            │                  Suggestions shown
            │                         │
            │                    [User corrects]
            │                         │
            └─────────────────────────┘
                         │
                    [Continue]
                         │
                         ▼
                  [Form Submit]


Special States:

     ┌──────────────┐              ┌──────────────┐
     │   WARNING    │              │  CORRECTING  │
     └──────────────┘              └──────────────┘
     Orange indicator              Orange border
     Valid but has issue           Auto-fix preview
     Can proceed                   User reviewing fix
```

---

## Progress Reporting Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                  PROGRESS REPORTING SYSTEM                       │
└─────────────────────────────────────────────────────────────────┘

                    ┌──────────────────┐
                    │  Main Thread     │
                    │  (UI)            │
                    └────────┬─────────┘
                             │
                             │ Start Generation
                             │
                             ▼
                    ┌──────────────────┐
                    │  Worker Thread   │
                    │  (Generation)    │
                    └────────┬─────────┘
                             │
                ┌────────────┼────────────┐
                │            │            │
                ▼            ▼            ▼
        ┌──────────┐  ┌──────────┐  ┌──────────┐
        │ Data Gen │  │ Barcode  │  │ Document │
        │          │  │ Encode   │  │ Creation │
        └────┬─────┘  └────┬─────┘  └────┬─────┘
             │             │             │
             │ Events      │ Events      │ Events
             │             │             │
             └─────────────┴─────────────┘
                         │
                         │ Progress Events
                         │
                         ▼
                ┌─────────────────┐
                │ Event Queue     │
                └────────┬────────┘
                         │
                         │ Poll (100ms)
                         │
                         ▼
                ┌─────────────────┐
                │ UI Update       │
                │ (Main Thread)   │
                └────────┬────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Progress Bar │ │ Status Text  │ │ Item List    │
│ [████░░░░░]  │ │ "23/50..."   │ │ ✓ #1         │
│ 46%          │ │              │ │ ✓ #2         │
│              │ │              │ │ ⟳ #23        │
└──────────────┘ └──────────────┘ └──────────────┘


Event Types:

┌────────────────────────────────────────────────┐
│ Event Type        │ Update Frequency          │
├────────────────────────────────────────────────┤
│ Stage Begin       │ Per stage (~5 times)      │
│ Stage Complete    │ Per stage (~5 times)      │
│ Item Start        │ Per item (50 times)       │
│ Item Complete     │ Per item (50 times)       │
│ Item Failed       │ On error (rare)           │
│ Progress Update   │ Throttled (max 10/sec)    │
│ Time Estimate     │ Every second              │
│ Memory Warning    │ On threshold (rare)       │
└────────────────────────────────────────────────┘
```

---

## Feedback Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│              USER FEEDBACK VISUAL HIERARCHY                      │
└─────────────────────────────────────────────────────────────────┘

LEVEL 1: SUBTLE (Proactive, Non-Intrusive)
─────────────────────────────────────────────
┌─────────────────────────────────────┐
│ State Code: [__________]            │  ← Gray hint text below
│ Enter 2-letter code (e.g., CA, NY)  │
└─────────────────────────────────────┘

Characteristics:
• Gray color (#666)
• Small font (12px)
• Below field
• Only when focused
• Disappears when typing starts


LEVEL 2: INFORMATIVE (Helpful Context)
─────────────────────────────────────────────
┌─────────────────────────────────────┐
│ Quantity: [50___] ✓                 │
│ ℹ️  This will take ~25 seconds      │  ← Blue info
└─────────────────────────────────────┘

Characteristics:
• Blue color (#0066cc)
• ℹ️ info icon
• Normal font (13px)
• Inline below field
• Provides context, not error


LEVEL 3: WARNING (Attention Recommended)
─────────────────────────────────────────────
┌─────────────────────────────────────┐
│ Quantity: [500__] ⚠️                │
│ ⚠️  Large batch will take ~2 minutes │  ← Orange warning
└─────────────────────────────────────┘

Characteristics:
• Orange color (#ff9900)
• ⚠️ warning icon
• Bold font
• Inline below field
• Can proceed, but user should know


LEVEL 4: ERROR (Must Fix)
─────────────────────────────────────────────
┌─────────────────────────────────────┐
│ State Code: [XX____] ✗              │
│ ✗ State code 'XX' not recognized    │  ← Red error
│ Did you mean: CA, CT, CO?           │  ← Suggestions
└─────────────────────────────────────┘

Characteristics:
• Red color (#cc0000)
• ✗ error icon
• Bold font
• Inline below field
• Blocks proceed
• Actionable suggestions


LEVEL 5: CRITICAL (System Issue)
─────────────────────────────────────────────
┌─────────────────────────────────────┐
│ ⛔ Missing Dependency: pdf417        │  ← Full-width banner
│ Barcode generation requires pdf417. │
│ [Install Now] [Learn More]          │
└─────────────────────────────────────┘

Characteristics:
• Red background (#cc0000)
• White text
• Full-width banner
• Top of application
• Blocks all operations
• Clear action buttons
```

---

## Error Recovery Decision Tree

```
┌─────────────────────────────────────────────────────────────────┐
│                    ERROR RECOVERY FLOW                           │
└─────────────────────────────────────────────────────────────────┘

                        [Error Occurs]
                              │
                              ▼
                    ┌─────────────────┐
                    │ Can Auto-Fix?   │
                    └────────┬────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
               YES                        NO
                │                         │
                ▼                         ▼
    ┌───────────────────┐    ┌───────────────────┐
    │ Show Auto-Fix     │    │ Is Critical?      │
    │ Preview           │    └────────┬──────────┘
    │ [Apply] [Cancel]  │             │
    └─────────┬─────────┘   ┌─────────┴─────────┐
              │             │                   │
         [Apply]           YES                  NO
              │             │                   │
              ▼             ▼                   ▼
    ┌───────────────┐ ┌──────────┐  ┌─────────────────┐
    │ Fixed!        │ │ Must Fix │  │ Can Continue?   │
    │ Continue      │ │ Blocking │  └────────┬────────┘
    └───────────────┘ │ Modal    │           │
                      └──────────┘  ┌────────┴────────┐
                                    │                 │
                                   YES                NO
                                    │                 │
                                    ▼                 ▼
                         ┌─────────────────┐  ┌────────────┐
                         │ Graceful Degrade│  │ Recovery   │
                         │ • Skip item     │  │ Dialog     │
                         │ • Partial save  │  │ Multiple   │
                         │ • Continue rest │  │ Options    │
                         └─────────────────┘  └────────────┘


DECISION MATRIX:

Error Type          │ Can Auto-Fix? │ Is Critical? │ Can Continue?
────────────────────┼───────────────┼──────────────┼──────────────
Missing Dependency  │ Yes (install) │ Yes          │ No
Invalid State       │ Yes (suggest) │ No           │ No
Barcode Too Long    │ Yes (shorten) │ No           │ Yes (skip)
Disk Full           │ No            │ Yes          │ No
File Locked         │ No            │ No           │ Yes (retry)
Network Error       │ No            │ No           │ Yes (queue)
Font Missing        │ Yes (fallback)│ No           │ Yes (degrade)
Permission Denied   │ No            │ No           │ Yes (new path)
```

---

## Component Interaction Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│          ERROR HANDLING COMPONENT INTERACTION                    │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐
│   InputField     │
│   Component      │
└────────┬─────────┘
         │ getValue()
         │ onChange()
         ▼
┌──────────────────┐     validates     ┌──────────────────┐
│  Validation      │◄──────────────────│  ValidationRule  │
│  Framework       │                   │  • Required()    │
└────────┬─────────┘                   │  • EnumValue()   │
         │                             │  • RangeCheck()  │
         │ ValidationResult            └──────────────────┘
         │
         ├──> Valid?
         │    │
         │    ├─> YES ──> ┌─────────────────┐
         │    │           │ SuccessFeedback │
         │    │           │ • Green border  │
         │    │           │ • Checkmark     │
         │    │           └─────────────────┘
         │    │
         │    └─> NO ──>  ┌─────────────────┐
         │                │ ErrorFeedback   │
         │                │ • Red border    │
         │                │ • Error message │
         │                │ • Suggestions   │
         │                └────────┬────────┘
         │                         │
         │                         ▼
         │                ┌─────────────────┐
         │                │ SuggestionBox   │
         │                │ • Fuzzy matches │
         │                │ • Quick fixes   │
         │                └─────────────────┘
         ▼
┌──────────────────┐
│   Generate       │
│   Button         │
│   (enabled when  │
│   all valid)     │
└────────┬─────────┘
         │ onClick()
         │
         ▼
┌──────────────────┐
│  Pre-Submit      │
│  Validator       │
│  (final check)   │
└────────┬─────────┘
         │
         │ All valid?
         │
         ├─> YES ──> ┌─────────────────┐
         │           │  GenerateTask   │
         │           └────────┬────────┘
         │                    │
         │                    ▼
         │           ┌─────────────────┐
         │           │ ProgressDialog  │
         │           └────────┬────────┘
         │                    │
         │                    │ Events
         │                    │
         │           ┌────────┴────────┐
         │           │                 │
         │           ▼                 ▼
         │    ┌──────────┐      ┌──────────┐
         │    │ Success  │      │  Error   │
         │    │ Summary  │      │ Recovery │
         │    └──────────┘      └─────┬────┘
         │                            │
         │                            ▼
         │                   ┌─────────────────┐
         │                   │ RecoveryDialog  │
         │                   │ • Retry         │
         │                   │ • Skip          │
         │                   │ • Modify        │
         │                   └─────────────────┘
         │
         └─> NO ──>  ┌─────────────────┐
                     │ Highlight Errors│
                     │ Focus first     │
                     └─────────────────┘
```

---

## State Persistence Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                   STATE PERSISTENCE SYSTEM                       │
└─────────────────────────────────────────────────────────────────┘

Session Timeline:
─────────────────

    T=0                T=30s              T=5min            T=End
     │                  │                   │                 │
     ▼                  ▼                   ▼                 ▼
 [App Start]      [Auto-save]        [Auto-save]      [Clean Exit]
     │                  │                   │                 │
     ├─> Load Config    ├─> Save Draft      ├─> Save Draft   ├─> Save Config
     │   • Last state   │   • Current form  │   • Current     │   • Final state
     │   • Window pos   │   • Timestamp     │     form        │   • All settings
     │   • Preferences  │                   │                 │
     │                  │                   │                 │
     ▼                  ▼                   ▼                 ▼
┌──────────┐      ┌──────────┐       ┌──────────┐     ┌──────────┐
│ Restore  │      │ .draft   │       │ .draft   │     │ config   │
│ Previous │      │ .json    │       │ .json    │     │ .json    │
└──────────┘      └──────────┘       └──────────┘     └──────────┘


Crash Recovery:
───────────────

     [App Crash]
         │
         ├─> Emergency Save
         │   • Dump current state
         │   • .recovery.json
         │   • Timestamp
         │
         ▼
    [Next Launch]
         │
         ├─> Detect .recovery.json
         │
         ▼
┌──────────────────────┐
│ Recovery Dialog      │
│ "Restore session?"   │
│ [Yes] [No] [Details] │
└──────────┬───────────┘
           │
      ┌────┴────┐
      │         │
     YES        NO
      │         │
      ▼         ▼
┌──────────┐ ┌──────────┐
│ Restore  │ │ Clean    │
│ State    │ │ Start    │
│ Continue │ │          │
└──────────┘ └──────────┘


File Structure:
───────────────

~/.aamva-generator/
├── config.json              ← Main configuration
├── drafts/
│   ├── draft_001.json      ← Saved draft "CA 50 licenses"
│   ├── draft_002.json      ← Saved draft "NY 100 licenses"
│   └── autosave.json       ← Auto-saved current work
├── recovery/
│   └── crash_2025-11-20.json  ← Emergency save
└── logs/
    └── error.log           ← Error history
```

---

## Keyboard Navigation Map

```
┌─────────────────────────────────────────────────────────────────┐
│                    KEYBOARD SHORTCUTS                            │
└─────────────────────────────────────────────────────────────────┘

NAVIGATION:
───────────
Tab             →  Next field
Shift+Tab       →  Previous field
Enter           →  Submit form / Confirm dialog
Escape          →  Close dialog / Cancel operation
Space           →  Toggle checkbox / Open dropdown


EDITING:
────────
Ctrl+Z          →  Undo last change
Ctrl+Shift+Z    →  Redo last undone change
Ctrl+A          →  Select all in field
Ctrl+C          →  Copy
Ctrl+V          →  Paste


VALIDATION:
───────────
Down Arrow      →  Show suggestions (when available)
Up/Down         →  Navigate suggestions
Enter           →  Apply selected suggestion
Escape          →  Close suggestions


ACCESSIBILITY:
──────────────
Ctrl+H          →  Toggle help panel
Ctrl+/          →  Show keyboard shortcuts
F1              →  Context help for focused field


Focus Order:
────────────
    ┌─────────────┐
    │ State Code  │ ←─── Tab starts here
    └──────┬──────┘
           │ Tab
           ▼
    ┌─────────────┐
    │ Quantity    │
    └──────┬──────┘
           │ Tab
           ▼
    ┌─────────────┐
    │ Output Path │
    └──────┬──────┘
           │ Tab
           ▼
    ┌─────────────┐
    │☐ PDF        │
    └──────┬──────┘
           │ Tab
           ▼
    ┌─────────────┐
    │☐ DOCX       │
    └──────┬──────┘
           │ Tab
           ▼
    ┌─────────────┐
    │ [Generate]  │ ←─── Enter to submit
    └─────────────┘
```

---

## Color Scheme Reference

```
┌─────────────────────────────────────────────────────────────────┐
│                    ERROR HANDLING COLOR PALETTE                  │
└─────────────────────────────────────────────────────────────────┘

STATE COLORS:
─────────────

Normal/Untouched:
  Border: #CCCCCC (Light Gray)
  Text:   #333333 (Dark Gray)
  BG:     #FFFFFF (White)
  █████ #CCCCCC

Focus/Typing:
  Border: #0066CC (Blue)
  Text:   #000000 (Black)
  BG:     #F0F7FF (Light Blue)
  █████ #0066CC

Validating:
  Border: #FFAA00 (Orange-Yellow)
  Text:   #000000 (Black)
  BG:     #FFFBF0 (Light Yellow)
  █████ #FFAA00 + spinner

Valid/Success:
  Border: #00AA00 (Green)
  Text:   #000000 (Black)
  BG:     #F0FFF0 (Light Green)
  Icon:   ✓ Green
  █████ #00AA00

Warning:
  Border: #FF9900 (Orange)
  Text:   #000000 (Black)
  BG:     #FFF5E6 (Light Orange)
  Icon:   ⚠️ Orange
  █████ #FF9900

Error:
  Border: #CC0000 (Red)
  Text:   #000000 (Black)
  BG:     #FFF0F0 (Light Red)
  Icon:   ✗ Red
  █████ #CC0000

Disabled:
  Border: #DDDDDD (Gray)
  Text:   #999999 (Medium Gray)
  BG:     #F5F5F5 (Light Gray)
  █████ #DDDDDD


MESSAGE COLORS:
───────────────

Hint (Gray):        #666666  "Enter 2-letter code..."
Info (Blue):        #0066CC  "This will take ~25 seconds"
Warning (Orange):   #FF9900  "Large batch - may be slow"
Error (Red):        #CC0000  "Invalid state code"
Success (Green):    #00AA00  "✓ Generated successfully"


ICON COLORS:
────────────

℉   Info:       #0066CC (Blue)
⚠️   Warning:    #FF9900 (Orange)
✗   Error:      #CC0000 (Red)
✓   Success:    #00AA00 (Green)
⟳   Loading:    #FFAA00 (Orange-Yellow)
⛔  Critical:   #AA0000 (Dark Red)


ACCESSIBILITY:
──────────────

All color combinations meet WCAG 2.1 AA standards:
  • Minimum contrast ratio: 4.5:1 for normal text
  • Minimum contrast ratio: 3:1 for large text
  • All states also use icons (not color-only)
  • Focus indicators: 2px solid border


HIGH CONTRAST MODE:
───────────────────

When system high contrast is enabled:
  • All borders become 3px
  • All backgrounds become pure white or black
  • Icons become more prominent
  • Text becomes higher contrast
```

---

## Responsive Layout Examples

```
┌─────────────────────────────────────────────────────────────────┐
│                    RESPONSIVE ERROR DISPLAY                      │
└─────────────────────────────────────────────────────────────────┘

DESKTOP (>1024px):
──────────────────

┌────────────────────────────────────────────────────────────────┐
│  AAMVA License Generator                           [_] [□] [×]  │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Configuration                                                  │
│  ┌───────────────────────────────────────────────────────┐    │
│  │ State Code:  [CA________] ✓                           │    │
│  │              California (636014)                      │    │
│  │                                                        │    │
│  │ Quantity:    [50________] ℹ️                           │    │
│  │              This will take ~25 seconds               │    │
│  │                                                        │    │
│  │ Output:      [/home/user/output___] [Browse] ✓       │    │
│  │              ✓ Writable ✓ 50GB available              │    │
│  └───────────────────────────────────────────────────────┘    │
│                                                                 │
│  Formats:  ☑ PDF   ☑ DOCX   ☐ ODT                             │
│                                                                 │
│  [Generate Licenses]                                           │
│                                                                 │
└────────────────────────────────────────────────────────────────┘


TABLET (768px - 1024px):
────────────────────────

┌──────────────────────────────────────────┐
│  AAMVA Generator          [_] [□] [×]    │
├──────────────────────────────────────────┤
│  State:     [CA____] ✓                   │
│             California (636014)          │
│                                          │
│  Quantity:  [50____] ℹ️                   │
│             ~25 seconds                  │
│                                          │
│  Output:    [/home/user/output]          │
│             [Browse]                     │
│             ✓ Writable ✓ 50GB           │
│                                          │
│  Formats:   ☑ PDF  ☑ DOCX  ☐ ODT        │
│                                          │
│  [Generate Licenses]                     │
└──────────────────────────────────────────┘


MOBILE (< 768px):
─────────────────

┌────────────────────────────┐
│  AAMVA Gen      ☰   [×]   │
├────────────────────────────┤
│                            │
│  State Code:               │
│  [CA_________] ✓           │
│  California (636014)       │
│                            │
│  Quantity:                 │
│  [50_________] ℹ️           │
│  ~25 seconds               │
│                            │
│  Output:                   │
│  [/home/user/output]       │
│  [Browse]                  │
│  ✓ Writable ✓ 50GB        │
│                            │
│  ☑ PDF                     │
│  ☑ DOCX                    │
│  ☐ ODT                     │
│                            │
│  [Generate]                │
│                            │
└────────────────────────────┘
```

---

## Conclusion

This visual guide provides a comprehensive reference for implementing the error handling system. All diagrams use ASCII art for maximum compatibility and can be directly referenced during development.

### Quick Reference Checklist:

**Validation:**
- [ ] Three-layer architecture (Prevention → Detection → Recovery)
- [ ] Real-time validation with debouncing (300ms)
- [ ] Inline feedback with color + icon + text
- [ ] State machine transitions properly handled

**Progress:**
- [ ] Multi-level progress reporting (overall, stage, item)
- [ ] Real-time updates without blocking
- [ ] Time estimation and memory monitoring
- [ ] Graceful cancellation support

**Recovery:**
- [ ] Per-error recovery workflows
- [ ] Multiple recovery options
- [ ] Auto-fix when possible
- [ ] Partial success handling

**Accessibility:**
- [ ] Keyboard navigation complete
- [ ] Screen reader support (ARIA)
- [ ] High contrast mode
- [ ] Not color-only indicators

**Persistence:**
- [ ] Auto-save every 30 seconds
- [ ] Crash recovery
- [ ] Draft system
- [ ] Undo/redo support

---

**Document Status:** Complete Visual Reference
**Last Updated:** 2025-11-20
**Version:** 1.0
