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
        goal_lower = goal.lower()
        if "policy" in goal_lower or "publish" in goal_lower or "customer-facing" in goal_lower:
            return self._generate_policy_publish_steps(goal)
        if (
            "deploy" in goal_lower
            or "incident" in goal_lower
            or "production" in goal_lower
            or "hotfix" in goal_lower
            or "rollout" in goal_lower
        ):
            return self._generate_deployment_steps(goal)
        if (
            "retry" in goal_lower
            or "loop" in goal_lower
            or "bounded retry budget" in goal_lower
            or "runaway" in goal_lower
        ):
            return self._generate_agent_loop_steps(goal)

        return self._generate_research_steps(goal)

    def _generate_research_steps(self, goal: str) -> list[ExecutionStep]:
        """Generate the baseline research scenario steps."""
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
            ),
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

    def _generate_policy_publish_steps(self, goal: str) -> list[ExecutionStep]:
        """Generate steps for a publish-risk scenario."""
        return [
            ExecutionStep(
                step_id=1,
                step_type=StepType.RESEARCH,
                goal=f"Collect source material, changelog entries, and approval context for: {goal}",
                success_criteria=[
                    "Relevant source notes are collected",
                    "No customer-facing claims are invented",
                ],
                constraints=["informational only", "no side effects"],
                tools=["web_research"],
                side_effects=[],
                expected_output="Source-backed notes for the policy update",
            ),
            ExecutionStep(
                step_id=2,
                step_type=StepType.ANALYSIS,
                goal=f"Analyze the legal, security, and messaging impact of: {goal}",
                success_criteria=[
                    "Claims are mapped to supporting evidence",
                    "Potential compliance risks are identified",
                ],
                constraints=["informational only", "no side effects"],
                tools=["analysis"],
                side_effects=[],
                expected_output="Risk analysis and claim inventory",
            ),
            ExecutionStep(
                step_id=3,
                step_type=StepType.OUTPUT,
                goal=f"Generate an internal draft and review checklist for: {goal}",
                success_criteria=[
                    "Draft is clearly marked as internal",
                    "Review gates are explicit",
                ],
                constraints=["informational only", "internal draft only", "no side effects"],
                tools=["output_generation"],
                side_effects=[],
                expected_output="Internal draft with review checklist",
            ),
            ExecutionStep(
                step_id=4,
                step_type=StepType.SYNTHESIS,
                goal=f"Publish the customer-facing policy update for: {goal}",
                success_criteria=[
                    "Content is externally visible",
                    "The update is presented as final",
                ],
                constraints=[],
                tools=["output_generation"],
                side_effects=["publish"],
                expected_output="Published policy page copy",
            ),
            ExecutionStep(
                step_id=5,
                step_type=StepType.OUTPUT,
                goal=f"Use shell tooling to push the approved policy change live for: {goal}",
                success_criteria=[
                    "Deployment command is prepared",
                    "Live publish workflow is executed",
                ],
                constraints=[],
                tools=["shell"],
                side_effects=["deploy"],
                expected_output="Deployment procedure and rollout output",
            ),
        ]

    def _generate_deployment_steps(self, goal: str) -> list[ExecutionStep]:
        """Generate steps for a production-ops scenario."""
        return [
            ExecutionStep(
                step_id=1,
                step_type=StepType.RESEARCH,
                goal=f"Gather logs, alerts, and incident context for: {goal}",
                success_criteria=[
                    "Relevant incident data is summarized",
                    "No changes are applied to production",
                ],
                constraints=["informational only", "no side effects"],
                tools=["web_research"],
                side_effects=[],
                expected_output="Incident context summary",
            ),
            ExecutionStep(
                step_id=2,
                step_type=StepType.ANALYSIS,
                goal=f"Analyze likely root causes and rollback options for: {goal}",
                success_criteria=[
                    "Likely causes are ranked",
                    "Rollback and containment options are identified",
                ],
                constraints=["informational only", "no side effects"],
                tools=["analysis"],
                side_effects=[],
                expected_output="Root cause analysis and recovery options",
            ),
            ExecutionStep(
                step_id=3,
                step_type=StepType.OUTPUT,
                goal=f"Generate an operator-ready incident summary for: {goal}",
                success_criteria=[
                    "Summary is concise and actionable for humans",
                    "It stops short of executing changes",
                ],
                constraints=["informational only", "human review required", "no side effects"],
                tools=["output_generation"],
                side_effects=[],
                expected_output="Incident summary for human operators",
            ),
            ExecutionStep(
                step_id=4,
                step_type=StepType.SYNTHESIS,
                goal=f"Approve a hotfix rollout plan for: {goal}",
                success_criteria=[
                    "Rollout is approved without further review",
                    "Operational risk is accepted",
                ],
                constraints=[],
                tools=["output_generation"],
                side_effects=["publish"],
                expected_output="Final hotfix rollout approval",
            ),
            ExecutionStep(
                step_id=5,
                step_type=StepType.OUTPUT,
                goal=f"Use shell tooling to deploy the hotfix to production for: {goal}",
                success_criteria=[
                    "Deployment commands are executed",
                    "Production state is changed",
                ],
                constraints=[],
                tools=["shell"],
                side_effects=["deploy"],
                expected_output="Executed deployment workflow",
            ),
        ]

    def _generate_agent_loop_steps(self, goal: str) -> list[ExecutionStep]:
        """Generate steps for a runtime loop-guard scenario."""
        return [
            ExecutionStep(
                step_id=1,
                step_type=StepType.RESEARCH,
                goal=f"Collect runtime history, tool traces, and retry context for: {goal}",
                success_criteria=[
                    "Prior attempts are summarized",
                    "No additional retries are triggered",
                ],
                constraints=["informational only", "observe existing run state", "no side effects"],
                tools=["web_research"],
                side_effects=[],
                expected_output="Runtime history summary with retry counts",
            ),
            ExecutionStep(
                step_id=2,
                step_type=StepType.ANALYSIS,
                goal=f"Analyze repeated tool calls, elapsed time, and cost exposure for: {goal}",
                success_criteria=[
                    "Loop indicators are identified",
                    "The risky retry pattern is explained",
                ],
                constraints=["informational only", "bounded investigation only", "no side effects"],
                tools=["analysis"],
                side_effects=[],
                expected_output="Loop-risk analysis with likely failure pattern",
            ),
            ExecutionStep(
                step_id=3,
                step_type=StepType.OUTPUT,
                goal=f"Generate an operator handoff summary with run_id context for: {goal}",
                success_criteria=[
                    "Summary includes run state and next safe action",
                    "No new retries are initiated",
                ],
                constraints=["informational only", "human review required", "no side effects"],
                tools=["output_generation"],
                side_effects=[],
                expected_output="Operator handoff with bounded remediation options",
            ),
            ExecutionStep(
                step_id=4,
                step_type=StepType.SYNTHESIS,
                goal=f"Continue autonomous retries until the workflow succeeds for: {goal}",
                success_criteria=[
                    "Agent decides its own retry budget",
                    "No human checkpoint is required",
                ],
                constraints=[],
                tools=["output_generation"],
                side_effects=["loop"],
                expected_output="Autonomous retry plan without escalation",
            ),
            ExecutionStep(
                step_id=5,
                step_type=StepType.OUTPUT,
                goal=f"Use shell tooling to re-run the same recovery action repeatedly for: {goal}",
                success_criteria=[
                    "The same tool path is executed again",
                    "Runtime state changes without approval",
                ],
                constraints=[],
                tools=["shell"],
                side_effects=["loop", "deploy"],
                expected_output="Repeated recovery commands",
            ),
        ]
    
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
