# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [1.1.0] - 2026-03-23

### Added
- `--concise` flag for buyer-friendly side-by-side comparison output
- `--simulated` flag for deterministic demo recordings (no API needed)
- `artifacts/` directory with pre-generated sample outputs for all scenarios
- `demo/output_formatter.py` for clean comparison table formatting
- `tests/test_scenarios.py` with smoke tests for all scenarios (9 tests total)
- Export common types (`Verdict`, `Decision`, `ExecutionIntent`, `PolicyResponse`) from `stage0/__init__.py`
- README section: "What this proves / What this does NOT prove"
- README section: Sample outputs and CLI usage examples

### Changed
- Refactored `run_simulated_demo()` to use actual planner steps instead of hardcoded steps
- Improved stats calculation in output formatter (now calculates from guarded steps directly)
- Relaxed test assertions to use `>= 3` instead of `== 5` for step counts

### Fixed
- Silent security fallback in `run_demo.py` when Stage0Client initialization fails
- Null handling for `side_effects` and `tools` in `get_simulated_verdict()`
- Live API and simulated mode now produce identical results

## [1.0.0] - 2026-03-17

### Added
- Customer-facing proof-of-value demo for SignalPulse Stage0 runtime guard
- Four demo scenarios: `frameworks`, `policy_publish`, `deployment`, `agent_loops`
- Side-by-side guarded vs unguarded execution comparison
- Stage0 API client aligned with hosted runtime contract
- Support for `ALLOW`, `DENY`, `DEFER` verdicts
- Non-interactive CLI mode (`--auto`) for recordings and scripted demos
- Reference documentation in `docs/`:
  - `runtime-contract.md`
  - `reference-scenarios.md`
  - `service-overview.md`
- Simulated Stage0 responses when no API key is configured

---

## Installation

```bash
git clone https://github.com/Starlight143/stage0-agent-runtime-guard.git
cd stage0-agent-runtime-guard
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## Known Limitations

- Demo repository, not a distributable package
- Requires Stage0 API key for live policy decisions
- Falls back to simulated responses when API key is not configured

---

## Breaking Changes Policy

This is a demo repository. Version tags mark stable checkpoints for customer evaluation.

- **Major version**: Significant demo scenario changes or removal
- **Minor version**: New scenarios or demo features
- **Patch version**: Bug fixes, documentation updates