import shutil
import subprocess

import helpers_stress as helpers


def test_juju_clone_main(uv_run, test_dir):
    command = [
        *uv_run,
        "gimmegit",
        *helpers.no_ssh,
        "-j",
        "-u",
        "juju",
        "https://github.com/dwilding/juju/tree/main",
    ]
    subprocess.run(
        command,
        cwd=test_dir,
        env=helpers.default_env(),
        capture_output=True,
        check=True,
    )
    assert (test_dir / "juju/dwilding-main").exists()


def test_juju_update_main(test_dir):
    subprocess.run(
        ["git", "update-branch"],
        cwd=test_dir / "juju/dwilding-main",
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "push"],
        cwd=test_dir / "juju/dwilding-main",
        capture_output=True,
        check=True,
    )


def test_juju_create_branch(uv_run, test_dir):
    command = [
        *uv_run,
        "gimmegit",
        *helpers.no_ssh,
        "-j",
        "-u",
        "juju",
        "dwilding/juju",
        "test-gimmegit",
    ]
    subprocess.run(
        command,
        cwd=test_dir,
        env=helpers.default_env(),
        capture_output=True,
        check=True,
    )
    assert (test_dir / "juju/dwilding-test-gimmegit").exists()
    subprocess.run(
        ["git", "push"],
        cwd=test_dir / "juju/dwilding-test-gimmegit",
        capture_output=True,
        check=True,
    )
    shutil.rmtree(test_dir / "juju/dwilding-test-gimmegit", ignore_errors=True)


def test_juju_clone_branch(uv_run, test_dir):
    command = [
        *uv_run,
        "gimmegit",
        *helpers.no_ssh,
        "-j",
        "-u",
        "juju",
        "https://github.com/dwilding/juju/tree/test-gimmegit",
    ]
    subprocess.run(
        command,
        cwd=test_dir,
        env=helpers.default_env(),
        capture_output=True,
        check=True,
    )
    assert (test_dir / "juju/dwilding-test-gimmegit").exists()


def test_juju_delete_branch(test_dir):
    subprocess.run(
        ["git", "push", "origin", "--delete", "test-gimmegit"],
        cwd=test_dir / "juju/dwilding-test-gimmegit",
        capture_output=True,
        check=True,
    )
