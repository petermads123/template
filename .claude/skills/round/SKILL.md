---
name: round
description: Coordinate one round of the feature in flight — create its branch and state files, run the round workflow in the background, answer or escalate its questions, record the merge in brief.json, then start the next round or /finish. Use after /feature writes the brief, after a round merges, or to resume a round that stopped.
argument-hint: "[round number]"
model: sonnet
effort: high
---

# /round — coordinate one round

The main session coordinates; the round itself runs as the `round` workflow
(`.claude/workflows/round.js`), each step an agent on its own model. This skill instructs you
to run that workflow: that is the opt-in it needs.

Exactly one round runs at a time, and while it runs the working tree belongs to it: do not
edit files, switch branches or commit until the workflow returns. Talking with the user is
fine.

## 1. Find the round

Read the live `brief.json` (`python .claude/hooks/dev_state.py`). The round is the argument,
else `current_round`.

- Round status `planned` → start it (step 2).
- Round status `running` → resume it: read its `round.json`. `step` is where it stands;
  `status` `blocked` means it is waiting on its `question` (go to 4 with that question);
  `failed` means a step gave up — read `note` and the end of `log.md`, tell the user, and ask
  how to proceed. Otherwise check out the round branch and go to step 3 with
  `start_step` = `step`.
- Every round `merged` → `/finish`.

## 2. Start it

On the feature branch, up to date with its remote:

- Create `<feature folder>/r<n>-<slug>/` with `log.md` (a title line, then the round's summary
  from the brief) and `round.json`: `round`, `name`, `branch`, `status` `running`, `step` 1,
  `steps` (the nine names in `.claude/hooks/dev_state.py` `ROUND_STEPS`), `attempt` 0,
  `question` "", `note` "starting".
- In `brief.json`: this round's status `running`, `current_round` = n.
- Commit `round <n>: start <name>`, push.
- `git switch -c <round branch>`, `git push -u origin <round branch>`.

After this, `round.json` is written only by the round's own steps, and `brief.json` only by
you, on the feature branch. That split is what lets the round merge back without conflicts.

## 3. Run the workflow

Call the Workflow tool with `scriptPath: ".claude/workflows/round.js"` and `args`:

```json
{ "feature_dir": "development/<branch>", "round_dir": "development/<branch>/r<n>-<slug>",
  "round": <n>, "feature_branch": "<branch>", "round_branch": "<branch>--r<n>",
  "start_step": <1, or the step to resume>, "answers": [<answers so far, if any>] }
```

It runs in the background. Tell the user in one line that round n is running and what it
covers, then end the turn; the workflow's completion wakes the session. Relay the trace it
returns: one line per step.

## 4. When it returns

- **`merged`** — the closer merged the round into the feature branch and left it checked
  out. In `brief.json`: the round's status `merged`; `current_round` to the next round, or
  status `final` if this was the last. Commit `round <n>: merged`, push. Check the round's
  "Changes" against the rounds still planned: if this round changed what a later round
  assumes, update `BRIEF.md` in the same commit and say so. Then start the next round (step 2)
  or invoke `/finish`.
- **`needs_input`** — the round asks a question. Answer it yourself when `BRIEF.md`, its
  Decisions and this conversation settle it; say in one line what you answered and why.
  Otherwise ask the user with `AskUserQuestion`, carrying the options the round saw. If the
  answer changes the feature itself, record it in `BRIEF.md`'s Decisions (on the feature
  branch, after the round, or via the round's `log.md` now). Re-run step 3 with `start_step`
  = the step that asked and the answer appended to `answers`.
- **`failed`** — tell the user which step failed and why, from `summary` and `log.md`, and
  ask how to proceed.

A round that keeps failing its gates escalates as `needs_input` after two fix attempts; treat
that as a real question, not a reason to rerun unchanged.
