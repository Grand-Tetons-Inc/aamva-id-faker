"""
AAMVA License Generator - Template System

This module provides a comprehensive template and preset system for saving and loading
license generation configurations. It enables users to create, manage, and share
templates for common testing scenarios.

Key Features:
- Template data model with full parameter support
- JSON-based storage with schema validation
- Variable substitution (${STATE}, ${AGE_RANGE}, etc.)
- Template inheritance and composition
- 10+ pre-built templates for common scenarios
- Export/import functionality for template sharing

Usage:
    from aamva_license_generator.templates import TemplateManager, Template

    # Load and use a built-in template
    manager = TemplateManager()
    template = manager.load_builtin('age_verification_ca')

    # Create a custom template
    custom = Template(
        name='my_test_scenario',
        description='Custom test scenario',
        parameters={'state': 'CA', 'count': 10}
    )
    manager.save(custom)
"""

from .template import Template, TemplateParameter, TemplateVariable
from .template_manager import TemplateManager
from .template_validator import TemplateValidator, ValidationError
from .builtin_templates import get_builtin_templates, get_builtin_template

__all__ = [
    'Template',
    'TemplateParameter',
    'TemplateVariable',
    'TemplateManager',
    'TemplateValidator',
    'ValidationError',
    'get_builtin_templates',
    'get_builtin_template',
]

__version__ = '1.0.0'
