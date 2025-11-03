from pathlib import Path
import subprocess

import helpers


def test_child_no_clone(uv_run, test_dir):
    subprocess.run(
        ["git", "init", "frogtab"],
        cwd=test_dir,
        check=True,
    )
    command = [*uv_run, "gimmegit", *helpers.no_color, "dwilding/frogtab", "new-branch"]
    result = subprocess.run(
        command,
        cwd=test_dir,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    project_dir = Path(test_dir) / "frogtab"
    expected_stout = """\
Getting repo details
"""
    assert result.stdout == expected_stout
    expected_stderr = f"""\
Error: '{project_dir}' is a repo.
"""
    assert result.stderr == expected_stderr
