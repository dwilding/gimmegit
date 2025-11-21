from pathlib import Path
import subprocess

import pytest

import helpers_functional as helpers


@pytest.mark.skipif(helpers.no_token.condition, reason=helpers.no_token.reason)
def test_forked_repo_token(uv_run, test_dir):
    command = [
        *uv_run,
        "gimmegit",
        *helpers.no_color,
        *helpers.no_ssh,
        "jubilant",
        "my-feature",
    ]
    result = subprocess.run(
        command,
        cwd=test_dir,
        env=helpers.token_env(),
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


@pytest.mark.skipif(helpers.no_token.condition, reason=helpers.no_token.reason)
def test_invalid_repo_token(uv_run, test_dir):
    command = [
        *uv_run,
        "gimmegit",
        *helpers.no_color,
        *helpers.no_ssh,
        "invalid",
    ]
    result = subprocess.run(
        command,
        cwd=test_dir,
        env=helpers.token_env(),
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
    assert not (Path(test_dir) / "invalid").exists()


@pytest.mark.skipif(helpers.no_token.condition, reason=helpers.no_token.reason)
def test_u_sets_upstream_owner(uv_run, test_dir):
    command = [
        *uv_run,
        "gimmegit",
        *helpers.no_color,
        *helpers.no_ssh,
        "-u",
        "dwilding",
        "jubilant",
        "my-feature-2",
    ]
    result = subprocess.run(
        command,
        cwd=test_dir,
        env=helpers.token_env(),
        capture_output=True,
        text=True,
        check=True,
    )
    expected_dir = Path(test_dir) / "jubilant/dwilding-my-feature-2"
    expected_stdout = f"""\
Getting repo details
Cloning https://github.com/dwilding/jubilant.git
Checking out a new branch my-feature-2 based on dwilding:main
Installing pre-commit using uvx
pre-commit installed at .git/hooks/pre-commit
Cloned repo:
{expected_dir}
"""
    assert result.stdout == expected_stdout


@pytest.mark.skipif(helpers.no_token.condition, reason=helpers.no_token.reason)
def test_b_sets_upstream_owner(uv_run, test_dir):
    command = [
        *uv_run,
        "gimmegit",
        *helpers.no_color,
        *helpers.no_ssh,
        "-b",
        "https://github.com/dwilding/jubilant/tree/main",
        "jubilant",
        "my-feature-3",
    ]
    result = subprocess.run(
        command,
        cwd=test_dir,
        env=helpers.token_env(),
        capture_output=True,
        text=True,
        check=True,
    )
    expected_dir = Path(test_dir) / "jubilant/dwilding-my-feature-3"
    expected_stdout = f"""\
Getting repo details
Cloning https://github.com/dwilding/jubilant.git
Checking out a new branch my-feature-3 based on dwilding:main
Installing pre-commit using uvx
pre-commit installed at .git/hooks/pre-commit
Cloned repo:
{expected_dir}
"""
    assert result.stdout == expected_stdout
