import os
import re
import shlex
import subprocess
from collections import Counter
from subprocess import PIPE, DEVNULL

FORMAT = "{:<50}{:<20}"
PATH_RE = re.compile(r"[^ /]+/(?:[^ /]+/)?[^ ]*\.yml")

def main():
    print(FORMAT.format("=========", "================"))
    print(FORMAT.format("File name", "Number of issues"))
    print(FORMAT.format("=========", "================"))

    high = os.getenv("HIGH_AUDIT_LEVEL", "")
    strict = os.getenv("STRICT_AUDIT_LEVEL", "")
    cmd = ["zizmor", *shlex.split(high), *shlex.split(strict), "."]

    try:
        proc = subprocess.run(
            cmd,
            text=True,
            stdout=PIPE,       # capture stdout
            stderr=DEVNULL,    # ignore stderr
            check=False,
        )
    except FileNotFoundError:
        print("zizmor not found in PATH")
        return

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
    print("\nNote: the summary excludes warning surpressed by zizmor.")

if __name__ == "__main__":
    main()
