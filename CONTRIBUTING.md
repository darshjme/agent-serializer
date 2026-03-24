# Contributing to agent-serializer

Thank you for your interest in contributing!

## Getting Started

```bash
git clone https://github.com/your-org/agent-serializer
cd agent-serializer
pip install -e ".[dev]"
```

## Running Tests

```bash
python -m pytest tests/ -v
```

All 27 tests must pass before submitting a PR.

## Guidelines

- **Zero dependencies** — keep `dependencies = []` in `pyproject.toml`. Stdlib only.
- **Python ≥ 3.10** — no walrus operator misuse, use `match` where appropriate.
- **Type hints** — all public APIs must be fully annotated.
- **Tests** — every new feature needs at least 2 test cases (happy path + edge case).
- **Docstrings** — Google style, concise.

## Pull Request Process

1. Fork the repo and create a feature branch: `git checkout -b feat/my-feature`
2. Write tests first (TDD preferred)
3. Implement the feature
4. Run `python -m pytest tests/ -v` — must be all green
5. Update `CHANGELOG.md` under `[Unreleased]`
6. Open a PR with a clear description

## Code Style

- Follow PEP 8
- Maximum line length: 100 characters
- Use `f-strings` over `.format()`

## Reporting Bugs

Open a GitHub Issue with:
- Python version
- Minimal reproducible example
- Expected vs actual behaviour

## Security Issues

See [SECURITY.md](SECURITY.md) — do **not** open a public issue for vulnerabilities.
