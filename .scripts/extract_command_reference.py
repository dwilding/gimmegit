"""Extracts gimmegit's help output from the "Command reference" section of README.md."""

from pathlib import Path


def main() -> None:
    text = Path("README.md").read_text()
    start_marker = "# Command reference\n\n```text\n"
    start_index = text.find(start_marker)
    assert start_index > 0
    start_index += len(start_marker)
    end_index = text.find("\n```", start_index)
    assert end_index > start_index
    print(text[start_index:end_index])


if __name__ == "__main__":
    main()
