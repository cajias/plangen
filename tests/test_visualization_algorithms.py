"""
Tests for algorithm visualizations.

This module tests the visualization capabilities for different algorithms,
ensuring proper observer pattern implementation and graph rendering.
"""

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import networkx as nx

from plangen.algorithms import BestOfN, MixtureOfAlgorithms, REBASE, TreeOfThought
from plangen.visualization import GraphRenderer


class TestAlgorithmVisualizations(unittest.TestCase):
    """Test suite for algorithm visualizations."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for visualization outputs
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a renderer with auto_render disabled for tests
        self.renderer = GraphRenderer(
            output_dir=self.temp_dir,
            auto_render=False
        )
        
        # Create a mock LLM interface that returns predictable responses
        self.llm_mock = MagicMock()
        self.llm_mock.generate.return_value = "Mock plan output"
        
        # Mock constraint agent to return predictable constraints
        self.constraint_agent_mock = MagicMock()
        self.constraint_agent_mock.run.return_value = [
            "Constraint 1", 
            "Constraint 2"
        ]
        
        # Mock verification agent to return predictable scores
        self.verification_agent_mock = MagicMock()
        self.verification_agent_mock.run.return_value = ("Good plan", 75.0)
        
        # Sample problem statement for all tests
        self.problem_statement = "Plan a simple event."

    def tearDown(self):
        """Clean up after tests."""
        # Clean up temporary directory
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)

    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.close')
    def test_tree_of_thought_visualization(self, mock_close, mock_savefig):
        """Test visualization of TreeOfThought algorithm."""
        # Initialize algorithm with mocks
        algorithm = TreeOfThought(
            branching_factor=2,
            max_depth=2,
            beam_width=1,
            llm_interface=self.llm_mock,
            constraint_agent=self.constraint_agent_mock,
            verification_agent=self.verification_agent_mock
        )
        
        # Add renderer as observer
        algorithm.add_observer(self.renderer)
        
        # Run algorithm
        algorithm.run(self.problem_statement)
        
        # Verify graph was updated with correct algorithm type
        self.assertEqual(self.renderer.algorithm_type, "TreeOfThought")
        
        # Check that graph has nodes
        self.assertGreater(len(self.renderer.graph.nodes), 0)
        
        # Render the graph
        self.renderer.render(save=True, display=False)
        
        # Check that savefig was called
        mock_savefig.assert_called_once()
        mock_close.assert_called_once()

    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.close')
    def test_rebase_visualization(self, mock_close, mock_savefig):
        """Test visualization of REBASE algorithm."""
        # Initialize algorithm with mocks
        algorithm = REBASE(
            max_iterations=2,
            improvement_threshold=0.1,
            llm_interface=self.llm_mock,
            constraint_agent=self.constraint_agent_mock,
            verification_agent=self.verification_agent_mock
        )
        
        # Add renderer as observer
        algorithm.add_observer(self.renderer)
        
        # Run algorithm
        algorithm.run(self.problem_statement)
        
        # Verify graph was updated with correct algorithm type
        self.assertEqual(self.renderer.algorithm_type, "REBASE")
        
        # Check that graph has nodes
        self.assertGreater(len(self.renderer.graph.nodes), 0)
        
        # Check that nodes have expected attributes
        for node, attrs in self.renderer.graph.nodes(data=True):
            if node.startswith("iteration_"):
                self.assertIn("score", attrs)
                self.assertIn("feedback", attrs)
        
        # Render the graph
        self.renderer.render(save=True, display=False)
        
        # Check that savefig was called
        mock_savefig.assert_called_once()
        mock_close.assert_called_once()

    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.close')
    def test_best_of_n_visualization(self, mock_close, mock_savefig):
        """Test visualization of BestOfN algorithm."""
        # Initialize algorithm with mocks
        algorithm = BestOfN(
            n_plans=3,
            sampling_strategy="basic",
            llm_interface=self.llm_mock,
            constraint_agent=self.constraint_agent_mock,
            verification_agent=self.verification_agent_mock
        )
        
        # Add renderer as observer
        algorithm.add_observer(self.renderer)
        
        # Run algorithm
        algorithm.run(self.problem_statement)
        
        # Verify graph was updated with correct algorithm type
        self.assertEqual(self.renderer.algorithm_type, "BestOfN")
        
        # Check that graph has nodes
        self.assertGreater(len(self.renderer.graph.nodes), 0)
        
        # Check that central node exists
        self.assertIn("best_of_n_root", self.renderer.graph.nodes)
        
        # Check plan nodes have expected attributes
        plan_nodes = [n for n in self.renderer.graph.nodes if n.startswith("plan_")]
        self.assertGreaterEqual(len(plan_nodes), 1)
        
        for node in plan_nodes:
            attrs = self.renderer.graph.nodes[node]
            self.assertIn("score", attrs)
            self.assertIn("plan", attrs)
        
        # Render the graph
        self.renderer.render(save=True, display=False)
        
        # Check that savefig was called
        mock_savefig.assert_called_once()
        mock_close.assert_called_once()

    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.close')
    def test_mixture_of_algorithms_visualization(self, mock_close, mock_savefig):
        """Test visualization of MixtureOfAlgorithms approach."""
        # Initialize algorithm with mocks
        algorithm = MixtureOfAlgorithms(
            max_algorithm_switches=1,
            llm_interface=self.llm_mock,
            constraint_agent=self.constraint_agent_mock,
            verification_agent=self.verification_agent_mock
        )
        
        # Mock the _select_algorithm method to return a predictable result
        algorithm._select_algorithm = MagicMock(return_value="REBASE")
        algorithm._select_next_algorithm = MagicMock(return_value="Best of N")
        
        # Add renderer as observer
        algorithm.add_observer(self.renderer)
        
        # Run algorithm
        algorithm.run(self.problem_statement)
        
        # Verify graph was updated with correct algorithm type
        self.assertEqual(self.renderer.algorithm_type, "MixtureOfAlgorithms")
        
        # Check that graph has nodes
        self.assertGreater(len(self.renderer.graph.nodes), 0)
        
        # Check that algorithm selection nodes exist
        algo_nodes = [
            n for n, a in self.renderer.graph.nodes(data=True) 
            if a.get("type") == "algorithm"
        ]
        self.assertGreaterEqual(len(algo_nodes), 1)
        
        # Render the graph
        self.renderer.render(save=True, display=False)
        
        # Check that savefig was called
        mock_savefig.assert_called_once()
        mock_close.assert_called_once()

    def test_save_graph_data(self):
        """Test saving graph data as JSON."""
        # Initialize algorithm with mocks
        algorithm = TreeOfThought(
            branching_factor=2,
            max_depth=2,
            beam_width=1,
            llm_interface=self.llm_mock,
            constraint_agent=self.constraint_agent_mock,
            verification_agent=self.verification_agent_mock
        )
        
        # Add renderer as observer
        algorithm.add_observer(self.renderer)
        
        # Run algorithm
        algorithm.run(self.problem_statement)
        
        # Save graph data
        file_path = self.renderer.save_graph_data(filename="test_data.json")
        
        # Check that file exists
        self.assertTrue(os.path.exists(file_path))
        
        # Check file has non-zero size
        self.assertGreater(os.path.getsize(file_path), 0)


if __name__ == "__main__":
    unittest.main()