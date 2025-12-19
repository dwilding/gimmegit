#!/usr/bin/env python3
"""Check that the help output in README.md matches the output of 'uv run gimmegit -h'."""

import subprocess
import sys
from pathlib import Path


def extract_help_from_readme(readme_path: Path) -> str:
    """Extract help text from README.md between the Command reference markers."""
    content = readme_path.read_text()
    
    # Find the start marker
    start_marker = "# Command reference\n\n```text\n"
    start_idx = content.find(start_marker)
    if start_idx == -1:
        print("Error: Could not find '# Command reference' marker in README.md")
        sys.exit(1)
    
    # Start after the marker
    start_idx += len(start_marker)
    
    # Find the closing triple backtick
    end_idx = content.find("\n```", start_idx)
    if end_idx == -1:
        print("Error: Could not find closing triple backtick after Command reference")
        sys.exit(1)
    
    # Extract the text between markers
    help_text = content[start_idx:end_idx]
    return help_text


def get_actual_help_output() -> str:
    """Get the actual help output from running 'uv run gimmegit -h'."""
    try:
        result = subprocess.run(
            ["uv", "run", "gimmegit", "-h"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.rstrip()
    except subprocess.CalledProcessError as e:
        print(f"Error running 'uv run gimmegit -h': {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        sys.exit(1)


def main():
    """Main function to check help consistency."""
    repo_root = Path(__file__).parent.parent
    readme_path = repo_root / "README.md"
    
    if not readme_path.exists():
        print(f"Error: README.md not found at {readme_path}")
        sys.exit(1)
    
    # Extract help from README
    readme_help = extract_help_from_readme(readme_path)
    
    # Get actual help output
    actual_help = get_actual_help_output()
    
    # Compare
    if readme_help == actual_help:
        print("✓ Help output in README.md matches 'uv run gimmegit -h'")
        sys.exit(0)
    else:
        print("✗ Help output in README.md does NOT match 'uv run gimmegit -h'")
        print()
        print("Expected (from 'uv run gimmegit -h'):")
        print("=" * 80)
        print(actual_help)
        print("=" * 80)
        print()
        print("Found in README.md:")
        print("=" * 80)
        print(readme_help)
        print("=" * 80)
        sys.exit(1)


if __name__ == "__main__":
    main()
