"""Checks for inconsistencies between uv.lock and pyproject.toml."""

import re
import subprocess


def main() -> None:
    passed = True
    packages = direct_deps()
    result = subprocess.run(
        ["uv", "lock", "--dry-run", "--resolution", "lowest-direct"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=True,
    )
    for line in result.stdout.splitlines():
        if not line.startswith("Update "):
            continue
        parts = line.split(maxsplit=2)
        if len(parts) < 2:
            continue
        if parts[1] in packages:
            print(line)
            passed = False
    if not passed:
        raise SystemExit(
            "These changes would have been made to the lockfile. Bump the project deps instead."
        )


def direct_deps() -> list[str]:
    packages = []
    result = subprocess.run(
        ["uv", "tree", "--depth", "1"],
        capture_output=True,
        text=True,
        check=True,
    )
    package_pattern = re.compile(r"─ ([^ \[]+)")
    for line in result.stdout.splitlines():
        match = package_pattern.search(line)
        if match is None:
            continue
        packages.append(match.group(1))
    return packages


if __name__ == "__main__":
    main()
