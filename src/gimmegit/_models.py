from dataclasses import dataclass
import subprocess
import tempfile


@dataclass
class Remote:
    owner: str
    project: str
    url: str


def is_valid_branch_name(branch: str) -> bool:
    with tempfile.TemporaryDirectory() as empty_dir:
        command = ["git", "check-ref-format", "--branch", branch]
        result = subprocess.run(
            command,
            cwd=empty_dir,
            capture_output=True,
            text=True,
        )
        return result.returncode == 0


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
