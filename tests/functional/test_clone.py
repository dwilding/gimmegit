import pathlib
import subprocess

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
    assert get_branch(expected_dir) == "2.23-maintenance"


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
    assert get_branch(expected_dir) == "my-feature"


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
