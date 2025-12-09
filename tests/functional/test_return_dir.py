from pathlib import Path
import subprocess

import helpers_functional as helpers


def test_return_dir_new_clone(uv_run, test_dir):
    command = [
        *uv_run,
        "gimmegit",
        "--return-dir",
        *helpers.no_ssh,
        "dwilding/jubilant",
        "my-feature",
    ]
    result = subprocess.run(
        command,
        cwd=test_dir,
        capture_output=True,
        text=True,
        check=True,
    )
    expected_dir = Path(test_dir) / "jubilant/dwilding-my-feature"
    expected_stdout = f"""\
{expected_dir}
"""
    assert result.stdout == expected_stdout
    expected_stderr = f"""\
Getting repo details
Cloning https://github.com/dwilding/jubilant.git
Checking out a new branch my-feature based on dwilding:main
Installing pre-commit hook
Cloned repo:
{expected_dir}
"""
    assert result.stderr == expected_stderr


def test_return_dir_existing_clone(uv_run, test_dir):
    command = [
        *uv_run,
        "gimmegit",
        "--return-dir",
        *helpers.no_ssh,
        "dwilding/jubilant",
        "my-feature",
    ]
    result = subprocess.run(
        command,
        cwd=test_dir,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 10
    expected_dir = Path(test_dir) / "jubilant/dwilding-my-feature"
    expected_stdout = f"""\
{expected_dir}
"""
    assert result.stdout == expected_stdout
    expected_stderr = f"""\
Getting repo details
You already have a clone:
{expected_dir}
"""
    assert result.stderr == expected_stderr
