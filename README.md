# template

A template for Python repositories developed with Claude Code: a feature pipeline that runs
each feature in rounds, with its progress kept in files a Claude Code mod can display.

**Version:** 0.1.0

## Packages

| Package | Main entry points |
|---|---|
| `template` | `template.hello_world.main()` — placeholder; replace with real code |

## Setup

```bash
python -m venv .venv
.venv/bin/pip install -e ".[dev]"       # Windows: .venv\Scripts\pip
```

Then ask Claude for a feature in plain words, or `/feature <what to build>`. `CLAUDE.md`
explains the pipeline; `DEVLOG.md` records every version.

New repo from this template: rename `src/template/` and `name` in `pyproject.toml`.
