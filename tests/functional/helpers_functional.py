from pathlib import Path
import os
import re
import subprocess
import types

from gimmegit import _version

no_ssh = ["--ssh", "never"]

fail_in_dev = types.SimpleNamespace(
    condition=re.search(r"\.dev\d+$", _version.__version__),
    reason="Follow up before release",
    strict=True,
)
no_token = types.SimpleNamespace(
    condition="GITHUB_TOKEN" not in os.environ,
    reason="GITHUB_TOKEN is not set",
)


def token_env() -> dict[str, str]:
    env = os.environ.copy()
    env["GIMMEGIT_GITHUB_TOKEN"] = os.environ["GITHUB_TOKEN"]
    return env


def get_branch(dir: Path) -> str:
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=dir,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def get_config(dir: Path, name: str) -> str:
    result = subprocess.run(
        ["git", "config", "--get", name],
        cwd=dir,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def get_remote_branches(dir: Path) -> str:
    result = subprocess.run(
        ["git", "branch", "--remotes"],
        cwd=dir,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout
