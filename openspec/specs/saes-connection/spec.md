<saes-connection Specification>
## Purpose

This specification covers the SAES account linking flow, including captcha handling, credentials validation, and scheduling synchronization.

## Requirements

### Requirement: SAES Account Linking

The system MUST allow users to link their SAES account.

#### Scenario: Successful SAES linking

- GIVEN the user is on the SAES connection page
- WHEN the user provides valid SAES credentials and a valid captcha
- THEN the system MUST link the account
- AND the system MUST trigger a scheduling synchronization

#### Scenario: Invalid credentials

- GIVEN the user is on the SAES connection page
- WHEN the user provides invalid SAES credentials
- THEN the system MUST display an error message
- AND the system MUST NOT link the account

#### Scenario: Captcha failure

- GIVEN the user is on the SAES connection page
- WHEN the user provides an invalid captcha
- THEN the system MUST prompt the user to solve a new captcha
