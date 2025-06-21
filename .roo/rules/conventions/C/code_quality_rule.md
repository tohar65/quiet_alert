# C Code Quality Rule

- **Author**: Tohar Laufer
- **Date**: 16/06/2025
- **Version**: 1.0.0
- **Priority**: High

## Description
This rule establishes the core conventions for writing high-quality C code. The focus is on ensuring code clarity, robust memory management, and comprehensive error handling to produce reliable and maintainable software.

## 1. Code Formatting

### 1.1. Line Length
- Maximum line length is 80 characters.

### 1.2. Indentation
- Use 4 spaces per indentation level. Do not use tabs.

### 1.3. Braces
- Use Allman style braces, where the opening brace is on a new line.

```c
if (condition)
{
    // ...
}
```

### 1.4. Spaces
- Use spaces around binary operators: `a = b + c;`
- Do not use spaces around unary operators: `*p = -x;`
- Use a space after commas and semicolons.

## 2. Best Practices

### 2.1. `const` Correctness
- Use `const` extensively to prevent unintended modifications.

### 2.2. Header Guards
- Use `#pragma once` for header guards. It is more concise and less error-prone than traditional `#ifndef` guards.

### 2.3. `static` Keyword
- Use `static` for functions and global variables that do not need to be visible outside of their translation unit.

### 2.4. Modern C Features
- Prefer C11 or later for new projects.
- Use `<stdbool.h>` for boolean types.
- Use `<stdint.h>` for fixed-width integer types.

## When to apply
- When writing or modifying any C code (`.c`, `.h` files).
- During code reviews to enforce quality and safety standards.

## When not to apply
- When interfacing with third-party libraries that have their own established conventions. In such cases, an adaptation layer may be necessary.