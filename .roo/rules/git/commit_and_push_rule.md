# Commit, Push, and Merge Workflow

- **Author**: Tohar Laufer
- **Date**: 13/06/2025
- **Version**: 1.1.0
- **Priority**: Medium

## Description
This rule outlines the workflow for committing, pushing, and merging changes. It ensures that progress is saved regularly and that the final merge into the `dev` branch is done only after user approval.

## Workflow
1.  **Regular Commits**: The agent must commit and push significant progress regularly to its feature branch. This ensures that work is not lost and provides a clear history of the development process.
2.  **Final Merge**: At the end of a task, after all work is completed, tested, and confirmed by the user, the agent must ask the user for approval to merge the feature branch into `dev`.

## When to apply
- After any code or file modification has been successfully completed and tested.
- After the user has explicitly confirmed that the changes are correct and ready to be saved.
- When a task is complete and ready for integration.

## When not to apply
- If the changes are incomplete, untested, or have known issues.
- If the user has not given their approval to commit, push or merge.