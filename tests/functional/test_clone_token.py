import os
import pathlib
import subprocess

import pytest

import helpers


@pytest.fixture()
def token_env():
    env = os.environ.copy()
    env["GIMMEGIT_GITHUB_TOKEN"] = os.environ["GITHUB_TOKEN"]
    return env


@pytest.mark.skipif("GITHUB_TOKEN" not in os.environ, reason="GITHUB_TOKEN is not set")
def test_forked_repo_token(test_dir, token_env):
    command = [
        *helpers.uv_run,
        test_dir,
        "gimmegit",
        *helpers.no_color,
        *helpers.no_ssh,
        "jubilant",
        "my-feature",
    ]
    result = subprocess.run(
        command,
        env=token_env,
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


@pytest.mark.skipif("GITHUB_TOKEN" not in os.environ, reason="GITHUB_TOKEN is not set")
def test_invalid_repo_token(test_dir, token_env):
    command = [
        *helpers.uv_run,
        test_dir,
        "gimmegit",
        *helpers.no_color,
        *helpers.no_ssh,
        "invalid",
    ]
    result = subprocess.run(
        command,
        env=token_env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    expected_stdout = """\
Getting repo details
"""
    assert result.stdout == expected_stdout
    expected_stderr = """\
Error: Unable to find 'dwilding/invalid' on GitHub. Do you have access to the repo?
"""
    assert result.stderr == expected_stderr
    assert not (pathlib.Path(test_dir) / "invalid").exists()
