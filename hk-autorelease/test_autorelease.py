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

"""Tests for the hk-autorelease version read/write helpers."""

from autorelease import (
    AutoReleaseError,
    bump_minor_major,
    bump_patch,
    classify_merge_conflict,
    dev_version_bump_pr_body,
    dev_version_bump_pr_title,
    main,
    parse_latest_release_tag,
    read_version,
    release_branch_name,
    require_dev_version,
    write_version,
)
import pytest


def test_read_version_file(tmp_path):
    """Test that read_version reads the whole file content for the 'file' source."""
    version_file = tmp_path / "VERSION"
    version_file.write_text("1.2.dev0\n")
    assert read_version("file", str(version_file)) == "1.2.dev0"


def test_write_version_file(tmp_path):
    """Test that write_version overwrites the whole file content for the 'file' source."""
    version_file = tmp_path / "VERSION"
    version_file.write_text("1.2.dev0\n")
    write_version("file", str(version_file), "1.2.0")
    assert version_file.read_text() == "1.2.0\n"


def test_read_version_pyproject(tmp_path):
    """Test that read_version extracts the project.version key from pyproject.toml."""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[project]\nname = "demo"\nversion = "1.2.3"\n')
    assert read_version("pyproject", str(pyproject)) == "1.2.3"


def test_write_version_pyproject_preserves_formatting(tmp_path):
    """Test that write_version preserves comments when updating pyproject.toml."""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[project]\nname = "demo"  # keep me\nversion = "1.2.3"\n')
    write_version("pyproject", str(pyproject), "1.3.0")
    content = pyproject.read_text()
    assert 'version = "1.3.0"' in content
    assert "# keep me" in content


def test_read_version_setup_py(tmp_path):
    """Test that read_version extracts the version= keyword argument from setup.py."""
    setup_py = tmp_path / "setup.py"
    setup_py.write_text(
        "from setuptools import setup\n\nsetup(\n    name='demo',\n    version='1.2.3',\n)\n"
    )
    assert read_version("setup-py", str(setup_py)) == "1.2.3"


def test_write_version_setup_py_preserves_quote_style(tmp_path):
    """Test that write_version keeps the original quote style when updating setup.py."""
    setup_py = tmp_path / "setup.py"
    setup_py.write_text(
        "from setuptools import setup\n\nsetup(\n    name='demo',\n    version='1.2.3',\n)\n"
    )
    write_version("setup-py", str(setup_py), "1.3.0")
    content = setup_py.read_text()
    assert "version='1.3.0'" in content
    assert "name='demo'" in content


def test_read_version_python_module(tmp_path):
    """Test that read_version extracts __version__ from a python module."""
    module = tmp_path / "_version.py"
    module.write_text('__version__ = "1.2.3"\n')
    assert read_version("python-module", str(module)) == "1.2.3"


def test_read_version_python_module_with_type_annotation(tmp_path):
    """Test that read_version handles a type-annotated __version__ assignment."""
    module = tmp_path / "_version.py"
    module.write_text('__version__: str = "1.2.3"\n')
    assert read_version("python-module", str(module)) == "1.2.3"


def test_write_version_python_module(tmp_path):
    """Test that write_version replaces __version__ in a python module."""
    module = tmp_path / "_version.py"
    module.write_text('__version__ = "1.2.3"\n')
    write_version("python-module", str(module), "1.3.0")
    assert module.read_text() == '__version__ = "1.3.0"\n'


def test_read_version_setup_py_ignores_unrelated_version_assignment(tmp_path):
    """Test that read_version ignores a version= assignment outside the setup() call.

    A plain regex search (unanchored) would incorrectly match this decoy assignment first,
    since it appears earlier in the file than the real ``setup(version=...)`` keyword.
    """
    setup_py = tmp_path / "setup.py"
    setup_py.write_text(
        "from setuptools import setup\n\n"
        "version = '9.9.9'  # leftover/unrelated module-level variable\n\n"
        "setup(\n    name='demo',\n    version='1.2.3',\n)\n"
    )
    assert read_version("setup-py", str(setup_py)) == "1.2.3"


def test_read_version_python_module_ignores_commented_out_assignment(tmp_path):
    """Test that read_version ignores a commented-out __version__ assignment."""
    module = tmp_path / "_version.py"
    module.write_text('# __version__ = "0.0.0"\n__version__ = "1.2.3"\n')
    assert read_version("python-module", str(module)) == "1.2.3"


