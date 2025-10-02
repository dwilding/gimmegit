import subprocess

tool_args = ["--color", "never", "--ssh", "never"]


def test_fork_jubilant(test_dir, tool_cmd):
    result = subprocess.run(
        tool_cmd + tool_args + ["-u", "canonical", "dwilding/jubilant", "my-feature"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout == f"""\
Getting repo details
Cloning https://github.com/dwilding/jubilant.git
Setting upstream to https://github.com/canonical/jubilant.git
Checking out a new branch my-feature based on canonical:main
Installing pre-commit using uvx
pre-commit installed at .git/hooks/pre-commit
Cloned repo:
{test_dir}/jubilant/dwilding-my-feature
"""


def test_fork_jubilant_exists(test_dir, tool_cmd):
    result = subprocess.run(
        tool_cmd + tool_args + ["-u", "canonical", "dwilding/jubilant", "my-feature"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 10
    assert result.stdout == f"""\
Getting repo details
You already have a clone:
{test_dir}/jubilant/dwilding-my-feature
"""
