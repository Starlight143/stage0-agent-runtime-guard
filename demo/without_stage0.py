"""Demo: Agent execution WITHOUT Stage0 runtime guard.

This demo shows what happens when an autonomous agent executes
without any external validation. The agent may produce outputs
that exceed its intended scope.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent import Agent
from demo.scenarios import DemoScenario, get_scenario


def print_scenario_context(scenario: DemoScenario) -> None:
    """Print the business framing for the selected scenario."""
    print(f"Scenario: {scenario.title}")
    print(f"Buyer context: {scenario.customer_type}")
    print(f"Why it matters: {scenario.why_it_matters}")
    print()


def main(scenario_key: str = "frameworks"):
    """Run the unguarded agent demo."""
    scenario = get_scenario(scenario_key)

    print("=" * 70)
    print("DEMO: Agent WITHOUT Stage0 Runtime Guard")
    print("=" * 70)
    print()
    print_scenario_context(scenario)
    print("This demo shows an agent executing freely without any external")
    print("validation. Notice how it produces outputs that may exceed the")
    print("intended task scope, including actionable recommendations,")
    print("publication decisions, or deployment guidance.")
    print()
    print("WARNING: In a real scenario, this could lead to:")
    print(f"  - {scenario.unguarded_risk}")
    print("  - Sensitive actions being prepared without external review")
    print("  - Customer trust or production safety being put at risk")
    print()
    
    # Create agent WITHOUT Stage0 client
    agent = Agent(stage0_client=None)
    
    # Run with guarded=False to skip all validations
    goal = scenario.goal
    result = agent.run(goal, guarded=False)
    
    # Show the final output
    print()
    print("=" * 70)
    print("FINAL OUTPUT (Full, unfiltered)")
    print("=" * 70)
    print(result.final_output)
    
    # Highlight potential issues
    print()
    print("=" * 70)
    print("ANALYSIS: What went wrong?")
    print("=" * 70)
    print("""
Without Stage0 validation, the agent:

1. Executed ALL planned steps without questioning scope
2. Crossed from research or analysis into execution-oriented output
   - Recommendations, approvals, or publication/deployment instructions
   - No external authority checked whether those steps were appropriate
   
3. Produced sensitive next-step guidance
   - Commands, rollout decisions, or publish-ready instructions
   - Output that a human might mistake for approved action

These outputs may be valuable, BUT:
- The user asked for bounded assistance, not autonomous escalation
- Sensitive output can be misinterpreted as approved next action
- No external runtime authority validated the appropriateness

This demonstrates why runtime guards are essential for
autonomous AI agents operating in production environments.
""")


if __name__ == "__main__":
    main()
