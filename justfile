[private]
default:
  @just --summary --unsorted

format:
  uv lock --check
  uv run ruff format

lint:
  uv lock --check
  uv run ruff check
  uv run ruff format --diff
  uv run ty check

unit: (test "tests/unit")

functional: (test "tests/functional")

[private]
stress: (test "tests/stress")

[private]
test args="tests/unit tests/functional":
  uv lock --check
  uv run pytest -vv {{args}}

[private]
zizmor:
  uv lock --check
  uv run zizmor --format=sarif . > workflows.sarif

[private]
command-reference:
  #!/bin/bash
  uv lock --check
  diff <(uv run --script .scripts/extract_command_reference.py) <(uv run gimmegit -h)

[private]
demo:
  #!/bin/bash
  uv lock --check
  package_dir="$PWD"
  mkdir -p demo
  cd demo
  rm -rf jubilant/dwilding-my-feature
  uv run --project "$package_dir" gimmegit --allow-nested -u canonical dwilding/jubilant my-feature
  cd jubilant/dwilding-my-feature
  echo
  uv run --project "$package_dir" gimmegit
