"""
Example of visualizing the MixtureOfAlgorithms approach.

This script demonstrates how to use the visualization module to render the 
MixtureOfAlgorithms planning process, which dynamically selects and switches
between different planning algorithms.

This script also includes verification tests to ensure the observer pattern
is working correctly.
"""

import os
import unittest

from plangen.algorithms import MixtureOfAlgorithms, BaseAlgorithm
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
    
    # Initialize MixtureOfAlgorithms
    algorithm = MixtureOfAlgorithms(
        max_algorithm_switches=2,
        llm_interface=model
    )
    
    # Add the renderer as an observer
    algorithm.add_observer(renderer)
    
    # Define a complex planning problem that might benefit from algorithm switching
    problem_statement = """
    Plan a sustainable urban development project for a mid-sized city that aims to:
    1. Reduce carbon emissions by 30% within 5 years
    2. Improve public transportation accessibility
    3. Increase affordable housing by 20%
    4. Create green spaces accessible within a 10-minute walk for all residents
    5. Develop renewable energy sources to power 40% of the city's needs
    
    Your plan should include phased implementation, budget considerations, 
    stakeholder engagement strategies, and metrics for tracking success.
    """
    
    # Run the algorithm (this will automatically update the renderer)
    best_plan, score, metadata = algorithm.run(problem_statement)
    
    # Create a final rendering
    renderer.render(save=True, display=True, filename="mixture_of_algorithms_final.png")
    
    # Save the graph data as JSON
    data_file = renderer.save_graph_data(filename="mixture_of_algorithms_data.json")
    
    # Print the results
    print(f"\nAlgorithm: Mixture of Algorithms")
    print(f"Best plan score: {score}")
    print(f"Algorithm history: {metadata['algorithm_history']}")
    print(f"Visualization saved to: {os.path.join(renderer.output_dir, 'mixture_of_algorithms_final.png')}")
    print(f"Graph data saved to: {data_file}")

class TestObserverMock(PlanObserver):
    """Mock observer for testing."""
    
    def __init__(self):
        self.updates = []
    
    def update(self, plan_data):
        """Record updates."""
        self.updates.append(plan_data)

class MockChildAlgorithm(BaseAlgorithm):
    """Mock algorithm for testing."""
    
    def run(self, problem_statement):
        """Run the algorithm."""
        # Notify observers about algorithm execution
        self.notify_observers({
            "algorithm_type": "MockAlgorithm",
            "event": "mock_event",
            "data": "test data",
        })
        return "Mock plan", 75.0, {"mock_metadata": True}

class MixtureOfAlgorithmsVisualizationTests(unittest.TestCase):
    """Tests for MixtureOfAlgorithms visualization."""
    
    def test_observer_notifications(self):
        """Test that MixtureOfAlgorithms sends proper observer notifications."""
        # Initialize algorithm without actual LLM to avoid API calls
        algorithm = MixtureOfAlgorithms(max_algorithm_switches=1)
        
        # Replace the actual methods with mocks
        algorithm.constraint_agent.run = lambda x: ["Test constraint 1", "Test constraint 2"]
        algorithm._select_algorithm = lambda x, y: "REBASE"
        algorithm._select_next_algorithm = lambda v, w, x, y, z: "Best of N"
        
        # Replace algorithms with mocks
        algorithm.algorithms = {
            "REBASE": MockChildAlgorithm(),
            "Best of N": MockChildAlgorithm(),
        }
        
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
        self.assertIn("algorithm_selection", event_types)
        self.assertIn("algorithm_complete", event_types)
        
        # Check for delegated updates from child algorithms
        delegated_updates = [u for u in observer.updates if u.get("event") == "delegated_update"]
        self.assertGreater(len(delegated_updates), 0)
        
        # Check for algorithm type
        for update in observer.updates:
            if "algorithm_type" in update:
                self.assertIn(update.get("algorithm_type"), ["MixtureOfAlgorithms", "MockAlgorithm"])
            
        print("✅ MixtureOfAlgorithms correctly implements observer notifications")

if __name__ == "__main__":
    # Run tests
    test_suite = unittest.TestLoader().loadTestsFromTestCase(MixtureOfAlgorithmsVisualizationTests)
    test_result = unittest.TextTestRunner().run(test_suite)
    
    # Only run the main visualization if tests pass
    if test_result.wasSuccessful():
        main()