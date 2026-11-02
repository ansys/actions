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

"""Tests for the scheduled tooling version updater."""

from pathlib import Path

import update_tooling_versions as tooling_versions


def test_apply_version_updates_to_matching_actions_updates_vale(tmp_path: Path) -> None:
    """Update the Vale input default without changing other version defaults."""
    action_file = tmp_path / "action.yml"
    action_file.write_text(
        "inputs:\n"
        "  vale-version:\n"
        "    description: |\n"
        "      Vale version.\n"
        "    default: '3.25.1'\n"
        "  other-version:\n"
        "    default: '1.2.3'\n",
        encoding="utf-8",
    )

    updated_files = tooling_versions.apply_version_updates_to_matching_actions(
        [action_file], None, None, None, "3.26.0"
    )

    assert updated_files == [action_file]
    updated_text = action_file.read_text(encoding="utf-8")
    assert "default: '3.26.0'" in updated_text
    assert "default: '1.2.3'" in updated_text


def test_resolve_tooling_updates_includes_vale(monkeypatch) -> None:
    """Resolve Vale releases alongside Syft and Quarto."""
    releases = {
        "anchore/syft": "1.2.3",
        "quarto-dev/quarto-cli": "2.3.4",
        "vale-cli/vale": "3.26.0",
    }
    requested_repositories = []

    def get_eligible_release(repository: str, cutoff_seconds: int) -> str:
        requested_repositories.append(repository)
        return releases[repository]

    monkeypatch.setattr(tooling_versions, "get_eligible_release", get_eligible_release)
    monkeypatch.setattr(tooling_versions, "resolve_syft_git_commit_sha", lambda _version: "sha")

    assert tooling_versions.resolve_tooling_updates(60) == ("1.2.3", "sha", "2.3.4", "3.26.0")
    assert requested_repositories == ["anchore/syft", "quarto-dev/quarto-cli", "vale-cli/vale"]
