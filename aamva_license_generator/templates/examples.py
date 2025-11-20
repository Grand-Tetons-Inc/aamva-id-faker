"""
Template System Examples

This module demonstrates various use cases and patterns for the template system.

Run this file directly to see examples:
    python -m aamva_license_generator.templates.examples

Author: AAMVA License Generator Team
Version: 1.0.0
"""

from pathlib import Path
from datetime import datetime

from .template import Template, TemplateParameter, ParameterType
from .template_manager import TemplateManager
from .template_validator import TemplateValidator
from .builtin_templates import list_builtin_template_names, get_builtin_template_summary


def example_1_list_builtin_templates():
    """Example 1: List all built-in templates"""
    print("=" * 60)
    print("EXAMPLE 1: List Built-in Templates")
    print("=" * 60)

    print("\nBuilt-in template names:")
    for name in list_builtin_template_names():
        print(f"  - {name}")

    print("\n" + get_builtin_template_summary())


def example_2_load_and_inspect_template():
    """Example 2: Load and inspect a template"""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Load and Inspect Template")
    print("=" * 60)

    manager = TemplateManager()

    # Load built-in template
    template = manager.load_builtin('age_verification')

    if template:
        print(f"\nTemplate loaded: {template.name}")
        print(f"Version: {template.version}")
        print(f"Description: {template.description}")
        print(f"Tags: {', '.join(template.tags)}")
        print(f"\nParameters:")
        for key, value in template.parameters.items():
            print(f"  {key}: {value}")

        print(f"\nFull summary:")
        print(template.get_summary())


def example_3_create_custom_template():
    """Example 3: Create a custom template"""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Create Custom Template")
    print("=" * 60)

    # Create a custom template
    custom = Template(
        name='example_california_seniors',
        version='1.0.0',
        description='California licenses for seniors (65+) testing',
        author='Example User',
        tags=['example', 'seniors', 'california'],
        parameters={
            'state': 'CA',
            'count': 15,
            'age_min': 65,
            'age_max': 90,
            'output_dir': 'output/seniors',
        },
        parameter_definitions=[
            TemplateParameter(
                name='state',
                type=ParameterType.STRING,
                default='CA',
                description='State code',
                required=True,
                validation={'pattern': r'^[A-Z]{2}$'},
            ),
            TemplateParameter(
                name='count',
                type=ParameterType.INTEGER,
                default=15,
                description='Number of licenses to generate',
                validation={'min_value': 1, 'max_value': 1000},
            ),
            TemplateParameter(
                name='age_min',
                type=ParameterType.INTEGER,
                default=65,
                description='Minimum age',
                validation={'min_value': 16, 'max_value': 120},
            ),
            TemplateParameter(
                name='age_max',
                type=ParameterType.INTEGER,
                default=90,
                description='Maximum age',
                validation={'min_value': 16, 'max_value': 120},
            ),
        ],
        variables={
            'STATE': 'CA',
            'AGE_RANGE': '65-90',
        },
        documentation="""
# California Seniors Template

This template generates licenses for senior citizens in California.

## Use Cases
- Testing senior discount validation
- Age-appropriate UI/UX testing
- Accessibility feature testing

## Parameters
- State: California (CA)
- Age Range: 65-90 years
- Count: 15 licenses
        """,
    )

    print("\nCreated custom template:")
    print(custom.get_summary())

    # Validate the template
    validator = TemplateValidator()
    is_valid, errors = validator.validate(custom)

    if is_valid:
        print("\n✓ Template is valid!")
    else:
        print("\n✗ Template has errors:")
        for error in errors:
            print(f"  - {error}")

    # Save to manager
    try:
        manager = TemplateManager()
        saved_path = manager.save(custom)
        print(f"\n✓ Template saved to: {saved_path}")
    except Exception as e:
        print(f"\n✗ Error saving template: {e}")


def example_4_clone_and_modify():
    """Example 4: Clone and modify existing template"""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Clone and Modify Template")
    print("=" * 60)

    manager = TemplateManager()

    # Load existing template
    original = manager.load_builtin('age_verification')

    if original:
        print(f"\nOriginal template: {original.name}")
        print(f"  State: {original.parameters.get('state')}")
        print(f"  Count: {original.parameters.get('count')}")

        # Clone with new name
        cloned = original.clone(new_name='example_age_verification_ny')

        # Modify parameters
        cloned.parameters['state'] = 'NY'
        cloned.parameters['count'] = 12
        cloned.description = 'New York age verification testing (cloned from age_verification)'

        print(f"\nCloned template: {cloned.name}")
        print(f"  State: {cloned.parameters.get('state')}")
        print(f"  Count: {cloned.parameters.get('count')}")

        # Save cloned template
        try:
            manager.save(cloned)
            print(f"\n✓ Cloned template saved successfully")
        except Exception as e:
            print(f"\n✗ Error saving: {e}")


def example_5_search_templates():
    """Example 5: Search templates"""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Search Templates")
    print("=" * 60)

    manager = TemplateManager()

    # Search for templates
    search_queries = ['age', 'test', 'demo']

    for query in search_queries:
        results = manager.search(query, include_builtin=True)
        print(f"\nSearch results for '{query}':")
        for template in results:
            print(f"  - {template.name}: {template.description}")


