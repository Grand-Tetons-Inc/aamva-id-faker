# AAMVA ID Faker - Data Structures Documentation

**Version:** 1.0
**Date:** 2025-11-20
**Analysis:** Multi-Agent Comprehensive Review

---

## Table of Contents
1. [Overview](#overview)
2. [Core Data Structures](#core-data-structures)
3. [AAMVA Field Specifications](#aamva-field-specifications)
4. [State License Number Formats](#state-license-number-formats)
5. [IIN Jurisdiction Mappings](#iin-jurisdiction-mappings)
6. [Barcode Data Structure](#barcode-data-structure)
7. [Type Specifications](#type-specifications)

---

## Overview

The AAMVA ID Faker uses **dictionary-based data structures** throughout the application. No custom classes are defined; all data is represented using Python's built-in `dict` type with string keys corresponding to AAMVA field codes.

### Data Structure Hierarchy

```
License Data (list)
├── [0] DL Subfile (dict)
│   ├── "subfile_type": "DL"
│   ├── "DAQ": str (License Number)
│   ├── "DCS": str (Last Name)
│   ├── "DAC": str (First Name)
│   └── ... (28 more AAMVA fields)
│
└── [1] State Subfile (dict)
    ├── "subfile_type": "Z[X]"  (X = state initial)
    ├── "Z[X]W": str (County)
    ├── "Z[X]T": str (Test String)
    └── "Z[X]X": str (Custom Field)
```

---

## Core Data Structures

### 1. DL Subfile Data (dlid_data)

**Definition:** Lines 309-351 in `generate_licenses.py`

**Type:** `dict[str, str]`

**Purpose:** Contains all standard AAMVA data elements for a driver's license/ID card

**Structure:**

```python
dlid_data = {
    # ============================================================
    # METADATA (Non-AAMVA)
    # ============================================================
    "subfile_type": "DL",  # Designates this as DL subfile

    # ============================================================
    # LICENSE INFORMATION
    # ============================================================
    "DAQ": str,            # Customer ID Number (License Number)
                          # Format: State-specific (see state formats)
                          # Example: "A1234567" (California)

    "DCA": str,            # Vehicle Class
                          # Values: "D" (standard), "A", "B", "C", "M"
                          # Example: "D"

    "DCB": str,            # Restrictions
                          # Values: "" (none) or codes like "B", "E"
                          # Example: ""

    "DCD": str,            # Endorsements
                          # Values: "" (none) or codes like "H", "N", "T"
                          # Example: ""

    # ============================================================
    # DATES (Format: MMDDYYYY)
    # ============================================================
    "DBA": str,            # Expiration Date
                          # Format: MMDDYYYY (8 digits)
                          # Example: "08142032" = August 14, 2032

    "DBD": str,            # Issue Date
                          # Format: MMDDYYYY
                          # Example: "11202025" = November 20, 2025

    "DBB": str,            # Birth Date
                          # Format: MMDDYYYY
                          # Example: "05151990" = May 15, 1990

    "DDB": str,            # Card Revision Date
                          # Format: MMDDYYYY
                          # Example: "11202025"

    "DDC": str,            # Hazmat Endorsement Expiration
                          # Format: MMDDYYYY or ""
                          # Example: ""

    # ============================================================
    # PERSONAL INFORMATION
    # ============================================================
    "DCS": str,            # Last Name (Family Name)
                          # Format: Uppercase letters
                          # Example: "DOE"

    "DAC": str,            # First Name (Given Name)
                          # Format: Uppercase letters
                          # Example: "JOHN"

    "DAD": str,            # Middle Name
                          # Format: Uppercase letters or single initial
                          # Example: "MICHAEL" or "M"

    # ============================================================
    # PHYSICAL CHARACTERISTICS
    # ============================================================
    "DBC": str,            # Sex
                          # Values: "1" = Male, "2" = Female
                          # Example: "1"

    "DAY": str,            # Eye Color
                          # Values: BLK, BLU, BRO, GRY, GRN, HAZ, MAR, PNK, DIC, UNK
                          # Example: "BRO"

    "DAU": str,            # Height (inches)
                          # Format: 3 digits (in inches)
                          # Range: 058-078 (4'10" to 6'6")
                          # Example: "070" = 5'10"

    "DAW": str,            # Weight (pounds)
                          # Format: 3 digits
                          # Range: 115-275
                          # Example: "180"

    "DAZ": str,            # Hair Color
                          # Values: BLK, BLN, BRO, GRY, RED, WHI, SDY, UNK
                          # Example: "BRO"

    "DCL": str,            # Race/Ethnicity
                          # Values: W, B, A, I, U
                          # W=White, B=Black, A=Asian, I=Native American, U=Unknown
                          # Example: "W"

    # ============================================================
    # ADDRESS
    # ============================================================
    "DAG": str,            # Street Address
                          # Format: Uppercase alphanumeric with spaces
                          # Example: "123 MAIN STREET"

    "DAI": str,            # City
                          # Format: Uppercase letters
                          # Example: "LOS ANGELES"

    "DAJ": str,            # State/Province
                          # Format: 2-letter abbreviation
                          # Example: "CA"

    "DAK": str,            # ZIP Code
                          # Format: 9 digits (zero-padded)
                          # Example: "900120000"

    # ============================================================
    # DOCUMENT METADATA
    # ============================================================
    "DCF": str,            # Document Discriminator
                          # Format: Unique identifier per license
                          # Example: "DOC12345"

    "DCG": str,            # Country of Issuance
                          # Values: "USA", "CAN"
                          # Example: "USA"

    # ============================================================
    # TRUNCATION FLAGS
    # ============================================================
    "DDE": str,            # Truncation - Family Name
                          # Values: "N"=Not truncated, "T"=Truncated, "U"=Unknown
                          # Example: "N"

    "DDF": str,            # Truncation - First Name
                          # Values: "N", "T", "U"
                          # Example: "N"

    "DDG": str,            # Truncation - Middle Name
                          # Values: "N", "T", "U"
                          # Example: "N"

    # ============================================================
    # COMPLIANCE & STATUS
    # ============================================================
    "DDA": str,            # DHS Compliance Type
                          # Values: "F"=Full compliance (REAL ID), "N"=Non-compliant
                          # Example: "F"

    "DDD": str,            # Limited Duration Document
                          # Values: "1"=Yes (temporary), "0"=No (permanent)
                          # Example: "0"

    "DDK": str,            # Organ Donor
                          # Values: "1"=Yes, "0"=No
                          # Example: "1"

    "DDL": str,            # Veteran Status
                          # Values: "1"=Yes, "0"=No
                          # Example: "0"
}
```

**Field Count:** 31 fields (30 AAMVA + 1 metadata)

**Total Size:** ~500-800 bytes when encoded

---

### 2. State Subfile Data

**Definition:** Lines 260-268 in `generate_licenses.py`

**Type:** `dict[str, str]`

**Purpose:** Contains state-specific data elements not in AAMVA standard

**Structure:**

```python
state_subfile_data = {
    # ============================================================
    # METADATA
    # ============================================================
    "subfile_type": str,   # "Z" + first letter of state
                          # Examples: "ZC" (California), "ZT" (Texas)

    # ============================================================
    # STATE-SPECIFIC FIELDS
    # ============================================================
    "Z[X]W": str,          # County Field
                          # [X] = first letter of state abbreviation
                          # Example: "ZCW": "ALAMEDA" (California)

    "Z[X]T": str,          # Test String Field
                          # Always: "TEST STRING"
                          # Example: "ZCT": "TEST STRING"

    "Z[X]X": str,          # Custom Alphanumeric Field
                          # Format: Random value (A######)
                          # Example: "ZCX": "A123456"
}
```

**Field Count:** 4 fields (1 metadata + 3 data fields)

**Total Size:** ~50-100 bytes when encoded

**Example for Different States:**

```python
# California (CA)
{
    "subfile_type": "ZC",
    "ZCW": "ORANGE",
    "ZCT": "TEST STRING",
    "ZCX": "A987654"
}

# Texas (TX)
{
    "subfile_type": "ZT",
    "ZTW": "HARRIS",
    "ZTT": "TEST STRING",
    "ZTX": "B123789"
}

# New York (NY)
{
    "subfile_type": "ZN",
    "ZNW": "KINGS",
    "ZNT": "TEST STRING",
    "ZNX": "C456123"
}
```

---

### 3. IIN Jurisdictions Dictionary

**Definition:** Lines 65-131 in `generate_licenses.py`

**Type:** `dict[str, dict[str, str]]`

**Purpose:** Maps 6-digit Issuer Identification Numbers to jurisdictions

**Structure:**

```python
IIN_JURISDICTIONS = {
    "IIN_CODE": {
        "jurisdiction": str,  # Full name
        "abbr": str,         # 2-letter code
        "country": str       # "USA" or "Canada"
    }
}
```

**Example Entries:**

```python
{
    "636014": {
        "jurisdiction": "California",
        "abbr": "CA",
        "country": "USA"
    },
    "636001": {
        "jurisdiction": "New York",
        "abbr": "NY",
        "country": "USA"
    },
    "636012": {
        "jurisdiction": "Ontario",
        "abbr": "ON",
        "country": "Canada"
    },
    "604426": {
        "jurisdiction": "Prince Edward Island",
        "abbr": "PE",
        "country": "Canada"
    }
}
```

**Total Entries:** 67 jurisdictions
- 50 US States
- 1 District of Columbia
- 4 US Territories (AS, GU, MP, PR, VI)
- 13 Canadian Provinces/Territories
- 1 US State Department

**Size:** ~3KB in memory

---

### 4. State License Format Dictionary

**Definition:** Lines 150-246 in `generate_licenses.py`

**Type:** `dict[str, Callable[[], str]]`

**Purpose:** Maps state abbreviations to license number generation functions

**Structure:**

```python
state_formats = {
    "STATE_CODE": lambda: generation_expression
}
```

**Format Notation:**
- `?` = Random uppercase letter (A-Z)
- `#` = Random digit (0-9)
- Literal characters are preserved

**Complete Format Table:**

| State | Format Expression | Example Output | Pattern |
|-------|------------------|----------------|---------|
| AL | `'#'*random.randint(1,7)` | 1234567 | 1-7 digits |
| AK | `'#'*random.randint(1,7)` | 123456 | 1-7 digits |
| AZ | `random.choice([...])` | A12345678 | 3 variations |
| AR | `'#'*random.randint(4,9)` | 123456789 | 4-9 digits |
| CA | `'?#######'` | A1234567 | 1 letter + 7 digits |
| CO | `random.choice([...])` | 123456789 | 3 variations |
| CT | `'#########'` | 123456789 | 9 digits |
| DE | `'#'*random.randint(1,7)` | 1234 | 1-7 digits |
| DC | `'#'*random.choice([7,9])` | 1234567 | 7 or 9 digits |
| FL | `'?############'` | A123456789012 | 1 letter + 12 digits |
| GA | `'#'*random.randint(7,9)` | 12345678 | 7-9 digits |
| HI | `random.choice([...])` | A12345678 | 2 variations |
| ID | `random.choice([...])` | AB123456C | 2 variations |
| IL | `random.choice([...])` | A12345678901 | 2 variations |
| IN | `random.choice([...])` | A123456789 | 3 variations |
| IA | `random.choice([...])` | 123456789 | 2 variations |
| KS | `random.choice([...])` | A1B2C | 3 variations |
| KY | `random.choice([...])` | A12345678 | 3 variations |
| LA | `'#'*random.randint(1,9)` | 123456789 | 1-9 digits |
| ME | `random.choice([...])` | 1234567A | 3 variations |
| MD | `'?############'` | M123456789012 | 1 letter + 12 digits |
| MA | `random.choice([...])` | A12345678 | 2 variations |
| MI | `random.choice([...])` | A1234567890 | 2 variations |
| MN | `'?############'` | B123456789012 | 1 letter + 12 digits |
| MS | `'#########'` | 123456789 | 9 digits |
| MO | `random.choice([...])` | A123456 | 5 variations |
| NY | `random.choice([...])` | A1234567 | 6 variations |
| TX | `'#'*random.choice([7,8])` | 12345678 | 7 or 8 digits |
| VA | `random.choice([...])` | A123456789 | 4 variations |
| WI | `'?#############'` | C1234567890123 | 1 letter + 13 digits |
| WY | `'#'*random.randint(9,10)` | 1234567890 | 9-10 digits |

**States Using Default Format (9 digits):**
MT, NE, NV, NH, NJ, NM, NC, ND, OH, OK, OR, PA, RI, SC, SD, TN, UT, VT, WA, WV

**Total Implemented:** 30 states with custom formats
**Total Using Default:** 21 states

---

## AAMVA Field Specifications

### Field Type Categories

```
┌─────────────────────────────────────────────────────┐
│ AAMVA Data Elements (30 total)                      │
├─────────────────────────────────────────────────────┤
│                                                     │
│ IDENTIFICATION (4 fields)                          │
│   DAQ, DCF, DCG, DCA                               │
│                                                     │
│ PERSONAL NAME (3 fields)                           │
│   DCS, DAC, DAD                                    │
│                                                     │
│ DATES (5 fields)                                   │
│   DBA, DBB, DBD, DDB, DDC                         │
│                                                     │
│ PHYSICAL (5 fields)                                │
│   DBC, DAY, DAU, DAW, DAZ, DCL                    │
│                                                     │
│ ADDRESS (4 fields)                                 │
│   DAG, DAI, DAJ, DAK                              │
│                                                     │
│ LICENSE (3 fields)                                 │
│   DCB, DCD                                         │
│                                                     │
│ TRUNCATION (3 fields)                             │
│   DDE, DDF, DDG                                    │
│                                                     │
│ COMPLIANCE (3 fields)                              │
│   DDA, DDD, DDK, DDL                              │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Enumerated Value Sets

#### Eye Color Codes (DAY)

```python
EYE_COLORS = [
    "BLK",  # Black
    "BLU",  # Blue
    "BRO",  # Brown
    "GRY",  # Gray
    "GRN",  # Green
    "HAZ",  # Hazel
    "MAR",  # Maroon
    "PNK",  # Pink
    "DIC",  # Dichromatic (multicolored)
    "UNK"   # Unknown
]
```

**Distribution in Generated Data:** Random uniform selection

#### Hair Color Codes (DAZ)

```python
HAIR_COLORS = [
    "BLK",  # Black
    "BLN",  # Blond
    "BRO",  # Brown
    "GRY",  # Gray/Grey
    "RED",  # Red/Auburn
    "WHI",  # White
    "SDY",  # Sandy
    "UNK"   # Unknown
]
```

#### Race/Ethnicity Codes (DCL)

```python
RACE_CODES = [
    "W",  # White/Caucasian
    "B",  # Black/African American
    "A",  # Asian/Pacific Islander
    "I",  # American Indian/Alaskan Native
    "U"   # Unknown
]
```

#### Truncation Status (DDE, DDF, DDG)

```python
TRUNCATION_CODES = [
    "N",  # Not truncated (full name in field)
    "T",  # Truncated (name abbreviated)
    "U"   # Unknown
]
```

**Implementation:** Always "N" (never truncated) in generated data

#### DHS Compliance Type (DDA)

```python
DHS_COMPLIANCE = [
    "F",  # Full compliance (REAL ID Act compliant)
    "N"   # Non-compliant
]
```

**Distribution:** Random 50/50 split

#### Sex Codes (DBC)

```python
SEX_CODES = {
    "1": "Male",
    "2": "Female"
}
```

**Implementation:** Random selection, influences name generation

---

## Barcode Data Structure

### AAMVA PDF417 Barcode Format

```
┌──────────────────────────────────────────────────────────┐
│ AAMVA PDF417 BARCODE DATA STRUCTURE                      │
├──────────────────────────────────────────────────────────┤
│                                                          │
│ SEGMENT 1: COMPLIANCE MARKERS (3 bytes)                 │
│ ┌──────────────────────────────────────────────────┐   │
│ │ @  \n  \x1E  \r                                  │   │
│ │ 0x40 0x0A 0x1E 0x0D                              │   │
│ └──────────────────────────────────────────────────┘   │
│                                                          │
│ SEGMENT 2: HEADER (17 bytes)                            │
│ ┌──────────────────────────────────────────────────┐   │
│ │ File Type    : "ANSI " (5 bytes)                 │   │
│ │ IIN          : "636014" (6 bytes)                │   │
│ │ Version      : "10" (2 bytes)                    │   │
│ │ Jurisdiction : "00" (2 bytes)                    │   │
│ │ Num Entries  : "02" (2 bytes)                    │   │
│ └──────────────────────────────────────────────────┘   │
│                                                          │
│ SEGMENT 3: SUBFILE DESIGNATORS (10 bytes each)         │
│ ┌──────────────────────────────────────────────────┐   │
│ │ DL Subfile:                                      │   │
│ │   Type   : "DL" (2 bytes)                        │   │
│ │   Offset : "0038" (4 bytes)                      │   │
│ │   Length : "0158" (4 bytes)                      │   │
│ ├──────────────────────────────────────────────────┤   │
│ │ State Subfile:                                   │   │
│ │   Type   : "ZC" (2 bytes)                        │   │
│ │   Offset : "0196" (4 bytes)                      │   │
│ │   Length : "0047" (4 bytes)                      │   │
│ └──────────────────────────────────────────────────┘   │
│                                                          │
│ SEGMENT 4: DL SUBFILE DATA (~158 bytes)                │
│ ┌──────────────────────────────────────────────────┐   │
│ │ DL                         (subfile marker)      │   │
│ │ DAQA1234567\n             (license number)       │   │
│ │ DCAD\n                    (vehicle class)        │   │
│ │ DCB\n                     (restrictions)         │   │
│ │ DCD\n                     (endorsements)         │   │
│ │ DBA08142032\n             (expiration)           │   │
│ │ DCSDOE\n                  (last name)            │   │
│ │ DACJOHN\n                 (first name)           │   │
│ │ DADMICHAEL\n              (middle name)          │   │
│ │ DBD11202025\n             (issue date)           │   │
│ │ DBB05151990\n             (birth date)           │   │
│ │ DBC1\n                    (sex)                  │   │
│ │ DAYBRO\n                  (eye color)            │   │
│ │ DAU070\n                  (height)               │   │
│ │ DAW180\n                  (weight)               │   │
│ │ DAZBRO\n                  (hair color)           │   │
│ │ DCLW\n                    (race)                 │   │
│ │ DAG123 MAIN STREET\n      (address)             │   │
│ │ DAILOS ANGELES\n          (city)                │   │
│ │ DAJCA\n                   (state)                │   │
│ │ DAK900120000\n            (zip)                  │   │
│ │ DCFDOC12345\n             (doc discriminator)   │   │
│ │ DCGUSA\n                  (country)              │   │
│ │ DDEN\n                    (truncation family)    │   │
│ │ DDFN\n                    (truncation first)     │   │
│ │ DDGN\n                    (truncation middle)    │   │
│ │ DDAF\n                    (DHS compliance)       │   │
│ │ DDB11202025\n             (revision date)        │   │
│ │ DDC\n                     (hazmat exp)           │   │
│ │ DDD0\n                    (limited duration)     │   │
│ │ DDK1\n                    (organ donor)          │   │
│ │ DDL0\n                    (veteran)              │   │
│ │ \r                        (terminator)          │   │
│ └──────────────────────────────────────────────────┘   │
│                                                          │
│ SEGMENT 5: STATE SUBFILE DATA (~47 bytes)              │
│ ┌──────────────────────────────────────────────────┐   │
│ │ ZC                         (subfile marker)      │   │
│ │ ZCWORANGE\n                (county)              │   │
│ │ ZCTTEST STRING\n           (test field)          │   │
│ │ ZCXA123456\n               (custom field)        │   │
│ │ \r                         (terminator)          │   │
│ └──────────────────────────────────────────────────┘   │
│                                                          │
│ TOTAL SIZE: ~263 bytes (variable based on data)        │
└──────────────────────────────────────────────────────────┘
```

### Barcode Encoding Visualization

```
Raw String → PDF417 Encoder → Code Array → Image Renderer → BMP File

"@\n\x1E\r..."  →  [13 columns]  →  2D array  →  Pixel data  →  50KB file
  ~400 bytes        security=5      of codes     300x200px      BMP format
```

### Offset Calculation Example

```
Header Base: "@\n\x1E\rANSI 63601410000002"
Length: 20 bytes

Designators: "DL00380158" + "ZC01960047"
Length: 20 bytes (10 each)

Total Header + Designators: 40 bytes

DL Subfile Offset: 40 - 2 = 38 (accounting for "DL" prefix already in header)
DL Subfile Length: 158 bytes

State Subfile Offset: 38 + 158 = 196
State Subfile Length: 47 bytes

Total Barcode Size: 40 + 158 + 47 = 245 bytes (varies by data)
```

---

## Type Specifications

### Recommended TypedDict Definitions

For future type safety improvements:

```python
from typing import TypedDict, Literal

class DLSubfile(TypedDict):
    """AAMVA DL subfile data structure"""
    subfile_type: Literal["DL"]
    DAQ: str  # License number
    DCA: str  # Vehicle class
    DCB: str  # Restrictions
    DCD: str  # Endorsements
    DBA: str  # Expiration date (MMDDYYYY)
    DCS: str  # Last name
    DAC: str  # First name
    DAD: str  # Middle name
    DBD: str  # Issue date (MMDDYYYY)
    DBB: str  # Birth date (MMDDYYYY)
    DBC: Literal["1", "2"]  # Sex
    DAY: Literal["BLK", "BLU", "BRO", "GRY", "GRN", "HAZ", "MAR", "PNK", "DIC", "UNK"]
    DAU: str  # Height (inches, 3 digits)
    DAW: str  # Weight (pounds, 3 digits)
    DAZ: Literal["BLK", "BLN", "BRO", "GRY", "RED", "WHI", "SDY", "UNK"]
    DCL: Literal["W", "B", "A", "I", "U"]
    DAG: str  # Street address
    DAI: str  # City
    DAJ: str  # State (2 letters)
    DAK: str  # ZIP (9 digits)
    DCF: str  # Document discriminator
    DCG: Literal["USA", "CAN"]
    DDE: Literal["N", "T", "U"]
    DDF: Literal["N", "T", "U"]
    DDG: Literal["N", "T", "U"]
    DDA: Literal["F", "N"]
    DDB: str  # Revision date (MMDDYYYY)
    DDC: str  # Hazmat expiration (MMDDYYYY or empty)
    DDD: Literal["0", "1"]
    DDK: Literal["0", "1"]
    DDL: Literal["0", "1"]

class StateSubfile(TypedDict):
    """State-specific subfile data structure"""
    subfile_type: str  # "Z" + state initial
    # Dynamic keys based on state (ZCW, ZCT, ZCX for CA)

class IINJurisdiction(TypedDict):
    """IIN jurisdiction information"""
    jurisdiction: str  # Full name
    abbr: str         # 2-letter code
    country: Literal["USA", "Canada"]

LicenseData = list[DLSubfile | StateSubfile]
```

### Data Validation Schema

For future validation improvements:

```python
from dataclasses import dataclass
import re

@dataclass
class FieldValidator:
    """AAMVA field validation rules"""

    @staticmethod
    def validate_date(date_str: str) -> bool:
        """Validate MMDDYYYY format"""
        return bool(re.match(r'^\d{8}$', date_str))

    @staticmethod
    def validate_zip(zip_str: str) -> bool:
        """Validate 9-digit ZIP"""
        return bool(re.match(r'^\d{9}$', zip_str))

    @staticmethod
    def validate_height(height_str: str) -> bool:
        """Validate height in inches (058-078)"""
        if not re.match(r'^\d{3}$', height_str):
            return False
        height = int(height_str)
        return 58 <= height <= 78

    @staticmethod
    def validate_weight(weight_str: str) -> bool:
        """Validate weight in pounds (115-275)"""
        if not re.match(r'^\d{3}$', weight_str):
            return False
        weight = int(weight_str)
        return 115 <= weight <= 275
```

---

## Data Size Analysis

### Memory Footprint

```
Single License:
├── DL Subfile Dict: ~1.5 KB (31 entries × ~50 bytes avg)
├── State Subfile Dict: ~0.3 KB (4 entries × ~75 bytes avg)
├── Total in Memory: ~2 KB per license
│
└── Encoded Forms:
    ├── AAMVA String: ~400 bytes
    ├── PDF417 Code Array: ~2 KB
    ├── BMP Image: ~50 KB
    ├── PNG Card: ~100 KB
    └── Total Disk: ~150 KB per license

Batch of 100 Licenses:
├── Python Objects: ~200 KB
├── Barcode Files: ~5 MB (BMPs)
├── Card Images: ~10 MB (PNGs)
├── PDF Document: ~5 MB
├── DOCX Document: ~10 MB
└── Total: ~30 MB
```

### Character Encoding

All strings use **ASCII encoding** (7-bit):
- Letters: Uppercase A-Z only
- Digits: 0-9
- Special: Space, newline, carriage return
- Control: \x1E (record separator)

**No Unicode support** - AAMVA standard is ASCII-only.

---

## Conclusion

The data structures in AAMVA ID Faker are **simple and effective** for their purpose but lack modern type safety features. The dictionary-based approach keeps the code straightforward but sacrifices compile-time validation and IDE autocomplete support.

### Recommendations:
1. Add TypedDict definitions for all data structures
2. Implement validation schemas for AAMVA fields
3. Create dataclass wrappers for better structure
4. Add Pydantic models for runtime validation
5. Document exact byte offsets and sizes
6. Provide JSON schema for external integrations

**Overall Data Structure Quality: 7/10** - Functional and clear, but could benefit from modern Python typing features.
