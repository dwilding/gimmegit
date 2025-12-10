# Instructions for Copilot code reviewer

## Structure of Python files in `src/gimmegit`

Each file must be organized in this order:

1. Imports
2. Variable definitions
3. Dataclasses, in alphabetical order
4. Other classes, in alphabetical order
5. Functions, in alphabetical order

Exceptions for `_cli.py`:

- The `main()` function must be first in the list of functions
- The `if __name__ == "__main__"` block must be at the end of the file
