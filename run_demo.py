#!/usr/bin/env python3
"""Main demo runner for stage0-agent-runtime-guard.

This script runs both demos to show the contrast between
unguarded and guarded agent execution.
"""

import os
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv


def print_header(title: str):
    """Print a formatted header."""
    width = 70
    print()
    print("=" * width)
    print(title.center(width))
    print("=" * width)
    print()


def print_section(title: str):
    """Print a section divider."""
    print()
    print("-" * 70)
    print(f"  {title}")
    print("-" * 70)
    print()


def check_setup():
    """Check if the environment is properly set up."""
    issues = []
    
    # Check for .env file
    env_file = Path(__file__).parent / ".env"
    if not env_file.exists():
        issues.append(".env file not found. Copy .env.example to .env")
    
    # Check for API key
    load_dotenv()
    api_key = os.getenv("STAGE0_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        issues.append("STAGE0_API_KEY not configured in .env")
    
    return issues


def main():
    """Run the complete demo."""
    print_header("stage0-agent-runtime-guard Demo")
    
    print("This demonstration shows why autonomous AI agents require")
    print("runtime execution guards. You will see two scenarios:")
    print()
    print("  1. WITHOUT Stage0: Agent executes freely, potentially overreaching")
    print("  2. WITH Stage0: Every step is validated, unsafe actions are denied")
    print()
    
    # Check setup
    issues = check_setup()
    if issues:
        print("NOTE: Setup issues detected:")
        for issue in issues:
            print(f"  - {issue}")
        print()
        print("The demo will run with simulated Stage0 responses.")
        print("For real validation, please configure your API key.")
        print()
        input("Press Enter to continue...")
    
    # Run Demo 1: Without Stage0
    print_section("DEMO 1: Agent WITHOUT Stage0 Runtime Guard")
    
    from demo.without_stage0 import main as run_without_stage0
    run_without_stage0()
    
    print()
    input("Press Enter to continue to Demo 2...")
    
    # Run Demo 2: With Stage0
    print_section("DEMO 2: Agent WITH Stage0 Runtime Guard")
    
    from demo.with_stage0 import main as run_with_stage0
    run_with_stage0()
    
    # Final comparison
    print_section("COMPARISON SUMMARY")
    
    print("""
┌─────────────────────────────────────────────────────────────────────┐
│                    WITHOUT vs WITH Stage0                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  WITHOUT Stage0:                    WITH Stage0:                    │
│  ─────────────────                  ─────────────                   │
│  ✓ All steps executed               ✓ Only approved steps executed  │
│  ✓ Full output generated            ✓ Scoped output generated       │
│  ✗ Overreaching advice              ✓ No unauthorized advice        │
│  ✗ Implementation code              ✓ No unauthorized code          │
│  ✗ No external validation           ✓ External authority validates  │
│  ✗ Agent self-approves              ✓ Agent cannot self-approve     │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│  KEY INSIGHT:                                                       │
│                                                                     │
│  Runtime guards like Stage0 are essential because:                 │
│                                                                     │
│  1. Agents cannot reliably self-constrain                          │
│  2. Prompt-based constraints are easily bypassed                    │
│  3. External validation catches what agents miss                    │
│  4. Pre-execution validation prevents, not just detects            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
""")
    
    print()
    print("Demo complete!")
    print()
    print("To integrate Stage0 into your own agents:")
    print("  1. Import: from stage0 import Stage0Client")
    print("  2. Initialize: client = Stage0Client()")
    print("  3. Validate: response = client.check_goal(intent)")
    print("  4. Enforce: Only proceed if response.verdict == ALLOW")
    print()


if __name__ == "__main__":
    main()
