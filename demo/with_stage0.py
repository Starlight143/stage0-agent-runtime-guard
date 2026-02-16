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
from stage0 import Stage0Client


def check_api_key() -> bool:
    """Check if Stage0 API key is configured."""
    api_key = os.getenv("STAGE0_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        return False
    return True


def main():
    """Run the guarded agent demo."""
    print("=" * 70)
    print("DEMO: Agent WITH Stage0 Runtime Guard")
    print("=" * 70)
    print()
    
    # Check for API key
    if not check_api_key():
        print("ERROR: STAGE0_API_KEY environment variable is not set.")
        print()
        print("To run this demo, you need a Stage0 API key from SignalPulse.")
        print()
        print("Setup instructions:")
        print("1. Copy .env.example to .env")
        print("2. Add your STAGE0_API_KEY to .env")
        print("3. Run this demo again")
        print()
        print("If you don't have an API key, the demo will show simulated")
        print("Stage0 responses to demonstrate the guard behavior.")
        print()
        
        # Run with simulated responses for demonstration
        run_simulated_demo()
        return
    
    print("Stage0 API key found. Connecting to Stage0...")
    print()
    print("This demo shows an agent where EVERY execution step is validated")
    print("by Stage0 before execution. Steps that exceed scope are DENIED.")
    print()
    print("Note: The demo intentionally includes steps with HIGH risk side effects")
    print("(publish, deploy) to trigger DENY verdicts from the API.")
    print()
    
    # Create Stage0 client
    try:
        stage0_client = Stage0Client()
    except ValueError as e:
        print(f"Error initializing Stage0 client: {e}")
        return
    
    # Create agent WITH Stage0 client
    agent = Agent(stage0_client=stage0_client)
    
    # Run with guarded=True (default, but explicit here)
    goal = "Research Python web frameworks for building APIs"
    result = agent.run(goal, guarded=True)
    
    # Show the final output
    print()
    print("=" * 70)
    print("FINAL OUTPUT (Constrained by Stage0)")
    print("=" * 70)
    print(result.final_output)
    
    # Show what was denied
    denied_steps = result.get_denied_steps()
    if denied_steps:
        print()
        print("=" * 70)
        print("DENIED STEPS (Stage0 prevented execution)")
        print("=" * 70)
        for denied in denied_steps:
            print(f"\nStep {denied.step.step_id}: {denied.step.goal}")
            print(f"Reason: {denied.stage0_reason}")
            if denied.stage0_verdict:
                print(f"Verdict: {denied.stage0_verdict.value}")
    
    # Summary
    print()
    print("=" * 70)
    print("ANALYSIS: How Stage0 protected the execution")
    print("=" * 70)
    
    executed_count = sum(1 for r in result.results if r.success and not r.skipped)
    denied_count = len(denied_steps)
    
    print(f"""
With Stage0 validation:

1. Steps 1-3: ALLOWED
   - Research, analysis, and informational reports
   - No high-risk side effects, proper constraints
   
2. Steps 4-5: DENIED
   - Step 4: Declares "publish" side effect without guardrails
     → Triggers SIDE_EFFECTS_NEED_GUARDRAILS (HIGH severity)
   - Step 5: Uses "shell" tool with "deploy" side effect
     → Triggers SIDE_EFFECTS_NEED_GUARDRAILS (HIGH severity)
     → Also triggers SENSITIVE_TOOLS_NEED_CONSTRAINTS (MEDIUM severity)

Result: The agent produced a focused research output without
executing steps that could publish or deploy content.

This demonstrates the value of runtime guards:
- External authority validates intent before execution
- Agent cannot self-approve actions
- High-risk side effects are blocked without proper guardrails
- Violations are prevented, not just detected after the fact

Stats:
- Steps executed: {executed_count}
- Steps denied: {denied_count}
""")


def run_simulated_demo():
    """Run demo with simulated Stage0 responses."""
    print("=" * 70)
    print("SIMULATED DEMO: What Stage0 would do")
    print("=" * 70)
    print()
    print("Since no API key is available, this shows simulated responses")
    print("that demonstrate how Stage0 would guard the agent.")
    print()
    
    # Simulated plan steps with side effects
    steps = [
        {
            "id": 1,
            "goal": "Search for information about Python web frameworks",
            "type": "research",
            "side_effects": [],
            "simulated_verdict": "ALLOW",
            "simulated_reason": "Informational research with no side effects"
        },
        {
            "id": 2,
            "goal": "Analyze and compare Python web frameworks",
            "type": "analysis",
            "side_effects": [],
            "simulated_verdict": "ALLOW",
            "simulated_reason": "Informational analysis within scope"
        },
        {
            "id": 3,
            "goal": "Generate a summary report on Python web frameworks",
            "type": "output",
            "side_effects": [],
            "simulated_verdict": "ALLOW",
            "simulated_reason": "Informational output, no actionable advice"
        },
        {
            "id": 4,
            "goal": "Provide actionable recommendations for Python web frameworks",
            "type": "synthesis",
            "side_effects": ["publish"],
            "simulated_verdict": "DENY",
            "simulated_reason": "HIGH severity: SIDE_EFFECTS_NEED_GUARDRAILS - 'publish' side effect without guardrails"
        },
        {
            "id": 5,
            "goal": "Provide step-by-step implementation guidance",
            "type": "output",
            "side_effects": ["deploy"],
            "simulated_verdict": "DENY",
            "simulated_reason": "HIGH severity: SIDE_EFFECTS_NEED_GUARDRAILS - 'deploy' side effect without guardrails"
        }
    ]
    
    print("Plan: Research Python web frameworks for building APIs")
    print("-" * 70)
    print()
    
    executed_outputs = []
    
    for step in steps:
        print(f"Step {step['id']}: {step['goal']}")
        print(f"  Type: {step['type']}")
        print(f"  Side Effects: {step['side_effects'] or 'None'}")
        print(f"  Stage0 Verdict: {step['simulated_verdict']}")
        print(f"  Reason: {step['simulated_reason']}")
        
        if step['simulated_verdict'] == "ALLOW":
            print(f"  Action: EXECUTING...")
            executed_outputs.append(step['goal'])
        else:
            print(f"  Action: SKIPPED (not authorized)")
        
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
    print("  - Provide actionable recommendations (publish side effect)")
    print("  - Provide step-by-step implementation guidance (deploy side effect)")
    
    print()
    print("=" * 70)
    print("RESULT: Agent stayed within research scope")
    print("=" * 70)
    print("""
The Stage0 runtime guard prevented the agent from:

1. Publishing actionable recommendations without guardrails
2. Deploying implementation guidance

Key API behavior:
- HIGH severity issues (SIDE_EFFECTS_NEED_GUARDRAILS) trigger DENY
- MEDIUM severity issues require Pro plan for DENY
- Free tier can still get DENY for high-risk operations

To run with real Stage0 validation, configure STAGE0_API_KEY.
""")


if __name__ == "__main__":
    main()
