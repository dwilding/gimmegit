import os

import pytest


def pytest_runtest_setup(item):
    if hasattr(item.parent, "_abort"):
        pytest.skip("Earlier test failed")


def pytest_runtest_makereport(item, call):
    if call.excinfo:
        item.parent._abort = "_abort"


@pytest.fixture(scope="session")
def uv_run():
    yield ["uv", "run", "--project", os.getcwd()]


@pytest.fixture(scope="module")
def test_dir(tmp_path_factory):
    yield tmp_path_factory.mktemp("integration")
