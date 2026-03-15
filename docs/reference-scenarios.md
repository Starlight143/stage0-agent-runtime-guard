# Reference Scenarios

These are buyer-facing reference scenarios adapted from the main SignalPulse site. They are not claims of customer logos or live proof. They are concrete workflow shapes that help a prospect understand where Stage0 belongs.

## Fintech approvals

Relevant workflow:

- payouts
- account changes
- external notifications

What Stage0 should control:

- approval-gated payouts
- role-aware access to sensitive customer data
- customer-visible communication that should defer until approved

What buyers usually ask:

- how approval evidence is represented
- whether role checks happen at runtime or only in the app
- which request fields are logged for incident review

## Enterprise deployment control

Relevant workflow:

- deploy approvals
- database migrations
- rollback readiness

What Stage0 should control:

- environment-aware deploy gating
- change-window checks
- explicit approval evidence before any production tool runs

What buyers usually ask:

- what happens if Stage0 times out
- who owns the final enforcement step
- whether the decision is traceable with `request_id` and policy version

## Internal tools and MCP servers

The latest backend guardrails now explicitly cover internal-tool controls such as:

- `resource_scope`
- `allowed_mcp_servers`

Good buyer language:

- "The model does not self-authorize the MCP call."
- "The server-side tool handler asks Stage0 before the tool runs."
- "Resource and server allowlists are evaluated from runtime context, not just from prompt text."

## AI SaaS guardrails

The latest backend guardrails also cover AI SaaS controls such as:

- tenant isolation
- customer-visible side effects
- output policy
- request channel throttles

This matters for prospects building:

- support agents
- billing assistants
- customer notification flows
- multi-tenant internal copilots
