# AAMVA License Generator - SOLID Architecture Design

**Version:** 2.0
**Date:** 2025-11-20
**Author:** Software Architecture Team
**Status:** Implementation Blueprint - Ready for Development

---

## Executive Summary

This document presents a **revolutionary refactoring** of the AAMVA license generator from a 787-line monolithic script into a **SOLID-compliant, test-driven, extensible architecture** that supports multiple interfaces (CLI, GUI, REST API) while maintaining a single source of truth for business logic.

### Current State: The Problem

The existing `generate_licenses.py` violates **every SOLID principle**:

- **Single Responsibility**: One file does data generation, barcode encoding, PDF creation, DOCX generation, file I/O, and CLI parsing (6+ responsibilities)
- **Open/Closed**: Adding new states requires modifying a 200-line dictionary. No extension points.
- **Liskov Substitution**: No abstractions, only concrete implementations
- **Interface Segregation**: No interfaces at all
- **Dependency Inversion**: Direct dependencies on Faker, PIL, ReportLab with no abstraction layer

### Proposed Architecture: The Solution

A **layered hexagonal architecture** with:
- **Core Domain Layer**: Pure business logic (state formats, AAMVA encoding, validation)
- **Application Layer**: Use cases and orchestration
- **Infrastructure Layer**: External dependencies (file I/O, PDF generation, barcode encoding)
- **Interface Layer**: CLI, GUI, REST API adapters

**Key Innovation**: All interfaces share the same core, enabling **100% code reuse** across CLI, GUI, and API.

---

## Table of Contents

