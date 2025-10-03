import os
import pathlib
import subprocess

import pytest

tool_args = ["--color", "never", "--ssh", "never"]


def get_branch(dir: str):
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=dir,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


@pytest.fixture()
def token_env():
    env = os.environ.copy()
    env["GIMMEGIT_GITHUB_TOKEN"] = os.environ["GITHUB_TOKEN"]
    return env


@pytest.mark.skipif("GITHUB_TOKEN" not in os.environ, reason="GITHUB_TOKEN is not set")
def test_fork_jubilant_token(test_dir, tool_cmd, token_env):
    result = subprocess.run(
        tool_cmd + tool_args + ["jubilant", "my-feature"],
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
    assert get_branch(expected_dir) == "my-feature"
