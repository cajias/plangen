"""
Example demonstrating how to use the public API for solving problems with various algorithms.
"""

import json
import os
from dotenv import load_dotenv

# Import from the public API
from plangen import PlanGen, Algorithm, Visualization, Verifiers

# Load environment variables (contains API keys)
load_dotenv()


def main():
    """Run a complete example using the public API."""
    # Problem statement
    problem = """
    Schedule a 30-minute meeting for 3 people: Alice, Bob, and Charlie.
    Alice is available from 9:00-11:00 and 14:00-16:00.
    Bob is available from 10:00-12:00 and 15:00-17:00.
    Charlie is available from 9:00-10:30 and 15:30-17:00.
    Find an earliest time slot that works for all participants.
    """
    
    print("=" * 80)
    print("PlanGEN Public API Example")
    print("=" * 80)
    print(f"\nProblem:\n{problem}")
    
    # 1. Using the default workflow
    print("\n[1] Using the default workflow")
    print("-" * 50)
    
    # Create a PlanGen instance with OpenAI
    plangen = PlanGen.with_openai(model_name="gpt-4o")
    
    # Extract constraints manually (optional step)
    print("\nExtracting constraints...")
    constraints = plangen.extract_constraints(problem)
    print("Constraints:")
    for i, constraint in enumerate(constraints, 1):
        print(f"  {i}. {constraint}")
    
    # Generate a single plan manually (optional step)
    print("\nGenerating a single plan...")
    plan = plangen.generate_plan(problem, constraints)
    print(f"Generated plan: {plan}")
    
    # Verify the plan manually (optional step)
    print("\nVerifying the plan...")
    feedback, score = plangen.verify_plan(problem, plan, constraints)
    print(f"Verification score: {score}")
    print(f"Feedback: {feedback}")
    
    # Solve the problem (runs the complete workflow)
    print("\nSolving with the complete workflow...")
    result = plangen.solve(problem)
    
    # Print the selected solution
    print("\nSelected solution:")
    if isinstance(result.get("selected_solution"), dict):
        print(result["selected_solution"].get("selected_solution", "No solution found"))
        print("\nSelection reasoning:")
        print(result["selected_solution"].get("selection_reasoning", "No reasoning provided"))
    else:
        print(result.get("selected_solution", "No solution found"))
    
    # 2. Using specific algorithms
    print("\n\n[2] Using specific algorithms")
    print("-" * 50)
    
    # Create a PlanGen instance with OpenAI
    plangen = PlanGen.with_openai(model_name="gpt-4o")
    
    # Solve with BestOfN
    print("\nSolving with BestOfN algorithm...")
    best_of_n_result = plangen.solve(
        problem=problem,
        algorithm="best_of_n",
        n_plans=3,
        sampling_strategy="diverse"
    )
    print(f"BestOfN solution: {best_of_n_result.get('selected_solution', 'No solution found')}")
    
    # Solve with TreeOfThought
    print("\nSolving with TreeOfThought algorithm...")
    tot_result = plangen.solve(
        problem=problem,
        algorithm="tree_of_thought",
        max_depth=3,
        branching_factor=2
    )
    print(f"TreeOfThought solution: {tot_result.get('selected_solution', 'No solution found')}")
    
    # 3. Using a custom verifier
    print("\n\n[3] Using a custom verifier")
    print("-" * 50)
    
    # Create a calendar-specific verifier
    print("\nCreating a calendar-specific verifier...")
    calendar_verifier = Verifiers.calendar()
    
    # Solve with the custom verifier
    print("\nSolving with custom verifier...")
    verifier_result = plangen.solve(
        problem=problem,
        verifier=calendar_verifier
    )
    
    # Print the selected solution
    print("\nVerified solution:")
    if isinstance(verifier_result.get("selected_solution"), dict):
        print(verifier_result["selected_solution"].get("selected_solution", "No solution found"))
    else:
        print(verifier_result.get("selected_solution", "No solution found"))
    
    # 4. Visualizing results
    print("\n\n[4] Visualizing results")
    print("-" * 50)
    
    # Visualize the results from one of the algorithms
    print("\nGenerating visualization...")
    try:
        # Create visualization (only if matplotlib is installed)
        viz_path = Visualization.render_to_html(
            result=tot_result,
            output_path="tree_of_thought_visualization.html"
        )
        print(f"Visualization saved to: {viz_path}")
    except Exception as e:
        print(f"Could not create visualization: {e}")
    
    # Save the results to a file
    with open("public_api_results.json", "w") as f:
        json.dump({
            "default_result": result,
            "best_of_n_result": best_of_n_result,
            "tree_of_thought_result": tot_result,
            "verifier_result": verifier_result
        }, f, indent=2)
    print("\nResults saved to public_api_results.json")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        
        # Check if it's an API key error
        if "api_key" in str(e).lower() or "apikey" in str(e).lower():
            print("\nTIP: Make sure you have set the appropriate API keys in your .env file:")
            print("  - For OpenAI: OPENAI_API_KEY")
            print("  - For AWS Bedrock: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and AWS_REGION")