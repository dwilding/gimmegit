from gimmegit import _remote

import pytest


def test_remote_from_ssh():
    remote = _remote.remote_from_url("git@github.com:my-name/my-project.git")
    assert remote.owner == "my-name"
    assert remote.project == "my-project"
    assert remote.url == "git@github.com:my-name/my-project.git"


def test_remote_from_https():
    remote = _remote.remote_from_url("https://github.com/my-name/my-project.git")
    assert remote.owner == "my-name"
    assert remote.project == "my-project"
    assert remote.url == "https://github.com/my-name/my-project.git"


def test_remote_from_invalid():
    with pytest.raises(ValueError):
        _remote.remote_from_url("github.com/my-name/my-project")