def test_write_version_python_module_with_type_annotation(tmp_path):
    """Test that write_version replaces a type-annotated __version__ assignment."""
    module = tmp_path / "_version.py"
    module.write_text('__version__: str = "1.2.3"\n')
    write_version("python-module", str(module), "1.3.0")
    assert module.read_text() == '__version__: str = "1.3.0"\n'


def test_read_version_missing_file_raises(tmp_path):
    """Test that read_version raises when the version-location file doesn't exist."""
    with pytest.raises(AutoReleaseError, match="does not exist"):
        read_version("file", str(tmp_path / "missing"))


def test_read_version_unparseable_setup_py_raises(tmp_path):
    """Test that read_version raises when setup.py has no version= keyword argument."""
    setup_py = tmp_path / "setup.py"
    setup_py.write_text("from setuptools import setup\n\nsetup(name='demo')\n")
    with pytest.raises(AutoReleaseError, match="Could not find a version string"):
        read_version("setup-py", str(setup_py))


def test_read_version_syntax_error_raises(tmp_path):
    """Test that read_version raises AutoReleaseError (not SyntaxError) for invalid Python."""
    setup_py = tmp_path / "setup.py"
    setup_py.write_text("def broken(:\n")
    with pytest.raises(AutoReleaseError, match="Could not parse"):
        read_version("setup-py", str(setup_py))


def test_read_version_unknown_source_raises(tmp_path):
    """Test that read_version raises for an unrecognized version-source."""
    version_file = tmp_path / "VERSION"
    version_file.write_text("1.2.3\n")
    with pytest.raises(AutoReleaseError, match="Unknown version-source"):
        read_version("bogus", str(version_file))


def test_release_branch_name():
    """Test that release_branch_name joins the prefix with major.minor."""
    assert release_branch_name("release/", 1, 2) == "release/1.2"


def test_bump_minor_major_minor():
    """Test that bump_minor_major computes the correct minor release and next dev version."""
    release_version, dev_version, branch = bump_minor_major("0.2.dev0", "minor", "release/")
    assert release_version == "0.2.0"
    assert dev_version == "0.3.dev0"
    assert branch == "release/0.2"


def test_bump_minor_major_major():
    """Test that bump_minor_major computes the correct major release and next dev version."""
    release_version, dev_version, branch = bump_minor_major("0.2.dev0", "major", "release/")
    assert release_version == "1.0.0"
    assert dev_version == "1.1.dev0"
    assert branch == "release/1.0"


def test_bump_minor_major_invalid_release_type_raises():
    """Test that bump_minor_major rejects a release-type other than minor/major."""
    with pytest.raises(AutoReleaseError, match="does not support release-type"):
        bump_minor_major("0.2.dev0", "patch", "release/")


def test_bump_patch():
    """Test that bump_patch increments only the patch component."""
    assert bump_patch("0.2.0") == "0.2.1"


def test_parse_latest_release_tag_picks_first_matching_tag():
    """Test that parse_latest_release_tag returns the first vX.Y.Z tag in the list."""
    tag_lines = ["v1.3.0", "v1.2.1", "v1.2.0"]
    assert parse_latest_release_tag(tag_lines) == (1, 3, 0)


def test_parse_latest_release_tag_skips_non_matching_tags():
    """Test that parse_latest_release_tag skips tags that aren't vX.Y.Z."""
    tag_lines = ["not-a-version", "v2.0.0"]
    assert parse_latest_release_tag(tag_lines) == (2, 0, 0)


def test_parse_latest_release_tag_raises_when_no_match():
    """Test that parse_latest_release_tag raises when no tag matches vX.Y.Z."""
    with pytest.raises(AutoReleaseError, match="No 'vX.Y.Z' tags found"):
        parse_latest_release_tag([])


def test_classify_merge_conflict_version_file_only():
    """Test that classify_merge_conflict returns True when only the version file conflicts."""
    assert classify_merge_conflict(["VERSION"], "VERSION") is True


def test_classify_merge_conflict_other_files():
    """Test that classify_merge_conflict returns False when other files also conflict."""
    assert classify_merge_conflict(["VERSION", "README.md"], "VERSION") is False


