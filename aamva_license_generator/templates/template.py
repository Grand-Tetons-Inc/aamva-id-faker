"""
Template Data Model

Defines the core data structures for the template system, including:
- Template: Complete template definition with parameters and metadata
- TemplateParameter: Individual parameter with type, validation, and defaults
- TemplateVariable: Runtime variables that can be substituted in templates

Author: AAMVA License Generator Team
Version: 1.0.0
"""

import json
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from enum import Enum


class ParameterType(Enum):
    """Parameter data types supported in templates"""
    STRING = 'string'
    INTEGER = 'integer'
    FLOAT = 'float'
    BOOLEAN = 'boolean'
    DATE = 'date'
    ENUM = 'enum'
    LIST = 'list'
    DICT = 'dict'


class ValidationRule(Enum):
    """Validation rules for template parameters"""
    REQUIRED = 'required'
    MIN_VALUE = 'min_value'
    MAX_VALUE = 'max_value'
    MIN_LENGTH = 'min_length'
    MAX_LENGTH = 'max_length'
    PATTERN = 'pattern'
    ENUM_VALUES = 'enum_values'
    CUSTOM = 'custom'


@dataclass
class TemplateParameter:
    """
    Represents a single parameter in a template.

    Attributes:
        name: Parameter name (e.g., 'state', 'count', 'age_range')
        type: Data type of the parameter
        default: Default value if not specified
        description: Human-readable description
        required: Whether the parameter is required
        validation: Validation rules (min, max, pattern, etc.)
        examples: Example values for documentation
    """
    name: str
    type: ParameterType
    default: Any = None
    description: str = ''
    required: bool = False
    validation: Dict[str, Any] = field(default_factory=dict)
    examples: List[Any] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'name': self.name,
            'type': self.type.value,
            'default': self.default,
            'description': self.description,
            'required': self.required,
            'validation': self.validation,
            'examples': self.examples,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TemplateParameter':
        """Create from dictionary representation"""
        return cls(
            name=data['name'],
            type=ParameterType(data['type']),
            default=data.get('default'),
            description=data.get('description', ''),
            required=data.get('required', False),
            validation=data.get('validation', {}),
            examples=data.get('examples', []),
        )

    def validate(self, value: Any) -> tuple[bool, Optional[str]]:
        """
        Validate a value against this parameter's rules.

        Args:
            value: The value to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check required
        if self.required and value is None:
            return False, f"Parameter '{self.name}' is required"

        if value is None:
            return True, None

        # Type validation
        if self.type == ParameterType.INTEGER and not isinstance(value, int):
            return False, f"Expected integer, got {type(value).__name__}"
        elif self.type == ParameterType.FLOAT and not isinstance(value, (int, float)):
            return False, f"Expected number, got {type(value).__name__}"
        elif self.type == ParameterType.STRING and not isinstance(value, str):
            return False, f"Expected string, got {type(value).__name__}"
        elif self.type == ParameterType.BOOLEAN and not isinstance(value, bool):
            return False, f"Expected boolean, got {type(value).__name__}"
        elif self.type == ParameterType.LIST and not isinstance(value, list):
            return False, f"Expected list, got {type(value).__name__}"
        elif self.type == ParameterType.DICT and not isinstance(value, dict):
            return False, f"Expected dict, got {type(value).__name__}"

        # Validation rules
        if 'min_value' in self.validation and value < self.validation['min_value']:
            return False, f"Value must be >= {self.validation['min_value']}"

        if 'max_value' in self.validation and value > self.validation['max_value']:
            return False, f"Value must be <= {self.validation['max_value']}"

        if 'min_length' in self.validation and len(value) < self.validation['min_length']:
            return False, f"Length must be >= {self.validation['min_length']}"

        if 'max_length' in self.validation and len(value) > self.validation['max_length']:
            return False, f"Length must be <= {self.validation['max_length']}"

        if 'pattern' in self.validation:
            if not re.match(self.validation['pattern'], str(value)):
                return False, f"Value does not match pattern: {self.validation['pattern']}"

        if 'enum_values' in self.validation:
            if value not in self.validation['enum_values']:
                return False, f"Value must be one of: {', '.join(map(str, self.validation['enum_values']))}"

        return True, None


@dataclass
class TemplateVariable:
    """
    Represents a variable that can be substituted in templates.

    Variables use the syntax ${VARIABLE_NAME} and are replaced at runtime.

    Common variables:
        ${STATE}: State code (e.g., 'CA', 'NY')
        ${STATE_NAME}: Full state name (e.g., 'California')
        ${COUNT}: Number of licenses to generate
        ${AGE_RANGE}: Age range (e.g., '18-21', '21-65')
        ${OUTPUT_DIR}: Output directory path
        ${DATE}: Current date
        ${TIMESTAMP}: Current timestamp
    """
    name: str
    value: Any
    description: str = ''

    @property
    def placeholder(self) -> str:
        """Get the placeholder syntax for this variable"""
        return f"${{{self.name}}}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'name': self.name,
            'value': self.value,
            'description': self.description,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TemplateVariable':
        """Create from dictionary representation"""
        return cls(
            name=data['name'],
            value=data['value'],
            description=data.get('description', ''),
        )


@dataclass
class Template:
    """
    Complete template definition for license generation.

    A template encapsulates all parameters needed to generate a specific set
    of licenses, along with metadata, documentation, and inheritance relationships.

    Attributes:
        name: Unique template identifier
        version: Template version (semver)
        description: Detailed description of what this template does
        author: Template author/creator
        tags: Tags for categorization (e.g., ['age_verification', 'testing'])
        parameters: Dictionary of parameters and their values
        parameter_definitions: Definitions for each parameter
        parent_template: Name of parent template (for inheritance)
        variables: Runtime variables for substitution
        metadata: Additional metadata (created_at, updated_at, etc.)
        documentation: Extended documentation in markdown
    """
    name: str
    version: str = '1.0.0'
    description: str = ''
    author: str = 'AAMVA Team'
    tags: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    parameter_definitions: List[TemplateParameter] = field(default_factory=list)
    parent_template: Optional[str] = None
    variables: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    documentation: str = ''

    def __post_init__(self):
        """Initialize metadata if not provided"""
        if 'created_at' not in self.metadata:
            self.metadata['created_at'] = datetime.utcnow().isoformat()
        if 'updated_at' not in self.metadata:
            self.metadata['updated_at'] = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary representation"""
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'author': self.author,
            'tags': self.tags,
            'parameters': self.parameters,
            'parameter_definitions': [p.to_dict() for p in self.parameter_definitions],
            'parent_template': self.parent_template,
            'variables': self.variables,
            'metadata': self.metadata,
            'documentation': self.documentation,
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert template to JSON string"""
        return json.dumps(self.to_dict(), indent=indent, default=str)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Template':
        """Create template from dictionary representation"""
        param_defs = [
            TemplateParameter.from_dict(p)
            for p in data.get('parameter_definitions', [])
        ]

        return cls(
            name=data['name'],
            version=data.get('version', '1.0.0'),
            description=data.get('description', ''),
            author=data.get('author', 'AAMVA Team'),
            tags=data.get('tags', []),
            parameters=data.get('parameters', {}),
            parameter_definitions=param_defs,
            parent_template=data.get('parent_template'),
            variables=data.get('variables', {}),
            metadata=data.get('metadata', {}),
            documentation=data.get('documentation', ''),
        )

    @classmethod
    def from_json(cls, json_str: str) -> 'Template':
        """Create template from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def validate_parameters(self) -> tuple[bool, List[str]]:
        """
        Validate all parameters against their definitions.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Create a lookup for parameter definitions
        param_def_lookup = {p.name: p for p in self.parameter_definitions}

        # Validate each parameter
        for param_name, param_value in self.parameters.items():
            if param_name in param_def_lookup:
                param_def = param_def_lookup[param_name]
                is_valid, error_msg = param_def.validate(param_value)
                if not is_valid:
                    errors.append(f"{param_name}: {error_msg}")

        # Check for missing required parameters
        for param_def in self.parameter_definitions:
            if param_def.required and param_def.name not in self.parameters:
                errors.append(f"{param_def.name}: Required parameter missing")

        return len(errors) == 0, errors

    def substitute_variables(self, text: str, additional_vars: Optional[Dict[str, Any]] = None) -> str:
        """
        Substitute variables in text.

        Args:
            text: Text containing variable placeholders
            additional_vars: Additional variables to use for substitution

        Returns:
            Text with variables substituted
        """
        # Combine template variables with additional variables
        all_vars = {**self.variables, **(additional_vars or {})}

        # Find and replace all variables
        result = text
        for var_name, var_value in all_vars.items():
            placeholder = f"${{{var_name}}}"
            result = result.replace(placeholder, str(var_value))

        return result

    def merge_with_parent(self, parent: 'Template') -> 'Template':
        """
        Merge this template with its parent template.

        Child template parameters override parent parameters.

        Args:
            parent: Parent template to merge with

        Returns:
            New template with merged configuration
        """
        # Merge parameters (child overrides parent)
        merged_params = {**parent.parameters, **self.parameters}

        # Merge parameter definitions
        parent_defs = {p.name: p for p in parent.parameter_definitions}
        child_defs = {p.name: p for p in self.parameter_definitions}
        merged_defs = {**parent_defs, **child_defs}

        # Merge tags
        merged_tags = list(set(parent.tags + self.tags))

        # Merge variables
        merged_vars = {**parent.variables, **self.variables}

        # Create merged template
        return Template(
            name=self.name,
            version=self.version,
            description=self.description or parent.description,
            author=self.author,
            tags=merged_tags,
            parameters=merged_params,
            parameter_definitions=list(merged_defs.values()),
            parent_template=None,  # Clear parent reference after merge
            variables=merged_vars,
            metadata=self.metadata,
            documentation=self.documentation or parent.documentation,
        )

    def clone(self, new_name: Optional[str] = None) -> 'Template':
        """
        Create a deep copy of this template.

        Args:
            new_name: Optional new name for the cloned template

        Returns:
            Cloned template
        """
        cloned_data = self.to_dict()
        if new_name:
            cloned_data['name'] = new_name
        cloned_data['metadata']['created_at'] = datetime.utcnow().isoformat()
        cloned_data['metadata']['updated_at'] = datetime.utcnow().isoformat()
        cloned_data['metadata']['cloned_from'] = self.name

        return Template.from_dict(cloned_data)

    def get_summary(self) -> str:
        """Get a human-readable summary of this template"""
        lines = [
            f"Template: {self.name} (v{self.version})",
            f"Author: {self.author}",
            f"Description: {self.description}",
            f"Tags: {', '.join(self.tags) if self.tags else 'None'}",
            f"Parameters: {len(self.parameters)}",
        ]

        if self.parent_template:
            lines.append(f"Inherits from: {self.parent_template}")

        if self.parameters:
            lines.append("\nParameters:")
            for name, value in self.parameters.items():
                lines.append(f"  - {name}: {value}")

        return '\n'.join(lines)

    def __str__(self) -> str:
        """String representation"""
        return f"Template(name='{self.name}', version='{self.version}', params={len(self.parameters)})"

    def __repr__(self) -> str:
        """Detailed representation"""
        return self.get_summary()
