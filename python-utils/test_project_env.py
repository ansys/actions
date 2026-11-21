# Copyright (C) 2022 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Tests for the project_env module."""

from pathlib import Path

from project_env import (
    PINNED_PIP,
    EnvironmentInputs,
    ProjectEnvError,
    plan_environment,
    split_names,
)
import pytest

PY = str(Path(".venv") / "bin" / "python")
PY_WIN = str(Path(".venv") / "Scripts" / "python.exe")


def make_project(
    tmp_path: Path, backend: str = "flit", lockfile: bool = False, files: tuple[str, ...] = ()
) -> Path:
    """Create a minimal project layout on disk."""
    backend_line = {
        "poetry": 'build-backend = "poetry.core.masonry.api"',
        "flit": 'build-backend = "flit_core.buildapi"',
    }[backend]
    (tmp_path / "pyproject.toml").write_text(f"[build-system]\n{backend_line}\n", encoding="utf-8")
    if lockfile:
        (tmp_path / "uv.lock").write_text("", encoding="utf-8")
    for name in files:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")
    return tmp_path


def install_commands(plan) -> list[list[str]]:
    """Commands after the venv creation and pip bootstrap, which are always first."""
    return plan.commands[2:]


# --- shared prelude -------------------------------------------------------


def test_every_plan_creates_venv_then_pins_pip(tmp_path):
    """Every plan creates venv then pins pip."""
    plan = plan_environment(
        EnvironmentInputs(use_uv=False), make_project(tmp_path), is_windows=False
    )
    assert plan.commands[0] == ["python", "-m", "venv", ".venv"]
    assert plan.commands[1][:3] == [PY, "-m", "pip"]
    assert plan.commands[1][-1] == PINNED_PIP


def test_windows_uses_scripts_interpreter(tmp_path):
    """Windows uses scripts interpreter."""
    plan = plan_environment(
        EnvironmentInputs(use_uv=False), make_project(tmp_path), is_windows=True
    )
    assert plan.commands[1][0] == PY_WIN
    assert install_commands(plan)[0][0] == PY_WIN


# --- backend detection ----------------------------------------------------


@pytest.mark.parametrize(
    ("backend", "use_uv", "expected", "prefix"),
    [
        ("poetry", True, "poetry", "poetry run --"),
        ("poetry", False, "poetry", "poetry run --"),
        ("flit", True, "uv", "uv run --no-sync --"),
        ("flit", False, "pip", ""),
    ],
)
def test_backend_detection(tmp_path, backend, use_uv, expected, prefix):
    """Backend detection."""
    plan = plan_environment(
        EnvironmentInputs(use_uv=use_uv), make_project(tmp_path, backend), is_windows=False
    )
    assert plan.backend == expected
    assert plan.run_prefix == prefix
    assert plan.bootstrap_poetry is (expected == "poetry")


def test_lockfile_ignored_without_uv(tmp_path):
    """Lockfile ignored without uv."""
    plan = plan_environment(
        EnvironmentInputs(use_uv=False), make_project(tmp_path, lockfile=True), is_windows=False
    )
    assert plan.use_uv_lockfile is False


def test_python_version_file_removed_only_with_uv(tmp_path):
    """Python version file removed only with uv."""
    project = make_project(tmp_path, files=(".python-version",))
    assert plan_environment(
        EnvironmentInputs(use_uv=True), project, False
    ).remove_python_version_file
    assert not plan_environment(
        EnvironmentInputs(use_uv=False), project, False
    ).remove_python_version_file


# --- library + dependencies per backend ----------------------------------


def test_poetry_install_with_groups_and_extras(tmp_path):
    """Poetry install with groups and extras."""
    inputs = EnvironmentInputs(use_uv=True, optional_dependencies="all", group_dependencies="doc")
    plan = plan_environment(inputs, make_project(tmp_path, "poetry"), is_windows=False)
    assert install_commands(plan) == [
        ["poetry", "install"],
        ["poetry", "install", "--with", "doc", "--extras", "all"],
    ]


