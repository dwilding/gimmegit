from dataclasses import dataclass
import urllib.parse

import git

from ._remote import remote_from_url


@dataclass
class Status:
    base_branch: str
    base_owner: str
    base_url: str
    branch: str
    has_remote: bool
    owner: str
    project: str
    url: str


def get_status(working: git.Repo) -> Status | None:
    with working.config_reader() as config:
        if (
            not config.has_section("gimmegit")
            or not config.has_option("gimmegit", "baseBranch")
            or not config.has_option("gimmegit", "baseRemote")
            or not config.has_option("gimmegit", "branch")
        ):
            return None
        base_branch = str(config.get_value("gimmegit", "baseBranch"))
        base_remote = str(config.get_value("gimmegit", "baseRemote"))
        branch = str(config.get_value("gimmegit", "branch"))
        has_remote = config.has_section(f'branch "{branch}"') and config.has_option(
            f'branch "{branch}"', "remote"
        )
    origin = remote_from_url(working.remotes.origin.url)
    if base_remote == "upstream":
        base = remote_from_url(working.remotes.upstream.url)
    elif base_remote == "origin":
        base = origin
    else:
        raise RuntimeError(f"Unexpected base remote '{base_remote}'")
    return Status(
        base_branch=base_branch,
        base_owner=base.owner,
        base_url=make_branch_url(base.owner, base.project, base_branch),
        branch=branch,
        has_remote=has_remote,
        owner=origin.owner,
        project=base.project,
        url=make_branch_url(origin.owner, origin.project, branch),
    )


def make_branch_url(owner: str, project: str, branch: str) -> str:
    branch = urllib.parse.quote(branch)
    return f"https://github.com/{owner}/{project}/tree/{branch}"
