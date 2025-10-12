from dataclasses import dataclass

import git


@dataclass
class Status:
    base_branch: str
    base_owner: str
    base_url: str
    branch: str
    owner: str
    project: str
    url: str


def get_status(working: git.Repo) -> Status | None:
    with working.config_reader() as config:
        if not config.has_section("gimmegit"):
            return None
        if not config.get_value("gimmegit", "baseBranch"):
            return None
        if not config.has_option("gimmegit", "baseRemote"):
            return None
        if not config.has_option("gimmegit", "branch"):
            return None
        # base_branch = config.get_value("gimmegit", "baseBranch")
        # base_remote = config.get_value("gimmegit", "baseRemote")
        # branch = config.get_value("gimmegit", "branch")
        return Status(
            base_branch="foo",
            base_owner="foo",
            base_url="foo",
            branch="foo",
            owner="foo",
            project="foo",
            url="foo",
        )
