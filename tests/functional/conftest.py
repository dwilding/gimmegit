import os

import pytest


@pytest.fixture(scope="session")
def uv_run():
    yield ["uv", "run", "--project", os.getcwd()]


@pytest.fixture(scope="module")
def test_dir(tmp_path_factory):
    yield tmp_path_factory.mktemp("module_temp")
