"""
Verification agent for PlanGEN.
"""

import re
from typing import Dict, List, Optional, Tuple, Any

from ..utils.llm_interface import LLMInterface
from ..utils.time_slot_verifier import TimeSlotVerifier, TimeSlot

class VerificationAgent:
    """Agent for verifying plans and solutions."""
    
    def __init__(self, llm_interface: LLMInterface):
        """Initialize the verification agent.
        
        Args:
            llm_interface: LLM interface for generating responses
        """
        self.llm_interface = llm_interface
    
    def run(
        self, 
        problem_statement: str,
        constraints: List[str],
        plan: str,
    ) -> Tuple[str, float]:
        """Verify a plan against constraints.
        
        Args:
            problem_statement: Original problem statement
            constraints: List of constraints
            plan: Plan to verify
            
        Returns:
            Tuple of (feedback, score)
        """
        # First verify the meeting time if this is a scheduling problem
        if "schedule" in problem_statement.lower() and "meeting" in problem_statement.lower():
            results = self.verify_meeting_time(problem_statement, plan, constraints)
            
            # If we found a valid meeting time, use that score
            if results["meeting_time"]:
                return (
                    f"Meeting Time Verification:\n{results['reason']}\n" +
                    (f"Earliest possible: {results['is_earliest']}\n" if results["is_earliest"] is not None else "") +
                    (f"Earliest slot available: {results['earliest_slot']}\n" if results["earliest_slot"] else ""),
                    results["score"]
                )
        
        # Otherwise do general plan verification
        results = self.verify_plan(problem_statement, plan, constraints)
        return results["raw_response"], float(results["score"])
    
    def verify_plan(
        self, 
        problem_statement: str, 
        plan: str, 
        constraints: List[str]
    ) -> Dict[str, Any]:
        """Verify a plan against constraints.
        
        Args:
            problem_statement: The problem statement
            plan: The plan to verify
            constraints: List of constraints
            
        Returns:
            Dictionary with verification results
        """
        # Format constraints as a string
        formatted_constraints = "\n".join([f"- {c}" for c in constraints])
        
        # Format the verification prompt
        prompt = (
            "You are a verification agent tasked with checking if a plan satisfies all constraints.\n\n"
            f"Problem Statement:\n{problem_statement}\n\n"
            f"Plan:\n{plan}\n\n"
            f"Constraints:\n{formatted_constraints}\n\n"
            "Provide your verification in the following format:\n"
            "Verification: [PASS/FAIL]\n"
            "Reason: [Your reasoning]\n"
            "Score: [0-100]"
        )
        
        # Generate the verification
        response = self.llm_interface.generate(prompt=prompt)
        
        # Extract verification results
        verification = "FAIL"
        reason = ""
        score = 0
        
        for line in response.split("\n"):
            if line.startswith("Verification:"):
                verification = line.replace("Verification:", "").strip()
            elif line.startswith("Reason:"):
                reason = line.replace("Reason:", "").strip()
            elif line.startswith("Score:"):
                try:
                    score = int(line.replace("Score:", "").strip())
                except ValueError:
                    pass
        
        return {
            "verification": verification,
            "reason": reason,
            "score": score,
            "raw_response": response
        }
    
    def verify_meeting_time(
        self,
        problem_statement: str,
        plan: str,
        constraints: List[str]
    ) -> Dict[str, Any]:
        """Verify a meeting time against scheduling constraints.
        
        Args:
            problem_statement: The problem statement
            plan: The plan containing a meeting time
            constraints: List of constraints
            
        Returns:
            Dictionary with verification results
        """
        # Extract meeting time from plan
        meeting_time = self._extract_meeting_time(plan)
        
        # Extract busy times from constraints and problem statement
        busy_times = self._extract_busy_times(problem_statement, constraints)
        
        # Create time slot verifier
        verifier = TimeSlotVerifier()
        
        # Add busy times
        for busy in busy_times:
            verifier.add_busy_slot(busy)
        
        # Verify meeting time if found
        if meeting_time:
            is_valid, reason = verifier.is_valid_meeting_slot(meeting_time)
            
            # Find earliest slot for comparison
            earliest_slot = verifier.find_earliest_slot()
            is_earliest = False
            
            if earliest_slot and meeting_time:
                meeting_slot = TimeSlot.from_str(meeting_time)
                is_earliest = (meeting_slot and meeting_slot.start == earliest_slot.start)
            
            return {
                "verification": "PASS" if is_valid else "FAIL",
                "reason": reason,
                "score": 100 if is_valid and is_earliest else (50 if is_valid else 0),
                "is_valid": is_valid,
                "is_earliest": is_earliest,
                "meeting_time": meeting_time,
                "earliest_slot": str(earliest_slot) if earliest_slot else None
            }
        
        # No meeting time found
        return {
            "verification": "FAIL",
            "reason": "No specific meeting time found in plan",
            "score": 0,
            "is_valid": False,
            "is_earliest": False,
            "meeting_time": None,
            "earliest_slot": None
        }
    
    def _extract_meeting_time(self, plan: str) -> Optional[str]:
        """Extract meeting time from plan.
        
        Args:
            plan: The plan text
            
        Returns:
            Meeting time string if found, None otherwise
        """
        # Look for patterns like "schedule from 10:00 to 10:30" or "meeting at 10:00-10:30"
        patterns = [
            r'from (\d{1,2}:\d{2})(?:\s*(?:to|-)?\s*)(\d{1,2}:\d{2})',
            r'at (\d{1,2}:\d{2})(?:\s*(?:to|-)?\s*)(\d{1,2}:\d{2})',
            r'schedule (?:for|at) (\d{1,2}:\d{2})(?:\s*(?:to|-)?\s*)(\d{1,2}:\d{2})',
            r'(\d{1,2}:\d{2})(?:\s*(?:to|-)?\s*)(\d{1,2}:\d{2})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, plan.lower())
            if match:
                start, end = match.groups()
                return f"{start}-{end}"
        
        return None
    
    def _extract_busy_times(self, problem_statement: str, constraints: List[str]) -> List[str]:
        """Extract busy times from problem statement and constraints.
        
        Args:
            problem_statement: The problem statement
            constraints: List of constraints
            
        Returns:
            List of busy time strings
        """
        busy_times = []
        
        # Combine problem statement and constraints
        text = problem_statement + "\n" + "\n".join(constraints)
        
        # Look for patterns like "busy at 9:30-10:00" or "unavailable from 9:30 to 10:00"
        patterns = [
            r'(?:busy|unavailable)(?:\s*(?:at|from))?\s*(\d{1,2}:\d{2})(?:\s*(?:to|-)?\s*)(\d{1,2}:\d{2})',
            r'(?:busy|unavailable)(?:\s*(?:at|from))?\s*(\d{1,2})(?:\s*(?:to|-)?\s*)(\d{1,2})',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text.lower())
            for match in matches:
                start, end = match.groups()
                # Add colon if missing
                if ":" not in start:
                    start = f"{start}:00"
                if ":" not in end:
                    end = f"{end}:00"
                busy_times.append(f"{start}-{end}")
        
        return busy_times