check: lint test

format:
  uv run ruff format

lint:
  uv run ruff check
  uv run ruff format --diff
  uv run ty check

test:
  uv run pytest -vv

build:
  uv build
  uv sync