def example_6_template_variables():
    """Example 6: Use template variables"""
    print("\n" + "=" * 60)
    print("EXAMPLE 6: Template Variables")
    print("=" * 60)

    # Create template with variables
    template = Template(
        name='example_variables',
        version='1.0.0',
        description='Demonstrates variable substitution',
        parameters={
            'state': 'CA',
            'count': 10,
            'output_dir': 'output/${STATE}_${DATE}',
        },
        variables={
            'STATE': 'CA',
            'DATE': datetime.now().strftime('%Y-%m-%d'),
            'COUNT': '10',
        },
    )

    # Substitute variables
    output_dir_original = template.parameters['output_dir']
    output_dir_substituted = template.substitute_variables(output_dir_original)

    print(f"\nOriginal output_dir: {output_dir_original}")
    print(f"After substitution: {output_dir_substituted}")

    # Substitute with additional variables
    text = "Generating ${COUNT} licenses for ${STATE} on ${DATE}"
    result = template.substitute_variables(text)
    print(f"\nTemplate text: {text}")
    print(f"After substitution: {result}")


def example_7_export_import():
    """Example 7: Export and import templates"""
    print("\n" + "=" * 60)
    print("EXAMPLE 7: Export and Import Templates")
    print("=" * 60)

    manager = TemplateManager()

    # Create a temporary template
    temp_template = Template(
        name='example_export_import',
        version='1.0.0',
        description='Template for export/import demonstration',
        parameters={'state': 'CA', 'count': 5},
    )

    try:
        # Save the template
        manager.save(temp_template)
        print(f"\n✓ Template '{temp_template.name}' created")

        # Export to file
        export_path = Path('/tmp/example_template.json')
        manager.export_template(temp_template.name, export_path)
        print(f"✓ Template exported to: {export_path}")

        # Import with new name
        imported = manager.import_template(
            export_path,
            new_name='example_imported',
            overwrite=True
        )
        print(f"✓ Template imported as: {imported.name}")

        # Clean up
        export_path.unlink()
        manager.delete('example_export_import')
        manager.delete('example_imported')
        print(f"✓ Cleanup completed")

    except Exception as e:
        print(f"\n✗ Error: {e}")


def example_8_validation():
    """Example 8: Template validation"""
    print("\n" + "=" * 60)
    print("EXAMPLE 8: Template Validation")
    print("=" * 60)

    # Create a template with validation errors
    invalid_template = Template(
        name='',  # Invalid: empty name
        version='not-semver',  # Invalid: not semantic version
        description='',  # Invalid: empty description
        parameters={
            'state': 'XX',  # Invalid: not a real state
            'count': -5,  # Invalid: negative count
        },
    )

    print("\nValidating intentionally invalid template:")

    validator = TemplateValidator()
    is_valid, errors = validator.validate(invalid_template)

    if not is_valid:
        print(f"\n✗ Template has {len(errors)} errors:")
        for i, error in enumerate(errors, 1):
            print(f"  {i}. {error}")
    else:
        print("\n✓ Template is valid (unexpected!)")

    # Show validation report
    print("\nFull validation report:")
    print(validator.get_validation_report(invalid_template))


def example_9_list_user_templates():
    """Example 9: List user templates"""
    print("\n" + "=" * 60)
    print("EXAMPLE 9: List User Templates")
    print("=" * 60)

    manager = TemplateManager()

    # List all templates
    all_templates = manager.list_templates(include_builtin=True)
    user_templates = manager.list_templates(include_builtin=False)
    builtin_templates = manager.list_templates(include_builtin=True)

    print(f"\nTotal templates: {len(all_templates)}")
    print(f"User templates: {len(user_templates)}")
    print(f"Built-in templates: {len(builtin_templates)}")

    if user_templates:
        print("\nUser templates:")
        for name in user_templates:
            info = manager.get_template_info(name)
            if info:
                print(f"  - {name} (v{info['version']}): {info['description']}")
    else:
        print("\nNo user templates found.")


def example_10_parameter_validation():
    """Example 10: Parameter validation"""
    print("\n" + "=" * 60)
    print("EXAMPLE 10: Parameter Validation")
    print("=" * 60)

    # Create parameter with validation rules
    count_param = TemplateParameter(
        name='count',
        type=ParameterType.INTEGER,
        description='Number of licenses',
        validation={
            'min_value': 1,
            'max_value': 100,
        },
    )

    # Test valid value
    is_valid, error = count_param.validate(50)
    print(f"\nValidate count=50: {'✓ Valid' if is_valid else f'✗ Error: {error}'}")

    # Test invalid value (too high)
    is_valid, error = count_param.validate(200)
    print(f"Validate count=200: {'✓ Valid' if is_valid else f'✗ Error: {error}'}")

    # Test invalid value (too low)
    is_valid, error = count_param.validate(0)
    print(f"Validate count=0: {'✓ Valid' if is_valid else f'✗ Error: {error}'}")

    # Test invalid type
    is_valid, error = count_param.validate("not a number")
    print(f"Validate count='not a number': {'✓ Valid' if is_valid else f'✗ Error: {error}'}")


def run_all_examples():
    """Run all examples"""
    print("\n")
    print("*" * 60)
    print(" " * 15 + "TEMPLATE SYSTEM EXAMPLES")
    print("*" * 60)

    examples = [
        example_1_list_builtin_templates,
        example_2_load_and_inspect_template,
        example_3_create_custom_template,
        example_4_clone_and_modify,
        example_5_search_templates,
        example_6_template_variables,
        example_7_export_import,
        example_8_validation,
        example_9_list_user_templates,
        example_10_parameter_validation,
    ]

    for example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"\n✗ Error in {example_func.__name__}: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "*" * 60)
    print(" " * 15 + "ALL EXAMPLES COMPLETED")
    print("*" * 60)
    print()


if __name__ == '__main__':
    run_all_examples()
