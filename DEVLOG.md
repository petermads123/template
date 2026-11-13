# Devlog

One entry per version, newest first: what changed, then the files it touched. `/finish`
writes each entry in the commit that opens the pull request.

## 0.2.3 — 2026-11-13

Adds `petermads123/home-assistant` to the repos `/template-change` carries pipeline changes
into. It is the configuration of a running Home Assistant rather than a Python package, so
its row names more repo-specific parts than the others and points at the list that repo
keeps in its own `development/README.md`. Template-only: nothing goes downstream.

Files:
- `.claude/skills/template-change/SKILL.md`
- `README.md`, `DEVLOG.md`, `pyproject.toml`

## 0.2.2 — 2026-11-09

Adds `/template-change`, the skill for changing the template itself. It classifies a change as
pipeline or template-only, makes it here with a patch bump, and for a pipeline change opens
one pull request in each repo made from the template, applying the template's own diff with
`git apply -3` and merging by hand where a repo changed the file, so its repo-specific parts
survive. Its table lists those repos and what each keeps; it also checks the user's
repositories for one the table misses and asks before adding it. It never merges. `/setup` deletes it, with itself and
its references, so a repo made from the template never pushes into other repos; setup's
`STRUCTURE.md` instructions now also name `/fix`.

Files:
- `.claude/skills/template-change/SKILL.md` (new), `.claude/skills/setup/SKILL.md`
- `CLAUDE.md`, `STRUCTURE.md`, `README.md`, `DEVLOG.md`, `pyproject.toml`

## 0.2.1 — 2026-11-09

The concept conversation asks one question at a time. In `/feature` every turn that waits
for the user ends on exactly one question, never a list, and the four repo scouts no longer
write into the chat: a report that arrives while a question is open is noted in `BRIEF.md`
under `## Scout findings`, the turn ends without a message, and the findings shape the next
question once the user answers. The rounds are proposed only after every report is in, so
none lands after them. `/fix` asks its intake and its agreement the same way.

Files:
- `.claude/skills/feature/SKILL.md`, `.claude/skills/fix/SKILL.md`
- `README.md`, `DEVLOG.md`, `pyproject.toml`

## 0.2.0 — 2026-11-09

A round runs only the tests its change can affect; the full suite runs in CI on the pull
request. The new hook `select_tests.py` reads the round's diff against the feature branch and
picks the changed test files, each changed module's `test_<module>.py` and every test file
that imports a changed module, directly or through other modules (by `ast`, never by
importing). It falls back to the full suite when `pyproject.toml`, a `conftest.py`, a test
helper, a re-exporting `__init__.py` or an unparseable file changed, and selects nothing for
prose and pipeline files. Step 7 runs that selection plus ruff and mypy on the whole tree,
records it in `log.md`, and in the fix loop re-runs with `--ff` and the earlier failures;
`final.js` runs the selection over the whole feature against `origin/main`. `/finish` now sees
the pull request's CI through to green, fixing a red run on the feature branch, and never
calls a feature done on a red or pending CI.

Files:
- `.claude/hooks/select_tests.py`, `tests/test_select_tests.py`
- `.claude/workflows/round.js`, `final.js`; `.claude/agents/test-runner.md`, `concept-checker.md`
- `.claude/skills/finish/SKILL.md`, `.claude/settings.json`
- `CLAUDE.md`, `STRUCTURE.md`, `README.md`, `DEVLOG.md`, `pyproject.toml`

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
