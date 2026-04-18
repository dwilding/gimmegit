[private]
default:
  @just --summary --unsorted

format:
  uv run --locked ruff format

lint:
  uv run --locked ruff check
  uv run --locked ruff format --diff
  uv run --locked ty check

unit: (test "tests/unit")

functional: (test "tests/functional")

[private]
stress: (test "tests/stress")

[private]
test args="tests/unit tests/functional":
  uv run --locked pytest -vv {{args}}

[private]
zizmor:
  uv run --locked zizmor .

[private]
command-reference:
  #!/bin/bash
  diff <(uv run --script .scripts/extract_command_reference.py) <(uv run --locked gimmegit -h)

[private]
demo:
  #!/bin/bash
  package_dir="$PWD"
  mkdir -p demo
  cd demo
  rm -rf jubilant/dwilding-my-feature
  uv run --locked --project "$package_dir" gimmegit --allow-nested -u canonical dwilding/jubilant my-feature
  cd jubilant/dwilding-my-feature
  echo
  uv run --locked --project "$package_dir" gimmegit
