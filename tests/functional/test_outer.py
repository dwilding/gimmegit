import pathlib
import subprocess

import helpers


def test_no_dashboard(test_dir):
    subprocess.run(
        ["git", "init"],
        cwd=test_dir,
        check=True,
    )
    subprocess.run(["mkdir", "foo"], cwd=test_dir, check=True)
    working_dir = pathlib.Path(test_dir) / "foo"
    command = [*helpers.uv_run, working_dir, "gimmegit", *helpers.no_color]
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    expected_stderr = """\
Error: The working directory is inside a repo that is not supported by gimmegit.
"""
    assert result.stderr == expected_stderr


def test_ignore_outer(test_dir):
    working_dir = pathlib.Path(test_dir) / "foo"
    command = [
        *helpers.uv_run,
        working_dir,
        "gimmegit",
        *helpers.no_color,
        *helpers.no_ssh,
        "--ignore-outer",
        "dwilding/frogtab",
        "new-branch",
    ]
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True,
    )
    expected_dir = working_dir / "frogtab/dwilding-new-branch"
    expected_stdout = f"""\
Getting repo details
Cloning https://github.com/dwilding/frogtab.git
Checking out a new branch new-branch based on dwilding:main
Cloned repo:
{expected_dir}
"""
    assert result.stdout == expected_stdout
