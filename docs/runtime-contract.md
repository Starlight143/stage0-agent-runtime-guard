# Runtime Contract

This document mirrors the current public SignalPulse Stage0 runtime shape at a practical level so buyers and implementers can understand what to send and what to log.

## Request shape

The hosted `/check` contract supports the usual top-level fields:

- `goal`
- `success_criteria`
- `constraints`
- `tools`
- `side_effects`
- `pro`

The important update is `context`. This is where runtime facts belong.

Common context fields:

- `actor_role`
- `approval_status`
- `approved_by`
- `approved_at`
- `environment`
- `request_channel`
- `run_id`
- `current_iteration`
- `elapsed_seconds`
- `current_tool`
- `recent_tools`
- `cumulative_cost_usd`
- `target_resources`
- `active_mcp_servers`
- `tenant_id`
- `target_tenants`
- `output_policy`

Example payload:

```json
{
  "goal": "Deploy the payments service to production",
  "success_criteria": ["Deployment completes safely"],
  "constraints": [
    "approval required",
    "required_role:platform_admin",
    "allowed_environment:staging,production",
    "max_iterations:3",
    "timeout:300s",
    "max_cost_usd:5"
  ],
  "tools": ["argo_cd", "slack"],
  "side_effects": ["deployment", "external notification"],
  "context": {
    "run_id": "run_9f3d7f51",
    "actor_role": "platform_admin",
    "approval_status": "approved",
    "approved_by": "ops-lead@company.com",
    "approved_at": "2026-03-15T09:30:00Z",
    "environment": "production",
    "request_channel": "dashboard",
    "current_iteration": 1,
    "elapsed_seconds": 42,
    "current_tool": "argo_cd",
    "recent_tools": ["github_actions"],
    "cumulative_cost_usd": 0.18
  },
  "pro": true
}
```

## Response shape

The newer hosted response is richer than a simple allow/deny:

- `decision`
- `verdict`
- `risk_score`
- `high_risk`
- `issues`
- `clarifying_questions`
- `defer_questions`
- `guardrails`
- `guardrail_checks`
- `value_findings`
- `cost_estimate`
- `request_id`
- `policy_pack_version`
- `policy_version`
- `timestamp`
- `evaluated_at`
- `decision_trace_summary`
- `cached`

Operationally important fields:

- `decision` tells you the decision posture: `GO`, `NO_GO`, `DEFER`, or `ERROR`
- `verdict` is the action gate you should enforce: `ALLOW`, `DENY`, or `DEFER`
- `request_id` should be copied into your own logs and approval records
- `policy_version` or `policy_pack_version` should be stored for audit traceability
- `guardrail_checks` helps explain which policy families were satisfied or violated

## Integration guidance

Use this sequence in production:

1. Build the payload immediately before tool execution.
2. Include real runtime context instead of relying only on prompt text.
3. Treat `verdict` as the authorization boundary.
4. Persist `request_id` and `policy_version` with your own execution record.
5. Fail closed if the decision cannot be trusted.

## Why this matters

The source repo now documents more than simple high-risk side effects. It explicitly supports runtime facts for:

- approval evidence
- actor and role checks
- environment scoping
- request channel restrictions
- loop and cost controls
- internal-tool and MCP authorization
- AI SaaS tenant and output policy controls
