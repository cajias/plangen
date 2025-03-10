"""
Tests for the visualization module.
"""

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import networkx as nx

from plangen.visualization import GraphRenderer, Observable, PlanObserver


class TestObservable(unittest.TestCase):
    """Test cases for the Observable class."""

    def test_add_observer(self):
        """Test adding an observer to an observable."""
        observable = Observable()
        observer = MagicMock(spec=PlanObserver)

        observable.add_observer(observer)
        self.assertEqual(len(observable._observers), 1)
        self.assertEqual(observable._observers[0], observer)

    def test_remove_observer(self):
        """Test removing an observer from an observable."""
        observable = Observable()
        observer = MagicMock(spec=PlanObserver)

        observable.add_observer(observer)
        observable.remove_observer(observer)
        self.assertEqual(len(observable._observers), 0)

    def test_notify_observers(self):
        """Test notifying observers."""
        observable = Observable()
        observer1 = MagicMock(spec=PlanObserver)
        observer2 = MagicMock(spec=PlanObserver)

        observable.add_observer(observer1)
        observable.add_observer(observer2)

        data = {"key": "value"}
        observable.notify_observers(data)

        observer1.update.assert_called_once_with(data)
        observer2.update.assert_called_once_with(data)


class TestGraphRenderer(unittest.TestCase):
    """Test cases for the GraphRenderer class."""

    def setUp(self):
        """Set up test case."""
        self.temp_dir = tempfile.mkdtemp()
        self.renderer = GraphRenderer(output_dir=self.temp_dir, auto_render=False)

    def tearDown(self):
        """Clean up after test."""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_initialization(self):
        """Test initialization of GraphRenderer."""
        self.assertEqual(self.renderer.output_dir, self.temp_dir)
        self.assertFalse(self.renderer.auto_render)
        self.assertIsInstance(self.renderer.graph, nx.DiGraph)
        self.assertEqual(self.renderer.update_count, 0)

    def test_update_tree_of_thought_graph(self):
        """Test updating a Tree of Thought graph."""
        # Set algorithm type
        self.renderer.algorithm_type = "TreeOfThought"

        # Create test data for a node
        node_data = {
            "algorithm_type": "TreeOfThought",
            "event": "algorithm_start",
            "new_nodes": [
                {
                    "id": "node1",
                    "steps": ["step1", "step2"],
                    "score": 0.8,
                    "depth": 1,
                    "complete": False,
                }
            ],
        }

        # Update graph
        self.renderer.update(node_data)

        # Check graph structure
        self.assertEqual(len(self.renderer.graph.nodes), 1)
        self.assertIn("node1", self.renderer.graph.nodes)
        self.assertEqual(self.renderer.graph.nodes["node1"]["score"], 0.8)

    def test_update_rebase_graph(self):
        """Test updating a REBASE graph."""
        # Set algorithm type
        self.renderer.algorithm_type = "REBASE"

        # Create test data for an iteration
        iteration_data = {
            "algorithm_type": "REBASE",
            "event": "iteration",
            "iteration": 1,
            "plan": "This is a test plan",
            "score": 0.75,
            "feedback": "Good plan",
        }

        # Update graph
        self.renderer.update(iteration_data)

        # Check graph structure
        self.assertEqual(len(self.renderer.graph.nodes), 1)
        self.assertIn("iteration_1", self.renderer.graph.nodes)
        self.assertEqual(self.renderer.graph.nodes["iteration_1"]["score"], 0.75)

    def test_save_graph_data(self):
        """Test saving graph data to JSON."""
        # Add a node to the graph
        self.renderer.graph.add_node("test_node", test_attr="test_value")

        # Save the graph data
        filepath = self.renderer.save_graph_data(filename="test_graph.json")

        # Check that file exists
        self.assertTrue(os.path.exists(filepath))

    @patch("matplotlib.pyplot.savefig")
    @patch("matplotlib.pyplot.figure")
    def test_render(self, mock_figure, mock_savefig):
        """Test rendering the graph."""
        # Add a node to the graph
        self.renderer.graph.add_node("test_node", test_attr="test_value")

        # Set algorithm type
        self.renderer.algorithm_type = "TreeOfThought"

        # Mock the layout function to avoid graphviz dependency
        with patch(
            "networkx.nx_agraph.graphviz_layout",
            side_effect=lambda g, prog: {n: (i, i) for i, n in enumerate(g.nodes)},
        ):
            # Render the graph
            self.renderer.render(save=True, display=False, filename="test_graph.png")

        # Check that savefig was called
        mock_savefig.assert_called_once()

        # Check that figure was created
        mock_figure.assert_called_once()


if __name__ == "__main__":
    unittest.main()
