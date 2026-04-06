import os
import subprocess
import time

import helpers_functional as helpers


def test_working_clone_exclude_dotgit(uv_run, test_dir):
    # Run gimmegit to get an outer repo.
    command_outer = [
        *uv_run,
        "gimmegit",
        *helpers.no_ssh,
        "dwilding/frogtab",
        "outer",
    ]
    subprocess.run(
        command_outer,
        cwd=test_dir,
        env=helpers.default_env(),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )
    # Ensure that the outer repo's .git dir is the latest dir.
    future = time.time() + 10
    os.utime(test_dir / "frogtab/dwilding-outer/.git", (future, future))
    # Run gimmegit to get an inner repo.
    command_inner = [
        *uv_run,
        "gimmegit",
        *helpers.no_ssh,
        "--allow-nested",
        "dwilding/frogtab",
        "inner",
    ]
    working_dir = test_dir / "frogtab/dwilding-outer"
    result = subprocess.run(
        command_inner,
        cwd=working_dir,
        env=helpers.default_env(),
        capture_output=True,
        text=True,
        check=True,
    )
    expected_dir = working_dir / "frogtab/dwilding-inner"
    expected_stdout = f"""\
Getting repo details
Cloning https://github.com/dwilding/frogtab.git
Checking out a new branch inner based on dwilding:main
Cloned repo:
{expected_dir}
"""
    assert result.stdout == expected_stdout
