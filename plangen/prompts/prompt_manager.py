"""Prompt manager for PlanGEN."""
from __future__ import annotations

from pathlib import Path
from typing_extensions import Self

import jinja2


class PromptManager:
    """Manager for loading and rendering prompt templates."""
    def __init__(self: Self, templates_dir: str | None = None) -> None:
        """Initialize the prompt manager.

        Args:
            templates_dir: Directory containing prompt templates
        """
        if templates_dir is None:
            # Use default templates directory
            templates_dir = Path(Path(__file__).parent) / "templates"

        self.templates_dir = templates_dir

        # Set up Jinja2 environment
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.templates_dir),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Store custom prompts
        self.custom_prompts = {}

    def render(self: Self, template_name: str, **kwargs: object) -> str:
        """Render a prompt template with the given variables.

        Args:
            template_name: Name of the template file
            **kwargs: Variables to use in the template

        Returns:
            Rendered prompt
        """
        # Check for custom prompt first
        if template_name in self.custom_prompts:
            template = jinja2.Template(self.custom_prompts[template_name])
            return template.render(**kwargs)

        # Fall back to file-based template
        template = self.env.get_template(f"{template_name}.j2")
        return template.render(**kwargs)

    def get_system_message(self: Self, agent_type: str) -> str:
        """Get the system message for a specific agent type.

        Args:
            agent_type: Type of agent (constraint, verification, selection)

        Returns:
            System message for the agent
        """
        return self.render(f"system_{agent_type}")

    def get_prompt(self: Self, prompt_type: str, **kwargs: object) -> str:
        """Get a rendered prompt of a specific type.

        Args:
            prompt_type: Type of prompt to render
            **kwargs: Variables to use in the template

        Returns:
            Rendered prompt
        """
        return self.render(prompt_type, **kwargs)

    def update_prompt(self: Self, prompt_name: str, prompt_text: str) -> None:
        """Update or add a custom prompt template.

        Args:
            prompt_name: Name of the prompt template
            prompt_text: Template text
        """
        self.custom_prompts[prompt_name] = prompt_text
