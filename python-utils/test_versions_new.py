import json
import os
import shutil
from pathlib import Path

import pytest
from packaging.version import Version
from versions import get_version_and_ref_type, get_versions_list, set_version_variable


# Monkeypatch has function level scope. This is a workaround
# to allow using monkeypatch at module level
@pytest.fixture(scope="module")
def monkeymodule():
    with pytest.MonkeyPatch.context() as mp:
        yield mp


@pytest.fixture(scope="module", autouse=True)
def general_environment_setup(monkeymodule, tmp_path_factory, request):
    # Set general environment variables
    monkeymodule.setenv("CNAME", "docs.pyansys.com")
    monkeymodule.setenv("RENDER_LAST", "3")

    # Change the working directory to the temp path where tests will run from
    monkeymodule.chdir(tmp_path_factory.getbasetemp())


@pytest.fixture(scope="function")
def test_environment_setup(request, tmp_path_factory, monkeypatch):
    def _create_versions_directories(versions: list[str]):
        # Setup
        version_path = tmp_path_factory.mktemp("version", numbered=False)
        for version_number in versions:
            specific_version_path = version_path / version_number
            specific_version_path.mkdir()

        return version_path

    def _create_github_output_file():
        # Setup
        gh_output_path = tmp_path_factory.getbasetemp() / "gh-output.txt"
        gh_output_path.touch(exist_ok=False)
        monkeypatch.setenv(
            "GITHUB_OUTPUT", str(gh_output_path.resolve())
        )  # Normal monkeypatch, so this is automatically cleaned up between tests

        return gh_output_path

    def _create_versions_json_file(versions: list[str]):
        # Setup
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
        versions_json_path = tmp_path_factory.getbasetemp() / "versions.json"
        with open(versions_json_path, "w") as versions_json_file:
            json.dump(data, versions_json_file, indent=2)

        return versions_json_path

    def _create_prerelease_folder(prerelease_number: str):
        # Setup
        prerelease_version_path = (
            tmp_path_factory.getbasetemp() / "version" / prerelease_number
        )
        prerelease_version_path.mkdir()

        return prerelease_version_path

    # Putting everything together

    # Setup
    # Setup common to all tests
    test_data: dict = request.param

    versions_list: list = test_data["versions"]
    ref_type: str = test_data["ref_type"]
    ref_name: str = test_data["ref_name"]
    independent_patch_release: str = test_data["independent_patch_release"]

    monkeypatch.setenv("REF_TYPE", ref_type)
    monkeypatch.setenv("REF_NAME", ref_name)
    monkeypatch.setenv("INDEPENDENT_PATCH_RELEASE_DOCS", independent_patch_release)

    # Setups that need to be requested by the running test
    create_versions_directories = (
        True if test_data.get("create_versions_directories") else False
    )
    create_github_output_file = (
        True if test_data.get("create_github_output_file") else False
    )
    create_versions_json_file = (
        True if test_data.get("create_versions_json_file") else False
    )
    create_prerelease_folder = (
        True if test_data.get("create_prerelease_folder") else False
    )

    if create_versions_directories:
        version_path = _create_versions_directories(versions_list)

    if create_github_output_file:
        gh_output_path = _create_github_output_file()

    if create_versions_json_file:
        versions_json_path = _create_versions_json_file(versions_list)

    if create_prerelease_folder:
        version_number = (
            ref_name.split("v")[1] if "v" in ref_name else ref_name.split("/")[1]
        )
        prerelease_version_path = _create_prerelease_folder(version_number)

    yield request.param

    # Teardown
    if create_versions_directories:
        # Note: this affects teardown of create_prerelease_folder
        # when both setups are used in a test because the entire version
        # directory is cleared.
        shutil.rmtree(version_path)
    if create_github_output_file:
        gh_output_path.unlink()
    if create_versions_json_file:
        versions_json_path.unlink()
    if create_prerelease_folder:
        # Wrap this in a conditional because of the reason above
        if prerelease_version_path.exists():
            prerelease_version_path.rmdir()


