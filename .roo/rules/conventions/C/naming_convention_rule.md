# C Naming Conventions Rule

- **Author**: Tohar Laufer
- **Date**: 16/06/2025
- **Version**: 1.0.0
- **Priority**: Medium

## Description
This rule defines the naming conventions for C code in this project to ensure consistency and readability.

## Conventions
- **Variables, Functions, and Methods**: Use `snake_case` (e.g., `my_variable`, `calculate_sum()`).
- **Macros and Enums**: Use `UPPER_SNAKE_CASE` (e.g., `MAX_CONNECTIONS`, `COLOR_RED`).
- **Structs, Unions, and Typedefs**: Use `PascalCase` or a `_t` suffix for typedefs (e.g., `MyStruct`, `color_t`). The chosen convention should be consistent across the project.
- **Global Variables**: If used, they should be prefixed with `g_` (e.g., `g_main_window`).
- **Pointers**: Do not use a special prefix or suffix for pointers. The type system is sufficient to identify them. For example, `int* user_data` is preferred over `int* p_user_data`.

## When to apply
- When writing or modifying any C code (`.c`, `.h` files).
- During code reviews to enforce style consistency.

## When not to apply
- When working with third-party libraries that have their own established conventions.