import pytest


@pytest.fixture(autouse=True)
def hermetic_git_env(monkeypatch: pytest.MonkeyPatch):
    """Drop Git environment variables inherited from the outer process.

    `git commit` runs pre-commit hooks with GIT_INDEX_FILE (and friends) exported,
    pointing at the parent repository's index. This fixture prevents Git subprocesses
    from reading that index and failing to find objects.
    """

    for var in (
        "GIT_INDEX_FILE",
        "GIT_DIR",
        "GIT_WORK_TREE",
        "GIT_OBJECT_DIRECTORY",
    ):
        monkeypatch.delenv(var, raising=False)
