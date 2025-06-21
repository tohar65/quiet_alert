# Python Error Handling Rule

- **Author**: Tohar Laufer
- **Date**: 16/06/2025
- **Version**: 1.0.0
- **Priority**: High

## Description
This rule defines the standard practices for error handling in Python using exceptions to ensure robust and predictable code.

## 1. Exception Handling

### 1.1. Raising Exceptions
- Use built-in exception types when they make sense.
- Create custom exception classes for application-specific errors. These should inherit from `Exception`.
- Raise exceptions with clear, informative messages.

### 1.2. Catching Exceptions
- Be specific in `except` clauses. Avoid catching broad exceptions like `Exception` or `BaseException`.
- Catch the most specific exception type that you can handle.
- Never use `except:` without specifying an exception type.
- Use a `finally` block for cleanup code that must always run, regardless of whether an exception occurred.

### 1.3. Example: Custom Exception

```python
class MyCustomError(Exception):
    """A custom error for my application."""
    pass

def process_data(data):
    if not data:
        raise MyCustomError("Data cannot be empty.")
    # ...

try:
    process_data(None)
except MyCustomError as e:
    print(f"Caught an error: {e}")

```

## When to apply
- When writing any function or method that can fail.
- When calling code that may raise exceptions.

## When not to apply
- This rule should be followed for all Python code.