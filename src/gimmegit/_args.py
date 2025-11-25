from dataclasses import dataclass
import argparse

CHOICES = ["auto", "always", "never"]
DEFAULT_CHOICE = "auto"
BAD_COLOR = "The value of --color must be 'auto', 'always', or 'never'."
BAD_SSH = "The value of --ssh must be 'auto', 'always', or 'never'."
MISSING_COLOR = "No --color value specified."
MISSING_SSH = "No --ssh value specified."


@dataclass
class ArgsWithUsage:
    args: argparse.Namespace
    error: str | None
    usage: str


@dataclass
class ReducedArgs:
    args: argparse.Namespace
    error: str | None


class CustomArgParser(argparse.ArgumentParser):
    def error(self, message):
        raise RuntimeError(message)


def parse_args(args_to_parse) -> ArgsWithUsage:
    parser = CustomArgParser(add_help=False, argument_default=argparse.SUPPRESS)
    parser.add_argument("--color", nargs="?")
    parser.add_argument("--ssh", nargs="?")
    parser.add_argument("--force-project-dir", action="store_true")
    parser.add_argument("--allow-outer-repo", action="store_true")
    parser.add_argument("--no-pre-commit", action="store_true")
    parser.add_argument("-b", "--base-branch", nargs="?")
    parser.add_argument("-u", "--upstream-owner", nargs="?")
    parser.add_argument("repo", nargs="?")
    parser.add_argument("new_branch", nargs="?")
    parser.add_argument("-h", "--help", action="store_const")
    parser.add_argument("--version", action="store_const")
    parser.add_argument("--parse-url", nargs="?")
    args, unknown_args = parser.parse_known_args(args_to_parse)
    if hasattr(args, "repo"):
        reduced = parse_as_primary(args, unknown_args)
        return ArgsWithUsage(
            args=reduced.args,
            error=reduced.error,
            usage="primary",
        )
    if hasattr(args, "help"):
        reduced = parse_as_help(args, unknown_args)
        return ArgsWithUsage(
            args=reduced.args,
            error=reduced.error,
            usage="help",
        )
    if hasattr(args, "version"):
        reduced = parse_as_version(args, unknown_args)
        return ArgsWithUsage(
            args=reduced.args,
            error=reduced.error,
            usage="version",
        )
    if hasattr(args, "parse_url"):
        reduced = parse_as_tool(args, unknown_args)
        return ArgsWithUsage(
            args=reduced.args,
            error=reduced.error,
            usage="tool",
        )
    reduced = parse_as_bare(args, unknown_args)
    return ArgsWithUsage(
        args=reduced.args,
        error=reduced.error,
        usage="bare",
    )


def parse_as_primary(args: argparse.Namespace, unknown_args: list[str]) -> ReducedArgs:
    def done(error: str | None) -> ReducedArgs:
        return ReducedArgs(args=args, error=error)

    # Handle --color.
    if not hasattr(args, "color"):
        args.color = DEFAULT_CHOICE
    elif not args.color:
        return done(MISSING_COLOR)
    elif args.color not in CHOICES:
        return done(BAD_COLOR)
    # Handle --ssh.
    if not hasattr(args, "ssh"):
        args.ssh = DEFAULT_CHOICE
    elif not args.ssh:
        return done(MISSING_SSH)
    elif args.ssh not in CHOICES:
        return done(BAD_SSH)
    # Handle --force-project-dir, --allow-outer-repo, and --no-pre-commit.
    if not hasattr(args, "force_project_dir"):
        args.force_project_dir = False
    if not hasattr(args, "allow_outer_repo"):
        args.allow_outer_repo = False
    if not hasattr(args, "no_pre_commit"):
        args.no_pre_commit = False
    # Handle -b/--base-branch and -u/--upstream-owner.
    if not hasattr(args, "base_branch"):
        args.base_branch = None
    elif not args.base_branch:
        return done("No base branch specified.")
    if not hasattr(args, "upstream_owner"):
        args.upstream_owner = None
    elif not args.upstream_owner:
        return done("No upstream owner specified.")
    # Handle new_branch.
    if not hasattr(args, "new_branch"):
        args.new_branch = None
    # Handle unknown args.
    if hasattr(args, "help"):
        unknown_args.append("-h/--help")
        del args.help
    if hasattr(args, "version"):
        unknown_args.append("--version")
        del args.version
    if hasattr(args, "parse_url"):
        unknown_args.append("--parse-url")
        del args.parse_url
    if unknown_args:
        return done(f"Unexpected options: {', '.join(unknown_args)}.")
    return done(None)