def test_classify_merge_conflict_unrelated_file():
    """Test that classify_merge_conflict returns False when the version file isn't conflicted."""
    assert classify_merge_conflict(["README.md"], "VERSION") is False


def test_main_invalid_release_type_raises(monkeypatch):
    """Test that main raises AutoReleaseError for an invalid RELEASE_TYPE."""
    monkeypatch.setenv("RELEASE_TYPE", "bogus")
    monkeypatch.setenv("VERSION_SOURCE", "file")
    monkeypatch.setenv("VERSION_LOCATION", "VERSION")
    monkeypatch.setenv("MAIN_BRANCH", "main")
    monkeypatch.setenv("RELEASE_BRANCH_PREFIX", "release/")
    with pytest.raises(AutoReleaseError, match="Invalid release-type"):
        main()


def test_main_invalid_version_source_raises(monkeypatch):
    """Test that main raises AutoReleaseError for an invalid VERSION_SOURCE."""
    monkeypatch.setenv("RELEASE_TYPE", "patch")
    monkeypatch.setenv("VERSION_SOURCE", "bogus")
    monkeypatch.setenv("VERSION_LOCATION", "VERSION")
    monkeypatch.setenv("MAIN_BRANCH", "main")
    monkeypatch.setenv("RELEASE_BRANCH_PREFIX", "release/")
    with pytest.raises(AutoReleaseError, match="Invalid version-source"):
        main()


def test_main_missing_env_var_raises(monkeypatch):
    """Test that main raises AutoReleaseError (not KeyError) for a missing env var."""
    monkeypatch.setenv("VERSION_SOURCE", "file")
    monkeypatch.setenv("VERSION_LOCATION", "VERSION")
    monkeypatch.setenv("MAIN_BRANCH", "main")
    monkeypatch.setenv("RELEASE_BRANCH_PREFIX", "release/")
    monkeypatch.delenv("RELEASE_TYPE", raising=False)
    with pytest.raises(AutoReleaseError, match="RELEASE_TYPE"):
        main()


def test_main_patch_cherry_pick_requires_commits(monkeypatch):
    """Test that main raises AutoReleaseError when patch-cherry-pick has no commits listed."""
    monkeypatch.setenv("RELEASE_TYPE", "patch-cherry-pick")
    monkeypatch.setenv("VERSION_SOURCE", "file")
    monkeypatch.setenv("VERSION_LOCATION", "VERSION")
    monkeypatch.setenv("MAIN_BRANCH", "main")
    monkeypatch.setenv("RELEASE_BRANCH_PREFIX", "release/")
    monkeypatch.setenv("CHERRY_PICK_COMMITS", "   ")
    with pytest.raises(AutoReleaseError, match="requires at least one commit"):
        main()


def test_main_invalid_release_type_still_rejects_bogus_value(monkeypatch):
    """Test that main still rejects a release-type outside the known set, incl. the new one."""
    monkeypatch.setenv("RELEASE_TYPE", "patch-cherry-picks")  # typo'd plural, invalid
    monkeypatch.setenv("VERSION_SOURCE", "file")
    monkeypatch.setenv("VERSION_LOCATION", "VERSION")
    monkeypatch.setenv("MAIN_BRANCH", "main")
    monkeypatch.setenv("RELEASE_BRANCH_PREFIX", "release/")
    with pytest.raises(AutoReleaseError, match="Invalid release-type"):
        main()


def test_require_dev_version_accepts_dev_version():
    """Test that require_dev_version accepts a 'X.Y.devN' version."""
    require_dev_version("0.2.dev0", "main")


def test_require_dev_version_rejects_release_version():
    """Test that require_dev_version rejects a plain release version."""
    with pytest.raises(AutoReleaseError, match="Expected a development version"):
        require_dev_version("0.2.0", "main")


def test_dev_version_bump_pr_title():
    """Test that dev_version_bump_pr_title names the target dev version."""
    assert dev_version_bump_pr_title("0.3.dev0") == "chore: bump dev version to v0.3.dev0"


def test_dev_version_bump_pr_body_mentions_release_and_caution():
    """Test that dev_version_bump_pr_body references the release version and warns not to merge."""
    body = dev_version_bump_pr_body("0.2.0")
    assert "v0.2.0" in body
    assert "[!CAUTION]" in body
    assert "release-github" in body or "release-pypi" in body
