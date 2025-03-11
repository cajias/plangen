# Simple Example

This example demonstrates the basic usage of PlanGEN using the new public API.

## Full Example

```python
"""
Simple example of using PlanGEN with the new public API
"""

import json
import os
from dotenv import load_dotenv

from plangen import PlanGen

# Load environment variables from .env file
load_dotenv()


def main():
    """Run a simple example of PlanGEN with the new public API."""
    # Create a PlanGen instance
    # This will automatically use OpenAI if OPENAI_API_KEY is set,
    # or try to fall back to AWS Bedrock if AWS credentials are available
    plangen = PlanGen.create()
    
    # You can also explicitly specify the model:
    # plangen = PlanGen.with_openai(model_name="gpt-4o")
    # plangen = PlanGen.with_bedrock(model_id="anthropic.claude-3-sonnet-20240229-v1:0")

    # Define a problem
    problem = """
    Design an algorithm to find the kth largest element in an unsorted array.
    For example, given [3, 2, 1, 5, 6, 4] and k = 2, the output should be 5.
    """

    print(f"Problem: {problem}")
    print("\nSolving problem...")

    # Solve the problem
    result = plangen.solve(problem)

    # Print the extracted constraints
    print("\n=== Extracted Constraints ===")
    constraints = result.get("constraints", [])
    for i, constraint in enumerate(constraints, 1):
        print(f"{i}. {constraint}")

    # Print the selected solution
    print("\n=== Selected Solution ===")
    print(result.get("selected_solution", "No solution found"))

    # Save the results to a file
    with open("plangen_results.json", "w") as f:
        json.dump(result, f, indent=2)

    print("\nResults saved to plangen_results.json")


if __name__ == "__main__":
    main()
```

## Step-by-Step Explanation

1. **Import the necessary modules:**
   ```python
   import json
   import os
   from dotenv import load_dotenv
   from plangen import PlanGen
   ```

2. **Load environment variables:**
   ```python
   load_dotenv()
   ```
   This loads API keys from a `.env` file if one exists.

3. **Create a PlanGen instance:**
   ```python
   plangen = PlanGen.create()
   ```
   This creates a PlanGen instance with default settings. It will automatically use the OpenAI API if an API key is available, or fall back to AWS Bedrock if AWS credentials are available.

4. **Define a problem:**
   ```python
   problem = """
   Design an algorithm to find the kth largest element in an unsorted array.
   For example, given [3, 2, 1, 5, 6, 4] and k = 2, the output should be 5.
   """
   ```

5. **Solve the problem:**
   ```python
   result = plangen.solve(problem)
   ```
   This will:
   - Extract constraints from the problem
   - Generate multiple solutions
   - Verify the solutions
   - Select the best solution

6. **Access the results:**
   ```python
   constraints = result.get("constraints", [])
   selected_solution = result.get("selected_solution", "No solution found")
   ```

7. **Save the results:**
   ```python
   with open("plangen_results.json", "w") as f:
       json.dump(result, f, indent=2)
   ```

## Alternative Model Configurations

You can create a PlanGen instance with a specific model:

```python
# Using OpenAI
plangen = PlanGen.with_openai(
    model_name="gpt-4o",
    temperature=0.7,
    max_tokens=1024
)

# Using AWS Bedrock
plangen = PlanGen.with_bedrock(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    region="us-east-1",
    temperature=0.7,
    max_tokens=1024
)
```

## Using a Specific Algorithm

You can also specify which algorithm to use when solving a problem:

```python
result = plangen.solve(
    problem,
    algorithm="best_of_n",
    n_plans=5,
    sampling_strategy="diverse"
)
```

Available algorithms are:
- `"best_of_n"` - Generates multiple plans and selects the best one
- `"tree_of_thought"` - Explores multiple reasoning paths in a tree structure
- `"rebase"` - Uses recursive refinement to improve plans
- `"mixture"` - Dynamically selects the best algorithm for the problem