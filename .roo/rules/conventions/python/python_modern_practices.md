# Python Modern Practices Rule

- **Author**: Tohar Laufer
- **Date**: 16/06/2025
- **Version**: 1.0.0
- **Priority**: High

## Description
This rule outlines modern Python features and best practices that should be used to write safe, clear, and elegant code.

## 1. Core Practices

### 1.1. Type Hinting
- Use type hints (PEP 484) for all function signatures, including methods.
- Use types from the `typing` module (`List`, `Dict`, `Tuple`, `Optional`, etc.).
- Strive for 100% type coverage, and use a static type checker like `mypy` in the CI pipeline.

### 1.2. Data Classes
- Use `dataclasses` (PEP 557) for classes that are primarily used to store data.
- Prefer immutable dataclasses (`@dataclass(frozen=True)`) to prevent objects from being modified after creation.

### 1.3. F-Strings
- Use f-strings for string formatting. They are more readable and performant than `str.format()` or the `%` operator.

### 1.4. Context Managers
- Use the `with` statement for managing resources like files or network connections to ensure they are properly closed.

### 1.5. Immutability
- Prefer immutable data structures (tuples, frozen dataclasses) over mutable ones (lists, dictionaries) where possible. This prevents unintended side effects.

## When to apply
- When writing any new Python code.
- When refactoring existing code to improve its quality and safety.

## When not to apply
- In performance-critical code where these features might introduce unacceptable overhead, after profiling and justification.