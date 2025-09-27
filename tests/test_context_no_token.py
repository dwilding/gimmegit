from pathlib import Path
import argparse
import logging

import pytest

from gimmegit import _cli


@pytest.fixture(autouse=True)
def no_ssh(monkeypatch):
    monkeypatch.setattr("gimmegit._cli.SSH", False)


@pytest.fixture(autouse=True)
def snapshot_name(monkeypatch):
    monkeypatch.setattr("gimmegit._cli.make_snapshot_name", lambda: "snapshot0801")


# TODO: Should we support these repos?
# git@github.com:dwilding/frogtab.git
# github.com/dwilding/frogtab.git
# https://github.com/dwilding/frogtab.git


@pytest.mark.parametrize(
    "repo, owner, project",
    [
        ("dwilding/frogtab", "dwilding", "frogtab"),
        ("github.com/dwilding/frogtab", "dwilding", "frogtab"),
        ("https://github.com/dwilding/frogtab", "dwilding", "frogtab"),
    ],
)
def test_repo(repo: str, project: str, owner: str):
    args = argparse.Namespace(
        base_branch=None,
        upstream_owner=None,
        repo=repo,
        new_branch=None,
    )
    expected_context = _cli.Context(
        base_branch=None,
        branch="snapshot0801",
        clone_url=f"https://github.com/{owner}/{project}.git",
        clone_dir=Path(f"{project}/{owner}-snapshot0801"),
        create_branch=True,
        owner=owner,
        project=project,
        upstream_owner=None,
        upstream_url=None,
    )
    assert _cli.get_context(args) == expected_context


def test_no_owner():
    args = argparse.Namespace(
        base_branch=None, upstream_owner=None, repo="frogtab", new_branch=None
    )
    with pytest.raises(ValueError) as exc_info:
        _cli.get_context(args)
    assert str(exc_info.value).startswith("GIMMEGIT_GITHUB_TOKEN is not set.")


@pytest.mark.parametrize(
    "repo",
    [
        "dwilding/frogtab/",
        "dwilding/frogtab/foo",
        "dwilding/frogtab/tree/foo",
    ],
)
def test_repo_invalid(repo: str):
    args = argparse.Namespace(
        base_branch=None,
        upstream_owner=None,
        repo=repo,
        new_branch=None,
    )
    with pytest.raises(ValueError) as exc_info:
        _cli.get_context(args)
    assert str(exc_info.value) == f"'{repo}' is not a supported repo."


# TODO: Why do these URLs pass?
# github.com/dwilding/frogtab/foo
# https://github.com/dwilding/frogtab/foo


@pytest.mark.parametrize(
    "repo",
    [
        "github.com/dwilding",
        "https://github.com/dwilding",
    ],
)
def test_repo_invalid_github(repo: str):
    args = argparse.Namespace(
        base_branch=None,
        upstream_owner=None,
        repo=repo,
        new_branch=None,
    )
    with pytest.raises(ValueError) as exc_info:
        _cli.get_context(args)
    url = repo if repo.startswith("https://") else f"https://{repo}"
    assert str(exc_info.value) == f"'{url}' is not a supported GitHub URL."


@pytest.mark.parametrize(
    "branch, in_slug",
    [
        ("fix-something", "fix-something"),
        ("releases/next-release", "releases-next-release"),
    ],
)
def test_new_branch(branch: str, in_slug: str):
    args = argparse.Namespace(
        base_branch=None,
        upstream_owner=None,
        repo="dwilding/frogtab",
        new_branch=branch,
    )
    expected_context = _cli.Context(
        base_branch=None,
        branch=branch,
        clone_url="https://github.com/dwilding/frogtab.git",
        clone_dir=Path(f"frogtab/dwilding-{in_slug}"),
        create_branch=True,
        owner="dwilding",
        project="frogtab",
        upstream_owner=None,
        upstream_url=None,
    )
    assert _cli.get_context(args) == expected_context


@pytest.mark.parametrize(
    "repo, branch, in_slug",
    [
        ("https://github.com/dwilding/frogtab/tree/next-release", "next-release", "next-release"),
        ("github.com/dwilding/frogtab/tree/next-release", "next-release", "next-release"),
        (
            "github.com/dwilding/frogtab/tree/releases/next-release",
            "releases/next-release",
            "releases-next-release",
        ),
        (
            "https://github.com/dwilding/frogtab/tree/release%2Bnext",
            "release+next",
            "release+next",
        ),
    ],
)
def test_repo_branch(repo: str, branch: str, in_slug: str):
    args = argparse.Namespace(
        base_branch=None,
        upstream_owner=None,
        repo=repo,
        new_branch=None,
    )
    expected_context = _cli.Context(
        base_branch=None,
        branch=branch,
        clone_url="https://github.com/dwilding/frogtab.git",
        clone_dir=Path(f"frogtab/dwilding-{in_slug}"),
        create_branch=False,
        owner="dwilding",
        project="frogtab",
        upstream_owner=None,
        upstream_url=None,
    )
    assert _cli.get_context(args) == expected_context


def test_repo_branch_new_branch(caplog):
    args = argparse.Namespace(
        base_branch=None,
        upstream_owner=None,
        repo="https://github.com/dwilding/frogtab/tree/next-release",
        new_branch="fix-something",
    )
    expected_context = _cli.Context(
        base_branch=None,
        branch="next-release",
        clone_url="https://github.com/dwilding/frogtab.git",
        clone_dir=Path("frogtab/dwilding-next-release"),
        create_branch=False,
        owner="dwilding",
        project="frogtab",
        upstream_owner=None,
        upstream_url=None,
    )
    with caplog.at_level(logging.WARNING):
        assert _cli.get_context(args) == expected_context
    assert len(caplog.records) == 1
    assert caplog.records[0].msg.startswith("Ignoring 'fix-something'")
