import subprocess

no_color = ["--color", "never"]
no_ssh = ["--ssh", "never"]


def get_branch(dir: str) -> str:
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=dir,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def get_config(dir: str, name: str) -> str:
    result = subprocess.run(
        ["git", "config", "--get", name],
        cwd=dir,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def set_config(dir: str, name: str, value: str) -> None:
    subprocess.run(
        ["git", "config", name, value],
        cwd=dir,
        check=True,
    )
