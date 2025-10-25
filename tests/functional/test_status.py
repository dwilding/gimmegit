from pathlib import Path
import subprocess

import git
import pytest

from gimmegit import _status

import helpers


def test_status(uv_run, test_dir):
    command = [
        *uv_run,
        "gimmegit",
        *helpers.no_color,
        *helpers.no_ssh,
        "-u",
        "canonical",
        "dwilding/jubilant",
        "my-feature",
    ]
    subprocess.run(
        command,
        cwd=test_dir,
        check=True,
    )
    expected_status = _status.Status(
        base_branch="main",
        base_owner="canonical",
        base_url="https://github.com/canonical/jubilant/tree/main",
        branch="my-feature",
        has_remote=False,
        owner="dwilding",
        project="jubilant",
        url="https://github.com/dwilding/jubilant/tree/my-feature",
    )
    expected_dir = Path(test_dir) / "jubilant/dwilding-my-feature"
    repo = git.Repo(expected_dir)
    assert _status.get_status(repo) == expected_status
    # Simulate pushing the branch.
    helpers.set_config(expected_dir, "branch.my-feature.remote", "origin")
    expected_status.has_remote = True
    assert _status.get_status(repo) == expected_status
    # Simulate changing the base branch to origin:main.
    helpers.set_config(expected_dir, "gimmegit.baseRemote", "origin")
    expected_status.base_owner = "dwilding"
    expected_status.base_url = "https://github.com/dwilding/jubilant/tree/main"
    assert _status.get_status(repo) == expected_status
    # Simulate changing the base branch to invalid:main.
    helpers.set_config(expected_dir, "gimmegit.baseRemote", "invalid")
    with pytest.raises(RuntimeError) as exc_info:
        _status.get_status(repo)
    assert str(exc_info.value) == "Unexpected base remote 'invalid'"
