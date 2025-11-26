from pathlib import Path
import subprocess

import helpers_functional as helpers


def test_repo_branch(uv_run, test_dir):
    command = [
        *uv_run,
        "gimmegit",
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
    command = [*uv_run, "gimmegit"]
    result = subprocess.run(
        command,
        cwd=working_dir,
        capture_output=True,
        text=True,
        check=True,
    )
    expected_stdout = """\
The working directory is inside a gimmegit clone.
"""
    assert result.stdout == expected_stdout


def test_dashboard_warning(uv_run, test_dir):
    working_dir = Path(test_dir) / "jubilant/dwilding-my-feature/docs"
    command = [*uv_run, "gimmegit", "some-project"]
    result = subprocess.run(
        command,
        cwd=working_dir,
        capture_output=True,
        text=True,
        check=True,
    )
    expected_stdout = """\
The working directory is inside a gimmegit clone.
"""
    assert result.stdout == expected_stdout
    expected_stderr = """\
Warning: Skipped cloning because the working directory is inside a gimmegit clone.
"""
    assert result.stderr == expected_stderr


def test_in_project_dir(uv_run, test_dir):
    # .
    # └── jubilant                  Try running 'gimmegit dwilding/jubilant my-feature'
    #     └── dwilding-my-feature   This dir exists from an earlier test
    working_dir = Path(test_dir) / "jubilant"
    command = [
        *uv_run,
        "gimmegit",
        *helpers.no_ssh,
        "dwilding/jubilant",
        "my-feature",
    ]
    result = subprocess.run(
        command,
        cwd=working_dir,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    expected_stdout = """\
Getting repo details
"""
    assert result.stdout == expected_stdout
    expected_stderr = """\
Error: The working directory has a gimmegit clone. Try running gimmegit in the parent directory.
"""
    assert result.stderr == expected_stderr
    assert not (working_dir / "jubilant").exists()


def test_in_project_dir_force(uv_run, test_dir):
    # .
    # └── jubilant                  Try running 'gimmegit dwilding/jubilant my-feature'
    #     ├── dwilding-my-feature   This dir exists from an earlier test
    #     └── jubilant              These dirs will be created
    #         └── dwilding-my-feature
    working_dir = Path(test_dir) / "jubilant"
    command = [
        *uv_run,
        "gimmegit",
        *helpers.no_ssh,
        "--force-project-dir",
        "dwilding/jubilant",
        "my-feature",
    ]
    result = subprocess.run(
        command,
        cwd=working_dir,
        capture_output=True,
        text=True,
        check=True,
    )
    expected_dir = working_dir / "jubilant/dwilding-my-feature"
    expected_stdout = f"""\
Getting repo details
Cloning https://github.com/dwilding/jubilant.git
Checking out a new branch my-feature based on dwilding:main
Installing pre-commit using uvx
pre-commit installed at .git/hooks/pre-commit
Cloned repo:
{expected_dir}
"""
    assert result.stdout == expected_stdout
