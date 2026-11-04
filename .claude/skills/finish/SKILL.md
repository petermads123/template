---
name: finish
description: Close a feature once every round has merged — run the final workflow (full test gate, three concept checkers, two extras scouts), add a fix round if the check fails, hold for the user on a critical extra, otherwise write the version bump, STRUCTURE.md, README.md and DEVLOG.md, open the pull request to main and list the non-critical extras in chat. Use when /round reports the last round merged, or to resume a feature at status final.
model: sonnet
effort: high
---

# /finish — final check and pull request

Runs on the feature branch once `brief.json` is at status `final`. Opening the pull request
needs no confirmation when everything passes; a critical extra holds it for the user.

## 1. Final check

Call the Workflow tool with `scriptPath: ".claude/workflows/final.js"` and `args`
`{ "feature_dir": "development/<branch>", "feature_branch": "<branch>" }`. This skill
instructs you to run it: that is the opt-in it needs. It is read-only and returns the test
gate, three concept verdicts and the extras.

- **Tests red, or fewer than two of three concept checks pass** — add a fix round to
  `brief.json` (`name` "Final fixes", the failures and blocking findings in its summary and
  in `BRIEF.md` under Rounds), set status back to `rounds`, commit, push, and invoke `/round`.
  If the feature already had a "Final fixes" round, do not add another: tell the user what
  still fails and ask.
- **Green** — go on.

## 2. Extras

Merge the scouts' extras: drop duplicates, keep at most five, best first.

- **Any extra marked critical** — keep the pull request closed. Show the critical ones with
  their reasons and ask with `AskUserQuestion` whether to add a round for them, ship anyway,
  or drop them. A new round goes through `brief.json` and `/round` as in step 1.
- **None critical** — go on; the list is shown after the pull request opens.

## 3. Version and documents

- `git fetch origin main`. Read `main`'s version (`git show origin/main:pyproject.toml`) and
  raise it once by the brief's `bump`: `major` → X+1.0.0, `minor` → X.Y+1.0, `patch` →
  X.Y.Z+1. Counting from `main` now, not from when the feature started, keeps two branches
  from claiming the same number.
- If `main` moved since the feature branch was cut, `git merge origin/main` first and re-run
  the test gate; a conflict goes to the user.
- Start a `docs-writer` agent (`model: sonnet`, `effort: medium`) with the new version, the
  feature folder and today's date. It writes `pyproject.toml`, `STRUCTURE.md`, `README.md`
  and `DEVLOG.md` and runs `check_sync.py --base origin/main` until clean.
- Run the full gate yourself: `pytest`, `ruff check .`, `ruff format --check .`, `mypy`,
  `python .claude/hooks/check_sync.py --base origin/main`.

## 4. Pull request

- In `brief.json`: status `review`. That status is what keeps the merged brief from showing as
  live on `main`.
- Commit `release: <version> — <feature title>` with the documents and the state file, push.
- Open the pull request to `main` (`gh pr create`, or the GitHub tools where `gh` is not
  available), titled `<feature title> (v<version>)`. Body: the BRIEF's goal; the rounds, one
  line each; the feature's acceptance criteria with how each is met; the version and why that
  bump; the test gate's summary.
- Write the pull request URL into `brief.json` `pr`, commit `feature: record PR`, push.

## 5. Report

In chat: the pull request link, then the non-critical extras — title, why, size — so the user
can pick any up as a new `/feature`. Nothing merges until the user merges it or tells you to
in so many words; see `CLAUDE.md`.
