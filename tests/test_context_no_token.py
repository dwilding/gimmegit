from pathlib import Path
import argparse
import logging

import pytest

from gimmegit import _cli


@pytest.fixture
def snapshot_name(monkeypatch):
    monkeypatch.setattr("gimmegit._cli.make_snapshot_name", lambda: "snapshot0801")


def test_project():
    args = argparse.Namespace(
        ssh="never", upstream_owner=None, base_branch=None, repo="gimmegit", new_branch=None
    )
    with pytest.raises(ValueError):
        _cli.get_context(args)


def test_owner_project(snapshot_name):
    args = argparse.Namespace(
        ssh="never",
        upstream_owner=None,
        base_branch=None,
        repo="dwilding/gimmegit",
        new_branch=None,
    )
    expected_context = _cli.Context(
        base_branch=None,
        branch="snapshot0801",
        clone_url="https://github.com/dwilding/gimmegit.git",
        clone_dir=Path("gimmegit/dwilding-snapshot0801"),
        create_branch=True,
        owner="dwilding",
        project="gimmegit",
        upstream_url=None,
    )
    assert _cli.get_context(args) == expected_context


def test_owner_project_branch():
    args = argparse.Namespace(
        ssh="never",
        upstream_owner=None,
        base_branch=None,
        repo="dwilding/gimmegit",
        new_branch="fix-something",
    )
    expected_context = _cli.Context(
        base_branch=None,
        branch="fix-something",
        clone_url="https://github.com/dwilding/gimmegit.git",
        clone_dir=Path("gimmegit/dwilding-fix-something"),
        create_branch=True,
        owner="dwilding",
        project="gimmegit",
        upstream_url=None,
    )
    assert _cli.get_context(args) == expected_context


def test_repo_url(snapshot_name):
    args = argparse.Namespace(
        ssh="never",
        upstream_owner=None,
        base_branch=None,
        repo="https://github.com/dwilding/gimmegit",
        new_branch=None,
    )
    expected_context = _cli.Context(
        base_branch=None,
        branch="snapshot0801",
        clone_url="https://github.com/dwilding/gimmegit.git",
        clone_dir=Path("gimmegit/dwilding-snapshot0801"),
        create_branch=True,
        owner="dwilding",
        project="gimmegit",
        upstream_url=None,
    )
    assert _cli.get_context(args) == expected_context


def test_repo_url_branch():
    args = argparse.Namespace(
        ssh="never",
        upstream_owner=None,
        base_branch=None,
        repo="https://github.com/dwilding/gimmegit",
        new_branch="fix-something",
    )
    expected_context = _cli.Context(
        base_branch=None,
        branch="fix-something",
        clone_url="https://github.com/dwilding/gimmegit.git",
        clone_dir=Path("gimmegit/dwilding-fix-something"),
        create_branch=True,
        owner="dwilding",
        project="gimmegit",
        upstream_url=None,
    )
    assert _cli.get_context(args) == expected_context


def test_branch_url(snapshot_name):
    args = argparse.Namespace(
        ssh="never",
        upstream_owner=None,
        base_branch=None,
        repo="https://github.com/dwilding/gimmegit/tree/next-release",
        new_branch=None,
    )
    expected_context = _cli.Context(
        base_branch=None,
        branch="next-release",
        clone_url="https://github.com/dwilding/gimmegit.git",
        clone_dir=Path("gimmegit/dwilding-next-release"),
        create_branch=False,
        owner="dwilding",
        project="gimmegit",
        upstream_url=None,
    )
    assert _cli.get_context(args) == expected_context


def test_branch_url_branch(caplog):
    args = argparse.Namespace(
        ssh="never",
        upstream_owner=None,
        base_branch=None,
        repo="https://github.com/dwilding/gimmegit/tree/next-release",
        new_branch="fix-something",  # This should be ignored.
    )
    expected_context = _cli.Context(
        base_branch=None,
        branch="next-release",
        clone_url="https://github.com/dwilding/gimmegit.git",
        clone_dir=Path("gimmegit/dwilding-next-release"),
        create_branch=False,
        owner="dwilding",
        project="gimmegit",
        upstream_url=None,
    )
    with caplog.at_level(logging.WARNING):
        assert _cli.get_context(args) == expected_context
    assert len(caplog.records) == 1
