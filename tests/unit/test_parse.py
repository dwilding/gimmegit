import pytest

from gimmegit import _parse


@pytest.fixture(autouse=True)
def no_ssh(monkeypatch):
    monkeypatch.setattr("gimmegit._remote.is_ssh_configured", lambda: False)


def test_parse_branch(monkeypatch):
    assert _parse.parse_url(
        "github.com/canonical/operator/tree/2.23-maintenance"
    ) == _parse.ParsedURL(
        branch="2.23-maintenance",
        owner="canonical",
        project="operator",
        remote_url="https://github.com/canonical/operator.git",
    )
    assert _parse.parse_url(
        "github.com/canonical/operator/tree/2.23-maintenance", ssh=False
    ) == _parse.ParsedURL(
        branch="2.23-maintenance",
        owner="canonical",
        project="operator",
        remote_url="https://github.com/canonical/operator.git",
    )
    assert _parse.parse_url(
        "github.com/canonical/operator/tree/2.23-maintenance", ssh=True
    ) == _parse.ParsedURL(
        branch="2.23-maintenance",
        owner="canonical",
        project="operator",
        remote_url="git@github.com:canonical/operator.git",
    )
    monkeypatch.setattr("gimmegit._remote.is_ssh_configured", lambda: True)
    assert _parse.parse_url(
        "github.com/canonical/operator/tree/2.23-maintenance"
    ) == _parse.ParsedURL(
        branch="2.23-maintenance",
        owner="canonical",
        project="operator",
        remote_url="git@github.com:canonical/operator.git",
    )


def test_parse_no_branch():
    assert _parse.parse_url("github.com/canonical/operator") == _parse.ParsedURL(
        branch=None,
        owner="canonical",
        project="operator",
        remote_url="https://github.com/canonical/operator.git",
    )


def test_parse_invalid():
    assert _parse.parse_url("github.com/canonical") is None
