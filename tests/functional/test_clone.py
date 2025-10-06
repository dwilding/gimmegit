import os
import pathlib
import subprocess

import pytest

import helpers

tool_args = ["--color", "never", "--ssh", "never"]


def test_operator_branch(test_dir, tool_cmd):
    result = subprocess.run(
        tool_cmd + tool_args + ["https://github.com/canonical/operator/tree/2.23-maintenance"],
        capture_output=True,
        text=True,
        check=True,
    )
    expected_dir = pathlib.Path(test_dir) / "operator/canonical-2.23-maintenance"
    expected_stdout = f"""\
Getting repo details
Cloning https://github.com/canonical/operator.git
Checking out canonical:2.23-maintenance with base canonical:main
Installing pre-commit using uvx
pre-commit installed at .git/hooks/pre-commit
Cloned repo:
{expected_dir}
"""
    assert result.stdout == expected_stdout
    assert helpers.get_branch(expected_dir) == "2.23-maintenance"
    assert helpers.get_config(expected_dir, "gimmegit.branch") == "2.23-maintenance"
    assert helpers.get_config(expected_dir, "gimmegit.baseRemote") == "origin"
    assert helpers.get_config(expected_dir, "gimmegit.baseBranch") == "main"


def test_fork_jubilant(test_dir, tool_cmd):
    result = subprocess.run(
        tool_cmd + tool_args + ["-u", "canonical", "dwilding/jubilant", "my-feature"],
        capture_output=True,
        text=True,
        check=True,
    )
    expected_dir = pathlib.Path(test_dir) / "jubilant/dwilding-my-feature"
    expected_stdout = f"""\
Getting repo details
Cloning https://github.com/dwilding/jubilant.git
Setting upstream to https://github.com/canonical/jubilant.git
Checking out a new branch my-feature based on canonical:main
Installing pre-commit using uvx
pre-commit installed at .git/hooks/pre-commit
Cloned repo:
{expected_dir}
"""
    assert result.stdout == expected_stdout
    assert helpers.get_branch(expected_dir) == "my-feature"
    assert helpers.get_config(expected_dir, "gimmegit.branch") == "my-feature"
    assert helpers.get_config(expected_dir, "gimmegit.baseRemote") == "upstream"
    assert helpers.get_config(expected_dir, "gimmegit.baseBranch") == "main"


def test_fork_jubilant_exists(test_dir, tool_cmd):
    result = subprocess.run(
        tool_cmd + tool_args + ["-u", "canonical", "dwilding/jubilant", "my-feature"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 10
    expected_dir = pathlib.Path(test_dir) / "jubilant/dwilding-my-feature"
    expected_stdout = f"""\
Getting repo details
You already have a clone:
{expected_dir}
"""
    assert result.stdout == expected_stdout


@pytest.fixture()
def askpass_env():
    env = os.environ.copy()
    env["GIT_ASKPASS"] = "/bin/true"
    return env


def test_invalid_repo(test_dir, tool_cmd, askpass_env):
    result = subprocess.run(
        tool_cmd + tool_args + ["dwilding/invalid", "my-feature"],
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
    assert (pathlib.Path(test_dir) / "invalid").exists()
    assert not (pathlib.Path(test_dir) / "invalid/dwilding-my-feature").exists()
