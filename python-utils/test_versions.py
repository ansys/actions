import os
from pathlib import Path

import pytest
from packaging.version import Version
from versions import get_version_and_ref_type, get_versions_list, set_version_variable


# Workaround to be able t use monkeypatch at module level scope
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
