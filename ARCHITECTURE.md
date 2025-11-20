# AAMVA ID Faker - Architecture Documentation

**Version:** 1.0
**Date:** 2025-11-20
**Status:** Comprehensive Analysis by Multi-Agent System

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [Component Breakdown](#component-breakdown)
4. [Data Flow Diagrams](#data-flow-diagrams)
5. [File Structure](#file-structure)
6. [Dependencies](#dependencies)
7. [Configuration](#configuration)

---

## Executive Summary

The AAMVA ID Faker is a **786-line single-file Python application** designed to generate realistic test driver's licenses and identification cards compliant with the AAMVA (American Association of Motor Vehicle Administrators) DL/ID-2020 standard. The application creates PDF417 2D barcodes encoded with properly formatted license data and produces print-ready documents on Avery 28371 business card templates.

### Key Characteristics
- **Architecture Pattern:** Procedural/Functional Programming
- **Primary Language:** Python 3.x
- **Core Functionality:** Fake data generation + PDF417 encoding + Document creation
- **Output Formats:** BMP, TXT, PNG, PDF, DOCX (ODT disabled)
- **Jurisdiction Coverage:** 67 jurisdictions (50 US states + DC + territories + Canadian provinces)

### Quality Metrics
- **Lines of Code:** 786
- **Functions:** 10 main functions
- **External Dependencies:** 6 libraries
- **Test Coverage:** 0% (no tests exist)
- **Code Quality Score:** 6.5/10 (Medium-Good)

---

## System Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         AAMVA ID FAKER SYSTEM                        │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │                    CLI INTERFACE (main)                     │   │
│  │  Argparse: -n <num> -s <state> --all-states --no-pdf etc. │   │
│  └─────────────────────┬──────────────────────────────────────┘   │
│                        │                                            │
│                        ▼                                            │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │              DATA GENERATION LAYER                          │   │
│  │  ┌──────────────────────────────────────────────────┐      │   │
│  │  │  generate_license_data()                         │      │   │
│  │  │    ├─ Faker: Names, addresses, dates             │      │   │
│  │  │    ├─ generate_state_license_number()            │      │   │
│  │  │    └─ generate_state_subfile()                   │      │   │
│  │  └──────────────────────────────────────────────────┘      │   │
│  │             │                                               │   │
│  │             ▼ [DL_data, State_data]                        │   │
│  └─────────────┼───────────────────────────────────────────────┘   │
│                │                                                    │
│                ▼                                                    │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │              BARCODE ENCODING LAYER                         │   │
│  │  ┌──────────────────────────────────────────────────┐      │   │
│  │  │  format_barcode_data()                           │      │   │
│  │  │    └─ AAMVA 2020 Format Construction             │      │   │
│  │  ├──────────────────────────────────────────────────┤      │   │
│  │  │  save_barcode_and_data()                         │      │   │
│  │  │    ├─ pdf417.encode() - Create barcode           │      │   │
│  │  │    ├─ pdf417.render_image() - Generate BMP       │      │   │
│  │  │    └─ Save to disk (BMP + TXT)                   │      │   │
│  │  └──────────────────────────────────────────────────┘      │   │
│  │             │                                               │   │
│  │             ▼ (image_path, data)                           │   │
│  └─────────────┼───────────────────────────────────────────────┘   │
│                │                                                    │
│                ▼                                                    │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │           DOCUMENT GENERATION LAYER                         │   │
│  │  ┌──────────────────┬─────────────────┬──────────────┐     │   │
│  │  │ create_avery_pdf │ create_docx_card│ create_odt   │     │   │
│  │  │   (ReportLab)    │  (python-docx)  │  (DISABLED)  │     │   │
│  │  │                  │                  │              │     │   │
│  │  │ • 10 cards/page  │ • 5x2 table     │              │     │   │
│  │  │ • Avery 28371    │ • Card images   │              │     │   │
│  │  │ • Barcode + text │ • Embed PNG     │              │     │   │
│  │  └──────────────────┴─────────────────┴──────────────┘     │   │
│  │             │              │                                │   │
│  │             ▼              ▼                                │   │
│  └─────────────┼──────────────┼─────────────────────────────────┘   │
│                │              │                                    │
│                ▼              ▼                                    │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │                    FILE SYSTEM OUTPUT                       │   │
│  │  output/                                                    │   │
│  │    ├─ barcodes/license_N.bmp                               │   │
│  │    ├─ data/license_N.txt                                   │   │
│  │    ├─ cards/license_N_card.png                             │   │
│  │    ├─ licenses_avery_28371.pdf                             │   │
│  │    └─ cards.docx                                           │   │
│  └────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### Architectural Patterns

#### 1. Layered Architecture (3 Layers)
- **Presentation Layer:** CLI interface (argparse)
- **Business Logic Layer:** Data generation, barcode encoding
- **Data Access Layer:** File I/O, document creation

#### 2. Functional Decomposition
- No classes defined (procedural approach)
- Each function has single responsibility
- Data passed through function parameters
- Stateless operations (except global faker instance)

#### 3. Pipeline Pattern
Data flows through sequential transformations:
```
User Input → License Data → Barcode Data → Encoded Barcode → Documents
```

---

## Component Breakdown

### Component Dependency Graph

```
┌─────────────────────────────────────────────────────────────────┐
│                         generate_licenses.py                     │
│                                                                  │
│  main()                                                          │
│    │                                                             │
│    ├─► ensure_dirs()                                            │
│    │                                                             │
│    ├─► generate_license_data(state)                             │
│    │     ├─► generate_state_license_number(state)               │
│    │     │     └─► Uses: fake, random, string                   │
│    │     │                                                       │
│    │     ├─► generate_state_subfile(dlid_data, custom_fields)   │
│    │     │     └─► Uses: random, string                         │
│    │     │                                                       │
│    │     └─► Uses: fake, datetime, random                       │
│    │                                                             │
│    ├─► save_barcode_and_data(data, index)                       │
│    │     ├─► format_barcode_data(data)                          │
│    │     │     ├─► get_iin_by_state(abbr)                       │
│    │     │     │     └─► Uses: IIN_JURISDICTIONS                │
│    │     │     │                                                 │
│    │     │     └─► format_date(d)                               │
│    │     │                                                       │
│    │     └─► Uses: pdf417, PIL                                  │
│    │                                                             │
│    ├─► create_avery_pdf(data_list)                              │
│    │     └─► Uses: reportlab, PIL                               │
│    │                                                             │
│    ├─► create_docx_card(data_list)                              │
│    │     ├─► generate_individual_card_image(data, img, width, dpi)│
│    │     │     └─► Uses: PIL                                    │
│    │     │                                                       │
│    │     └─► Uses: python-docx                                  │
│    │                                                             │
│    └─► create_odt_card(data_list) [DISABLED]                    │
│          └─► Uses: odfpy                                        │
│                                                                  │
│  Configuration Data:                                            │
│    • IIN_JURISDICTIONS (lines 65-131)                          │
│    • Output directory constants (lines 56-61)                  │
│    • Global faker instance (line 51)                           │
└─────────────────────────────────────────────────────────────────┘
```

### Function Catalog

| Function | Lines | LOC | Purpose | Dependencies |
|----------|-------|-----|---------|--------------|
| `main()` | 720-786 | 67 | CLI interface & orchestration | argparse, all other functions |
| `ensure_dirs()` | 139-144 | 6 | Create output directory structure | os |
| `get_iin_by_state()` | 132-136 | 5 | Lookup IIN by state abbreviation | IIN_JURISDICTIONS |
| `format_date()` | 147-148 | 2 | Format datetime as MMDDYYYY | datetime |
| `generate_state_license_number()` | 148-246 | 99 | Generate state-specific DL numbers | fake, random, string |
| `generate_state_subfile()` | 248-273 | 26 | Create state-specific subfile data | random, string |
| `generate_license_data()` | 275-357 | 83 | Generate complete license dataset | fake, datetime, random |
| `format_barcode_data()` | 359-407 | 49 | Construct AAMVA barcode string | get_iin_by_state, format_date |
| `save_barcode_and_data()` | 409-417 | 9 | Encode and save barcode + data | pdf417, PIL, format_barcode_data |
| `create_avery_pdf()` | 419-509 | 91 | Generate Avery template PDF | reportlab, PIL |
| `generate_individual_card_image()` | 511-565 | 55 | Create high-res card image | PIL |
| `create_odt_card()` | 573-616 | 44 | Generate ODT document (disabled) | odfpy |
| `create_docx_card()` | 618-719 | 102 | Generate DOCX with card layout | python-docx, PIL |

**Total Functional LOC:** ~638 (excluding comments, blank lines, shebang)

---

## Data Flow Diagrams

### Primary Data Flow (Single License Generation)

```
START
  │
  ▼
┌─────────────────────┐
│ User Input          │
│ • Number: 1         │
│ • State: "CA"       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────┐
│ generate_license_data("CA")         │
│                                     │
│ Random Data Generation:             │
│ • Name: John Doe (gender-matched)   │
│ • DOB: 1990-05-15                   │
│ • Address: 123 Main St, LA, CA      │
│ • Physical: 70", 180lbs, BRO, BRO   │
│                                     │
│ State-Specific:                     │
│ • generate_state_license_number()   │
│   → "A1234567" (CA format)          │
│                                     │
│ Dates:                              │
│ • Issue: 2025-11-20                 │
│ • Expiration: 2032-08-14            │
│                                     │
│ Additional:                         │
│ • Document #: DOC12345              │
│ • Class: D                          │
│ • DHS: F (compliant)                │
└──────────┬──────────────────────────┘
           │
           ▼ Returns [DL_dict, State_dict]
┌─────────────────────────────────────┐
│ format_barcode_data(data)           │
│                                     │
│ Header Construction:                │
│ "@\n\x1E\rANSI "                   │
│ + "636014" (CA IIN)                 │
│ + "10" (version)                    │
│ + "00" (jurisdiction ver)           │
│ + "02" (num subfiles)               │
│                                     │
│ Subfile Designators:                │
│ "DL" + offset + length              │
│ "ZC" + offset + length              │
│                                     │
│ Subfile Data:                       │
│ "DL" + fields + "\r"                │
│ "ZC" + fields + "\r"                │
└──────────┬──────────────────────────┘
           │
           ▼ Returns AAMVA string (350-450 bytes)
┌─────────────────────────────────────┐
│ save_barcode_and_data(data, 0)      │
│                                     │
│ pdf417.encode():                    │
│ • Columns: 13                       │
│ • Security: Level 5                 │
│ • Output: Code array                │
│                                     │
│ pdf417.render_image():              │
│ • Convert to PIL Image              │
│ • Format: BMP                       │
│                                     │
│ File Writes:                        │
│ • output/barcodes/license_0.bmp     │
│ • output/data/license_0.txt         │
└──────────┬──────────────────────────┘
           │
           ▼ Returns (img_path, data)
     ┌─────┴─────┐
     │           │
     ▼           ▼
┌─────────┐ ┌──────────────┐
│ PDF Gen │ │  DOCX Gen    │
│         │ │              │
│ Creates:│ │  Creates:    │
│ Avery   │ │  Table with  │
│ layout  │ │  embedded    │
│ 1 card  │ │  card images │
└─────────┘ └──────────────┘
     │           │
     ▼           ▼
┌─────────────────────┐
│ Output Files:       │
│ • PDF (1 page)      │
│ • DOCX (1 card)     │
│ • BMP barcode       │
│ • TXT data          │
│ • PNG card image    │
└─────────────────────┘
     │
     ▼
   END
```

### Batch Processing Flow (N Licenses)

```
┌──────────────────┐
│ main(-n 10)      │
└────────┬─────────┘
         │
         ▼
  ┌──────────────┐
  │ records = [] │
  └──────┬───────┘
         │
         ▼
  ┌─────────────────────────┐
  │ FOR i in range(10):     │
  │   data = generate_...() │
  │   img, data = save_...()│
  │   records.append(...)   │
  └────────┬────────────────┘
           │
           ▼ records = [(img1, data1), ..., (img10, data10)]
     ┌─────┴─────┬──────────────┐
     │           │              │
     ▼           ▼              ▼
┌─────────┐ ┌─────────┐  ┌──────────┐
│ PDF     │ │ DOCX    │  │ ODT      │
│ (1 pg)  │ │ (10 img)│  │(disabled)│
└─────────┘ └─────────┘  └──────────┘
```

### State Selection Flow

```
┌───────────────────────┐
│ CLI Arguments         │
└──────────┬────────────┘
           │
   ┌───────┼───────┬─────────────┐
   │       │       │             │
   ▼       ▼       ▼             ▼
┌──────┐ ┌────┐ ┌───────┐  ┌──────────┐
│ -s CA│ │ -a │ │ None  │  │ -n 10    │
└──┬───┘ └─┬──┘ └───┬───┘  └─────┬────┘
   │       │        │            │
   │       │        │            │
   ▼       ▼        ▼            ▼
  "CA"   [All 51]  Random    10 iterations
   │       │        │            │
   │       │        │            │
   ▼       ▼        ▼            ▼
┌────────────────────────────────────┐
│ generate_license_data(state)       │
│                                    │
│ If state provided:                 │
│   use state                        │
│ Else:                              │
│   state = fake.state_abbr()        │
│     → Random US state              │
└────────────────────────────────────┘
```

---

## File Structure

### Project Tree

```
aamva-id-faker/
├── .git/                          # Git repository
├── .gitignore                     # Python gitignore (208 lines)
├── LICENSE                        # Original license file
├── LICENSE.md                     # MIT License (James W Rogers, Jr.)
├── README.md                      # User documentation (62 lines)
├── PROJECT.md                     # State DL format reference (65 lines)
├── INNs.csv                       # IIN reference data (72 lines)
├── LiberationMono-Bold.ttf        # Font file for card generation
├── generate_licenses.py           # Main application (786 lines)
│
└── output/                        # Generated files (created at runtime)
    ├── barcodes/
    │   └── license_N.bmp          # PDF417 barcode images
    ├── data/
    │   └── license_N.txt          # Raw AAMVA barcode data
    ├── cards/
    │   └── license_N_card.png     # Individual card images (temp)
    ├── licenses_avery_28371.pdf   # Print-ready PDF
    └── cards.docx                 # Print-ready DOCX
```

### Code Organization (generate_licenses.py)

```
Line Range │ Section                        │ Lines │ Purpose
───────────┼────────────────────────────────┼───────┼─────────────────────
1-29       │ Shebang & License Header       │ 29    │ Execution & copyright
31-50      │ Import Statements              │ 20    │ Dependencies
51-61      │ Output Configuration           │ 11    │ Directory constants
62-64      │ IIN Reference Comment          │ 3     │ Data source links
65-131     │ IIN_JURISDICTIONS Dictionary   │ 67    │ 67 jurisdiction mappings
132-136    │ get_iin_by_state()             │ 5     │ IIN lookup utility
139-144    │ ensure_dirs()                  │ 6     │ Directory creation
147-148    │ format_date()                  │ 2     │ Date formatting
148-246    │ generate_state_license_number()│ 99    │ State DL number generation
248-273    │ generate_state_subfile()       │ 26    │ State subfile creation
275-357    │ generate_license_data()        │ 83    │ Main data generation
359-407    │ format_barcode_data()          │ 49    │ AAMVA encoding
409-417    │ save_barcode_and_data()        │ 9     │ Barcode creation
419-509    │ create_avery_pdf()             │ 91    │ PDF generation
511-565    │ generate_individual_card_image()│ 55   │ Card image creation
567-571    │ Disabled Feature Comment       │ 5     │ ODT explanation
573-616    │ create_odt_card() [DISABLED]   │ 44    │ ODT generation (unused)
618-719    │ create_docx_card()             │ 102   │ DOCX generation
720-786    │ main()                         │ 67    │ CLI & orchestration
```

---

## Dependencies

### Dependency Graph

```
┌────────────────────────────────────────────────────────────┐
│                    generate_licenses.py                     │
└─────────────────────┬──────────────────────────────────────┘
                      │
          ┌───────────┼───────────┬─────────────┬─────────────┐
          │           │           │             │             │
          ▼           ▼           ▼             ▼             ▼
     ┌────────┐  ┌────────┐  ┌────────┐   ┌─────────┐  ┌─────────┐
     │ faker  │  │pdf417  │  │ Pillow │   │reportlab│  │python-  │
     │        │  │        │  │  (PIL) │   │         │  │  docx   │
     └────────┘  └────────┘  └────────┘   └─────────┘  └─────────┘
         │            │            │             │             │
         │            │            │             │             │
         ▼            ▼            ▼             ▼             ▼
    Personal      PDF417      Image Ops     PDF Canvas    DOCX API
    Data Gen      Encoding    • Create      • Drawing     • Document
    • Names       • 2D Code   • Resize      • Images      • Tables
    • Addresses   • Render    • Paste       • Text        • Images
    • Dates       Security=5  • Draw        • Layout      • Formatting
    • Random      Columns=13  • Fonts       • Pages       • XML manip
```

### External Library Details

| Library | Version | Purpose | Functions Used | Install Size |
|---------|---------|---------|----------------|--------------|
| **faker** | Latest | Realistic fake data generation | `Faker()`, `first_name_male()`, `first_name_female()`, `last_name()`, `state_abbr()`, `date_of_birth()`, `street_address()`, `city()`, `zipcode()`, `bothify()`, `numerify()`, `lexify()`, `unique` | ~5MB |
| **pdf417** | Latest | PDF417 2D barcode encoding | `encode()`, `render_image()` | ~1MB |
| **Pillow (PIL)** | Latest | Image manipulation | `Image.open()`, `Image.new()`, `Image.paste()`, `ImageDraw.Draw()`, `ImageFont.truetype()`, `ImageFont.load_default()` | ~10MB |
| **reportlab** | Latest | PDF document generation | `canvas.Canvas()`, `pagesizes.letter`, `units.inch`, `Image()`, `colors` | ~15MB |
| **python-docx** | Latest | DOCX document creation | `Document()`, `Inches()`, `Pt()`, `WD_ALIGN_PARAGRAPH`, `qn()`, `OxmlElement()` | ~3MB |
| **odfpy** | Latest | OpenDocument format (unused) | `OpenDocumentText`, `Style`, `P`, `Frame`, `Image`, `Table` | ~2MB |

**Total Install Size:** ~36MB

### Standard Library Dependencies

```python
os              # File system operations (makedirs, path.join)
argparse        # CLI argument parsing
random          # Random number/choice generation
string          # String constants (ascii_uppercase, digits)
datetime        # Date/time manipulation (datetime, timedelta)
tempfile        # (Imported but unused)
```

### Installation Instructions

**1. Set up Python virtual environment:**
```bash
# Install venv (if not already installed)
sudo apt install python3-venv

# Create virtual environment
cd /path/to/aamva-id-faker
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# OR
.venv\Scripts\activate     # Windows
```

**2. Install dependencies:**
```bash
pip install faker pdf417 pillow odfpy reportlab python-docx
```

**Note:** Always activate the virtual environment before running the script.

---

## Configuration

### Configuration Points

```
┌──────────────────────────────────────────────────────────┐
│ Configuration Layer                                      │
├──────────────────────────────────────────────────────────┤
│                                                          │
│ 1. Output Directories (lines 56-61)                     │
│    OUTPUT_DIR = "output"                                 │
│    BARCODE_DIR = "output/barcodes"                       │
│    DATA_DIR = "output/data"                              │
│    CARDS_DIR = "output/cards"                            │
│    ODT_FILE = "output/cards.odt"                         │
│    DOCX_FILE = "output/cards.docx"                       │
│                                                          │
│ 2. AAMVA Barcode Settings (lines 362-365)               │
│    compliance = "@\n\x1E\r"                             │
│    file_type = "ANSI "                                   │
│    version = "10"  # AAMVA 2020                          │
│    jurisdiction_version = "00"                           │
│                                                          │
│ 3. PDF417 Parameters (line 411)                         │
│    columns = 13                                          │
│    security_level = 5                                    │
│                                                          │
│ 4. Avery Template (lines 421-427)                       │
│    card_width = 3.5 * inch                               │
│    card_height = 2 * inch                                │
│    left_margin = 0.75 * inch                             │
│    top_margin = 0.5 * inch                               │
│    horizontal_spacing = 0.25 * inch                      │
│    vertical_spacing = 0 * inch                           │
│                                                          │
│ 5. Card Image Settings (lines 520, 537)                 │
│    default_dpi = 300                                     │
│    base_font_size = 50                                   │
│    small_font_size = 40                                  │
│                                                          │
│ 6. Faker Instance (line 51)                             │
│    fake = Faker()  # Global instance                     │
│                                                          │
│ 7. IIN Jurisdictions (lines 65-131)                     │
│    IIN_JURISDICTIONS = {                                 │
│      "636014": {"jurisdiction": "California", ...}       │
│      ... 67 total entries ...                           │
│    }                                                     │
│                                                          │
│ 8. State License Formats (lines 148-246)                │
│    state_formats = {                                     │
│      'CA': lambda: fake.bothify('?#######'),            │
│      'FL': lambda: fake.bothify('?############'),       │
│      ... 30 total states ...                            │
│    }                                                     │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### CLI Configuration

```
Usage: generate_licenses.py [OPTIONS]

Options:
  -n, --number N        Number of licenses to generate (default: 10)
  -s, --state XX        Specific state abbreviation (e.g., CA, NY)
  -a, --all-states      Generate one license per state (51 total)
  -d, --directory PATH  Custom output directory (default: ./output)
  -z, --state-subfile   Enable state subfile generation (currently stub)
  -p, --no-pdf          Skip PDF generation
  -o, --no-odt          Skip ODT generation (already disabled)
  -w, --no-word         Skip DOCX generation
  -h, --help            Show help message

Examples:
  python generate_licenses.py                      # 10 random licenses
  python generate_licenses.py -n 50                # 50 random licenses
  python generate_licenses.py -s CA -n 5           # 5 California licenses
  python generate_licenses.py --all-states         # 1 per state (51 total)
  python generate_licenses.py -n 100 -p -w         # Only barcodes/data
```

### Environment-Based Configuration (Not Currently Supported)

**Recommendation:** Add environment variable support for:
```python
OUTPUT_DIR = os.getenv('AAMVA_OUTPUT_DIR', 'output')
DPI = int(os.getenv('AAMVA_CARD_DPI', '300'))
AAMVA_VERSION = os.getenv('AAMVA_VERSION', '10')
```

---

## Performance Characteristics

### Time Complexity Analysis

| Operation | Time Complexity | Notes |
|-----------|----------------|-------|
| Single license data generation | O(1) | Constant time operations |
| State license number generation | O(1) | Dictionary lookup + random |
| Barcode formatting | O(n) | n = number of fields (~30) |
| PDF417 encoding | O(m²) | m = data length (~400 bytes) |
| Barcode rendering | O(p) | p = number of pixels |
| PDF page creation | O(k) | k = cards per page (10) |
| DOCX generation | O(k) | k = number of cards |
| **Total for N licenses** | **O(N)** | Linear scaling |

### Space Complexity

| Component | Space Usage | Notes |
|-----------|-------------|-------|
| Single license data | ~2KB | Dictionary in memory |
| Barcode string | ~400 bytes | AAMVA formatted text |
| Barcode image (BMP) | ~50KB | Uncompressed bitmap |
| Card image (PNG) | ~100KB | 300 DPI, compressed |
| PDF (10 cards) | ~500KB | Embedded images |
| DOCX (10 cards) | ~1MB | Embedded PNG images |
| **Memory for N licenses** | **O(N)** | All records in memory |

### Benchmark Estimates

```
Single License: ~0.5 seconds
  ├─ Data generation: 50ms
  ├─ Barcode encoding: 100ms
  ├─ Image rendering: 200ms
  └─ File I/O: 150ms

10 Licenses: ~5 seconds
  ├─ Data + barcodes: 3s
  ├─ PDF creation: 1s
  └─ DOCX creation: 1s

51 States (--all-states): ~25 seconds
  ├─ Data + barcodes: 15s
  ├─ PDF creation: 5s
  └─ DOCX creation: 5s

100 Licenses: ~50 seconds
  ├─ Data + barcodes: 30s
  ├─ PDF creation: 10s
  └─ DOCX creation: 10s
```

**Bottlenecks:**
1. PDF417 barcode encoding (CPU-intensive)
2. High-resolution image generation (300 DPI)
3. PDF/DOCX document assembly (disk I/O)
4. Memory usage (all records loaded before document creation)

---

## Extensibility Points

### Current Extension Mechanisms

1. **New State Formats:** Add entries to `state_formats` dictionary (line 150)
2. **New Jurisdictions:** Add entries to `IIN_JURISDICTIONS` (line 65)
3. **Custom Fields:** Modify `generate_license_data()` to add AAMVA fields
4. **State Subfiles:** Implement custom_fields in `generate_state_subfile()`
5. **Output Formats:** Add new document generation functions

### Recommended Future Extensions

```python
# Configuration file support
def load_config(config_file):
    """Load JSON/YAML configuration"""
    pass

# Plugin system for state formats
class StateFormatPlugin:
    """Base class for state-specific logic"""
    def generate_license_number(self) -> str: pass
    def get_subfile_fields(self) -> dict: pass

# Custom AAMVA version support
def format_barcode_data(data, version='10'):
    """Support multiple AAMVA versions"""
    pass

# Streaming generation for large batches
def generate_licenses_streaming(count):
    """Yield licenses one at a time"""
    for i in range(count):
        yield generate_license_data()
```

---

## Conclusion

The AAMVA ID Faker demonstrates a **simple but effective architecture** for its intended purpose: generating test license data. The single-file procedural design keeps complexity low but sacrifices modularity and testability. For production use or long-term maintenance, consider refactoring into a package structure with proper separation of concerns, comprehensive error handling, and extensive test coverage.

### Architectural Strengths
✅ Clear layered structure (CLI → Logic → I/O)
✅ Functional decomposition with single responsibilities
✅ Straightforward data flow (pipeline pattern)
✅ Minimal dependencies (6 external libraries)

### Architectural Weaknesses
❌ Monolithic single file (786 lines)
❌ Global state (faker instance)
❌ No separation of configuration
❌ Tight coupling between layers
❌ No error handling architecture

**Overall Architecture Quality: 6/10** - Functional but needs refactoring for maintainability.
