set ignore-comments

[private]
default:
  @just --summary --unsorted

format:
  uv run ruff check --fix
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
zizmor:
  uv run zizmor --format=sarif . > workflows.sarif

[private]
command-ref:
  #!/bin/bash
  set -euo pipefail
  diff <(uv run --script .scripts/extract_command_ref.py) <(uv run gimmegit -h)

[private]
demo:
  #!/bin/bash
  set -euo pipefail
  package_dir="$PWD"
  mkdir -p demo
  cd demo
  rm -rf jubilant/dwilding-my-feature
  uv run --project "$package_dir" gimmegit --nest -u canonical dwilding/jubilant my-feature
  cd jubilant/dwilding-my-feature
  echo
  uv run --project "$package_dir" gimmegit
