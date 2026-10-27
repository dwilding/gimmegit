import argparse
from dataclasses import dataclass, field
from pathlib import Path
from types import SimpleNamespace

import github
import pytest

from gimmegit import _cli, _remote

FORKED_REPO = SimpleNamespace(
    fork=True,
    parent=SimpleNamespace(
        owner=SimpleNamespace(login="canonical"),
        name="jubilant",
    ),
)


@pytest.fixture(autouse=True)
def no_ssh(monkeypatch):
    monkeypatch.setattr("gimmegit._remote.is_ssh_configured", lambda: False)


@pytest.fixture(autouse=True)
def snapshot_name(monkeypatch):
    monkeypatch.setattr("gimmegit._cli.make_snapshot_name", lambda: "snapshot0801")


@dataclass
class FakeGithubState:
    repo: object | None = None
    user: object | None = None
    missing: bool = False  # Whether to raise UnknownObjectException for a missing repo.
    denied: bool = False  # Whether to raise BadCredentialsException for a rejected token.
    clients: list = field(default_factory=list)
    repo_calls: list = field(default_factory=list)


@pytest.fixture
def fake_github(monkeypatch):
    """Stand-in for github.Github. Set state.repo or state.user before calling the function under test."""

    state = FakeGithubState()

    class FakeGithub:
        def __init__(self, login_or_token=None, **kwargs):
            self.token = login_or_token
            state.clients.append(self)

        def get_repo(self, owner_project):
            state.repo_calls.append(owner_project)
            if state.missing:
                raise github.UnknownObjectException(404, None)
            if state.denied:
                raise github.BadCredentialsException(401, "Bad credentials")
            return state.repo

        def get_user(self):
            if state.denied:
                raise github.BadCredentialsException(401, "Bad credentials")
            return state.user

    monkeypatch.setattr(github, "Github", FakeGithub)
    return state


@pytest.mark.parametrize("token", [None, ""])
def test_github_url_token_unset(monkeypatch, fake_github, token):
    monkeypatch.setattr(_cli, "GITHUB_TOKEN", token)
    with pytest.raises(ValueError) as exc_info:
        _cli.make_github_url("frogtab")
    assert str(exc_info.value) == (
        "GIMMEGIT_GITHUB_TOKEN is not set. For the repo, use '<owner>/<project>' or a GitHub URL."
    )
    assert fake_github.clients == []


@pytest.mark.parametrize("repo", ["frogtab", "frogtab/"])
def test_github_url_project(monkeypatch, fake_github, repo):
    monkeypatch.setattr(_cli, "GITHUB_TOKEN", "fake-token")
    fake_github.user = SimpleNamespace(login="dwilding")
    assert _cli.make_github_url(repo) == "https://github.com/dwilding/frogtab"
    assert fake_github.clients[0].token == "fake-token"


def test_github_url_denied(monkeypatch, fake_github):
    monkeypatch.setattr(_cli, "GITHUB_TOKEN", "bad-token")
    fake_github.denied = True
    with pytest.raises(ValueError) as exc_info:
        _cli.make_github_url("frogtab")
    assert str(exc_info.value) == "GitHub rejected the token. Has the token expired?"


@pytest.mark.parametrize("token", [None, ""])
def test_upstream_token_unset(monkeypatch, fake_github, token):
    monkeypatch.setattr(_cli, "GITHUB_TOKEN", token)
    assert _cli.get_github_upstream("dwilding", "forked-jubilant") is None
    assert fake_github.clients == []


def test_upstream_fork(monkeypatch, fake_github):
    monkeypatch.setattr(_cli, "GITHUB_TOKEN", "fake-token")
    fake_github.repo = FORKED_REPO
    remote = _cli.get_github_upstream("dwilding", "forked-jubilant")
    assert remote == _remote.Remote(
        owner="canonical",
        project="jubilant",
        url="https://github.com/canonical/jubilant.git",
    )
    assert fake_github.repo_calls == ["dwilding/forked-jubilant"]
    assert fake_github.clients[0].token == "fake-token"


def test_upstream_fork_ssh(monkeypatch, fake_github):
    monkeypatch.setattr(_cli, "GITHUB_TOKEN", "fake-token")
    monkeypatch.setattr(_cli, "SSH", True)
    fake_github.repo = FORKED_REPO
    remote = _cli.get_github_upstream("dwilding", "forked-jubilant")
    assert remote == _remote.Remote(
        owner="canonical",
        project="jubilant",
        url="git@github.com:canonical/jubilant.git",
    )


def test_upstream_not_fork(monkeypatch, fake_github):
    monkeypatch.setattr(_cli, "GITHUB_TOKEN", "fake-token")
    fake_github.repo = SimpleNamespace(fork=False)
    assert _cli.get_github_upstream("dwilding", "forked-jubilant") is None


