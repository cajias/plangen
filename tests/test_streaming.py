"""Tests for streaming functionality."""

from unittest.mock import MagicMock, patch

from plangen import PlanGEN
from plangen.api import PlanGen
from plangen.models import OpenAIModelInterface


class TestModelStreaming:
    """Tests for model-level streaming."""

    def test_base_model_generate_stream_fallback(self):
        """Test that base model streaming falls back to non-streaming generate."""
        # Create a concrete test class that uses the default implementation
        from plangen.models.base_model import BaseModelInterface

        class TestModel(BaseModelInterface):
            def generate(
                self, prompt, system_message=None, temperature=None, max_tokens=None
            ):
                return "Complete response"

            def batch_generate(
                self, prompts, system_message=None, temperature=None, max_tokens=None
            ):
                return [self.generate(p) for p in prompts]

        # Create instance and test
        model = TestModel()
        result_chunks = list(model.generate_stream("Test prompt"))

        # Should have yielded the complete response
        assert len(result_chunks) == 1
        assert result_chunks[0] == "Complete response"

    @patch("plangen.models.openai_model.OpenAI")
    def test_openai_generate_stream(self, mock_openai_class):
        """Test OpenAI streaming generation."""
        # Setup mock
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        # Create mock stream response
        mock_chunk_1 = MagicMock()
        mock_chunk_1.choices = [MagicMock()]
        mock_chunk_1.choices[0].delta.content = "Hello "

        mock_chunk_2 = MagicMock()
        mock_chunk_2.choices = [MagicMock()]
        mock_chunk_2.choices[0].delta.content = "world"

        mock_chunk_3 = MagicMock()
        mock_chunk_3.choices = [MagicMock()]
        mock_chunk_3.choices[0].delta.content = None  # End of stream

        mock_client.chat.completions.create.return_value = [
            mock_chunk_1,
            mock_chunk_2,
            mock_chunk_3,
        ]

        # Create model and test streaming
        model = OpenAIModelInterface(
            model_name="gpt-4o",
            api_key="test-key",
        )

        chunks = list(model.generate_stream("Test prompt"))

        # Verify chunks
        assert len(chunks) == 2
        assert chunks[0] == "Hello "
        assert chunks[1] == "world"

        # Verify API call
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]["stream"] is True


