# Contributing

## Development Setup

```bash
python -m pip install -e .[dev]
```

## Before Opening a PR

Run locally:

```bash
make lint
make test
```

## PR Rules

- Keep changes scoped and atomic.
- Include or update tests for behavior changes.
- Do not bypass sandbox/security checks.
- Keep README and docs aligned with runtime behavior.

## Commit Style

Use conventional-style messages:

- `fix: ...`
- `feat: ...`
- `chore: ...`
- `test: ...`
- `docs: ...`
