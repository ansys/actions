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
"""Prepare a project environment: a ``.venv`` holding the project and its dependencies.

This module is the single place that decides *how* a Python project's dependencies
are installed in CI. It is used by the ``_setup-project-env`` action.

The work is split in two:

* :func:`plan_environment` is pure. Given the action inputs and the project
  directory, it returns an :class:`EnvironmentPlan` describing the build backend
  and every command to run. Tests exercise this function.
* :func:`apply_plan` performs the side effects: bootstrapping poetry, writing to
  ``GITHUB_PATH``/``GITHUB_ENV``/``GITHUB_OUTPUT``, removing ``.python-version``
  and running the planned commands.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import os
from pathlib import Path
import shutil
import subprocess
import sys

VENV_DIR = ".venv"
LOCKFILE = "uv.lock"
PYTHON_VERSION_FILE = ".python-version"
POETRY_BUILD_BACKEND = 'build-backend = "poetry.core.masonry.api"'

# Bootstrap from the PSF-published wheel and hash: an index-based upgrade
# would still rely on the old pip's compromised CA bundle.
PINNED_PIP = (
    "pip @ https://files.pythonhosted.org/packages/3f/06/"
    "3e4420302363fbb71be3c7f35ce042f54bfca330e3e66b3a2e3c4cca579f/pip-26.2.2-py3-none-any.whl"
    "#sha256=fd7f4dfa8190e014013b9f08f3e973f4e4c26ffd179a204895533a7254813a70"
)

RUN_PREFIXES = {
    "poetry": "poetry run --",
    "uv": "uv run --no-sync --",
    "pip": "",
}


class ProjectEnvError(Exception):
    """Raised when the inputs or the project layout cannot produce an environment."""


@dataclass(frozen=True)
class EnvironmentInputs:
    """What the caller asks for."""

    use_uv: bool
    skip_install: bool = False
    optional_dependencies: str = ""
    group_dependencies: str = ""
    requirements_file: str = ""


@dataclass
class EnvironmentPlan:
    """Everything needed to build the environment, decided up front."""

    backend: str
    use_uv_lockfile: bool
    bootstrap_poetry: bool
    remove_python_version_file: bool
    commands: list[list[str]] = field(default_factory=list)

    @property
    def run_prefix(self) -> str:
        """Prefix that runs a command inside the environment (may be empty)."""
        return RUN_PREFIXES[self.backend]


def split_names(value: str) -> list[str]:
    """Split a comma-separated list of names, trimming blanks and dropping empties."""
    return [name.strip() for name in value.split(",") if name.strip()]


def venv_python(is_windows: bool) -> str:
    """Return the path of the Python interpreter inside the virtual environment."""
    if is_windows:
        return str(Path(VENV_DIR) / "Scripts" / "python.exe")
    return str(Path(VENV_DIR) / "bin" / "python")


def detect_backend(project_dir: Path, use_uv: bool) -> str:
    """Return ``poetry``, ``uv`` or ``pip``. A poetry build backend always wins."""
    pyproject = project_dir / "pyproject.toml"
    if pyproject.is_file() and POETRY_BUILD_BACKEND in pyproject.read_text(encoding="utf-8"):
        return "poetry"
    return "uv" if use_uv else "pip"


def _library_install(backend: str, use_lockfile: bool, python: str) -> list[str]:
    if backend == "poetry":
        return ["poetry", "install"]
    if backend == "uv":
        if use_lockfile:
            return ["uv", "sync", "--frozen", "--no-default-groups"]
        return ["uv", "pip", "install", "."]
    return [python, "-m", "pip", "install", "."]


def _dependencies_install(
    backend: str, use_lockfile: bool, python: str, inputs: EnvironmentInputs
) -> list[str]:
    if backend == "poetry":
        command = ["poetry", "install"]
        if inputs.group_dependencies.strip():
            command += ["--with", inputs.group_dependencies.strip()]
        if inputs.optional_dependencies.strip():
            command += ["--extras", inputs.optional_dependencies.strip()]
        return command

    extras = split_names(inputs.optional_dependencies)
    group_flags = [
        flag for group in split_names(inputs.group_dependencies) for flag in ("--group", group)
    ]

    if backend == "uv" and use_lockfile:
        extra_flags = [flag for extra in extras for flag in ("--extra", extra)]
        return ["uv", "sync", "--frozen", "--no-default-groups", *group_flags, *extra_flags]

    project_spec = f".[{','.join(extras)}]" if extras else "."
    if backend == "uv":
        return ["uv", "pip", "install", *group_flags, project_spec]
    return [python, "-m", "pip", "install", *group_flags, project_spec]


def plan_environment(
    inputs: EnvironmentInputs,
    project_dir: Path,
    is_windows: bool,
    system_python: str = "python",
) -> EnvironmentPlan:
    """Decide the backend and the ordered commands that build the environment.

    Raises
    ------
    ProjectEnvError
        If both a ``uv.lock`` file and the requirements file exist.
    """
    backend = detect_backend(project_dir, inputs.use_uv)
    use_lockfile = inputs.use_uv and (project_dir / LOCKFILE).is_file()
    has_requirements = (
        bool(inputs.requirements_file) and (project_dir / inputs.requirements_file).is_file()
    )

    if use_lockfile and has_requirements:
        raise ProjectEnvError(
            f"A {LOCKFILE} file was detected and the requirements file "
            f"'{inputs.requirements_file}' exists. Please, either use the lock file or the "
            "requirements file, but not both."
        )

    python = venv_python(is_windows)
    commands: list[list[str]] = [
        [system_python, "-m", "venv", VENV_DIR],
        [
            python,
            "-m",
            "pip",
            "--disable-pip-version-check",
            "install",
            "--no-cache-dir",
            "--force-reinstall",
            PINNED_PIP,
        ],
    ]

    if has_requirements:
        if inputs.use_uv:
            commands.append(["uv", "pip", "install", "-r", inputs.requirements_file])
        else:
            commands.append([python, "-m", "pip", "install", "-r", inputs.requirements_file])

    if not inputs.skip_install:
        commands.append(_library_install(backend, use_lockfile, python))

    if not has_requirements:
        commands.append(_dependencies_install(backend, use_lockfile, python, inputs))

    return EnvironmentPlan(
        backend=backend,
        use_uv_lockfile=use_lockfile,
        bootstrap_poetry=backend == "poetry",
        remove_python_version_file=inputs.use_uv and (project_dir / PYTHON_VERSION_FILE).is_file(),
        commands=commands,
    )


# ---------------------------------------------------------------------------
# Side effects
# ---------------------------------------------------------------------------


def _append(path_variable: str, line: str) -> None:
    target = os.environ.get(path_variable)
    if target:
        with Path(target).open("a", encoding="utf-8") as handle:
            handle.write(f"{line}\n")


def _run(command: list[str], env: dict[str, str]) -> None:
    # Resolve the executable against the *child* PATH: on Windows, subprocess
    # otherwise searches the parent's PATH and misses freshly installed tools.
    executable = shutil.which(command[0], path=env.get("PATH")) or command[0]
    print(f"$ {' '.join(command)}", flush=True)
    subprocess.run([executable, *command[1:]], env=env, check=True)


def _bootstrap_poetry(env: dict[str, str], system_python: str) -> None:
    """Install poetry with pipx outside the project environment.

    Poetry lives in its own environment so it never shares dependencies with
    the project, see https://github.com/ansys/actions/pull/560. Its bin dir is
    exported to following steps and ``POETRY_VIRTUALENVS_CREATE=false`` makes
    it install into the ``.venv`` this module creates.
    """
    runner_temp = Path(env.get("RUNNER_TEMP", Path.cwd() / ".pipx-temp"))
    pipx_bin = str(runner_temp / "pipx" / "bin")
    pipx_env = {**env, "PIPX_BIN_DIR": pipx_bin, "PIPX_HOME": str(runner_temp / "pipx" / "home")}
    _run([system_python, "-m", "pip", "install", "pipx"], pipx_env)
    _run([system_python, "-m", "pipx", "install", "poetry"], pipx_env)

    _append("GITHUB_PATH", pipx_bin)
    _append("GITHUB_ENV", "POETRY_VIRTUALENVS_CREATE=false")
    env["PATH"] = os.pathsep.join([pipx_bin, env.get("PATH", "")])
    env["POETRY_VIRTUALENVS_CREATE"] = "false"


def apply_plan(
    plan: EnvironmentPlan, project_dir: Path, is_windows: bool, system_python: str
) -> None:
    """Run the plan in ``project_dir`` and publish its outputs."""
    env = dict(os.environ)

    if plan.bootstrap_poetry:
        _bootstrap_poetry(env, system_python)

    if plan.remove_python_version_file:
        print(f"{PYTHON_VERSION_FILE} file detected. Removing it so uv keeps the selected Python.")
        (project_dir / PYTHON_VERSION_FILE).unlink()

    # Equivalent of activating the virtual environment for every command that follows.
    venv = (project_dir / VENV_DIR).resolve()
    env["VIRTUAL_ENV"] = str(venv)
    env["PATH"] = os.pathsep.join(
        [str(venv / ("Scripts" if is_windows else "bin")), env.get("PATH", "")]
    )

    for command in plan.commands:
        _run(command, env)

    _append("GITHUB_OUTPUT", f"build-backend={plan.backend}")
    _append("GITHUB_OUTPUT", f"use-uv-lockfile={str(plan.use_uv_lockfile).lower()}")
    _append("GITHUB_OUTPUT", f"run-prefix={plan.run_prefix}")


def _flag(name: str, default: bool = False) -> bool:
    return os.environ.get(name, str(default)).strip().lower() == "true"


def main() -> int:
    """Read the action inputs from the environment, then plan and build the environment."""
    inputs = EnvironmentInputs(
        use_uv=_flag("USE_UV"),
        skip_install=_flag("SKIP_INSTALL"),
        optional_dependencies=os.environ.get("OPTIONAL_DEPENDENCIES_NAME", ""),
        group_dependencies=os.environ.get("GROUP_DEPENDENCIES_NAME", ""),
        requirements_file=os.environ.get("REQUIREMENTS_FILE", ""),
    )
    project_dir = Path.cwd()
    is_windows = os.name == "nt"
    try:
        plan = plan_environment(inputs, project_dir, is_windows, sys.executable)
        print(f"Build backend: {plan.backend} | uv lockfile: {plan.use_uv_lockfile}", flush=True)
        apply_plan(plan, project_dir, is_windows, sys.executable)
    except ProjectEnvError as error:
        print(f"::error::{error}", flush=True)
        return 1
    except subprocess.CalledProcessError as error:
        command = " ".join(map(str, error.cmd))
        print(f"::error::Command failed with exit code {error.returncode}: {command}", flush=True)
        return error.returncode or 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
