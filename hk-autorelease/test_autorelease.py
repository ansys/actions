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

import pytest

from autorelease import (
    AutoReleaseError,
    bump_minor_major,
    bump_patch,
    read_version,
    release_branch_name,
    write_version,
)


def test_read_version_file(tmp_path):
    version_file = tmp_path / "VERSION"
    version_file.write_text("1.2.dev0\n")
    assert read_version("file", str(version_file)) == "1.2.dev0"


def test_write_version_file(tmp_path):
    version_file = tmp_path / "VERSION"
    version_file.write_text("1.2.dev0\n")
    write_version("file", str(version_file), "1.2.0")
    assert version_file.read_text() == "1.2.0\n"


def test_read_version_pyproject(tmp_path):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[project]\nname = "demo"\nversion = "1.2.3"\n')
    assert read_version("pyproject", str(pyproject)) == "1.2.3"


def test_write_version_pyproject_preserves_formatting(tmp_path):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[project]\nname = "demo"  # keep me\nversion = "1.2.3"\n')
    write_version("pyproject", str(pyproject), "1.3.0")
    content = pyproject.read_text()
    assert 'version = "1.3.0"' in content
    assert "# keep me" in content


def test_read_version_setup_py(tmp_path):
    setup_py = tmp_path / "setup.py"
    setup_py.write_text(
        "from setuptools import setup\n\nsetup(\n    name='demo',\n    version='1.2.3',\n)\n"
    )
    assert read_version("setup-py", str(setup_py)) == "1.2.3"


def test_write_version_setup_py_preserves_quote_style(tmp_path):
    setup_py = tmp_path / "setup.py"
    setup_py.write_text(
        "from setuptools import setup\n\nsetup(\n    name='demo',\n    version='1.2.3',\n)\n"
    )
    write_version("setup-py", str(setup_py), "1.3.0")
    content = setup_py.read_text()
    assert "version='1.3.0'" in content
    assert "name='demo'" in content


def test_read_version_python_module(tmp_path):
    module = tmp_path / "_version.py"
    module.write_text('__version__ = "1.2.3"\n')
    assert read_version("python-module", str(module)) == "1.2.3"


def test_read_version_python_module_with_type_annotation(tmp_path):
    module = tmp_path / "_version.py"
    module.write_text('__version__: str = "1.2.3"\n')
    assert read_version("python-module", str(module)) == "1.2.3"


def test_write_version_python_module(tmp_path):
    module = tmp_path / "_version.py"
    module.write_text('__version__ = "1.2.3"\n')
    write_version("python-module", str(module), "1.3.0")
    assert module.read_text() == '__version__ = "1.3.0"\n'


def test_read_version_missing_file_raises(tmp_path):
    with pytest.raises(AutoReleaseError, match="does not exist"):
        read_version("file", str(tmp_path / "missing"))


def test_read_version_unparseable_setup_py_raises(tmp_path):
    setup_py = tmp_path / "setup.py"
    setup_py.write_text("from setuptools import setup\n\nsetup(name='demo')\n")
    with pytest.raises(AutoReleaseError, match="Could not find a version string"):
        read_version("setup-py", str(setup_py))


def test_read_version_unknown_source_raises(tmp_path):
    version_file = tmp_path / "VERSION"
    version_file.write_text("1.2.3\n")
    with pytest.raises(AutoReleaseError, match="Unknown version-source"):
        read_version("bogus", str(version_file))


def test_release_branch_name():
    assert release_branch_name("release/", 1, 2) == "release/1.2"


def test_bump_minor_major_minor():
    release_version, dev_version, branch = bump_minor_major("0.2.dev0", "minor", "release/")
    assert release_version == "0.2.0"
    assert dev_version == "0.3.dev0"
    assert branch == "release/0.2"


def test_bump_minor_major_major():
    release_version, dev_version, branch = bump_minor_major("0.2.dev0", "major", "release/")
    assert release_version == "1.0.0"
    assert dev_version == "1.1.dev0"
    assert branch == "release/1.0"


def test_bump_minor_major_invalid_release_type_raises():
    with pytest.raises(AutoReleaseError, match="does not support release-type"):
        bump_minor_major("0.2.dev0", "patch", "release/")


def test_bump_patch():
    assert bump_patch("0.2.0") == "0.2.1"
