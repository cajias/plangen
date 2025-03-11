"""
Integration tests for the PlanGEN public API.
"""

import os
import pytest
from unittest.mock import MagicMock, patch

from plangen import PlanGen, Algorithm, Visualization, Verifiers


class TestPlanGenIntegration:
    """Integration tests for the PlanGen class."""
    
    @pytest.mark.skipif(not os.environ.get("INTEGRATION_TESTS"), reason="Integration tests disabled")
    def test_api_workflow_full(self):
        """Test the full API workflow with multiple components."""
        # This is a full integration test and will not run by default
        # Set INTEGRATION_TESTS=1 to run this test
        
        # Setup
        problem = """
        Schedule a 30-minute meeting for 3 people: Alice, Bob, and Charlie.
        Alice is available from 9:00-11:00 and 14:00-16:00.
        Bob is available from 10:00-12:00 and 15:00-17:00.
        Charlie is available from 9:00-10:30 and 15:30-17:00.
        Find an earliest time slot that works for all participants.
        """
        
        # Create PlanGen with mock LLM to avoid actual API calls
        with patch("plangen.api.OpenAIModelInterface") as mock_openai:
            # Mock the model interface
            mock_model = MagicMock()
            mock_model.generate.return_value = "10:00-10:30"
            mock_openai.return_value = mock_model
            
            # Create PlanGen instance
            plangen = PlanGen.with_openai(model_name="gpt-4o")
            
            # Mock the constraint agent
            mock_constraint_agent = MagicMock()
            mock_constraint_agent.extract_constraints.return_value = [
                "30-minute meeting",
                "Alice is available from 9:00-11:00 and 14:00-16:00",
                "Bob is available from 10:00-12:00 and 15:00-17:00",
                "Charlie is available from 9:00-10:30 and 15:30-17:00"
            ]
            plangen._plangen.constraint_agent = mock_constraint_agent
            
            # Mock the solution agent
            mock_solution_agent = MagicMock()
            mock_solution_agent.generate_solutions.return_value = ["10:00-10:30", "15:30-16:00"]
            plangen._plangen.solution_agent = mock_solution_agent
            
            # Mock the verification agent
            mock_verification_agent = MagicMock()
            mock_verification_agent.verify_solution.return_value = {
                "feedback": "Valid solution",
                "score": 0.9
            }
            plangen._plangen.verification_agent = mock_verification_agent
            
            # Mock the selection agent
            mock_selection_agent = MagicMock()
            mock_selection_agent.select_solution.return_value = {
                "selected_solution": "10:00-10:30",
                "selection_reasoning": "This is the earliest valid time slot"
            }
            plangen._plangen.selection_agent = mock_selection_agent
            
            # Execute the workflow
            
            # 1. Extract constraints
            constraints = plangen.extract_constraints(problem)
            assert constraints == [
                "30-minute meeting",
                "Alice is available from 9:00-11:00 and 14:00-16:00",
                "Bob is available from 10:00-12:00 and 15:00-17:00",
                "Charlie is available from 9:00-10:30 and 15:30-17:00"
            ]
            
            # 2. Generate a plan
            plan = plangen.generate_plan(problem)
            assert plan == "10:00-10:30"
            
            # 3. Verify the plan
            feedback, score = plangen.verify_plan(problem, plan)
            assert feedback == "Valid solution"
            assert score == 0.9
            
            # 4. Solve the problem
            result = plangen.solve(problem)
            assert result["selected_solution"]["selected_solution"] == "10:00-10:30"
    
    @patch("plangen.api.LLMInterface")
    def test_api_algorithm_integration(self, mock_llm):
        """Test the API with different algorithms."""
        # Setup
        mock_model = MagicMock()
        mock_llm.return_value = mock_model
        
        problem = "Find the best algorithm to sort a list of integers."
        
        # Test with BestOfN
        with patch("plangen.api.BestOfN") as mock_best_of_n:
            mock_algorithm = MagicMock()
            mock_algorithm.run.return_value = ("Quick Sort", 0.9, {"steps": ["Step 1", "Step 2"]})
            mock_best_of_n.return_value = mock_algorithm
            
            # Create PlanGen and solve with BestOfN
            plangen = PlanGen.create()
            result = plangen.solve(problem, algorithm="best_of_n", n_plans=3)
            
            assert result["selected_solution"] == "Quick Sort"
            assert result["score"] == 0.9
            assert result["metadata"] == {"steps": ["Step 1", "Step 2"]}
        
        # Test with TreeOfThought
        with patch("plangen.api.TreeOfThought") as mock_tot:
            mock_algorithm = MagicMock()
            mock_algorithm.run.return_value = ("Merge Sort", 0.95, {"tree_nodes": 5})
            mock_tot.return_value = mock_algorithm
            
            # Create PlanGen and solve with TreeOfThought
            plangen = PlanGen.create()
            result = plangen.solve(problem, algorithm="tree_of_thought", max_depth=3)
            
            assert result["selected_solution"] == "Merge Sort"
            assert result["score"] == 0.95
            assert result["metadata"] == {"tree_nodes": 5}
    
    @patch("plangen.api.GraphRenderer")
    def test_visualization_integration(self, mock_renderer):
        """Test the visualization API integration."""
        # Setup
        mock_instance = MagicMock()
        mock_instance.render_html.return_value = "/path/to/output.html"
        mock_renderer.return_value = mock_instance
        
        # Create sample result
        result = {
            "problem": "Test problem",
            "selected_solution": "Solution",
            "score": 0.9,
            "metadata": {
                "steps": ["Step 1", "Step 2"],
                "path": [{"node": "A"}, {"node": "B"}]
            }
        }
        
        # Test rendering to HTML
        output_path = Visualization.render_to_html(result)
        assert output_path == "/path/to/output.html"
        mock_instance.render_html.assert_called_once()
    
    @patch("plangen.api.CalendarVerifier")
    def test_verifier_integration(self, mock_calendar_verifier):
        """Test the verifier API integration."""
        # Setup
        mock_verifier = MagicMock()
        mock_verifier.verify.return_value = ("Good solution", 0.85)
        mock_calendar_verifier.return_value = mock_verifier
        
        problem = """
        Schedule a meeting for Alice and Bob.
        Alice is free from 9:00-10:00 and 11:00-12:00.
        Bob is free from 9:30-10:30 and 11:30-12:30.
        """
        solution = "9:30-10:00"
        
        # Extract constraints
        constraints = [
            "Alice is free from 9:00-10:00 and 11:00-12:00",
            "Bob is free from 9:30-10:30 and 11:30-12:30"
        ]
        
        # Create verifier
        verifier = Verifiers.calendar()
        
        # Verify solution
        feedback, score = verifier.verify(problem, constraints, solution)
        
        assert feedback == "Good solution"
        assert score == 0.85
        mock_verifier.verify.assert_called_once_with(problem, constraints, solution)