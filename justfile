[private]
default:
  @just --summary --unsorted

format:
  uv run --frozen ruff format

lint:
  uv run --frozen ruff check
  uv run --frozen ruff format --diff
  uv run --frozen ty check

unit: (test "tests/unit")

functional: (test "tests/functional")

[private]
stress: (test "tests/stress")

[private]
test args="tests/unit tests/functional":
  uv run --locked pytest -vv {{args}}

[private]
zizmor:
  uv run --frozen zizmor --format=sarif . > workflows.sarif

[private]
command-ref:
  #!/bin/bash
  set -e
  diff <(uv run --frozen --script .scripts/extract_command_ref.py) <(uv run --frozen gimmegit -h)

[private]
demo:
  #!/bin/bash
  set -e
  package_dir="$PWD"
  mkdir -p demo
  cd demo
  rm -rf jubilant/dwilding-my-feature
  uv run --frozen --project "$package_dir" gimmegit --allow-nested -u canonical dwilding/jubilant my-feature
  cd jubilant/dwilding-my-feature
  echo
  uv run --frozen --project "$package_dir" gimmegit
