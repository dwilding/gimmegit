from pathlib import Path
import os
import subprocess

import pytest

import helpers_functional as helpers


@pytest.fixture
def askpass_env():
    env = os.environ.copy()
    env["GIT_ASKPASS"] = "/bin/true"
    return env


def test_invalid_repo(uv_run, test_dir, askpass_env):
    command = [
        *uv_run,
        "gimmegit",
        *helpers.no_color,
        *helpers.no_ssh,
        "dwilding/invalid",
        "my-feature",
    ]
    result = subprocess.run(
        command,
        cwd=test_dir,
        env=askpass_env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    expected_stdout = """\
Getting repo details
Cloning https://github.com/dwilding/invalid.git
"""
    assert result.stdout == expected_stdout
    expected_stderr = """\
Error: Unable to clone repo. Is the repo private? Try configuring Git to use SSH.
"""
    assert result.stderr == expected_stderr
    assert (Path(test_dir) / "invalid").exists()
    assert not (Path(test_dir) / "invalid/dwilding-my-feature").exists()


def test_invalid_upstream(uv_run, test_dir, askpass_env):
    command = [
        *uv_run,
        "gimmegit",
        *helpers.no_color,
        *helpers.no_ssh,
        "-u",
        "_invalid",
        "dwilding/jubilant",
        "my-feature",
    ]
    result = subprocess.run(
        command,
        cwd=test_dir,
        env=askpass_env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    expected_stdout = """\
Getting repo details
Cloning https://github.com/dwilding/jubilant.git
Setting upstream to https://github.com/_invalid/jubilant.git
"""
    assert result.stdout == expected_stdout
    expected_stderr = """\
Error: Unable to fetch upstream repo. Is the repo private? Try configuring Git to use SSH.
"""
    assert result.stderr == expected_stderr
    assert (Path(test_dir) / "jubilant").exists()
    assert not (Path(test_dir) / "jubilant/dwilding-my-feature").exists()
