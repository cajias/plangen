# Streaming Support in PlanGEN

PlanGEN provides streaming support to enable real-time progress tracking and intermediate result access during problem-solving workflows.

## Overview

Streaming allows you to receive updates as PlanGEN progresses through its workflow stages:

1. **Constraint Extraction** - Extract constraints from the problem
2. **Solution Generation** - Generate multiple candidate solutions
3. **Solution Verification** - Verify each solution against constraints
4. **Solution Selection** - Select the best solution based on verification results

## Basic Usage

### Using `solve_stream()`

The `solve_stream()` method yields dictionaries with step information as the workflow progresses:

```python
from plangen import PlanGen

# Create PlanGen instance
plangen = PlanGen.create(model="gpt-4o")

# Stream the solving process
problem = "Your problem statement here"
for update in plangen.solve_stream(problem):
    step = update["step"]
    status = update["status"]
    
    if status == "in_progress":
        print(f"Starting {step}...")
    elif status == "complete":
        print(f"Completed {step}")
        # Access step data
        data = update.get("data", {})
    elif status == "error":
        print(f"Error in {step}: {update['error']}")
        break
```

## Update Structure

Each update dictionary contains:

- **`step`** (str): The current workflow step
  - `"extract_constraints"` - Constraint extraction
  - `"generate_solutions"` - Solution generation
  - `"verify_solutions"` - Solution verification
  - `"select_solution"` - Solution selection
  - `"error"` - General error (only on critical failures)

- **`status`** (str): Current status of the step
  - `"in_progress"` - Step has started
  - `"complete"` - Step has finished successfully
  - `"error"` - Step encountered an error

- **`data`** (dict or None): Step-specific data
  - Available when `status == "complete"`
  - Contains results from the step (constraints, solutions, etc.)

- **`error`** (str, optional): Error message
  - Only present when `status == "error"`

## Common Patterns

### Pattern 1: Progress Tracking

Track overall progress as PlanGEN processes your problem:

```python
steps = [
    "extract_constraints",
    "generate_solutions", 
    "verify_solutions",
    "select_solution"
]

progress = {step: "pending" for step in steps}

for update in plangen.solve_stream(problem):
    step = update["step"]
    if step in progress:
        progress[step] = update["status"]
        
    # Calculate percentage
    completed = sum(1 for s in progress.values() if s == "complete")
    percentage = (completed / len(steps)) * 100
    print(f"Progress: {percentage:.0f}%")
```

### Pattern 2: Collecting Intermediate Results

Collect all intermediate results for analysis or debugging:

```python
results = {
    "constraints": None,
    "solutions": [],
    "verification_results": [],
    "selected_solution": None,
}

for update in plangen.solve_stream(problem):
    if update["status"] == "complete":
        data = update.get("data", {})
        
        # Extract relevant data
        if "constraints" in data:
            results["constraints"] = data["constraints"]
        if "solutions" in data:
            results["solutions"] = data["solutions"]
        if "verification_results" in data:
            results["verification_results"] = data["verification_results"]
        if "selected_solution" in data:
            results["selected_solution"] = data["selected_solution"]

# Now analyze all intermediate results
print(f"Found {len(results['solutions'])} candidate solutions")
```

### Pattern 3: Real-time UI Updates

Update a user interface in real-time as processing occurs:

```python
def update_ui(step: str, status: str, data: dict):
    """Update UI based on streaming updates."""
    if status == "in_progress":
        show_spinner(f"Processing {step}...")
    elif status == "complete":
        hide_spinner()
        if step == "extract_constraints":
            display_constraints(data["constraints"])
        elif step == "generate_solutions":
            display_solutions(data["solutions"])
        elif step == "select_solution":
            display_final_result(data["selected_solution"])

for update in plangen.solve_stream(problem):
    update_ui(update["step"], update["status"], update.get("data", {}))
```

### Pattern 4: Early Termination

Stop processing early if a condition is met:

```python
for update in plangen.solve_stream(problem):
    if update["status"] == "error":
        # Handle error and stop
        handle_error(update["error"])
        break
        
    if update["step"] == "generate_solutions" and update["status"] == "complete":
        # Check if we got enough solutions
        solutions = update["data"]["solutions"]
        if len(solutions) < 2:
            print("Not enough solutions generated, stopping")
            break
```

