"""
Example of visualizing the BestOfN algorithm.

This script demonstrates how to use the visualization module to render the 
BestOfN algorithm's planning process.

This script also includes verification tests to ensure the observer pattern
is working correctly.
"""

import os
import unittest

from plangen.algorithms import BestOfN
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
    
    # Initialize BestOfN algorithm
    algorithm = BestOfN(
        n_plans=5,
        sampling_strategy="diverse",
        parallel=False,  # Sequential generation works better for visualization
        llm_interface=model
    )
    
    # Add the renderer as an observer
    algorithm.add_observer(renderer)
    
    # Define a simple planning problem
    problem_statement = """
    Design a project plan for launching a new mobile app. The app is 
    a social platform for fitness enthusiasts to share workout routines and 
    track progress together. Include milestones for design, development, 
    testing, and marketing.
    """
    
    # Run the algorithm (this will automatically update the renderer)
    best_plan, score, metadata = algorithm.run(problem_statement)
    
    # Create a final rendering
    renderer.render(save=True, display=True, filename="best_of_n_final.png")
    
    # Save the graph data as JSON
    data_file = renderer.save_graph_data(filename="best_of_n_data.json")
    
    # Print the results
    print(f"\nAlgorithm: BestOfN")
    print(f"Best plan score: {score}")
    print(f"Total plans generated: {metadata['n_plans']}")
    print(f"Sampling strategy: {metadata['sampling_strategy']}")
    print(f"Visualization saved to: {os.path.join(renderer.output_dir, 'best_of_n_final.png')}")
    print(f"Graph data saved to: {data_file}")

class TestObserverMock(PlanObserver):
    """Mock observer for testing."""
    
    def __init__(self):
        self.updates = []
    
    def update(self, plan_data):
        """Record updates."""
        self.updates.append(plan_data)

class BestOfNVisualizationTests(unittest.TestCase):
    """Tests for BestOfN visualization."""
    
    def test_observer_notifications(self):
        """Test that BestOfN sends proper observer notifications."""
        # Initialize algorithm without actual LLM to avoid API calls
        algorithm = BestOfN(n_plans=2)
        
        # Replace the actual methods with mocks
        algorithm.constraint_agent.run = lambda x: ["Test constraint 1", "Test constraint 2"]
        algorithm._basic_sampling = lambda x, y, z: "Sample plan"
        algorithm._verify_plan = lambda x, y, z: ("Good feedback", 80.0)
        
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
        self.assertIn("plan_generation_complete", event_types)
        self.assertIn("best_plan_selected", event_types)
        self.assertIn("algorithm_complete", event_types)
        
        # Check for algorithm type
        for update in observer.updates:
            self.assertEqual(update.get("algorithm_type"), "BestOfN")
            
        print("✅ BestOfN algorithm correctly implements observer notifications")

if __name__ == "__main__":
    # Run tests
    test_suite = unittest.TestLoader().loadTestsFromTestCase(BestOfNVisualizationTests)
    test_result = unittest.TextTestRunner().run(test_suite)
    
    # Only run the main visualization if tests pass
    if test_result.wasSuccessful():
        main()