def parse_as_help(args: argparse.Namespace, unknown_args: list[str]) -> ReducedArgs:
    def done(error: str | None) -> ReducedArgs:
        return ReducedArgs(args=args, error=error)

    # Handle --color.
    if not hasattr(args, "color"):
        args.color = DEFAULT_CHOICE
    elif not args.color:
        return done(MISSING_COLOR)
    elif args.color not in CHOICES:
        return done(BAD_COLOR)
    # Handle unknown args.
    unknown_args = add_non_primary_unknown_args(args, unknown_args)
    if hasattr(args, "ssh"):
        unknown_args.append("--ssh")
        del args.ssh
    if hasattr(args, "version"):
        unknown_args.append("--version")
        del args.version
    if hasattr(args, "parse_url"):
        unknown_args.append("--parse-url")
        del args.parse_url
    if unknown_args:
        return done(f"Unexpected options: {', '.join(unknown_args)}.")
    return done(None)


def parse_as_version(args: argparse.Namespace, unknown_args: list[str]) -> ReducedArgs:
    def done(error: str | None) -> ReducedArgs:
        return ReducedArgs(args=args, error=error)

    # Handle --color.
    if not hasattr(args, "color"):
        args.color = DEFAULT_CHOICE
    elif not args.color:
        return done(MISSING_COLOR)
    elif args.color not in CHOICES:
        return done(BAD_COLOR)
    # Handle unknown args.
    unknown_args = add_non_primary_unknown_args(args, unknown_args)
    if hasattr(args, "ssh"):
        unknown_args.append("--ssh")
        del args.ssh
    if hasattr(args, "parse_url"):
        unknown_args.append("--parse-url")
        del args.parse_url
    if unknown_args:
        return done(f"Unexpected options: {', '.join(unknown_args)}.")
    return done(None)


def parse_as_tool(args: argparse.Namespace, unknown_args: list[str]) -> ReducedArgs:
    def done(error: str | None) -> ReducedArgs:
        return ReducedArgs(args=args, error=error)

    # Handle --color.
    if not hasattr(args, "color"):
        args.color = DEFAULT_CHOICE
    elif not args.color:
        return done(MISSING_COLOR)
    elif args.color not in CHOICES:
        return done(BAD_COLOR)
    # Handle --ssh.
    if not hasattr(args, "ssh"):
        args.ssh = DEFAULT_CHOICE
    elif not args.ssh:
        return done(MISSING_SSH)
    elif args.ssh not in CHOICES:
        return done(BAD_SSH)
    # Handle --parse-url.
    if not args.parse_url:
        return done("No GitHub URL specified.")
    # Handle unknown args.
    unknown_args = add_non_primary_unknown_args(args, unknown_args)
    if unknown_args:
        return done(f"Unexpected options: {', '.join(unknown_args)}.")
    return done(None)


def parse_as_bare(args: argparse.Namespace, unknown_args: list[str]) -> ReducedArgs:
    def done(error: str | None) -> ReducedArgs:
        return ReducedArgs(args=args, error=error)

    # Handle --color.
    if not hasattr(args, "color"):
        args.color = DEFAULT_CHOICE
    elif not args.color:
        return done(MISSING_COLOR)
    elif args.color not in CHOICES:
        return done(BAD_COLOR)
    # Handle unknown args.
    unknown_args = add_non_primary_unknown_args(args, unknown_args)
    if hasattr(args, "ssh"):
        unknown_args.append("--ssh")
        del args.ssh
    if unknown_args:
        return done(f"Unexpected options: {', '.join(unknown_args)}.")
    return done(None)


def add_non_primary_unknown_args(args: argparse.Namespace, unknown_args: list[str]) -> list[str]:
    extended = unknown_args.copy()
    if hasattr(args, "force_project_dir"):
        extended.append("--force-project-dir")
        del args.force_project_dir
    if hasattr(args, "allow_outer_repo"):
        extended.append("--allow-outer-repo")
        del args.allow_outer_repo
    if hasattr(args, "no_pre_commit"):
        extended.append("--no-pre-commit")
        del args.no_pre_commit
    if hasattr(args, "base_branch"):
        extended.append("-b/--base-branch")
        del args.base_branch
    if hasattr(args, "upstream_owner"):
        extended.append("-u/--upstream-owner")
        del args.upstream_owner
    return extended
