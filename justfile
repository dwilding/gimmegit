[private]
default:
  @just --summary --unsorted

format:
  uv run ruff format

lint:
  uv run ruff check
  uv run ruff format --diff
  uv run ty check

unit: (test "tests/unit")

functional: (test "tests/functional")

[private]
stress: (test "tests/stress")

[private]
test args="tests/unit tests/functional":
  uv run pytest -vv {{args}}

[private]
check-command-reference:
  #!/bin/bash
  diff <(uv run .scripts/extract_command_reference.py) <(uv run gimmegit -h)

[private]
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
