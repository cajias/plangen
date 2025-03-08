"""
Integration tests for all PlanGEN algorithms
"""

import os
import pytest
from unittest.mock import MagicMock, patch

from plangen.algorithms.best_of_n import BestOfN
from plangen.algorithms.tree_of_thought import TreeOfThought
from plangen.algorithms.rebase import REBASE
from plangen.algorithms.mixture_of_algorithms import MixtureOfAlgorithms
from plangen.utils.llm_interface import LLMInterface
from plangen.agents.constraint_agent import ConstraintAgent
from plangen.agents.verification_agent import VerificationAgent
from plangen.agents.selection_agent import SelectionAgent


@pytest.mark.skipif(
    "OPENAI_API_KEY" not in os.environ,
    reason="OPENAI_API_KEY environment variable not set",
)
class TestAllAlgorithmsIntegration:
    """Integration tests for all PlanGEN algorithms."""
    
    def setup_method(self):
        """Set up common test components."""
        # Create mock LLM interface
        self.mock_llm = MagicMock(spec=LLMInterface)
        
        # Create mock verifier
        self.mock_verifier = MagicMock()
        self.mock_verifier.extract_domain_constraints.return_value = []
        
        # Create agents
        self.constraint_agent = ConstraintAgent(llm_interface=self.mock_llm)
        self.verification_agent = VerificationAgent(
            llm_interface=self.mock_llm, 
            verifier=self.mock_verifier
        )
        self.selection_agent = MagicMock()
        
        # Define a simple problem
        self.problem = """
        Design a function to find the maximum sum of a contiguous subarray within an array of integers.
        For example, given the array [-2, 1, -3, 4, -1, 2, 1, -5, 4], the contiguous subarray with the
        largest sum is [4, -1, 2, 1], with a sum of 6.
        """
    
    def test_tree_of_thought_algorithm(self):
        """Test Tree of Thought algorithm with a simple problem."""
        # Mock responses for constraint extraction
        self.mock_llm.generate.side_effect = [
            # Constraint extraction
            """
            1. Function must find maximum sum of contiguous subarray
            2. Function should handle negative numbers
            3. Function should return the sum value
            """,
            # First level exploration
            "Consider Kadane's algorithm",
            "Consider brute force approach",
            # Second level exploration from Kadane's
            "Implement Kadane's algorithm with O(n) time complexity",
            "Implement Kadane's with additional space for tracking indices",
            # Verification
            "Valid solution with optimal time complexity"
        ]
        
        # Mock verification scores
        self.mock_verifier.verify_solution.side_effect = [
            {"is_valid": True, "score": 95, "reason": "Optimal solution"}
        ]
        
        # Create Tree of Thought algorithm
        tot = TreeOfThought(
            llm_interface=self.mock_llm,
            constraint_agent=self.constraint_agent,
            verification_agent=self.verification_agent,
            branching_factor=2,
            max_depth=2,
            beam_width=1
        )
        
        # Patch the _explore_node method to control the exploration
        with patch.object(tot, '_explore_node') as mock_explore:
            # Set up the mock to simulate tree exploration
            mock_explore.side_effect = [
                # First level exploration
                [
                    {"steps": ["Consider Kadane's algorithm"], "score": 70, "depth": 1, "complete": False},
                    {"steps": ["Consider brute force approach"], "score": 40, "depth": 1, "complete": False}
                ],
                # Second level exploration from Kadane's
                [
                    {"steps": ["Consider Kadane's algorithm", "Implement Kadane's algorithm with O(n) time complexity"], 
                     "score": 95, "depth": 2, "complete": True}
                ]
            ]
            
            # Run the algorithm
            best_plan, best_score, metadata = tot.run(self.problem)
        
        # Verify the results
        assert "Kadane's algorithm" in best_plan
        assert best_score == 95
        assert metadata["algorithm"] == "tree_of_thought"
        assert metadata["max_depth"] == 2
        assert metadata["branching_factor"] == 2
    
    def test_rebase_algorithm(self):
        """Test REBASE algorithm with a simple problem."""
        # Mock responses
        self.mock_llm.generate.side_effect = [
            # Constraint extraction
            """
            1. Function must find maximum sum of contiguous subarray
            2. Function should handle negative numbers
            3. Function should return the sum value
            """,
            # Initial plan
            "Initial solution using brute force approach",
            # First refinement
            "Improved solution using Kadane's algorithm",
            # Second refinement
            "Optimized Kadane's algorithm with O(1) space complexity"
        ]
        
        # Mock verification scores with increasing scores
        self.mock_verifier.verify_solution.side_effect = [
            {"is_valid": True, "score": 60, "reason": "Works but inefficient"},
            {"is_valid": True, "score": 85, "reason": "Good algorithm choice"},
            {"is_valid": True, "score": 95, "reason": "Optimal solution"}
        ]
        
        # Create REBASE algorithm
        rebase = REBASE(
            llm_interface=self.mock_llm,
            constraint_agent=self.constraint_agent,
            verification_agent=self.verification_agent,
            max_iterations=3,
            improvement_threshold=0.05
        )
        
        # Run the algorithm
        best_plan, best_score, metadata = rebase.run(self.problem)
        
        # Verify the results
        assert "Optimized Kadane's algorithm" in best_plan
        assert best_score == 95
        assert metadata["algorithm"] == "rebase"
        assert len(metadata["iterations"]) == 3
        assert metadata["iterations"][0]["score"] == 60
        assert metadata["iterations"][2]["score"] == 95
    
    def test_mixture_of_algorithms(self):
        """Test Mixture of Algorithms with a simple problem."""
        # Mock algorithm selection
        self.mock_llm.generate.side_effect = [
            # Constraint extraction
            """
            1. Function must find maximum sum of contiguous subarray
            2. Function should handle negative numbers
            3. Function should return the sum value
            """,
            # Algorithm selection
            "Tree of Thought"
        ]
        
        # Create mock algorithms
        mock_best_of_n = MagicMock(spec=BestOfN)
        mock_tree_of_thought = MagicMock(spec=TreeOfThought)
        mock_rebase = MagicMock(spec=REBASE)
        
        # Set up the mock Tree of Thought to return a good plan
        mock_tree_of_thought.run.return_value = (
            "Solution using Kadane's algorithm", 
            95.0, 
            {"algorithm": "tree_of_thought"}
        )
        
        # Mock selection agent
        mock_selection_agent = MagicMock(spec=SelectionAgent)
        mock_selection_agent.select_algorithm.return_value = "Tree of Thought"
        
        # Create Mixture of Algorithms
        moa = MixtureOfAlgorithms(
            llm_interface=self.mock_llm,
            constraint_agent=self.constraint_agent,
            verification_agent=self.verification_agent,
            selection_agent=mock_selection_agent,
            max_algorithm_switches=2
        )
        
        # Replace the algorithms with mocks
        moa.algorithms = {
            "Best of N": mock_best_of_n,
            "Tree of Thought": mock_tree_of_thought,
            "REBASE": mock_rebase
        }
        
        # Run the algorithm
        best_plan, best_score, metadata = moa.run(self.problem)
        
        # Verify the results
        assert best_plan == "Solution using Kadane's algorithm"
        assert best_score == 95.0
        assert metadata["algorithm"] == "mixture_of_algorithms"
        assert metadata["selected_algorithm"] == "Tree of Thought"
        
        # Verify the selection agent was called
        mock_selection_agent.select_algorithm.assert_called_once()
        
        # Verify the selected algorithm was run
        mock_tree_of_thought.run.assert_called_once_with(self.problem)