##########################################################################
#         Generic tests, can be applied to multiple datasets             #
##########################################################################
BASE_DATA = [
    {
        "ref_type": "tag",
        "ref_name": "v0.4.0a0",
        "independent_patch_release": "false",
        "versions": ["0.1", "0.2", "0.3"],
    },
    {
        "ref_type": "tag",
        "ref_name": "v0.69.0rc0",
        "independent_patch_release": "false",
        "versions": ["0.66", "0.67", "0.68", "0.69.0a0", "0.69.0b0"],
    },
    {
        "ref_type": "branch",
        "ref_name": "release/0.5.0a0",
        "independent_patch_release": "false",
        "versions": ["0.1", "0.2", "0.3", "0.4"],
    },
]


@pytest.mark.parametrize("test_environment_setup", BASE_DATA, indirect=True)
def test_get_version_and_ref_type(test_environment_setup):
    version, ref_type = get_version_and_ref_type()

    test_data = test_environment_setup
    ref_name = test_data["ref_name"]
    expected_result = (
        ref_name.split("v")[1] if "v" in ref_name else ref_name.split("/")[1],
        test_data["ref_type"],
    )

    assert (version, ref_type) == expected_result


# Modify base data, this test requires versions directory to be present
BASE_DATA_ONE = list(BASE_DATA)
for data in BASE_DATA_ONE:
    data["create_versions_directories"] = True


@pytest.mark.parametrize("test_environment_setup", BASE_DATA_ONE, indirect=True)
def test_get_versions_list_default(test_environment_setup):
    versions_list = get_versions_list()

    test_data = test_environment_setup
    versions = test_data["versions"]
    expected_result = [Version(version) for version in versions]
    versions_list.sort()
    expected_result.sort()

    assert versions_list == expected_result


# Modify base data, this test requires versions directory presence, existence of a prerelease
# directory (can be from test data or by creating a directory for the current prerelease), and
# GITHUB_OUTPUT file
BASE_DATA_TWO = list(BASE_DATA)
for data in BASE_DATA_TWO:
    data["create_versions_directories"] = True
    data["create_prerelease_folder"] = True
    data["create_github_output_file"] = True


@pytest.mark.parametrize("test_environment_setup", BASE_DATA_TWO, indirect=True)
def test_get_versions_list_exclude_prereleases(test_environment_setup):
    versions_list = get_versions_list(exclude_prereleases=True)
    print(versions_list)
    # assert False
    test_data = test_environment_setup
    versions = test_data["versions"]
    expected_result = [
        Version(version) for version in versions if not Version(version).is_prerelease
    ]
    versions_list.sort()
    expected_result.sort()

    assert versions_list == expected_result


# Modify base data, this test requires versions directory presence and GITHUB_OUTPUT file
BASE_DATA_THREE = list(BASE_DATA)
for data in BASE_DATA_THREE:
    data["create_versions_directories"] = True
    data["create_github_output_file"] = True


@pytest.mark.parametrize("test_environment_setup", BASE_DATA_THREE, indirect=True)
def test_set_versions_variable(test_environment_setup):

    set_version_variable()
    gh_output_path = os.getenv("GITHUB_OUTPUT")
    gh_output_content = Path(gh_output_path).read_text()

    test_data = test_environment_setup
    ref_name = test_data["ref_name"]
    version_number = (
        ref_name.split("v")[1] if "v" in ref_name else ref_name.split("/")[1]
    )
    version = Version(version_number)
    prerelease = "true" if version.is_prerelease else "false"
    expected_result = f"VERSION={version_number}\nPRE_RELEASE={prerelease}\n"

    assert gh_output_content == expected_result


# @pytest.mark.parametrize


##########################################################################
#         Specific tests, requires specific setup and datasets           #
##########################################################################

# def test_set_versions_variable_on_independent_patch_release():
#     pass
