from dataclasses import dataclass
import re
import urllib.parse

from . import _remote


@dataclass
class ParsedURL:
    branch: str | None
    owner: str
    project: str
    remote_url: str


def parse_url(url: str, *, ssh: bool | None = None) -> ParsedURL | None:
    """Parse a GitHub URL into owner, project, and branch.

    Also returns the corresponding Git remote URL.

    Args:
        url: URL to parse. For example,
            https://github.com/canonical/operator/tree/2.23-maintenance.
        ssh: Controls whether the Git remote uses SSH or HTTPS. If not specified, the Git remote
            uses SSH if `~/.ssh` contains an SSH key.

    Returns:
        A ParsedURL object, or None if the URL cannot be parsed.
    """
    pattern = r"(https://)?github\.com/([^/]+)/([^/]+)(/tree/(.+))?"
    # TODO: Disallow PR URLs.
    # TODO: Improve parsing. See https://github.com/dwilding/gimmegit/pull/120#discussion_r3176453217
    match = re.search(pattern, url)
    if match:
        branch = match.group(5)
        if branch:
            branch = urllib.parse.unquote(branch)
        if ssh is None:
            ssh = _remote.is_ssh_configured()
        return ParsedURL(
            branch=branch,
            owner=match.group(2),
            project=match.group(3),
            remote_url=_remote.make_remote_url(ssh, match.group(2), match.group(3)),
        )
