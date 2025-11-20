# Verification Guide

Verification is a critical component of PlanGEN that evaluates whether generated solutions satisfy the problem constraints. This guide explains how to use and customize verification.

## Overview

PlanGEN's verification system:

1. Checks if solutions meet all constraints
2. Provides detailed feedback on issues
3. Assigns numerical scores (0.0 to 1.0)
4. Enables iterative refinement

## Built-in Verifiers

### Base Verifier

The default verifier uses LLM-based verification:

```python
from plangen import PlanGen

plangen = PlanGen.create()

# Verify a plan
feedback, score = plangen.verify_plan(
    problem="Schedule a meeting...",
    plan="Meeting at 10:00-10:30",
    constraints=["Must be 30 minutes", "Must be on Monday"]
)

print(f"Score: {score}")
print(f"Feedback: {feedback}")
```

### Domain-Specific Verifiers

PlanGEN includes specialized verifiers for common domains:

```python
from plangen import Verifiers

# Calendar scheduling verifier
calendar_verifier = Verifiers.calendar()

# Math problem verifier
math_verifier = Verifiers.math()

# Algorithm design verifier
algorithm_verifier = Verifiers.algorithm()
```

## Using Custom Verifiers

### With solve() Method

```python
from plangen import PlanGen, Verifiers

plangen = PlanGen.create()
verifier = Verifiers.calendar()

result = plangen.solve(
    problem="Schedule a meeting for 3 people...",
    verifier=verifier
)
```

### With verify_plan() Method

```python
from plangen import PlanGen, Verifiers

plangen = PlanGen.create()
verifier = Verifiers.calendar()

feedback, score = plangen.verify_plan(
    problem="Schedule a meeting...",
    plan="Monday 10:00-10:30",
    verifier=verifier
)
```

## Creating Custom Verifiers

### Basic Custom Verifier

```python
from typing import List, Tuple
from plangen.verification.base_verifier import BaseVerifier

class CustomVerifier(BaseVerifier):
    """Custom verifier for specific problem domain."""
    
    def verify_solution(
        self,
        problem: str,
        solution: str,
        constraints: List[str]
    ) -> Tuple[str, float]:
        """
        Verify a solution.
        
        Args:
            problem: The problem statement
            solution: The proposed solution
            constraints: List of constraints to check
            
        Returns:
            Tuple of (feedback, score)
        """
        feedback = []
        total_score = 0.0
        
        # Check each constraint
        for i, constraint in enumerate(constraints):
            satisfied = self._check_constraint(solution, constraint)
            if satisfied:
                feedback.append(f"✓ Constraint {i+1} satisfied")
                total_score += 1.0
            else:
                feedback.append(f"✗ Constraint {i+1} not satisfied: {constraint}")
        
        # Calculate final score
        score = total_score / len(constraints) if constraints else 0.0
        
        return "\n".join(feedback), score
    
    def _check_constraint(self, solution: str, constraint: str) -> bool:
        """Check if a specific constraint is satisfied."""
        # Implement constraint checking logic
        return constraint.lower() in solution.lower()
    
    def is_applicable(self, problem: str) -> bool:
        """Check if this verifier applies to the problem."""
        return "schedule" in problem.lower()
```

### Using the Custom Verifier

```python
from plangen import PlanGen

# Create custom verifier
verifier = CustomVerifier()

# Use with PlanGen
plangen = PlanGen.create()
result = plangen.solve(
    problem="Your problem here",
    verifier=verifier
)
```

## Verification Strategies

### 1. Rule-Based Verification

Check specific rules programmatically:

