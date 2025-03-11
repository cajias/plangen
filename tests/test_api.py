"""
Tests for the public API in plangen/api.py.
"""

import pytest
from unittest.mock import MagicMock, patch

from plangen import PlanGen, Algorithm, Visualization, Verifiers
from plangen.api import (
    PlanType, ScoreType, ConstraintType, FeedbackType, MetadataType, PlanResultType,
    ModelProtocol, VerifierProtocol
)


class TestPlanGen:
    """Tests for the PlanGen class in the public API."""

    @patch("plangen.api.LLMInterface")
    def test_create_default(self, mock_llm):
        """Test creating a PlanGen instance with default parameters."""
        # Setup
        mock_llm.return_value = MagicMock()
        
        # Execute
        plangen = PlanGen.create()
        
        # Assert
        assert plangen is not None
        mock_llm.assert_called_once()
        assert isinstance(plangen._plangen, object)

    @patch("plangen.api.OpenAIModelInterface")
    def test_with_openai(self, mock_openai):
        """Test creating a PlanGen instance with OpenAI model."""
        # Setup
        mock_openai.return_value = MagicMock()
        
        # Execute
        plangen = PlanGen.with_openai(model_name="gpt-4o")
        
        # Assert
        assert plangen is not None
        mock_openai.assert_called_once_with(model_name="gpt-4o")
        assert isinstance(plangen._plangen, object)

    @patch("plangen.api.BedrockModelInterface")
    def test_with_bedrock(self, mock_bedrock):
        """Test creating a PlanGen instance with Bedrock model."""
        # Setup
        mock_bedrock.return_value = MagicMock()
        
        # Execute
        plangen = PlanGen.with_bedrock(model_id="anthropic.claude-3-sonnet-20240229-v1:0")
        
        # Assert
        assert plangen is not None
        mock_bedrock.assert_called_once_with(model_id="anthropic.claude-3-sonnet-20240229-v1:0", region="us-east-1")
        assert isinstance(plangen._plangen, object)

    def test_with_model(self):
        """Test creating a PlanGen instance with a custom model."""
        # Setup
        mock_model = MagicMock(spec=ModelProtocol)
        
        # Execute
        plangen = PlanGen.with_model(mock_model)
        
        # Assert
        assert plangen is not None
        assert isinstance(plangen._plangen, object)

    def test_solve_default(self):
        """Test solving a problem with the default algorithm."""
        # Setup
        mock_plangen = MagicMock()
        mock_plangen.solve.return_value = {"result": "success"}
        plangen = PlanGen(mock_plangen)
        
        # Execute
        result = plangen.solve("test problem")
        
        # Assert
        assert result == {"result": "success"}
        mock_plangen.solve.assert_called_once_with("test problem")

    @patch("plangen.api.Algorithm.create")
    def test_solve_with_algorithm(self, mock_algorithm_create):
        """Test solving a problem with a specific algorithm."""
        # Setup
        mock_algorithm = MagicMock()
        mock_algorithm.run.return_value = ("best plan", 0.95, {"metadata": "value"})
        mock_algorithm_create.return_value = mock_algorithm
        
        mock_plangen = MagicMock()
        plangen = PlanGen(mock_plangen)
        
        # Execute
        result = plangen.solve("test problem", algorithm="best_of_n", n_plans=5)
        
        # Assert
        assert result == {
            "problem": "test problem",
            "selected_solution": "best plan",
            "score": 0.95,
            "metadata": {"metadata": "value"}
        }
        mock_algorithm_create.assert_called_once()
        mock_algorithm.run.assert_called_once_with("test problem")

    def test_extract_constraints(self):
        """Test extracting constraints from a problem."""
        # Setup
        mock_plangen = MagicMock()
        mock_constraint_agent = MagicMock()
        mock_constraint_agent.extract_constraints.return_value = ["constraint1", "constraint2"]
        mock_plangen.constraint_agent = mock_constraint_agent
        plangen = PlanGen(mock_plangen)
        
        # Execute
        constraints = plangen.extract_constraints("test problem")
        
        # Assert
        assert constraints == ["constraint1", "constraint2"]
        mock_constraint_agent.extract_constraints.assert_called_once_with("test problem")

    def test_generate_plan(self):
        """Test generating a plan."""
        # Setup
        mock_plangen = MagicMock()
        mock_solution_agent = MagicMock()
        mock_solution_agent.generate_solutions.return_value = ["solution1"]
        mock_plangen.solution_agent = mock_solution_agent
        mock_plangen.constraint_agent.extract_constraints.return_value = ["constraint1"]
        plangen = PlanGen(mock_plangen)
        
        # Execute
        plan = plangen.generate_plan("test problem")
        
        # Assert
        assert plan == "solution1"
        mock_solution_agent.generate_solutions.assert_called_once()

    def test_verify_plan_with_default_verifier(self):
        """Test verifying a plan with the default verifier."""
        # Setup
        mock_plangen = MagicMock()
        mock_verification_agent = MagicMock()
        mock_verification_agent.verify_solution.return_value = {
            "feedback": "Good plan",
            "score": 0.8
        }
        mock_plangen.verification_agent = mock_verification_agent
        mock_plangen.constraint_agent.extract_constraints.return_value = ["constraint1"]
        plangen = PlanGen(mock_plangen)
        
        # Execute
        feedback, score = plangen.verify_plan("test problem", "test plan")
        
        # Assert
        assert feedback == "Good plan"
        assert score == 0.8
        mock_verification_agent.verify_solution.assert_called_once()

    def test_verify_plan_with_custom_verifier(self):
        """Test verifying a plan with a custom verifier."""
        # Setup
        mock_plangen = MagicMock()
        mock_verifier = MagicMock(spec=VerifierProtocol)
        mock_verifier.verify.return_value = ("Custom feedback", 0.9)
        mock_plangen.constraint_agent.extract_constraints.return_value = ["constraint1"]
        plangen = PlanGen(mock_plangen)
        
        # Execute
        feedback, score = plangen.verify_plan("test problem", "test plan", verifier=mock_verifier)
        
        # Assert
        assert feedback == "Custom feedback"
        assert score == 0.9
        mock_verifier.verify.assert_called_once_with("test problem", ["constraint1"], "test plan")


