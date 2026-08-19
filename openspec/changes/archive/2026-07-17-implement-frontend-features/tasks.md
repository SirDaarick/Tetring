## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~250-350 |
| 400-line budget risk | Medium |
| Chained PRs recommended | No |
| Suggested split | single-pr |
| Delivery strategy | single-pr |
| Chain strategy | size-exception |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: size-exception
400-line budget risk: Medium

### Suggested Work Units

Not needed, proceeding with a single-pr per strategy.

## Phase 1: Backend/API definitions

- [x] 1.1 Update `backend/app/schemas/schedule.py`: Add `exclude_professors: list[str] | None` to `GenerateRequest`.
- [x] 1.2 Update `backend/app/api/v1/schedules.py`: Add `/professors` GET endpoint to fetch distinct professors for pending subjects.
- [x] 1.3 Update `frontend/src/lib/api.ts`: Add `exclude_professors` to `GenerateScheduleRequest` type and create `ProfessorResponse` interface.

## Phase 2: Frontend components & pages core logic

- [x] 2.1 Create `frontend/src/components/saes/SaesConnectionWizard.tsx`: Implement multi-step dialog for SAES login (credentials input, loading, success/error).
- [x] 2.2 Update `frontend/src/components/scheduler/FilterPanel.tsx`: Integrate a `MultiSelect` accessible popover component for `exclude_professors`.
- [x] 2.3 Update `frontend/src/pages/DashboardPage.tsx`: Replace generic sync button with `SaesConnectionWizard` trigger when `!isSynced`.
- [x] 2.4 Update `frontend/src/pages/ProfilePage.tsx`: Map query data to show SAES link status, add an unlink hook (`api.post("/saes/unlink")`), and trigger `SaesConnectionWizard` if unlinked.
- [x] 2.5 Update `frontend/src/pages/SavedPage.tsx`: Add `useQuery(["schedules", "saved"])` and map results to render `ScheduleCard` components.

## Phase 3: Integration and manual testing/verifications

- [x] 3.1 Verify unit behavior of `MultiSelect`: Ensure selection toggle, search filtering, and state updates work as expected.
- [x] 3.2 Verify integration of `SaesConnectionWizard`: Test step transitions (input -> loading -> success).
- [x] 3.3 Verify integration of `SavedPage.tsx`: Mock or hit API `/schedules/saved` and ensure `ScheduleCard` renders correctly.
- [x] 3.4 Verify backend `/professors` endpoint: Assert only distinct professors from pending subjects are returned.
