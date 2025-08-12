import json
import os
from pathlib import Path

import pytest
from packaging.version import Version
from versions import (
    find_stable_release,
    get_version_and_ref_type,
    get_versions_list,
    set_version_variable,
    write_versions_file,
)


# Monkeypatch has function level scope. This is a workaround
# to allow using monkeypatch at module level
@pytest.fixture(scope="module")
def monkeymodule():
    with pytest.MonkeyPatch.context() as mp:
        yield mp


@pytest.fixture(
    scope="module", params=[("tag", "v0.3.4a1", "false", ["0.1", "0.2", "0.3"])]
)
def set_testing_environment(monkeymodule, tmp_path_factory, request):
    # Create folders to mimic the contents of the version directory
    # on a typical gh-pages branch
    version_path = tmp_path_factory.mktemp("version", numbered=False)

    for version_number in request.param[3]:
        specific_version_path = version_path / version_number
        specific_version_path.mkdir()

    # Set environment variables to mimic information passed during a
    # github actions workflow
    monkeymodule.setenv("CNAME", "docs.pyansys.com")
    monkeymodule.setenv("RENDER_LAST", "3")
    monkeymodule.setenv("REF_TYPE", request.param[0])
    monkeymodule.setenv("REF_NAME", request.param[1])
    monkeymodule.setenv("INDEPENDENT_PATCH_RELEASE_DOCS", request.param[2])

    # Create a file to mimick the github output file
    gh_output_path = tmp_path_factory.getbasetemp() / "gh-output.txt"
    if (
        gh_output_path.exists()
    ):  # Clear between successive parameterized runs on this fixture
        gh_output_path.unlink
    gh_output_path.touch(exist_ok=False)
    monkeymodule.setenv("GITHUB_OUTPUT", str(gh_output_path.resolve()))

    # Change the cwd to a temporary one where the tests will run from
    monkeymodule.chdir(tmp_path_factory.getbasetemp())

    # Create a versions.json file
    def create_versions_json(versions):
        def ver_key(v):
            return [int(x) for x in str(v).split(".")]

        versions = sorted(versions, key=ver_key, reverse=True)
        data = [
            {
                "name": "dev",
                "version": "dev",
                "url": "https://docs.pyansys.com/version/dev/",
            }
        ]
        for i, v in enumerate(versions):
            v_str = str(v)
            name = f"{v_str} (stable)" if i == 0 else v_str
            url = f"https://docs.pyansys.com/version/{'stable' if i == 0 else v_str}/"
            data.append({"name": name, "version": v_str, "url": url})
        data.append(
            {
                "name": "Older versions",
                "version": "N/A",
                "url": "https://docs.pyansys.com/version/",
            }
        )
        with open("versions.json", "w") as f:
            json.dump(data, f, indent=2)

    create_versions_json(request.param[3])

    # Trick to be able to create prerelease folder at function scope
    def _create_prerelease_folder():
        prerelease_number = request.param[1]
        prerelease_version_path = version_path / prerelease_number
        prerelease_version_path.mkdir()
        return prerelease_version_path

    return _create_prerelease_folder


# Creates prerelease folder at function level scope
@pytest.fixture(scope="function")
def create_prerelease_folder(set_testing_environment):
    # Setup
    pre_release_version_path = set_testing_environment()
    yield

    # Teardown
    pre_release_version_path.rmdir()


def test_get_version_and_ref_type(set_testing_environment):
    version, ref_type = get_version_and_ref_type()
    assert version, ref_type == ("0.3.4a1", "tag")


def test_get_versions_list(set_testing_environment):
    assert all(
        version in [Version("0.1"), Version("0.2"), Version("0.3")]
        for version in get_versions_list()
    )


def test_set_version_variable(set_testing_environment):
    set_version_variable()
    gh_output_path = os.getenv("GITHUB_OUTPUT")
    gh_output_content = Path(gh_output_path).read_text()
    assert gh_output_content == "VERSION=0.3.4a1\nPRE_RELEASE=true\n"


def test_find_stable_release(create_prerelease_folder):
    stable_release = find_stable_release()

    assert stable_release == "0.3"


def test_write_versions_file(create_prerelease_folder):
    write_versions_file()

    # versions_json_path = Path("versions.json")
    # versions_json_content = versions_json_path.read_text(encoding="utf-8")
    # print(versions_json_content)

    gh_output_path = os.getenv("GITHUB_OUTPUT")
    gh_output_content = Path(gh_output_path).read_text()
    print(gh_output_content)

    assert "LATEST_STABLE_VERSION=0.3" in gh_output_content
