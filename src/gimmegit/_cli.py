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

COLOR = False
SSH = False

GITHUB_TOKEN = os.getenv("GIMMEGIT_GITHUB_TOKEN") or None


@dataclass
class Context:
    base_branch: str | None
    branch: str
    clone_url: str
    clone_dir: Path
    create_branch: bool
    owner: str
    project: str
    upstream_owner: str | None
    upstream_url: str | None


@dataclass
class Upstream:
    owner: str
    project: str
    remote_url: str


@dataclass
class ParsedURL:
    branch: str | None
    owner: str
    project: str


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create and clone fully-isolated development branches"
    )
    parser.add_argument(
        "--color",
        choices=["auto", "always", "never"],
        default="auto",
        help="Use color in the output",
    )
    parser.add_argument(
        "--ssh",
        choices=["auto", "always", "never"],
        default="auto",
        help="Use SSH for git remotes",
    )
    parser.add_argument(
        "--no-pre-commit",
        action="store_true",
        help="Don't try to install pre-commit after cloning",
    )
    parser.add_argument("-u", "--upstream-owner", help="Upstream owner in GitHub")
    parser.add_argument("-b", "--base-branch", help="Base branch of the new or existing branch")
    parser.add_argument("repo", help="Repo to clone from GitHub")
    parser.add_argument("new_branch", nargs="?", help="Name of the branch to create")
    command_args = sys.argv[1:]
    cloning_args = ["--no-tags"]
    if "--" in command_args:
        sep_index = command_args.index("--")
        cloning_args.extend(command_args[sep_index + 1 :])
        command_args = command_args[:sep_index]
    args = parser.parse_args(command_args)
    set_global_color(args.color)
    set_global_ssh(args.ssh)
    configure_logger()
    try:
        context = get_context(args)
    except ValueError as e:
        logger.error(e)
        sys.exit(1)
    if context.clone_dir.exists():
        outcome = "You already have a clone:"
        logger.info(f"{format_outcome(outcome)}\n{context.clone_dir.resolve()}")
        sys.exit(10)
    clone(context, cloning_args)
    if not args.no_pre_commit:
        install_pre_commit(context.clone_dir)
    outcome = "Cloned repo:"
    logger.info(f"{format_outcome(outcome)}\n{context.clone_dir.resolve()}")


def set_global_color(color_arg: str) -> None:
    global COLOR
    if color_arg == "auto":
        COLOR = os.isatty(sys.stdout.fileno()) and not bool(os.getenv("NO_COLOR"))
    elif color_arg == "always":
        COLOR = True


def format_branch(branch: str) -> str:
    if COLOR:
        return f"\033[36m{branch}\033[0m"
    else:
        return branch


def format_outcome(outcome: str) -> str:
    if COLOR:
        return f"\033[1m{outcome}\033[0m"
    else:
        return outcome


def set_global_ssh(ssh_arg: str) -> None:
    global SSH
    if ssh_arg == "auto":
        ssh_dir = Path.home() / ".ssh"
        SSH = any(ssh_dir.glob("id_*"))
    elif ssh_arg == "always":
        SSH = True


def configure_logger() -> None:
    info = logging.StreamHandler(sys.stdout)
    info.setFormatter(logging.Formatter("%(message)s"))
    warning = logging.StreamHandler(sys.stderr)
    error = logging.StreamHandler(sys.stderr)
    if COLOR:
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
    logger.info("Getting repo details")
    # Parse the 'repo' arg to get the owner, project, and branch.
    github_url = make_github_url(args.repo)
    parsed = parse_github_url(github_url)
    if not parsed:
        raise ValueError(f"'{github_url}' is not a supported GitHub URL.")
    owner = parsed.owner
    project = parsed.project
    branch = parsed.branch
    # Get clone URLs for origin and upstream.
    clone_url = make_github_clone_url(owner, project)
    upstream_owner = None
    upstream_url = None
    if args.upstream_owner:
        upstream_owner = args.upstream_owner
        upstream_url = make_github_clone_url(args.upstream_owner, project)
    else:
        upstream = get_github_upstream(owner, project)
        if upstream:
            upstream_owner = upstream.owner
            upstream_url = upstream.remote_url
            project = upstream.project
    # Decide whether to create a branch.
    create_branch = False
    if not branch:
        create_branch = True
        if args.new_branch:
            branch = args.new_branch
        else:
            branch = make_snapshot_name()
    elif args.new_branch:
        logger.warning(f"Ignoring '{args.new_branch}' because {github_url} specifies a branch.")
    return Context(
        base_branch=args.base_branch,
        branch=branch,
        clone_url=clone_url,
        clone_dir=make_clone_path(owner, project, branch),
        create_branch=create_branch,
        owner=owner,
        project=project,
        upstream_owner=upstream_owner,
        upstream_url=upstream_url,
    )


