# Architecture Overview

## Runtime Flow

The orchestration loop is runtime-centric:

1. `inject_memory`: pulls profile + relevant journal history
2. `plan`: generates an executable step list
3. `choose_action`: proposes a tool call
4. `execute_tool`: runtime executes allowed tool only
5. `record_result`: stores normalized `ToolResult`
6. `decide`: runtime determines next transition

## Core Principles

- Runtime execution is authoritative.
- LLM output is proposal, not truth.
- Tool execution is constrained by policy.
- State transitions are explicit and inspectable.

## Security Model

- Allowlisted commands and paths.
- Optional network deny-by-default (`ALLOW_NETWORK=false`).
- Output truncation and command timeout in sandbox executor.

## Reliability Model

- Checkpoint support via LangGraph checkpointer.
- Persistent profile/journal in SQLite.
- Structured logging under `logs/agent.log`.

## Maturity Gaps (Planned)

- API channel still contains placeholders.
- Telegram channel is not fully integrated in runtime graph.
- End-to-end integration test coverage needs expansion.
