import gimmegit


def test_parse_branch():
    assert gimmegit.parse_url(
        "github.com/canonical/operator/tree/2.23-maintenance", ssh=False
    ) == gimmegit.ParsedURL(
        branch="2.23-maintenance",
        owner="canonical",
        project="operator",
        remote_url="https://github.com/canonical/operator.git",
    )


def test_parse_no_branch():
    assert gimmegit.parse_url("github.com/canonical/operator", ssh=False) == gimmegit.ParsedURL(
        branch=None,
        owner="canonical",
        project="operator",
        remote_url="https://github.com/canonical/operator.git",
    )


def test_parse_invalid():
    assert gimmegit.parse_url("github.com/canonical") is None
