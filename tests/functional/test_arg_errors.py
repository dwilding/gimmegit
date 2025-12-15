import subprocess


def test_no_repo(uv_run, test_dir):
    command = [
        *uv_run,
        "gimmegit",
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


def test_missing_upstream_owner(uv_run, test_dir):
    command = [
        *uv_run,
        "gimmegit",
        "dwilding/jubilant",
        "-u",
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
Error: No upstream owner specified. Run 'gimmegit -h' for help.
"""
    assert result.stderr == expected_stderr


def test_missing_base_branch(uv_run, test_dir):
    command = [
        *uv_run,
        "gimmegit",
        "dwilding/jubilant",
        "-b",
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
Error: No base branch specified. Run 'gimmegit -h' for help.
"""
    assert result.stderr == expected_stderr


def test_missing_color(uv_run, test_dir):
    command = [
        *uv_run,
        "gimmegit",
        "dwilding/jubilant",
        "--color",
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
Error: No --color value specified. Run 'gimmegit -h' for help.
"""
    assert result.stderr == expected_stderr


def test_invalid_color(uv_run, test_dir):
    command = [
        *uv_run,
        "gimmegit",
        "dwilding/jubilant",
        "--color",
        "invalid",
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
Error: The value of --color must be 'auto', 'always', or 'never'. Run 'gimmegit -h' for help.
"""
    assert result.stderr == expected_stderr


def test_missing_ssh(uv_run, test_dir):
    command = [
        *uv_run,
        "gimmegit",
        "dwilding/jubilant",
        "--ssh",
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
Error: No --ssh value specified. Run 'gimmegit -h' for help.
"""
    assert result.stderr == expected_stderr


def test_invalid_ssh(uv_run, test_dir):
    command = [
        *uv_run,
        "gimmegit",
        "dwilding/jubilant",
        "--ssh",
        "invalid",
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
Error: The value of --ssh must be 'auto', 'always', or 'never'. Run 'gimmegit -h' for help.
"""
    assert result.stderr == expected_stderr


def test_repo_with_compare(uv_run, test_dir):
    command = [
        *uv_run,
        "gimmegit",
        "-c",
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
Error: Unexpected options: -c/--compare. Run 'gimmegit -h' for help.
"""
    assert result.stderr == expected_stderr


def test_repo_with_help(uv_run, test_dir):
    command = [
        *uv_run,
        "gimmegit",
        "-h",
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
Error: Unexpected options: -h/--help. Run 'gimmegit -h' for help.
"""
    assert result.stderr == expected_stderr


def test_repo_with_version(uv_run, test_dir):
    command = [
        *uv_run,
        "gimmegit",
        "--version",
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
Error: Unexpected options: --version. Run 'gimmegit -h' for help.
"""
    assert result.stderr == expected_stderr


def test_repo_with_parse(uv_run, test_dir):
    command = [
        *uv_run,
        "gimmegit",
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


def test_parse_missing_ssh(uv_run, test_dir):
    command = [
        *uv_run,
        "gimmegit",
        "--parse-url",
        "github.com/canonical/operator/tree/2.23-maintenance",
        "--ssh",
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
Error: No --ssh value specified. Run 'gimmegit -h' for help.
"""
    assert result.stderr == expected_stderr


def test_parse_invalid_ssh(uv_run, test_dir):
    command = [
        *uv_run,
        "gimmegit",
        "--parse-url",
        "github.com/canonical/operator/tree/2.23-maintenance",
        "--ssh",
        "invalid",
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
Error: The value of --ssh must be 'auto', 'always', or 'never'. Run 'gimmegit -h' for help.
"""
    assert result.stderr == expected_stderr


def test_status_unexpected(uv_run, test_dir):
    command = [
        *uv_run,
        "gimmegit",
        "--return-dir",
        "--ssh",
        "always",
        "--force-project-dir",
        "--allow-outer-repo",
        "--no-pre-commit",
        "-b",
        "2.23-maintenance",
        "-u",
        "canonical",
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
Error: Unexpected options: --return-dir, --force-project-dir, --allow-outer-repo, --no-pre-commit, -b/--base-branch, -u/--upstream-owner, --ssh. Run 'gimmegit -h' for help.
"""
    assert result.stderr == expected_stderr
