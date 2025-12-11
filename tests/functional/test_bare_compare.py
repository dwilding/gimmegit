import subprocess


def test_compre_no_outer(uv_run, test_dir):
    command = [
        *uv_run,
        "gimmegit",
        "-c",
    ]
    result = subprocess.run(
        command,
        cwd=test_dir,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert not result.stdout
    expected_stderr = """\
Error: The working directory is not inside a gimmegit clone.
"""
    assert result.stderr == expected_stderr