def test_upstream_missing(monkeypatch, fake_github):
    monkeypatch.setattr(_cli, "GITHUB_TOKEN", "fake-token")
    fake_github.missing = True
    with pytest.raises(ValueError) as exc_info:
        _cli.get_github_upstream("dwilding", "invalid")
    assert (
        str(exc_info.value)
        == "Unable to find 'dwilding/invalid' on GitHub. Do you have access to the repo?"
    )


def test_upstream_denied(monkeypatch, fake_github):
    monkeypatch.setattr(_cli, "GITHUB_TOKEN", "bad-token")
    fake_github.denied = True
    with pytest.raises(ValueError) as exc_info:
        _cli.get_github_upstream("dwilding", "frogtab")
    assert str(exc_info.value) == "GitHub rejected the token. Has the token expired?"


def test_context_fork(monkeypatch, fake_github):
    monkeypatch.setattr(_cli, "GITHUB_TOKEN", "fake-token")
    fake_github.repo = FORKED_REPO
    args = argparse.Namespace(
        base_branch=None,
        upstream_owner=None,
        repo="dwilding/forked-jubilant",
        new_branch=None,
    )
    expected_context = _cli.Context(
        base_branch=None,
        branch="snapshot0801",
        clone_url="https://github.com/dwilding/forked-jubilant.git",
        clone_dir=Path("jubilant/dwilding-snapshot0801"),
        create_branch=True,
        owner="dwilding",
        project="jubilant",
        upstream_owner="canonical",
        upstream_url="https://github.com/canonical/jubilant.git",
    )
    assert _cli.get_context(args) == expected_context


# -u overrides the fork's upstream, but get_context still queries the fork.
# The query doubles as a fast-fail check that the repo exists, so it's worth keeping.
def test_context_fork_u_overrides_upstream(monkeypatch, fake_github):
    monkeypatch.setattr(_cli, "GITHUB_TOKEN", "fake-token")
    fake_github.repo = FORKED_REPO
    args = argparse.Namespace(
        base_branch=None,
        upstream_owner="some-org",
        repo="dwilding/forked-jubilant",
        new_branch=None,
    )
    expected_context = _cli.Context(
        base_branch=None,
        branch="snapshot0801",
        clone_url="https://github.com/dwilding/forked-jubilant.git",
        clone_dir=Path("forked-jubilant/dwilding-snapshot0801"),
        create_branch=True,
        owner="dwilding",
        project="forked-jubilant",
        upstream_owner="some-org",
        upstream_url="https://github.com/some-org/forked-jubilant.git",
    )
    assert _cli.get_context(args) == expected_context
    assert fake_github.repo_calls == ["dwilding/forked-jubilant"]


# -b overrides the fork's upstream, but get_context still queries the fork.
# The query doubles as a fast-fail check that the repo exists, so it's worth keeping.
def test_context_fork_b_overrides_upstream(monkeypatch, fake_github):
    monkeypatch.setattr(_cli, "GITHUB_TOKEN", "fake-token")
    fake_github.repo = FORKED_REPO
    args = argparse.Namespace(
        base_branch="https://github.com/some-org/frogtab/tree/maintenance",
        upstream_owner=None,
        repo="dwilding/forked-jubilant",
        new_branch=None,
    )
    expected_context = _cli.Context(
        base_branch="maintenance",
        branch="snapshot0801",
        clone_url="https://github.com/dwilding/forked-jubilant.git",
        clone_dir=Path("frogtab/dwilding-snapshot0801"),
        create_branch=True,
        owner="dwilding",
        project="frogtab",
        upstream_owner="some-org",
        upstream_url="https://github.com/some-org/frogtab.git",
    )
    assert _cli.get_context(args) == expected_context
    assert fake_github.repo_calls == ["dwilding/forked-jubilant"]


def test_context_repo_from_login(monkeypatch, fake_github):
    monkeypatch.setattr(_cli, "GITHUB_TOKEN", "fake-token")
    fake_github.user = SimpleNamespace(login="dwilding")
    fake_github.repo = SimpleNamespace(fork=False)
    args = argparse.Namespace(
        base_branch=None,
        upstream_owner=None,
        repo="jubilant",
        new_branch=None,
    )
    expected_context = _cli.Context(
        base_branch=None,
        branch="snapshot0801",
        clone_url="https://github.com/dwilding/jubilant.git",
        clone_dir=Path("jubilant/dwilding-snapshot0801"),
        create_branch=True,
        owner="dwilding",
        project="jubilant",
        upstream_owner=None,
        upstream_url=None,
    )
    assert _cli.get_context(args) == expected_context
    assert fake_github.repo_calls == ["dwilding/jubilant"]
