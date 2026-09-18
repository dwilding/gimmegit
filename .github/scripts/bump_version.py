"""Sets a new x.y.z package version."""

import re
import subprocess
import sys
from pathlib import Path

VERSION_FILE = Path("src/gimmegit/_version.py")


def parse_version(version: str) -> tuple[int, ...] | None:
    """Parse 'x.y.z' or 'x.y.z.devN' into a comparable tuple.

    Returns None for anything else. A dev version sorts just before the
    corresponding final release.
    """
    match = re.fullmatch(r"(\d+(?:\.\d+)*)\.dev\d+", version)
    if match:
        return tuple(int(part) for part in match.group(1).split(".")) + (-1,)
    parts = version.split(".")
    if not all(part.isdigit() for part in parts):
        return None
    return tuple(int(part) for part in parts)


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("usage: bump_version.py VERSION")
    new = sys.argv[1]
    parsed = parse_version(new)
    if parsed is None or len(parsed) != 3:
        sys.exit(f"Error: {new} is not an x.y.z version.")
    content = Path("pyproject.toml").read_text()
    match = re.search(r'^version = "(.+)"$', content, re.MULTILINE)
    assert match is not None
    current = match[1]
    current_parsed = parse_version(current)
    assert current_parsed is not None
    if parsed <= current_parsed:
        sys.exit(f"Error: {new} does not exceed the current version {current}.")
    content = re.sub(
        r'^version = ".+"$',
        f'version = "{new}"',
        content,
        count=1,
        flags=re.MULTILINE,
    )
    Path("pyproject.toml").write_text(content)
    VERSION_FILE.write_text(f'__version__ = "{new}"\n')
    subprocess.run(["uv", "lock"], check=True)


if __name__ == "__main__":
    main()
