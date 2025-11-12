# Visualization Example

Example using visualization tools.

```python
from plangen.visualization import GraphRenderer
from plangen.algorithms import TreeOfThought

renderer = GraphRenderer(output_dir="./viz")
algorithm = TreeOfThought(llm_interface=model)
algorithm.add_observer(renderer)

solution, score, metadata = algorithm.run(problem)
```
