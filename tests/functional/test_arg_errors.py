import subprocess

import helpers_functional as helpers


def test_no_repo(uv_run, test_dir):
    command = [
        *uv_run,
        "gimmegit",
        *helpers.no_color,
    ]
    result = subprocess.run(
        command,
        cwd=test_dir,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert not result.stdout
    expected_stderr = """\
Error: No repo specified. Run 'gimmegit -h' for help.
"""
    assert result.stderr == expected_stderr


def test_repo_with_parse(uv_run, test_dir):
    command = [
        *uv_run,
        "gimmegit",
        *helpers.no_color,
        *helpers.no_ssh,
        "--parse-url",
        "github.com/canonical/operator/tree/2.23-maintenance",
        "dwilding/jubilant",
    ]
    result = subprocess.run(
        command,
        cwd=test_dir,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert not result.stdout
    expected_stderr = """\
Error: Unexpected options: --parse-url. Run 'gimmegit -h' for help.
"""
    assert result.stderr == expected_stderr


def test_parse_no_url(uv_run, test_dir):
    command = [
        *uv_run,
        "gimmegit",
        *helpers.no_color,
        *helpers.no_ssh,
        "--parse-url",
    ]
    result = subprocess.run(
        command,
        cwd=test_dir,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert not result.stdout
    expected_stderr = """\
Error: No GitHub URL specified. Run 'gimmegit -h' for help.
"""
    assert result.stderr == expected_stderr
