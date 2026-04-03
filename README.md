# Agent Runtime (Professional Baseline)

Autonomous local agent runtime built around a runtime-first LangGraph loop:

`inject_memory -> plan -> choose_action -> execute_tool -> record_result -> decide`

## Goals

- Keep runtime execution as source of truth (not LLM claims).
- Enforce explicit tool permissions (allowlist + network gate).
- Keep operations auditable with structured logs.
- Enable production-quality workflows (CI + lint + reproducible local checks).

## Project Layout

- `core/`: graph, state, nodes, prompts, schemas
- `tools/`: terminal, files, web, memory, task management
- `sandbox/`: command execution and permission controls
- `memory/`: profile, journal, checkpoint DB access
- `channels/`: CLI/API/Telegram entry points
- `observability/`: logging and tracing hooks
- `tests/`: behavior-focused test suite

## Quick Start

### 1. Install

```bash
python -m pip install -e .[dev]
```

### 2. Configure

Create `.env` at project root:

```env
OPENAI_API_KEY=your_key
MODEL_NAME=gpt-4o
MAX_ITERATIONS=20
TOOL_TIMEOUT=30
ALLOW_NETWORK=false
```

### 3. Run

```bash
python main.py run "Create test.txt with Hello"
python main.py history
```

## Engineering Commands

```bash
make install-dev
make lint
make test
make check
```

## Quality Baseline

- CI on push/PR (`.github/workflows/ci.yml`)
- Static analysis via `ruff`
- Test suite via `pytest`
- Type checks ready via `mypy` config

## Security Posture

- Command execution controlled by allowlist in `sandbox/permissions.py`
- Optional network hard gate through `ALLOW_NETWORK`
- Read/write path restrictions for sandboxed file operations

## Current Maturity (Now)

- Runtime safety controls in place
- Deterministic `tool_results` accumulation fixed
- Dynamic DB path resolution for test/runtime parity
- CLI aligned with actual runtime node names

## Next Professional Milestones

1. Implement real API execution streaming (remove placeholders).
2. Add end-to-end integration tests with deterministic stubs.
3. Introduce package-level type coverage target and strict mypy profile.
4. Add release/versioning workflow and changelog automation.
5. Add production deployment profile (container hardening + health endpoints).
