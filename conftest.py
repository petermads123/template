"""Root pytest configuration: loads the live-progress plugin for every run.

`pytest_progress` lives in `.claude/hooks/` (on `pythonpath`, see `pyproject.toml`) and
writes `.pytest_cache/progress.json` while tests run, which the `feature-band` mod draws as
a bar. It sits here, at the root, so it also covers tests run from outside `tests/`, such as
a fix's reproduction under `development/`.
"""

pytest_plugins = ("pytest_progress",)
