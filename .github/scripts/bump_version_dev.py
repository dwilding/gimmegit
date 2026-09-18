"""Sets the next x.y.z.dev0 package version."""

import re
import subprocess
from pathlib import Path

VERSION_FILE = Path("src/gimmegit/_version.py")


def main() -> None:
    content = Path("pyproject.toml").read_text()
    match = re.search(r'^version = "(\d+)\.(\d+)\.(\d+)"$', content, re.MULTILINE)
    assert match is not None
    major, minor, patch = (int(part) for part in match.groups())
    new = f"{major}.{minor}.{patch + 1}.dev0"
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
