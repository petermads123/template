---
name: setup
description: One-time setup of a repo created from this template — asks what the repo is for, renames the package, sets the approver, starts the version history at 0.1.0, offers the branch ruleset, then deletes itself and its reference in CLAUDE.md in the same commit so it can never run twice. Use at the start of the first conversation in a fresh repo made from the template, whether the user names the skill or not.
argument-hint: "[what the repo is for, optionally]"
model: opus
effort: medium
---

# /setup — make this repo its own

Runs once, in the first conversation of a repo created from `petermads123/template`. It turns
the template into *this* repo and then removes itself: the skill folder, its block in
`CLAUDE.md` and its row in `STRUCTURE.md` are deleted in the same commit as the setup, so
nothing is left that could run it again.

Three things only the user knows: what the repo is for, the package name, and whether anyone
else works in it. Ask all three up front (steps 3 and 4), then make every change without
stopping. Do not guess. Keep each question to a line or two.

## 1. Check it should run at all

```bash
git remote get-url origin
ls src/
```

- The remote is `petermads123/template` itself → **this is the template, not a repo made
  from it. Say so and stop.** Setup here would rename the template.
- `src/template/` is gone, or `.claude/skills/setup/` no longer exists in `HEAD` → setup has
  already run. Say so and stop.
- A feature is in flight (`python .claude/hooks/dev_state.py` reports one) → stop and say
  setup comes first only in a fresh repo; ask the user what they want.

## 2. Branch

`git switch main`, `git pull --ff-only`, `git switch -c chore/repo-setup`. A hosted session
that may push only its own branch uses that branch instead.

## 3. The three questions

> What is this repo for? A sentence or two on what it does and who or what uses it.

This replaces the README's opening paragraph and `[project] description`. Keep it to what they
said.

> Do other people work in this repo, or is it just you?

The answer picks the branch ruleset in step 6.

## 4. The package name

Propose one from the remote's repo name: `my-cool-thing` → `my_cool_thing`. It must be a valid
Python identifier (lowercase, underscores, not starting with a digit) and none of `lib`,
`build`, `dist`, `sdist`, `src`, `tests`, `docs`, `development`: the first four are ignored by
`.gitignore`, so the folder would silently go untracked, and the rest collide with this repo's
own folders. A repo name is not always a good package name, so let the user confirm or change
it.

## 5. Make the changes

| What | Change |
|---|---|
| `src/template/` | `git mv src/template src/<package>` |
| `src/template.egg-info/` | delete it if present: it is a stale install record under the old name |
| `pyproject.toml` | `[project] name` and `description`; `version` to `0.1.0`; `authors` stays if it is the user (`git config user.name`), else ask |
| `tests/test_hello_world.py` | `from <package>.hello_world import main` |
| `README.md` | Title `# <repo name>`; **replace** the opening paragraph with the description; `**Version:** 0.1.0`; the packages row (`<package>`, `<package>.hello_world.main()`); delete the "New repo from this template" paragraph |
| `STRUCTURE.md` | In the tree: `src/<package>/` with the note "the package" (drop "rename for a new repo"), and the `skills/` line back to `/feature, /round, /finish`; the `src/template/...` headings; delete the `skills/setup/` row |
| `DEVLOG.md` | Keep the title and its intro paragraph, and replace every entry (they record the template's history, not this repo's) with exactly this one, filled in: |
| `CLAUDE.md` | The approver in "Review and merge": the remote's owner unless the user names someone else; delete the "This repo has not been set up yet" block |

```
## 0.1.0 — <YYYY-MM-DD>

Created from `petermads123/template`: the feature pipeline, its hooks and CI, and a
placeholder package `<package>`.

Files:
- everything
```

Then check nothing is left behind:

- `git grep -n -w template -- ':!.venv'` — clear every hit that names the package. Prose about
  where the repo came from (`petermads123/template`, `template_repo`, the `.gitignore`
  comments) stays.
- `git grep -n -i setup -- ':!.venv' ':!.claude/skills/setup'` — clear every hit about this
  skill; "the setup guide" and the README's "Setup" heading are about installing and stay.

`[tool.setuptools.packages.find]` points at `src` and `[tool.mypy] files` names directories, so
neither needs a change; read them to confirm.

The version starts at `0.1.0` because this repo's history starts here. That is the one time a
version goes down, and it is why this pull request does not run `check_sync.py --base`.

## 6. The branch ruleset (asks before applying)

Copy the chosen ruleset out of the skill folder first, to the scratchpad (or a temp folder
outside the repo), because step 7 deletes the folder:

| Answer to "just you?" | File | Adds over the other |
|---|---|---|
| Just me | `main_protect.solo.json` | — |
| Others too | `main_protect.collab.json` | one required approval, stale approvals dismissed on push, approval of the last push |

Both block deleting and force-pushing `main`, require a pull request with its review threads
resolved, require the CI check `check` to pass, allow merge commits only (the pipeline deletes
a branch after checking its head is on `main`, which a squash or rebase breaks), and ask
Copilot to review each push (a request, not a gate; it does nothing without Copilot).

The solo file requires no approval on purpose: GitHub does not let anyone approve their own
pull request, so in a one-person repo an approval rule cannot be satisfied and every merge
would go through an admin bypass, which protects nothing.

Applying it changes the repository's settings, so it needs the user's yes. With it:
`gh api repos/<owner>/<repo>/rulesets --method POST --input <copied file>`. If that is not
possible here, say so plainly, give the copied file's path, and the path in the GitHub UI:
*Settings → Rules → Rulesets → New ruleset → Import a ruleset*.

## 7. Delete this skill

`git rm -r .claude/skills/setup` — this file and its rulesets. Its block in `CLAUDE.md` and
its lines in `STRUCTURE.md` went in step 5. After this the repo holds nothing that runs setup
again.

## 8. Check and commit

With a venv on Python 3.13 or later (`python -m venv .venv` if there is none, then activate it):

```
pip install -e ".[dev]"
ruff check .
ruff format --check .
mypy
pytest
python .claude/hooks/check_sync.py
python -m <package>.hello_world
```

All must pass; the last proves the rename and the `src/` layout agree.

Show the user the changes in a few lines, then `git add -A`, commit
`chore: set up <repo name>`, push, and open the pull request to `main` (`gh pr create`, or the
GitHub tools where `gh` is not available), titled `Set up <repo name> (v0.1.0)`. From here the
repo works through `/feature`.
