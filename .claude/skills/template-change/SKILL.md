---
name: template-change
description: Make a change to the template repo itself (petermads123/template) — its pipeline, skills, agents, workflows, hooks, CI or setup — and then carry every pipeline change to each repo made from the template, one pull request per repo, so they all run the latest pipeline. Use for any change in petermads123/template, whether the user names the skill or not; never in a repo made from the template (setup deletes it there).
argument-hint: <the change to the template>
model: opus
effort: medium
---

# /template-change — change the template, then the repos made from it

Only for `petermads123/template` itself. A repo made from the template has none of this:
`/setup` deletes this skill, and such a repo routes its own workflow changes through its
`CLAUDE.md`. If `git remote get-url origin` is not `petermads123/template`, say so and stop.

Two parts, in order: the change in the template (sections 1–3), then the same change in each
downstream repo (sections 4–6). The user never has to ask for the second part: a pipeline
change is not done until every downstream repo has its pull request.

## 1. Classify the change

| Kind | Touches | Downstream |
|---|---|---|
| **Pipeline** | `.claude/skills/{feature,fix,round,finish}/`, `.claude/agents/`, `.claude/workflows/`, `.claude/hooks/` and their tests, `.claude/settings.json`, `.claude/rules/python.md`, `development/README.md`, `.github/workflows/check.yml`, the workflow sections of `CLAUDE.md` and `STRUCTURE.md` | every repo in section 4 |
| **Template-only** | `/setup` and its rulesets, this skill, the placeholder package `src/template/`, the "not set up yet" block in `CLAUDE.md`, the template's own `README.md` prose | none: say so, and stop after section 3 |

A change that is both is a pipeline change; only its pipeline files go downstream.

Settle with the user, one question per turn, what the change does and what it does not; a
small, clear request needs no questions.

## 2. Make it in the template

- Branch: `git switch main`, `git pull --ff-only`, `git switch -c chore/<kebab-slug>`. A hosted
  session that may push only its own branch restarts that branch from `origin/main` instead
  (`git checkout -B <branch> origin/main`, when its earlier pull request has merged).
- Make the change. A `.py` change has tests in `tests/`, as `.claude/rules/python.md` says.
- `STRUCTURE.md`, `CLAUDE.md` and `README.md` say what changed where they describe it.
- Version: `patch` for a workflow change (`CLAUDE.md`'s table), in `pyproject.toml`,
  `README.md`'s `**Version:**` and a new `DEVLOG.md` entry (`## X.Y.Z — <date>`, prose, then
  `Files:`).

## 3. Gate, commit, pull request

```
ruff check .
ruff format --check .
mypy
pytest
python .claude/hooks/check_sync.py --base origin/main
```

The whole suite here: the template's is small. Commit `chore: <what> (v<version>)`, push with
`-u`, open the pull request to `main`, and watch its CI through to green. Note the template
commit the change starts from (`git rev-parse origin/main` before the branch) and the one it
ends on: section 5 uses both.

## 4. The downstream repos

Repos made from the template, or moved onto its pipeline:

| Repo | Repo-specific parts to keep |
|---|---|
| `petermads123/heatingsystem` | `CLAUDE.md` "What this project is"; `DEVELOPMENT.md` |
| `petermads123/ev_frequency_support` | `PROJECT_RULES` in all three workflows; `/finish`'s extra steps (assign the approver, `DEVELOPMENT.md` extras, stage by explicit path); `guard_git.py`'s Overleaf and other-repository rules; `guard_data.py` and its registration in `settings.json`; the additions to `rules/python.md`; `[tool.select_tests] ignore`; the `report and sources/` and `data/` rules in `CLAUDE.md`; `STRUCTURE.md` and `README.md` edited in place, never rewritten |
| `petermads123/energydata` | `.claude/rules/structure-*.md`; the live tests and API keys in `CLAUDE.md`; `DEVELOPMENT.md` |
| `petermads123/energy_optimization` | `CLAUDE.md` "What this project is"; `DEVELOPMENT.md` |
| `petermads123/valg_data` | `CLAUDE.md` "What this project is"; the fixtures rule; `DEVELOPMENT.md` |

The table can fall behind. Before starting, list the user's repositories
(`mcp__claude-code-remote__list_repos`) and look for any other repo with
`.claude/workflows/round.js` and `.claude/hooks/dev_state.py`; a repo that has them belongs
here. Add it to this table in the template's pull request, and say so to the user. A repo not
attached to the session is added with `add_repo` (push access).

## 5. Carry the change into each repo (one pull request per repo)

Work through the repos one after another, or with one agent each when there are several and
the change is large; each agent gets this section, its repo, the template patch and the
repo's row of the table.

In each repo:

1. **Sync and branch.** `git fetch origin`, then the same branch rule as section 2, from that
   repo's `origin/main`. A repo with a feature in flight keeps it: this pull request goes to
   `main`, and the feature merges `main` later.
2. **Apply the patch** of the template's pipeline files between the two commits of section 3:
   `git -C <template> diff <from> <to> -- <pipeline paths> > <scratchpad>/template.patch`, then
   in the repo `git apply -3 <scratchpad>/template.patch`. A file that applies clean was the
   template's own. A conflict means the repo changed that file: merge by hand, keeping both the
   template's change and every repo-specific part in the table. Never overwrite a repo file
   wholesale with the template's.
3. **Documents in the repo's own words.** `CLAUDE.md` and `STRUCTURE.md` get the same pipeline
   facts the template's got, edited into the repo's text rather than pasted over it.
   `README.md` only when it describes the changed part.
4. **Version.** `patch` bump from that repo's `main`, its `README.md` `**Version:**` line and a
   `DEVLOG.md` entry that names the template version it adopts.
5. **Gate.** `ruff check .`, `ruff format --check .`, `mypy`,
   `python .claude/hooks/check_sync.py --base origin/main`, and the tests
   `python .claude/hooks/select_tests.py --base origin/main` picks. A version bump selects the
   full suite; run it locally only where it is fast, and leave a long one to CI.
6. **Commit and pull request.** Commit `chore: <what> (v<version>)` (staging by explicit path
   where the repo says so), push with `-u`, open the pull request to `main`. Its body starts
   with `Adopts petermads123/template#<n> (template <version>)` and says what was merged by
   hand and why.

## 6. Watch and report

Subscribe to every pull request and see each CI through: a red run caused by the change is
fixed on its branch; a failure that is also red on that repo's `main` is not this change's,
and is reported, not fixed here. Then give the user one table: repo, pull request, version,
CI. **Never merge** any of them on your own judgment: they reach `main` when the approver
merges or says so in so many words, as each repo's `CLAUDE.md` says.
