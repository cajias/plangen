"""
Template loader for PlanGEN.

This module provides functionality for loading and rendering templates used by
PlanGEN algorithms and agents.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

from jinja2 import Environment, FileSystemLoader, TemplateNotFound, select_autoescape


class TemplateError(Exception):
    """Exception raised for template-related errors."""

    pass


class TemplateLoader:
    """Loads and renders templates for PlanGEN algorithms and agents.

    This class provides a unified way to load and render templates for all
    PlanGEN components, with support for algorithm-specific, domain-specific,
    and common templates.

    Attributes:
        template_dir: Path to the template directory
        env: Jinja2 environment for template rendering
    """

    def __init__(self, template_dir: Optional[str] = None):
        """Initialize the template loader.

        Args:
            template_dir: Optional custom template directory path
        """
        if template_dir:
            self.template_dir = Path(template_dir)
        else:
            # Default to the templates directory in the package
            module_dir = Path(__file__).parent.parent
            self.template_dir = module_dir / "templates"

        # Initialize Jinja environment
        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def get_algorithm_template(
        self, algorithm: str, template_type: str, domain: Optional[str] = None
    ) -> str:
        """Get the path to a template for a specific algorithm.

        This method implements a template resolution hierarchy:
        1. Domain-specific algorithm template (algorithm/domain/type.jinja)
        2. Algorithm-specific template (algorithm/type.jinja)
        3. Common template (common/type.jinja)

        Args:
            algorithm: Name of the algorithm (e.g., "best_of_n")
            template_type: Type of template (e.g., "plan", "verification")
            domain: Optional domain name for domain-specific templates

        Returns:
            Template path as a string

        Raises:
            TemplateError: If the template cannot be found
        """
        # Check for domain-specific template first
        if domain:
            domain_path = f"{algorithm}/{domain}/{template_type}.jinja"
            if (self.template_dir / domain_path).exists():
                return domain_path

        # Check for algorithm-specific template
        algorithm_path = f"{algorithm}/{template_type}.jinja"
        if (self.template_dir / algorithm_path).exists():
            return algorithm_path

        # Check for common template
        common_path = f"common/{template_type}.jinja"
        if (self.template_dir / common_path).exists():
            return common_path

        raise TemplateError(
            f"Template not found for algorithm '{algorithm}', "
            f"type '{template_type}', domain '{domain}'"
        )

    def render_template(self, template_path: str, variables: Dict[str, Any]) -> str:
        """Render a template with the given variables.

        Args:
            template_path: Path to the template file
            variables: Dictionary of variables to use in the template

        Returns:
            Rendered template as a string

        Raises:
            TemplateError: If the template cannot be rendered
        """
        try:
            template = self.env.get_template(template_path)
            return template.render(**variables)
        except TemplateNotFound:
            raise TemplateError(f"Template not found: {template_path}")
        except Exception as e:
            raise TemplateError(f"Error rendering template: {str(e)}")
