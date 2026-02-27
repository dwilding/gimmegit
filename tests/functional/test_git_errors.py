import os
import shutil
import subprocess

import pytest

import helpers_functional as helpers


@pytest.fixture
def askpass_env():
    env = os.environ.copy()
    env["GIT_ASKPASS"] = "/bin/true"
    return env


@pytest.mark.parametrize(
    "args",
    [
        ["dwilding/invalid", "my-feature"],
        ["https://github.com/dwilding/invalid/tree/my-feature"],
        ["-j", "dwilding/invalid", "my-feature"],
        ["-j", "https://github.com/dwilding/invalid/tree/my-feature"],
    ],
    ids=["branch_off", "branch", "jumbo_branch_off", "jumbo_branch"],
)
def test_invalid_repo(uv_run, test_dir, askpass_env, args: list[str]):
    shutil.rmtree(test_dir / "invalid", ignore_errors=True)
    command = [
        *uv_run,
        "gimmegit",
        *helpers.no_ssh,
        *args,
    ]
    result = subprocess.run(
        command,
        cwd=test_dir,
        env=askpass_env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    expected_stdout = (
        """\
Getting repo details
Cloning https://github.com/dwilding/invalid.git with limited history
"""
        if args[0] == "-j"
        else """\
Getting repo details
Cloning https://github.com/dwilding/invalid.git
"""
    )
    assert result.stdout == expected_stdout
    expected_stderr = """\
Error: Unable to access repo. Is the repo private? Try configuring Git to use SSH.
"""
    assert result.stderr == expected_stderr
    assert (test_dir / "invalid").exists()
    assert not (test_dir / "invalid/dwilding-my-feature").exists()


@pytest.mark.parametrize(
    "new_branch",
    [
        "main",
        "jubilant-backports",
    ],
)
def test_branch_exists(uv_run, test_dir, askpass_env, new_branch: str):
    command = [
        *uv_run,
        "gimmegit",
        *helpers.no_ssh,
        "canonical/jubilant",
        new_branch,
    ]
    result = subprocess.run(
        command,
        cwd=test_dir,
        env=askpass_env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    expected_stdout = f"""\
Getting repo details
Cloning https://github.com/canonical/jubilant.git
Checking out a new branch {new_branch} based on canonical:main
"""
    assert result.stdout == expected_stdout
    expected_stderr = f"""\
Error: The repo already has a branch {new_branch}.
"""
    assert result.stderr == expected_stderr
    assert (test_dir / "jubilant").exists()
    assert not (test_dir / f"jubilant/canonical-{new_branch}").exists()


def test_invalid_branch(uv_run, test_dir, askpass_env):
    command = [
        *uv_run,
        "gimmegit",
        *helpers.no_ssh,
        "https://github.com/canonical/jubilant/tree/invalid",
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
Cloning https://github.com/canonical/jubilant.git
Checking out canonical:invalid with base canonical:main
"""
    assert result.stdout == expected_stdout
    expected_stderr = """\
Error: The branch canonical:invalid does not exist.
"""
    assert result.stderr == expected_stderr
    assert (test_dir / "jubilant").exists()
    assert not (test_dir / "jubilant/canonical-my-feature").exists()


def test_invalid_branch_with_upstream(uv_run, test_dir, askpass_env):
    command = [
        *uv_run,
        "gimmegit",
        *helpers.no_ssh,
        "-u",
        "canonical",
        "https://github.com/dwilding/jubilant/tree/invalid",
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
Setting upstream to https://github.com/canonical/jubilant.git
Checking out dwilding:invalid with base canonical:main
"""
    assert result.stdout == expected_stdout
    expected_stderr = """\
Error: The branch dwilding:invalid does not exist.
"""
    assert result.stderr == expected_stderr
    assert (test_dir / "jubilant").exists()
    assert not (test_dir / "jubilant/dwilding-my-feature").exists()


def test_branch_invalid_base_origin(uv_run, test_dir, askpass_env):
    command = [
        *uv_run,
        "gimmegit",
        *helpers.no_ssh,
        "-b",
        "invalid",
        "https://github.com/dwilding/jubilant/tree/main",
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
Checking out dwilding:main with base dwilding:invalid
"""
    assert result.stdout == expected_stdout
    expected_stderr = """\
Error: The base branch dwilding:invalid does not exist.
"""
    assert result.stderr == expected_stderr
    assert (test_dir / "jubilant").exists()
    assert not (test_dir / "jubilant/dwilding-main").exists()


def test_branch_invalid_base_upstream(uv_run, test_dir, askpass_env):
    command = [
        *uv_run,
        "gimmegit",
        *helpers.no_ssh,
        "-b",
        "invalid",
        "-u",
        "canonical",
        "https://github.com/dwilding/jubilant/tree/main",
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
Setting upstream to https://github.com/canonical/jubilant.git
Checking out dwilding:main with base canonical:invalid
"""
    assert result.stdout == expected_stdout
    expected_stderr = """\
Error: The base branch canonical:invalid does not exist.
"""
    assert result.stderr == expected_stderr
    assert (test_dir / "jubilant").exists()
    assert not (test_dir / "jubilant/dwilding-main").exists()


def test_new_branch_invalid_base_origin(uv_run, test_dir, askpass_env):
    command = [
        *uv_run,
        "gimmegit",
        *helpers.no_ssh,
        "-b",
        "invalid",
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
Checking out a new branch my-feature based on dwilding:invalid
"""
    assert result.stdout == expected_stdout
    expected_stderr = """\
Error: The base branch dwilding:invalid does not exist.
"""
    assert result.stderr == expected_stderr
    assert (test_dir / "jubilant").exists()
    assert not (test_dir / "jubilant/dwilding-my-feature").exists()


def test_new_branch_invalid_base_upstream(uv_run, test_dir, askpass_env):
    command = [
        *uv_run,
        "gimmegit",
        *helpers.no_ssh,
        "-b",
        "invalid",
        "-u",
        "canonical",
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
Setting upstream to https://github.com/canonical/jubilant.git
Checking out a new branch my-feature based on canonical:invalid
"""
    assert result.stdout == expected_stdout
    expected_stderr = """\
Error: The base branch canonical:invalid does not exist.
"""
    assert result.stderr == expected_stderr
    assert (test_dir / "jubilant").exists()
    assert not (test_dir / "jubilant/dwilding-my-feature").exists()


def test_invalid_upstream(uv_run, test_dir, askpass_env):
    command = [
        *uv_run,
        "gimmegit",
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
Checking out a new branch my-feature based on _invalid:main
"""
    assert result.stdout == expected_stdout
    expected_stderr = """\
Error: Unable to access upstream repo. Is the repo private? Try configuring Git to use SSH.
"""
    assert result.stderr == expected_stderr
    assert (test_dir / "jubilant").exists()
    assert not (test_dir / "jubilant/dwilding-my-feature").exists()


def test_invalid_fetch_opt(uv_run, test_dir):
    command = [
        *uv_run,
        "gimmegit",
        *helpers.no_ssh,
        "dwilding/jubilant",
        "my-feature",
        "--",
        "--invalid",
    ]
    result = subprocess.run(
        command,
        cwd=test_dir,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    expected_stdout = """\
Getting repo details
Cloning https://github.com/dwilding/jubilant.git
"""
    assert result.stdout == expected_stdout
    expected_stderr = """\
Error: Unable to run Git command.

error: unknown option `invalid'
"""
    assert result.stderr.startswith(expected_stderr)
    assert (test_dir / "jubilant").exists()
    assert not (test_dir / "jubilant/dwilding-my-feature").exists()
