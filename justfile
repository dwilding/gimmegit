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
zizmor:
  uv run zizmor --format=sarif . > workflows.sarif

[private]
command-ref:
  #!/bin/bash
  set -e
  diff <(uv run --script .scripts/extract_command_ref.py) <(uv run gimmegit -h)

[private]
demo:
  #!/bin/bash
  set -e
  package_dir="$PWD"
  mkdir -p demo
  cd demo
  rm -rf jubilant/dwilding-my-feature
  uv run --project "$package_dir" gimmegit --allow-nested -u canonical dwilding/jubilant my-feature
  cd jubilant/dwilding-my-feature
  echo
  uv run --project "$package_dir" gimmegit

[private]
deps:
  #!/bin/bash
  set -e
  uv lock --check
  # If we bumped a direct dependency in uv.lock, we should also bump the minimum version constraint
  # in pyproject.toml (because gimmegit doesn't require uv). Let's check for any inconsistencies:
  lockfile_committed=$(git log --max-count=1 --format=%cI -- uv.lock)
  uv_output=$(uv lock --dry-run --resolution lowest-direct --exclude-newer "$lockfile_committed" 2>&1)
  if grep '^Update ' <<<"$uv_output"; then
    exit 1
  fi