def test_poetry_omits_empty_extras(tmp_path):
    """Poetry omits empty extras."""
    plan = plan_environment(
        EnvironmentInputs(use_uv=False, skip_install=True),
        make_project(tmp_path, "poetry"),
        is_windows=False,
    )
    assert install_commands(plan) == [["poetry", "install"]]


def test_uv_with_lockfile_trims_extras_and_groups(tmp_path):
    """Uv with lockfile trims extras and groups."""
    inputs = EnvironmentInputs(
        use_uv=True, optional_dependencies="a, b ,", group_dependencies=" doc , tests"
    )
    plan = plan_environment(inputs, make_project(tmp_path, lockfile=True), is_windows=False)
    assert plan.use_uv_lockfile is True
    assert install_commands(plan) == [
        ["uv", "sync", "--frozen", "--no-default-groups"],
        [
            "uv",
            "sync",
            "--frozen",
            "--no-default-groups",
            "--group",
            "doc",
            "--group",
            "tests",
            "--extra",
            "a",
            "--extra",
            "b",
        ],
    ]


def test_uv_without_lockfile(tmp_path):
    """Uv without lockfile."""
    inputs = EnvironmentInputs(use_uv=True, optional_dependencies="a, b", group_dependencies="doc")
    plan = plan_environment(inputs, make_project(tmp_path), is_windows=False)
    assert install_commands(plan) == [
        ["uv", "pip", "install", "."],
        ["uv", "pip", "install", "--group", "doc", ".[a,b]"],
    ]


def test_pip_passes_groups(tmp_path):
    """Pip passes groups."""
    inputs = EnvironmentInputs(
        use_uv=False, optional_dependencies="tests", group_dependencies="doc"
    )
    plan = plan_environment(inputs, make_project(tmp_path), is_windows=False)
    assert install_commands(plan) == [
        [PY, "-m", "pip", "install", "."],
        [PY, "-m", "pip", "install", "--group", "doc", ".[tests]"],
    ]


def test_skip_install_keeps_dependencies(tmp_path):
    """Skip install keeps dependencies."""
    inputs = EnvironmentInputs(use_uv=True, skip_install=True, group_dependencies="doc")
    plan = plan_environment(inputs, make_project(tmp_path, lockfile=True), is_windows=False)
    assert install_commands(plan) == [
        ["uv", "sync", "--frozen", "--no-default-groups", "--group", "doc"]
    ]


# --- requirements file ----------------------------------------------------


@pytest.mark.parametrize(
    ("use_uv", "installer"), [(True, ["uv", "pip"]), (False, [PY, "-m", "pip"])]
)
def test_requirements_file_replaces_pyproject_dependencies(tmp_path, use_uv, installer):
    """Requirements file replaces pyproject dependencies."""
    req = "requirements/requirements_doc.txt"
    inputs = EnvironmentInputs(use_uv=use_uv, optional_dependencies="doc", requirements_file=req)
    plan = plan_environment(inputs, make_project(tmp_path, files=(req,)), is_windows=False)
    assert install_commands(plan) == [
        [*installer, "install", "-r", req],
        [*installer, "install", "."],
    ]


def test_missing_requirements_file_falls_back_to_pyproject(tmp_path):
    """Missing requirements file falls back to pyproject."""
    inputs = EnvironmentInputs(
        use_uv=False, optional_dependencies="doc", requirements_file="requirements/nope.txt"
    )
    plan = plan_environment(inputs, make_project(tmp_path), is_windows=False)
    assert install_commands(plan)[-1] == [PY, "-m", "pip", "install", ".[doc]"]


def test_lockfile_and_requirements_file_conflict(tmp_path):
    """Lockfile and requirements file conflict."""
    req = "requirements/requirements_doc.txt"
    with pytest.raises(ProjectEnvError, match="not both"):
        plan_environment(
            EnvironmentInputs(use_uv=True, requirements_file=req),
            make_project(tmp_path, lockfile=True, files=(req,)),
            is_windows=False,
        )


def test_split_names():
    """Split names."""
    assert split_names(" a, ,b ,") == ["a", "b"]
    assert split_names("") == []
