from dataclasses import dataclass


@dataclass
class Remote:
    owner: str
    project: str
    url: str


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
