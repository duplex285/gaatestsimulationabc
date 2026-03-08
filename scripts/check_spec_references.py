#!/usr/bin/env python3
"""Check that all Python functions in src/ include a spec reference.

Scans for function definitions in src/python_scoring/ and verifies each
contains a comment or docstring referencing the spec document.

Reference: CLAUDE_RULES.md Rule 2
"""

import ast
import sys
from pathlib import Path

SPEC_PATTERNS = [
    "reference: abc-assessment-spec",
    "reference: section",
    "spec section",
]

SRC_DIR = Path(__file__).parent.parent / "src" / "python_scoring"


def check_file(filepath: Path) -> list[str]:
    """Return list of functions missing spec references in a file."""
    if filepath.name == "__init__.py":
        return []

    try:
        source = filepath.read_text()
        tree = ast.parse(source)
    except (SyntaxError, FileNotFoundError):
        return [f"  Could not parse {filepath}"]

    violations = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        if node.name.startswith("_"):
            continue

        # Get the source lines for this function (docstring + first few lines)
        start = node.lineno - 1
        end = min(start + 20, len(source.splitlines()))
        func_text = "\n".join(source.splitlines()[start:end]).lower()

        has_ref = any(pattern in func_text for pattern in SPEC_PATTERNS)
        if not has_ref:
            violations.append(
                f"  {filepath.name}:{node.lineno} - {node.name}() missing spec reference"
            )

    return violations


def main() -> int:
    if not SRC_DIR.exists():
        print("src/python_scoring/ not found. Nothing to check.")
        return 0

    py_files = list(SRC_DIR.glob("*.py"))
    if not py_files:
        print("No Python files in src/python_scoring/. Nothing to check.")
        return 0

    all_violations = []
    for f in sorted(py_files):
        all_violations.extend(check_file(f))

    if all_violations:
        print("FAIL: Functions missing spec references:")
        for v in all_violations:
            print(v)
        print(f"\n{len(all_violations)} function(s) need a spec reference.")
        print('Add: "Reference: abc-assessment-spec Section X.Y" to docstring.')
        return 1

    print("PASS: All functions have spec references.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