```python
class RuleBasedVerifier(BaseVerifier):
    """Verifier that checks specific rules."""
    
    def verify_solution(self, problem, solution, constraints):
        feedback = []
        score = 1.0
        
        # Check time format
        if not self._has_valid_time_format(solution):
            feedback.append("Invalid time format")
            score -= 0.3
        
        # Check duration
        if not self._has_correct_duration(solution, constraints):
            feedback.append("Incorrect meeting duration")
            score -= 0.4
        
        # Check participants
        if not self._has_all_participants(solution, constraints):
            feedback.append("Missing participants")
            score -= 0.3
        
        score = max(0.0, score)
        return "\n".join(feedback) if feedback else "All checks passed", score
    
    def _has_valid_time_format(self, solution):
        import re
        time_pattern = r'\d{1,2}:\d{2}'
        return bool(re.search(time_pattern, solution))
    
    def _has_correct_duration(self, solution, constraints):
        # Implement duration checking logic
        return True
    
    def _has_all_participants(self, solution, constraints):
        # Implement participant checking logic
        return True
```

### 2. LLM-Enhanced Verification

Combine rules with LLM verification:

```python
class HybridVerifier(BaseVerifier):
    """Verifier combining rules and LLM."""
    
    def __init__(self, llm_interface):
        self.llm = llm_interface
    
    def verify_solution(self, problem, solution, constraints):
        # First, check basic rules
        rule_feedback, rule_score = self._check_rules(solution, constraints)
        
        # If rules pass, use LLM for deeper verification
        if rule_score >= 0.7:
            llm_feedback, llm_score = self._llm_verify(
                problem, solution, constraints
            )
            final_score = (rule_score + llm_score) / 2
            feedback = f"Rules: {rule_feedback}\nLLM: {llm_feedback}"
            return feedback, final_score
        
        return rule_feedback, rule_score
    
    def _check_rules(self, solution, constraints):
        # Implement rule checking
        return "Rules passed", 0.9
    
    def _llm_verify(self, problem, solution, constraints):
        # Use LLM for verification
        prompt = f"""Verify this solution:
        Problem: {problem}
        Solution: {solution}
        Constraints: {constraints}
        
        Provide score (0.0-1.0) and feedback."""
        
        response = self.llm.generate("You are a verifier", prompt)
        # Parse response to extract score and feedback
        return response, 0.85
```

### 3. Multi-Criteria Verification

Evaluate multiple aspects separately:

```python
class MultiCriteriaVerifier(BaseVerifier):
    """Verifier that checks multiple criteria."""
    
    def verify_solution(self, problem, solution, constraints):
        criteria_scores = {}
        
        # Correctness
        criteria_scores['correctness'] = self._check_correctness(
            solution, constraints
        )
        
        # Completeness
        criteria_scores['completeness'] = self._check_completeness(
            solution, constraints
        )
        
        # Clarity
        criteria_scores['clarity'] = self._check_clarity(solution)
        
        # Efficiency
        criteria_scores['efficiency'] = self._check_efficiency(solution)
        
        # Calculate weighted score
        weights = {
            'correctness': 0.4,
            'completeness': 0.3,
            'clarity': 0.2,
            'efficiency': 0.1,
        }
        
        final_score = sum(
            criteria_scores[k] * weights[k]
            for k in weights
        )
        
        feedback = self._format_feedback(criteria_scores)
        return feedback, final_score
    
    def _check_correctness(self, solution, constraints):
        # Check if solution is correct
        return 0.9
    
    def _check_completeness(self, solution, constraints):
        # Check if solution is complete
        return 0.85
    
    def _check_clarity(self, solution):
        # Check if solution is clear
        return 0.8
    
    def _check_efficiency(self, solution):
        # Check if solution is efficient
        return 0.75
    
    def _format_feedback(self, scores):
        return "\n".join(f"{k}: {v:.2f}" for k, v in scores.items())
```

## Verification Best Practices

### 1. Separate Concerns

```python
# Good: Separate verification logic
class SchedulingVerifier(BaseVerifier):
    def verify_solution(self, problem, solution, constraints):
        time_valid = self._verify_time(solution)
        participants_valid = self._verify_participants(solution, constraints)
        duration_valid = self._verify_duration(solution, constraints)
        
        # Combine results
        ...
```

### 2. Provide Actionable Feedback

