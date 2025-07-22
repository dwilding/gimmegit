from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import argparse
import logging
import re
import os
import shutil
import subprocess
import sys

import git
import github

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

GITHUB_TOKEN = os.getenv("GIMMEGIT_GITHUB_TOKEN") or None
NO_COLOR = bool(os.getenv("NO_COLOR"))
NO_PRE_COMMIT = bool(os.getenv("GIMMEGIT_NO_PRE_COMMIT"))
NO_SSH = bool(os.getenv("GIMMEGIT_NO_SSH"))


@dataclass
class Context:
    base_branch: str | None
    branch: str
    clone_url: str
    clone_dir: Path
    create_branch: bool
    owner: str
    project: str
    source_url: str | None


@dataclass
class Source:
    remote_url: str
    project: str


@dataclass
class ParsedURL:
    branch: str | None
    owner: str
    project: str


def main() -> None:
    parser = argparse.ArgumentParser(description="todo")
    parser.add_argument(
        "--color", choices=["auto", "always", "never"], default="auto", help="todo"
    )
    parser.add_argument("-s", "--source-owner", help="todo")
    parser.add_argument("-b", "--base-branch", help="todo")
    parser.add_argument("repo", help="todo")
    parser.add_argument("new_branch", nargs="?", help="todo")
    command_args = sys.argv[1:]
    cloning_args = ["--no-tags"]
    if "--" in command_args:
        sep_index = command_args.index("--")
        cloning_args.extend(command_args[sep_index + 1 :])
        command_args = command_args[:sep_index]
    args = parser.parse_args(command_args)
    configure_logger(use_color(args.color))
    try:
        context = get_context(args)
    except ValueError as e:
        logger.error(e)
        sys.exit(1)
    if context.clone_dir.exists():
        logger.info(f"You already have a clone:\n{context.clone_dir.resolve()}")
        sys.exit(10)
    clone(context, cloning_args)
    install_pre_commit(context.clone_dir)
    logger.info(f"Cloned repo:\n{context.clone_dir.resolve()}")


def use_color(color_arg: str) -> bool:
    if color_arg == "never":
        return False
    if color_arg == "always":
        return True
    return os.isatty(sys.stdout.fileno()) and not NO_COLOR


def configure_logger(color: bool) -> None:
    info = logging.StreamHandler(sys.stdout)
    info.setFormatter(logging.Formatter("%(message)s"))
    warning = logging.StreamHandler(sys.stderr)
    error = logging.StreamHandler(sys.stderr)
    if color:
        warning.setFormatter(logging.Formatter("\033[33mWarning:\033[0m %(message)s"))
        error.setFormatter(logging.Formatter("\033[1;31mError:\033[0m %(message)s"))
    else:
        warning.setFormatter(logging.Formatter("Warning: %(message)s"))
        error.setFormatter(logging.Formatter("Error: %(message)s"))
    info.addFilter(lambda _: _.levelno == logging.INFO)
    warning.addFilter(lambda _: _.levelno == logging.WARNING)
    error.addFilter(lambda _: _.levelno == logging.ERROR)
    logger.addHandler(info)
    logger.addHandler(warning)
    logger.addHandler(error)


def get_context(args: argparse.Namespace) -> Context:
    logger.info("Getting repo details...")
    # Parse the 'repo' arg to get the owner, project, and branch.
    if args.repo.startswith("https://"):
        github_url = args.repo
    elif args.repo.count("/") == 1:
        github_url = f"https://github.com/{args.repo}"
    elif args.repo.count("/") == 0:
        if not GITHUB_TOKEN:
            raise ValueError(
                "GIMMEGIT_GITHUB_TOKEN is not set. Use a GitHub URL instead of a repo name."
            )
        github_login = get_github_login()
        github_url = f"https://github.com/{github_login}/{args.repo}"
    else:
        raise ValueError(f"'{args.repo}' is not a supported repo name.")
    parsed = parse_github_url(github_url)
    if not parsed:
        raise ValueError(f"'{github_url}' is not a supported GitHub URL.")
    owner = parsed.owner
    project = parsed.project
    branch = parsed.branch
    # Get clone URLs for origin and source.
    clone_url = make_github_clone_url(owner, project)
    source_url = None
    if args.source_owner:
        source_url = make_github_clone_url(args.source_owner, project)
    else:
        source = get_github_source(owner, project)
        if source:
            source_url = source.remote_url
            project = source.project
    # Decide whether to create a branch.
    create_branch = False
    if not branch:
        create_branch = True
        if args.new_branch:
            branch = args.new_branch
        else:
            branch = make_snapshot_name()
    elif args.new_branch:
        logger.warning(f"Ignoring '{args.new_branch}' because '{github_url}' specifies a branch.")
    return Context(
        base_branch=args.base_branch,
        branch=branch,
        clone_url=clone_url,
        clone_dir=make_clone_path(owner, project, branch),
        create_branch=create_branch,
        owner=owner,
        project=project,
        source_url=source_url,
    )


