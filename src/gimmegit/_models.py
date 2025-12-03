import subprocess
import tempfile


def is_valid_branch_name(branch: str) -> bool:
    with tempfile.TemporaryDirectory() as tmpdir:
        command = ["git", "check-ref-format", "--branch", branch]
        result = subprocess.run(
            command,
            cwd=tmpdir,
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
