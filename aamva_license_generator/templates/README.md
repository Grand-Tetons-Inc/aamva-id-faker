# AAMVA License Generator - Template System

**Version:** 1.0.0
**Author:** AAMVA License Generator Team
**Date:** 2025-11-20

## Overview

The Template System provides a comprehensive solution for saving and loading license generation configurations. It enables users to create reusable templates for common testing scenarios, share configurations across teams, and rapidly iterate on test data generation.

### Key Features

- **Template Data Model**: Full-featured data model with parameters, metadata, and validation
- **JSON-Based Storage**: Human-readable, version-controllable template files
- **Schema Validation**: Automatic validation against JSON schemas
- **Variable Substitution**: Dynamic variable replacement (${STATE}, ${COUNT}, etc.)
- **Template Inheritance**: Child templates can extend parent templates
- **11 Pre-Built Templates**: Production-ready templates for common scenarios
- **Import/Export**: Share templates across teams and environments
- **CRUD Operations**: Complete create, read, update, delete functionality

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Template Structure](#template-structure)
3. [Built-in Templates](#built-in-templates)
4. [Creating Custom Templates](#creating-custom-templates)
5. [Using Templates](#using-templates)
6. [Template Variables](#template-variables)
7. [Template Inheritance](#template-inheritance)
8. [Import/Export](#importexport)
9. [API Reference](#api-reference)
10. [Examples](#examples)

---

## Quick Start

### Using a Built-in Template

```python
from aamva_license_generator.templates import TemplateManager

# Create a template manager
manager = TemplateManager()

# Load a built-in template
template = manager.load('age_verification')

# View template details
print(template.get_summary())

# Access parameters
state = template.parameters['state']  # 'CA'
count = template.parameters['count']  # 6

# Use the template to generate licenses
# (Actual generation would integrate with your license generator)
```

### Creating a Simple Template

```python
from aamva_license_generator.templates import Template, TemplateParameter, ParameterType

# Create a new template
my_template = Template(
    name='my_test_scenario',
    version='1.0.0',
    description='Testing licenses for New York with specific age range',
    tags=['testing', 'custom'],
    parameters={
        'state': 'NY',
        'count': 20,
        'age_min': 25,
        'age_max': 35,
    },
    parameter_definitions=[
        TemplateParameter(
            name='state',
            type=ParameterType.STRING,
            required=True,
            description='State code'
        ),
        TemplateParameter(
            name='count',
            type=ParameterType.INTEGER,
            default=10,
            validation={'min_value': 1, 'max_value': 1000}
        ),
    ]
)

# Save the template
manager = TemplateManager()
manager.save(my_template)
```

---

## Template Structure

### Complete Template Anatomy

```json
{
  "name": "template_name",
  "version": "1.0.0",
  "description": "Human-readable description of what this template does",
  "author": "Your Name or Team",
  "tags": ["testing", "age_verification"],
  "parameters": {
    "state": "CA",
    "count": 10,
    "age_min": 18,
    "age_max": 65
  },
  "parameter_definitions": [
    {
      "name": "state",
      "type": "string",
      "default": "CA",
      "description": "State code for licenses",
      "required": true,
      "validation": {
        "pattern": "^[A-Z]{2}$"
      },
      "examples": ["CA", "NY", "TX"]
    }
  ],
  "parent_template": null,
  "variables": {
    "STATE": "CA",
    "COUNT": "10"
  },
  "metadata": {
    "created_at": "2025-11-20T08:00:00Z",
    "updated_at": "2025-11-20T08:00:00Z"
  },
  "documentation": "# Extended Documentation\n\nMarkdown-formatted documentation..."
}
```

### Core Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Unique template identifier (alphanumeric, underscores, hyphens) |
| `version` | string | Yes | Semantic version (e.g., "1.0.0") |
| `description` | string | Yes | Brief description of template purpose |
| `author` | string | No | Author or team name |
| `tags` | array | No | Tags for categorization and search |
| `parameters` | object | Yes | Actual parameter values |
| `parameter_definitions` | array | No | Parameter metadata and validation rules |
| `parent_template` | string | No | Name of parent template (for inheritance) |
| `variables` | object | No | Runtime variables for substitution |
| `metadata` | object | No | Additional metadata (timestamps, etc.) |
| `documentation` | string | No | Extended documentation in Markdown |

---

## Built-in Templates

The system includes 11 production-ready templates for common scenarios:

### 1. **age_verification** - Age Verification Testing
Generates licenses for testing age verification logic:
- 2 licenses: People aged 18-20.99 (under 21)
- 2 licenses: Exactly 21 years old (edge case)
- 2 licenses: People aged 21-30 (over 21)

**Use Cases:** Testing bar/nightclub age checks, online gambling, alcohol purchase validation

```python
template = manager.load('age_verification')
# Default: 6 California licenses
```

### 2. **expired_licenses** - Expiration Testing
Tests expiration validation with three scenarios:
- 3 expired licenses (30-365 days ago)
- 3 expiring soon (within 30 days)
- 3 valid licenses (1+ years remaining)

**Use Cases:** Testing expiration warnings, validation logic

```python
template = manager.load('expired_licenses')
# Default: 9 California licenses
```

### 3. **all_states** - State Coverage Testing
Generates one license from each US jurisdiction (50 states + DC).

**Use Cases:** Parser testing, format coverage, comprehensive validation

```python
template = manager.load('all_states')
# Generates 51 licenses, one per state
```

### 4. **edge_cases** - Edge Case Testing
Tests unusual but valid data:
- Long names (30+ characters)
- Special characters (O'Brien, José)
- Leap year birthdates (Feb 29)
- Maximum/minimum ages

**Use Cases:** Robust testing, truncation handling, special character support

```python
template = manager.load('edge_cases')
# 10 licenses with various edge cases
```

### 5. **training_scenario** - Security Training
Pre-configured for security trainer use cases:
- Under 21, valid 21+, expired, veteran, organ donor scenarios

**Use Cases:** New hire training, quarterly refreshers, casino security

```python
template = manager.load('training_scenario')
# Default: Nevada (NV) for casino training
```

### 6. **demo_scenario** - Sales Demonstrations
Professional licenses for product demos:
- Clean data, no edge cases
- Professional age range (25-40)
- Easy to scan and demonstrate

**Use Cases:** Sales presentations, trade shows, customer onboarding

```python
template = manager.load('demo_scenario')
# 5 California licenses, professional appearance
```

### 7. **veteran_licenses** - Veteran Status Testing
Licenses with veteran designation.

**Use Cases:** Veteran discount validation, indicator recognition

```python
template = manager.load('veteran_licenses')
# Default: Texas (prominent veteran flag)
```

### 8. **organ_donor** - Organ Donor Testing
Licenses with organ donor designation.

**Use Cases:** Organ donor status recognition in scanning systems

```python
template = manager.load('organ_donor')
# 10 California licenses with donor indicator
```

### 9. **real_id_mix** - REAL ID Compliance
Mix of REAL ID compliant and non-compliant licenses.

**Use Cases:** REAL ID verification logic testing

```python
template = manager.load('real_id_mix')
# 5 REAL ID + 5 non-REAL ID
```

### 10. **quick_test** - Rapid Development Testing
Minimal template for quick iteration (3 licenses).

**Use Cases:** Fast development cycles, quick validation

```python
template = manager.load('quick_test')
# Just 3 licenses for speed
```

### 11. **performance_test** - Performance Testing
Large batch for performance and stress testing (1000 licenses).

**Use Cases:** Performance benchmarking, stress testing, memory validation

```python
template = manager.load('performance_test')
# 1000 licenses with parallel generation enabled
```

---

## Creating Custom Templates

### Method 1: Programmatic Creation

```python
from aamva_license_generator.templates import Template, TemplateParameter, ParameterType

# Create template
custom = Template(
    name='california_seniors',
    version='1.0.0',
    description='California licenses for seniors (65+) testing',
    author='QA Team',
    tags=['testing', 'seniors', 'california'],
    parameters={
        'state': 'CA',
        'count': 15,
        'age_min': 65,
        'age_max': 90,
        'output_dir': 'output/seniors',
    },
    parameter_definitions=[
        TemplateParameter(
            name='age_min',
            type=ParameterType.INTEGER,
            default=65,
            description='Minimum age for senior testing',
            validation={'min_value': 65, 'max_value': 120},
        ),
    ],
)

# Save
manager = TemplateManager()
manager.save(custom)
```

### Method 2: Clone and Modify

```python
# Load existing template
base = manager.load('age_verification')

# Clone with new name
seniors = base.clone(new_name='seniors_age_verification')

# Modify parameters
seniors.parameters['state'] = 'FL'  # Florida seniors
seniors.parameters['age_ranges'] = [
    {'min': 65, 'max': 75, 'count': 5},
    {'min': 75, 'max': 90, 'count': 5},
]
seniors.description = 'Senior age verification testing for Florida'

# Save
manager.save(seniors)
```

### Method 3: JSON File

Create a JSON file in `~/.aamva-templates/` or use the manager:

```json
{
  "name": "custom_scenario",
  "version": "1.0.0",
  "description": "My custom test scenario",
  "parameters": {
    "state": "NY",
    "count": 25
  }
}
```

```python
# Import from file
manager.import_template('path/to/custom_scenario.json')
```

---

## Using Templates

### Loading Templates

```python
manager = TemplateManager()

# Load by name (searches user templates, then built-in)
template = manager.load('age_verification')

# Load built-in specifically
template = manager.load_builtin('quick_test')

# Load with inheritance resolution
template = manager.load('child_template', resolve_inheritance=True)
```

### Listing Templates

```python
# List all templates
all_templates = manager.list_templates(include_builtin=True)
print(all_templates)
# ['age_verification', 'all_states', 'custom_scenario', ...]

# Filter by tags
testing_templates = manager.list_templates(tags=['testing'])
training_templates = manager.list_templates(tags=['training'])
```

### Searching Templates

```python
# Search by name, description, or tags
results = manager.search('age', include_builtin=True)
for template in results:
    print(f"{template.name}: {template.description}")
```

### Deleting Templates

```python
# Delete a user template (built-in templates cannot be deleted)
success = manager.delete('old_template')
if success:
    print("Template deleted")
```

---

## Template Variables

Variables allow dynamic substitution in templates using the syntax `${VARIABLE_NAME}`.

### Common Variables

| Variable | Description | Example Value |
|----------|-------------|---------------|
| `${STATE}` | State code | "CA", "NY" |
| `${STATE_NAME}` | Full state name | "California" |
| `${COUNT}` | Number of licenses | "10", "50" |
| `${AGE_RANGE}` | Age range | "18-21", "65-90" |
| `${OUTPUT_DIR}` | Output directory | "output/testing" |
| `${DATE}` | Current date | "2025-11-20" |
| `${TIMESTAMP}` | Current timestamp | "2025-11-20T08:00:00Z" |

### Using Variables

```python
template = Template(
    name='variable_example',
    parameters={
        'state': 'CA',
        'output_dir': 'output/${STATE}_testing',
    },
    variables={
        'STATE': 'CA',
        'DATE': '2025-11-20',
    }
)

# Substitute variables in any string
output_dir = template.substitute_variables('output/${STATE}_${DATE}')
# Result: "output/CA_2025-11-20"
```

---

## Template Inheritance

Templates can inherit from parent templates, with child parameters overriding parent parameters.

### Parent Template

```python
# Create parent template
base = Template(
    name='base_testing',
    version='1.0.0',
    description='Base template for all testing scenarios',
    parameters={
        'output_dir': 'output',
        'include_pdf': True,
        'include_docx': True,
    }
)
manager.save(base)
```

### Child Template

```python
# Create child template
child = Template(
    name='california_testing',
    version='1.0.0',
    description='California-specific testing',
    parent_template='base_testing',  # Inherit from parent
    parameters={
        'state': 'CA',
        'count': 20,
        # Inherits: output_dir, include_pdf, include_docx
    }
)
manager.save(child)

# Load with inheritance resolved
loaded = manager.load('california_testing', resolve_inheritance=True)
print(loaded.parameters)
# {'state': 'CA', 'count': 20, 'output_dir': 'output', 'include_pdf': True, 'include_docx': True}
```

---

## Import/Export

### Exporting Templates

```python
# Export to file
manager.export_template('age_verification', 'templates/age_verification.json')

# Export adds metadata
# - exported_at timestamp
# - export_version
```

### Importing Templates

```python
# Import from file
template = manager.import_template(
    'templates/age_verification.json',
    new_name='imported_age_verification',  # Optional rename
    overwrite=False
)

# Import adds metadata
# - imported_at timestamp
# - imported_from path
```

### Sharing Templates

```bash
# Export template
python -c "
from aamva_license_generator.templates import TemplateManager
manager = TemplateManager()
manager.export_template('my_template', 'shared_templates/my_template.json')
"

# Share the JSON file with team (email, version control, etc.)

# Team member imports
python -c "
from aamva_license_generator.templates import TemplateManager
manager = TemplateManager()
manager.import_template('shared_templates/my_template.json')
"
```

---

## API Reference

### TemplateManager

```python
class TemplateManager:
    def __init__(self, templates_dir: Optional[Path] = None)
    def save(self, template: Template, overwrite: bool = False) -> Path
    def load(self, name: str, resolve_inheritance: bool = True) -> Optional[Template]
    def load_builtin(self, name: str) -> Optional[Template]
    def delete(self, name: str) -> bool
    def list_templates(self, include_builtin: bool = True, tags: Optional[List[str]] = None) -> List[str]
    def search(self, query: str, include_builtin: bool = True) -> List[Template]
    def export_template(self, name: str, output_path: Union[str, Path]) -> Path
    def import_template(self, import_path: Union[str, Path], new_name: Optional[str] = None, overwrite: bool = False) -> Template
    def copy_template(self, source_name: str, new_name: str, overwrite: bool = False) -> Template
    def get_template_info(self, name: str) -> Optional[Dict[str, any]]
    def validate_template(self, name: str) -> Tuple[bool, List[str]]
```

### Template

```python
class Template:
    def __init__(self, name: str, version: str = '1.0.0', ...)
    def to_dict(self) -> Dict[str, Any]
    def to_json(self, indent: int = 2) -> str
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Template'
    @classmethod
    def from_json(cls, json_str: str) -> 'Template'
    def validate_parameters(self) -> Tuple[bool, List[str]]
    def substitute_variables(self, text: str, additional_vars: Optional[Dict[str, Any]] = None) -> str
    def merge_with_parent(self, parent: 'Template') -> 'Template'
    def clone(self, new_name: Optional[str] = None) -> 'Template'
    def get_summary(self) -> str
```

### TemplateValidator

```python
class TemplateValidator:
    def __init__(self, schema_path: Optional[Path] = None)
    def validate(self, template: Template) -> Tuple[bool, List[str]]
    def validate_file(self, file_path: Path) -> Tuple[bool, List[str]]
    def get_validation_report(self, template: Template) -> str
```

---

## Examples

### Example 1: QA Engineer - Comprehensive Testing

```python
"""
QA Engineer needs to test all 51 US states with specific age scenarios
"""
from aamva_license_generator.templates import TemplateManager, Template

manager = TemplateManager()

# Create comprehensive test suite
test_suite = Template(
    name='qa_comprehensive_suite',
    version='1.0.0',
    description='Comprehensive QA test suite for all states and age scenarios',
    tags=['qa', 'comprehensive', 'testing'],
    parameters={
        'states': 'ALL',
        'count_per_state': 10,
        'age_scenarios': [
            {'type': 'under_18', 'count': 2},
            {'type': '18_to_21', 'count': 2},
            {'type': '21_to_65', 'count': 4},
            {'type': 'over_65', 'count': 2},
        ],
        'include_edge_cases': True,
        'output_dir': 'qa_test_suite_${DATE}',
    },
)

manager.save(test_suite)

# Use in testing
loaded = manager.load('qa_comprehensive_suite')
print(f"Will generate {51 * loaded.parameters['count_per_state']} licenses")
# 510 licenses total (51 states × 10 per state)
```

### Example 2: Security Trainer - Monthly Training Session

```python
"""
Security trainer preparing for monthly casino security training
"""
manager = TemplateManager()

# Start with built-in training template
base_training = manager.load('training_scenario')

# Clone and customize for this month
monthly_training = base_training.clone(new_name='november_2025_training')
monthly_training.parameters['state'] = 'NV'
monthly_training.parameters['count'] = 12
monthly_training.parameters['include_annotations'] = True
monthly_training.variables['TRAINING_MONTH'] = 'November 2025'

manager.save(monthly_training)

# Export for backup/sharing
manager.export_template(
    'november_2025_training',
    'training_materials/november_2025_training.json'
)
```

### Example 3: Developer - Quick Iteration

```python
"""
Developer testing new barcode encoding feature
"""
manager = TemplateManager()

# Use quick test template for rapid iteration
quick = manager.load('quick_test')
quick.parameters['state'] = 'NY'
quick.parameters['count'] = 5

# During development, modify and save frequently
for test_case in ['edge_long_names', 'edge_special_chars', 'edge_leap_year']:
    test_template = quick.clone(new_name=f'dev_{test_case}')
    test_template.parameters['output_dir'] = f'dev_output/{test_case}'
    manager.save(test_template)

    # Generate and test
    # ... your generation code ...
```

### Example 4: Product Manager - Sales Demo Preparation

```python
"""
Product manager preparing demo for California prospect
"""
manager = TemplateManager()

# Start with demo scenario
demo = manager.load('demo_scenario')
demo.parameters['state'] = 'CA'
demo.parameters['count'] = 3  # Small number for live demo

# Customize for specific demo
demo_custom = demo.clone(new_name='ca_prospect_demo_2025')
demo_custom.description = 'California prospect demo - Nov 2025'
demo_custom.parameters['age_range'] = [30, 45]  # Match prospect demographic
demo_custom.parameters['clean_data'] = True

manager.save(demo_custom)

# Export for sales team
manager.export_template(
    'ca_prospect_demo_2025',
    'sales_materials/demos/ca_prospect_demo_2025.json'
)
```

---

## Best Practices

### 1. Naming Conventions

- Use lowercase with underscores: `age_verification`, `california_testing`
- Be descriptive: `seniors_florida_testing` not `test1`
- Include version in name if maintaining multiple versions: `demo_v1`, `demo_v2`

### 2. Versioning

- Use semantic versioning: `1.0.0`, `1.1.0`, `2.0.0`
- Increment patch for bug fixes: `1.0.0` → `1.0.1`
- Increment minor for new features: `1.0.0` → `1.1.0`
- Increment major for breaking changes: `1.0.0` → `2.0.0`

### 3. Documentation

- Always provide a clear description
- Use the `documentation` field for detailed usage instructions
- Include examples in documentation

### 4. Tags

- Use consistent, lowercase tags
- Common tags: `testing`, `training`, `demo`, `production`, `development`
- Add domain-specific tags: `age_verification`, `performance`, `edge_cases`

### 5. Parameters

- Define parameter_definitions for validation
- Use sensible defaults
- Document expected ranges and formats
- Validate at template save time

### 6. Organization

- Use subdirectories in templates_dir for organization
- Export important templates to version control
- Share templates via Git repositories
- Document custom templates in README files

---

## Troubleshooting

### Template Not Found

```python
template = manager.load('my_template')
if template is None:
    print("Template not found")
    print("Available templates:", manager.list_templates())
```

### Validation Errors

```python
is_valid, errors = manager.validate_template('my_template')
if not is_valid:
    print("Validation errors:")
    for error in errors:
        print(f"  - {error}")
```

### Import Conflicts

```python
try:
    manager.import_template('template.json', new_name='imported_template')
except FileExistsError:
    print("Template already exists. Use overwrite=True to replace.")
    manager.import_template('template.json', overwrite=True)
```

---

## Advanced Topics

### Custom Validation Rules

```python
# Add custom validation in parameter definitions
param = TemplateParameter(
    name='custom_field',
    type=ParameterType.STRING,
    validation={
        'pattern': r'^[A-Z]{3}-\d{4}$',  # Format: ABC-1234
        'min_length': 8,
        'max_length': 8,
    }
)
```

### Template Composition

```python
# Combine multiple templates
base = manager.load('base_testing')
age_config = manager.load('age_verification')
state_config = manager.load('california_settings')

# Merge parameters
combined = Template(
    name='combined_template',
    parameters={
        **base.parameters,
        **age_config.parameters,
        **state_config.parameters,
    }
)
```

### Programmatic Template Generation

```python
# Generate templates programmatically
states = ['CA', 'NY', 'TX', 'FL']

for state in states:
    template = Template(
        name=f'quick_test_{state.lower()}',
        version='1.0.0',
        description=f'Quick test template for {state}',
        parameters={'state': state, 'count': 5}
    )
    manager.save(template)
```

---

## Support and Contributing

- **Issues**: Report bugs and request features at GitHub repository
- **Documentation**: Full documentation at https://docs.aamva-license-generator.org
- **Contributing**: See CONTRIBUTING.md for guidelines
- **License**: See LICENSE file

---

**Last Updated:** 2025-11-20
**Version:** 1.0.0
**Maintainer:** AAMVA License Generator Team
