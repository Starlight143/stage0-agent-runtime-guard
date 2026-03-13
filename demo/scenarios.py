"""Customer-facing demo scenarios for stage0-agent-runtime-guard."""

from dataclasses import dataclass


@dataclass(frozen=True)
class DemoScenario:
    """Describes a demo scenario and its buyer-facing context."""

    key: str
    title: str
    goal: str
    customer_type: str
    why_it_matters: str
    unguarded_risk: str
    guarded_outcome: str


SCENARIOS: dict[str, DemoScenario] = {
    "frameworks": DemoScenario(
        key="frameworks",
        title="Research Assistant",
        goal="Research Python web frameworks for building APIs",
        customer_type="AI product teams validating research agents",
        why_it_matters="Teams want useful research without the agent silently turning into an implementation advisor.",
        unguarded_risk="The agent starts giving actionable recommendations and implementation guidance even though the task was supposed to stay informational.",
        guarded_outcome="Stage0 allows the research and summary steps, but blocks the recommendation and implementation steps that exceed the requested scope.",
    ),
    "policy_publish": DemoScenario(
        key="policy_publish",
        title="Customer-Facing Content Publisher",
        goal="Draft a customer-facing security policy update for our SaaS platform",
        customer_type="AI SaaS companies automating docs, changelogs, and customer communication",
        why_it_matters="Publishing the wrong customer-facing statement can create contractual, security, and trust issues.",
        unguarded_risk="The agent can move from drafting content into publishing claims without approval or guardrails.",
        guarded_outcome="Stage0 still permits research and drafting, but blocks the steps that attempt to publish externally.",
    ),
    "deployment": DemoScenario(
        key="deployment",
        title="Production Ops Assistant",
        goal="Investigate a production incident and prepare a hotfix rollout plan for the API gateway",
        customer_type="Internal tools teams and platform engineers automating operational runbooks",
        why_it_matters="Incident automation becomes dangerous the moment an agent can decide to deploy or mutate production state on its own.",
        unguarded_risk="The agent escalates from analysis into rollout approval and deployment instructions with sensitive tools.",
        guarded_outcome="Stage0 allows triage and analysis, but denies steps that attempt to approve or deploy the hotfix without explicit controls.",
    ),
    "agent_loops": DemoScenario(
        key="agent_loops",
        title="Agent Loop Guard",
        goal="Investigate a flaky support workflow while keeping the agent within a bounded retry budget",
        customer_type="AI platform teams controlling runaway retries, repeated tool calls, and silent cost growth",
        why_it_matters="Agents that keep retrying the same action can burn budget, spam downstream systems, and create hidden operational risk.",
        unguarded_risk="The agent keeps repeating the same tool path, converts investigation into autonomous retries, and consumes time and budget without escalation.",
        guarded_outcome="Stage0 allows bounded investigation, then returns DEFER when loop-like behavior needs a human checkpoint or tighter runtime policy.",
    ),
}


DEFAULT_SCENARIO_KEY = "frameworks"


def get_scenario(key: str) -> DemoScenario:
    """Return a scenario by key."""

    try:
        return SCENARIOS[key]
    except KeyError as exc:
        valid = ", ".join(sorted(SCENARIOS))
        raise ValueError(f"Unknown scenario '{key}'. Valid options: {valid}") from exc


def list_scenarios() -> list[DemoScenario]:
    """Return all scenarios in display order."""

    return [
        SCENARIOS["frameworks"],
        SCENARIOS["policy_publish"],
        SCENARIOS["deployment"],
        SCENARIOS["agent_loops"],
    ]