### Pattern 5: Logging and Monitoring

Log all steps for debugging or monitoring:

```python
import logging

logger = logging.getLogger(__name__)

for update in plangen.solve_stream(problem):
    step = update["step"]
    status = update["status"]
    
    if status == "in_progress":
        logger.info(f"Started {step}")
    elif status == "complete":
        logger.info(f"Completed {step}")
        logger.debug(f"Data: {update.get('data', {})}")
    elif status == "error":
        logger.error(f"Error in {step}: {update['error']}")
```

## Model-Level Streaming

For more advanced use cases, models also support streaming at the generation level:

```python
from plangen.models import OpenAIModelInterface

model = OpenAIModelInterface(model_name="gpt-4o")

# Stream text generation
for chunk in model.generate_stream("Your prompt here"):
    print(chunk, end="", flush=True)
```

This is useful when:
- Building custom workflows
- Displaying token-by-token generation to users
- Implementing custom agents with streaming

## Comparison with Non-Streaming

### Non-Streaming (Traditional)

```python
result = plangen.solve(problem)
# Wait for entire process to complete
print(result["selected_solution"])
```

**Pros:**
- Simpler API
- Get complete result in one call
- Better for batch processing

**Cons:**
- No progress feedback
- Can't access intermediate results
- Must wait for entire workflow

### Streaming

```python
for update in plangen.solve_stream(problem):
    # Process updates in real-time
    pass
```

**Pros:**
- Real-time progress updates
- Access to intermediate results
- Better user experience
- Can implement early termination

**Cons:**
- More complex to use
- Requires iteration handling
- Must track state yourself

## Best Practices

1. **Always handle errors**: Check for `status == "error"` and handle appropriately
2. **Use progress tracking**: Provide feedback to users on long-running operations
3. **Collect what you need**: Only store intermediate results if you actually need them
4. **Don't block the event loop**: In async contexts, use appropriate patterns
5. **Log streaming updates**: For production systems, log all steps for debugging

## Error Handling

Errors can occur at any step. Always check the status:

```python
try:
    for update in plangen.solve_stream(problem):
        if update["status"] == "error":
            step = update["step"]
            error = update["error"]
            print(f"Error in {step}: {error}")
            
            # Decide how to handle based on step
            if step == "extract_constraints":
                # Constraint extraction failed
                # Maybe retry with a simpler problem statement
                pass
            elif step == "generate_solutions":
                # Solution generation failed
                # Maybe reduce num_solutions
                pass
                
            break  # Stop processing
            
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Performance Considerations

- **Streaming overhead**: Streaming adds minimal overhead compared to non-streaming
- **Memory usage**: Streaming allows processing without keeping all data in memory
- **Latency**: First update comes faster than waiting for complete result
- **Concurrency**: Streaming doesn't affect underlying model concurrency

## Examples

See the `examples/streaming_example.py` file for complete working examples:

```bash
python examples/streaming_example.py
```

## Integration with Web Frameworks

### FastAPI Example

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import json

app = FastAPI()

@app.post("/solve-stream")
async def solve_stream(problem: str):
    plangen = PlanGen.create(model="gpt-4o")
    
    def generate():
        for update in plangen.solve_stream(problem):
            # Stream as JSON lines
            yield json.dumps(update) + "\n"
    
    return StreamingResponse(generate(), media_type="application/x-ndjson")
```

### Flask Example

```python
from flask import Flask, Response, request
import json

app = Flask(__name__)

@app.route("/solve-stream", methods=["POST"])
def solve_stream():
    problem = request.json["problem"]
    plangen = PlanGen.create(model="gpt-4o")
    
    def generate():
        for update in plangen.solve_stream(problem):
            yield f"data: {json.dumps(update)}\n\n"
    
    return Response(generate(), mimetype="text/event-stream")
```

## Future Enhancements

Planned improvements to streaming support:

- **Async streaming**: `async for update in plangen.solve_stream_async(problem)`
- **Token-level streaming**: Stream LLM tokens for each step
- **Custom callbacks**: Register callbacks for specific steps
- **Cancellation**: Cancel streaming mid-process
- **Backpressure**: Handle slow consumers gracefully

## See Also

- [API Reference](api_reference/index.md) - Complete API documentation
- [User Guide](user_guide/index.md) - General usage guide
- [Examples](examples/index.md) - More code examples
