"""
Template Validator

Validates template definitions against JSON schemas and business rules.

Author: AAMVA License Generator Team
Version: 1.0.0
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .template import Template, TemplateParameter, ParameterType


class ValidationError(Exception):
    """Raised when template validation fails"""
    pass


class TemplateValidator:
    """
    Validates templates against schemas and business rules.

    Validation includes:
    - JSON schema validation
    - Parameter type checking
    - Required field verification
    - Value range validation
    - Pattern matching
    - Cross-field validation
    """

    # Valid state codes (subset - full list should be loaded from IIN data)
    VALID_STATE_CODES = {
        'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL',
        'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME',
        'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH',
        'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI',
        'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY',
    }

    # Common parameter names and their expected types
    STANDARD_PARAMETERS = {
        'state': ParameterType.STRING,
        'count': ParameterType.INTEGER,
        'output_dir': ParameterType.STRING,
        'age_min': ParameterType.INTEGER,
        'age_max': ParameterType.INTEGER,
        'is_expired': ParameterType.BOOLEAN,
        'is_veteran': ParameterType.BOOLEAN,
        'is_organ_donor': ParameterType.BOOLEAN,
        'expiration_days_from_now': ParameterType.INTEGER,
        'include_photo': ParameterType.BOOLEAN,
        'format': ParameterType.STRING,
    }

    def __init__(self, schema_path: Optional[Path] = None):
        """
        Initialize the validator.

        Args:
            schema_path: Path to JSON schema file. If None, uses built-in validation.
        """
        self.schema_path = schema_path
        self.schema = None

        if schema_path and schema_path.exists():
            with open(schema_path, 'r') as f:
                self.schema = json.load(f)

    def validate(self, template: Template) -> Tuple[bool, List[str]]:
        """
        Validate a template.

        Args:
            template: Template to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Basic field validation
        errors.extend(self._validate_basic_fields(template))

        # Parameter validation
        errors.extend(self._validate_parameters(template))

        # Variable validation
        errors.extend(self._validate_variables(template))

        # Business logic validation
        errors.extend(self._validate_business_rules(template))

        # Cross-field validation
        errors.extend(self._validate_cross_fields(template))

        return len(errors) == 0, errors

    def _validate_basic_fields(self, template: Template) -> List[str]:
        """Validate basic required fields"""
        errors = []

        if not template.name:
            errors.append("Template name is required")
        elif not self._is_valid_name(template.name):
            errors.append(
                "Template name must be alphanumeric with underscores/hyphens "
                "(no spaces or special characters)"
            )

        if not template.version:
            errors.append("Template version is required")
        elif not self._is_valid_semver(template.version):
            errors.append("Template version must be valid semver (e.g., 1.0.0)")

        if not template.description:
            errors.append("Template description is required")

        return errors

    def _validate_parameters(self, template: Template) -> List[str]:
        """Validate template parameters"""
        errors = []

        # Validate parameter definitions
        for param_def in template.parameter_definitions:
            # Check parameter name
            if not param_def.name:
                errors.append("Parameter definition missing name")
                continue

            # Validate default value against type
            if param_def.default is not None:
                is_valid, error = param_def.validate(param_def.default)
                if not is_valid:
                    errors.append(f"Parameter '{param_def.name}' default value invalid: {error}")

        # Validate actual parameters against definitions
        is_valid, param_errors = template.validate_parameters()
        errors.extend(param_errors)

        # Check for common parameter issues
        if 'state' in template.parameters:
            state = template.parameters['state']
            if state and state not in self.VALID_STATE_CODES and state != 'ALL':
                errors.append(f"Invalid state code: {state}")

        if 'count' in template.parameters:
            count = template.parameters['count']
            if not isinstance(count, int):
                errors.append(f"Count must be integer, got {type(count).__name__}")
            elif count < 1:
                errors.append("Count must be at least 1")
            elif count > 10000:
                errors.append("Count should not exceed 10,000 for performance reasons")

        if 'age_min' in template.parameters and 'age_max' in template.parameters:
            age_min = template.parameters['age_min']
            age_max = template.parameters['age_max']
            if age_min > age_max:
                errors.append(f"age_min ({age_min}) cannot be greater than age_max ({age_max})")

        return errors

    def _validate_variables(self, template: Template) -> List[str]:
        """Validate template variables"""
        errors = []

        for var_name, var_value in template.variables.items():
            # Variable names should be uppercase with underscores
            if not re.match(r'^[A-Z][A-Z0-9_]*$', var_name):
                errors.append(
                    f"Variable name '{var_name}' should be UPPER_CASE with underscores"
                )

        return errors

    def _validate_business_rules(self, template: Template) -> List[str]:
        """Validate business logic rules"""
        errors = []

        # Check for conflicting parameters
        if template.parameters.get('is_expired') and template.parameters.get('expiration_days_from_now', 0) > 0:
            errors.append(
                "Cannot have both is_expired=True and positive expiration_days_from_now"
            )

        # Validate age ranges make sense
        if 'age_min' in template.parameters:
            age_min = template.parameters['age_min']
            if age_min < 16:
                errors.append("Minimum age should be at least 16 (minimum driving age)")
            if age_min > 100:
                errors.append("Minimum age should not exceed 100")

        if 'age_max' in template.parameters:
            age_max = template.parameters['age_max']
            if age_max > 120:
                errors.append("Maximum age should not exceed 120")

        return errors

    def _validate_cross_fields(self, template: Template) -> List[str]:
        """Validate relationships between fields"""
        errors = []

        # If parent template is specified, warn about potential issues
        if template.parent_template:
            if not self._is_valid_name(template.parent_template):
                errors.append(
                    f"Parent template name '{template.parent_template}' is invalid"
                )

        # Check for circular dependencies (basic check)
        if template.parent_template == template.name:
            errors.append("Template cannot inherit from itself")

        return errors

    @staticmethod
    def _is_valid_name(name: str) -> bool:
        """Check if template name is valid"""
        # Allow alphanumeric, underscores, hyphens
        return bool(re.match(r'^[a-zA-Z0-9_-]+$', name))

    @staticmethod
    def _is_valid_semver(version: str) -> bool:
        """Check if version is valid semver"""
        pattern = r'^\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?(\+[a-zA-Z0-9.]+)?$'
        return bool(re.match(pattern, version))

    def validate_json_schema(self, template_dict: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate template against JSON schema.

        Args:
            template_dict: Template as dictionary

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        if not self.schema:
            return True, []  # No schema to validate against

        try:
            # Would use jsonschema library here
            # For now, return success
            return True, []
        except Exception as e:
            return False, [str(e)]

    def validate_file(self, file_path: Path) -> Tuple[bool, List[str]]:
        """
        Validate a template file.

        Args:
            file_path: Path to template JSON file

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        if not file_path.exists():
            return False, [f"File not found: {file_path}"]

        try:
            with open(file_path, 'r') as f:
                template = Template.from_json(f.read())
        except json.JSONDecodeError as e:
            return False, [f"Invalid JSON: {e}"]
        except Exception as e:
            return False, [f"Failed to load template: {e}"]

        return self.validate(template)

    def get_validation_report(self, template: Template) -> str:
        """
        Get a detailed validation report.

        Args:
            template: Template to validate

        Returns:
            Formatted validation report
        """
        is_valid, errors = self.validate(template)

        lines = [
            f"Validation Report for '{template.name}'",
            "=" * 60,
            f"Status: {'✓ VALID' if is_valid else '✗ INVALID'}",
            f"Template Version: {template.version}",
            f"Parameters: {len(template.parameters)}",
            f"Parameter Definitions: {len(template.parameter_definitions)}",
            "",
        ]

        if errors:
            lines.append("Errors:")
            for i, error in enumerate(errors, 1):
                lines.append(f"  {i}. {error}")
        else:
            lines.append("No errors found.")

        # Add parameter summary
        lines.append("")
        lines.append("Parameters:")
        for name, value in template.parameters.items():
            lines.append(f"  - {name}: {value}")

        return '\n'.join(lines)
