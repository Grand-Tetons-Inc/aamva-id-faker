"""
Built-in Templates

Provides pre-configured templates for common testing scenarios.

This module contains 10+ production-ready templates for:
- Age verification testing
- Expired license testing
- State coverage testing
- Veteran and organ donor scenarios
- Edge case testing
- Training and demo scenarios

Author: AAMVA License Generator Team
Version: 1.0.0
"""

from datetime import datetime, timedelta
from typing import Dict, List

from .template import Template, TemplateParameter, ParameterType


def create_age_verification_template() -> Template:
    """
    Age Verification Testing Template

    Generates licenses for testing age verification logic:
    - Under 21 years old (18-20.99)
    - Exactly 21 years old
    - Over 21 years old (21-30)

    Use case: Testing alcohol purchase, gambling, age-restricted content
    """
    return Template(
        name='age_verification',
        version='1.0.0',
        description='Generate licenses for age verification testing (under 21, exactly 21, over 21)',
        author='AAMVA Team',
        tags=['testing', 'age_verification', 'compliance'],
        parameters={
            'state': 'CA',
            'count': 6,
            'age_ranges': [
                {'min': 18, 'max': 20.99, 'count': 2},
                {'min': 21, 'max': 21, 'count': 2},
                {'min': 21.01, 'max': 30, 'count': 2},
            ],
            'output_dir': 'output/age_verification',
        },
        parameter_definitions=[
            TemplateParameter(
                name='state',
                type=ParameterType.STRING,
                default='CA',
                description='State code for licenses',
                required=True,
                validation={'pattern': r'^[A-Z]{2}$'},
                examples=['CA', 'NY', 'TX'],
            ),
            TemplateParameter(
                name='count',
                type=ParameterType.INTEGER,
                default=6,
                description='Total number of licenses (2 per age group)',
                required=True,
                validation={'min_value': 3, 'max_value': 100},
            ),
        ],
        variables={
            'STATE': 'CA',
            'SCENARIO': 'Age Verification',
        },
        documentation="""
# Age Verification Template

This template generates three groups of licenses for comprehensive age verification testing:

1. **Under 21**: People aged 18-20.99 years (should fail 21+ checks)
2. **Exactly 21**: People exactly 21 years old (edge case)
3. **Over 21**: People aged 21-30 years (should pass 21+ checks)

## Use Cases
- Testing bar/nightclub age verification systems
- Online gambling age gates
- Alcohol purchase validation
- Age-restricted content access

## Expected Results
- Group 1 (Under 21): Should be rejected for 21+ activities
- Group 2 (Exactly 21): Edge case - should be accepted
- Group 3 (Over 21): Should be accepted for all age restrictions

## Example Usage
```python
from aamva_license_generator.templates import TemplateManager

manager = TemplateManager()
template = manager.load_builtin('age_verification')

# Customize for your state
template.parameters['state'] = 'NY'
template.parameters['count'] = 12  # 4 per age group

# Generate licenses
# (implementation depends on your generation API)
```
        """,
    )


def create_expired_licenses_template() -> Template:
    """
    Expired Licenses Template

    Generates licenses with various expiration states:
    - Already expired (30-365 days ago)
    - Expiring soon (within 30 days)
    - Recently issued (valid for years)

    Use case: Testing expiration validation logic
    """
    return Template(
        name='expired_licenses',
        version='1.0.0',
        description='Generate expired, expiring soon, and valid licenses for testing expiration logic',
        author='AAMVA Team',
        tags=['testing', 'expiration', 'validation'],
        parameters={
            'state': 'CA',
            'count': 9,
            'expiration_scenarios': [
                {'type': 'expired', 'days_ago': -180, 'count': 3},
                {'type': 'expiring_soon', 'days_from_now': 15, 'count': 3},
                {'type': 'valid', 'days_from_now': 365, 'count': 3},
            ],
            'output_dir': 'output/expiration_testing',
        },
        parameter_definitions=[
            TemplateParameter(
                name='state',
                type=ParameterType.STRING,
                default='CA',
                description='State code for licenses',
                required=True,
            ),
            TemplateParameter(
                name='count',
                type=ParameterType.INTEGER,
                default=9,
                description='Total licenses to generate',
                required=True,
            ),
        ],
        variables={
            'STATE': 'CA',
            'SCENARIO': 'Expiration Testing',
        },
        documentation="""
# Expired Licenses Template

Tests expiration validation with three scenarios:

1. **Expired**: Licenses expired 30-365 days ago
2. **Expiring Soon**: Licenses expiring within 30 days
3. **Valid**: Recently issued licenses (valid for 1+ years)

## Test Cases
- Verify expired licenses are rejected
- Test "expiring soon" warning messages
- Confirm valid licenses are accepted
        """,
    )


