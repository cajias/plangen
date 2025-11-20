# Custom Prompts Guide

PlanGEN uses Jinja2 templates for all LLM interactions. This guide explains how to customize prompts to improve performance for your specific use cases.

## Understanding the Prompt System

PlanGEN uses prompts for different stages of the planning workflow:

1. **Constraint Extraction**: Identify constraints from problem statements
2. **Solution Generation**: Generate candidate solutions
3. **Verification**: Evaluate solutions against constraints
4. **Selection**: Choose the best solution from candidates

## Prompt Manager

The `PromptManager` class manages all prompts:

```python
from plangen.prompts import PromptManager

# Create a prompt manager
prompt_manager = PromptManager()

# Get current prompt template
constraint_prompt = prompt_manager.get_prompt("constraint_extraction")
print(constraint_prompt)
```

## Customizing Prompts

### Method 1: Using update_prompt

```python
from plangen.prompts import PromptManager
from plangen import PlanGen
from plangen.models import OpenAIModelInterface

# Create a custom prompt manager
prompt_manager = PromptManager()

# Update constraint extraction prompt
prompt_manager.update_prompt(
    "constraint_extraction",
    """You are an expert at analyzing scheduling problems.
    
    Problem: {problem}
    
    Identify all constraints including:
    - Time constraints
    - Resource constraints
    - Person availability
    - Meeting requirements
    
    List each constraint clearly and concisely."""
)

# Create model and use custom prompts
model = OpenAIModelInterface(model_name="gpt-4o")
plangen = PlanGen.with_model(model)
plangen._plangen.prompt_manager = prompt_manager

# Use PlanGen with custom prompts
result = plangen.solve(problem)
```

### Method 2: Using Custom Template Files

Create a custom template directory:

```
my_prompts/
├── constraint_extraction.j2
├── solution_generation.j2
├── verification.j2
└── selection.j2
```

Load custom templates:

```python
from plangen.prompts import PromptManager

# Load custom templates from directory
prompt_manager = PromptManager(template_dir="my_prompts")
```

## Prompt Templates

### Constraint Extraction

Default template:

```jinja2
You are an expert at analyzing problems and extracting constraints.

Problem: {{ problem }}

Analyze the problem and identify all constraints, requirements, and limitations.
List each constraint on a separate line.
```

Custom example for scheduling:

```jinja2
You are an expert scheduler with deep knowledge of time management.

Problem: {{ problem }}

Extract all constraints from this scheduling problem:
1. Time windows and availability
2. Duration requirements
3. Resource conflicts
4. Priority requirements
5. Any other limitations

Format: List each constraint as a bullet point.
```

### Solution Generation

Default template:

```jinja2
You are an expert problem solver.

Problem: {{ problem }}

{% if constraints %}
Constraints:
{% for constraint in constraints %}
- {{ constraint }}
{% endfor %}
{% endif %}

Generate a detailed solution that satisfies all constraints.
```

Custom example with emphasis on creativity:

```jinja2
You are a creative problem solver who thinks outside the box.

Problem: {{ problem }}

{% if constraints %}
Requirements:
{% for constraint in constraints %}
✓ {{ constraint }}
{% endfor %}
{% endif %}

Think creatively and propose an innovative solution. Consider:
- Alternative approaches
- Edge cases
- Potential optimizations

Provide a detailed, step-by-step solution.
```

### Verification

Default template:

```jinja2
You are an expert at verifying solutions.

Problem: {{ problem }}
Solution: {{ solution }}

{% if constraints %}
Constraints:
{% for constraint in constraints %}
- {{ constraint }}
{% endfor %}
{% endif %}

Verify if the solution satisfies all constraints.
Provide feedback and a score from 0.0 to 1.0.
```

Custom example with detailed rubric:

```jinja2
You are a meticulous solution verifier.

Problem: {{ problem }}
Proposed Solution: {{ solution }}

{% if constraints %}
Requirements:
{% for constraint in constraints %}
{{ loop.index }}. {{ constraint }}
{% endfor %}
{% endif %}

Evaluate the solution:

For each requirement:
- Check if it's satisfied (Yes/No)
- Provide specific feedback
- Note any issues

Calculate score:
- 1.0: All requirements perfectly satisfied
- 0.8-0.9: Minor issues or improvements needed
- 0.6-0.7: Some requirements not met
- 0.4-0.5: Multiple problems
- 0.0-0.3: Fundamental issues

Format your response as:
Score: [0.0-1.0]
Feedback: [Detailed explanation]
```

### Selection

Default template:

```jinja2
You are an expert at comparing and selecting solutions.

Problem: {{ problem }}

{% for solution in solutions %}
Solution {{ loop.index }} (Score: {{ solution.score }}):
{{ solution.text }}

Feedback: {{ solution.feedback }}
---
{% endfor %}

Select the best solution and explain your reasoning.
```

## Domain-Specific Prompt Examples

### Calendar Scheduling

```python
prompt_manager.update_prompt(
    "constraint_extraction",
    """You are an expert calendar scheduling assistant.

Problem: {{ problem }}

Extract scheduling constraints:
1. PARTICIPANTS: List all participants
2. DURATION: Meeting duration
3. TIME_WINDOW: Available time range
4. BUSY_TIMES: Each participant's busy slots
5. PREFERENCES: Any scheduling preferences
6. REQUIREMENTS: Additional requirements (earliest time, etc.)

Be precise with times and participants."""
)

prompt_manager.update_prompt(
    "solution_generation",
    """You are an expert at finding optimal meeting times.

Problem: {{ problem }}

{% if constraints %}
Constraints:
{% for constraint in constraints %}
• {{ constraint }}
{% endfor %}
{% endif %}

Find the optimal meeting time:
1. Check all participants' availability
2. Find overlapping free slots
3. Apply any preferences (e.g., earliest time)
4. Propose the time in format: "Day HH:MM-HH:MM"

Explain your reasoning step by step."""
)
```

