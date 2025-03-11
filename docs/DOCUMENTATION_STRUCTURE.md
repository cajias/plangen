# PlanGEN Documentation Structure

This file provides an overview of the documentation structure for the PlanGEN project.

## Documentation Directory Structure

```
docs/
├── index.md                      # Main documentation page
├── DOCUMENTATION_STRUCTURE.md    # This file
├── api_reference/                # API reference documentation
│   ├── index.md                  # API reference overview
│   ├── plangen.md                # PlanGen class reference
│   ├── algorithm.md              # Algorithm class reference
│   ├── visualization.md          # Visualization class reference
│   └── verifiers.md              # Verifiers class reference
├── user_guide/                   # User guide documentation
│   ├── index.md                  # User guide overview
│   ├── installation.md           # Installation instructions
│   ├── quickstart.md             # Quick start guide
│   ├── configuration.md          # Configuration guide
│   ├── models.md                 # Models guide
│   ├── custom_prompts.md         # Custom prompts guide
│   ├── verification.md           # Verification guide
│   └── visualization.md          # Visualization guide
├── algorithm_reference/          # Algorithm reference documentation
│   ├── index.md                  # Algorithm reference overview
│   ├── best_of_n.md              # BestOfN algorithm reference
│   ├── tree_of_thought.md        # TreeOfThought algorithm reference
│   ├── rebase.md                 # REBASE algorithm reference
│   └── mixture_of_algorithms.md  # MixtureOfAlgorithms reference
└── examples/                     # Example documentation
    ├── index.md                  # Examples overview
    ├── simple_example.md         # Simple example
    ├── openai_example.md         # OpenAI example
    ├── bedrock_example.md        # Bedrock example
    ├── best_of_n_example.md      # BestOfN example
    ├── tree_of_thought_example.md # TreeOfThought example
    ├── rebase_example.md         # REBASE example
    ├── mixture_of_algorithms_example.md # MixtureOfAlgorithms example
    ├── custom_verification.md    # Custom verification example
    ├── visualization_example.md  # Visualization example
    └── custom_prompts_example.md # Custom prompts example
```

## Examples Directory

Additionally, we've added new example files:

```
examples/
├── api_quickstart.py             # Quick start example using the new API
└── api_best_of_n.py              # BestOfN algorithm example using the new API
```

## Documentation Status

This is the initial version of the documentation. The following sections have been completed:

- [x] Main documentation page (index.md)
- [x] User guide overview (user_guide/index.md)
- [x] Installation guide (user_guide/installation.md)
- [x] Quick start guide (user_guide/quickstart.md)
- [x] API reference overview (api_reference/index.md)
- [x] PlanGen class reference (api_reference/plangen.md)
- [x] Algorithm reference overview (algorithm_reference/index.md)
- [x] BestOfN algorithm reference (algorithm_reference/best_of_n.md)
- [x] Examples overview (examples/index.md)
- [x] Simple example (examples/simple_example.md)

The following sections still need to be completed:

- [ ] Algorithm class reference (api_reference/algorithm.md)
- [ ] Visualization class reference (api_reference/visualization.md)
- [ ] Verifiers class reference (api_reference/verifiers.md)
- [ ] Configuration guide (user_guide/configuration.md)
- [ ] Models guide (user_guide/models.md)
- [ ] Custom prompts guide (user_guide/custom_prompts.md)
- [ ] Verification guide (user_guide/verification.md)
- [ ] Visualization guide (user_guide/visualization.md)
- [ ] TreeOfThought algorithm reference (algorithm_reference/tree_of_thought.md)
- [ ] REBASE algorithm reference (algorithm_reference/rebase.md)
- [ ] MixtureOfAlgorithms reference (algorithm_reference/mixture_of_algorithms.md)
- [ ] OpenAI example (examples/openai_example.md)
- [ ] Bedrock example (examples/bedrock_example.md)
- [ ] BestOfN example (examples/best_of_n_example.md)
- [ ] TreeOfThought example (examples/tree_of_thought_example.md)
- [ ] REBASE example (examples/rebase_example.md)
- [ ] MixtureOfAlgorithms example (examples/mixture_of_algorithms_example.md)
- [ ] Custom verification example (examples/custom_verification.md)
- [ ] Visualization example (examples/visualization_example.md)
- [ ] Custom prompts example (examples/custom_prompts_example.md)

## Next Steps

1. Complete the remaining documentation sections
2. Add more example files
3. Add API reference documentation for internal classes (for contributors)
4. Add more advanced usage examples