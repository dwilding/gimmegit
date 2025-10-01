check: lint test-unit

format:
  uv run ruff format

lint:
  uv run ruff check
  uv run ruff format --diff
  uv run ty check

test: test-unit

test-unit:
  uv run pytest -vv tests/unit

build:
  uv build
  uv sync