```python
# Bad: Vague feedback
feedback = "Solution has issues"

# Good: Specific feedback
feedback = """Issues found:
1. Time 9:30-10:00 conflicts with Alice's availability
2. Meeting duration is 30 min but requirement is 60 min
3. Location not specified"""
```

### 3. Use Appropriate Scoring

```python
# Define clear scoring rubric
def calculate_score(violations):
    base_score = 1.0
    critical_violations = [v for v in violations if v.critical]
    minor_violations = [v for v in violations if not v.critical]
    
    # Critical issues: -0.3 each
    base_score -= len(critical_violations) * 0.3
    
    # Minor issues: -0.1 each
    base_score -= len(minor_violations) * 0.1
    
    return max(0.0, base_score)
```

### 4. Handle Edge Cases

```python
def verify_solution(self, problem, solution, constraints):
    # Handle empty solution
    if not solution or not solution.strip():
        return "Solution is empty", 0.0
    
    # Handle missing constraints
    if not constraints:
        return "No constraints to verify against", 0.5
    
    # Normal verification
    ...
```

### 5. Make Verifiers Reusable

```python
# Good: Configurable verifier
class ConfigurableVerifier(BaseVerifier):
    def __init__(self, strict_mode=False, min_score=0.6):
        self.strict_mode = strict_mode
        self.min_score = min_score
    
    def verify_solution(self, problem, solution, constraints):
        feedback, score = self._verify(problem, solution, constraints)
        
        if self.strict_mode and score < self.min_score:
            feedback += f"\nScore {score} below minimum {self.min_score}"
            score = 0.0
        
        return feedback, score
```

## Verification Examples

### Calendar Scheduling

```python
class CalendarVerifier(BaseVerifier):
    def verify_solution(self, problem, solution, constraints):
        from datetime import datetime, timedelta
        
        feedback = []
        score = 1.0
        
        # Extract time from solution
        time_match = self._extract_time(solution)
        if not time_match:
            return "No valid time found in solution", 0.0
        
        start_time = time_match['start']
        end_time = time_match['end']
        
        # Check duration
        duration = (end_time - start_time).total_seconds() / 60
        required_duration = self._extract_duration(constraints)
        if abs(duration - required_duration) > 5:
            feedback.append(
                f"Duration {duration} min differs from required {required_duration} min"
            )
            score -= 0.3
        
        # Check availability
        busy_times = self._extract_busy_times(constraints)
        if self._has_conflicts(start_time, end_time, busy_times):
            feedback.append("Time slot conflicts with busy times")
            score -= 0.5
        
        return "\n".join(feedback) if feedback else "Valid", max(0.0, score)
```

### Mathematical Proofs

```python
class MathVerifier(BaseVerifier):
    def verify_solution(self, problem, solution, constraints):
        feedback = []
        score = 1.0
        
        # Check if solution includes calculation steps
        if not self._has_calculation_steps(solution):
            feedback.append("Missing calculation steps")
            score -= 0.2
        
        # Check final answer format
        if not self._has_final_answer(solution):
            feedback.append("Final answer not clearly stated")
            score -= 0.3
        
        # Verify calculations (if possible)
        if self._can_verify_calculations(solution):
            if not self._calculations_correct(solution):
                feedback.append("Calculation errors detected")
                score -= 0.5
        
        return "\n".join(feedback) if feedback else "Correct", max(0.0, score)
```

## Integration with Algorithms

Verification works seamlessly with all PlanGEN algorithms:

```python
from plangen import PlanGen

verifier = CustomVerifier()

# With BestOfN
result = plangen.solve(
    problem,
    algorithm="best_of_n",
    n_plans=5,
    verifier=verifier
)

# With TreeOfThought
result = plangen.solve(
    problem,
    algorithm="tree_of_thought",
    verifier=verifier
)

# With REBASE
result = plangen.solve(
    problem,
    algorithm="rebase",
    verifier=verifier
)
```

## Next Steps

- See [Examples](../examples/custom_verification.md) for complete verification examples
- Learn about [Visualization](visualization.md) to see verification results
- Explore [Configuration](configuration.md) for verification settings
