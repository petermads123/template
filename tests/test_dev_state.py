import json
import subprocess
from pathlib import Path

import pytest
from dev_state import (
    ROUND_STEPS,
    active_brief,
    all_briefs,
    current_branch,
    read_brief,
    read_round,
    round_state,
)


def write_brief(
    root: Path, branch: str, status: str = "rounds", **extra: object
) -> Path:
    folder = root / "development" / branch
    folder.mkdir(parents=True, exist_ok=True)
    data: dict[str, object] = {
        "schema": 1,
        "feature": branch.split("/")[-1],
        "title": "CSV export",
        "branch": branch,
        "bump": "minor",
        "status": status,
        "summary": "Export tables as CSV",
        "current_round": 1,
        "rounds": [
            {
                "n": 1,
                "name": "Writer core",
                "slug": "writer-core",
                "branch": f"{branch}--r1",
                "status": "running",
                "summary": "The writer",
            },
            {
                "n": 2,
                "name": "CLI",
                "slug": "cli",
                "branch": f"{branch}--r2",
                "status": "planned",
                "summary": "The command",
            },
        ],
        "pr": "",
    }
    data.update(extra)
    path = folder / "brief.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def write_round(folder: Path, **extra: object) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    data: dict[str, object] = {
        "schema": 1,
        "round": 1,
        "name": "Writer core",
        "branch": "feat/csv-export--r1",
        "status": "running",
        "step": 3,
        "steps": list(ROUND_STEPS),
        "attempt": 0,
        "question": "",
        "note": "writing the module",
    }
    data.update(extra)
    path = folder / "round.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_read_brief_parses_every_field(tmp_path: Path) -> None:
    brief = read_brief(write_brief(tmp_path, "feat/csv-export"))
    assert brief is not None
    assert brief.feature == "csv-export"
    assert brief.branch == "feat/csv-export"
    assert brief.live
    assert [r.folder for r in brief.rounds] == ["r1-writer-core", "r2-cli"]
    assert brief.round_entry(2) is not None
    assert brief.round_entry(3) is None


@pytest.mark.parametrize("content", ["", "not json", "[]", '{"title": "no feature"}'])
def test_read_brief_returns_none_for_unusable_files(
    tmp_path: Path, content: str
) -> None:
    path = tmp_path / "brief.json"
    path.write_text(content, encoding="utf-8")
    assert read_brief(path) is None


def test_read_brief_returns_none_for_missing_file(tmp_path: Path) -> None:
    assert read_brief(tmp_path / "brief.json") is None


def test_read_brief_skips_malformed_rounds(tmp_path: Path) -> None:
    path = write_brief(
        tmp_path, "feat/x", rounds=[{"n": 0}, "junk", {"n": 2, "name": "B"}]
    )
    brief = read_brief(path)
    assert brief is not None
    assert [r.number for r in brief.rounds] == [2]


def test_read_brief_ignores_wrongly_typed_fields(tmp_path: Path) -> None:
    brief = read_brief(write_brief(tmp_path, "feat/x", current_round=True, title=5))
    assert brief is not None
    assert brief.current_round == 0
    assert brief.title == ""


def test_read_round_reports_step_name(tmp_path: Path) -> None:
    state = read_round(write_round(tmp_path / "r1"))
    assert state is not None
    assert state.step_name == "Implement"
    assert state.steps == ROUND_STEPS


@pytest.mark.parametrize("step", [0, 10, -1])
def test_step_name_is_empty_out_of_range(tmp_path: Path, step: int) -> None:
    state = read_round(write_round(tmp_path / "r1", step=step))
    assert state is not None
    assert state.step_name == ""


def test_read_round_defaults_missing_steps(tmp_path: Path) -> None:
    state = read_round(write_round(tmp_path / "r1", steps=None))
    assert state is not None
    assert state.steps == ROUND_STEPS


def test_read_round_rejects_missing_round_number(tmp_path: Path) -> None:
    assert read_round(write_round(tmp_path / "r1", round=0)) is None


def test_active_brief_ignores_finished_features(tmp_path: Path) -> None:
    write_brief(tmp_path, "feat/old", status="review")
    write_brief(tmp_path, "feat/parked", status="parked")
    assert active_brief(tmp_path, branch="main") is None


def test_active_brief_prefers_the_checked_out_round_branch(tmp_path: Path) -> None:
    write_brief(tmp_path, "feat/a")
    write_brief(tmp_path, "feat/b")
    brief = active_brief(tmp_path, branch="feat/a--r1")
    assert brief is not None
    assert brief.branch == "feat/a"


def test_active_brief_with_no_development_folder(tmp_path: Path) -> None:
    assert all_briefs(tmp_path) == []
    assert active_brief(tmp_path, branch="x") is None


def test_round_state_reads_the_rounds_folder(tmp_path: Path) -> None:
    brief = read_brief(write_brief(tmp_path, "feat/csv-export"))
    assert brief is not None
    write_round(brief.folder / "r1-writer-core")
    state = round_state(brief, 1)
    assert state is not None
    assert state.round == 1
    assert round_state(brief, 2) is None
    assert round_state(brief, 9) is None


def test_current_branch_in_a_repo(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "-q", "-b", "feat/x"], cwd=tmp_path, check=True)
    assert current_branch(tmp_path) == "feat/x"


def test_current_branch_outside_a_repo(tmp_path: Path) -> None:
    assert current_branch(tmp_path / "missing") == ""
