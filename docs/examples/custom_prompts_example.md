# Custom Prompts Example

Example customizing prompts.

```python
from plangen.prompts import PromptManager

prompt_manager = PromptManager()
prompt_manager.update_prompt(
    "constraint_extraction",
    "Your custom prompt template"
)
```