def parse_github_url(url: str) -> ParsedURL | None:
    pattern = r"https://github\.com/([^/]+)/([^/]+)(/tree/(.+))?"
    # TODO: Disallow PR URLs.
    match = re.search(pattern, url)
    if match:
        return ParsedURL(
            owner=match.group(1),
            project=match.group(2),
            branch=match.group(4),
        )


def get_github_login() -> str:
    api = github.Github(GITHUB_TOKEN)
    user = api.get_user()
    return user.login


def get_github_source(owner: str, project: str) -> Source | None:
    if not GITHUB_TOKEN:
        return None
    api = github.Github(GITHUB_TOKEN)
    repo = api.get_repo(f"{owner}/{project}")
    if repo.fork:
        parent = repo.parent
        return Source(
            remote_url=make_github_clone_url(parent.owner.login, parent.name),
            project=parent.name,
        )


def make_github_clone_url(owner: str, project: str) -> str:
    if use_ssh():
        return f"git@github.com:{owner}/{project}.git"
    else:
        return f"https://github.com/{owner}/{project}.git"


def use_ssh() -> bool:
    if NO_SSH:
        return False
    ssh_dir = Path.home() / ".ssh"
    return any(ssh_dir.glob("id_*"))


def make_snapshot_name() -> str:
    today = datetime.now()
    today_formatted = today.strftime("%m%d")
    return f"snapshot{today_formatted}"


def make_clone_path(owner: str, project: str, branch: str) -> Path:
    branch_short = branch.split("/")[-1]
    return Path(f"{project}/{owner}-{branch_short}")


def clone(context: Context, cloning_args: list[str]) -> None:
    logger.info(f"Cloning '{context.clone_url}'...")
    cloned = git.Repo.clone_from(context.clone_url, context.clone_dir, multi_options=cloning_args)
    origin = cloned.remotes.origin
    if not context.base_branch:
        context.base_branch = get_default_branch(cloned)
    if context.source_url:
        logger.info(f"Setting source to '{context.source_url}'...")
        source = cloned.create_remote("source", context.source_url)
        source.fetch(no_tags=True)
        if context.create_branch:
            # Create a local branch, starting from the base branch on source.
            branch = cloned.create_head(context.branch, source.refs[context.base_branch])
        else:
            # Create a local branch that tracks the existing branch on origin.
            branch = cloned.create_head(context.branch, origin.refs[context.branch])
            branch.set_tracking_branch(origin.refs[context.branch])
        branch.checkout()
        base_remote = "source"
    else:
        if context.create_branch:
            # Create a local branch, starting from the base branch.
            branch = cloned.create_head(context.branch, origin.refs[context.base_branch])
        else:
            # Create a local branch that tracks the existing branch.
            branch = cloned.create_head(context.branch, origin.refs[context.branch])
            branch.set_tracking_branch(origin.refs[context.branch])
        branch.checkout()
        base_remote = "origin"
    with cloned.config_writer() as config:
        update_branch = "!" + " && ".join(
            [
                f'echo "$ git checkout {branch}"',
                f'git checkout "{branch}"',
                f'echo "$ git fetch {base_remote} {context.base_branch}"',
                f'git fetch "{base_remote}" "{context.base_branch}"',
                f'echo "$ git merge {base_remote}/{context.base_branch}"',
                f'git merge "{base_remote}/{context.base_branch}"',
            ]
        )  # Not cross-platform!
        config.set_value(
            "alias",
            "update-branch",
            update_branch,
        )


def get_default_branch(cloned: git.Repo) -> str:
    for ref in cloned.remotes.origin.refs:
        if ref.name == "origin/HEAD":
            return ref.ref.name.removeprefix("origin/")
    raise RuntimeError("Unable to identify default branch.")


def install_pre_commit(clone_dir: Path) -> None:
    if NO_PRE_COMMIT:
        return
    if not (clone_dir / ".pre-commit-config.yaml").exists():
        return
    if not shutil.which("uvx"):
        return
    logger.info("Installing pre-commit using uvx...")
    subprocess.run(["uvx", "pre-commit", "install"], cwd=clone_dir, check=True)


if __name__ == "__main__":
    main()
