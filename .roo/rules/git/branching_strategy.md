# Git Branching Strategy

- **Author**: Tohar Laufer
- **Date**: 16/06/2025
- **Version**: 1.0.0
- **Priority**: High

## Description
This rule defines the Git branching model for this project. It is designed to ensure a clean and stable codebase by organizing the workflow around two primary branches: `main` and `dev`.

## Branching Model

### `main`
- The `main` branch represents the production-ready code.
- Direct commits to `main` are forbidden.
- Merges to `main` should only come from the `dev` branch, typically as part of a release process.

### `dev`
- The `dev` branch serves as the primary integration branch for new features.
- All feature branches are created from `dev`.
- Direct commits to `dev` are forbidden. All changes must come through Merge Requests (MRs) from feature branches.
- This branch should always be in a state that is ready for release.

### Feature Branches
- All new features and non-trivial bug fixes must be developed in separate feature branches.
- Feature branches should be named descriptively, using the convention `feature/<short-description>` (e.g., `feature/add-user-authentication`).
- Feature branches must be created from the `dev` branch.
- If a feature branch for the current task or context already exists, it should be used for all related commits. Avoid creating a new branch for work that belongs to an existing feature.

## When to apply
- When starting any new development work.
- When creating branches for features, bug fixes, or releases.

## When not to apply
- This rule should be followed for all code-related changes in the repository.