def create_all_states_template() -> Template:
    """
    All States Coverage Template

    Generates one license from each of the 50 US states + DC.

    Use case: Testing state format coverage, parser compatibility
    """
    return Template(
        name='all_states',
        version='1.0.0',
        description='Generate one license from each US state for comprehensive state coverage testing',
        author='AAMVA Team',
        tags=['testing', 'coverage', 'states'],
        parameters={
            'states': 'ALL',
            'count': 51,  # 50 states + DC
            'output_dir': 'output/all_states',
        },
        parameter_definitions=[
            TemplateParameter(
                name='states',
                type=ParameterType.STRING,
                default='ALL',
                description='Generate for all states',
                required=True,
            ),
        ],
        variables={
            'COUNT': '51',
            'SCENARIO': 'All States Coverage',
        },
        documentation="""
# All States Coverage Template

Generates exactly one license from each US jurisdiction (50 states + DC).

## Use Cases
- Parser testing across all state formats
- Comprehensive format coverage
- State-specific validation testing
- Documentation and training materials

## Output
51 licenses total, one per jurisdiction in alphabetical order.
        """,
    )


def create_real_id_mix_template() -> Template:
    """
    REAL ID Mix Template

    Generates a mix of REAL ID compliant and non-compliant licenses.

    Use case: Testing REAL ID compliance checking
    """
    return Template(
        name='real_id_mix',
        version='1.0.0',
        description='Generate mix of REAL ID compliant and non-compliant licenses',
        author='AAMVA Team',
        tags=['testing', 'real_id', 'compliance'],
        parameters={
            'state': 'CA',
            'count': 10,
            'real_id_count': 5,
            'non_real_id_count': 5,
            'output_dir': 'output/real_id_testing',
        },
        parameter_definitions=[
            TemplateParameter(
                name='state',
                type=ParameterType.STRING,
                default='CA',
                description='State code',
                required=True,
            ),
            TemplateParameter(
                name='real_id_count',
                type=ParameterType.INTEGER,
                default=5,
                description='Number of REAL ID compliant licenses',
            ),
            TemplateParameter(
                name='non_real_id_count',
                type=ParameterType.INTEGER,
                default=5,
                description='Number of non-REAL ID licenses',
            ),
        ],
        variables={
            'STATE': 'CA',
        },
        documentation="""
# REAL ID Mix Template

Tests REAL ID compliance with:
- 50% REAL ID compliant licenses (star indicator)
- 50% non-REAL ID licenses (no star)

Use for testing REAL ID verification logic.
        """,
    )


def create_veteran_licenses_template() -> Template:
    """
    Veteran Licenses Template

    Generates licenses with veteran designation.

    Use case: Testing veteran status identification
    """
    return Template(
        name='veteran_licenses',
        version='1.0.0',
        description='Generate licenses with veteran designation for veteran status testing',
        author='AAMVA Team',
        tags=['testing', 'veteran', 'special_cases'],
        parameters={
            'state': 'TX',
            'count': 10,
            'veteran': True,
            'output_dir': 'output/veteran_testing',
        },
        parameter_definitions=[
            TemplateParameter(
                name='state',
                type=ParameterType.STRING,
                default='TX',
                description='State code (TX has prominent veteran indicator)',
                required=True,
            ),
            TemplateParameter(
                name='veteran',
                type=ParameterType.BOOLEAN,
                default=True,
                description='Mark as veteran',
                required=True,
            ),
        ],
        variables={
            'STATE': 'TX',
        },
        documentation="""
# Veteran Licenses Template

Generates licenses with veteran designation.

Texas is recommended as it has a prominent veteran flag indicator.

## Use Cases
- Testing veteran status recognition
- Veteran discount validation
- Training on veteran ID indicators
        """,
    )


def create_organ_donor_template() -> Template:
    """
    Organ Donor Template

    Generates licenses with organ donor designation.

    Use case: Testing organ donor status identification
    """
    return Template(
        name='organ_donor',
        version='1.0.0',
        description='Generate licenses with organ donor designation',
        author='AAMVA Team',
        tags=['testing', 'organ_donor', 'special_cases'],
        parameters={
            'state': 'CA',
            'count': 10,
            'organ_donor': True,
            'output_dir': 'output/organ_donor_testing',
        },
        parameter_definitions=[
            TemplateParameter(
                name='organ_donor',
                type=ParameterType.BOOLEAN,
                default=True,
                description='Mark as organ donor',
                required=True,
            ),
        ],
        variables={
            'STATE': 'CA',
        },
        documentation="""
# Organ Donor Template

Generates licenses with organ donor designation (heart indicator).

Test organ donor status recognition in ID scanning systems.
        """,
    )


