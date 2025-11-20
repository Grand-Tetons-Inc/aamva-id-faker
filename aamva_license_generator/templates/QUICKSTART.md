# Template System Quick Start Guide

**Get started with templates in 5 minutes**

---

## Installation

The template system is included in the AAMVA License Generator package. No additional installation needed.

---

## Quick Examples

### 1. Use a Built-in Template

```python
from aamva_license_generator.templates import TemplateManager

# Create manager
manager = TemplateManager()

# Load built-in template
template = manager.load('age_verification')

# View parameters
print(f"State: {template.parameters['state']}")        # 'CA'
print(f"Count: {template.parameters['count']}")        # 6
print(f"Description: {template.description}")

# Use template parameters in your code
# (integrate with your license generator)
```

### 2. List All Available Templates

```python
manager = TemplateManager()

# List all templates (built-in + user)
templates = manager.list_templates()
print("Available templates:")
for name in templates:
    print(f"  - {name}")

# Filter by tag
testing_templates = manager.list_templates(tags=['testing'])
```

### 3. Create and Save a Custom Template

```python
from aamva_license_generator.templates import Template

# Create custom template
my_template = Template(
    name='my_custom_test',
    version='1.0.0',
    description='My custom testing scenario',
    tags=['testing', 'custom'],
    parameters={
        'state': 'NY',
        'count': 20,
        'age_min': 25,
        'age_max': 40,
    }
)

# Save it
manager = TemplateManager()
manager.save(my_template)
print(f"✓ Template saved to: {manager.templates_dir}")

# Load it later
loaded = manager.load('my_custom_test')
```

### 4. Clone and Modify Existing Template

```python
manager = TemplateManager()

# Load existing template
original = manager.load('age_verification')

# Clone it
modified = original.clone(new_name='age_verification_florida')

# Modify parameters
modified.parameters['state'] = 'FL'
modified.parameters['count'] = 12

# Save
manager.save(modified)
```

### 5. Search for Templates

```python
manager = TemplateManager()

# Search by keyword
results = manager.search('age')
for template in results:
    print(f"{template.name}: {template.description}")
```

---

## Built-in Templates at a Glance

| Template | Count | Purpose |
|----------|-------|---------|
| `age_verification` | 6 | Test age verification logic (under 21, 21, over 21) |
| `expired_licenses` | 9 | Test expiration checking |
| `all_states` | 51 | One license per US state |
| `edge_cases` | 10 | Long names, special chars, leap years |
| `training_scenario` | 8 | Security training materials |
| `demo_scenario` | 5 | Professional demos |
| `quick_test` | 3 | Fast development testing |
| `performance_test` | 1000 | Performance/stress testing |
| `veteran_licenses` | 10 | Veteran designation testing |
| `organ_donor` | 10 | Organ donor testing |
| `real_id_mix` | 10 | REAL ID compliance |

---

## Common Use Cases

### For QA Engineers

```python
# Load comprehensive test template
template = manager.load('performance_test')

# Customize for your test
template.parameters['count'] = 500
template.parameters['state'] = 'CA'

# Save as new test scenario
manager.save(template.clone('qa_regression_test_v1'))
```

### For Trainers

```python
# Load training template
template = manager.load('training_scenario')

# Customize for your location
template.parameters['state'] = 'NV'  # Nevada for casino training

# View what it will generate
print(template.get_summary())
```

### For Developers

```python
# Quick iteration during development
template = manager.load('quick_test')

# Modify on the fly
template.parameters['count'] = 5
template.parameters['state'] = 'NY'

# Generate immediately (integrate with your generator)
```

---

## Next Steps

1. **Read the full documentation**: See `README.md` for comprehensive guide
2. **Try the examples**: Run `python -m aamva_license_generator.templates.examples`
3. **Create your own templates**: Start with cloning existing ones
4. **Share with team**: Export/import templates as JSON files

---

## Need Help?

- **Full Documentation**: `/home/user/aamva-id-faker/aamva_license_generator/templates/README.md`
- **Examples**: `/home/user/aamva-id-faker/aamva_license_generator/templates/examples.py`
- **Implementation Summary**: `/home/user/aamva-id-faker/TEMPLATE_SYSTEM_SUMMARY.md`

---

**Happy templating!** 🎉
