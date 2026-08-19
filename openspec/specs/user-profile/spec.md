<user-profile Specification>
## Purpose

This specification covers displaying active user info, school linking state, and unlinking.

## Requirements

### Requirement: User Profile Display

The system MUST display user information and external account linking states.

#### Scenario: Viewing active profile

- GIVEN the user is logged in
- WHEN the user navigates to their profile
- THEN the system MUST display their active user information
- AND the system MUST display their school linking state

#### Scenario: Unlinking school account

- GIVEN the user has a linked school account
- WHEN the user chooses to unlink the account
- THEN the system MUST remove the connection
- AND the system MUST update the linking state to disconnected
