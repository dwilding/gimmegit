from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
import argparse
import json
import logging
import re
import os
import shutil
import subprocess
import sys
import urllib.parse

import git
import github

from . import _args, _inspect, _remote, _status

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
class ParsedURL:
    branch: str | None
    owner: str
    project: str
    remote_url: str


@dataclass
class ParsedBranchSpec:
    branch: str
    owner: str | None
    project: str | None
    remote_url: str | None


class CloneError(RuntimeError):
    pass


def main() -> None:
    command_args = sys.argv[1:]
    cloning_args = ["--no-tags"]
    if "--" in command_args:
        sep_index = command_args.index("--")
        cloning_args.extend(command_args[sep_index + 1 :])
        command_args = command_args[:sep_index]
    args_with_usage = _args.parse_args(command_args)
    args = args_with_usage.args
    set_global_color(args.color)
    configure_logger()
    if args_with_usage.error:
        logger.error(f"{args_with_usage.error} Run 'gimmegit -h' for help.")
        sys.exit(2)
    if args_with_usage.usage == "primary":
        if not args.allow_outer_repo:
            working = _inspect.get_outer_repo()
            if working:
                status = _status.get_status(working)
                if not status:
                    logger.error("The working directory is inside a repo.")
                    sys.exit(1)
                logger.warning(
                    "Skipped cloning because the working directory is inside a gimmegit clone."
                )
                logger.info("The working directory is inside a gimmegit clone.")
                return
        primary_usage(args, cloning_args)
    elif args_with_usage.usage == "help":
        logger.info("help output TODO")
    elif args_with_usage.usage == "version":
        logger.info("version output TODO")
    elif args_with_usage.usage == "tool":
        set_global_ssh(args.ssh)
        parsed_url = parse_github_url(args.parse_url)
        if parsed_url:
            logger.info(json.dumps(asdict(parsed_url)))
        else:
            logger.error(f"'{args.parse_url}' is not a supported GitHub URL.")
            sys.exit(1)
    elif args_with_usage.usage == "bare":
        working = _inspect.get_outer_repo()
        if working:
            status = _status.get_status(working)
            if not status:
                logger.error(
                    "The working directory is inside a repo that is not supported by gimmegit."
                )
                sys.exit(1)
            logger.info("The working directory is inside a gimmegit clone.")
        else:
            logger.error("No repo specified. Run 'gimmegit -h' for help.")
            sys.exit(2)


