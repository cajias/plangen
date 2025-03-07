"""
REBASE algorithm for PlanGEN

REBASE: REward-BAlanced SEarch
"""

from typing import Dict, List, Optional, Tuple, Any
import random

from .base_algorithm import BaseAlgorithm
from ..utils.llm_interface import LLMInterface

class REBASE(BaseAlgorithm):
    """Implementation of the REBASE algorithm.
    
    REBASE (REward-BAlanced SEarch) balances exploration and exploitation
    in the search space.
    """
    
    def __init__(
        self,
        population_size: int = 5,
        num_generations: int = 3,
        mutation_rate: float = 0.3,
        crossover_rate: float = 0.7,
        **kwargs,
    ):
        """Initialize the REBASE algorithm.
        
        Args:
            population_size: Size of the population in each generation
            num_generations: Number of generations to evolve
            mutation_rate: Probability of mutation
            crossover_rate: Probability of crossover
            **kwargs: Additional arguments passed to BaseAlgorithm
        """
        super().__init__(**kwargs)
        self.population_size = population_size
        self.num_generations = num_generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        
        self.mutation_prompt_template = (
            "I have a plan to solve a problem, but I want to improve it by making some changes.\n\n"
            "Problem statement:\n{problem_statement}\n\n"
            "Constraints to consider:\n{constraints}\n\n"
            "Current plan:\n{current_plan}\n\n"
            "Please modify this plan to improve it. You can:\n"
            "1. Add new steps\n"
            "2. Remove or modify existing steps\n"
            "3. Reorganize the steps\n"
            "4. Add more detail to certain steps\n\n"
            "Focus on addressing any weaknesses in the current plan while ensuring it still "
            "addresses the problem and constraints. Make significant changes to explore new approaches.\n\n"
            "Improved plan:"
        )
        
        self.crossover_prompt_template = (
            "I have two different plans to solve the same problem. I want to combine their "
            "strengths to create a better plan.\n\n"
            "Problem statement:\n{problem_statement}\n\n"
            "Constraints to consider:\n{constraints}\n\n"
            "Plan 1:\n{plan_1}\n\n"
            "Plan 2:\n{plan_2}\n\n"
            "Please create a new plan that combines the best elements of both plans. "
            "Take the strongest aspects from each plan and integrate them into a cohesive solution "
            "that addresses the problem and constraints effectively.\n\n"
            "Combined plan:"
        )
    
    def run(self, problem_statement: str) -> Tuple[str, float, Dict[str, Any]]:
        """Run the REBASE algorithm on the given problem statement.
        
        Args:
            problem_statement: The problem statement to solve
            
        Returns:
            Tuple of (best_plan, best_score, metadata)
        """
        # Extract constraints
        constraints = self.constraint_agent.run(problem_statement)
        
        # Initialize population with random plans
        population = []
        for _ in range(self.population_size):
            # Generate plan with slightly different temperature for diversity
            temperature = self.temperature + (random.random() * 0.2 - 0.1)
            plan = self._generate_plan(
                problem_statement, 
                constraints,
                temperature=temperature,
            )
            
            # Verify plan
            feedback, score = self._verify_plan(problem_statement, constraints, plan)
            
            population.append({
                "plan": plan,
                "score": score,
                "feedback": feedback,
            })
        
        # Track all individuals for metadata
        all_individuals = population.copy()
        
        # Evolve the population for num_generations
        for generation in range(self.num_generations):
            # Create new individuals through mutation and crossover
            new_individuals = []
            
            # Mutation
            for individual in population:
                if random.random() < self.mutation_rate:
                    mutated_plan = self._mutate(
                        problem_statement,
                        constraints,
                        individual["plan"],
                    )
                    
                    # Verify mutated plan
                    feedback, score = self._verify_plan(
                        problem_statement, 
                        constraints, 
                        mutated_plan,
                    )
                    
                    new_individuals.append({
                        "plan": mutated_plan,
                        "score": score,
                        "feedback": feedback,
                        "generation": generation + 1,
                        "type": "mutation",
                    })
            
            # Crossover
            for _ in range(self.population_size // 2):
                if random.random() < self.crossover_rate:
                    # Select two parents using tournament selection
                    parent1 = self._tournament_selection(population)
                    parent2 = self._tournament_selection(population)
                    
                    # Perform crossover
                    child_plan = self._crossover(
                        problem_statement,
                        constraints,
                        parent1["plan"],
                        parent2["plan"],
                    )
                    
                    # Verify child plan
                    feedback, score = self._verify_plan(
                        problem_statement, 
                        constraints, 
                        child_plan,
                    )
                    
                    new_individuals.append({
                        "plan": child_plan,
                        "score": score,
                        "feedback": feedback,
                        "generation": generation + 1,
                        "type": "crossover",
                    })
            
            # Add new individuals to the population
            population.extend(new_individuals)
            all_individuals.extend(new_individuals)
            
            # Select the best individuals for the next generation
            population = sorted(population, key=lambda x: x["score"], reverse=True)[:self.population_size]
        
        # Select the best plan
        best_individual = max(population, key=lambda x: x["score"])
        best_plan = best_individual["plan"]
        best_score = best_individual["score"]
        
        # Prepare metadata
        metadata = {
            "algorithm": "REBASE",
            "population_size": self.population_size,
            "num_generations": self.num_generations,
            "mutation_rate": self.mutation_rate,
            "crossover_rate": self.crossover_rate,
            "all_individuals": all_individuals,
            "constraints": constraints,
        }
        
        return best_plan, best_score, metadata
    
    def _mutate(
        self, 
        problem_statement: str, 
        constraints: List[str], 
        current_plan: str,
    ) -> str:
        """Mutate a plan to create a new variant.
        
        Args:
            problem_statement: The problem statement to solve
            constraints: List of constraints to consider
            current_plan: The current plan to mutate
            
        Returns:
            Mutated plan
        """
        # Format constraints as a numbered list
        formatted_constraints = "\n".join(
            f"{i+1}. {constraint}" for i, constraint in enumerate(constraints)
        )
        
        prompt = self.mutation_prompt_template.format(
            problem_statement=problem_statement,
            constraints=formatted_constraints,
            current_plan=current_plan,
        )
        
        return self.llm_interface.generate(prompt=prompt)
    
    def _crossover(
        self, 
        problem_statement: str, 
        constraints: List[str], 
        plan_1: str, 
        plan_2: str,
    ) -> str:
        """Perform crossover between two plans to create a new plan.
        
        Args:
            problem_statement: The problem statement to solve
            constraints: List of constraints to consider
            plan_1: The first parent plan
            plan_2: The second parent plan
            
        Returns:
            Child plan
        """
        # Format constraints as a numbered list
        formatted_constraints = "\n".join(
            f"{i+1}. {constraint}" for i, constraint in enumerate(constraints)
        )
        
        prompt = self.crossover_prompt_template.format(
            problem_statement=problem_statement,
            constraints=formatted_constraints,
            plan_1=plan_1,
            plan_2=plan_2,
        )
        
        return self.llm_interface.generate(prompt=prompt)
    
    def _tournament_selection(self, population: List[Dict[str, Any]], tournament_size: int = 3) -> Dict[str, Any]:
        """Select an individual using tournament selection.
        
        Args:
            population: List of individuals
            tournament_size: Number of individuals to include in the tournament
            
        Returns:
            Selected individual
        """
        tournament = random.sample(population, min(tournament_size, len(population)))
        return max(tournament, key=lambda x: x["score"])