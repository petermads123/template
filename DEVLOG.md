# Devlog

One entry per version, newest first: what changed, then the files it touched. `/finish`
writes each entry in the commit that opens the pull request.

## 0.1.2 — 2026-11-04

Adds `/setup`, the one-time setup for a repo made from this template. It asks what the repo
is for, renames the package, sets the approver, restarts the version history at 0.1.0 and
offers a branch ruleset that requires CI and merge commits. It then deletes itself and its
`CLAUDE.md` block in the same commit.

Adds `/fix`: a fix starts with a diagnosis workflow (reproduce, three cause hunters, a proven
root cause with its class, an adversarial critique), the user agrees cause, scope and bump,
and the fix then runs through the normal rounds with fix rules: reproduction red before the
fix and green after. `brief.json` gains `kind` and the `diagnosis` status, with the
diagnosis's own `state.json` for hooks and mods.

Files:
- `.claude/skills/setup/` — `SKILL.md`, `main_protect.solo.json`, `main_protect.collab.json`
- `.claude/skills/fix/SKILL.md`, `.claude/workflows/diagnose.js`
- `.claude/agents/` — `reproducer`, `cause-hunter`, `root-cause-analyst`, `diagnosis-critic`
- `.claude/workflows/round.js`, `final.js`; `.claude/skills/round/`, `finish/`
- `.claude/hooks/dev_state.py`, `session_brief.py`, `check_sync.py` and their tests
- `CLAUDE.md`, `STRUCTURE.md`, `README.md`, `DEVLOG.md`, `pyproject.toml`, `development/README.md`

## 0.1.1 — 2026-11-04

Pre-approves the commands an unattended round and `/finish` run on Windows (a PowerShell
twin of every rule) and the `gh pr` commands `/finish` opens the pull request with, so
neither stops at a permission prompt.

Files:
- `.claude/settings.json`
- `pyproject.toml`, `README.md`, `DEVLOG.md`

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
