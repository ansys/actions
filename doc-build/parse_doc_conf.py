# Copyright (C) 2022 - 2024 ANSYS, Inc. and/or its affiliates.
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

"""
Documentation script.

Notes
-----
Script parsing the documentation's conf.py file to determine the name of
the PDF generated after building the documentation.
"""

import os
import re
import warnings
from pathlib import Path

CONF_PATH = Path("doc", "source", "conf.py")


def get_project_name(conf_path):
    """Parse file to retrieve documentation's project name."""
    res = None
    with open(conf_path, "r") as conf_file:
        for line in conf_file:
            if line.strip().startswith(("project =", "project=")):
                print(line)
                res = re.search(r'project\s*=\s*[\'"](.+)[\'"]', line).group(1)
                break
    return res


def generate_pdf_name(project_name):
    """Convert a project name to a valid file name."""
    # Remove spaces and covert to lowercase
    sanitized_name = re.sub(r"\s+", "", project_name)
    res = f"{sanitized_name.lower()}.pdf"
    return res


project_name = get_project_name(CONF_PATH)

if project_name:
    print(f"Project name: {project_name}")
    pdf_file_name = generate_pdf_name(project_name)
    print(f"PDF file name: {pdf_file_name}")

    # Get the GITHUB_ENV variable
    github_env = os.getenv("GITHUB_ENV")

    # Append PDF_FILENAME with its value to GITHUB_ENV
    with open(github_env, "a") as f:
        f.write(f"PDF_FILENAME={pdf_file_name}")
else:
    warnings.warn(
        "The name of the project is not specified in the documentation's"
        "configuration file. Please, set variable 'project'",
        UserWarning,
    )
