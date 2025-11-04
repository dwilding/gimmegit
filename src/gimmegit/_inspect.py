from pathlib import Path

import git


def get_outer_repo() -> git.Repo | None:
    try:
        return git.Repo(search_parent_directories=True)
    except git.InvalidGitRepositoryError:
        return None


def get_repo(dir: Path) -> git.Repo | None:
    try:
        return git.Repo(dir)
    except git.InvalidGitRepositoryError:
        return None


def get_repo_from_latest_dir(dir: Path) -> git.Repo | None:
    dirs = [d for d in dir.iterdir() if d.is_dir()]
    if not dirs:
        return
    latest_dir = max(dirs, key=lambda d: d.stat().st_mtime)
    return get_repo(latest_dir)
