# Structure

The map of this repo: every module, and every public class and function with its signature
and return type. Read it before opening source files. `/finish` rewrites it from the code once
per feature; `check_sync.py` fails when a Python file under `src/`, `tests/` or
`.claude/hooks/` is missing from it or named here without existing. Private names (`_x`) stay
out.

## Tree

```
src/template/           the package (rename for a new repo)
tests/                  pytest suite, one test_<module>.py per module
development/            the pipeline's state: one folder per feature branch (see its README)
.claude/
  skills/               /feature, /round, /finish; /setup until a new repo has run it
  agents/               the pipeline's agents, one file each
  workflows/            round.js (one round), final.js (the whole-feature check)
  hooks/                session brief, git guard, Ruff on edit, state reader, sync checker
  rules/python.md       coding conventions, loaded for **/*.py
.github/workflows/      CI: the gate and check_sync
pyproject.toml          package, version, Ruff/mypy/pytest config
CLAUDE.md               routing map and rules for Claude
README.md               short: version, packages and entry points
DEVLOG.md               one entry per version
STRUCTURE.md            this file
```

## Package: `src/template/`

### `src/template/__init__.py`

Package entry point; re-exports the public API. Nothing exported yet.

### `src/template/hello_world.py`

Placeholder. Delete when real code arrives.

| Signature | Returns |
|---|---|
| `main() -> None` | Prints `Hello, World!`. |

## Hooks: `.claude/hooks/`

Stdlib only; importable by each other and by the tests (`pythonpath` in `pyproject.toml`).

### `.claude/hooks/dev_state.py`

Reads `brief.json` and `round.json` leniently: a malformed file reads as None.

| Signature | Returns |
|---|---|
| `RoundEntry` | Frozen dataclass: `number`, `name`, `slug`, `branch`, `status`, `summary`; property `folder -> str` (`r<n>-<slug>`). |
| `Brief` | Frozen dataclass: `path`, `feature`, `title`, `branch`, `bump`, `status`, `summary`, `current_round`, `rounds: tuple[RoundEntry, ...]`, `pr`; properties `folder -> Path`, `live -> bool`; `round_entry(number: int) -> RoundEntry \| None`. |
| `RoundState` | Frozen dataclass: `path`, `round`, `name`, `branch`, `status`, `step`, `steps: tuple[str, ...]`, `attempt`, `question`, `note`; property `step_name -> str`. |
| `read_brief(path: Path) -> Brief \| None` | One `brief.json`, or None if unusable. |
| `read_round(path: Path) -> RoundState \| None` | One `round.json`, or None if unusable. |
| `all_briefs(project_dir: Path) -> list[Brief]` | Every brief under `development/`, newest first. |
| `active_brief(project_dir: Path, branch: str = "") -> Brief \| None` | The live brief, preferring the checked-out feature or round branch. |
| `round_state(brief: Brief, number: int) -> RoundState \| None` | That round's `round.json`. |
| `git_lines(project_dir: Path, args: list[str]) -> list[str]` | Non-empty output lines of a git command, `[]` on failure. |
| `current_branch(project_dir: Path) -> str` | The checked-out branch, or `""`. |
| `main() -> None` | Prints the live feature and its current round. |

Constants: `DEV_DIR`, `LIVE_STATUSES`, `FEATURE_STATUSES`, `ROUND_STATUSES`, `STEP_STATUSES`,
`ROUND_STEPS` (the nine step names).

### `.claude/hooks/session_brief.py`

`SessionStart` hook: injects the live feature's state and the skill that resumes it.

| Signature | Returns |
|---|---|
| `brief(project_dir: Path, feature: Brief) -> str` | The paragraph for the session's context. |
| `main() -> None` | Emits it as `additionalContext`, or nothing when no feature is live. |

### `.claude/hooks/check_sync.py`

Checks the documents agree with each other and with the code. Run by `/finish` and CI.

| Signature | Returns |
|---|---|
| `parse_version(text: str) -> tuple[int, int, int] \| None` | The version, or None if not exactly `X.Y.Z`. |
| `bumped(version: tuple[int, int, int], bump: str) -> tuple[int, int, int]` | The version raised by `major`/`minor`/`patch`; raises `ValueError` otherwise. |
| `project_version(pyproject_text: str) -> str` | `[project] version`, or `""`. |
| `version_problems(project_dir: Path) -> list[str]` | pyproject, README `**Version:**` and newest DEVLOG entry disagree; DEVLOG order. |
| `structure_problems(project_dir: Path) -> list[str]` | Python files missing from STRUCTURE.md, or named but absent. |
| `state_problems(project_dir: Path) -> list[str]` | Unparseable state files, unknown statuses. |
| `branch_brief(project_dir: Path, branch: str) -> Brief \| None` | The brief whose feature or round branch is `branch`. |
| `bump_problems(project_dir: Path, base: str) -> list[str]` | Version not raised above `base`'s by this branch's brief's bump (any raise without one). |
| `problems(project_dir: Path, base: str = "") -> list[str]` | All of the above. |
| `main() -> None` | CLI: `[--base REF] [--root DIR]`; prints problems, exits 1 if any. |

