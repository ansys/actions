import json

import pytest

from scripts.version_mapper import update_switch_version_file


@pytest.mark.parametrize(
    "new_version, render_last",
    [["0.5", 5], ["0.6", 3]],
    ids=["existing version", "new version"],
)
def test_update_switch_version_file(new_version, render_last, cname):
    # The content for the file shouldn't change since the version already exists
    # and the number of shown versions is the available one
    expected_content = []
    expected_content.append(dict(version="dev", url=f"https://{cname}/dev"))
    minor_version = int(new_version[-1])
    lower_bound, upper_bound = minor_version + 1 - render_last, minor_version + 1
    for ith_version, minor_version in enumerate(
        reversed(range(lower_bound, upper_bound))
    ):
        version_name = f"0.{minor_version}"
        version_name = f"{version_name} (stable)" if ith_version == 0 else version_name
        expected_content.append(
            dict(
                version=version_name,
                url=f"https://{cname}/release/0.{minor_version}",
            )
        )

    # Execute the logic behind the version update script
    update_switch_version_file(
        json_filename="versions.json",
        new_version=new_version,
        cname=cname,
        render_last=render_last,
    )

    with open("release/versions.json", "r") as switcher_file:
        # Load the content of the version file
        current_content = json.load(switcher_file)

        # Verify that the content of the file is the expected one
        assert current_content == expected_content
