"""
Upper Confidence Bound (UCB) implementation for PlanGEN
"""

import math
from typing import Dict, List, Tuple

import numpy as np


class UCB:
    """Upper Confidence Bound algorithm for multi-armed bandit problems.

    This is an improved UCB implementation based on the paper mentioned in PlanGEN.
    Reference: Han et al., 2024 - "UCB algorithms for multi-armed bandits:
    Precise regret and adaptive inference"
    """

    def __init__(self, algorithm_names: List[str], exploration_weight: float = 2.0):
        """Initialize the UCB algorithm.

        Args:
            algorithm_names: List of algorithm names to choose from
            exploration_weight: Weight for the exploration term
        """
        self.algorithm_names = algorithm_names
        self.exploration_weight = exploration_weight

        # Initialize counts and values for each algorithm
        self.counts = {algo: 0 for algo in algorithm_names}
        self.values = {algo: 0.0 for algo in algorithm_names}
        self.total_pulls = 0

    def select_algorithm(self) -> str:
        """Select the next algorithm to try based on UCB scores.

        Returns:
            Name of the selected algorithm
        """
        # If any algorithm hasn't been tried yet, try it first
        for algo in self.algorithm_names:
            if self.counts[algo] == 0:
                return algo

        # Calculate UCB scores for each algorithm
        ucb_scores = {}
        for algo in self.algorithm_names:
            exploitation = self.values[algo]
            exploration = self.exploration_weight * math.sqrt(
                math.log(self.total_pulls) / self.counts[algo]
            )
            ucb_scores[algo] = exploitation + exploration

        # Return the algorithm with the highest UCB score
        return max(ucb_scores.items(), key=lambda x: x[1])[0]

    def update(self, algorithm: str, reward: float) -> None:
        """Update the UCB algorithm with the reward from the selected algorithm.

        Args:
            algorithm: Name of the algorithm that was used
            reward: Reward received from using the algorithm
        """
        self.counts[algorithm] += 1
        self.total_pulls += 1

        # Update the running average for the algorithm
        n = self.counts[algorithm]
        value = self.values[algorithm]
        self.values[algorithm] = ((n - 1) / n) * value + (1 / n) * reward

    def get_best_algorithm(self) -> str:
        """Get the algorithm with the highest average reward.

        Returns:
            Name of the best algorithm
        """
        return max(self.values.items(), key=lambda x: x[1])[0]

    def get_ucb_scores(self) -> Dict[str, float]:
        """Get the current UCB scores for all algorithms.

        Returns:
            Dictionary mapping algorithm names to UCB scores
        """
        ucb_scores = {}
        for algo in self.algorithm_names:
            if self.counts[algo] == 0:
                ucb_scores[algo] = float("inf")
            else:
                exploitation = self.values[algo]
                exploration = self.exploration_weight * math.sqrt(
                    math.log(self.total_pulls) / self.counts[algo]
                )
                ucb_scores[algo] = exploitation + exploration

        return ucb_scores
