# Devlog

One entry per version, newest first: what changed, then the files it touched. `/finish`
writes each entry in the commit that opens the pull request.

## 0.1.0 — 2026-11-04

The template's first version: the feature pipeline (`/feature`, `/round`, `/finish`), its
agents and the `round` and `final` workflows, the state files under `development/` that hooks
and mods read, and the documents every change keeps in sync.

Files:
- `CLAUDE.md`, `STRUCTURE.md`, `README.md`, `DEVLOG.md`, `pyproject.toml`
- `.claude/skills/` — `feature`, `round`, `finish`
- `.claude/agents/` — the thirteen pipeline agents
- `.claude/workflows/` — `round.js`, `final.js`
- `.claude/hooks/` — `dev_state.py`, `session_brief.py`, `check_sync.py`, `guard_git.py`, `lint_py.py`
- `.claude/rules/python.md`, `.claude/settings.json`
- `src/template/`, `tests/`, `development/README.md`, `.github/workflows/check.yml`