class TestAlgorithm:
    """Tests for the Algorithm class in the public API."""

    @patch("plangen.api.BestOfN")
    def test_create_best_of_n(self, mock_best_of_n):
        """Test creating a BestOfN algorithm."""
        # Setup
        mock_best_of_n.return_value = MagicMock()
        mock_model = MagicMock(spec=ModelProtocol)
        
        # Execute
        algorithm = Algorithm.create(
            algorithm_type="best_of_n",
            model=mock_model,
            n_plans=5,
            sampling_strategy="diverse"
        )
        
        # Assert
        assert algorithm is not None
        mock_best_of_n.assert_called_once()

    @patch("plangen.api.TreeOfThought")
    def test_create_tree_of_thought(self, mock_tot):
        """Test creating a TreeOfThought algorithm."""
        # Setup
        mock_tot.return_value = MagicMock()
        mock_model = MagicMock(spec=ModelProtocol)
        
        # Execute
        algorithm = Algorithm.create(
            algorithm_type="tree_of_thought",
            model=mock_model,
            max_depth=5,
            branching_factor=3
        )
        
        # Assert
        assert algorithm is not None
        mock_tot.assert_called_once()

    @patch("plangen.api.REBASE")
    def test_create_rebase(self, mock_rebase):
        """Test creating a REBASE algorithm."""
        # Setup
        mock_rebase.return_value = MagicMock()
        mock_model = MagicMock(spec=ModelProtocol)
        
        # Execute
        algorithm = Algorithm.create(
            algorithm_type="rebase",
            model=mock_model,
            max_iterations=5
        )
        
        # Assert
        assert algorithm is not None
        mock_rebase.assert_called_once()

    @patch("plangen.api.MixtureOfAlgorithms")
    def test_create_mixture(self, mock_mixture):
        """Test creating a MixtureOfAlgorithms algorithm."""
        # Setup
        mock_mixture.return_value = MagicMock()
        mock_model = MagicMock(spec=ModelProtocol)
        
        # Execute
        algorithm = Algorithm.create(
            algorithm_type="mixture",
            model=mock_model,
            max_algorithm_switches=2
        )
        
        # Assert
        assert algorithm is not None
        mock_mixture.assert_called_once()

    def test_run(self):
        """Test running an algorithm."""
        # Setup
        mock_algorithm = MagicMock()
        mock_algorithm.run.return_value = ("best plan", 0.9, {"metadata": "value"})
        algorithm = Algorithm(mock_algorithm)
        
        # Execute
        result = algorithm.run("test problem")
        
        # Assert
        assert result == ("best plan", 0.9, {"metadata": "value"})
        mock_algorithm.run.assert_called_once_with("test problem")


