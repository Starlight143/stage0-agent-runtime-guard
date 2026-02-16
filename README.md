# stage0-agent-runtime-guard

A demonstration project showing why autonomous AI agents require runtime execution guards.

## Problem

Autonomous AI agents operate by planning and executing sequences of actions to achieve goals. Without external oversight, an agent may:

- Execute actions that exceed its intended scope
- Produce outputs that violate safety constraints
- Make decisions based on incomplete context
- Chain actions in ways that were not anticipated

Traditional prompt-based constraints are insufficient because:

1. Agents can reinterpret or circumvent instructions
2. Complex action chains create emergent behaviors
3. No external authority validates execution intent
4. Violations are only discovered after execution

## Why Runtime Guards Matter

A runtime guard acts as an external policy authority that validates every execution intent **before** it happens. This differs from:

- **Prompt constraints**: Easily bypassed or reinterpreted by the agent
- **Post-hoc filtering**: Only catches violations after damage is done
- **Human review**: Does not scale and introduces latency

Key properties of a runtime guard:

1. **External to the agent**: The agent cannot modify or bypass the guard
2. **Pre-execution validation**: Actions are approved or denied before execution
3. **Consistent policy enforcement**: Same rules apply regardless of agent reasoning
4. **Auditable decisions**: Every verdict is logged with reasoning

## What This Project Demonstrates

This project implements a research-style autonomous agent that:

1. Receives a research goal
2. Plans a sequence of execution steps
3. Executes steps to produce a structured report

The project includes two demo modes:

- **Without Stage0**: Agent executes freely, producing overreaching output
- **With Stage0**: Every step is validated; unsafe actions are denied

## Without vs With Stage0

### Without Stage0 (`demo/without_stage0.py`)

The agent plans and executes without external validation:

```
Goal: Research Python web frameworks
Plan:
  1. Search for popular Python web frameworks
  2. Compare features and performance
  3. Generate recommendation report
  4. Provide implementation guidance
  5. Include security best practices

Result: Agent produces detailed implementation guidance and security recommendations
that may exceed the intended research scope.
```

### With Stage0 (`demo/with_stage0.py`)

The same agent with Stage0 validation:

```
Goal: Research Python web frameworks
Plan:
  1. Search for popular Python web frameworks
     → Stage0: ALLOW (informational research)
  2. Compare features and performance
     → Stage0: ALLOW (informational research)
  3. Generate recommendation report
     → Stage0: ALLOW (informational output)
  4. Provide implementation guidance
     → Stage0: DENY (exceeds research scope, provides actionable advice)
  5. Include security best practices
     → Stage0: DENY (exceeds research scope, provides actionable advice)

Result: Agent produces research report constrained to informational content.
```

## How to Run

### Prerequisites

- Python 3.10 or higher
- Stage0 API key from SignalPulse

### Setup

1. Clone the repository:

```bash
git clone <repository-url>
cd stage0-agent-runtime-guard
```

2. Create virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Configure environment:

```bash
cp .env.example .env
# Edit .env and add your STAGE0_API_KEY
```

### Run Demos

Run both demos to see the contrast:

```bash
python run_demo.py
```

Or run individually:

```bash
# Without Stage0 (unsafe execution)
python -m demo.without_stage0

# With Stage0 (guarded execution)
python -m demo.with_stage0
```

### Expected Output

The demo will show:

1. Agent planning phase
2. Execution steps (with Stage0 verdicts in guarded mode)
3. Final output comparison

The guarded demo will demonstrate at least one denied action, showing how Stage0 constrains agent behavior.
