# Test-Driven Development (TDD) Workflow

- **Author**: Tohar Laufer
- **Date**: 13/06/2025
- **Version**: 1.0.0
- **Priority**: High

## Description
This rule establishes the testing strategy and principles for the project, mandating a Test-Driven Development (TDD) approach. The goal is to ensure high code quality, maintainability, and confidence in the system's correctness. All development must adhere to the principles outlined in `plan/testing_principles.md`.

## When to apply
- When writing any new code, for both new features and bug fixes.
- When creating or modifying automated test suites.
- When configuring the Continuous Integration (CI) pipeline.

## When not to apply
- When creating non-code assets like documentation or design files.
- During initial exploratory work or prototyping that is not intended for production.

## Key Principles

### 1. TDD Cycle
New code must only be written after a failing test has been created for it.

### 2. Test Hermeticity
Tests must be hermetic (self-contained) and must not rely on external services. Mocks and stubs are required to isolate components under test.

### 3. Test Automation
All tests must be automated and integrated into the CI pipeline to run on every commit.

### 4. Test Organization
Tests must be organized into the following directory structure:
- **Unit Tests:** `tests/unit/`
- **Integration Tests:** `tests/integration/`
- **System Tests:** `tests/system/`