"""
AAMVA License Generator - Validation Package

Comprehensive validation engine with real-time validation capabilities,
field-level validators, cross-field validators, state-specific rules,
and AAMVA compliance checking.

Features:
- Pydantic schema validation
- Validation levels (error, warning, info)
- Fuzzy matching for state names
- Extensible rule system
- Fast performance for real-time validation
"""

from .schemas import (
    LicenseData,
    ValidationResult,
    ValidationLevel,
    FieldValidationResult,
    BatchValidationResult,
)
from .validators import (
    LicenseValidator,
    StateCodeValidator,
    DateValidator,
    LicenseNumberValidator,
    AddressValidator,
    PersonalDataValidator,
)
from .rules import (
    ValidationRule,
    ValidationRuleSet,
    create_default_rules,
)
from .state_rules import (
    StateRules,
    get_state_rules,
    validate_state_license_format,
)
from .aamva_compliance import (
    AAMVACompliance,
    check_aamva_compliance,
)

__version__ = "1.0.0"
__all__ = [
    # Schemas
    "LicenseData",
    "ValidationResult",
    "ValidationLevel",
    "FieldValidationResult",
    "BatchValidationResult",
    # Validators
    "LicenseValidator",
    "StateCodeValidator",
    "DateValidator",
    "LicenseNumberValidator",
    "AddressValidator",
    "PersonalDataValidator",
    # Rules
    "ValidationRule",
    "ValidationRuleSet",
    "create_default_rules",
    # State Rules
    "StateRules",
    "get_state_rules",
    "validate_state_license_format",
    # AAMVA Compliance
    "AAMVACompliance",
    "check_aamva_compliance",
]
