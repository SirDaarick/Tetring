<saved-schedules Specification>
## Purpose

This specification covers listing, details inspection, favoriting, and deletion of saved schedules.

## Requirements

### Requirement: Saved Schedules Management

The system MUST allow users to manage their saved schedules.

#### Scenario: Listing saved schedules

- GIVEN the user has saved schedules
- WHEN the user navigates to the saved schedules view
- THEN the system MUST list all saved schedules

#### Scenario: Inspecting schedule details

- GIVEN the user is viewing their saved schedules
- WHEN the user selects a specific schedule
- THEN the system MUST display the details of the schedule

#### Scenario: Favoriting a schedule

- GIVEN the user is viewing their saved schedules
- WHEN the user marks a schedule as favorite
- THEN the system MUST pin the schedule to the top of the list

#### Scenario: Deleting a schedule

- GIVEN the user is viewing their saved schedules
- WHEN the user deletes a schedule
- THEN the system MUST remove the schedule from the list
