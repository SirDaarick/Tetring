## Apply Progress - `implement-frontend-features`

### Phase 1: Backend/API definitions
- [x] 1.1 Update `backend/app/schemas/schedule.py`: Add `exclude_professors: list[str] | None` to `GenerateRequest`.
- [x] 1.2 Update `backend/app/api/v1/schedules.py`: Add `/professors` GET endpoint to fetch distinct professors for pending subjects.
- [x] 1.3 Update `frontend/src/lib/api.ts`: Add `exclude_professors` to `GenerateScheduleRequest` type and create `ProfessorResponse` interface.

### Phase 2: Frontend components & pages core logic
- [x] 2.1 Create `frontend/src/components/saes/SaesConnectionWizard.tsx`: Implement multi-step dialog for SAES login (credentials input, loading, success/error).
- [x] 2.2 Update `frontend/src/components/scheduler/FilterPanel.tsx`: Integrate a `MultiSelect` accessible popover component for `exclude_professors`.
- [x] 2.3 Update `frontend/src/pages/DashboardPage.tsx`: Replace generic sync button with `SaesConnectionWizard` trigger when `!isSynced`.
- [x] 2.4 Update `frontend/src/pages/ProfilePage.tsx`: Map query data to show SAES link status, add an unlink hook (`api.post("/saes/unlink")`), and trigger `SaesConnectionWizard` if unlinked.
- [x] 2.5 Update `frontend/src/pages/SavedPage.tsx`: Add `useQuery(["schedules", "saved"])` and map results to render `ScheduleCard` components.

### TDD Cycle Evidence
| Task | RED | GREEN | REFACTOR |
|---|---|---|---|
| 1.1, 1.2 | `test_exclude_professors_in_generate_request`, `test_get_professors_endpoint` | All backend tests passed | Done |
| 1.3 - 2.5 | N/A (No frontend test runner) | N/A | N/A |

### Work Unit Evidence
| Evidence | Required value |
|---|---|
| Focused test command and exact result | `cd backend && pytest tests/test_scheduler_api.py` (2 passed) |
| Runtime harness command/scenario and exact result | N/A - No frontend test runner for 1.3, 2.1-2.5. Manual UI verifications |
| Rollback boundary | `git revert` or drop uncommitted changes on `frontend/src` and `backend/app` |