class TestVisualization:
    """Tests for the Visualization class in the public API."""

    @patch("plangen.api.GraphRenderer")
    def test_create_graph_png(self, mock_renderer):
        """Test creating a PNG visualization."""
        # Setup
        mock_instance = MagicMock()
        mock_instance.render_png.return_value = "/path/to/output.png"
        mock_renderer.return_value = mock_instance
        
        # Execute
        result = Visualization.create_graph(
            result={"metadata": {"data": "value"}},
            output_format="png"
        )
        
        # Assert
        assert result == "/path/to/output.png"
        mock_instance.render_png.assert_called_once()

    @patch("plangen.api.GraphRenderer")
    def test_create_graph_svg(self, mock_renderer):
        """Test creating an SVG visualization."""
        # Setup
        mock_instance = MagicMock()
        mock_instance.render_svg.return_value = "/path/to/output.svg"
        mock_renderer.return_value = mock_instance
        
        # Execute
        result = Visualization.create_graph(
            result={"metadata": {"data": "value"}},
            output_format="svg"
        )
        
        # Assert
        assert result == "/path/to/output.svg"
        mock_instance.render_svg.assert_called_once()

    @patch("plangen.api.GraphRenderer")
    def test_create_graph_html(self, mock_renderer):
        """Test creating an HTML visualization."""
        # Setup
        mock_instance = MagicMock()
        mock_instance.render_html.return_value = "/path/to/output.html"
        mock_renderer.return_value = mock_instance
        
        # Execute
        result = Visualization.create_graph(
            result={"metadata": {"data": "value"}},
            output_format="html"
        )
        
        # Assert
        assert result == "/path/to/output.html"
        mock_instance.render_html.assert_called_once()

    @patch("plangen.api.Visualization.create_graph")
    def test_render_to_html(self, mock_create_graph):
        """Test rendering to HTML."""
        # Setup
        mock_create_graph.return_value = "/path/to/output.html"
        
        # Execute
        result = Visualization.render_to_html(
            result={"metadata": {"data": "value"}}
        )
        
        # Assert
        assert result == "/path/to/output.html"
        mock_create_graph.assert_called_once_with(
            {"metadata": {"data": "value"}},
            output_format="html",
            output_path=None
        )


class TestVerifiers:
    """Tests for the Verifiers class in the public API."""

    @patch("plangen.api.CalendarVerifier")
    def test_calendar_verifier(self, mock_calendar_verifier):
        """Test creating a calendar verifier."""
        # Setup
        mock_calendar_verifier.return_value = MagicMock(spec=VerifierProtocol)
        
        # Execute
        verifier = Verifiers.calendar()
        
        # Assert
        assert verifier is not None
        mock_calendar_verifier.assert_called_once()

    @patch("plangen.api.MathVerifier")
    def test_math_verifier(self, mock_math_verifier):
        """Test creating a math verifier."""
        # Setup
        mock_math_verifier.return_value = MagicMock(spec=VerifierProtocol)
        
        # Execute
        verifier = Verifiers.math()
        
        # Assert
        assert verifier is not None
        mock_math_verifier.assert_called_once()

    @patch("plangen.api.BaseVerifier")
    def test_custom_verifier(self, mock_base_verifier):
        """Test creating a custom verifier."""
        # Setup
        mock_base_verifier.return_value = MagicMock(spec=VerifierProtocol)
        mock_verify_function = MagicMock(return_value=("feedback", 0.9))
        
        # Execute
        verifier = Verifiers.custom(verify_function=mock_verify_function)
        
        # Assert
        assert verifier is not None
        # BaseVerifier should have been subclassed with a custom verify method
        assert mock_base_verifier.call_count >= 1