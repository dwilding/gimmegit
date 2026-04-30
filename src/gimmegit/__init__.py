from ._cli import parse_github_url, ParsedURL, set_global_ssh
from ._version import __version__

__all__ = [
    "__version__",
    "parse_url",
    "ParsedURL",
]


def parse_url(url: str, *, ssh: bool | None = None) -> ParsedURL | None:
    """Parse a GitHub URL into owner, project, and branch.

    This function also returns the corresponding Git remote URL.

    Args:
        ssh: Controls whether the Git remote uses SSH or HTTPS. If not specified, the Git remote
            uses SSH if ``~/.ssh`` contains an SSH key.
    """
    ssh_arg = "auto"
    if ssh is not None:
        ssh_arg = "always" if ssh else "never"
    set_global_ssh(ssh_arg)
    return parse_github_url(url)
