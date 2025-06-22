# Conventional Commits Rule

- **Author**: Tohar Laufer
- **Date**: 16/06/2025
- **Version**: 1.0.0
- **Priority**: High

## Description
All commit messages must follow the Conventional Commits specification. This ensures that commit messages are human and machine-readable, which helps in automating changelog generation and semantic versioning.

The commit message should be structured as follows:

```
<type>: <description>

[optional body]

[optional footer(s)]
```

### Types
The following types are allowed:
- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **perf**: A code change that improves performance
- **test**: Adding missing tests or correcting existing tests
- **build**: Changes that affect the build system or external dependencies (example scopes: gulp, broccoli, npm)
- **ci**: Changes to our CI configuration files and scripts (example scopes: Travis, Circle, BrowserStack, SauceLabs)
- **chore**: Other changes that don't modify src or test files
- **revert**: Reverts a previous commit

## When to apply
- When writing any commit message.

## When not to apply
- This rule should always be applied.

## Example

### Correct
```
feat: allow provided config object to extend other configs
```
```
fix: correct minor typos in code

see the issue for details on the typos fixed

Reviewed-by: Z
Refs #133
```
```
docs: correct spelling of CHANGELOG
```

### Incorrect
```
Fixed a bug
```
```
Update code
```
```
initial commit