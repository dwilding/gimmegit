import subprocess
from pathlib import Path

import git
import pytest

from gimmegit import _cli


def sh(args: list[str], cwd: Path) -> None:
    subprocess.run(
        args,
        cwd=cwd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )


@pytest.fixture
def test_dir(tmp_path_factory):
    yield tmp_path_factory.mktemp("unit_test_alias")


@pytest.fixture
def clone_dir(test_dir):
    """Create a base repo, a clone of it, and a `feat` branch on the clone."""
    base = test_dir / "base"
    clone = test_dir / "clone"
    sh(["git", "init", "-q", "-b", "main", str(base)], test_dir)
    sh(["git", "config", "user.email", "t@t"], base)
    sh(["git", "config", "user.name", "t"], base)
    sh(["git", "commit", "-q", "--allow-empty", "-m", "one"], base)
    sh(["git", "commit", "-q", "--allow-empty", "-m", "two"], base)
    sh(["git", "clone", "-q", str(base), str(clone)], test_dir)
    sh(["git", "config", "user.email", "t@t"], clone)
    sh(["git", "config", "user.name", "t"], clone)
    context = _cli.Context(
        base_branch="main",
        branch="feat",
        clone_url=str(base),
        clone_dir=clone,
        create_branch=True,
        owner="me",
        project="base",
        upstream_owner=None,
        upstream_url=None,
    )
    _cli.create_local_branch(
        git.Repo(clone), None, context, ["--no-tags"]
    )  # Defines the 'update-branch' alias.
    sh(["git", "commit", "-q", "--allow-empty", "-m", "feat"], clone)
    yield clone


def run_alias(clone_dir: Path, args: list[str]) -> str:
    result = subprocess.run(
        ["git", "update-branch", *args],
        cwd=clone_dir,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stderr


@pytest.mark.parametrize(
    "args, command",
    [
        ([], "merge"),
        (["rebase"], "rebase"),
    ],
    ids=["default", "rebase"],
)
def test_update_branch_alias(clone_dir: Path, args: list[str], command: str):
    stderr = run_alias(clone_dir, args)
    assert f"+ git {command} origin/main" in stderr, stderr


def test_update_branch_rebases_not_merges(clone_dir: Path, test_dir: Path):
    sh(["git", "commit", "-q", "--allow-empty", "-m", "three"], test_dir / "base")
    run_alias(clone_dir, ["rebase"])
    subjects = subprocess.run(
        ["git", "log", "--format=%s"],
        cwd=clone_dir,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.splitlines()
    # Exactly these commits, in this order: no merge commit was created.
    assert subjects == ["feat", "three", "two", "one"], subjects
