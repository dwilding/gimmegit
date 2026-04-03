import os
import subprocess

import helpers_functional as helpers


def test_working_clone_exclude_dotgit(uv_run, test_dir):
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
        capture_output=True,
        check=True,
    )
    os.utime(test_dir / "frogtab/dwilding-outer/.git")
    command_inner = [
        *uv_run,
        "gimmegit",
        *helpers.no_ssh,
        "--allow-outer-repo",
        "dwilding/frogtab",
        "inner",
    ]
    working_dir = test_dir / "frogtab/dwilding-outer"
    result = subprocess.run(
        command_inner,
        cwd=working_dir,
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