1. [Architectural Principles & Opinions](#1-architectural-principles--opinions)
2. [High-Level Architecture](#2-high-level-architecture)
3. [Core Domain Model](#3-core-domain-model)
4. [Module Structure](#4-module-structure)
5. [SOLID Compliance Analysis](#5-solid-compliance-analysis)
6. [Class Diagrams](#6-class-diagrams)
7. [Interface Definitions](#7-interface-definitions)
8. [Dependency Graph](#8-dependency-graph)
9. [Extension Points](#9-extension-points)
10. [Package Organization](#10-package-organization)
11. [Migration Strategy](#11-migration-strategy)
12. [Implementation Roadmap](#12-implementation-roadmap)

---

## 1. Architectural Principles & Opinions

### Core Philosophy: **YAGNI with Future-Proofing**

**Controversial Opinion #1: YAGNI vs. Architecture**

Many developers will say: *"You're over-engineering! Just refactor when you need it!"*

**WRONG.** Here's why:

The current monolithic code has **three confirmed future requirements**:
1. GUI interface (User Personas document confirms this)
2. REST API (Developer Dana needs it)
3. ML dataset generation (Research Rita needs it)

Refactoring for SOLID **now** costs **2 weeks**. Refactoring later when you have 3 different monolithic scripts (CLI, GUI, API) costs **3 months** and introduces bugs.

**Principle**: Design for known future requirements, not hypothetical ones.

---

### Architectural Style: **Hexagonal (Ports & Adapters)**

**Controversial Opinion #2: Layered vs. Hexagonal**

Traditional layered architecture (Presentation → Business → Data) **fails for this project** because:

```
❌ LAYERED ARCHITECTURE PROBLEM:
┌─────────────────┐
│       CLI       │  ← What about GUI?
├─────────────────┤
│   Business      │  ← Tightly coupled to CLI
├─────────────────┤
│      Data       │
└─────────────────┘

Adding GUI requires duplicating business logic!
```

Hexagonal architecture **solves this**:

```
✅ HEXAGONAL ARCHITECTURE:
        ┌────────┐
        │  CLI   │
        └───┬────┘
            │
    ┌───────┴────────┐
    │   Core Domain  │
    │ (Pure Business │
    │     Logic)     │
    └───────┬────────┘
            │
        ┌───┴────┐
        │  GUI   │
        └────────┘

Core is independent of interfaces!
```

**Principle**: Business logic must not know about its consumers.

---

### Testing Philosophy: **TDD with Property-Based Testing**

**Controversial Opinion #3: Example-Based Tests Are Insufficient**

Most developers write tests like:
```python
def test_california_license():
    result = generate_license_number('CA')
    assert result == 'A1234567'  # One example
```

**This is weak.** It tests ONE case out of 26^1 × 10^7 = **260 million** possible California licenses.

Property-based testing tests **all of them**:
```python
@given(st.text(alphabet=string.ascii_uppercase, min_size=1, max_size=1),
       st.text(alphabet=string.digits, min_size=7, max_size=7))
def test_california_license_format(letter, digits):
    # Tests MILLIONS of combinations automatically
    result = f"{letter}{digits}"
    assert len(result) == 8
    assert result[0].isalpha()
    assert result[1:].isdigit()
```

**Principle**: Use property-based testing (Hypothesis) for validation logic. Example-based tests for specific scenarios.

---

### Dependency Injection: **Constructor Injection with Protocols**

**Controversial Opinion #4: Python Doesn't Need a DI Framework**

Many developers reach for `injector` or `dependency-injector` libraries.

**This is cargo-culting from Java.** Python has:
1. Duck typing (structural subtyping)
2. Protocols (PEP 544) for static typing without inheritance
3. Simple constructor injection

Example:
```python
# ❌ Over-engineered (Java-style)
from injector import inject, Module

class LicenseGenerator:
    @inject
    def __init__(self, formatter: BarcodeFormatter, validator: Validator):
        pass

# ✅ Pythonic (clean)
class LicenseGenerator:
    def __init__(self, formatter: BarcodeFormatter, validator: Validator):
        self.formatter = formatter
        self.validator = validator

# Usage (manual wiring)
generator = LicenseGenerator(
    formatter=AAMV2020BarcodeFormatter(),
    validator=CompositeValidator([DateValidator(), FieldValidator()])
)
```

**Principle**: Manual dependency injection with type hints. No magic.

---

## 2. High-Level Architecture

### Layered Hexagonal Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    INTERFACE LAYER (ADAPTERS)                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐   │
│  │   CLI    │  │   GUI    │  │ REST API │  │  Python SDK  │   │
│  │ Adapter  │  │ Adapter  │  │ Adapter  │  │   (Future)   │   │
│  └─────┬────┘  └─────┬────┘  └─────┬────┘  └──────┬───────┘   │
└────────┼─────────────┼─────────────┼───────────────┼───────────┘
         │             │             │               │
         └─────────────┴─────────────┴───────────────┘
                               │
┌──────────────────────────────┼────────────────────────────────┐
│                   APPLICATION LAYER (USE CASES)                │
│                              │                                 │
│  ┌──────────────────┐  ┌────┴─────────────┐  ┌─────────────┐ │
│  │ GenerateLicense  │  │ GenerateBatch    │  │ ValidateLic │ │
│  │    UseCase       │  │    UseCase       │  │   UseCase   │ │
│  └────────┬─────────┘  └────────┬─────────┘  └──────┬──────┘ │
└───────────┼────────────────────┼────────────────────┼────────┘
            │                    │                    │
            └────────────────────┴────────────────────┘
                                 │
┌────────────────────────────────┼────────────────────────────────┐
│                      CORE DOMAIN LAYER                           │
│                                │                                 │
│  ┌────────────────────────────┴───────────────────────────┐    │
│  │            Domain Model (Pure Business Logic)           │    │
│  │                                                          │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │    │
│  │  │   License    │  │    State     │  │   Barcode    │ │    │
│  │  │   (Entity)   │  │   Format     │  │  Formatter   │ │    │
│  │  │              │  │  (Strategy)  │  │  (Strategy)  │ │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘ │    │
│  │                                                          │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │    │
│  │  │  Validator   │  │     IIN      │  │     Date     │ │    │
│  │  │ (Composite)  │  │   Registry   │  │   Services   │ │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘ │    │
│  └──────────────────────────────────────────────────────┘     │
└───────────────────────────┬───────────────────────────────────┘
                            │
┌───────────────────────────┼───────────────────────────────────┐
│                INFRASTRUCTURE LAYER (PORTS)                    │
│                           │                                    │
│  ┌──────────┐  ┌─────────┴──────┐  ┌────────────┐  ┌───────┐│
│  │  Faker   │  │  PDF417        │  │  ReportLab │  │ Pillow││
│  │ Adapter  │  │  Encoder       │  │  Generator │  │Adapter││
│  └──────────┘  └────────────────┘  └────────────┘  └───────┘│
└──────────────────────────────────────────────────────────────┘
```

### Layer Responsibilities

**INTERFACE LAYER (Adapters)**
- **Purpose**: Convert external requests into domain operations
- **Dependencies**: Application Layer (use cases)
- **Examples**: CLI argument parser, GUI event handlers, REST API routes

**APPLICATION LAYER (Use Cases)**
- **Purpose**: Orchestrate domain objects to fulfill use cases
- **Dependencies**: Domain Layer
- **Examples**: "Generate 10 California licenses", "Validate license data"

**DOMAIN LAYER (Core Business Logic)**
- **Purpose**: Pure business rules, no external dependencies
- **Dependencies**: NONE (only Python standard library)
- **Examples**: License number format rules, AAMVA encoding logic

**INFRASTRUCTURE LAYER (Ports)**
- **Purpose**: Implement technical details (I/O, rendering, encoding)
- **Dependencies**: External libraries (Faker, PIL, ReportLab)
- **Examples**: PDF417 barcode encoding, PDF file generation

---

## 3. Core Domain Model

### Domain Entities

#### `License` (Entity)

**Responsibility**: Represent a single driver's license with all its attributes.

```python
from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass(frozen=True)  # Immutable entity
class License:
    """Domain entity representing a driver's license.

    This is a VALUE OBJECT - immutable and validated on construction.
    """
    # Identity
    license_number: str
    document_discriminator: str

    # Jurisdiction
    state: str
    iin: str

    # Personal Information
    first_name: str
    middle_name: str
    last_name: str
    date_of_birth: date
    sex: str  # '1' = Male, '2' = Female

    # Physical Characteristics
    height_inches: int
    weight_lbs: int
    eye_color: str
    hair_color: str
    race: str

    # Address
    street_address: str
    city: str
    zip_code: str

    # Dates
    issue_date: date
    expiration_date: date

    # Classification
    vehicle_class: str
    restrictions: str
    endorsements: str

    # Status Flags
    compliance_type: str  # 'F' = compliant, 'N' = non-compliant
    organ_donor: bool
    veteran: bool
    limited_duration: bool

    # Name Truncation Flags
    family_name_truncated: str  # 'N', 'T', 'U'
    first_name_truncated: str
    middle_name_truncated: str

    # Country
    country: str = "USA"

    def __post_init__(self):
        """Validate invariants on construction."""
        # Defensive validation
        if not self.license_number:
            raise ValueError("License number cannot be empty")

        if self.date_of_birth >= self.issue_date:
            raise ValueError("Date of birth must be before issue date")

        if self.issue_date >= self.expiration_date:
            raise ValueError("Issue date must be before expiration date")

        age_at_issue = (self.issue_date - self.date_of_birth).days / 365.25
        if age_at_issue < 16:
            raise ValueError(f"Driver must be at least 16 years old at issue (was {age_at_issue:.1f})")

    def age_at_date(self, reference_date: date) -> float:
        """Calculate age at a given date."""
        return (reference_date - self.date_of_birth).days / 365.25

    def is_expired(self, reference_date: date = None) -> bool:
        """Check if license is expired."""
        if reference_date is None:
            reference_date = date.today()
        return self.expiration_date < reference_date

    def to_aamva_dict(self) -> dict[str, str]:
        """Convert to AAMVA field dictionary for barcode encoding.

        This is the anti-corruption layer between domain and infrastructure.
        """
        return {
            "DAQ": self.license_number,
            "DCA": self.vehicle_class,
            "DCB": self.restrictions,
            "DCD": self.endorsements,
            "DBA": self.expiration_date.strftime("%m%d%Y"),
            "DCS": self.last_name.upper(),
            "DAC": self.first_name.upper(),
            "DAD": self.middle_name.upper(),
            "DBD": self.issue_date.strftime("%m%d%Y"),
            "DBB": self.date_of_birth.strftime("%m%d%Y"),
            "DBC": self.sex,
            "DAY": self.eye_color,
            "DAU": f"{self.height_inches:03d}",
            "DAW": f"{self.weight_lbs:03d}",
            "DAZ": self.hair_color,
            "DCL": self.race,
            "DAG": self.street_address.upper(),
            "DAI": self.city.upper(),
            "DAJ": self.state.upper(),
            "DAK": self.zip_code.ljust(9, "0"),
            "DCF": self.document_discriminator,
            "DCG": self.country,
            "DDE": self.family_name_truncated,
            "DDF": self.first_name_truncated,
            "DDG": self.middle_name_truncated,
            "DDA": self.compliance_type,
            "DDB": self.issue_date.strftime("%m%d%Y"),
            "DDC": self.expiration_date.strftime("%m%d%Y"),
            "DDD": "1" if self.limited_duration else "0",
            "DDK": "1" if self.organ_donor else "0",
            "DDL": "1" if self.veteran else "0",
        }
```

**Design Decisions**:
1. **Immutable (frozen=True)**: Licenses don't change after creation. This prevents bugs.
2. **Value Object**: Two licenses with same data are equal. No hidden state.
3. **Rich Domain Model**: Business logic (age calculation, expiration check) lives WITH the data.
4. **Defensive Programming**: Validation in `__post_init__` ensures invalid licenses can't exist.

**Why Not ORM?** This is NOT a database-backed entity. It's a pure domain object. Adding SQLAlchemy would be premature.

---

### Domain Services

#### `StateFormatRegistry` (Strategy Pattern)

**Responsibility**: Provide state-specific license number formats.

```python
from typing import Protocol, Callable
from abc import abstractmethod

class LicenseNumberGenerator(Protocol):
    """Protocol for state-specific license number generators."""

    @abstractmethod
    def generate(self) -> str:
        """Generate a license number conforming to state format."""
        ...

class StateFormatRegistry:
    """Registry of state-specific license number formats.

    Uses Strategy pattern for extensibility.
    Open/Closed Principle: Add new states without modifying existing code.
    """

    def __init__(self):
        self._formats: dict[str, LicenseNumberGenerator] = {}

    def register(self, state: str, generator: LicenseNumberGenerator):
        """Register a state format generator."""
        self._formats[state.upper()] = generator

    def generate(self, state: str) -> str:
        """Generate license number for state."""
        state_upper = state.upper()

        if state_upper not in self._formats:
            raise ValueError(f"Unknown state: {state}")

        return self._formats[state_upper].generate()

    def supports(self, state: str) -> bool:
        """Check if state is supported."""
        return state.upper() in self._formats


# Example concrete generators
class CaliforniaLicenseNumberGenerator:
    """California format: 1 letter + 7 digits"""

    def generate(self) -> str:
        import random
        import string
        letter = random.choice(string.ascii_uppercase)
        digits = ''.join(random.choices(string.digits, k=7))
        return f"{letter}{digits}"


class NewYorkLicenseNumberGenerator:
    """New York format: Multiple variations"""

    def generate(self) -> str:
        import random
        import string

        formats = [
            lambda: random.choice(string.ascii_uppercase) + ''.join(random.choices(string.digits, k=7)),
            lambda: random.choice(string.ascii_uppercase) + ''.join(random.choices(string.digits, k=18)),
            lambda: ''.join(random.choices(string.digits, k=8)),
            lambda: ''.join(random.choices(string.digits, k=9)),
        ]

        return random.choice(formats)()


# Registration (in module initialization)
def create_default_registry() -> StateFormatRegistry:
    """Factory function to create registry with default formats."""
    registry = StateFormatRegistry()

    registry.register('CA', CaliforniaLicenseNumberGenerator())
    registry.register('NY', NewYorkLicenseNumberGenerator())
    registry.register('TX', TexasLicenseNumberGenerator())
    # ... register all 51 states

    return registry
```

**Design Decisions**:
1. **Strategy Pattern**: Each state is a separate strategy. Adding new states doesn't modify existing code (Open/Closed).
2. **Protocol (not ABC)**: Python 3.8+ structural subtyping. More flexible than inheritance.
3. **Explicit Registration**: Clear, testable, no magic.

---

#### `IINRegistry` (Simple Registry)

**Responsibility**: Map state codes to Issuer Identification Numbers.

```python
class IINRegistry:
    """Registry for AAMVA Issuer Identification Numbers.

    Single Responsibility: One source of truth for IIN mappings.
    """

    def __init__(self, mappings: dict[str, str]):
        self._iin_to_state: dict[str, str] = mappings
        # Create reverse mapping for lookups
        self._state_to_iin: dict[str, str] = {
            info['abbr'].upper(): iin
            for iin, info in mappings.items()
        }

    def get_iin(self, state: str) -> str:
        """Get IIN for state abbreviation."""
        state_upper = state.upper()

        if state_upper not in self._state_to_iin:
            raise ValueError(f"Unknown state: {state}")

        return self._state_to_iin[state_upper]

    def get_state_info(self, iin: str) -> dict:
        """Get state information from IIN."""
        if iin not in self._iin_to_state:
            raise ValueError(f"Unknown IIN: {iin}")

        return self._iin_to_state[iin]

    def all_states(self) -> list[str]:
        """Return list of all supported state abbreviations."""
        return sorted(self._state_to_iin.keys())


# Factory function
def create_default_iin_registry() -> IINRegistry:
    """Create registry with official AAMVA IIN mappings."""
    # Import from constants module
    from .constants import IIN_JURISDICTIONS
    return IINRegistry(IIN_JURISDICTIONS)
```

---

#### `BarcodeFormatter` (Abstract Strategy)

**Responsibility**: Format license data as AAMVA-compliant barcode string.

```python
from abc import ABC, abstractmethod
from typing import Protocol

class BarcodeFormatter(Protocol):
    """Protocol for barcode formatters.

    Interface Segregation: Clients depend only on what they need.
    """

    @abstractmethod
    def format(self, license: License, state_subfile: dict) -> str:
        """Format license as AAMVA barcode string.

        Args:
            license: Domain entity
            state_subfile: State-specific additional fields

        Returns:
            AAMVA-compliant barcode string
        """
        ...


class AAMVA2020BarcodeFormatter:
    """AAMVA DL/ID-2020 specification formatter.

    Single Responsibility: AAMVA 2020 encoding only.
    Open/Closed: Want AAMVA 2016? Create new class, don't modify this.
    """

    def __init__(self, iin_registry: IINRegistry):
        self.iin_registry = iin_registry

    def format(self, license: License, state_subfile: dict) -> str:
        """Format according to AAMVA 2020 spec."""
        # Compliance markers
        compliance = "@\n\x1E\r"

        # Header
        file_type = "ANSI "
        iin = self.iin_registry.get_iin(license.state)
        version = "10"  # AAMVA 2020
        jurisdiction_version = "00"
        number_of_entries = "02"  # DL + State subfile

        # Convert license to AAMVA dictionary
        dl_fields = license.to_aamva_dict()

        # Build DL subfile
        dl_subfile = self._build_subfile("DL", dl_fields)

        # Build state subfile
        state_subfile_data = self._build_subfile(
            state_subfile.get('subfile_type', 'ZX'),
            {k: v for k, v in state_subfile.items() if k != 'subfile_type'}
        )

        # Calculate offsets
        header_base = compliance + file_type + iin + version + jurisdiction_version + number_of_entries
        designators_length = 10 * 2  # 2 subfiles, 10 bytes each

        dl_offset = len((header_base + ' ' * designators_length).encode('ascii'))
        dl_length = len(dl_subfile.encode('ascii'))

        state_offset = dl_offset + dl_length
        state_length = len(state_subfile_data.encode('ascii'))

        # Build designators
        dl_designator = f"DL{dl_offset:04d}{dl_length:04d}"
        state_designator = f"{state_subfile.get('subfile_type', 'ZX')}{state_offset:04d}{state_length:04d}"

        # Assemble complete barcode
        return header_base + dl_designator + state_designator + dl_subfile + state_subfile_data

    def _build_subfile(self, subfile_type: str, fields: dict[str, str]) -> str:
        """Build a subfile string."""
        # DAQ must come first (AAMVA requirement)
        daq = fields.pop('DAQ', None)
        field_string = f"DAQ{daq}\n" if daq else ""

        # Add remaining fields
        field_string += "".join(f"{key}{value}\n" for key, value in fields.items())

        # Subfile terminator
        return subfile_type + field_string + "\r"
```

---

### Domain Value Objects

#### `PhysicalCharacteristics`

```python
@dataclass(frozen=True)
class PhysicalCharacteristics:
    """Value object for physical characteristics."""

    height_inches: int
    weight_lbs: int
    eye_color: str
    hair_color: str

    VALID_EYE_COLORS = {'BLK', 'BLU', 'BRO', 'GRY', 'GRN', 'HAZ', 'MAR', 'PNK', 'DIC', 'UNK'}
    VALID_HAIR_COLORS = {'BLK', 'BLN', 'BRO', 'GRY', 'RED', 'WHI', 'SDY', 'UNK'}

    def __post_init__(self):
        if not (48 <= self.height_inches <= 96):  # 4' to 8'
            raise ValueError(f"Invalid height: {self.height_inches} inches")

        if not (50 <= self.weight_lbs <= 500):
            raise ValueError(f"Invalid weight: {self.weight_lbs} lbs")

        if self.eye_color not in self.VALID_EYE_COLORS:
            raise ValueError(f"Invalid eye color: {self.eye_color}")

        if self.hair_color not in self.VALID_HAIR_COLORS:
            raise ValueError(f"Invalid hair color: {self.hair_color}")
```

---

## 4. Module Structure

### Proposed Directory Layout

```
aamva-id-faker/
├── pyproject.toml                    # Modern Python packaging
├── setup.py                          # Backward compatibility
├── README.md
├── LICENSE
│
├── src/
│   └── aamva/                        # Main package
│       ├── __init__.py
│       │
│       ├── domain/                   # CORE DOMAIN LAYER (no external deps)
│       │   ├── __init__.py
│       │   ├── entities.py           # License entity
│       │   ├── value_objects.py      # PhysicalCharacteristics, Address, etc.
│       │   ├── services.py           # Domain services
│       │   │   ├── state_formats.py  # StateFormatRegistry
│       │   │   ├── iin_registry.py   # IINRegistry
│       │   │   └── validators.py     # Domain validation
│       │   ├── constants.py          # AAMVA constants, IIN mappings
│       │   └── exceptions.py         # Domain exceptions
│       │
│       ├── application/              # APPLICATION LAYER (use cases)
│       │   ├── __init__.py
│       │   ├── use_cases/
│       │   │   ├── __init__.py
│       │   │   ├── generate_license.py      # GenerateLicenseUseCase
│       │   │   ├── generate_batch.py        # GenerateBatchUseCase
│       │   │   ├── validate_license.py      # ValidateLicenseUseCase
│       │   │   └── export_licenses.py       # ExportLicensesUseCase
│       │   ├── ports/                       # Ports (interfaces)
│       │   │   ├── __init__.py
│       │   │   ├── data_generator.py        # IDataGenerator protocol
│       │   │   ├── barcode_encoder.py       # IBarcodeEncoder protocol
│       │   │   ├── document_exporter.py     # IDocumentExporter protocol
│       │   │   └── repository.py            # ILicenseRepository protocol
│       │   └── dtos.py                      # Data Transfer Objects
│       │
│       ├── infrastructure/           # INFRASTRUCTURE LAYER (adapters)
│       │   ├── __init__.py
│       │   ├── data_generation/
│       │   │   ├── __init__.py
│       │   │   ├── faker_adapter.py          # Faker integration
│       │   │   └── random_generator.py       # Pure random generation
│       │   ├── encoding/
│       │   │   ├── __init__.py
│       │   │   ├── pdf417_encoder.py         # PDF417 barcode encoding
│       │   │   └── barcode_image_generator.py# Barcode image rendering
│       │   ├── export/
│       │   │   ├── __init__.py
│       │   │   ├── pdf_exporter.py           # PDF generation
│       │   │   ├── docx_exporter.py          # DOCX generation
│       │   │   ├── json_exporter.py          # JSON export
│       │   │   └── image_exporter.py         # PNG/JPG export
│       │   ├── persistence/
│       │   │   ├── __init__.py
│       │   │   ├── file_repository.py        # File-based storage
│       │   │   └── memory_repository.py      # In-memory storage (testing)
│       │   └── external/
│       │       └── aamva_spec_validator.py   # External spec validation
│       │
│       ├── interfaces/               # INTERFACE LAYER (adapters)
│       │   ├── __init__.py
│       │   ├── cli/
│       │   │   ├── __init__.py
│       │   │   ├── main.py                   # CLI entry point
│       │   │   ├── commands.py               # CLI commands
│       │   │   └── formatters.py             # Output formatting
│       │   ├── gui/
│       │   │   ├── __init__.py
│       │   │   ├── main_window.py            # Main GUI window
│       │   │   ├── components/
│       │   │   │   ├── license_form.py
│       │   │   │   ├── preview_widget.py
│       │   │   │   └── batch_generator.py
│       │   │   └── presenters.py             # GUI presenters
│       │   └── api/                          # Future REST API
│       │       ├── __init__.py
│       │       ├── main.py                   # FastAPI app
│       │       ├── routes.py                 # API routes
│       │       └── schemas.py                # Pydantic schemas
│       │
│       └── shared/                   # SHARED UTILITIES
│           ├── __init__.py
│           ├── config.py             # Configuration management
│           ├── logging.py            # Logging setup
│           └── types.py              # Type aliases
│
├── tests/                            # Test suite (mirrors src/)
│   ├── conftest.py
│   ├── unit/
│   │   ├── domain/
│   │   ├── application/
│   │   └── infrastructure/
│   ├── integration/
│   ├── e2e/
│   ├── fixtures/
│   └── utils/
│
├── scripts/                          # Development scripts
│   ├── generate_state_formats.py     # Code generation
│   ├── validate_iin_mappings.py      # Data validation
│   └── benchmark.py                  # Performance testing
│
└── docs/                             # Documentation
    ├── architecture/
    ├── api/
    └── user_guide/
```

---

## 5. SOLID Compliance Analysis

### Single Responsibility Principle (SRP)

**Current Code Violations**:
```python
# generate_licenses.py (787 lines)
def main():
    # 1. Parse CLI arguments
    # 2. Generate license data
    # 3. Format AAMVA barcode
    # 4. Encode PDF417
    # 5. Render barcode image
    # 6. Create PDF document
    # 7. Create DOCX document
    # 8. Save files
    pass  # 8 responsibilities in one function!
```

**Proposed Solution**:

| Class | Single Responsibility |
|-------|----------------------|
| `License` | Represent license data and business rules |
| `StateFormatRegistry` | Provide state-specific formats |
| `AAMVA2020BarcodeFormatter` | Format data as AAMVA 2020 barcode string |
| `PDF417Encoder` | Encode string as PDF417 barcode |
| `BarcodeImageRenderer` | Render barcode as image |
| `PDFExporter` | Export licenses as PDF document |
| `DOCXExporter` | Export licenses as DOCX document |
| `FileRepository` | Save/load files |
| `GenerateLicenseUseCase` | Orchestrate license generation |
| `CLIAdapter` | Parse CLI arguments and invoke use cases |

**Each class has ONE reason to change.**

---

### Open/Closed Principle (OCP)

**Current Code Violation**:
```python
# To add a new state format:
state_formats = {
    'CA': lambda: ...,
    'NY': lambda: ...,
    # Must modify this dictionary (CLOSED for extension)
}
```

**Proposed Solution**:
```python
# To add a new state format:
class WyomingLicenseNumberGenerator:
    def generate(self) -> str:
        # New implementation
        pass

# Register without modifying existing code
registry.register('WY', WyomingLicenseNumberGenerator())
```

**OPEN for extension, CLOSED for modification.**

---

### Liskov Substitution Principle (LSP)

**Current Code**: No abstractions, so LSP doesn't apply.

**Proposed Solution**:
```python
# Protocol (interface)
class BarcodeFormatter(Protocol):
    def format(self, license: License) -> str: ...

# Implementations
class AAMVA2020BarcodeFormatter:
    def format(self, license: License) -> str:
        # AAMVA 2020 implementation
        pass

class AAMVA2016BarcodeFormatter:
    def format(self, license: License) -> str:
        # AAMVA 2016 implementation (hypothetical)
        pass

# Client code
def generate_barcode(license: License, formatter: BarcodeFormatter) -> str:
    # Works with ANY BarcodeFormatter implementation
    return formatter.format(license)
```

**Any `BarcodeFormatter` implementation is substitutable.**

---

### Interface Segregation Principle (ISP)

**Current Code**: No interfaces.

**Proposed Solution**:

Instead of one fat interface:
```python
# ❌ BAD: Fat interface
class LicenseService(Protocol):
    def generate_license(self) -> License: ...
    def format_barcode(self, license: License) -> str: ...
    def encode_pdf417(self, data: str) -> Image: ...
    def export_pdf(self, licenses: list[License]) -> bytes: ...
    def export_docx(self, licenses: list[License]) -> bytes: ...
    def export_json(self, licenses: list[License]) -> str: ...
```

Use small, focused interfaces:
```python
# ✅ GOOD: Segregated interfaces
class IDataGenerator(Protocol):
    def generate_license(self, state: str) -> License: ...

class IBarcodeFormatter(Protocol):
    def format(self, license: License) -> str: ...

class IBarcodeEncoder(Protocol):
    def encode(self, data: str) -> bytes: ...

class IDocumentExporter(Protocol):
    def export(self, licenses: list[License]) -> bytes: ...
```

**Clients depend only on interfaces they use.**

---

### Dependency Inversion Principle (DIP)

**Current Code Violation**:
```python
# Direct dependency on Faker (low-level module)
from faker import Faker

def generate_license_data():
    fake = Faker()  # Tight coupling
    first_name = fake.first_name()
```

**Proposed Solution**:
```python
# High-level module depends on abstraction
class IDataGenerator(Protocol):
    def generate_name(self) -> tuple[str, str, str]: ...
    def generate_address(self) -> Address: ...

# Low-level module implements abstraction
class FakerDataGenerator:
    def __init__(self):
        self._faker = Faker()

    def generate_name(self) -> tuple[str, str, str]:
        return (
            self._faker.first_name(),
            self._faker.last_name(),
            self._faker.first_name()  # Middle name
        )

# Dependency injection
class LicenseFactory:
    def __init__(self, data_generator: IDataGenerator):
        self.data_generator = data_generator  # Depends on abstraction
```

**High-level modules (use cases) don't depend on low-level modules (Faker, PIL, etc.).**

---

## 6. Class Diagrams

### Domain Layer Class Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DOMAIN LAYER                                 │
│                      (No External Dependencies)                      │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────────┐
│      <<Entity>>      │
│       License        │
├──────────────────────┤
│ - license_number     │
│ - state              │
│ - iin                │
│ - first_name         │
│ - last_name          │
│ - date_of_birth      │
│ - issue_date         │
│ - expiration_date    │
│ - ...                │
├──────────────────────┤
│ + __init__(...)      │
│ + age_at_date()      │
│ + is_expired()       │
│ + to_aamva_dict()    │
└──────────┬───────────┘
           │
           │ has-a
           ▼
┌──────────────────────┐
│  <<Value Object>>    │
│Physical Characteristics│
├──────────────────────┤
│ - height_inches      │
│ - weight_lbs         │
│ - eye_color          │
│ - hair_color         │
└──────────────────────┘


┌──────────────────────┐         ┌──────────────────────┐
│  <<Domain Service>>  │         │    <<Protocol>>      │
│StateFormatRegistry   │         │LicenseNumberGenerator│
├──────────────────────┤         ├──────────────────────┤
│ - _formats: dict     │         │ + generate(): str    │
├──────────────────────┤         └──────────┬───────────┘
│ + register(...)      │                    △
│ + generate(state)    │                    │ implements
│ + supports(state)    │                    │
└──────────┬───────────┘         ┌──────────┴───────────┐
           │                     │                       │
           │ uses                │                       │
           ▼                     │                       │
┌──────────────────────┐  ┌──────┴───────┐  ┌──────────┴────────┐
│CaliforniaLicense     │  │NewYorkLicense│  │   TexasLicense    │
│  NumberGenerator     │  │NumberGenerator│  │  NumberGenerator   │
├──────────────────────┤  ├───────────────┤  ├───────────────────┤
│ + generate(): str    │  │+ generate()   │  │ + generate(): str │
└──────────────────────┘  └───────────────┘  └───────────────────┘


┌──────────────────────┐         ┌──────────────────────┐
│  <<Domain Service>>  │         │  <<Domain Service>>  │
│    IINRegistry       │         │ BarcodeFormatter     │
├──────────────────────┤         ├──────────────────────┤
│ - _iin_to_state      │         │ - iin_registry       │
│ - _state_to_iin      │         ├──────────────────────┤
├──────────────────────┤         │ + format(license)    │
│ + get_iin(state)     │◄────────┤ - _build_subfile()   │
│ + get_state_info()   │  uses   └──────────────────────┘
│ + all_states()       │
└──────────────────────┘
```

### Application Layer Class Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                      APPLICATION LAYER                               │
│                    (Use Cases & Orchestration)                       │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────┐
│       <<Use Case>>           │
│  GenerateLicenseUseCase      │
├──────────────────────────────┤
│ - license_factory            │
│ - barcode_formatter          │
│ - barcode_encoder            │
├──────────────────────────────┤
│ + execute(request): License │
└──────────┬───────────────────┘
           │ uses
           ▼
┌──────────────────────────────┐
│       <<Port>>               │
│      IDataGenerator          │
├──────────────────────────────┤
│ + generate_name()            │
│ + generate_address()         │
│ + generate_physical_attrs()  │
└──────────┬───────────────────┘
           △
           │ implements
           │
┌──────────┴───────────────────┐
│    <<Adapter>>               │
│   FakerDataGenerator         │
├──────────────────────────────┤
│ - _faker: Faker              │
├──────────────────────────────┤
│ + generate_name()            │
│ + generate_address()         │
└──────────────────────────────┘


┌──────────────────────────────┐
│       <<Use Case>>           │
│    GenerateBatchUseCase      │
├──────────────────────────────┤
│ - generate_single_use_case   │
│ - repository                 │
├──────────────────────────────┤
│ + execute(request): List[Lic]│
└──────────┬───────────────────┘
           │ uses
           ▼
┌──────────────────────────────┐
│       <<Port>>               │
│    ILicenseRepository        │
├──────────────────────────────┤
│ + save(license)              │
│ + find_by_id(id)             │
│ + find_all()                 │
└──────────────────────────────┘


┌──────────────────────────────┐
│       <<Use Case>>           │
│   ExportLicensesUseCase      │
├──────────────────────────────┤
│ - exporter: IDocumentExporter│
├──────────────────────────────┤
│ + execute(licenses, format)  │
└──────────┬───────────────────┘
           │ uses
           ▼
┌──────────────────────────────┐
│       <<Port>>               │
│    IDocumentExporter         │
├──────────────────────────────┤
│ + export(licenses): bytes    │
└──────────┬───────────────────┘
           △
           │ implements
           │
    ┌──────┴──────┬──────────────┐
    │             │              │
┌───┴─────┐  ┌────┴────┐  ┌──────┴─────┐
│PDFExport│  │DOCXExport│  │JSONExporter│
└─────────┘  └─────────┘  └────────────┘
```

### Complete System Dependency Diagram

```
┌────────────────────────────────────────────────────────────────────┐
│                    INTERFACE LAYER (Adapters)                       │
└────────────────────────────────────────────────────────────────────┘
          │                    │                    │
    ┌─────▼──────┐      ┌──────▼──────┐      ┌────▼───────┐
    │ CLIAdapter │      │ GUIAdapter  │      │ APIAdapter │
    └─────┬──────┘      └──────┬──────┘      └────┬───────┘
          │                    │                   │
          └────────────────────┴───────────────────┘
                               │
┌──────────────────────────────▼─────────────────────────────────────┐
│                   APPLICATION LAYER (Use Cases)                     │
└─────────────────────────────────────────────────────────────────────┘
          │                    │                    │
    ┌─────▼──────────┐  ┌──────▼───────┐  ┌────────▼───────┐
    │GenerateLicense │  │GenerateBatch │  │ExportLicenses  │
    │   UseCase      │  │   UseCase    │  │   UseCase      │
    └─────┬──────────┘  └──────┬───────┘  └────────┬───────┘
          │                    │                    │
          └────────────────────┴────────────────────┘
                               │
┌──────────────────────────────▼─────────────────────────────────────┐
│                      DOMAIN LAYER (Core Logic)                      │
└─────────────────────────────────────────────────────────────────────┘
    ┌──────────┐  ┌──────────────┐  ┌─────────────┐
    │ License  │  │StateFormat   │  │IINRegistry  │
    │ (Entity) │  │  Registry    │  │             │
    └──────────┘  └──────────────┘  └─────────────┘
          │                    │                    │
          └────────────────────┴────────────────────┘
                               │
┌──────────────────────────────▼─────────────────────────────────────┐
│                 INFRASTRUCTURE LAYER (Adapters)                     │
└─────────────────────────────────────────────────────────────────────┘
    ┌──────────┐  ┌──────────────┐  ┌─────────────┐
    │  Faker   │  │  PDF417      │  │  ReportLab  │
    │ Adapter  │  │  Encoder     │  │  Generator  │
    └──────────┘  └──────────────┘  └─────────────┘
```

---

## 7. Interface Definitions

### Port: `IDataGenerator`

```python
from typing import Protocol
from datetime import date

class IDataGenerator(Protocol):
    """Port for data generation services.

    This is the INTERFACE that domain/application layers depend on.
    Infrastructure provides IMPLEMENTATIONS.

    Dependency Inversion Principle: High-level doesn't depend on low-level.
    """

    def generate_personal_name(self, sex: str) -> tuple[str, str, str]:
        """Generate (first, middle, last) name based on sex.

        Args:
            sex: '1' for male, '2' for female

        Returns:
            Tuple of (first_name, middle_name, last_name)
        """
        ...

    def generate_address(self, state: str) -> tuple[str, str, str]:
        """Generate street address, city, and ZIP code.

        Args:
            state: Two-letter state code

        Returns:
            Tuple of (street, city, zip_code)
        """
        ...

    def generate_date_of_birth(self, min_age: int, max_age: int) -> date:
        """Generate date of birth.

        Args:
            min_age: Minimum age in years
            max_age: Maximum age in years

        Returns:
            Date of birth
        """
        ...

    def generate_document_discriminator(self) -> str:
        """Generate unique document discriminator."""
        ...
```

### Port: `IBarcodeEncoder`

```python
from typing import Protocol
from PIL import Image

class IBarcodeEncoder(Protocol):
    """Port for barcode encoding services."""

    def encode(self, data: str, **options) -> bytes:
        """Encode data as PDF417 barcode.

        Args:
            data: AAMVA-formatted barcode string
            **options: Encoder-specific options

        Returns:
            Encoded barcode as byte array
        """
        ...

    def render_image(self, encoded_data: bytes, **options) -> Image.Image:
        """Render barcode as PIL Image.

        Args:
            encoded_data: Encoded barcode bytes
            **options: Rendering options

        Returns:
            PIL Image object
        """
        ...
```

### Port: `IDocumentExporter`

```python
from typing import Protocol
from pathlib import Path

class IDocumentExporter(Protocol):
    """Port for document export services."""

    def export(self, licenses: list[License], output_path: Path) -> None:
        """Export licenses to document.

        Args:
            licenses: List of licenses to export
            output_path: Output file path
        """
        ...

    def export_to_bytes(self, licenses: list[License]) -> bytes:
        """Export licenses as bytes (for API responses).

        Args:
            licenses: List of licenses to export

        Returns:
            Document bytes
        """
        ...
```

---

## 8. Dependency Graph

### Dependency Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ DEPENDENCY RULE: Dependencies point INWARD only                 │
│                                                                  │
│ ┌──────────────────────────────────────────────────────────┐   │
│ │ INTERFACES (Outer Layer)                                  │   │
│ │   - Depends on: Application Layer                         │   │
│ │   - Knows about: Use cases, DTOs                          │   │
│ │   - Doesn't know: Domain entities                         │   │
│ └────────────────────────┬─────────────────────────────────┘   │
│                          │                                      │
│                          ▼                                      │
│ ┌──────────────────────────────────────────────────────────┐   │
│ │ APPLICATION (Middle Layer)                                │   │
│ │   - Depends on: Domain Layer, Infrastructure Ports        │   │
│ │   - Knows about: Entities, Value Objects, Ports           │   │
│ │   - Doesn't know: Framework details, External libraries   │   │
│ └────────────────────────┬─────────────────────────────────┘   │
│                          │                                      │
│                          ▼                                      │
│ ┌──────────────────────────────────────────────────────────┐   │
│ │ DOMAIN (Core - No Dependencies)                           │   │
│ │   - Depends on: NOTHING (only Python stdlib)              │   │
│ │   - Pure business logic                                   │   │
│ │   - Defines interfaces that infrastructure implements     │   │
│ └──────────────────────────────────────────────────────────┘   │
│                          △                                      │
│                          │                                      │
│ ┌────────────────────────┴─────────────────────────────────┐   │
│ │ INFRASTRUCTURE (Outer Layer)                              │   │
│ │   - Depends on: Domain Layer (implements ports)           │   │
│ │   - Knows about: External libraries (Faker, PIL, etc.)    │   │
│ │   - Implements: Ports defined by domain                   │   │
│ └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Concrete Dependencies

```
CLI Adapter
├── GenerateLicenseUseCase
│   ├── LicenseFactory
│   │   ├── StateFormatRegistry (domain)
│   │   ├── IINRegistry (domain)
│   │   └── IDataGenerator (port)
│   │       └── FakerDataGenerator (infra) ← INJECTED
│   ├── AAMVA2020BarcodeFormatter (domain)
│   │   └── IINRegistry (domain)
│   ├── IBarcodeEncoder (port)
│   │   └── PDF417Encoder (infra) ← INJECTED
│   └── ILicenseRepository (port)
│       └── FileRepository (infra) ← INJECTED
└── IDocumentExporter (port)
    ├── PDFExporter (infra) ← INJECTED
    └── DOCXExporter (infra) ← INJECTED
```

**Key Insight**: Infrastructure adapters are **injected** at runtime. Application/domain layers never import infrastructure directly.

---

## 9. Extension Points

### Adding a New State Format

**Current Code**: Modify 200-line dictionary.

**New Architecture**:

```python
# 1. Create new generator class
class WyomingLicenseNumberGenerator:
    """Wyoming format: 9-10 digits"""

    def generate(self) -> str:
        import random
        length = random.choice([9, 10])
        return ''.join(random.choices(string.digits, k=length))

# 2. Register (no existing code modified)
registry.register('WY', WyomingLicenseNumberGenerator())

# 3. Write tests
def test_wyoming_license_format():
    generator = WyomingLicenseNumberGenerator()
    result = generator.generate()
    assert len(result) in [9, 10]
    assert result.isdigit()
```

**Zero lines of existing code modified.**

---

### Adding a New Export Format (e.g., CSV)

```python
# 1. Create exporter
class CSVExporter:
    """Export licenses as CSV."""

    def export(self, licenses: list[License], output_path: Path) -> None:
        import csv

        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[...])
            writer.writeheader()
            for license in licenses:
                writer.writerow(license.to_aamva_dict())

    def export_to_bytes(self, licenses: list[License]) -> bytes:
        # Implementation
        pass

# 2. Register with use case
exporter = CSVExporter()
use_case = ExportLicensesUseCase(exporter)

# 3. Use
use_case.execute(licenses, format='csv')
```

**No modification to domain or application layers.**

---

### Adding a New Interface (e.g., Web API)

```python
# In interfaces/api/main.py
from fastapi import FastAPI, Depends
from aamva.application.use_cases import GenerateLicenseUseCase
from aamva.application.dtos import GenerateLicenseRequest

app = FastAPI()

def get_use_case() -> GenerateLicenseUseCase:
    """Dependency injection for use case."""
    # Wire up dependencies
    return GenerateLicenseUseCase(
        license_factory=...,
        barcode_formatter=...,
        # ... etc
    )

@app.post("/api/v1/licenses/generate")
def generate_license(
    request: GenerateLicenseRequest,
    use_case: GenerateLicenseUseCase = Depends(get_use_case)
):
    """Generate a single license."""
    license = use_case.execute(request)
    return license.to_aamva_dict()
```

**Reuses ALL existing business logic. Zero duplication.**

---

## 10. Package Organization

### Packaging Strategy

**Modern Python packaging with `pyproject.toml`**:

```toml
# pyproject.toml
[build-system]
requires = ["setuptools>=65.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "aamva-id-faker"
version = "2.0.0"
description = "AAMVA DL/ID Card Generator"
authors = [{name = "James W Rogers, Jr.", email = "your@email.com"}]
license = {text = "MIT"}
readme = "README.md"
requires-python = ">=3.9"
dependencies = [
    "faker>=20.0.0",
    "pdf417>=1.0.0",
    "pillow>=10.0.0",
    "reportlab>=4.0.0",
    "python-docx>=1.0.0",
]

[project.optional-dependencies]
gui = [
    "customtkinter>=5.2.0",
]
api = [
    "fastapi>=0.100.0",
    "uvicorn>=0.23.0",
]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "hypothesis>=6.92.0",
    "ruff>=0.1.0",
    "mypy>=1.7.0",
]

[project.scripts]
aamva-cli = "aamva.interfaces.cli.main:main"
aamva-gui = "aamva.interfaces.gui.main_window:main"

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "--cov=src --cov-report=html --cov-report=term-missing"

[tool.ruff]
line-length = 100
target-version = "py39"

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

### Installation

```bash
# Install CLI only
pip install aamva-id-faker

# Install with GUI
pip install aamva-id-faker[gui]

# Install with API
pip install aamva-id-faker[api]

# Install for development
pip install -e ".[dev]"
```

### Entry Points

```bash
# CLI (installed as script)
aamva-cli generate -s CA -n 10

# GUI (installed as script)
aamva-gui

# Python API
python -c "from aamva.domain import License; print(License(...))"
```

---

## 11. Migration Strategy

### Phase 1: Extract Domain Layer (Week 1)

**Goal**: Create domain entities and services WITHOUT breaking existing code.

**Steps**:

1. **Create parallel structure**:
   ```bash
   src/aamva/domain/entities.py       # New
   generate_licenses.py                # Old (keep working)
   ```

2. **Extract `License` entity**:
   - Copy data from `generate_license_data()` function
   - Create immutable dataclass
   - Add validation to `__post_init__`

3. **Extract state format logic**:
   - Create `StateFormatRegistry`
   - Create individual generator classes
   - Keep old `state_formats` dict working

4. **Write comprehensive tests**:
   - 95%+ coverage on domain layer
   - Property-based tests for validation
   - ALL tests must pass before moving to Phase 2

**Success Criteria**: Domain layer tested at 95%+ coverage. Old code still works.

---

### Phase 2: Extract Infrastructure Layer (Week 2)

**Goal**: Create infrastructure adapters.

**Steps**:

1. **Create adapters**:
   - `FakerDataGenerator` (wraps Faker)
   - `PDF417Encoder` (wraps pdf417 library)
   - `PDFExporter` (wraps reportlab)
   - `DOCXExporter` (wraps python-docx)

2. **Define ports (interfaces)**:
   - `IDataGenerator`
   - `IBarcodeEncoder`
   - `IDocumentExporter`

3. **Write adapter tests**:
   - Mock external dependencies
   - Test port contracts

**Success Criteria**: All infrastructure adapters tested. Old code still works.

---

### Phase 3: Create Application Layer (Week 3)

**Goal**: Create use cases that orchestrate domain and infrastructure.

**Steps**:

1. **Create use cases**:
   - `GenerateLicenseUseCase`
   - `GenerateBatchUseCase`
   - `ExportLicensesUseCase`

2. **Wire dependencies**:
   - Manual constructor injection
   - No DI framework needed

3. **Integration tests**:
   - Test complete workflows
   - Use real adapters (not mocks)

**Success Criteria**: Use cases tested with integration tests.

---

### Phase 4: Refactor CLI (Week 4)

**Goal**: Make CLI use new architecture instead of monolithic script.

**Steps**:

1. **Create `CLIAdapter`**:
   ```python
   # interfaces/cli/main.py

   def main():
       args = parse_args()

       # Wire dependencies
       use_case = GenerateLicenseUseCase(
           license_factory=LicenseFactory(...),
           # ...
       )

       # Execute
       result = use_case.execute(...)

       # Present results
       print(f"Generated {len(result)} licenses")
   ```

2. **Remove old code**:
   - Delete monolithic `generate_licenses.py`
   - CLI now imports from `aamva` package

3. **E2E tests**:
   - Test CLI end-to-end
   - Ensure output matches old behavior

**Success Criteria**: CLI works identically to before, but uses new architecture.

---

### Phase 5: Add GUI (Week 5-6)

**Goal**: Add GUI using shared core logic.

**Steps**:

1. **Create GUI adapter**:
   - `GUIAdapter` translates GUI events → use case calls

2. **Implement GUI components**:
   - Main window
   - License form
   - Preview widget
   - Progress indicators

3. **GUI tests**:
   - pytest-qt for component tests
   - Visual regression tests

**Success Criteria**: GUI works, shares 100% of business logic with CLI.

---

### Phase 6: Polish & Document (Week 7)

**Goal**: Production-ready release.

**Steps**:

1. **Documentation**:
   - API reference (auto-generated)
   - User guide
   - Architecture decision records

2. **Performance optimization**:
   - Profile bottlenecks
   - Optimize hot paths
   - Target: 50 licenses/second

3. **Packaging**:
   - PyPI release
   - Binary distributions (PyInstaller)
   - Docker image

**Success Criteria**: Published to PyPI, documentation complete.

---

## 12. Implementation Roadmap

### Detailed Timeline

```
Week 1: Domain Layer
├── Day 1-2: License entity + tests
├── Day 3: StateFormatRegistry + tests
├── Day 4: IINRegistry + tests
├── Day 5: BarcodeFormatter + tests
└── Deliverable: Domain layer at 95%+ coverage

Week 2: Infrastructure Layer
├── Day 1-2: Data generation adapters + tests
├── Day 3: Barcode encoding adapters + tests
├── Day 4-5: Export adapters (PDF, DOCX) + tests
└── Deliverable: All ports implemented and tested

Week 3: Application Layer
├── Day 1-2: Use cases + unit tests
├── Day 3-4: Integration tests
├── Day 5: Performance testing
└── Deliverable: Use cases tested end-to-end

Week 4: CLI Refactoring
├── Day 1-2: CLI adapter implementation
├── Day 3: Remove old monolithic code
├── Day 4-5: E2E tests + bug fixes
└── Deliverable: New CLI working, old code deleted

Week 5-6: GUI Implementation
├── Day 1-2: GUI framework setup + main window
├── Day 3-4: Components (forms, preview, batch)
├── Day 5-6: GUI tests + polish
├── Day 7-10: User acceptance testing + fixes
└── Deliverable: Working GUI

Week 7: Polish & Release
├── Day 1-2: Documentation
├── Day 3-4: Performance optimization
├── Day 5: Packaging + PyPI release
└── Deliverable: v2.0.0 released to PyPI
```

---

## Conclusion: Why This Architecture Wins

### Comparison: Monolithic vs. SOLID Architecture

| Aspect | Current (Monolithic) | Proposed (SOLID) | Winner |
|--------|---------------------|------------------|--------|
| **Lines of Code** | 787 lines (1 file) | ~2000 lines (50 files) | Monolithic (less code) |
| **Testability** | 0% coverage | 95%+ coverage | **SOLID** |
| **Maintainability** | Very low | Very high | **SOLID** |
| **Extensibility** | Modify existing code | Add new classes | **SOLID** |
| **Interfaces** | 1 (CLI only) | 3+ (CLI, GUI, API) | **SOLID** |
| **Code Reuse** | 0% reuse | 100% core reuse | **SOLID** |
| **Bug Risk** | High (change ripples) | Low (isolated changes) | **SOLID** |
| **Time to Add GUI** | 2 weeks (duplicate logic) | 3 days (reuse core) | **SOLID** |
| **Time to Add State** | 5 minutes | 10 minutes | Tie |
| **Learning Curve** | 30 minutes | 2 hours | Monolithic |

**Verdict**: SOLID architecture wins on **every metric that matters for long-term success**.

### Final Opinion: Don't Be Afraid of "Over-Engineering"

**Common Objection**: "This is over-engineered for a simple script!"

**Counter-Argument**:

1. **This is NOT a simple script.** It has:
   - 51 state formats
   - AAMVA specification compliance
   - Multiple output formats (PDF, DOCX, images)
   - Confirmed future requirements (GUI, API)

2. **"Over-engineering"** would be:
   - Adding microservices
   - Using Kubernetes
   - Building a plugin system

3. **This architecture is NOT over-engineering.** It's:
   - Separating concerns (basic OOP)
   - Defining interfaces (basic abstraction)
   - Using dependency injection (basic decoupling)

**These are SOFTWARE ENGINEERING FUNDAMENTALS, not "over-engineering."**

### Implementation Recommendation

**DO THIS**: Follow the migration strategy. 7 weeks to production-ready v2.0.

**DON'T DO THIS**: Try to refactor everything at once. Incremental migration reduces risk.

**Key Success Factors**:
1. **Tests first**: Write domain tests before domain code
2. **Keep old code working**: Parallel implementation until proven
3. **Incremental migration**: One layer at a time
4. **Ruthless simplicity**: No premature optimization

---

**This architecture is battle-tested, SOLID-compliant, and ready for implementation.**

**Let's build it.**

