from pathlib import Path
import argparse
import logging

import pytest

from gimmegit import _cli

import helpers_unit as helpers


@pytest.fixture(autouse=True)
def no_ssh(monkeypatch):
    monkeypatch.setattr("gimmegit._cli.SSH", False)


@pytest.fixture(autouse=True)
def snapshot_name(monkeypatch):
    monkeypatch.setattr("gimmegit._cli.make_snapshot_name", lambda: "snapshot0801")


# TODO: Make sure these repos either pass or fail.
# git@github.com:dwilding/frogtab.git
# github.com/dwilding/frogtab.git
# https://github.com/dwilding/frogtab.git


# TODO: Make sure these repos fail.
# github.com/dwilding/frogtab/foo
# https://github.com/dwilding/frogtab/foo


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
        base_branch=None,
        upstream_owner=None,
        repo="frogtab",
        new_branch=None,
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
        (
            "github.com/dwilding/frogtab/tree/next-release",
            "next-release",
            "next-release",
        ),
        (
            "https://github.com/dwilding/frogtab/tree/next-release",
            "next-release",
            "next-release",
        ),
        (
            "https://github.com/dwilding/frogtab/tree/releases/next-release",
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
    assert (
        caplog.records[0].msg
        == "Ignoring 'fix-something' because you specified an existing branch."
    )


@pytest.mark.parametrize(
    "base_in, base_out",
    [
        (None, None),
        ("maintenance", "maintenance"),
        ("github.com/some-org/frogtab/tree/maintenance", "maintenance"),
        ("https://github.com/some-org/frogtab/tree/maintenance", "maintenance"),
    ],
)
def test_upstream(base_in: str | None, base_out: str | None):
    args = argparse.Namespace(
        base_branch=base_in,
        upstream_owner="some-org",
        repo="dwilding/frogtab",
        new_branch=None,
    )
    expected_context = _cli.Context(
        base_branch=base_out,
        branch="snapshot0801",
        clone_url="https://github.com/dwilding/frogtab.git",
        clone_dir=Path("frogtab/dwilding-snapshot0801"),
        create_branch=True,
        owner="dwilding",
        project="frogtab",
        upstream_owner="some-org",
        upstream_url="https://github.com/some-org/frogtab.git",
    )
    assert _cli.get_context(args) == expected_context


@pytest.mark.xfail(**helpers.fail_in_dev)
@pytest.mark.parametrize(
    "base_in, base_out",
    [
        (None, None),
        ("maintenance", "maintenance"),
        ("github.com/dwilding/frogtab/tree/maintenance", "maintenance"),
        ("https://github.com/dwilding/frogtab/tree/maintenance", "maintenance"),
    ],
)
def test_upstream_same_owner(base_in: str | None, base_out: str | None):
    args = argparse.Namespace(
        base_branch=base_in,
        upstream_owner="dwilding",
        repo="dwilding/frogtab",
        new_branch=None,
    )
    expected_context = _cli.Context(
        base_branch=base_out,
        branch="snapshot0801",
        clone_url="https://github.com/dwilding/frogtab.git",
        clone_dir=Path("frogtab/dwilding-snapshot0801"),
        create_branch=True,
        owner="dwilding",
        project="frogtab",
        upstream_owner=None,
        upstream_url=None,
    )
    assert _cli.get_context(args) == expected_context


def test_base_sets_project():
    args = argparse.Namespace(
        base_branch="https://github.com/some-org/frogtab/tree/maintenance",
        upstream_owner=None,
        repo="dwilding/frogtab-fork",
        new_branch=None,
    )
    expected_context = _cli.Context(
        base_branch="maintenance",
        branch="snapshot0801",
        clone_url="https://github.com/dwilding/frogtab-fork.git",
        clone_dir=Path("frogtab/dwilding-snapshot0801"),
        create_branch=True,
        owner="dwilding",
        project="frogtab",
        upstream_owner="some-org",
        upstream_url="https://github.com/some-org/frogtab.git",
    )
    assert _cli.get_context(args) == expected_context


def test_base_sets_upstream_owner(caplog):
    args = argparse.Namespace(
        base_branch="https://github.com/some-org/frogtab/tree/maintenance",
        upstream_owner="different-owner",
        repo="dwilding/frogtab",
        new_branch=None,
    )
    expected_context = _cli.Context(
        base_branch="maintenance",
        branch="snapshot0801",
        clone_url="https://github.com/dwilding/frogtab.git",
        clone_dir=Path("frogtab/dwilding-snapshot0801"),
        create_branch=True,
        owner="dwilding",
        project="frogtab",
        upstream_owner="some-org",
        upstream_url="https://github.com/some-org/frogtab.git",
    )
    with caplog.at_level(logging.WARNING):
        assert _cli.get_context(args) == expected_context
    assert len(caplog.records) == 1
    assert (
        caplog.records[0].msg
        == "Ignoring upstream owner 'different-owner' because the base branch includes an owner."
    )


def test_base_url_no_branch():
    args = argparse.Namespace(
        base_branch="https://github.com/dwilding/frogtab",
        upstream_owner=None,
        repo="dwilding/frogtab",
        new_branch=None,
    )
    with pytest.raises(ValueError) as exc_info:
        _cli.get_context(args)
    assert (
        str(exc_info.value) == "'https://github.com/dwilding/frogtab' does not specify a branch."
    )
