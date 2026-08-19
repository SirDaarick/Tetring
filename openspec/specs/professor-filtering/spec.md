<professor-filtering Specification>
## Purpose

This specification covers the professor selection filter and its backtracking validation constraints.

## Requirements

### Requirement: Professor Selection Filter

The system MUST provide a filter to select preferred professors for specific subjects.

#### Scenario: Selecting a valid professor

- GIVEN the user is viewing the schedule builder
- WHEN the user selects a professor for a subject
- THEN the system MUST apply the filter
- AND the system MUST update available combinations

#### Scenario: Backtracking validation failure

- GIVEN the user has selected a set of professors
- WHEN the user selects an additional professor that causes no valid schedules to exist
- THEN the system MUST indicate a conflict
- AND the system MUST allow the user to backtrack their selections
