# C Error Handling Rule

- **Author**: Tohar Laufer
- **Date**: 16/06/2025
- **Version**: 1.0.0
- **Priority**: High

## Description
This rule defines the standard practices for error handling in C to ensure robust and predictable code.

## Error Handling
- **Return Values**: Functions should return an error code (e.g., an enum) or `NULL` on failure.
- `0` or `true` should indicate success.
- **`goto` for Cleanup**: Use `goto` for centralized cleanup in functions with multiple exit points.

```c
int process_data()
{
    int result = -1;
    void* data = malloc(1024);
    if (!data)
    {
        goto cleanup;
    }

    // ...

    result = 0;

cleanup:
    free(data);
    return result;
}
```

## When to apply
- When writing or modifying any C code (`.c`, `.h` files).
- During code reviews to enforce quality and safety standards.

## When not to apply
- When interfacing with third-party libraries that have their own established conventions. In such cases, an adaptation layer may be necessary.