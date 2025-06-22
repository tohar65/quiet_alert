# C Memory Management Rule

- **Author**: Tohar Laufer
- **Date**: 16/06/2025
- **Version**: 1.1.0
- **Priority**: High

## Description
This rule outlines critical practices for memory management in C to prevent leaks, buffer overflows, and other memory-related bugs. Adherence to these guidelines is crucial for writing safe and reliable C code.

## Memory Management
- **Check Allocation Return**: Always check the return value of `malloc()`, `calloc()`, and `realloc()`. If allocation fails, it returns `NULL`. The program must handle this gracefully, for example by propagating the error up to the caller.
- **Initialize Memory**: Initialize memory immediately after allocation to avoid undefined behavior. `calloc()` is preferred over `malloc` when zero-initialization is needed, as it's often more performant and secure. Otherwise, use `memset()` immediately after `malloc`.
- **Free Memory Exactly Once**: Every memory block allocated with `malloc`, `calloc`, or `realloc` must have a corresponding `free()`. Freeing memory more than once or freeing a pointer not obtained from the allocation functions leads to undefined behavior.
- **Avoid Dangling Pointers**: After `free()`-ing a pointer, set it to `NULL` immediately. This prevents accidental use of a dangling pointer, which points to deallocated memory.
- **Clear Ownership Semantics**: For any dynamically allocated memory, there must be a single, clear owner responsible for freeing it. This can be a specific function, a struct, or a component. Document the ownership semantics clearly.
- **`sizeof` with Pointer, Not Type**: Use `sizeof(*pointer)` instead of `sizeof(type)` when allocating memory. This avoids type mismatches if the pointer's type changes during refactoring (e.g., `int *p = malloc(10 * sizeof(*p));` is safer than `int *p = malloc(10 * sizeof(int));`).
- **`realloc` Usage**: Be cautious with `realloc`. It may move the memory block to a new location. All existing pointers to the old block will become invalid. The original pointer must be updated with the return value of `realloc`. Also, if `realloc` fails, it returns `NULL` and the original memory block is *not* freed. A common safe pattern is: `void* new_ptr = realloc(old_ptr, new_size); if (new_ptr == NULL) { /* handle error, old_ptr is still valid */ } else { old_ptr = new_ptr; }`.
- **Prevent Buffer Overflows**: Use bounded and safe string/memory functions like `snprintf()`, `strncpy()`, and `memcpy_s` (if available) instead of their unsafe counterparts (`sprintf`, `strcpy`, `memcpy`). Always validate buffer sizes and input lengths.
- **Avoid Variable-Length Arrays (VLAs)**: Do not use VLAs on the stack, as they can easily cause a stack overflow if the requested size is large. If you need a dynamically-sized array, allocate it on the heap using `malloc` or `calloc`.

## When to apply
- When writing or modifying any C code (`.c`, `.h` files).
- During code reviews to enforce quality and safety standards.

## When not to apply
- When interfacing with third-party libraries that have their own established conventions. In such cases, an adaptation layer may be necessary.