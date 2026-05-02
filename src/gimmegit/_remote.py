from dataclasses import dataclass
from pathlib import Path


@dataclass
class Remote:
    owner: str
    project: str
    url: str


def is_ssh_configured() -> bool:
    ssh_dir = Path.home() / ".ssh"
    return any(ssh_dir.glob("id_*"))


def make_remote_url(ssh: bool, owner: str, project: str) -> str:
    if ssh:
        return f"git@github.com:{owner}/{project}.git"
    else:
        return f"https://github.com/{owner}/{project}.git"


def remote_from_url(url: str) -> Remote:
    if url.startswith("git@github.com:") and url.endswith(".git"):
        owner_project = url.removeprefix("git@github.com:").removesuffix(".git")
    elif url.startswith("https://github.com/") and url.endswith(".git"):
        owner_project = url.removeprefix("https://github.com/").removesuffix(".git")
    else:
        raise ValueError(f"'{url}' is not a supported remote URL.")
    owner, project = owner_project.split("/")
    return Remote(
        owner=owner,
        project=project,
        url=url,
    )
