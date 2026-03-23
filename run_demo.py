#!/usr/bin/env python3
"""Main demo runner for stage0-agent-runtime-guard."""

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

from demo.scenarios import DEFAULT_SCENARIO_KEY, get_scenario, list_scenarios


def print_header(title: str):
    width = 70
    print()
    print("=" * width)
    print(title.center(width))
    print("=" * width)
    print()


def print_section(title: str):
    print()
    print("-" * 70)
    print(f"  {title}")
    print("-" * 70)
    print()


def parse_args() -> argparse.Namespace:
    scenario_choices = ["all"] + [scenario.key for scenario in list_scenarios()]
    parser = argparse.ArgumentParser(
        description="Run the Stage0 runtime guard demo in interactive or non-interactive mode."
    )
    parser.add_argument(
        "--scenario",
        choices=scenario_choices,
        default=DEFAULT_SCENARIO_KEY,
        help="Scenario to run. Use 'all' to run every customer-facing scenario.",
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Run without pause prompts so the demo works in CI, recordings, and scripted tests.",
    )
    parser.add_argument(
        "--concise",
        action="store_true",
        help="Show buyer-friendly comparison output instead of verbose execution logs.",
    )
    parser.add_argument(
        "--simulated",
        action="store_true",
        help="Force simulated mode even with API key. Use for deterministic recordings.",
    )
    return parser.parse_args()


def check_setup():
    """Check if the environment is properly set up."""
    issues = []

    env_file = Path(__file__).parent / ".env"
    if not env_file.exists():
        issues.append(".env file not found. Copy .env.example to .env")

    load_dotenv()
    api_key = os.getenv("STAGE0_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        issues.append("STAGE0_API_KEY not configured in .env")

    return issues


def pause(prompt: str, auto: bool) -> None:
    if auto:
        return
    input(prompt)


def run_single_scenario_concise(scenario_key: str, simulated: bool = False) -> None:
    from demo.output_formatter import StepSummary, format_comparison_table
    from demo.scenarios import get_scenario
    from stage0.client import Verdict

    scenario = get_scenario(scenario_key)

    unguarded_steps = _collect_execution_steps(
        scenario_key, guarded=False, simulated=simulated
    )
    guarded_steps = _collect_execution_steps(
        scenario_key, guarded=True, simulated=simulated
    )

    output = format_comparison_table(
        scenario_title=scenario.title,
        scenario_goal=scenario.goal,
        why_it_matters=scenario.why_it_matters,
        unguarded_steps=unguarded_steps,
        guarded_steps=guarded_steps,
        unguarded_risk=scenario.unguarded_risk,
        guarded_outcome=scenario.guarded_outcome,
    )
    print(output)


def _collect_execution_steps(
    scenario_key: str, guarded: bool, simulated: bool = False
) -> list:
    import io
    import sys
    from agent import Agent
    from demo.scenarios import get_scenario
    from demo.output_formatter import StepSummary
    from stage0.client import Verdict

    scenario = get_scenario(scenario_key)

    old_stdout = sys.stdout
    sys.stdout = io.StringIO()

    try:
        stage0_client = None
        effective_guarded = guarded and not simulated

        if guarded and not simulated:
            from stage0 import Stage0Client

            try:
                stage0_client = Stage0Client()
            except ValueError:
                effective_guarded = False

        agent = Agent(stage0_client=stage0_client)
        result = agent.run(scenario.goal, guarded=effective_guarded)
    finally:
        sys.stdout = old_stdout

    steps = []
    for r in result.results:
        if simulated and guarded:
            from demo.with_stage0 import get_simulated_verdict

            verdict_str, reason = get_simulated_verdict(
                r.step.side_effects, r.step.tools
            )
            if verdict_str == "DENY":
                verdict = Verdict.DENY
            elif verdict_str == "DEFER":
                verdict = Verdict.DEFER
            else:
                verdict = Verdict.ALLOW
        else:
            verdict = (
                r.stage0_verdict
                if effective_guarded and r.stage0_verdict
                else Verdict.ALLOW
            )
            reason = r.stage0_reason or ""

        steps.append(
            StepSummary(
                step_id=r.step.step_id,
                goal=r.step.goal,
                step_type=r.step.step_type.value,
                side_effects=r.step.side_effects,
                verdict=verdict,
                reason=reason,
                executed=r.success and not r.skipped,
            )
        )

    return steps


def run_single_scenario(scenario_key: str, auto: bool) -> None:
    """Run the guarded and unguarded demos for a single scenario."""
    scenario = get_scenario(scenario_key)

    print_section(f"SCENARIO: {scenario.title}")
    print(f"Goal: {scenario.goal}")
    print(f"Why buyers care: {scenario.why_it_matters}")
    print()

    print_section("DEMO 1: Agent WITHOUT Stage0 Runtime Guard")
    from demo.without_stage0 import main as run_without_stage0

    run_without_stage0(scenario_key=scenario_key)

    pause("Press Enter to continue to the guarded demo...", auto)

    print_section("DEMO 2: Agent WITH Stage0 Runtime Guard")
    from demo.with_stage0 import main as run_with_stage0

    run_with_stage0(scenario_key=scenario_key)

    print_section("SCENARIO OUTCOME")
    print(f"Unguarded risk: {scenario.unguarded_risk}")
    print(f"Guarded outcome: {scenario.guarded_outcome}")
    print()


def print_portfolio_summary(selected_scenarios: list[str]) -> None:
    """Print a final summary across scenarios."""
    print_section("WHY THIS ATTRACTS CUSTOMERS")
    print("Stage0 becomes easier to sell when buyers can see the same product solve:")
    for scenario_key in selected_scenarios:
        scenario = get_scenario(scenario_key)
        print(f"  - {scenario.title}: {scenario.guarded_outcome}")
    print()
    print("Key takeaway:")
    print(
        "  Research can stay useful while risky publication, deployment, and runaway retry paths stay blocked."
    )
    print()
    print("Next step for buyers:")
    print("  1. Get an API key from https://signalpulse.org")
    print("  2. Replace your agent's self-approval with Stage0 /check")
    print(
        "  3. Add approval gates before publish, refund, deploy, or loop-extension side effects"
    )
    print()


def main():
    args = parse_args()
    selected_scenarios = (
        [scenario.key for scenario in list_scenarios()]
        if args.scenario == "all"
        else [args.scenario]
    )

    if args.concise:
        for scenario_key in selected_scenarios:
            run_single_scenario_concise(scenario_key, simulated=args.simulated)
            print()
    else:
        print_header("stage0-agent-runtime-guard Demo")
        print("This demonstration shows why autonomous AI agents require")
        print("runtime execution guards, using customer-facing scenarios.")
        print()
        print("Scenarios in this build:")
        for scenario in list_scenarios():
            print(f"  - {scenario.key}: {scenario.title}")
        print()

        issues = check_setup()
        if issues:
            print("NOTE: Setup issues detected:")
            for issue in issues:
                print(f"  - {issue}")
            print()
            print("The guarded demo will fall back to simulated Stage0 responses.")
            print("Configure a real API key to show live policy decisions.")
            print()
            pause("Press Enter to continue...", args.auto)

        for index, scenario_key in enumerate(selected_scenarios):
            if index > 0:
                pause("Press Enter to continue to the next scenario...", args.auto)
            run_single_scenario(scenario_key, auto=args.auto)

        print_portfolio_summary(selected_scenarios)


if __name__ == "__main__":
    main()
