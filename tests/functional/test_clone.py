from pathlib import Path
import os
import subprocess

import pytest

import helpers


def test_repo_branch(uv_run, test_dir):
    command = [
        *uv_run,
        "gimmegit",
        *helpers.no_color,
        *helpers.no_ssh,
        "https://github.com/canonical/operator/tree/2.23-maintenance",
    ]
    result = subprocess.run(
        command,
        cwd=test_dir,
        capture_output=True,
        text=True,
        check=True,
    )
    expected_dir = Path(test_dir) / "operator/canonical-2.23-maintenance"
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


def test_forked_repo(uv_run, test_dir):
    command = [
        *uv_run,
        "gimmegit",
        *helpers.no_color,
        *helpers.no_ssh,
        "-u",
        "canonical",
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


def test_existing_clone(uv_run, test_dir):
    command = [
        *uv_run,
        "gimmegit",
        *helpers.no_color,
        *helpers.no_ssh,
        "-u",
        "canonical",
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
Getting repo details
You already have a clone:
{expected_dir}
"""
    assert result.stdout == expected_stdout


def test_dashboard(uv_run, test_dir):
    working_dir = Path(test_dir) / "jubilant/dwilding-my-feature/docs"
    command = [*uv_run, "gimmegit", *helpers.no_color]
    result = subprocess.run(
        command,
        cwd=working_dir,
        capture_output=True,
        text=True,
        check=True,
    )
    expected_stdout = """\
[STATUS DASHBOARD]
"""
    assert result.stdout == expected_stdout


def test_dashboard_warning(uv_run, test_dir):
    working_dir = Path(test_dir) / "jubilant/dwilding-my-feature/docs"
    command = [*uv_run, "gimmegit", *helpers.no_color, "some-repo"]
    result = subprocess.run(
        command,
        cwd=working_dir,
        capture_output=True,
        text=True,
        check=True,
    )
    expected_stdout = """\
[STATUS DASHBOARD]
"""
    assert result.stdout == expected_stdout
    expected_stderr = """\
Warning: Ignoring 'some-repo' because the working directory is inside a repo.
"""
    assert result.stderr == expected_stderr


@pytest.fixture()
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


def test_no_repo(uv_run, test_dir):
    command = [
        *uv_run,
        "gimmegit",
        *helpers.no_color,
    ]
    result = subprocess.run(
        command,
        cwd=test_dir,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert not result.stdout
    expected_stderr = """\
Error: No repo specified. Run 'gimmegit -h' for help.
"""
    assert result.stderr == expected_stderr
