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

    executed_count = sum(1 for item in result.results if item.success and not item.skipped)
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


def run_simulated_demo(scenario_key: str):
    """Run demo with simulated Stage0 responses."""
    scenario = get_scenario(scenario_key)

    print("=" * 70)
    print("SIMULATED DEMO: What Stage0 would do")
    print("=" * 70)
    print()
    print("Since no API key is available, this shows simulated responses")
    print("that demonstrate how Stage0 would guard the agent.")
    print()

    if scenario_key == "agent_loops":
        steps = [
            {
                "id": 1,
                "goal": f"Collect runtime history for: {scenario.goal}",
                "type": "research",
                "side_effects": [],
                "simulated_verdict": "ALLOW",
                "simulated_reason": "Observing existing run state is informational only",
            },
            {
                "id": 2,
                "goal": f"Analyze retry counts and repeated tool paths for: {scenario.goal}",
                "type": "analysis",
                "side_effects": [],
                "simulated_verdict": "ALLOW",
                "simulated_reason": "Loop analysis is within scope and has no side effects",
            },
            {
                "id": 3,
                "goal": f"Generate an operator handoff summary for: {scenario.goal}",
                "type": "output",
                "side_effects": [],
                "simulated_verdict": "ALLOW",
                "simulated_reason": "A bounded handoff is safe and reviewable",
            },
            {
                "id": 4,
                "goal": f"Keep retrying the same workflow for: {scenario.goal}",
                "type": "synthesis",
                "side_effects": ["loop"],
                "simulated_verdict": "DEFER",
                "simulated_reason": "Loop threshold reached: human confirmation required before extending retry budget",
            },
            {
                "id": 5,
                "goal": f"Re-run the same sensitive recovery action for: {scenario.goal}",
                "type": "output",
                "side_effects": ["loop", "deploy"],
                "simulated_verdict": "DEFER",
                "simulated_reason": "Repeated side effects detected: require run_id review and policy escalation before continuing",
            },
        ]
    else:
        steps = [
            {
                "id": 1,
                "goal": f"Collect source material for: {scenario.goal}",
                "type": "research",
                "side_effects": [],
                "simulated_verdict": "ALLOW",
                "simulated_reason": "Informational research with no side effects",
            },
            {
                "id": 2,
                "goal": f"Analyze key constraints and trade-offs for: {scenario.goal}",
                "type": "analysis",
                "side_effects": [],
                "simulated_verdict": "ALLOW",
                "simulated_reason": "Informational analysis within scope",
            },
            {
                "id": 3,
                "goal": f"Generate an internal summary draft for: {scenario.goal}",
                "type": "output",
                "side_effects": [],
                "simulated_verdict": "ALLOW",
                "simulated_reason": "Informational output, no actionable advice",
            },
            {
                "id": 4,
                "goal": f"Approve or publish the next customer-facing action for: {scenario.goal}",
                "type": "synthesis",
                "side_effects": ["publish"],
                "simulated_verdict": "DENY",
                "simulated_reason": "HIGH severity: SIDE_EFFECTS_NEED_GUARDRAILS - 'publish' side effect without guardrails",
            },
            {
                "id": 5,
                "goal": f"Use sensitive tools to change live state for: {scenario.goal}",
                "type": "output",
                "side_effects": ["deploy"],
                "simulated_verdict": "DENY",
                "simulated_reason": "HIGH severity: SIDE_EFFECTS_NEED_GUARDRAILS - 'deploy' side effect without guardrails",
            },
        ]

    print(f"Plan: {scenario.goal}")
    print("-" * 70)
    print()

    executed_outputs: list[str] = []

    for step in steps:
        print(f"Step {step['id']}: {step['goal']}")
        print(f"  Type: {step['type']}")
        print(f"  Side Effects: {step['side_effects'] or 'None'}")
        print(f"  Stage0 Verdict: {step['simulated_verdict']}")
        print(f"  Reason: {step['simulated_reason']}")

        if step["simulated_verdict"] == "ALLOW":
            print("  Action: EXECUTING...")
            executed_outputs.append(step["goal"])
        elif step["simulated_verdict"] == "DEFER":
            print("  Action: SKIPPED (requires human review)")
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
    if scenario_key == "agent_loops":
        print("Steps Deferred (DEFER):")
        print("  - Keep retrying the same workflow (loop budget exceeded)")
        print("  - Re-run the same sensitive recovery action (repeat side effects)")
    else:
        print("Steps Denied (DENY):")
        print("  - Approve or publish the next customer-facing action (publish side effect)")
        print("  - Use sensitive tools to change live state (deploy side effect)")

    print()
    print("=" * 70)
    print("RESULT: Agent stayed within the approved task boundary")
    print("=" * 70)
    print(
        """
The Stage0 runtime guard prevented the agent from:

1. Escalating from safe analysis into high-risk action
2. Publishing, deploying, or extending loop behavior without explicit guardrails

Key API behavior:
- HIGH severity issues (SIDE_EFFECTS_NEED_GUARDRAILS) trigger DENY
- Loop-like or under-specified follow-up actions can trigger DEFER
- MEDIUM severity issues require Pro plan for DENY
- Free tier can still get DENY for high-risk operations

To run with real Stage0 validation, configure STAGE0_API_KEY.
"""
    )


if __name__ == "__main__":
    main()
