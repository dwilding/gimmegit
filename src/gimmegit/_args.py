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


class CustomArgParser(argparse.ArgumentParser):
    def error(self, message):
        raise RuntimeError(message)


def parse_args(args_to_parse) -> ArgsWithUsage:
    parser = CustomArgParser(add_help=False, argument_default=argparse.SUPPRESS)
    parser.add_argument("--color", nargs="?")
    parser.add_argument("--return-dir", action="store_true")
    parser.add_argument("--ssh", nargs="?")
    parser.add_argument("--force-project-dir", action="store_true")
    parser.add_argument("--allow-outer-repo", action="store_true")
    parser.add_argument("--no-pre-commit", action="store_true")
    parser.add_argument("-b", "--base-branch", nargs="?")
    parser.add_argument("-u", "--upstream-owner", nargs="?")
    parser.add_argument("repo", nargs="?")
    parser.add_argument("new_branch", nargs="?")
    parser.add_argument("-c", "--compare", action="store_const")
    parser.add_argument("-h", "--help", action="store_const")
    parser.add_argument("--version", action="store_const")
    parser.add_argument("--parse-url", nargs="?")
    args, unknown_args = parser.parse_known_args(args_to_parse)
    # Handle --color.
    # We use args.color to configure error logging, so make sure it has a proper value.
    if not hasattr(args, "color"):
        args.color = DEFAULT_CHOICE
    elif not args.color:
        args.color = DEFAULT_CHOICE
        return ArgsWithUsage(args=args, error=MISSING_COLOR, usage="")
    elif args.color not in CHOICES:
        args.color = DEFAULT_CHOICE
        return ArgsWithUsage(args=args, error=BAD_COLOR, usage="")
    # Handle usages of the gimmegit command.
    if hasattr(args, "repo"):
        return parse_as_primary(args, unknown_args)
    if hasattr(args, "compare"):
        return parse_as_compare(args, unknown_args)
    if hasattr(args, "help"):
        return parse_as_help(args, unknown_args)
    if hasattr(args, "version"):
        return parse_as_version(args, unknown_args)
    if hasattr(args, "parse_url"):
        return parse_as_tool(args, unknown_args)
    return parse_as_bare(args, unknown_args)


def parse_as_primary(args: argparse.Namespace, unknown_args: list[str]) -> ArgsWithUsage:
    def done(error: str | None) -> ArgsWithUsage:
        return ArgsWithUsage(args=args, error=error, usage="primary")

    # Handle --return-dir.
    if not hasattr(args, "return_dir"):
        args.return_dir = False
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
    if hasattr(args, "compare"):
        unknown_args.append("-c/--compare")
    if hasattr(args, "help"):
        unknown_args.append("-h/--help")
    if hasattr(args, "version"):
        unknown_args.append("--version")
    if hasattr(args, "parse_url"):
        unknown_args.append("--parse-url")
    if unknown_args:
        return done(f"Unexpected options: {', '.join(unknown_args)}.")
    return done(None)


def parse_as_compare(args: argparse.Namespace, unknown_args: list[str]) -> ArgsWithUsage:
    def done(error: str | None) -> ArgsWithUsage:
        return ArgsWithUsage(args=args, error=error, usage="compare")

    # Handle unknown args.
    unknown_args = add_non_primary_unknown_args(args, unknown_args)
    if hasattr(args, "ssh"):
        unknown_args.append("--ssh")
    if hasattr(args, "help"):
        unknown_args.append("-h/--help")
    if hasattr(args, "version"):
        unknown_args.append("--version")
    if hasattr(args, "parse_url"):
        unknown_args.append("--parse-url")
    if unknown_args:
        return done(f"Unexpected options: {', '.join(unknown_args)}.")
    return done(None)


def parse_as_help(args: argparse.Namespace, unknown_args: list[str]) -> ArgsWithUsage:
    def done(error: str | None) -> ArgsWithUsage:
        return ArgsWithUsage(args=args, error=error, usage="help")

    # Handle unknown args.
    unknown_args = add_non_primary_unknown_args(args, unknown_args)
    if hasattr(args, "ssh"):
        unknown_args.append("--ssh")
    if hasattr(args, "version"):
        unknown_args.append("--version")
    if hasattr(args, "parse_url"):
        unknown_args.append("--parse-url")
    if unknown_args:
        return done(f"Unexpected options: {', '.join(unknown_args)}.")
    return done(None)


def parse_as_version(args: argparse.Namespace, unknown_args: list[str]) -> ArgsWithUsage:
    def done(error: str | None) -> ArgsWithUsage:
        return ArgsWithUsage(args=args, error=error, usage="version")

    # Handle unknown args.
    unknown_args = add_non_primary_unknown_args(args, unknown_args)
    if hasattr(args, "ssh"):
        unknown_args.append("--ssh")
    if hasattr(args, "parse_url"):
        unknown_args.append("--parse-url")
    if unknown_args:
        return done(f"Unexpected options: {', '.join(unknown_args)}.")
    return done(None)


def parse_as_tool(args: argparse.Namespace, unknown_args: list[str]) -> ArgsWithUsage:
    def done(error: str | None) -> ArgsWithUsage:
        return ArgsWithUsage(args=args, error=error, usage="tool")

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


def parse_as_bare(args: argparse.Namespace, unknown_args: list[str]) -> ArgsWithUsage:
    def done(error: str | None) -> ArgsWithUsage:
        return ArgsWithUsage(args=args, error=error, usage="bare")

    # Handle unknown args.
    unknown_args = add_non_primary_unknown_args(args, unknown_args)
    if hasattr(args, "ssh"):
        unknown_args.append("--ssh")
    if unknown_args:
        return done(f"Unexpected options: {', '.join(unknown_args)}.")
    return done(None)


def add_non_primary_unknown_args(args: argparse.Namespace, unknown_args: list[str]) -> list[str]:
    extended = unknown_args.copy()
    if hasattr(args, "return_dir"):
        extended.append("--return-dir")
    if hasattr(args, "force_project_dir"):
        extended.append("--force-project-dir")
    if hasattr(args, "allow_outer_repo"):
        extended.append("--allow-outer-repo")
    if hasattr(args, "no_pre_commit"):
        extended.append("--no-pre-commit")
    if hasattr(args, "base_branch"):
        extended.append("-b/--base-branch")
    if hasattr(args, "upstream_owner"):
        extended.append("-u/--upstream-owner")
    return extended
