from pathlib import Path

import tomli

FILE = Path("pyproject.toml")
PYPROJECT_DATA = tomli.loads(FILE.read_text())


def check_poetry_dependencies():
    """Check if any git dependencies in pyproject.toml are missing 'rev' or 'tag'."""
    DEPENDENCIES: dict = PYPROJECT_DATA["tool"]["poetry"]["dependencies"]

    git_dependency_specs = []
    for spec in DEPENDENCIES.values():
        if isinstance(spec, dict) and "git" in spec:
            git_dependency_specs.append(spec)

    if git_dependency_specs:
        print("Git dependency found:")
        for spec in git_dependency_specs:
            print(f"  - {spec}")
        return False
    return True


def check_project_dependencies():
    """Check if any git dependencies in requirements.txt are missing 'rev' or 'tag'."""
    DEPENDENCIES = PYPROJECT_DATA["project"]["dependencies"]

    git_dependency_specs = []
    for spec in DEPENDENCIES:
        if "git+" in spec:
            git_dependency_specs.append(spec)

    if git_dependency_specs:
        print("Git dependency found:")
        for spec in git_dependency_specs:
            print(f"  - {spec}")
        return False
    return True
