# AWS Bedrock Example

Example using AWS Bedrock models with PlanGEN.

```python
from plangen import PlanGen

# Create PlanGen with Bedrock
plangen = PlanGen.with_bedrock(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    region="us-east-1"
)

# Solve problem
result = plangen.solve("Your problem here")
print(result["selected_solution"])
```