### `.claude/hooks/guard_git.py`

`PreToolUse` hook on `Bash` and `PowerShell`: refuses a `git commit` or `git push` that would
land on `main`, reading the command as a shell would (quoting, separators, subshells, branch
switches chained with `&&`). Vendored from `template_repo`.

| Signature | Returns |
|---|---|
| `Segment` | Frozen dataclass: `tokens`, `separator`. |
| `segments(command: str) -> list[Segment] \| None` | The command split into invocations, or None if unreadable. |
| `git_subcommand(tokens: tuple[str, ...]) -> tuple[str, tuple[str, ...]]` | The git subcommand and its arguments. |
| `push_targets_main(args: tuple[str, ...], branch: str) -> bool` | Whether a push would update `main`. |
| `switch_target(subcommand: str, args: tuple[str, ...]) -> str` | The branch a checkout/switch moves to, `""`, or `UNRESOLVED`. |
| `violation(command: str, branch: str) -> str` | The reason to refuse, or `""`. |
| `main() -> None` | Entry point: allow or refuse. |

### `.claude/hooks/lint_py.py`

`PostToolUse` hook: `ruff format` and `ruff check --fix` on an edited `.py` file.

| Signature | Returns |
|---|---|
| `find_ruff(project_dir: Path) -> Path \| None` | Ruff in the project venv. |
| `run(ruff: Path, args: list[str]) -> CompletedProcess[str]` | Ruff's result. |
| `target_file(payload: dict[str, object], project_dir: Path) -> Path \| None` | The edited `.py` file. |
| `main() -> None` | Format, fix, report. |

## Tests: `tests/`

| File | Covers |
|---|---|
| `tests/test_hello_world.py` | the placeholder |
| `tests/test_dev_state.py` | parsing, malformed files, active-brief choice, git helpers; its `write_brief`/`write_round` helpers are reused by other tests |
| `tests/test_session_brief.py` | the brief text and `main`'s output |
| `tests/test_check_sync.py` | every check, including the version raise against a throwaway repo |
| `tests/test_guard_git.py` | the guard, vendored with it |

## Pipeline configuration: `.claude/`

| Path | Role |
|---|---|
| `skills/feature/` | `/feature`: Main Conceptualize (Opus medium), background `repo-scout`s, BRIEF, starts round 1 |
| `skills/round/` | `/round`: coordinates one round (Sonnet high), runs `workflows/round.js`, answers or escalates questions |
| `skills/setup/` | `/setup`: one-time setup of a repo made from the template (purpose, package rename, approver, version 0.1.0, ruleset from its `main_protect.*.json`); deletes itself when done |
| `skills/finish/` | `/finish`: runs `workflows/final.js`, extras, `docs-writer`, version, pull request |
| `workflows/round.js` | The nine round steps; args `feature_dir`, `round_dir`, `round`, `feature_branch`, `round_branch`, `start_step`, `attempt`, `answers`; returns `merged`, `needs_input` or `failed` |
| `workflows/final.js` | Read-only whole-feature check: test gate first, then three independent concept checks and two extras scouts; returns `tests`, `checks`, `extras`, `missing` |
| `agents/repo-scout.md` | Read-only investigation for `/feature`, one angle each |
| `agents/round-conceptualizer.md`, `round-planner.md` | Round steps 1 and 2 (Opus) |
| `agents/implementer.md` | Step 3, and fix mode for failing gates |
| `agents/verifier.md`, `code-reviewer.md` | Step 4 |
| `agents/test-designer.md`, `test-writer.md`, `test-runner.md` | Steps 5 to 7 |
| `agents/concept-checker.md` | Step 8 and the final check |
| `agents/round-closer.md` | Step 9: merge into the feature branch |
| `agents/extras-scout.md`, `docs-writer.md` | `/finish` |
| `rules/python.md` | Conventions for `**/*.py` |
| `settings.json` | Hooks and pre-approved commands |