class TestPlanGENStreaming:
    """Tests for PlanGEN-level streaming."""

    def test_solve_stream_complete_workflow(self):
        """Test complete workflow streaming."""
        # Setup mocks
        mock_model = MagicMock()
        mock_prompt_manager = MagicMock()
        mock_constraint_agent = MagicMock()
        mock_solution_agent = MagicMock()
        mock_verification_agent = MagicMock()
        mock_selection_agent = MagicMock()

        # Configure mock responses
        mock_constraint_agent.extract_constraints.return_value = "Test constraints"
        mock_solution_agent.generate_solutions.return_value = [
            "Solution 1",
            "Solution 2",
        ]
        mock_verification_agent.verify_solutions.return_value = [
            "Verification 1",
            "Verification 2",
        ]
        mock_selection_agent.select_best_solution.return_value = {
            "selected_solution": "Solution 1",
            "score": 0.95,
        }

        # Create PlanGEN instance
        plangen = PlanGEN(
            model=mock_model,
            prompt_manager=mock_prompt_manager,
            num_solutions=2,
        )

        # Replace agents with mocks
        plangen.constraint_agent = mock_constraint_agent
        plangen.solution_agent = mock_solution_agent
        plangen.verification_agent = mock_verification_agent
        plangen.selection_agent = mock_selection_agent

        # Test streaming
        problem = "Test problem"
        updates = list(plangen.solve_stream(problem))

        # Verify we got all expected steps
        step_names = [update["step"] for update in updates]
        assert "extract_constraints" in step_names
        assert "generate_solutions" in step_names
        assert "verify_solutions" in step_names
        assert "select_solution" in step_names

        # Verify each step has in_progress and complete status
        constraint_updates = [u for u in updates if u["step"] == "extract_constraints"]
        assert len(constraint_updates) == 2
        assert constraint_updates[0]["status"] == "in_progress"
        assert constraint_updates[1]["status"] == "complete"
        assert constraint_updates[1]["data"]["constraints"] == "Test constraints"

        solution_updates = [u for u in updates if u["step"] == "generate_solutions"]
        assert len(solution_updates) == 2
        assert solution_updates[0]["status"] == "in_progress"
        assert solution_updates[1]["status"] == "complete"
        assert solution_updates[1]["data"]["solutions"] == [
            "Solution 1",
            "Solution 2",
        ]

        verification_updates = [u for u in updates if u["step"] == "verify_solutions"]
        assert len(verification_updates) == 2
        assert verification_updates[0]["status"] == "in_progress"
        assert verification_updates[1]["status"] == "complete"

        selection_updates = [u for u in updates if u["step"] == "select_solution"]
        assert len(selection_updates) == 2
        assert selection_updates[0]["status"] == "in_progress"
        assert selection_updates[1]["status"] == "complete"
        assert (
            selection_updates[1]["data"]["selected_solution"]["selected_solution"]
            == "Solution 1"
        )

    def test_solve_stream_with_constraint_error(self):
        """Test streaming with error in constraint extraction."""
        # Setup mocks
        mock_model = MagicMock()
        mock_prompt_manager = MagicMock()
        mock_constraint_agent = MagicMock()

        # Configure mock to raise error
        mock_constraint_agent.extract_constraints.side_effect = Exception(
            "Constraint error"
        )

        # Create PlanGEN instance
        plangen = PlanGEN(
            model=mock_model,
            prompt_manager=mock_prompt_manager,
        )
        plangen.constraint_agent = mock_constraint_agent

        # Test streaming
        updates = list(plangen.solve_stream("Test problem"))

        # Verify we got in_progress and error
        assert len(updates) == 2
        assert updates[0]["step"] == "extract_constraints"
        assert updates[0]["status"] == "in_progress"
        assert updates[1]["step"] == "extract_constraints"
        assert updates[1]["status"] == "error"
        assert "Constraint error" in updates[1]["error"]

    def test_solve_stream_with_solution_error(self):
        """Test streaming with error in solution generation."""
        # Setup mocks
        mock_model = MagicMock()
        mock_prompt_manager = MagicMock()
        mock_constraint_agent = MagicMock()
        mock_solution_agent = MagicMock()

        # Configure mocks
        mock_constraint_agent.extract_constraints.return_value = "Test constraints"
        mock_solution_agent.generate_solutions.side_effect = Exception("Solution error")

        # Create PlanGEN instance
        plangen = PlanGEN(
            model=mock_model,
            prompt_manager=mock_prompt_manager,
        )
        plangen.constraint_agent = mock_constraint_agent
        plangen.solution_agent = mock_solution_agent

        # Test streaming
        updates = list(plangen.solve_stream("Test problem"))

        # Find solution generation updates
        solution_updates = [u for u in updates if u["step"] == "generate_solutions"]

        # Verify error was captured
        assert len(solution_updates) == 2
        assert solution_updates[1]["status"] == "error"
        assert "Solution error" in solution_updates[1]["error"]

    def test_solve_stream_with_verification_error(self):
        """Test streaming with error in solution verification."""
        # Setup mocks
        mock_model = MagicMock()
        mock_prompt_manager = MagicMock()
        mock_constraint_agent = MagicMock()
        mock_solution_agent = MagicMock()
        mock_verification_agent = MagicMock()

        # Configure mocks
        mock_constraint_agent.extract_constraints.return_value = "Test constraints"
        mock_solution_agent.generate_solutions.return_value = [
            "Solution 1",
            "Solution 2",
        ]
        mock_verification_agent.verify_solutions.side_effect = Exception(
            "Verification error"
        )

        # Create PlanGEN instance
        plangen = PlanGEN(
            model=mock_model,
            prompt_manager=mock_prompt_manager,
        )
        plangen.constraint_agent = mock_constraint_agent
        plangen.solution_agent = mock_solution_agent
        plangen.verification_agent = mock_verification_agent

        # Test streaming
        updates = list(plangen.solve_stream("Test problem"))

        # Find verification updates
        verification_updates = [u for u in updates if u["step"] == "verify_solutions"]

        # Verify error was captured
        assert len(verification_updates) == 2
        assert verification_updates[0]["status"] == "in_progress"
        assert verification_updates[1]["status"] == "error"
        assert "Verification error" in verification_updates[1]["error"]

        # Verify accumulated data is preserved in error update
        assert verification_updates[1]["data"]["constraints"] == "Test constraints"
        assert verification_updates[1]["data"]["solutions"] == [
            "Solution 1",
            "Solution 2",
        ]

    def test_solve_stream_with_selection_error(self):
        """Test streaming with error in solution selection."""
        # Setup mocks
        mock_model = MagicMock()
        mock_prompt_manager = MagicMock()
        mock_constraint_agent = MagicMock()
        mock_solution_agent = MagicMock()
        mock_verification_agent = MagicMock()
        mock_selection_agent = MagicMock()

        # Configure mocks
        mock_constraint_agent.extract_constraints.return_value = "Test constraints"
        mock_solution_agent.generate_solutions.return_value = [
            "Solution 1",
            "Solution 2",
        ]
        mock_verification_agent.verify_solutions.return_value = [
            "Verification 1",
            "Verification 2",
        ]
        mock_selection_agent.select_best_solution.side_effect = Exception(
            "Selection error"
        )

        # Create PlanGEN instance
        plangen = PlanGEN(
            model=mock_model,
            prompt_manager=mock_prompt_manager,
        )
        plangen.constraint_agent = mock_constraint_agent
        plangen.solution_agent = mock_solution_agent
        plangen.verification_agent = mock_verification_agent
        plangen.selection_agent = mock_selection_agent

        # Test streaming
        updates = list(plangen.solve_stream("Test problem"))

        # Find selection updates
        selection_updates = [u for u in updates if u["step"] == "select_solution"]

        # Verify error was captured
        assert len(selection_updates) == 2
        assert selection_updates[0]["status"] == "in_progress"
        assert selection_updates[1]["status"] == "error"
        assert "Selection error" in selection_updates[1]["error"]

        # Verify all accumulated data is preserved in error update
        assert selection_updates[1]["data"]["constraints"] == "Test constraints"
        assert selection_updates[1]["data"]["solutions"] == [
            "Solution 1",
            "Solution 2",
        ]
        assert selection_updates[1]["data"]["verification_results"] == [
            "Verification 1",
            "Verification 2",
        ]


