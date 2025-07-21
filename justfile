default: format lint test

format:
  uv run ruff format

lint:
  uv run ruff check

test:
  uv run pytest -vv

build:
  uv build

publish: test build
  uv publish
