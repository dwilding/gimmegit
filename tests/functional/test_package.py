import gimmegit


def test_parse():
    assert gimmegit.parse_url(
        "github.com/canonical/operator/tree/2.23-maintenance", ssh=False
    ) == gimmegit.ParsedURL(
        branch="2.23-maintenance",
        owner="canonical",
        project="operator",
        remote_url="https://github.com/canonical/operator.git",
    )