def create_edge_cases_template() -> Template:
    """
    Edge Cases Template

    Generates licenses with edge case data:
    - Very long names (30+ characters)
    - Special characters in names (O'Brien, José)
    - Leap year birthdates (Feb 29)
    - Maximum/minimum ages
    - Unusual addresses

    Use case: Testing edge case handling, truncation, special character support
    """
    return Template(
        name='edge_cases',
        version='1.0.0',
        description='Generate licenses with edge case data for robust testing',
        author='AAMVA Team',
        tags=['testing', 'edge_cases', 'qa'],
        parameters={
            'state': 'CA',
            'count': 10,
            'test_cases': [
                {'type': 'long_name', 'count': 2},
                {'type': 'special_chars', 'count': 2},
                {'type': 'leap_year', 'count': 2},
                {'type': 'max_age', 'count': 2},
                {'type': 'min_age', 'count': 2},
            ],
            'output_dir': 'output/edge_cases',
        },
        parameter_definitions=[
            TemplateParameter(
                name='state',
                type=ParameterType.STRING,
                default='CA',
                description='State code',
                required=True,
            ),
        ],
        variables={
            'SCENARIO': 'Edge Cases',
        },
        documentation="""
# Edge Cases Template

Tests unusual but valid data scenarios:

1. **Long Names**: 30+ character names (truncation testing)
2. **Special Characters**: Names with apostrophes, hyphens, accents
3. **Leap Year**: Feb 29 birthdates
4. **Maximum Age**: 100-year-old license holders
5. **Minimum Age**: 16-year-old (minimum driving age)

## Examples
- Name: "Wolfeschlegelsteinhausenbergerdorff"
- Name: "O'Brien-Smith"
- Name: "José García"
- DOB: 2000-02-29 (leap year)
        """,
    )


def create_training_scenario_template() -> Template:
    """
    Training Scenario Template

    Pre-configured for security trainer use cases (Security Sarah persona).

    Generates easy-to-present licenses for training sessions.
    """
    return Template(
        name='training_scenario',
        version='1.0.0',
        description='Security training scenario with age verification and expiration examples',
        author='AAMVA Team',
        tags=['training', 'education', 'demo'],
        parameters={
            'state': 'NV',  # Nevada (casino security training)
            'count': 8,
            'scenarios': [
                {'type': 'under_21', 'count': 2},
                {'type': 'valid_21_plus', 'count': 2},
                {'type': 'expired', 'count': 2},
                {'type': 'veteran', 'count': 1},
                {'type': 'organ_donor', 'count': 1},
            ],
            'output_dir': 'output/training',
            'include_annotations': True,
        },
        parameter_definitions=[
            TemplateParameter(
                name='state',
                type=ParameterType.STRING,
                default='NV',
                description='State for training (Nevada recommended for casino training)',
                required=True,
            ),
        ],
        variables={
            'STATE': 'NV',
            'STATE_NAME': 'Nevada',
            'TRAINING_TYPE': 'Security Training',
        },
        documentation="""
# Training Scenario Template

Designed for security trainers conducting ID verification training.

## Scenarios Covered
1. Under 21 (should fail alcohol/gambling checks)
2. Valid 21+ (should pass checks)
3. Expired licenses (should be rejected)
4. Veteran indicator recognition
5. Organ donor indicator recognition

## Recommended Use
- New hire orientation
- Quarterly refresher training
- Casino security training
- Bar/nightclub staff training

## Output
8 licenses with diverse, easy-to-explain scenarios.
        """,
    )


def create_demo_scenario_template() -> Template:
    """
    Demo Scenario Template

    Pre-configured for sales and product demonstrations.
    Clean, professional-looking licenses for demos.
    """
    return Template(
        name='demo_scenario',
        version='1.0.0',
        description='Professional demo licenses for sales presentations',
        author='AAMVA Team',
        tags=['demo', 'sales', 'presentation'],
        parameters={
            'state': 'CA',
            'count': 5,
            'age_range': (25, 40),  # Professional age range
            'clean_data': True,  # No edge cases
            'output_dir': 'output/demo',
        },
        parameter_definitions=[
            TemplateParameter(
                name='state',
                type=ParameterType.STRING,
                default='CA',
                description='State code (CA recommended for demos)',
                required=True,
            ),
            TemplateParameter(
                name='clean_data',
                type=ParameterType.BOOLEAN,
                default=True,
                description='Use clean, professional data (no edge cases)',
            ),
        ],
        variables={
            'STATE': 'CA',
            'PURPOSE': 'Demo',
        },
        documentation="""
# Demo Scenario Template

Professional licenses for product demonstrations and sales presentations.

## Features
- Clean, realistic data
- Professional age range (25-40)
- No edge cases or unusual data
- Easy to scan and demonstrate

## Use Cases
- Sales presentations
- Product demos
- Trade show demonstrations
- Customer onboarding

## Notes
Generates visually appealing, easy-to-scan licenses that work reliably
in live demonstrations.
        """,
    )


