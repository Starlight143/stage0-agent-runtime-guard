"""Demo: Agent execution WITH Stage0 runtime guard.

This demo shows how Stage0 validates every execution intent
before the agent can proceed. Steps that exceed the allowed
scope are denied, keeping the agent within safe boundaries.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent import Agent
from demo.scenarios import DemoScenario, get_scenario
from stage0 import Stage0Client


def check_api_key() -> bool:
    """Check if Stage0 API key is configured."""
    api_key = os.getenv("STAGE0_API_KEY")
    return bool(api_key and api_key != "your_api_key_here")


def print_scenario_context(scenario: DemoScenario) -> None:
    """Print the business framing for the selected scenario."""
    print(f"Scenario: {scenario.title}")
    print(f"Buyer context: {scenario.customer_type}")
    print(f"Why it matters: {scenario.why_it_matters}")
    print()


def main(scenario_key: str = "frameworks"):
    """Run the guarded agent demo."""
    scenario = get_scenario(scenario_key)

    print("=" * 70)
    print("DEMO: Agent WITH Stage0 Runtime Guard")
    print("=" * 70)
    print()
    print_scenario_context(scenario)

    if not check_api_key():
        print("ERROR: STAGE0_API_KEY environment variable is not set.")
        print()
        print("To run this demo against the real API, you need a Stage0 API key")
        print("from SignalPulse.")
        print()
        print("Setup instructions:")
        print("1. Copy .env.example to .env")
        print("2. Add your STAGE0_API_KEY to .env")
        print("3. Run this demo again")
        print()
        print("The fallback below uses simulated Stage0 responses so you can still")
        print("show the guard behavior to prospects or teammates.")
        print()
        run_simulated_demo(scenario_key)
        return

    print("Stage0 API key found. Connecting to Stage0...")
    print()
    print("This demo shows an agent where every execution step is validated")
    print("by Stage0 before execution. Steps that exceed scope are denied.")
    print()

    try:
        stage0_client = Stage0Client()
    except ValueError as exc:
        print(f"Error initializing Stage0 client: {exc}")
        return

    agent = Agent(stage0_client=stage0_client)
    result = agent.run(scenario.goal, guarded=True)

    print()
    print("=" * 70)
    print("FINAL OUTPUT (Constrained by Stage0)")
    print("=" * 70)
    print(result.final_output)

    blocked_steps = result.get_denied_steps()
    if blocked_steps:
        print()
        print("=" * 70)
        print("BLOCKED STEPS (Stage0 prevented execution)")
        print("=" * 70)
        for blocked in blocked_steps:
            print(f"\nStep {blocked.step.step_id}: {blocked.step.goal}")
            print(f"Reason: {blocked.stage0_reason}")
            if blocked.stage0_decision:
                print(f"Decision: {blocked.stage0_decision.value}")
            if blocked.stage0_verdict:
                print(f"Verdict: {blocked.stage0_verdict.value}")
            if blocked.stage0_request_id:
                print(f"Request ID: {blocked.stage0_request_id}")
            if blocked.stage0_policy_version:
                print(f"Policy Version: {blocked.stage0_policy_version}")

    print()
    print("=" * 70)
    print("ANALYSIS: How Stage0 protected the execution")
    print("=" * 70)

    executed_count = sum(
        1 for item in result.results if item.success and not item.skipped
    )
    denied_count = sum(
        1
        for item in blocked_steps
        if item.stage0_verdict and item.stage0_verdict.value == "DENY"
    )
    deferred_count = sum(
        1
        for item in blocked_steps
        if item.stage0_verdict and item.stage0_verdict.value == "DEFER"
    )

    final_gate_summary = "DENY or DEFER"
    if scenario_key == "agent_loops":
        final_gate_summary = "DEFER"

    print(
        f"""
With Stage0 validation:

1. Steps 1-3: ALLOWED
   - Research, analysis, and informational preparation
   - No high-risk side effects, proper constraints

