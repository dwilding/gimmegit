from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Never
import argparse
import json
import logging
import re
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
import webbrowser

import git
import github

from . import _args, _help, _inspect, _remote, _status, _version

DATA_LEVEL = 19
logger = logging.getLogger(__name__)
logger.setLevel(DATA_LEVEL)

INFO_TO = "stdout"
COLOR = {
    "stdout": False,
    "stderr": False,
}

SSH = False

GITHUB_TOKEN = os.getenv("GIMMEGIT_GITHUB_TOKEN") or None


@dataclass
class Column:
    last: bool
    title: str
    url: str | None
    value: str


@dataclass
class FormattedStr:
    formatted: str
    plain: str


@dataclass
class BranchName:
    branch: str


@dataclass
class ParsedBranchSpec(BranchName):
    owner: str
    project: str
    remote_url: str


@dataclass
class ParsedURL:
    branch: str | None
    owner: str
    project: str
    remote_url: str


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
    configure_logger_error()
    configure_logger_warning()
    if args_with_usage.error:
        logger.error(f"{args_with_usage.error} Run 'gimmegit -h' for help.")
        sys.exit(2)
    if hasattr(args, "return_dir"):
        set_global_info(args.return_dir)
    configure_logger_info()
    configure_logger_data()
    if hasattr(args, "ssh"):
        set_global_ssh(args.ssh)
    if args_with_usage.usage == "primary":
        if not args.allow_outer_repo:
            working = _inspect.get_outer_repo()
            if working:
                status = _status.get_status(working)
                if not status:
                    exit_with_error("The working directory is inside a repo.")
                status_usage(status)
                logger.warning(
                    "Skipped cloning because the working directory is inside a gimmegit clone."
                )
                return
        primary_usage(args, cloning_args)
    elif args_with_usage.usage == "compare":
        working = _inspect.get_outer_repo()
        status = _status.get_status(working) if working else None
        if not status:
            exit_with_error("The working directory is not inside a gimmegit clone.")
        compare_usage(status)
    elif args_with_usage.usage == "help":
        logger.info(_help.help)
    elif args_with_usage.usage == "version":
        logger.log(DATA_LEVEL, f"gimmegit {_version.__version__}")
    elif args_with_usage.usage == "tool":
        parsed_url = parse_github_url(args.parse_url)
        if not parsed_url:
            exit_with_error(f"'{args.parse_url}' is not a supported GitHub URL.")
        logger.log(DATA_LEVEL, json.dumps(asdict(parsed_url)))
    elif args_with_usage.usage == "bare":
        working = _inspect.get_outer_repo()
        if not working:
            exit_with_error("No repo specified. Run 'gimmegit -h' for help.", 2)
        status = _status.get_status(working)
        if not status:
            exit_with_error("The working directory is not inside a gimmegit clone.")
        status_usage(status)


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
    origin = cloned.remotes.origin
    if context.create_branch and context.branch in origin.refs:
        raise CloneError(f"The branch {f_blue(context.branch)} already exists.")
    if not context.base_branch:
        context.base_branch = get_default_branch(cloned)
    if context.upstream_url:
        logger.info(f"Setting upstream to {context.upstream_url}")
        upstream = cloned.create_remote("upstream", context.upstream_url)
        try:
            upstream.fetch(no_tags=True)
        except git.CommandError:
            if SSH:
                raise CloneError(
                    "Unable to fetch upstream repo. Do you have access to the repo? Is SSH correctly configured?"
                )
            else:
                raise CloneError(
                    "Unable to fetch upstream repo. Is the repo private? Try configuring Git to use SSH."
                )
        create_local_branch(cloned, upstream, context)
    else:
        create_local_branch(cloned, None, context)


