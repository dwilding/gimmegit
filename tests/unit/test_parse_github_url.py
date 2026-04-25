import pytest

from gimmegit import _cli


@pytest.fixture(autouse=True)
def no_ssh(monkeypatch):
    monkeypatch.setattr("gimmegit._cli.SSH", False)


def test_url_branch():
    assert _cli.parse_github_url(
        "github.com/canonical/operator/tree/2.23-maintenance"
    ) == _cli.ParsedURL(
        branch="2.23-maintenance",
        owner="canonical",
        project="operator",
        remote_url="https://github.com/canonical/operator.git",
    )


def test_url_no_branch():
    assert _cli.parse_github_url("github.com/canonical/operator") == _cli.ParsedURL(
        branch=None,
        owner="canonical",
        project="operator",
        remote_url="https://github.com/canonical/operator.git",
    )


def test_url_invalid():
    assert _cli.parse_github_url("github.com/canonical") is None
