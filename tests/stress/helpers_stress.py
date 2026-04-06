import os

no_ssh = ["--ssh", "never"]


def default_env() -> dict[str, str]:
    env = os.environ.copy()
    env["GIMMEGIT_FORCE_STDOUT"] = "1"
    return env