### Algorithm Design

```python
prompt_manager.update_prompt(
    "constraint_extraction",
    """You are an expert in algorithm design and complexity analysis.

Problem: {{ problem }}

Identify algorithmic constraints:
1. TIME_COMPLEXITY: Required time complexity
2. SPACE_COMPLEXITY: Required space complexity
3. INPUT_FORMAT: Input data format and constraints
4. OUTPUT_FORMAT: Required output format
5. EDGE_CASES: Special cases to handle
6. CONSTRAINTS: Any additional requirements

Be specific about Big-O notation."""
)

prompt_manager.update_prompt(
    "solution_generation",
    """You are an expert algorithm designer.

Problem: {{ problem }}

{% if constraints %}
Requirements:
{% for constraint in constraints %}
- {{ constraint }}
{% endfor %}
{% endif %}

Design an algorithm:
1. Describe the approach
2. Provide pseudocode
3. Analyze time complexity
4. Analyze space complexity
5. Explain why it meets all requirements

Be thorough and precise."""
)
```

### Mathematical Problems

```python
prompt_manager.update_prompt(
    "verification",
    """You are a mathematics professor with expertise in proof verification.

Problem: {{ problem }}
Solution: {{ solution }}

{% if constraints %}
Requirements:
{% for constraint in constraints %}
- {{ constraint }}
{% endfor %}
{% endif %}

Verify the solution:
1. Check mathematical correctness
2. Verify all steps in the derivation
3. Confirm the final answer
4. Check for computational errors

Score:
- 1.0: Mathematically sound and correct
- 0.8: Correct with minor notation issues
- 0.6: Right approach but calculation errors
- 0.4: Conceptual errors
- 0.2: Fundamentally wrong

Provide detailed mathematical feedback."""
)
```

## Best Practices

### 1. Be Specific

❌ Bad: "List the constraints"
✅ Good: "List all time constraints, resource constraints, and participant availability"

### 2. Use Clear Formatting

```jinja2
# Good: Clear structure
Problem: {{ problem }}

Constraints:
{% for constraint in constraints %}
{{ loop.index }}. {{ constraint }}
{% endfor %}

Your task: Generate a solution
```

### 3. Provide Examples

```jinja2
Generate a solution in this format:

Example:
Time: Monday 10:00-10:30
Participants: Alice, Bob, Carol
Reasoning: This is the earliest available slot for all participants.

Your solution:
```

### 4. Set Clear Expectations

```jinja2
Provide a score from 0.0 to 1.0 where:
- 1.0 means perfect compliance with all constraints
- 0.5 means partial compliance
- 0.0 means no constraints are satisfied

Score: [your score]
Explanation: [detailed reasoning]
```

### 5. Include Context

```jinja2
You are an expert {{ domain }} specialist with {{ years }} years of experience.
Your expertise includes:
- {{ skill_1 }}
- {{ skill_2 }}
- {{ skill_3 }}

Problem: {{ problem }}
```

## Testing Custom Prompts

Always test custom prompts with various inputs:

```python
from plangen import PlanGen

# Create PlanGen with custom prompts
plangen = create_custom_plangen()

# Test cases
test_problems = [
    "Simple scheduling problem...",
    "Complex scheduling problem...",
    "Edge case problem...",
]

for problem in test_problems:
    print(f"\nTesting: {problem[:50]}...")
    result = plangen.solve(problem)
    print(f"Score: {result['selected_solution']['score']}")
    print(f"Solution: {result['selected_solution']['solution'][:100]}...")
```

## Advanced Techniques

### Conditional Prompts

```jinja2
{% if domain == "scheduling" %}
You are a calendar scheduling expert.
{% elif domain == "algorithms" %}
You are a computer science algorithm expert.
{% else %}
You are a general problem-solving expert.
{% endif %}

Problem: {{ problem }}
```

### Chain-of-Thought Prompting

```jinja2
Think through this problem step by step:

Problem: {{ problem }}

1. First, understand what is being asked
2. Then, identify all constraints
3. Next, consider possible approaches
4. Finally, select and explain the best solution

Let's begin with step 1...
```

### Few-Shot Examples

```jinja2
Here are examples of good solutions:

Example 1:
Problem: Schedule a 30-min meeting for 2 people...
Solution: Monday 10:00-10:30 because...

Example 2:
Problem: Schedule a 1-hour meeting for 3 people...
Solution: Tuesday 14:00-15:00 because...

Now solve this problem:
Problem: {{ problem }}
```

## Prompt Engineering Tips

1. **Start simple**: Begin with default prompts and refine
2. **Be explicit**: State exactly what you want
3. **Use examples**: Show the model what good output looks like
4. **Test iteratively**: Make small changes and test
5. **Domain-specific**: Customize for your problem domain
6. **Clear metrics**: Define scoring criteria explicitly
7. **Error handling**: Include instructions for edge cases

## Next Steps

- See [Verification](verification.md) for custom verification strategies
- Explore [Examples](../examples/custom_prompts_example.md) for complete examples
- Learn about [Configuration](configuration.md) for additional settings
