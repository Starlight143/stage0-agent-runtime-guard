"""Agent planning module.

This module handles the planning phase of the agent, breaking down
a high-level goal into executable steps.
"""

from dataclasses import dataclass
from enum import Enum


class StepType(Enum):
    """Types of execution steps."""
    RESEARCH = "research"
    ANALYSIS = "analysis"
    SYNTHESIS = "synthesis"
    OUTPUT = "output"


@dataclass
class ExecutionStep:
    """Represents a single execution step in the agent's plan."""
    step_id: int
    step_type: StepType
    goal: str
    success_criteria: list[str]
    constraints: list[str]
    tools: list[str]
    side_effects: list[str]
    expected_output: str
    
    def __str__(self) -> str:
        """Human-readable representation."""
        return f"Step {self.step_id}: [{self.step_type.value}] {self.goal}"


@dataclass
class Plan:
    """Represents a complete execution plan."""
    goal: str
    steps: list[ExecutionStep]
    
    def __str__(self) -> str:
        """Human-readable representation."""
        lines = [f"Plan for: {self.goal}", "-" * 50]
        for step in self.steps:
            lines.append(str(step))
        return "\n".join(lines)


class Planner:
    """Plans execution steps for achieving a goal.
    
    The planner breaks down a high-level research goal into
    a sequence of executable steps. Each step represents an
    intent that may need validation by Stage0.
    """
    
    # Predefined step templates for research-style agents
    RESEARCH_TEMPLATES = {
        "web_search": {
            "step_type": StepType.RESEARCH,
            "tools": ["web_research"],
            "side_effects": [],
            "constraints": ["informational only"]
        },
        "comparison": {
            "step_type": StepType.ANALYSIS,
            "tools": ["analysis"],
            "side_effects": [],
            "constraints": ["informational only"]
        },
        "report": {
            "step_type": StepType.OUTPUT,
            "tools": ["output_generation"],
            "side_effects": [],
            "constraints": ["informational only"]
        },
        "recommendation": {
            "step_type": StepType.SYNTHESIS,
            "tools": ["output_generation"],
            "side_effects": [],
            "constraints": []  # No constraints - may produce advice
        },
        "implementation": {
            "step_type": StepType.OUTPUT,
            "tools": ["output_generation"],
            "side_effects": [],
            "constraints": []  # No constraints - produces actionable content
        }
    }
    
    def create_plan(self, goal: str) -> Plan:
        """Create an execution plan for the given goal.
        
        Args:
            goal: The high-level goal to achieve.
            
        Returns:
            A Plan containing ordered ExecutionSteps.
        """
        steps = self._generate_steps(goal)
        return Plan(goal=goal, steps=steps)
    
    def _generate_steps(self, goal: str) -> list[ExecutionStep]:
        """Generate execution steps for a research goal.
        
        This method creates a sequence of steps that a typical
        research agent would execute. Some steps are intentionally
        designed to exceed safe boundaries for demonstration.
        """
        steps = [
            # Step 1: Initial research (safe)
            ExecutionStep(
                step_id=1,
                step_type=StepType.RESEARCH,
                goal=f"Search for information related to: {goal}",
                success_criteria=[
                    "At least 3 relevant sources found",
                    "Sources are from credible domains"
                ],
                constraints=["informational only", "no side effects"],
                tools=["web_research"],
                side_effects=[],
                expected_output="List of relevant sources with summaries"
            ),
            # Step 2: Analysis (safe)
            ExecutionStep(
                step_id=2,
                step_type=StepType.ANALYSIS,
                goal=f"Analyze and compare findings related to: {goal}",
                success_criteria=[
                    "Key points identified",
                    "Comparative analysis completed"
                ],
                constraints=["informational only", "no side effects"],
                tools=["analysis"],
                side_effects=[],
                expected_output="Comparative analysis document"
            ),
            # Step 3: Generate summary report (safe)
            ExecutionStep(
                step_id=3,
                step_type=StepType.OUTPUT,
                goal=f"Generate a summary report on: {goal}",
                success_criteria=[
                    "Report covers all researched topics",
                    "Report is well-structured"
                ],
                constraints=["informational only", "no side effects"],
                tools=["output_generation"],
                side_effects=[],
                expected_output="Structured summary report"
            ),
            # Step 4: Provide recommendations (unsafe - triggers HIGH severity DENY)
            # This step declares "publish" side effect without guardrails,
            # which triggers SIDE_EFFECTS_NEED_GUARDRAILS issue (HIGH severity)
            ExecutionStep(
                step_id=4,
                step_type=StepType.SYNTHESIS,
                goal=f"Provide actionable recommendations based on: {goal}",
                success_criteria=[
                    "Recommendations are specific",
                    "Recommendations are actionable"
                ],
                constraints=[],  # No guardrails - intentionally unsafe
                tools=["output_generation"],
                side_effects=["publish"],  # HIGH risk side effect
                expected_output="List of actionable recommendations"
            ),
            # Step 5: Provide implementation guidance (unsafe - triggers HIGH severity DENY)
            # This step uses sensitive tool without constraints and has deploy side effect
            ExecutionStep(
                step_id=5,
                step_type=StepType.OUTPUT,
                goal=f"Provide step-by-step implementation guidance for: {goal}",
                success_criteria=[
                    "Steps are detailed",
                    "Code examples provided if applicable"
                ],
                constraints=[],  # No constraints - exceeds research scope
                tools=["shell"],  # Sensitive tool
                side_effects=["deploy"],  # HIGH risk side effect
                expected_output="Implementation guide with code examples"
            )
        ]
        
        return steps
    
    def create_constrained_plan(self, goal: str) -> Plan:
        """Create a constrained plan that stays within research scope.
        
        This creates a plan with only informational steps that
        should be allowed by Stage0.
        """
        steps = [
            ExecutionStep(
                step_id=1,
                step_type=StepType.RESEARCH,
                goal=f"Search for information related to: {goal}",
                success_criteria=[
                    "At least 3 relevant sources found",
                    "Sources are from credible domains"
                ],
                constraints=["informational only", "no side effects"],
                tools=["web_research"],
                side_effects=[],
                expected_output="List of relevant sources with summaries"
            ),
            ExecutionStep(
                step_id=2,
                step_type=StepType.ANALYSIS,
                goal=f"Analyze and compare findings related to: {goal}",
                success_criteria=[
                    "Key points identified",
                    "Comparative analysis completed"
                ],
                constraints=["informational only", "no side effects"],
                tools=["analysis"],
                side_effects=[],
                expected_output="Comparative analysis document"
            ),
            ExecutionStep(
                step_id=3,
                step_type=StepType.OUTPUT,
                goal=f"Generate a summary report on: {goal}",
                success_criteria=[
                    "Report covers all researched topics",
                    "Report is well-structured"
                ],
                constraints=["informational only", "no side effects"],
                tools=["output_generation"],
                side_effects=[],
                expected_output="Structured summary report"
            )
        ]
        
        return Plan(goal=goal, steps=steps)
