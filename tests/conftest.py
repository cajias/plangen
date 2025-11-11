"""
Shared pytest fixtures for PlanGEN tests.

This module provides common fixtures that can be reused across all test files,
reducing code duplication and ensuring consistency in test setup.
"""

import pytest
from unittest.mock import MagicMock
from plangen.models import BaseModelInterface
from plangen.prompts import PromptManager


@pytest.fixture
def mock_model():
    """Provide a mock model interface for testing.

    Returns:
        MagicMock: A mock BaseModelInterface with common methods configured.
    """
    mock = MagicMock(spec=BaseModelInterface)
    mock.generate.return_value = "Generated response"
    mock.batch_generate.return_value = ["Response 1", "Response 2", "Response 3"]
    return mock


@pytest.fixture
def mock_prompt_manager():
    """Provide a mock prompt manager for testing.

    Returns:
        MagicMock: A mock PromptManager with common methods configured.
    """
    mock = MagicMock(spec=PromptManager)
    mock.get_system_message.return_value = "System message"
    mock.get_prompt.return_value = "Rendered prompt"
    return mock


@pytest.fixture
def sample_problem():
    """Provide a sample problem statement for testing.

    Returns:
        str: A sample problem statement.
    """
    return """
    Schedule a 30-minute meeting for Alexander, Elizabeth, and Walter
    on Monday between 9:00 and 17:00. All participants must be available.
    """


@pytest.fixture
def sample_constraints():
    """Provide sample constraints for testing.

    Returns:
        str: Sample constraints as a string.
    """
    return """
    1. Meeting duration must be 30 minutes
    2. Meeting must be on Monday
    3. Meeting must be between 9:00 and 17:00
    4. All participants must be available
    """


@pytest.fixture
def sample_constraints_list():
    """Provide sample constraints as a list for testing.

    Returns:
        List[str]: Sample constraints as a list.
    """
    return [
        "Meeting duration must be 30 minutes",
        "Meeting must be on Monday",
        "Meeting must be between 9:00 and 17:00",
        "All participants must be available",
    ]


@pytest.fixture
def sample_solutions():
    """Provide sample solutions for testing.

    Returns:
        List[str]: List of sample solutions.
    """
    return [
        "Solution 1: Schedule meeting on Monday at 10:00",
        "Solution 2: Schedule meeting on Monday at 14:00",
        "Solution 3: Schedule meeting on Monday at 16:00",
    ]


@pytest.fixture
def sample_verification_results():
    """Provide sample verification results for testing.

    Returns:
        List[str]: List of sample verification results.
    """
    return [
        "Valid: All constraints satisfied",
        "Valid: All constraints satisfied",
        "Invalid: Meeting ends after 17:00",
    ]


@pytest.fixture
def temp_directory(tmp_path):
    """Provide a temporary directory for file-based tests.

    Args:
        tmp_path: pytest's built-in temporary directory fixture.

    Returns:
        Path: Path to a temporary directory that will be cleaned up after tests.
    """
    return tmp_path


@pytest.fixture
def mock_algorithm_result():
    """Provide a mock algorithm result for testing.

    Returns:
        tuple: A tuple of (plan, score, metadata) representing algorithm output.
    """
    return (
        "Best solution: Schedule meeting on Monday at 10:00",
        0.95,
        {
            "algorithm": "best_of_n",
            "iterations": 3,
            "timestamp": "2024-01-01T00:00:00",
        }
    )
