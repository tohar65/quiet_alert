# Python Style Guide

- **Author**: Tohar Laufer
- **Date**: 16/06/2025
- **Version**: 1.0.0
- **Priority**: High

## Description
This guide establishes the definitive coding style for Python in this project. It is primarily based on PEP 8, with additions inspired by Google's Python Style Guide to ensure code is readable, consistent, and maintainable.

## 1. Formatting

### 1.1. Line Length
- Maximum line length is 80 characters.

### 1.2. Indentation
- Use 4 spaces per indentation level. Do not use tabs.

### 1.3. Blank Lines
- Use two blank lines to separate top-level functions and class definitions.
- Use one blank line to separate method definitions inside a class.

### 1.4. Imports
- Imports should be at the top of the file.
- Group imports in the following order, with a blank line between each group:
    1. Standard library imports (e.g., `os`, `sys`).
    2. Third-party library imports (e.g., `requests`, `numpy`).
    3. Local application/library specific imports.
- Use absolute imports over relative imports.
- Avoid wildcard imports (`from module import *`).

## 2. Naming Conventions

- **Modules**: `short_snake_case`.
- **Classes**: `PascalCase`.
- **Functions & Methods**: `snake_case`.
- **Variables**: `snake_case`.
- **Constants**: `UPPER_SNAKE_CASE`.
- **Private Attributes**: Prefix with a single underscore (`_private_variable`).
- **Name-mangled Attributes**: Prefix with a double underscore (`__mangled_variable`).

## 3. Comments and Docstrings

### 3.1. Docstrings
- All public modules, functions, classes, and methods must have docstrings.
- Use Google-style docstrings.

```python
def my_function(arg1: int, arg2: str) -> bool:
    """Short description of the function.

    Longer description explaining the function's behavior,
    its side effects, etc.

    Args:
        arg1: Description of the first argument.
        arg2: Description of the second argument.

    Returns:
        Description of the return value.

    Raises:
        ValueError: If arg1 is invalid.
    """
    # ...
```

### 3.2. Comments
- Use comments to explain *why* something is done, not *what* is being done. The code should explain the "what".
- Keep comments up-to-date with code changes.

## When to apply
- When writing or modifying any Python code (`.py` files).
- During code reviews to enforce style consistency.

## When not to apply
- When working with third-party libraries that have their own established conventions.