def primary_usage(args: argparse.Namespace, cloning_args: list[str]) -> None:
    set_global_ssh(args.ssh)
    try:
        context = get_context(args)
    except ValueError as e:
        logger.error(e)
        sys.exit(1)
    if context.clone_dir.exists():
        outcome = "You already have a clone:"
        logger.info(f"{format_outcome(outcome)}\n{context.clone_dir.resolve()}")
        sys.exit(10)
    if (
        not args.allow_outer_repo
        and context.clone_dir.parent.exists()
        and _inspect.get_repo(context.clone_dir.parent)
    ):
        logger.error(f"'{context.clone_dir.parent.resolve()}' is a repo.")
        sys.exit(1)
    if not args.force_project_dir and not context.clone_dir.parent.exists():
        candidate = _inspect.get_repo_from_latest_dir(Path.cwd())
        if candidate and _status.get_status(candidate):
            logger.error(
                "The working directory has a gimmegit clone. Try running gimmegit in the parent directory."
            )
            sys.exit(1)
    try:
        clone(context, cloning_args)
    except CloneError as e:
        logger.error(e)
        sys.exit(1)
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
    clone_url = parsed.remote_url
    # Check that the repo exists and look for an upstream repo (if a token is set).
    upstream = get_github_upstream(owner, project)
    upstream_owner = None
    upstream_url = None
    parsed_base = None
    if args.base_branch:
        parsed_base = parse_github_branch_spec(args.base_branch)
    if parsed_base and parsed_base.owner:
        assert parsed_base.project  # For the type checker.
        if (parsed_base.owner, parsed_base.project) != (owner, project):
            project = parsed_base.project
            upstream_owner = parsed_base.owner
            upstream_url = parsed_base.remote_url
        if args.upstream_owner and args.upstream_owner != parsed_base.owner:
            logger.warning(
                f"Ignored upstream owner '{args.upstream_owner}' because the base branch includes an owner."
            )
    elif args.upstream_owner:
        if args.upstream_owner != owner:
            upstream_owner = args.upstream_owner
            upstream_url = make_github_clone_url(upstream_owner, project)
    elif upstream:
        project = upstream.project
        upstream_owner = upstream.owner
        upstream_url = upstream.url
    # Decide whether to create a branch.
    create_branch = False
    if not branch:
        create_branch = True
        if args.new_branch:
            branch = args.new_branch
        else:
            branch = make_snapshot_name()
    elif args.new_branch:
        logger.warning(f"Ignored '{args.new_branch}' because you specified an existing branch.")
    return Context(
        base_branch=parsed_base.branch if parsed_base else None,
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
    if repo.startswith(("https://github.com/", "github.com/")):
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
    pattern = r"(https://)?github\.com/([^/]+)/([^/]+)(/tree/(.+))?"
    # TODO: Disallow PR URLs.
    match = re.search(pattern, url)
    if match:
        branch = match.group(5)
        if branch:
            branch = urllib.parse.unquote(branch)
        return ParsedURL(
            branch=branch,
            owner=match.group(2),
            project=match.group(3),
            remote_url=make_github_clone_url(match.group(2), match.group(3)),
        )


def parse_github_branch_spec(branch_spec: str) -> ParsedBranchSpec | None:
    parsed = parse_github_url(branch_spec)
    if not parsed:
        return ParsedBranchSpec(
            branch=branch_spec,
            owner=None,
            project=None,
            remote_url=None,
        )
    if not parsed.branch:
        raise ValueError(f"'{branch_spec}' does not specify a branch.")
    return ParsedBranchSpec(
        branch=parsed.branch,
        owner=parsed.owner,
        project=parsed.project,
        remote_url=parsed.remote_url,
    )


def get_github_login() -> str:
    api = github.Github(GITHUB_TOKEN)
    user = api.get_user()
    return user.login


def get_github_upstream(owner: str, project: str) -> _remote.Remote | None:
    if not GITHUB_TOKEN:
        return None
    api = github.Github(GITHUB_TOKEN)
    try:
        repo = api.get_repo(f"{owner}/{project}")
    except github.UnknownObjectException:
        raise ValueError(
            f"Unable to find '{owner}/{project}' on GitHub. Do you have access to the repo?"
        )
    if repo.fork:
        parent = repo.parent
        return _remote.Remote(
            owner=parent.owner.login,
            project=parent.name,
            url=make_github_clone_url(parent.owner.login, parent.name),
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
    logger.info(f"Cloning {context.clone_url}")
    try:
        cloned = git.Repo.clone_from(
            context.clone_url, context.clone_dir, multi_options=cloning_args
        )
    except git.GitCommandError:
        if SSH:
            raise CloneError(
                "Unable to clone repo. Do you have access to the repo? Is SSH correctly configured?"
            )
        else:
            raise CloneError(
                "Unable to clone repo. Is the repo private? Try configuring Git to use SSH."
            )
    if not context.base_branch:
        context.base_branch = get_default_branch(cloned)
    if context.upstream_url:
        logger.info(f"Setting upstream to {context.upstream_url}")
        upstream = cloned.create_remote("upstream", context.upstream_url)
        try:
            upstream.fetch(no_tags=True)
        except git.CommandError:
            shutil.rmtree(context.clone_dir)
            if SSH:
                raise CloneError(
                    "Unable to fetch upstream repo. Do you have access to the repo? Is SSH correctly configured?"
                )
            else:
                raise CloneError(
                    "Unable to fetch upstream repo. Is the repo private? Try configuring Git to use SSH."
                )
        base_remote = "upstream"
        create_local_branch(cloned, upstream, context)
    else:
        base_remote = "origin"
        create_local_branch(cloned, None, context)
    with cloned.config_writer() as config:
        update_branch = "!" + " && ".join(
            [
                "branch=$(git config --get gimmegit.branch)",
                "base_remote=$(git config --get gimmegit.baseRemote)",
                "base_branch=$(git config --get gimmegit.baseBranch)",
                'echo \\"$ git checkout $branch\\"',
                "git checkout $branch",
                'echo \\"$ git fetch $base_remote $base_branch\\"',
                "git fetch $base_remote $base_branch",
                'echo \\"$ git merge $base_remote/$base_branch\\"',
                "git merge $base_remote/$base_branch",
            ]
        )  # Not cross-platform!
        config.set_value(
            "alias",
            "update-branch",
            update_branch,
        )
        config.set_value(
            "gimmegit",
            "baseBranch",
            context.base_branch,
        )
        config.set_value(
            "gimmegit",
            "baseRemote",
            base_remote,
        )
        config.set_value(
            "gimmegit",
            "branch",
            context.branch,
        )


def get_default_branch(cloned: git.Repo) -> str:
    for ref in cloned.remotes.origin.refs:
        if ref.name == "origin/HEAD":
            return ref.ref.name.removeprefix("origin/")
    raise RuntimeError("Unable to identify default branch.")


def create_local_branch(cloned: git.Repo, upstream: git.Remote | None, context: Context):
    origin = cloned.remotes.origin
    if upstream:
        base = upstream
        base_owner = context.upstream_owner
    else:
        base = origin
        base_owner = context.owner
    base_branch_full = f"{base_owner}:{context.base_branch}"
    if context.create_branch:
        # Create a local branch, starting from the base branch.
        logger.info(
            f"Checking out a new branch {format_branch(context.branch)} based on {format_branch(base_branch_full)}"
        )
        if context.base_branch not in base.refs:
            shutil.rmtree(context.clone_dir)
            raise CloneError(f"The base branch {format_branch(base_branch_full)} does not exist.")
        branch = cloned.create_head(context.branch, base.refs[context.base_branch])
        # Ensure that on first push, a remote branch is created and set as the tracking branch.
        # The remote branch will be created on origin (the default remote).
        with cloned.config_writer() as config:
            config.set_value(
                "push",
                "default",
                "current",
            )
            config.set_value(
                "push",
                "autoSetupRemote",
                "true",
            )
    else:
        # Create a local branch that tracks the existing branch on origin.
        branch_full = f"{context.owner}:{context.branch}"
        logger.info(
            f"Checking out {format_branch(branch_full)} with base {format_branch(base_branch_full)}"
        )
        if context.base_branch not in base.refs:
            shutil.rmtree(context.clone_dir)
            raise CloneError(f"The base branch {format_branch(base_branch_full)} does not exist.")
        if context.branch not in origin.refs:
            shutil.rmtree(context.clone_dir)
            raise CloneError(f"The branch {format_branch(branch_full)} does not exist.")
        branch = cloned.create_head(context.branch, origin.refs[context.branch])
        branch.set_tracking_branch(origin.refs[context.branch])
    branch.checkout()


def install_pre_commit(clone_dir: Path) -> None:
    if not (clone_dir / ".pre-commit-config.yaml").exists():
        return
    if not shutil.which("uvx"):
        return
    logger.info("Installing pre-commit using uvx")
    subprocess.run(
        ["uvx", "pre-commit", "install"],
        cwd=clone_dir,
        check=True,
    )


if __name__ == "__main__":
    main()