def create_quick_test_template() -> Template:
    """
    Quick Test Template

    Fast, small batch for quick testing during development.
    """
    return Template(
        name='quick_test',
        version='1.0.0',
        description='Quick test template for rapid iteration during development',
        author='AAMVA Team',
        tags=['testing', 'development', 'quick'],
        parameters={
            'state': 'CA',
            'count': 3,
            'output_dir': 'output/quick_test',
        },
        parameter_definitions=[
            TemplateParameter(
                name='state',
                type=ParameterType.STRING,
                default='CA',
                description='State code',
                required=True,
            ),
            TemplateParameter(
                name='count',
                type=ParameterType.INTEGER,
                default=3,
                description='Small count for quick testing',
                validation={'min_value': 1, 'max_value': 10},
            ),
        ],
        variables={
            'STATE': 'CA',
        },
        documentation="""
# Quick Test Template

Minimal template for rapid testing during development.

Generates just 3 licenses with standard settings for quick iteration.
        """,
    )


def create_performance_test_template() -> Template:
    """
    Performance Test Template

    Large batch for performance and stress testing.
    """
    return Template(
        name='performance_test',
        version='1.0.0',
        description='Large batch template for performance and stress testing',
        author='AAMVA Team',
        tags=['testing', 'performance', 'stress'],
        parameters={
            'state': 'CA',
            'count': 1000,
            'parallel': True,
            'output_dir': 'output/performance_test',
        },
        parameter_definitions=[
            TemplateParameter(
                name='count',
                type=ParameterType.INTEGER,
                default=1000,
                description='Large count for performance testing',
                validation={'min_value': 100, 'max_value': 10000},
            ),
            TemplateParameter(
                name='parallel',
                type=ParameterType.BOOLEAN,
                default=True,
                description='Enable parallel generation',
            ),
        ],
        variables={
            'COUNT': '1000',
        },
        documentation="""
# Performance Test Template

Generates 1000 licenses for performance and stress testing.

## Use Cases
- Performance benchmarking
- Stress testing
- Batch processing validation
- Memory usage testing

## Recommendations
- Enable parallel generation for faster execution
- Monitor memory usage
- Test with different batch sizes
        """,
    )


# Built-in template registry
BUILTIN_TEMPLATES = {
    'age_verification': create_age_verification_template,
    'expired_licenses': create_expired_licenses_template,
    'all_states': create_all_states_template,
    'real_id_mix': create_real_id_mix_template,
    'veteran_licenses': create_veteran_licenses_template,
    'organ_donor': create_organ_donor_template,
    'edge_cases': create_edge_cases_template,
    'training_scenario': create_training_scenario_template,
    'demo_scenario': create_demo_scenario_template,
    'quick_test': create_quick_test_template,
    'performance_test': create_performance_test_template,
}


def get_builtin_templates() -> Dict[str, Template]:
    """
    Get all built-in templates.

    Returns:
        Dictionary mapping template names to Template instances
    """
    return {name: factory() for name, factory in BUILTIN_TEMPLATES.items()}


def get_builtin_template(name: str) -> Template:
    """
    Get a specific built-in template by name.

    Args:
        name: Template name

    Returns:
        Template instance

    Raises:
        KeyError: If template not found
    """
    if name not in BUILTIN_TEMPLATES:
        available = ', '.join(BUILTIN_TEMPLATES.keys())
        raise KeyError(
            f"Built-in template '{name}' not found. "
            f"Available templates: {available}"
        )

    return BUILTIN_TEMPLATES[name]()


def list_builtin_template_names() -> List[str]:
    """Get list of all built-in template names"""
    return sorted(BUILTIN_TEMPLATES.keys())


def get_builtin_template_summary() -> str:
    """Get a summary of all built-in templates"""
    lines = [
        "Built-in Templates",
        "=" * 60,
        "",
    ]

    for name in sorted(BUILTIN_TEMPLATES.keys()):
        template = get_builtin_template(name)
        lines.append(f"**{name}** (v{template.version})")
        lines.append(f"  {template.description}")
        lines.append(f"  Tags: {', '.join(template.tags)}")
        lines.append("")

    return '\n'.join(lines)