def make_github_url(repo: str) -> str:
    if repo.startswith("https://github.com/"):
        return repo
    if repo.count("/") == 1 and not repo.endswith("/"):
        return f"https://github.com/{repo}"
    if repo.endswith("/") or repo.endswith("\\"):
        project = repo[:-1]  # The user might have tab-completed a project dir.
    else:
        project = repo
    if "/" not in project:
        if not GITHUB_TOKEN:
            raise ValueError(
                "GIMMEGIT_GITHUB_TOKEN is not set. For the repo, use '<owner>/<project>' or a GitHub URL."
            )
        github_login = get_github_login()
        return f"https://github.com/{github_login}/{project}"
    raise ValueError(f"'{repo}' is not a supported repo.")


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


def get_github_upstream(owner: str, project: str) -> Upstream | None:
    if not GITHUB_TOKEN:
        return None
    api = github.Github(GITHUB_TOKEN)
    repo = api.get_repo(f"{owner}/{project}")
    if repo.fork:
        parent = repo.parent
        return Upstream(
            remote_url=make_github_clone_url(parent.owner.login, parent.name),
            owner=parent.owner.login,
            project=parent.name,
        )


def make_github_clone_url(owner: str, project: str) -> str:
    if SSH:
        return f"git@github.com:{owner}/{project}.git"
    else:
        return f"https://github.com/{owner}/{project}.git"


def make_snapshot_name() -> str:
    today = datetime.now()
    today_formatted = today.strftime("%m%d")
    return f"snapshot{today_formatted}"


def make_clone_path(owner: str, project: str, branch: str) -> Path:
    branch_slug = branch.replace("/", "-")
    return Path(f"{project}/{owner}-{branch_slug}")


def clone(context: Context, cloning_args: list[str]) -> None:
    # TODO: Handle branch errors
    logger.info(f"Cloning {context.clone_url}")
    cloned = git.Repo.clone_from(context.clone_url, context.clone_dir, multi_options=cloning_args)
    origin = cloned.remotes.origin
    if not context.base_branch:
        context.base_branch = get_default_branch(cloned)
    branch_full = f"{context.owner}:{context.branch}"
    if context.upstream_url:
        logger.info(f"Setting upstream to {context.upstream_url}")
        upstream = cloned.create_remote("upstream", context.upstream_url)
        upstream.fetch(no_tags=True)
        base_branch_full = f"{context.upstream_owner}:{context.base_branch}"
        base_remote = "upstream"
        if context.create_branch:
            # Create a local branch, starting from the base branch on upstream.
            logger.info(
                f"Checking out a new branch {format_branch(context.branch)} based on {format_branch(base_branch_full)}"
            )
            branch = cloned.create_head(context.branch, upstream.refs[context.base_branch])
        else:
            # Create a local branch that tracks the existing branch on origin.
            logger.info(
                f"Checking out {format_branch(branch_full)} with base {format_branch(base_branch_full)}"
            )
            branch = cloned.create_head(context.branch, origin.refs[context.branch])
            branch.set_tracking_branch(origin.refs[context.branch])
        branch.checkout()
    else:
        base_branch_full = f"{context.owner}:{context.base_branch}"
        base_remote = "origin"
        if context.create_branch:
            # Create a local branch, starting from the base branch.
            logger.info(
                f"Checking out a new branch {format_branch(context.branch)} based on {format_branch(base_branch_full)}"
            )
            branch = cloned.create_head(context.branch, origin.refs[context.base_branch])
        else:
            # Create a local branch that tracks the existing branch.
            logger.info(
                f"Checking out {format_branch(branch_full)} with base {format_branch(base_branch_full)}"
            )
            branch = cloned.create_head(context.branch, origin.refs[context.branch])
            branch.set_tracking_branch(origin.refs[context.branch])
        branch.checkout()
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
    if not (clone_dir / ".pre-commit-config.yaml").exists():
        return
    if not shutil.which("uvx"):
        return
    logger.info("Installing pre-commit using uvx")
    subprocess.run(["uvx", "pre-commit", "install"], cwd=clone_dir, check=True)


if __name__ == "__main__":
    main()
