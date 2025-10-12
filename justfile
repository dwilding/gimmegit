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
  #!/bin/sh
  mkdir -p demo
  cd demo
  rm -rf jubilant/dwilding-my-feature
  uv run --project .. gimmegit --ignore-outer -u canonical dwilding/jubilant my-feature
  cd jubilant/dwilding-my-feature
  echo
  uv run --project ../.. gimmegit
