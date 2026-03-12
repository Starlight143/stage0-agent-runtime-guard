# stage0-agent-runtime-guard

`stage0-agent-runtime-guard` is a customer-facing proof-of-value demo for [SignalPulse](https://signalpulse.org/), showing why AI agents need a runtime policy authority before they can publish, deploy, or otherwise create side effects.

This repository is intentionally lightweight:

- a small autonomous agent
- a Stage0 API client
- side-by-side guarded vs unguarded demos
- customer-oriented scenarios you can show in a sales call, pilot, or internal evaluation

If you want the full product surface, dashboards, billing flows, API-key lifecycle, and hosted runtime described in the broader SignalPulse app, this repo is the shortest path to understanding the core runtime-guard value proposition.

## Why buyers care

Most teams already know how to make an agent produce text. The hard part is stopping the agent from quietly escalating into actions that should require policy, approval, or stronger guardrails.

Without a runtime guard, an agent can:

- turn research into advice
- turn drafting into publishing
- turn analysis into deployment
- turn "help me think" into "I already executed it"

Stage0 addresses that by validating execution intent before the action happens.

## What this demo proves

This repo demonstrates the boundary between:

- useful bounded assistance
- unsafe autonomous escalation

The demo intentionally compares two modes:

1. `WITHOUT Stage0`
   The agent executes every planned step, including higher-risk steps that go beyond the user's original request.
2. `WITH Stage0`
   The agent still completes safe informational work, but Stage0 denies steps that attempt to publish or deploy without explicit guardrails.

## Customer scenarios included

This repository now includes three scenarios designed to map to common buyer conversations:

1. `frameworks`
   Research assistant for AI product teams. The agent should research and summarize, but should not silently become an implementation advisor.
2. `policy_publish`
   Customer-facing content publisher. The agent can draft and analyze, but should not publish outward-facing claims without approval.
3. `deployment`
   Production ops assistant. The agent can investigate incidents, but should not approve or execute rollout changes on its own.

These scenarios are useful for:

- AI SaaS founders
- internal tools teams
- platform and DevOps teams
- buyers evaluating runtime safety controls for agents

## Quick start

### Prerequisites

- Python 3.10 or newer
- A Stage0 API key from [SignalPulse](https://signalpulse.org/) if you want live policy decisions

### Setup

```bash
git clone https://github.com/Starlight143/stage0-agent-runtime-guard.git
cd stage0-agent-runtime-guard
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Then set:

```env
STAGE0_API_KEY=your_api_key_here
STAGE0_BASE_URL=https://api.signalpulse.org
```

If no API key is configured, the guarded demo falls back to simulated Stage0 responses so you can still demonstrate the control flow.

## Run the demo

### Run one scenario interactively

```bash
python run_demo.py --scenario frameworks
```

### Run a scenario without pause prompts

```bash
python run_demo.py --scenario deployment --auto
```

### Run every scenario in sequence

```bash
python run_demo.py --scenario all --auto
```

## Expected outcome

For each scenario, you will see:

1. an unguarded run
2. a guarded run
3. the exact steps that Stage0 denied
4. a summary of why those denied steps matter commercially and operationally

The important observation is not "the agent was blocked." The real value is:

- safe work still proceeds
- risky work is denied before execution
- the guard is external to the agent

## Integrate Stage0 into your own agent

The minimum integration is intentionally small:

```python
from stage0 import Stage0Client
from stage0.client import Verdict

client = Stage0Client()
response = client.check_goal(
    goal="Publish the weekly changelog",
    success_criteria=["Post to the public changelog"],
    constraints=["human approval required"],
    tools=["shell"],
    side_effects=["publish"],
)

if response.verdict != Verdict.ALLOW:
    raise RuntimeError(response.reason)
```

In a real implementation, you should validate every execution step, not just the top-level task.

## Repository structure

```text
agent/              Agent planning and execution logic
demo/               Guarded and unguarded scenario runners
stage0/             Stage0 API client
run_demo.py         Multi-scenario demo entrypoint
```

## What changed in this repo

This repo has been updated to better support customer conversion and live evaluation:

- richer customer-facing demo scenarios
- non-interactive CLI mode for recordings and scripted demos
- clearer environment configuration for hosted Stage0
- stronger buyer-oriented README positioning

## When to use this repo vs the full app

Use this repo when you want to:

- show the concept quickly
- demo the difference between guarded and unguarded execution
- validate runtime guard behavior before a larger integration
- support customer conversations with a minimal example

Use the broader SignalPulse application when you want:

- account management
- hosted billing flows
- API key lifecycle and issuance
- dashboards, logs, and analytics
- a fuller product experience

## Get access

To try the real Stage0 runtime:

1. Visit [signalpulse.org](https://signalpulse.org/)
2. Create an account
3. Generate an API key
4. Re-run this demo with your key in `.env`

## License

See the repository license and remote project terms before production use.
