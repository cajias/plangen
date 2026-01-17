# Prompts

Prompt management and templating for PlanGEN.

## Overview

PlanGEN uses Jinja2 templates for prompt management. The `PromptManager` handles loading, rendering, and customization of prompts.

## Classes

### PromptManager

```python
from plangen.prompts import PromptManager

manager = PromptManager()
```

#### Methods

**`render(template_name: str, **kwargs) -> str`**

Render a prompt template with variables.

```python
prompt = manager.render("constraint_extraction", problem="Schedule a meeting")
```

**`get_system_message(agent_type: str) -> str`**

Get the system message for an agent type.

```python
system_msg = manager.get_system_message("constraint")
```

**`get_prompt(prompt_type: str, **kwargs) -> str`**

Get a rendered prompt by type.

```python
prompt = manager.get_prompt("verification", solution="...", constraints=["..."])
```

**`update_prompt(prompt_name: str, prompt_text: str) -> None`**

Override a prompt template at runtime.

```python
manager.update_prompt("constraint_extraction", "Your custom template: {{ problem }}")
```

## Template Location

Default templates are in `plangen/prompts/templates/`. Templates use Jinja2 syntax with `.j2` extension.

## See Also

- [Agents](agents.md) - Agents that use prompt templates
