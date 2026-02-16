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


def main():
    """Run the unguarded agent demo."""
    print("=" * 70)
    print("DEMO: Agent WITHOUT Stage0 Runtime Guard")
    print("=" * 70)
    print()
    print("This demo shows an agent executing freely without any external")
    print("validation. Notice how it produces outputs that may exceed the")
    print("intended research scope, including actionable recommendations")
    print("and implementation guidance.")
    print()
    print("WARNING: In a real scenario, this could lead to:")
    print("  - Advice being provided when only research was requested")
    print("  - Code generation without safety review")
    print("  - Actions that violate user expectations or policy")
    print()
    
    # Create agent WITHOUT Stage0 client
    agent = Agent(stage0_client=None)
    
    # Run with guarded=False to skip all validations
    goal = "Research Python web frameworks for building APIs"
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
2. Provided ACTIONABLE RECOMMENDATIONS (Step 4)
   - "Start with Option A if you are new"
   - "Consider Option B for production"
   
3. Provided IMPLEMENTATION GUIDANCE (Step 5)
   - Specific installation commands
   - Code examples
   - Security best practices

These outputs may be valuable, BUT:
- The user only asked for RESEARCH
- Actionable advice could be misinterpreted
- Implementation guidance could be outdated or incorrect
- No external authority validated the appropriateness

This demonstrates why runtime guards are essential for
autonomous AI agents operating in production environments.
""")


if __name__ == "__main__":
    main()
