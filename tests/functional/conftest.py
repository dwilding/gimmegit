import os

import pytest


@pytest.fixture(scope="session")
def uv_run():
    yield ["uv", "run", "--project", os.getcwd()]


@pytest.fixture(scope="module")
def test_dir(tmp_path_factory):
    yield tmp_path_factory.mktemp("functional")


@pytest.fixture()
def fresh_dir(tmp_path_factory):
    # A dir no other test has touched. Use it in tests that assert nothing is created.
    yield tmp_path_factory.mktemp("functional")
