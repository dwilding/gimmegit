check: lint test-unit

format:
  uv run ruff format

lint:
  uv run ruff check
  uv run ruff format --diff
  uv run ty check

test-unit: (test "tests/unit")

test-functional: (test "tests/functional")

test args="tests/unit tests/functional":
  uv run pytest -vv {{args}}

check-command-reference:
  #!/bin/bash
  diff <(uv run .scripts/extract_command_reference.py) <(uv run gimmegit -h)

demo:
  #!/bin/bash
  package_dir="$PWD"
  mkdir -p demo
  cd demo
  rm -rf jubilant/dwilding-my-feature
  uv run --project "$package_dir" gimmegit --allow-outer-repo -u canonical dwilding/jubilant my-feature
  cd jubilant/dwilding-my-feature
  echo
  uv run --project "$package_dir" gimmegit
