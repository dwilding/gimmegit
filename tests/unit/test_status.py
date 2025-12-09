import subprocess

import git
import pytest

from gimmegit import _status


def init(dir: str) -> None:
    subprocess.run(
        ["git", "init"],
        cwd=dir,
        check=True,
    )


def set_config(dir: str, name: str, value: str) -> None:
    subprocess.run(
        ["git", "config", name, value],
        cwd=dir,
        check=True,
    )


@pytest.fixture
def test_dir(tmp_path_factory):
    yield tmp_path_factory.mktemp("unit_test_status")


def test_status_base_upstream(test_dir):
    init(test_dir)
    set_config(test_dir, "remote.upstream.url", "https://github.com/canonical/jubilant.git")
    set_config(test_dir, "remote.origin.url", "https://github.com/dwilding/forked-jubilant.git")
    set_config(test_dir, "gimmegit.baseRemote", "upstream")
    set_config(test_dir, "gimmegit.baseBranch", "main")
    set_config(test_dir, "gimmegit.branch", "my-feature")
    expected_status = _status.Status(
        base_branch="main",
        base_owner="canonical",
        base_url="https://github.com/canonical/jubilant/tree/main",
        branch="my-feature",
        has_remote=False,
        owner="dwilding",
        project="jubilant",
        url="https://github.com/dwilding/forked-jubilant/tree/my-feature",
    )
    assert _status.get_status(git.Repo(test_dir)) == expected_status
    # Simulate pushing the branch.
    set_config(test_dir, "branch.my-feature.remote", "origin")
    expected_status.has_remote = True
    assert _status.get_status(git.Repo(test_dir)) == expected_status


def test_status_base_origin(test_dir):
    init(test_dir)
    set_config(test_dir, "remote.origin.url", "https://github.com/dwilding/jubilant.git")
    set_config(test_dir, "gimmegit.baseRemote", "origin")
    set_config(test_dir, "gimmegit.baseBranch", "main")
    set_config(test_dir, "gimmegit.branch", "my-feature")
    expected_status = _status.Status(
        base_branch="main",
        base_owner="dwilding",
        base_url="https://github.com/dwilding/jubilant/tree/main",
        branch="my-feature",
        has_remote=False,
        owner="dwilding",
        project="jubilant",
        url="https://github.com/dwilding/jubilant/tree/my-feature",
    )
    assert _status.get_status(git.Repo(test_dir)) == expected_status
    # Simulate pushing the branch.
    set_config(test_dir, "branch.my-feature.remote", "origin")
    expected_status.has_remote = True
    assert _status.get_status(git.Repo(test_dir)) == expected_status


def test_status_base_invalid(test_dir):
    init(test_dir)
    set_config(test_dir, "remote.origin.url", "https://github.com/dwilding/jubilant.git")
    set_config(test_dir, "gimmegit.baseRemote", "invalid")
    set_config(test_dir, "gimmegit.baseBranch", "main")
    set_config(test_dir, "gimmegit.branch", "my-feature")
    with pytest.raises(RuntimeError) as exc_info:
        print(_status.get_status(git.Repo(test_dir)))
    assert str(exc_info.value) == "Unexpected base remote 'invalid'."


def test_status_not_gimmegit(test_dir):
    init(test_dir)
    assert _status.get_status(git.Repo(test_dir)) is None
