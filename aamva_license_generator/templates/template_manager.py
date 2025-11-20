"""
Template Manager - CRUD Operations

Provides comprehensive template management functionality including:
- Create, Read, Update, Delete templates
- Import/Export templates
- Template inheritance resolution
- Search and filtering
- Built-in template access

Author: AAMVA License Generator Team
Version: 1.0.0
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

from .template import Template
from .template_validator import TemplateValidator, ValidationError


class TemplateManager:
    """
    Manages template storage, retrieval, and lifecycle operations.

    The manager handles:
    - Loading templates from JSON files
    - Saving templates to disk
    - Template inheritance resolution
    - Built-in template access
    - Import/export functionality
    """

    def __init__(self, templates_dir: Optional[Path] = None):
        """
        Initialize the template manager.

        Args:
            templates_dir: Directory for storing user templates.
                          Defaults to ~/.aamva-templates/
        """
        if templates_dir is None:
            templates_dir = Path.home() / '.aamva-templates'

        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(parents=True, exist_ok=True)

        # Built-in templates directory (in package)
        package_dir = Path(__file__).parent
        self.builtin_dir = package_dir / 'library'

        # Template validator
        self.validator = TemplateValidator()

        # Cache for loaded templates
        self._cache: Dict[str, Template] = {}

    def save(self, template: Template, overwrite: bool = False) -> Path:
        """
        Save a template to disk.

        Args:
            template: Template to save
            overwrite: Whether to overwrite if template already exists

        Returns:
            Path to the saved template file

        Raises:
            FileExistsError: If template exists and overwrite=False
            ValidationError: If template validation fails
        """
        # Validate template
        is_valid, errors = self.validator.validate(template)
        if not is_valid:
            raise ValidationError(f"Template validation failed: {'; '.join(errors)}")

        # Check if template already exists
        template_path = self.templates_dir / f"{template.name}.json"
        if template_path.exists() and not overwrite:
            raise FileExistsError(
                f"Template '{template.name}' already exists. "
                "Use overwrite=True to replace it."
            )

        # Update metadata
        template.metadata['updated_at'] = datetime.utcnow().isoformat()
        if not template_path.exists():
            template.metadata['created_at'] = datetime.utcnow().isoformat()

        # Save to file
        with open(template_path, 'w') as f:
            f.write(template.to_json(indent=2))

        # Update cache
        self._cache[template.name] = template

        return template_path

    def load(self, name: str, resolve_inheritance: bool = True) -> Optional[Template]:
        """
        Load a template by name.

        Searches in this order:
        1. Cache
        2. User templates directory
        3. Built-in templates directory

        Args:
            name: Template name (without .json extension)
            resolve_inheritance: Whether to resolve parent templates

        Returns:
            Template instance or None if not found

        Raises:
            ValidationError: If template is invalid
        """
        # Check cache first
        if name in self._cache:
            return self._cache[name]

        # Try user templates
        template_path = self.templates_dir / f"{name}.json"
        if not template_path.exists():
            # Try built-in templates
            template_path = self.builtin_dir / f"{name}.json"
            if not template_path.exists():
                return None

        # Load from file
        with open(template_path, 'r') as f:
            template = Template.from_json(f.read())

        # Validate
        is_valid, errors = self.validator.validate(template)
        if not is_valid:
            raise ValidationError(
                f"Template '{name}' is invalid: {'; '.join(errors)}"
            )

        # Resolve inheritance if needed
        if resolve_inheritance and template.parent_template:
            parent = self.load(template.parent_template, resolve_inheritance=True)
            if parent is None:
                raise ValidationError(
                    f"Parent template '{template.parent_template}' not found"
                )
            template = template.merge_with_parent(parent)

        # Cache and return
        self._cache[name] = template
        return template

    def load_builtin(self, name: str) -> Optional[Template]:
        """
        Load a built-in template.

        Args:
            name: Built-in template name

        Returns:
            Template instance or None if not found
        """
        template_path = self.builtin_dir / f"{name}.json"
        if not template_path.exists():
            return None

        with open(template_path, 'r') as f:
            template = Template.from_json(f.read())

        return template

    def delete(self, name: str) -> bool:
        """
        Delete a user template.

        Args:
            name: Template name to delete

        Returns:
            True if deleted, False if not found

        Note:
            Built-in templates cannot be deleted.
        """
        template_path = self.templates_dir / f"{name}.json"
        if not template_path.exists():
            return False

        template_path.unlink()

        # Remove from cache
        if name in self._cache:
            del self._cache[name]

        return True

    def list_templates(
        self,
        include_builtin: bool = True,
        tags: Optional[List[str]] = None
    ) -> List[str]:
        """
        List available templates.

        Args:
            include_builtin: Whether to include built-in templates
            tags: Filter by tags (any tag matches)

        Returns:
            List of template names
        """
        templates = []

        # User templates
        if self.templates_dir.exists():
            for path in self.templates_dir.glob('*.json'):
                template_name = path.stem
                if tags:
                    template = self.load(template_name)
                    if template and any(tag in template.tags for tag in tags):
                        templates.append(template_name)
                else:
                    templates.append(template_name)

        # Built-in templates
        if include_builtin and self.builtin_dir.exists():
            for path in self.builtin_dir.glob('*.json'):
                template_name = path.stem
                if template_name not in templates:  # Avoid duplicates
                    if tags:
                        template = self.load_builtin(template_name)
                        if template and any(tag in template.tags for tag in tags):
                            templates.append(template_name)
                    else:
                        templates.append(template_name)

        return sorted(templates)

    def search(self, query: str, include_builtin: bool = True) -> List[Template]:
        """
        Search templates by name, description, or tags.

        Args:
            query: Search query string
            include_builtin: Whether to include built-in templates

        Returns:
            List of matching templates
        """
        results = []
        query_lower = query.lower()

        for name in self.list_templates(include_builtin=include_builtin):
            template = self.load(name)
            if template is None:
                continue

            # Search in name, description, and tags
            if (query_lower in template.name.lower() or
                query_lower in template.description.lower() or
                any(query_lower in tag.lower() for tag in template.tags)):
                results.append(template)

        return results

    def export_template(self, name: str, output_path: Union[str, Path]) -> Path:
        """
        Export a template to a file.

        Args:
            name: Template name to export
            output_path: Path to export to

        Returns:
            Path to exported file

        Raises:
            FileNotFoundError: If template not found
        """
        template = self.load(name)
        if template is None:
            raise FileNotFoundError(f"Template '{name}' not found")

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save with export metadata
        template.metadata['exported_at'] = datetime.utcnow().isoformat()
        template.metadata['export_version'] = '1.0.0'

        with open(output_path, 'w') as f:
            f.write(template.to_json(indent=2))

        return output_path

    def import_template(
        self,
        import_path: Union[str, Path],
        new_name: Optional[str] = None,
        overwrite: bool = False
    ) -> Template:
        """
        Import a template from a file.

        Args:
            import_path: Path to template file to import
            new_name: Optional new name for the template
            overwrite: Whether to overwrite if template exists

        Returns:
            Imported template

        Raises:
            FileNotFoundError: If import file not found
            ValidationError: If template is invalid
        """
        import_path = Path(import_path)
        if not import_path.exists():
            raise FileNotFoundError(f"Import file not found: {import_path}")

        # Load template
        with open(import_path, 'r') as f:
            template = Template.from_json(f.read())

        # Rename if requested
        if new_name:
            template.name = new_name

        # Add import metadata
        template.metadata['imported_at'] = datetime.utcnow().isoformat()
        template.metadata['imported_from'] = str(import_path)

        # Save
        self.save(template, overwrite=overwrite)

        return template

    def copy_template(
        self,
        source_name: str,
        new_name: str,
        overwrite: bool = False
    ) -> Template:
        """
        Copy an existing template with a new name.

        Args:
            source_name: Name of template to copy
            new_name: Name for the new template
            overwrite: Whether to overwrite if new name exists

        Returns:
            Copied template

        Raises:
            FileNotFoundError: If source template not found
        """
        source = self.load(source_name)
        if source is None:
            raise FileNotFoundError(f"Template '{source_name}' not found")

        # Clone with new name
        copied = source.clone(new_name=new_name)

        # Save
        self.save(copied, overwrite=overwrite)

        return copied

    def get_template_info(self, name: str) -> Optional[Dict[str, any]]:
        """
        Get detailed information about a template without fully loading it.

        Args:
            name: Template name

        Returns:
            Dictionary with template info or None if not found
        """
        template = self.load(name)
        if template is None:
            return None

        # Check if it's a built-in template
        is_builtin = (self.builtin_dir / f"{name}.json").exists()

        return {
            'name': template.name,
            'version': template.version,
            'description': template.description,
            'author': template.author,
            'tags': template.tags,
            'parameters': list(template.parameters.keys()),
            'parameter_count': len(template.parameters),
            'has_parent': template.parent_template is not None,
            'parent_template': template.parent_template,
            'is_builtin': is_builtin,
            'created_at': template.metadata.get('created_at'),
            'updated_at': template.metadata.get('updated_at'),
        }

    def validate_template(self, name: str) -> tuple[bool, List[str]]:
        """
        Validate a template without modifying it.

        Args:
            name: Template name

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        template = self.load(name, resolve_inheritance=False)
        if template is None:
            return False, [f"Template '{name}' not found"]

        return self.validator.validate(template)

    def clear_cache(self):
        """Clear the template cache."""
        self._cache.clear()

    def get_cache_size(self) -> int:
        """Get the number of cached templates."""
        return len(self._cache)

    def __str__(self) -> str:
        """String representation"""
        user_count = len(list(self.templates_dir.glob('*.json')))
        builtin_count = len(list(self.builtin_dir.glob('*.json'))) if self.builtin_dir.exists() else 0
        return (
            f"TemplateManager(user_templates={user_count}, "
            f"builtin_templates={builtin_count}, "
            f"cached={len(self._cache)})"
        )
