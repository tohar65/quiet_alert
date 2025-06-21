# Merge Request and Code Review Process

- **Author**: Tohar Laufer
- **Date**: 16/06/2025
- **Version**: 1.0.0
- **Priority**: High

## Description
This rule outlines the mandatory process for submitting, reviewing, and merging code via Merge Requests (MRs). The goal is to ensure that all changes are peer-reviewed and meet quality standards before being integrated into the `dev` branch.

## Merge Request (MR) Requirements
1.  **Creation**: All new code must be submitted through an MR targeted at the `dev` branch. Direct pushes to `main` and `dev` are forbidden.
2.  **Source Branch**: Feature branches must be up-to-date with the `dev` branch. Developers must rebase their feature branch on top of the latest `dev` before submitting an MR.
3.  **Title and Description**: The MR title must be clear and concise, following the Conventional Commits format. The description should explain the "what" and "why" of the changes.

## Code Review (CR) Requirements
1.  **Mandatory Review**: Every MR must be reviewed and approved by at least one other developer before it can be merged.
2.  **Reviewer's Responsibility**: The reviewer is responsible for checking for correctness, clarity, performance, and adherence to all project rules and conventions.
3.  **Approval**: Approval indicates that the reviewer is confident in the quality of the code and its readiness for integration.

## Merging
- **Web Only**: Merges must be performed through the web interface (e.g., GitHub, GitLab) after all checks and reviews have passed.
- **Linear History**: The project must maintain a linear Git history. Merges should be performed using a squash or rebase strategy to avoid merge commits on the `dev` branch.

## When to apply
- When submitting any code for review.
- When reviewing code submitted by other developers.

## When not to apply
- This rule should be followed for all code changes.