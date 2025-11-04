from pathlib import Path
import subprocess

import helpers


def test_working_repo_no_dashboard(uv_run, test_dir):
    # .
    # └── frogtab   Suppose that this dir is a repo
    #     └── foo   Try running 'gimmegit'
    repo_dir = Path(test_dir) / "frogtab"
    subprocess.run(
        ["git", "init", repo_dir],
        cwd=test_dir,
        check=True,
    )
    working_dir = repo_dir / "foo"
    working_dir.mkdir()
    command = [*uv_run, "gimmegit", *helpers.no_color]
    result = subprocess.run(
        command,
        cwd=working_dir,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert not result.stdout
    expected_stderr = """\
Error: The working directory is inside a repo that is not supported by gimmegit.
"""
    assert result.stderr == expected_stderr


def test_working_repo_no_clone(uv_run, test_dir):
    # .
    # └── frogtab   Suppose that this dir is a repo
    #     └── foo   Try running 'gimmegit some-project'
    working_dir = Path(test_dir) / "frogtab/foo"
    command = [*uv_run, "gimmegit", *helpers.no_color, "some-project"]
    result = subprocess.run(
        command,
        cwd=working_dir,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert not result.stdout
    expected_stderr = """\
Error: The working directory is inside a repo.
"""
    assert result.stderr == expected_stderr
    assert not (working_dir / "some-project").exists()


def test_working_repo_ignore(uv_run, test_dir):
    # .
    # └── frogtab           Suppose that this dir is a repo
    #     └── foo           Try running 'gimmegit --ignore-outer-repo dwilding/frogtab my-feature'
    #         └── frogtab   These dirs will be created
    #             └── dwilding-my-feature
    working_dir = Path(test_dir) / "frogtab/foo"
    command = [
        *uv_run,
        "gimmegit",
        *helpers.no_color,
        *helpers.no_ssh,
        "--ignore-outer-repo",
        "dwilding/frogtab",
        "my-feature",
    ]
    result = subprocess.run(
        command,
        cwd=working_dir,
        capture_output=True,
        text=True,
        check=True,
    )
    expected_dir = working_dir / "frogtab/dwilding-my-feature"
    expected_stdout = f"""\
Getting repo details
Cloning https://github.com/dwilding/frogtab.git
Checking out a new branch my-feature based on dwilding:main
Cloned repo:
{expected_dir}
"""
    assert result.stdout == expected_stdout


def test_project_repo_no_clone(uv_run, test_dir):
    # .             Try running 'gimmegit dwilding/frogtab my-feature'
    # └── frogtab   Suppose that this dir is a repo
    command = [
        *uv_run,
        "gimmegit",
        *helpers.no_color,
        *helpers.no_ssh,
        "dwilding/frogtab",
        "my-feature",
    ]
    result = subprocess.run(
        command,
        cwd=test_dir,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    project_dir = Path(test_dir) / "frogtab"
    expected_stout = """\
Getting repo details
"""
    assert result.stdout == expected_stout
    expected_stderr = f"""\
Error: '{project_dir}' is a repo.
"""
    assert result.stderr == expected_stderr
    assert not (project_dir / "dwilding-my-feature").exists()


def test_project_repo_ignore(uv_run, test_dir):
    # .                             Try running 'gimmegit --ignore-outer-repo dwilding/frogtab my-feature'
    # └── frogtab                   Suppose that this dir is a repo
    #     └── dwilding-my-feature   This dir will be created
    command = [
        *uv_run,
        "gimmegit",
        *helpers.no_color,
        *helpers.no_ssh,
        "--ignore-outer-repo",
        "dwilding/frogtab",
        "my-feature",
    ]
    result = subprocess.run(
        command,
        cwd=test_dir,
        capture_output=True,
        text=True,
    )
    expected_dir = test_dir / "frogtab/dwilding-my-feature"
    expected_stdout = f"""\
Getting repo details
Cloning https://github.com/dwilding/frogtab.git
Checking out a new branch my-feature based on dwilding:main
Cloned repo:
{expected_dir}
"""
    assert result.stdout == expected_stdout
