"""
Template loader utility for PlanGEN.
"""

import os
from typing import Dict, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape

class TemplateLoader:
    """Utility for loading and rendering templates."""
    
    def __init__(self):
        """Initialize the template loader."""
        # Base directory for templates
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Initialize Jinja environment
        self.env = Environment(
            loader=FileSystemLoader([
                os.path.join(self.base_dir, "templates"),
                os.path.join(self.base_dir, "examples")
            ]),
            autoescape=select_autoescape(['html', 'xml'])
        )
    
    def render_template(
        self, 
        template_path: str, 
        variables: Dict[str, str]
    ) -> str:
        """Render a template with the given variables.
        
        Args:
            template_path: Path to the template file, relative to the templates directory
            variables: Dictionary of variables to use in the template
            
        Returns:
            Rendered template as a string
        """
        template = self.env.get_template(template_path)
        return template.render(**variables)
    
    def get_algorithm_template(
        self,
        algorithm: str,
        template_type: str,
        domain: Optional[str] = None
    ) -> str:
        """Get a template for a specific algorithm and template type.
        
        Args:
            algorithm: Name of the algorithm (e.g., "tree_of_thought")
            template_type: Type of template (e.g., "step", "reward")
            domain: Optional domain name for domain-specific templates
            
        Returns:
            Path to the template
        """
        # First try domain-specific template
        if domain:
            domain_path = f"{domain}/templates/{algorithm}/{template_type}.jinja"
            if os.path.exists(os.path.join(self.base_dir, "examples", domain_path)):
                return domain_path
        
        # Fall back to generic template
        return f"{algorithm}/{template_type}.jinja"