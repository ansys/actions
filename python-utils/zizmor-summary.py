# Copyright (C) 2022 - 2026 ANSYS, Inc. and/or its affiliates.
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

import os
import re
import shlex
import subprocess
from collections import Counter
from subprocess import DEVNULL, PIPE

FORMAT = "{:<50}{:<20}"
PATH_RE = re.compile(
    r"[^ /\\]+[\\/](?:[^ /\\]+[\\/])?[^ ]*\.yml"
    if os.name == "nt"
    else r"[^ /]+/(?:[^ /]+/)?[^ ]*\.yml"
)


def main():
    high = os.getenv("HIGH_AUDIT_LEVEL", "")
    strict = os.getenv("STRICT_AUDIT_LEVEL", "")
    if high not in ["--persona=pedantic", ""]:
        raise ValueError(
            f'The value of HIGH_AUDIT_LEVEL environment variable should be "--persona=pedantic", not "{high}".'
        )
    if strict not in ["--persona=auditor", ""]:
        raise ValueError(
            f'The value of STRICT_AUDIT_LEVEL environment variable should be "--persona=auditor", not "{strict}".'
        )
    if high and strict:  # high and strict have both been set
        raise ValueError(
            "One of HIGH_AUDIT_LEVEL, STRICT_AUDIT_LEVEL environment variables should be set, not both."
        )

    cmd = ["zizmor", *shlex.split(high), *shlex.split(strict), "."]

    try:
        proc = subprocess.run(
            cmd,
            text=True,
            stdout=PIPE,  # capture stdout
            stderr=DEVNULL,  # ignore stderr
            check=False,
        )
    except FileNotFoundError:
        print("zizmor not found in PATH")
        return

    print(FORMAT.format("=========", "================"))
    print(FORMAT.format("File name", "Number of issues"))
    print(FORMAT.format("=========", "================"))

    files = []
    for line in proc.stdout.splitlines():
        files.extend(PATH_RE.findall(line))

    counts = Counter(files)
    total = 0
    for wf, n in sorted(counts.items()):
        print(FORMAT.format(wf, n))
        total += n

    print(FORMAT.format("=========", "================"))
    print(FORMAT.format("Total", total))
    print(FORMAT.format("=========", "================"))
    print("\nNote: the summary excludes warning suppressed by zizmor.")


if __name__ == "__main__":
    main()
