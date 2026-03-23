"""Smoke tests for demo scenarios."""

import io
import sys
from unittest import TestCase

from demo.scenarios import list_scenarios
from agent import Agent


class ScenarioSmokeTests(TestCase):
    def test_all_scenarios_run_without_errors(self) -> None:
        for scenario in list_scenarios():
            with self.subTest(scenario=scenario.key):
                old_stdout = sys.stdout
                sys.stdout = io.StringIO()
                try:
                    agent = Agent(stage0_client=None)
                    result = agent.run(scenario.goal, guarded=False)
                    self.assertGreaterEqual(len(result.results), 3)
                    self.assertTrue(all(r.success for r in result.results))
                finally:
                    sys.stdout = old_stdout

    def test_frameworks_scenario_completes(self) -> None:
        self._run_scenario("frameworks")

    def test_policy_publish_scenario_completes(self) -> None:
        self._run_scenario("policy_publish")

    def test_deployment_scenario_completes(self) -> None:
        self._run_scenario("deployment")

    def test_agent_loops_scenario_completes(self) -> None:
        self._run_scenario("agent_loops")

    def _run_scenario(self, scenario_key: str) -> None:
        from demo.scenarios import get_scenario

        scenario = get_scenario(scenario_key)

        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            agent = Agent(stage0_client=None)
            result = agent.run(scenario.goal, guarded=False)
            self.assertGreaterEqual(len(result.results), 3)
            self.assertTrue(all(r.success for r in result.results))
        finally:
            sys.stdout = old_stdout


class OutputFormatterTests(TestCase):
    def test_format_comparison_table_produces_output(self) -> None:
        from demo.output_formatter import StepSummary, format_comparison_table
        from stage0.client import Verdict

        unguarded_steps = [
            StepSummary(1, "Step 1", "research", [], Verdict.ALLOW, "", True),
            StepSummary(2, "Step 2", "analysis", [], Verdict.ALLOW, "", True),
        ]
        guarded_steps = [
            StepSummary(1, "Step 1", "research", [], Verdict.ALLOW, "", True),
            StepSummary(
                2, "Step 2", "analysis", ["deploy"], Verdict.DENY, "Side effect", False
            ),
        ]

        output = format_comparison_table(
            "Test Scenario",
            "Test goal",
            "Test why it matters",
            unguarded_steps,
            guarded_steps,
            "Test unguarded risk",
            "Test guarded outcome",
        )

        self.assertIn("Test Scenario", output)
        self.assertIn("Test goal", output)
        self.assertIn("[OK]", output)
        self.assertIn("[BLOCKED]", output)
        self.assertIn("2 steps", output)
