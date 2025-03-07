"""
Main PlanGEN implementation using LangGraph
"""

from typing import Dict, List, Any, Optional, TypedDict, Annotated
from pydantic import BaseModel, Field

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from .models import BaseModelInterface, OpenAIModelInterface
from .prompts import PromptManager
from .agents import ConstraintAgent, SolutionAgent, VerificationAgent, SelectionAgent


class PlanGENState(TypedDict):
    """State for the PlanGEN workflow."""
    
    problem: str
    constraints: Optional[str]
    solutions: Optional[List[str]]
    verification_results: Optional[List[str]]
    selected_solution: Optional[Dict[str, Any]]
    error: Optional[str]


class PlanGEN:
    """Main PlanGEN implementation using LangGraph."""
    
    def __init__(
        self,
        model: Optional[BaseModelInterface] = None,
        prompt_manager: Optional[PromptManager] = None,
        num_solutions: int = 3,
    ):
        """Initialize the PlanGEN framework.
        
        Args:
            model: Model interface for generating responses
            prompt_manager: Manager for prompt templates
            num_solutions: Number of solutions to generate
        """
        # Use default model if not provided
        self.model = model or OpenAIModelInterface()
        
        # Use default prompt manager if not provided
        self.prompt_manager = prompt_manager or PromptManager()
        
        # Number of solutions to generate
        self.num_solutions = num_solutions
        
        # Initialize agents
        self.constraint_agent = ConstraintAgent(self.model, self.prompt_manager)
        self.solution_agent = SolutionAgent(self.model, self.prompt_manager)
        self.verification_agent = VerificationAgent(self.model, self.prompt_manager)
        self.selection_agent = SelectionAgent(self.model, self.prompt_manager)
        
        # Build the workflow graph
        self.workflow = self._build_workflow()
    
    def _extract_constraints(self, state: PlanGENState) -> PlanGENState:
        """Extract constraints from the problem statement.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated workflow state
        """
        try:
            constraints = self.constraint_agent.extract_constraints(state["problem"])
            return {"constraints": constraints}
        except Exception as e:
            return {"error": f"Error extracting constraints: {str(e)}"}
    
    def _generate_solutions(self, state: PlanGENState) -> PlanGENState:
        """Generate solutions based on constraints.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated workflow state
        """
        try:
            solutions = self.solution_agent.generate_solutions(
                state["problem"],
                state["constraints"],
                num_solutions=self.num_solutions
            )
            return {"solutions": solutions}
        except Exception as e:
            return {"error": f"Error generating solutions: {str(e)}"}
    
    def _verify_solutions(self, state: PlanGENState) -> PlanGENState:
        """Verify solutions against constraints.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated workflow state
        """
        try:
            verification_results = self.verification_agent.verify_solutions(
                state["solutions"],
                state["constraints"]
            )
            return {"verification_results": verification_results}
        except Exception as e:
            return {"error": f"Error verifying solutions: {str(e)}"}
    
    def _select_solution(self, state: PlanGENState) -> PlanGENState:
        """Select the best solution based on verification results.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated workflow state
        """
        try:
            selected = self.selection_agent.select_best_solution(
                state["solutions"],
                state["verification_results"]
            )
            return {"selected_solution": selected}
        except Exception as e:
            return {"error": f"Error selecting solution: {str(e)}"}
    
    def _should_end(self, state: PlanGENState) -> str:
        """Determine if the workflow should end.
        
        Args:
            state: Current workflow state
            
        Returns:
            Next node name or END
        """
        if state.get("error") is not None:
            return "error"
        return "continue"
    
    def _build_workflow(self) -> StateGraph:
        """Build the workflow graph.
        
        Returns:
            StateGraph for the PlanGEN workflow
        """
        # Create the graph
        workflow = StateGraph(PlanGENState)
        
        # Add nodes
        workflow.add_node("extract_constraints", self._extract_constraints)
        workflow.add_node("generate_solutions", self._generate_solutions)
        workflow.add_node("verify_solutions", self._verify_solutions)
        workflow.add_node("select_solution", self._select_solution)
        
        # Add edges
        workflow.add_edge("extract_constraints", "generate_solutions")
        workflow.add_edge("generate_solutions", "verify_solutions")
        workflow.add_edge("verify_solutions", "select_solution")
        workflow.add_edge("select_solution", END)
        
        # Set the entry point
        workflow.set_entry_point("extract_constraints")
        
        # Compile the graph
        return workflow.compile()
    
    def solve(self, problem: str) -> Dict[str, Any]:
        """Solve a problem using the PlanGEN workflow.
        
        Args:
            problem: Problem statement
            
        Returns:
            Dictionary with the solution and intermediate results
        """
        try:
            # Initialize the state
            state = {"problem": problem}
            
            # Extract constraints
            print("Extracting constraints...")
            constraints_result = self._extract_constraints(state)
            if "error" in constraints_result:
                return {"problem": problem, "error": constraints_result["error"]}
            state.update(constraints_result)
            
            # Generate solutions
            print("Generating solutions...")
            solutions_result = self._generate_solutions(state)
            if "error" in solutions_result:
                return {**state, "error": solutions_result["error"]}
            state.update(solutions_result)
            
            # Verify solutions
            print("Verifying solutions...")
            verify_result = self._verify_solutions(state)
            if "error" in verify_result:
                return {**state, "error": verify_result["error"]}
            state.update(verify_result)
            
            # Select solution
            print("Selecting best solution...")
            select_result = self._select_solution(state)
            if "error" in select_result:
                return {**state, "error": select_result["error"]}
            state.update(select_result)
            
            print("Solution process complete.")
            return state
            
        except Exception as e:
            return {
                "problem": problem,
                "error": f"Error in workflow: {str(e)}"
            }