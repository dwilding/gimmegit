"""Writes release notes based on merged PRs."""

import json
import os
import subprocess
import sys

PREFIXES = ["feat:", "fix:", "revert:", "perf:", "docs:"]


def gh(*args: str) -> str:
    """Run a gh command and return its stdout, stripped of trailing whitespace."""
    result = subprocess.run(["gh", *args], check=True, capture_output=True, text=True)
    return result.stdout.strip()


def latest_tag() -> str:
    return gh("release", "list", "-L", "1", "--json", "tagName", "-q", ".[0].tagName")


def merged_prs() -> list[dict]:
    """Return the number and title of PRs merged since the latest release."""
    repo = os.environ["GITHUB_REPOSITORY"]
    release_date = gh("api", f"repos/{repo}/releases/tags/{latest_tag()}", "--jq", ".created_at")
    prs = gh(
        "pr",
        "list",
        "--state",
        "merged",
        "--base",
        "main",
        "--json",
        "number,title",
        "--search",
        f"merged:>{release_date}",
        "--limit",
        "50",
    )
    return json.loads(prs)


def release_notes(prs: list[dict], new_tag: str) -> str:
    """Return the release notes body for the given PRs.

    Groups PRs by title prefix then breaking/non-breaking.
    """
    entries = ""
    for prefix in PREFIXES:
        breaking_prefix = f"{prefix.removesuffix(':')}!:"
        group = sorted(
            (pr for pr in prs if pr["title"].startswith((prefix, breaking_prefix))),
            key=lambda pr: (not pr["title"].startswith(breaking_prefix), pr["number"]),
        )
        for pr in group:
            entries += f"- {pr['title']} (#{pr['number']})\n"
    if not entries:
        entries = "This is a maintenance release with no fixes or new features.\n"
    repo = os.environ["GITHUB_REPOSITORY"]
    return f"{entries}\nChangelog: https://github.com/{repo}/compare/{latest_tag()}...{new_tag}"


if __name__ == "__main__":
    print(release_notes(merged_prs(), sys.argv[1]))
