"""Buyer-friendly demo output formatter.

This module provides clean, concise output formatting for the demo,
designed for sales calls and buyer presentations.
"""

from dataclasses import dataclass
from typing import Optional

from stage0.client import Verdict


@dataclass
class StepSummary:
    step_id: int
    goal: str
    step_type: str
    side_effects: list[str]
    verdict: Optional[Verdict]
    reason: str
    executed: bool


def format_comparison_table(
    scenario_title: str,
    scenario_goal: str,
    why_it_matters: str,
    unguarded_steps: list[StepSummary],
    guarded_steps: list[StepSummary],
    unguarded_risk: str,
    guarded_outcome: str,
) -> str:
    """Format a side-by-side comparison of guarded vs unguarded execution."""

    lines = []

    lines.append("=" * 70)
    lines.append(f"  SCENARIO: {scenario_title}")
    lines.append("=" * 70)
    lines.append("")
    lines.append(f"Goal: {scenario_goal}")
    lines.append("")
    lines.append(f"Why this matters: {why_it_matters}")
    lines.append("")

    lines.append("-" * 70)
    lines.append("  COMPARISON: Unguarded vs Guarded")
    lines.append("-" * 70)
    lines.append("")

    max_steps = max(len(unguarded_steps), len(guarded_steps))

    for i in range(max_steps):
        unguarded = unguarded_steps[i] if i < len(unguarded_steps) else None
        guarded = guarded_steps[i] if i < len(guarded_steps) else None

        step_num = i + 1

        is_blocked = guarded is not None and guarded.verdict in (
            Verdict.DENY,
            Verdict.DEFER,
        )

        if is_blocked and guarded is not None and guarded.verdict is not None:
            goal_text = " ".join(guarded.goal.split()[:8])
            lines.append(f"  Step {step_num}: {goal_text}...")
            lines.append(f"    UNGUARDED: [OK] Executed")
            blocked_type = "DEFERRED" if guarded.verdict == Verdict.DEFER else "BLOCKED"
            lines.append(f"    GUARDED:   [{blocked_type}] {guarded.verdict.value}")
            reason_short = (
                guarded.reason[:60] + "..."
                if len(guarded.reason) > 60
                else guarded.reason
            )
            lines.append(f"               Reason: {reason_short}")
        else:
            goal = (
                unguarded.goal
                if unguarded
                else (guarded.goal if guarded else "Unknown")
            )
            goal_text = " ".join(goal.split()[:8])
            status = (
                "[OK] Executed"
                if (unguarded and unguarded.executed)
                else "[SKIP] Skipped"
            )
            lines.append(f"  Step {step_num}: {goal_text}...")
            lines.append(f"    UNGUARDED: {status}")
            lines.append(f"    GUARDED:   [ALLOW]")
        lines.append("")

    lines.append("-" * 70)
    lines.append("  KEY TAKEAWAY")
    lines.append("-" * 70)
    lines.append("")
    lines.append(f"  Without Stage0: {unguarded_risk}")
    lines.append("")
    lines.append(f"  With Stage0:    {guarded_outcome}")
    lines.append("")

    allowed_guarded = sum(1 for s in guarded_steps if s.verdict == Verdict.ALLOW)
    blocked_guarded = sum(1 for s in guarded_steps if s.verdict == Verdict.DENY)
    deferred_guarded = sum(1 for s in guarded_steps if s.verdict == Verdict.DEFER)
    total_guarded = len(guarded_steps)

    lines.append(
        f"  Stats: {total_guarded} steps -> {allowed_guarded} allowed + {blocked_guarded + deferred_guarded} blocked with Stage0"
    )
    lines.append("")

    return "\n".join(lines)


def format_quick_summary(
    scenario_key: str,
    scenario_title: str,
    guarded_steps: list[StepSummary],
    unguarded_risk: str,
    guarded_outcome: str,
) -> str:
    """Format a quick one-line summary for each scenario."""

    blocked = sum(1 for s in guarded_steps if s.verdict == Verdict.DENY)
    deferred = sum(1 for s in guarded_steps if s.verdict == Verdict.DEFER)

    if blocked > 0:
        action = f"blocked {blocked} risky step{'s' if blocked > 1 else ''}"
    elif deferred > 0:
        action = f"deferred {deferred} step{'s' if deferred > 1 else ''} for review"
    else:
        action = "allowed all steps"

    return f"  {scenario_title}: Stage0 {action}"
