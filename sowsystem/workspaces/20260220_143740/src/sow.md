    # Statement of Work (SOW)

## Project Name
Agent Controller Proof of Concept

## Objective
Create a standalone controller project that can safely make automated changes
to a separate agents repository on the local machine.

## Scope
- The controller project shall run independently from the agents repository.
- The controller shall be able to:
  - Read configuration values from a config file
  - Locate a target repository on the local filesystem
  - Modify predefined files in a controlled and reversible way
- Initial changes are limited to appending text to existing files.

## Out of Scope
- No direct production deployments
- No destructive file operations
- No network-based code execution

## Deliverables
- A runnable controller script
- A configuration file specifying target paths
- A log or console output describing applied changes

## Success Criteria
- Script runs without errors
- Target file is modified exactly once per execution
- Changes are visible via Git diff in the target repository