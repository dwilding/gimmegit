from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import argparse
import re
import os
import sys

import git
import github

GIMMEGIT_GITHUB_SSH = bool(os.getenv("GIMMEGIT_GITHUB_SSH"))
GIMMEGIT_GITHUB_TOKEN = os.getenv("GIMMEGIT_GITHUB_TOKEN") or None


@dataclass
class Context:
    branch: str
    clone_url: str
    clone_dir: Path
    create_branch: bool
    owner: str
    project: str
    source_url: str | None
    base_branch: str | None


@dataclass
class Source:
    remote_url: str
    project: str


@dataclass
class ParsedURL:
    branch: str | None
    owner: str
    project: str


def cli() -> None:
    parser = argparse.ArgumentParser(description="todo")
    parser.add_argument("-b", "--base", dest="base_branch", help="todo")
    parser.add_argument("repo", help="todo")
    parser.add_argument("new_branch", nargs="?", help="todo")
    args = parser.parse_args()
    print("Getting repo details...")
    context = get_context(args)
    print(f"Cloning '{context.clone_url}'...")
    clone(context)
    print(f"Cloned repo:\n{context.clone_dir.resolve()}")


def get_context(args: argparse.Namespace) -> Context:
    if "/" not in args.repo:  # Simplistic way to detect a repo name
        if not GIMMEGIT_GITHUB_TOKEN:
            print(
                "Error: GIMMEGIT_GITHUB_TOKEN is not set. Use a GitHub URL instead of a repo name."
            )
            sys.exit(1)
        github_url = f"https://github.com/{get_github_login()}/{args.repo}"
    else:
        github_url = args.repo
    parsed = parse_github_url(github_url)
    if not parsed:
        print(f"Error: '{github_url}' is not a GitHub URL")
        sys.exit(1)
    if GIMMEGIT_GITHUB_SSH:
        clone_url = f"git@github.com:{parsed.owner}/{parsed.project}.git"
    else:
        clone_url = f"https://github.com/{parsed.owner}/{parsed.project}.git"
    if parsed.branch:
        create_branch = False
        branch = parsed.branch
        if args.new_branch:
            print(
                f"Warning: ignoring '{args.new_branch}' because '{github_url}' specifies a branch."
            )
    else:
        create_branch = True
        if args.new_branch:
            branch = args.new_branch
        else:
            branch = make_snapshot_name()
    source = get_github_source(parsed.owner, parsed.project)
    if source:
        source_url = source.remote_url
        project = source.project
    else:
        source_url = None
        project = parsed.project
    branch_short = branch.split("/")[-1]
    clone_dir = Path(f"{project}/{parsed.owner}-{branch_short}")
    if clone_dir.exists():
        print(f"You already have a clone:\n{clone_dir.resolve()}")
        sys.exit(10)
    return Context(
        branch=branch,
        clone_url=clone_url,
        clone_dir=clone_dir,
        create_branch=create_branch,
        owner=parsed.owner,
        project=project,
        source_url=source_url,
        base_branch=args.base_branch,
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
    api = github.Github(GIMMEGIT_GITHUB_TOKEN)
    user = api.get_user()
    return user.login


def get_github_source(owner: str, project: str) -> Source | None:
    if not GIMMEGIT_GITHUB_TOKEN:
        return None
    api = github.Github(GIMMEGIT_GITHUB_TOKEN)
    repo = api.get_repo(f"{owner}/{project}")
    if repo.fork:
        parent = repo.parent
        if GIMMEGIT_GITHUB_SSH:
            remote_url = f"git@github.com:{parent.owner.login}/{parent.name}.git"
        else:
            remote_url = f"https://github.com/{parent.owner.login}/{parent.name}.git"
        return Source(
            remote_url=remote_url,
            project=parent.name,
        )


def make_snapshot_name() -> str:
    today = datetime.now()
    today_formatted = today.strftime("%m%d")
    return f"snapshot{today_formatted}"


def clone(context: Context) -> None:
    cloned = git.Repo.clone_from(context.clone_url, context.clone_dir, no_tags=True)
    origin = cloned.remotes.origin
    if not context.base_branch:
        context.base_branch = get_default_branch(cloned)
    if context.source_url:
        source = cloned.create_remote("source", context.source_url)
        source.fetch(no_tags=True)
        if context.create_branch:
            # Create a local branch, starting from the base branch.
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
