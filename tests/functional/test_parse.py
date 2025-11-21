import json
import subprocess

import helpers_functional as helpers


def test_parse(uv_run, test_dir):
    command = [
        *uv_run,
        "gimmegit",
        *helpers.no_color,
        *helpers.no_ssh,
        "--parse-url",
        "github.com/canonical/operator/tree/2.23-maintenance",
    ]
    result = subprocess.run(
        command,
        cwd=test_dir,
        capture_output=True,
        text=True,
        check=True,
    )
    assert json.loads(result.stdout) == {
        "branch": "2.23-maintenance",
        "owner": "canonical",
        "project": "operator",
        "remote_url": "https://github.com/canonical/operator.git",
    }


def test_parse_with_repo(uv_run, test_dir):
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
        check=True,
    )
    assert json.loads(result.stdout) == {
        "branch": "2.23-maintenance",
        "owner": "canonical",
        "project": "operator",
        "remote_url": "https://github.com/canonical/operator.git",
    }


def test_parse_invalid(uv_run, test_dir):
    command = [
        *uv_run,
        "gimmegit",
        *helpers.no_color,
        *helpers.no_ssh,
        "--parse-url",
        "github.com/canonical",
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
Error: 'github.com/canonical' is not a supported GitHub URL.
"""
    assert result.stderr == expected_stderr
