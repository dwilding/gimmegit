import pytest


@pytest.fixture(scope="module")
def test_dir(tmp_path_factory):
    yield tmp_path_factory.mktemp("module_temp")


@pytest.fixture
def tool_cmd(test_dir):
    return ["uv", "run", "--directory", test_dir, "gimmegit"]
