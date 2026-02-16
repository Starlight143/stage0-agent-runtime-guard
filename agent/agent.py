"""Main agent module.

This module defines the Agent class that orchestrates planning
and execution, with optional Stage0 runtime guard integration.
"""

from dataclasses import dataclass
from typing import Optional

from stage0.client import Stage0Client
from agent.planner import Planner, Plan, ExecutionStep
from agent.executor import Executor, ExecutionResult


@dataclass
class AgentRunResult:
    """Result of a complete agent run."""
    goal: str
    plan: Plan
    results: list[ExecutionResult]
    final_output: str
    guarded: bool
    
    def get_successful_outputs(self) -> list[str]:
        """Get outputs from all successful steps."""
        return [r.output for r in self.results if r.success and not r.skipped]
    
    def get_denied_steps(self) -> list[ExecutionResult]:
        """Get steps that were denied by Stage0."""
        return [r for r in self.results if r.skipped]


class Agent:
    """Autonomous research agent with optional Stage0 guard.
    
    This agent demonstrates the difference between unguarded and
    guarded execution. Without Stage0, the agent may execute steps
    that exceed its intended scope. With Stage0, every execution
    intent is validated before execution.
    
    Key principle: Stage0 is NOT part of the agent. The agent
    cannot self-approve actions. All execution intent MUST be
    validated via Stage0 /check.
    """
    
    def __init__(
        self,
        stage0_client: Optional[Stage0Client] = None,
        planner: Optional[Planner] = None,
        executor: Optional[Executor] = None
    ):
        """Initialize the agent.
        
        Args:
            stage0_client: Optional Stage0 client. If provided, the agent
                          will validate execution intents before execution.
            planner: Optional planner instance. Defaults to new Planner.
            executor: Optional executor instance. Defaults to new Executor.
        """
        self.stage0_client = stage0_client
        self.planner = planner or Planner()
        self.executor = executor or Executor(stage0_client=stage0_client)
    
    def run(
        self,
        goal: str,
        guarded: bool = True
    ) -> AgentRunResult:
        """Run the agent to achieve a goal.
        
        Args:
            goal: The goal to achieve.
            guarded: Whether to validate with Stage0 before each step.
                    If False, executes all steps without validation.
                    
        Returns:
            AgentRunResult containing the plan and execution results.
        """
        # Reset executor results for a clean run
        self.executor.reset_results()
        
        # Phase 1: Planning
        print(f"\n{'='*60}")
        print(f"AGENT RUN: {goal}")
        print(f"Mode: {'GUARDED (with Stage0)' if guarded else 'UNGUARDED (no Stage0)'}")
        print(f"{'='*60}\n")
        
        print("[PLANNING PHASE]")
        plan = self.planner.create_plan(goal)
        print(plan)
        print()
        
        # Phase 2: Execution
        print("[EXECUTION PHASE]")
        results: list[ExecutionResult] = []
        
        for step in plan.steps:
            print(f"\n>>> Executing: {step}")
            
            result = self.executor.execute_step(step, validate=guarded)
            results.append(result)
            
            if result.skipped:
                print(f"    [DENIED] {result.stage0_reason}")
                # In guarded mode, we continue to show more denials
                # In a real system, we might stop or replan
            else:
                print(f"    [EXECUTED] Output length: {len(result.output)} chars")
        
        print()
        print(self.executor.get_summary())
        
        # Compile final output
        final_output = self._compile_output(results)
        
        return AgentRunResult(
            goal=goal,
            plan=plan,
            results=results,
            final_output=final_output,
            guarded=guarded
        )
    
    def _compile_output(self, results: list[ExecutionResult]) -> str:
        """Compile execution results into a final output."""
        lines = ["=" * 60, "FINAL OUTPUT", "=" * 60, ""]
        
        for result in results:
            if result.success and not result.skipped:
                lines.append(f"--- {result.step.goal} ---")
                lines.append(result.output)
                lines.append("")
        
        return "\n".join(lines)
    
    def run_with_adaptation(
        self,
        goal: str
    ) -> AgentRunResult:
        """Run with automatic adaptation when steps are denied.
        
        When Stage0 denies a step, the agent attempts to modify
        its plan to stay within approved boundaries.
        """
        # Reset executor results for a clean run
        self.executor.reset_results()
        
        print(f"\n{'='*60}")
        print(f"AGENT RUN WITH ADAPTATION: {goal}")
        print(f"{'='*60}\n")
        
        print("[PLANNING PHASE]")
        plan = self.planner.create_plan(goal)
        print(plan)
        print()
        
        print("[EXECUTION PHASE - WITH ADAPTATION]")
        results: list[ExecutionResult] = []
        adapted_steps: list[ExecutionStep] = []
        
        for step in plan.steps:
            print(f"\n>>> Attempting: {step}")
            
            result = self.executor.execute_step(step, validate=True)
            results.append(result)
            
            if result.skipped:
                print(f"    [DENIED] {result.stage0_reason}")
                
                # Try to adapt the step
                adapted_step = self._adapt_step(step)
                if adapted_step:
                    print(f"\n>>> Adapting to: {adapted_step}")
                    adapted_result = self.executor.execute_step(adapted_step, validate=True)
                    results.append(adapted_result)
                    
                    if adapted_result.skipped:
                        print(f"    [STILL DENIED] Cannot execute this step")
                    else:
                        print(f"    [EXECUTED] Adapted step succeeded")
                        adapted_steps.append(adapted_step)
            else:
                print(f"    [EXECUTED] Output length: {len(result.output)} chars")
        
        print()
        print(self.executor.get_summary())
        
        final_output = self._compile_output(results)
        
        return AgentRunResult(
            goal=goal,
            plan=plan,
            results=results,
            final_output=final_output,
            guarded=True
        )
    
    def _adapt_step(self, step: ExecutionStep) -> Optional[ExecutionStep]:
        """Attempt to adapt a denied step to be compliant.
        
        This method modifies a step to be more restrictive,
        adding constraints that may allow it to pass Stage0.
        """
        # If step already has informational constraints, can't adapt further
        if "informational only" in step.constraints:
            return None
        
        # Add informational constraints to the step (avoid duplicates)
        adapted_constraints = list(step.constraints)
        for constraint in ["informational only", "no advice", "no side effects"]:
            if constraint not in adapted_constraints:
                adapted_constraints.append(constraint)
        
        # Modify the goal to be informational
        if "implementation" in step.goal.lower():
            adapted_goal = step.goal.replace(
                "Provide step-by-step implementation guidance",
                "Provide informational overview"
            )
            adapted_goal = adapted_goal.replace(
                "step-by-step implementation guidance",
                "informational overview"
            )
        elif "recommendation" in step.goal.lower():
            adapted_goal = step.goal.replace(
                "actionable recommendations",
                "informational comparison"
            )
            adapted_goal = adapted_goal.replace(
                "recommendations",
                "observations"
            )
        else:
            adapted_goal = f"Provide informational summary about: {step.goal}"
        
        return ExecutionStep(
            step_id=step.step_id * 10,  # New step ID to avoid conflicts
            step_type=step.step_type,
            goal=adapted_goal,
            success_criteria=["Output is informational only"],
            constraints=adapted_constraints,
            tools=step.tools,
            side_effects=[],
            expected_output="Informational content only"
        )
