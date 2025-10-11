check: lint test-unit

format:
  uv run ruff format

lint:
  uv run ruff check
  uv run ruff format --diff
  uv run ty check

test: test-unit test-functional

test-unit:
  uv run pytest -vv tests/unit

test-functional:
  uv run pytest -vv tests/functional

demo:
  mkdir -p demo
  rm -rf demo/jubilant/dwilding-my-feature
  uv run --directory demo gimmegit -u canonical dwilding/jubilant my-feature
