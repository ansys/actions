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
    print("\nNote: the summary excludes warning supressed by zizmor.")


if __name__ == "__main__":
    main()
