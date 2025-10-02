import os
import subprocess

import pytest

tool_args = ["--color", "never", "--ssh", "never"]


@pytest.mark.skipif("GITHUB_TOKEN" not in os.environ, reason="GITHUB_TOKEN is not set")
def test_fork_jubilant_token(test_dir, tool_cmd):
    result = subprocess.run(
        tool_cmd + tool_args + ["jubilant", "my-feature"],
        env={"GIMMEGIT_GITHUB_TOKEN": os.environ["GITHUB_TOKEN"]},
        capture_output=True,
        text=True,
        check=True,
    )
    expected_stdout = f"""\
Getting repo details
Cloning https://github.com/dwilding/jubilant.git
Setting upstream to https://github.com/canonical/jubilant.git
Checking out a new branch my-feature based on canonical:main
Installing pre-commit using uvx
pre-commit installed at .git/hooks/pre-commit
Cloned repo:
{test_dir}/jubilant/dwilding-my-feature
"""
    assert result.stdout == expected_stdout