2. Steps 4-5: {final_gate_summary}
   - Stage0 blocks or defers steps that cross into publish, deploy, or runaway-loop behavior
   - The agent is forced to stop before it can create external, production, or repeated side effects

Result: {scenario.guarded_outcome}

This demonstrates the value of runtime guards:
- External authority validates intent before execution
- Agent cannot self-approve actions
- High-risk side effects and repeated loops are blocked without proper guardrails
- Runtime context such as approvals, environment, request channel, and run state can shape the decision
- Violations are prevented, not just detected after the fact

Stats:
- Steps executed: {executed_count}
- Steps denied: {denied_count}
- Steps deferred: {deferred_count}
"""
    )


def get_simulated_verdict(side_effects: list[str], tools: list[str]) -> tuple[str, str]:
    """Compute simulated Stage0 verdict based on side effects and tools.

    This matches the actual Stage0 API behavior:
    - DENY for 'publish' or 'deploy' side effects
    - DENY for 'shell' tools
    - ALLOW for everything else (including 'loop')
    """
    side_effects = side_effects or []
    tools = tools or []

    if "publish" in side_effects or "deploy" in side_effects:
        return (
            "DENY",
            "SIDE_EFFECTS_NEED_GUARDRAILS: External/irreversible side effects declared without machine-readable guardrails in constraints.",
        )
    if "shell" in tools:
        return (
            "DENY",
            "SENSITIVE_TOOLS_NEED_CONSTRAINTS: Sensitive tools present without sandbox/allowlist constraints.",
        )
    return "ALLOW", "No blocking issues detected."


def run_simulated_demo(scenario_key: str):
    """Run demo with simulated Stage0 responses using actual planner steps."""
    from agent.planner import Planner
    from stage0.client import Verdict

    scenario = get_scenario(scenario_key)

    print("=" * 70)
    print("SIMULATED DEMO: What Stage0 would do")
    print("=" * 70)
    print()
    print("Since no API key is available, this shows simulated responses")
    print("that demonstrate how Stage0 would guard the agent.")
    print()

    planner = Planner()
    plan = planner.create_plan(scenario.goal)

    print(f"Plan: {scenario.goal}")
    print("-" * 70)
    print()

    executed_outputs: list[str] = []

    for step in plan.steps:
        verdict, reason = get_simulated_verdict(step.side_effects, step.tools)

        print(f"Step {step.step_id}: {step.goal}")
        print(f"  Type: {step.step_type.value}")
        print(f"  Side Effects: {step.side_effects or 'None'}")
        print(f"  Stage0 Verdict: {verdict}")
        print(f"  Reason: {reason}")

        if verdict == "ALLOW":
            print("  Action: EXECUTING...")
            executed_outputs.append(step.goal)
        else:
            print("  Action: SKIPPED (not authorized)")

        print()

    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print("Steps Executed (ALLOW):")
    for output in executed_outputs:
        print(f"  - {output}")

    print()
    print("Steps Denied (DENY):")
    for step in plan.steps:
        verdict, _ = get_simulated_verdict(step.side_effects, step.tools)
        if verdict == "DENY":
            side_effects_str = (
                ", ".join(step.side_effects) if step.side_effects else "none"
            )
            print(
                f"  - {step.goal} ({side_effects_str} side effect{'s' if len(step.side_effects) > 1 else ''})"
            )

    print()
    print("=" * 70)
    print("RESULT: Agent stayed within the approved task boundary")
    print("=" * 70)
    print("""
The Stage0 runtime guard prevented the agent from:

1. Escalating from safe analysis into high-risk action
2. Publishing, deploying, or extending loop behavior without explicit guardrails

Key API behavior:
- HIGH severity issues (SIDE_EFFECTS_NEED_GUARDRAILS) trigger DENY
- Loop-like or under-specified follow-up actions can trigger DEFER
- MEDIUM severity issues require Pro plan for DENY
- Free tier can still get DENY for high-risk operations

To run with real Stage0 validation, configure STAGE0_API_KEY.
""")


if __name__ == "__main__":
    main()
