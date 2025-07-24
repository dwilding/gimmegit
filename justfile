check: lint static test

format:
  uv run ruff format

lint:
  uv run ruff check
  uv run ruff format --diff

static:
  uv run ty check

test:
  uv run pytest -vv

build:
  uv build
  uv sync

publish: build
  uv publish
