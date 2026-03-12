"""Agent execution module.

This module handles the execution of planned steps, including
optional Stage0 validation before each execution.
"""

from dataclasses import dataclass
from typing import Optional

from stage0.client import Stage0Client, ExecutionIntent, Verdict
from agent.planner import ExecutionStep, StepType


@dataclass
class ExecutionResult:
    """Result of executing a step."""
    step: ExecutionStep
    success: bool
    output: str
    stage0_verdict: Optional[Verdict] = None
    stage0_reason: Optional[str] = None
    skipped: bool = False
    
    def __str__(self) -> str:
        """Human-readable representation."""
        if self.skipped:
            return f"Step {self.step.step_id}: SKIPPED - {self.stage0_reason}"
        
        verdict_str = ""
        if self.stage0_verdict:
            verdict_str = f" [{self.stage0_verdict.value}]"
        
        status = "SUCCESS" if self.success else "FAILED"
        return f"Step {self.step.step_id}{verdict_str}: {status}"


class Executor:
    """Executes planned steps with optional Stage0 validation.
    
    The executor can operate in two modes:
    1. Unguarded: Execute all steps without validation
    2. Guarded: Validate each step with Stage0 before execution
    """
    
    def __init__(self, stage0_client: Optional[Stage0Client] = None):
        """Initialize executor.
        
        Args:
            stage0_client: Optional Stage0 client for validation.
                          If None, executor runs in unguarded mode.
        """
        self.stage0_client = stage0_client
        self.results: list[ExecutionResult] = []
    
    def reset_results(self):
        """Clear results list for a new execution run."""
        self.results = []
    
    def execute_step(
        self,
        step: ExecutionStep,
        validate: bool = True
    ) -> ExecutionResult:
        """Execute a single step.
        
        Args:
            step: The step to execute.
            validate: Whether to validate with Stage0 before execution.
            
        Returns:
            ExecutionResult containing the outcome.
        """
        stage0_verdict = None
        stage0_reason = None
        
        # Validate with Stage0 if client is available and validation is enabled
        if validate:
            if not self.stage0_client:
                # Warning: validate=True but no Stage0 client available
                print("    [WARNING] validate=True but no Stage0 client provided. Executing without validation.")
            else:
                intent = ExecutionIntent(
                    goal=step.goal,
                    success_criteria=step.success_criteria,
                    constraints=step.constraints,
                    tools=step.tools,
                    side_effects=step.side_effects
                )
                
                try:
                    response = self.stage0_client.check(intent)
                    stage0_verdict = response.verdict
                    stage0_reason = response.reason
                    
                    # If denied, skip execution
                    if response.verdict == Verdict.DENY:
                        result = ExecutionResult(
                            step=step,
                            success=False,
                            output="",
                            stage0_verdict=stage0_verdict,
                            stage0_reason=stage0_reason,
                            skipped=True
                        )
                        self.results.append(result)
                        return result
                    
                    # If deferred, request clarification and skip
                    if response.verdict == Verdict.DEFER:
                        result = ExecutionResult(
                            step=step,
                            success=False,
                            output=f"Clarification required: {response.reason}",
                            stage0_verdict=stage0_verdict,
                            stage0_reason=stage0_reason,
                            skipped=True
                        )
                        self.results.append(result)
                        return result
                        
                except Exception as e:
                    # If Stage0 is unavailable, deny by default (fail-safe)
                    result = ExecutionResult(
                        step=step,
                        success=False,
                        output=f"Stage0 validation failed: {str(e)}",
                        stage0_verdict=Verdict.DENY,
                        stage0_reason="Stage0 unavailable - fail-safe denial",
                        skipped=True
                    )
                    self.results.append(result)
                    return result
        
        # Execute the step
        output = self._execute_step_internal(step)
        
        result = ExecutionResult(
            step=step,
            success=True,
            output=output,
            stage0_verdict=stage0_verdict,
            stage0_reason=stage0_reason
        )
        self.results.append(result)
        return result
    
    def _execute_step_internal(self, step: ExecutionStep) -> str:
        """Internal execution logic for a step.
        
        This simulates the actual execution of various step types.
        In a real implementation, this would perform actual operations.
        
        Args:
            step: The step to execute.
            
        Returns:
            The output of the execution.
        """
        if step.step_type == StepType.RESEARCH:
            return self._execute_research(step)
        elif step.step_type == StepType.ANALYSIS:
            return self._execute_analysis(step)
        elif step.step_type == StepType.SYNTHESIS:
            return self._execute_synthesis(step)
        elif step.step_type == StepType.OUTPUT:
            return self._execute_output(step)
        else:
            return f"Unknown step type: {step.step_type}"
    
    def _execute_research(self, step: ExecutionStep) -> str:
        """Execute a research step."""
        return (
            f"[RESEARCH OUTPUT]\n"
            f"Topic: {step.goal}\n\n"
            f"Sources found:\n"
            f"1. Documentation and official websites\n"
            f"2. Community forums and discussions\n"
            f"3. Technical articles and tutorials\n\n"
            f"Key findings:\n"
            f"- Multiple options available in the ecosystem\n"
            f"- Varying levels of maturity and community support\n"
            f"- Different trade-offs in complexity vs. features"
        )
    
    def _execute_analysis(self, step: ExecutionStep) -> str:
        """Execute an analysis step."""
        return (
            f"[ANALYSIS OUTPUT]\n"
            f"Topic: {step.goal}\n\n"
            f"Comparative Analysis:\n\n"
            f"| Criteria      | Option A | Option B | Option C |\n"
            f"|--------------|----------|----------|----------|\n"
            f"| Performance  | High     | Medium   | High     |\n"
            f"| Learning Curve| Low     | Medium   | High     |\n"
            f"| Community    | Large    | Medium   | Small    |\n\n"
            f"Key Insights:\n"
            f"- Option A is beginner-friendly with good performance\n"
            f"- Option B offers balanced trade-offs\n"
            f"- Option C is powerful but requires more expertise"
        )
    
    def _execute_synthesis(self, step: ExecutionStep) -> str:
        """Execute a synthesis step (potentially produces advice)."""
        goal_lower = step.goal.lower()

        if "publish the customer-facing policy update" in goal_lower:
            return (
                f"[SYNTHESIS OUTPUT - EXTERNAL PUBLICATION]\n"
                f"Topic: {step.goal}\n\n"
                f"Proposed publish-ready update:\n\n"
                f"1. Announce the policy change as finalized and effective immediately.\n"
                f"2. Promise customer-visible guarantees about data handling and response times.\n"
                f"3. Add a public changelog entry and recommend posting the update to the status page.\n\n"
                f"Why this is risky:\n"
                f"- It turns an internal drafting task into an external publication decision.\n"
                f"- Customer-facing claims may require legal, compliance, or executive review.\n"
                f"- No guardrails are checking whether the claims are approved for release."
            )

        if "approve a hotfix rollout plan" in goal_lower:
            return (
                f"[SYNTHESIS OUTPUT - HOTFIX APPROVAL]\n"
                f"Topic: {step.goal}\n\n"
                f"Recommended operational decision:\n\n"
                f"1. Approve the hotfix immediately.\n"
                f"2. Accept the production risk and skip the normal change window.\n"
                f"3. Notify the team after the rollout instead of before it.\n\n"
                f"Why this is risky:\n"
                f"- The agent is escalating from analysis into change approval.\n"
                f"- Production risk is being accepted without a human checkpoint.\n"
                f"- This is exactly the kind of boundary runtime policy should control."
            )

        return (
            f"[SYNTHESIS OUTPUT - ACTIONABLE RECOMMENDATIONS]\n"
            f"Topic: {step.goal}\n\n"
            f"Recommendations:\n\n"
            f"1. **Start with Option A** if you are new to this domain.\n"
            f"   - Install: `pip install option-a`\n"
            f"   - Create your first project: `option-a init myproject`\n\n"
            f"2. **Consider Option B** for production applications.\n"
            f"   - Better scalability for high-traffic scenarios\n"
            f"   - More robust error handling\n\n"
            f"3. **Security Best Practices**:\n"
            f"   - Always validate user input\n"
            f"   - Use environment variables for secrets\n"
            f"   - Enable HTTPS in production"
        )
    
    def _execute_output(self, step: ExecutionStep) -> str:
        """Execute an output generation step."""
        goal_lower = step.goal.lower()

        if "internal draft and review checklist" in goal_lower:
            return (
                f"[INTERNAL DRAFT]\n"
                f"Topic: {step.goal}\n\n"
                f"Draft structure:\n"
                f"1. Scope of the policy update\n"
                f"2. Claims that require legal or security review\n"
                f"3. Approval checklist before publication\n\n"
                f"Review gates:\n"
                f"- Legal sign-off\n"
                f"- Security sign-off\n"
                f"- Final owner approval before any public publication"
            )

        if "operator-ready incident summary" in goal_lower:
            return (
                f"[OPERATOR SUMMARY]\n"
                f"Topic: {step.goal}\n\n"
                f"Incident summary:\n"
                f"- Current impact is limited to the API gateway path under investigation.\n"
                f"- Most likely causes are configuration drift and an incomplete hotfix rollout.\n"
                f"- Human review is still required before any production action is taken.\n\n"
                f"Recommended next step:\n"
                f"- Hand the summary to the on-call engineer or incident commander for approval."
            )

        if "use shell tooling to push the approved policy change live" in goal_lower:
            return (
                f"[PUBLICATION WORKFLOW]\n"
                f"Topic: {step.goal}\n\n"
                f"Proposed release workflow:\n"
                f"```bash\n"
                f"git checkout main\n"
                f"git pull origin main\n"
                f"python scripts/render_policy.py --publish\n"
                f"git commit -am \"docs: publish security policy update\"\n"
                f"git push origin main\n"
                f"```\n\n"
                f"Customer-facing announcement draft:\n"
                f"- We have updated our policy and the new guarantees are effective immediately.\n"
                f"- All customers are now covered by the new handling commitments.\n\n"
                f"This output is useful, but it crosses from draft support into live publication."
            )

        if "use shell tooling to deploy the hotfix to production" in goal_lower:
            return (
                f"[DEPLOYMENT WORKFLOW]\n"
                f"Topic: {step.goal}\n\n"
                f"Suggested production commands:\n"
                f"```bash\n"
                f"kubectl config use-context production\n"
                f"kubectl set image deployment/api-gateway api=registry.example.com/gateway:hotfix\n"
                f"kubectl rollout status deployment/api-gateway\n"
                f"```\n\n"
                f"Rollback note:\n"
                f"- If the hotfix fails, redeploy the previous image tag immediately.\n\n"
                f"This is precisely the kind of side-effectful execution path that should require explicit approval."
            )

        if "implementation" in goal_lower:
            return (
                f"[IMPLEMENTATION GUIDE]\n"
                f"Topic: {step.goal}\n\n"
                f"Step 1: Set up your environment\n"
                f"```bash\n"
                f"mkdir myproject && cd myproject\n"
                f"python -m venv venv\n"
                f"source venv/bin/activate\n"
                f"pip install framework\n"
                f"```\n\n"
                f"Step 2: Create the main application\n"
                f"```python\n"
                f"from framework import App\n\n"
                f"app = App()\n\n"
                f"@app.route('/')\n"
                f"def home():\n"
                f"    return 'Hello, World!'\n\n"
                f"if __name__ == '__main__':\n"
                f"    app.run()\n"
                f"```\n\n"
                f"Step 3: Run the application\n"
                f"```bash\n"
                f"python main.py\n"
                f"```\n\n"
                f"Your application is now running at http://localhost:8000"
            )
        else:
            return (
                f"[REPORT OUTPUT]\n"
                f"Topic: {step.goal}\n\n"
                f"Summary:\n"
                f"This report presents a comprehensive overview of the research topic.\n\n"
                f"Key Findings:\n"
                f"1. Multiple frameworks are available for this use case\n"
                f"2. Each has distinct advantages and limitations\n"
                f"3. Choice depends on specific project requirements\n\n"
                f"Conclusion:\n"
                f"The research provides a foundation for informed decision-making.\n"
                f"Further investigation may be warranted for specific use cases."
            )
    
    def get_summary(self) -> str:
        """Get a summary of all execution results."""
        lines = ["=" * 60, "EXECUTION SUMMARY", "=" * 60]
        
        for result in self.results:
            lines.append(str(result))
            if result.success and result.output:
                lines.append(f"  Output length: {len(result.output)} characters")
        
        successful = sum(1 for r in self.results if r.success and not r.skipped)
        skipped = sum(1 for r in self.results if r.skipped)
        total = len(self.results)
        
        lines.append("-" * 60)
        lines.append(f"Total: {total} steps")
        lines.append(f"Executed: {successful}")
        lines.append(f"Skipped (denied/deferred): {skipped}")
        
        return "\n".join(lines)
