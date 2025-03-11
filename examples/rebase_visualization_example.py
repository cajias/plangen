"""
Example of visualizing the REBASE algorithm.

This script demonstrates how to use the visualization module to render the 
REBASE algorithm's planning process.

This script also includes verification tests to ensure the observer pattern
is working correctly.
"""

import os
import unittest

from plangen.algorithms import REBASE
from plangen.models import OpenAIModelInterface 
from plangen.visualization import GraphRenderer, PlanObserver

# Skip loading dotenv for testing
# Try to load dotenv if available for main execution
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("dotenv not available, skipping .env loading")

# Initialize model interface
model = OpenAIModelInterface(model_name="gpt-4o")

# Create a visualization directory
os.makedirs("./visualizations", exist_ok=True)

def main():
    # Initialize the graph renderer
    renderer = GraphRenderer(
        output_dir="./visualizations", 
        auto_render=True,
        render_format="png"
    )
    
    # Initialize REBASE algorithm
    algorithm = REBASE(
        max_iterations=3,
        improvement_threshold=0.1,
        llm_interface=model
    )
    
    # Add the renderer as an observer
    algorithm.add_observer(renderer)
    
    # Define a simple planning problem
    problem_statement = """
    Plan a three-day conference for 100 software engineers. 
    The conference should include keynote speeches, technical workshops, 
    networking sessions, and social events.
    """
    
    # Run the algorithm (this will automatically update the renderer)
    best_plan, score, metadata = algorithm.run(problem_statement)
    
    # Create a final rendering
    renderer.render(save=True, display=True, filename="rebase_final.png")
    
    # Save the graph data as JSON
    data_file = renderer.save_graph_data(filename="rebase_data.json")
    
    # Print the results
    print(f"\nAlgorithm: REBASE")
    print(f"Best plan score: {score}")
    print(f"Total iterations: {len(metadata['iterations']) - 1}")
    print(f"Visualization saved to: {os.path.join(renderer.output_dir, 'rebase_final.png')}")
    print(f"Graph data saved to: {data_file}")

class TestObserverMock(PlanObserver):
    """Mock observer for testing."""
    
    def __init__(self):
        self.updates = []
    
    def update(self, plan_data):
        """Record updates."""
        self.updates.append(plan_data)

class REBASEVisualizationTests(unittest.TestCase):
    """Tests for REBASE visualization."""
    
    def test_observer_notifications(self):
        """Test that REBASE sends proper observer notifications."""
        # Initialize algorithm without actual LLM to avoid API calls
        algorithm = REBASE(max_iterations=2)
        
        # Replace the actual methods with mocks
        algorithm.constraint_agent.run = lambda x: ["Test constraint 1", "Test constraint 2"]
        algorithm._generate_initial_plan = lambda x, y: "Initial plan"
        algorithm._verify_plan = lambda x, y, z: ("Good feedback", 70.0)
        algorithm._refine_plan = lambda w, x, y, z: "Refined plan"
        
        # Add observer
        observer = TestObserverMock()
        algorithm.add_observer(observer)
        
        # Run algorithm
        algorithm.run("Test problem")
        
        # Check notifications
        self.assertGreater(len(observer.updates), 0)
        
        # Check for key event types
        event_types = [update.get("event") for update in observer.updates if "event" in update]
        self.assertIn("algorithm_start", event_types)
        self.assertIn("initial_plan", event_types)
        
        # Check for algorithm type
        for update in observer.updates:
            self.assertEqual(update.get("algorithm_type"), "REBASE")
            
        print("✅ REBASE algorithm correctly implements observer notifications")

if __name__ == "__main__":
    # Check for test mode flag
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Run only tests
        unittest.main(argv=['first-arg-is-ignored'])
    else:
        # Run tests
        test_suite = unittest.TestLoader().loadTestsFromTestCase(REBASEVisualizationTests)
        test_result = unittest.TextTestRunner().run(test_suite)
        
        # Only run the main visualization if tests pass
        if test_result.wasSuccessful():
            main()