def compare_usage(status: _status.Status) -> None:
    if not status.has_remote:
        exit_with_error("The review branch has not been created. Push to GitHub first.")
    if not os.isatty(sys.stdout.fileno()):
        logger.log(DATA_LEVEL, status.compare_url)
        return
    # Try xdg-open first, to suppress a Linux/snap/Firefox error message:
    # Gtk-Message: ... Not loading module "atk-bridge"...
    if shutil.which("xdg-open"):
        result = subprocess.run(
            ["xdg-open", status.compare_url],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if result.returncode:
            logger.log(DATA_LEVEL, status.compare_url)
        return
    try:
        opened = webbrowser.open(status.compare_url, new=2)
    except webbrowser.Error:
        logger.log(DATA_LEVEL, status.compare_url)
    else:
        if not opened:
            logger.log(DATA_LEVEL, status.compare_url)


def configure_logger_data() -> None:
    retval = logging.StreamHandler(sys.stdout)
    retval.setFormatter(logging.Formatter("%(message)s"))
    retval.addFilter(lambda _: _.levelno == DATA_LEVEL)
    logger.addHandler(retval)


def configure_logger_error() -> None:
    error = logging.StreamHandler(sys.stderr)
    if COLOR["stderr"]:
        error.setFormatter(logging.Formatter("\033[1;31mError:\033[0m %(message)s"))
    else:
        error.setFormatter(logging.Formatter("Error: %(message)s"))
    error.addFilter(lambda _: _.levelno == logging.ERROR)
    logger.addHandler(error)


def configure_logger_info() -> None:
    if INFO_TO == "stdout":
        info = logging.StreamHandler(sys.stdout)
    else:
        info = logging.StreamHandler(sys.stderr)
    info.setFormatter(logging.Formatter("%(message)s"))
    info.addFilter(lambda _: _.levelno == logging.INFO)
    logger.addHandler(info)


def configure_logger_warning() -> None:
    warning = logging.StreamHandler(sys.stderr)
    if COLOR["stderr"]:
        warning.setFormatter(logging.Formatter("\033[33mWarning:\033[0m %(message)s"))
    else:
        warning.setFormatter(logging.Formatter("Warning: %(message)s"))
    warning.addFilter(lambda _: _.levelno == logging.WARNING)
    logger.addHandler(warning)


def create_local_branch(cloned: git.Repo, upstream: git.Remote | None, context: Context):
    """Create the local branch and define the ``update-branch`` alias. ``context.base_branch`` cannot be ``None``."""
    assert context.base_branch
    origin = cloned.remotes.origin
    if upstream:
        base_owner = context.upstream_owner
        base_remote = "upstream"
        base = upstream
    else:
        base_owner = context.owner
        base_remote = "origin"
        base = origin
    base_branch_full = f"{base_owner}:{context.base_branch}"
    if context.create_branch:
        # Create a local branch, starting from the base branch.
        logger.info(
            f"Checking out a new branch {f_blue(context.branch)} based on {f_blue(base_branch_full)}"
        )
        if context.base_branch not in base.refs:
            raise CloneError(f"The base branch {f_blue(base_branch_full)} does not exist.")
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
        logger.info(f"Checking out {f_blue(branch_full)} with base {f_blue(base_branch_full)}")
        if context.base_branch not in base.refs:
            raise CloneError(f"The base branch {f_blue(base_branch_full)} does not exist.")
        if context.branch not in origin.refs:
            raise CloneError(f"The branch {f_blue(branch_full)} does not exist.")
        branch = cloned.create_head(context.branch, origin.refs[context.branch])
        branch.set_tracking_branch(origin.refs[context.branch])
    branch.checkout()
    # Define the 'update-branch' alias.
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


def exit_with_error(error: Exception | str, code: int = 1) -> Never:
    logger.error(error)
    sys.exit(code)


def f_blue(value: str) -> str:
    if COLOR[INFO_TO]:
        return f"\033[36m{value}\033[0m"
    else:
        return value


def f_bold(value: str) -> str:
    if COLOR[INFO_TO]:
        return f"\033[1m{value}\033[0m"
    else:
        return value


def f_link(value: str, url: str) -> str:
    if COLOR[INFO_TO]:
        return f"\033]8;;{url}\a{f_blue(value)}\033]8;;\a"
    else:
        return value


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
    if parsed_base and isinstance(parsed_base, ParsedBranchSpec):
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
            if not is_valid_branch_name(branch):
                raise ValueError(f"'{branch}' is not a valid branch name.")
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


def get_default_branch(cloned: git.Repo) -> str:
    for ref in cloned.remotes.origin.refs:
        if ref.name == "origin/HEAD":
            return ref.ref.name.removeprefix("origin/")
    raise RuntimeError("Unable to identify default branch.")


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


def install_pre_commit(clone_dir: Path) -> None:
    if not (clone_dir / ".pre-commit-config.yaml").exists():
        return
    # The pre-commit package should have been installed in gimmegit's venv.
    # AFAIK, pre-commit doesn't expose a stable Python API, so we'll run it as a module.
    logger.info("Installing pre-commit hook")
    subprocess.run(
        [sys.executable, "-m", "pre_commit", "install"],
        cwd=clone_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )


def is_valid_branch_name(branch: str) -> bool:
    # When run in a repo, 'git check-ref-format --branch' expands "previous checkout" references.
    # Such references should be flagged as invalid, so we run the Git command in an empty dir.
    with tempfile.TemporaryDirectory() as empty_dir:
        command = [
            "git",
            "check-ref-format",
            "--branch",
            branch,
        ]
        result = subprocess.run(
            command,
            cwd=empty_dir,
            capture_output=True,
            text=True,
        )
        return result.returncode == 0


def make_clone_path(owner: str, project: str, branch: str) -> Path:
    branch_slug = branch.replace("/", "-")
    return Path(f"{project}/{owner}-{branch_slug}")


def make_columns(status: _status.Status) -> list[Column]:
    project = Column(
        last=False,
        title="Project",
        url=None,
        value=status.project,
    )
    base = Column(
        last=False,
        title="Base branch",
        url=status.base_url,
        value=f"{status.base_owner}:{status.base_branch}",
    )
    review = Column(
        last=True,
        title="Review branch",
        url=status.url,
        value=f"{status.owner}:{status.branch}",
    )
    return [project, base, review]


def make_formatted_title(col: Column) -> FormattedStr:
    return FormattedStr(
        formatted=f_bold(col.title),
        plain=col.title,
    )


def make_formatted_value(col: Column) -> FormattedStr:
    if col.url:
        return FormattedStr(
            formatted=f_link(col.value, col.url),
            plain=col.value,
        )
    else:
        return FormattedStr(
            formatted=col.value,
            plain=col.value,
        )


def make_github_clone_url(owner: str, project: str) -> str:
    if SSH:
        return f"git@github.com:{owner}/{project}.git"
    else:
        return f"https://github.com/{owner}/{project}.git"


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


def make_snapshot_name() -> str:
    today = datetime.now()
    today_formatted = today.strftime("%m%d")
    return f"snapshot{today_formatted}"


def make_title_cell(col: Column) -> str:
    formatted_title = make_formatted_title(col)
    if col.last:
        return formatted_title.formatted
    formatted_value = make_formatted_value(col)
    width = max(len(formatted_title.plain), len(formatted_value.plain))
    padding = " " * (width - len(formatted_title.plain))
    return f"{formatted_title.formatted}{padding}"


def make_value_cell(col: Column) -> str:
    formatted_value = make_formatted_value(col)
    if col.last:
        return formatted_value.formatted
    formatted_title = make_formatted_title(col)
    width = max(len(formatted_title.plain), len(formatted_value.plain))
    padding = " " * (width - len(formatted_value.plain))
    return f"{formatted_value.formatted}{padding}"


def parse_github_branch_spec(branch_spec: str) -> ParsedBranchSpec | BranchName | None:
    parsed = parse_github_url(branch_spec)
    if not parsed:
        if not is_valid_branch_name(branch_spec):
            raise ValueError(f"'{branch_spec}' is not a valid branch name.")
        return BranchName(
            branch=branch_spec,
        )
    if not parsed.branch:
        raise ValueError(f"'{branch_spec}' does not specify a branch.")
    return ParsedBranchSpec(
        branch=parsed.branch,
        owner=parsed.owner,
        project=parsed.project,
        remote_url=parsed.remote_url,
    )


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


def primary_usage(args: argparse.Namespace, cloning_args: list[str]) -> None:
    try:
        context = get_context(args)
    except ValueError as e:
        exit_with_error(e)
    if context.clone_dir.exists():
        logger.info(f_bold("You already have a clone:"))
        logger.info(context.clone_dir.resolve())
        if INFO_TO == "stderr":
            logger.log(DATA_LEVEL, context.clone_dir.resolve())
        sys.exit(10)
    if (
        not args.allow_outer_repo
        and context.clone_dir.parent.exists()
        and _inspect.get_repo(context.clone_dir.parent)
    ):
        exit_with_error(f"'{context.clone_dir.parent.resolve()}' is a repo.")
    if not args.force_project_dir and not context.clone_dir.parent.exists():
        candidate = _inspect.get_repo_from_latest_dir(Path.cwd())
        if candidate and _status.get_status(candidate):
            exit_with_error(
                "The working directory contains a gimmegit clone. Try running gimmegit in the parent directory."
            )
    try:
        clone(context, cloning_args)
    except CloneError as e:
        if context.clone_dir.exists():
            shutil.rmtree(context.clone_dir, ignore_errors=True)
        exit_with_error(e)
    if not args.no_pre_commit:
        install_pre_commit(context.clone_dir)
    logger.info(f_bold("Cloned repo:"))
    logger.info(context.clone_dir.resolve())
    if INFO_TO == "stderr":
        logger.log(DATA_LEVEL, context.clone_dir.resolve())


def set_global_color(color_arg: str) -> None:
    global COLOR
    if color_arg == "auto":
        COLOR["stdout"] = os.isatty(sys.stdout.fileno()) and not bool(os.getenv("NO_COLOR"))
        COLOR["stderr"] = os.isatty(sys.stderr.fileno()) and not bool(os.getenv("NO_COLOR"))
    elif color_arg == "always":
        COLOR["stdout"] = True
        COLOR["stderr"] = True


def set_global_info(return_dir_arg: bool) -> None:
    global INFO_TO
    if return_dir_arg:
        INFO_TO = "stderr"


def set_global_ssh(ssh_arg: str) -> None:
    global SSH
    if ssh_arg == "auto":
        ssh_dir = Path.home() / ".ssh"
        SSH = any(ssh_dir.glob("id_*"))
    elif ssh_arg == "always":
        SSH = True


def status_usage(status: _status.Status) -> None:
    columns = make_columns(status)
    logger.info("   ".join([make_title_cell(col) for col in columns]))
    values = "   ".join([make_value_cell(col) for col in columns])
    if not status.has_remote:
        values = f"{values} (not created)"
    logger.info(values)


if __name__ == "__main__":
    main()
