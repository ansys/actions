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
"""Tests for the parse_pr module."""

from parse_pr import get_invalid_title_characters
import pytest


@pytest.mark.parametrize(
    "title",
    [
        "feat: Add support for Python 3.14",
        "fix(mapdl): Resolve PyMAPDL installation errors",
        "docs: Update installation/setup instructions",
        "fix: Handle _download_file in PyMAPDL",
        "fix: Update the ansys.mapdl.core import path",
    ],
)
def test_allowed_title(title):
    """Test that typical PyAnsys pull request titles are accepted."""
    assert get_invalid_title_characters(title) == []


@pytest.mark.parametrize("character", ["*", "`", "[", "]", ">", "#", "\\", "@", "+", ","])
def test_rejects_unsupported_characters(character):
    """Test that rich text and other unsupported characters are rejected."""
    assert get_invalid_title_characters(f"fix: title {character}") == [character]
