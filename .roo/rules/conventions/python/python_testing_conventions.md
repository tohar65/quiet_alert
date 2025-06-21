# Python Testing Conventions

- **Author**: Tohar Laufer
- **Date**: 16/06/2025
- **Version**: 1.0.0
- **Priority**: High

## Description
This rule defines the conventions for writing automated tests in Python, complementing the project-wide TDD workflow. The goal is to ensure tests are clear, maintainable, and effective.

## 1. Testing Framework
- The standard testing framework for this project is `pytest`.

## 2. Test Structure
- Test files must be named `test_*.py` or `*_test.py`.
- Test functions must be named `test_*`.
- Group related tests into classes named `Test*`.

## 3. Assertions
- Use plain `assert` statements. `pytest` provides detailed output for failed assertions.
- Do not use `unittest.TestCase` style assertions (e.g., `self.assertEqual`).

## 4. Fixtures
- Use `pytest` fixtures (`@pytest.fixture`) to provide a fixed baseline for tests.
- Fixtures are preferred over `setup/teardown` methods for managing test state.

## 5. Mocking
- Use the `unittest.mock` library for mocking objects and patching modules.
- `pytest-mock` provides a `mocker` fixture that simplifies its use.

## Example

```python
import pytest
from unittest.mock import Mock

# Assume my_module.py has a function to test
# from my_app import my_module

def test_my_function(mocker):
    """Tests my_function with a mock."""
    # Arrange
    mock_dependency = mocker.patch('my_app.my_module.dependency_function')
    mock_dependency.return_value = "mocked_value"

    # Act
    result = my_module.my_function()

    # Assert
    mock_dependency.assert_called_once()
    assert result == "expected_result_from_mock"

```

## When to apply
- When writing any unit, integration, or system tests in Python.

## When not to apply
- This rule should be followed for all Python tests.