class TestAPIStreaming:
    """Tests for API-level streaming."""

    def test_api_solve_stream(self):
        """Test streaming through the public API."""
        # Setup mocks
        mock_plangen = MagicMock()

        # Configure mock to return streaming updates
        mock_plangen.solve_stream.return_value = iter(
            [
                {
                    "step": "extract_constraints",
                    "status": "in_progress",
                    "data": None,
                },
                {
                    "step": "extract_constraints",
                    "status": "complete",
                    "data": {"constraints": "Test constraints"},
                },
            ]
        )

        # Create PlanGen wrapper
        plangen_api = PlanGen(mock_plangen)

        # Test streaming
        updates = list(plangen_api.solve_stream("Test problem"))

        # Verify updates were passed through
        assert len(updates) == 2
        assert updates[0]["step"] == "extract_constraints"
        assert updates[0]["status"] == "in_progress"
        assert updates[1]["status"] == "complete"

        # Verify the underlying method was called
        mock_plangen.solve_stream.assert_called_once_with("Test problem")

    def test_api_solve_stream_with_mock_plangen(self):
        """Test streaming through API wrapper with mocked PlanGEN."""
        # Create mock PlanGEN instance
        mock_plangen_instance = MagicMock()

        # Configure streaming response
        mock_plangen_instance.solve_stream.return_value = iter(
            [
                {
                    "step": "extract_constraints",
                    "status": "complete",
                    "data": {"constraints": "Test"},
                }
            ]
        )

        # Create PlanGen wrapper directly
        plangen = PlanGen(mock_plangen_instance)
        updates = list(plangen.solve_stream("Test problem"))

        # Verify streaming worked
        assert len(updates) == 1
        assert updates[0]["step"] == "extract_constraints"
        mock_plangen_instance.solve_stream.assert_called_once_with("Test problem")
