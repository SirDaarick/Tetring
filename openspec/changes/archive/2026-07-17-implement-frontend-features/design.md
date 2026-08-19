<Design: implement-frontend-features>
## Technical Approach

Introduce a new `SaesConnectionWizard` component for handling the SAES account connection process step-by-step, replacing the direct `syncMutation` call on the `DashboardPage` and adding SAES status/unlink capabilities on `ProfilePage`. Extend the scheduler to support filtering out specific professors by adding a `/schedules/professors` endpoint in the backend and a new custom multi-select in the `FilterPanel`. Fully implement `SavedPage` to fetch and render the user's saved schedules using existing `ScheduleCard` components.

## Architecture Decisions

### Decision: SAES Connection Wizard Integration
**Choice**: Use a unified `SaesConnectionWizard` component triggered from both `DashboardPage` (when not synced) and `ProfilePage` (when adding/updating SAES).
**Alternatives considered**: Separate wizards or keeping the simple sync button.
**Rationale**: Centralizing the connection flow ensures a consistent UX and easier maintainability for future auth steps (e.g. CAPTCHA).

### Decision: Professor Filtering Strategy
**Choice**: Pass `exclude_professors` in `GenerateRequest` instead of filtering client-side. The frontend fetches available professors from a new `/schedules/professors` endpoint.
**Alternatives considered**: Send all professors to the frontend and filter everything client-side.
**Rationale**: Offloading filtering to the backend scheduler optimizes memory and ensures only valid generated combinations are transferred over the network.

### Decision: Custom Multi-Select Component
**Choice**: Build a generic `MultiSelect` accessible component inside `FilterPanel.tsx` (or a sub-component) using a popover with a searchable checkbox list.
**Alternatives considered**: Standard `<select multiple>` or heavy third-party libs.
**Rationale**: A native-feel custom component keeps the bundle light while providing a better UX matching the current clay design system.

## Data Flow

    [DashboardPage/ProfilePage] ──(wizard state)──→ [SaesConnectionWizard] ──(credentials)──→ API /saes/link
                                                                                                   │
    [FilterPanel] ──(fetch)──→ API /schedules/professors                                           │
         │                                                                                         │
         └─────────(exclude_professors)──→ [SchedulerPage] ──(generate)──→ API /schedules/generate │
                                                                                                   │
    [SavedPage] ──(fetch)──→ API /schedules/saved ──(render)──→ [ScheduleCard] ────────────────────┘

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `frontend/src/pages/DashboardPage.tsx` | Modify | Remove generic sync button; render `SaesConnectionWizard` trigger when `!isSynced`. |
| `frontend/src/pages/ProfilePage.tsx` | Modify | Add query mapping to show SAES link status. Add unlink hook calling `api.post("/saes/unlink")` and trigger wizard if unlinked. |
| `frontend/src/components/saes/SaesConnectionWizard.tsx` | Create | Multi-step dialog for SAES login (credentials, loading, success/error). |
| `frontend/src/components/scheduler/FilterPanel.tsx` | Modify | Integrate `MultiSelect` component for `exclude_professors`. |
| `frontend/src/pages/SavedPage.tsx` | Modify | Add `useQuery(["schedules", "saved"])` and map results to `ScheduleCard`. |
| `backend/app/api/v1/schedules.py` | Modify | Add `/professors` GET endpoint to fetch distinct professors for pending subjects. |
| `backend/app/schemas/schedule.py` | Modify | Add `exclude_professors: list[str] | None` to `GenerateRequest`. |
| `frontend/src/lib/api.ts` | Modify | Add `exclude_professors` to `GenerateScheduleRequest` type and new types for professors. |

## Interfaces / Contracts

```typescript
// frontend/src/lib/api.ts additions
export interface GenerateScheduleRequest {
  // ... existing fields
  exclude_professors?: string[];
}

export interface ProfessorResponse {
  name: string;
}
```

```python
# backend/app/schemas/schedule.py additions
class GenerateRequest(BaseModel):
    # ... existing fields
    exclude_professors: list[str] | None = Field(
        None,
        description="Lista de nombres de profesores a excluir",
    )
```

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit | MultiSelect Component | Verify selection toggle, search filtering, and state updates. |
| Integration | `SavedPage.tsx` | Mock API `/schedules/saved` and ensure `ScheduleCard` renders correctly. |
| Integration | `SaesConnectionWizard`| Test step transitions (input -> loading -> success). |
| Unit (Backend) | `/professors` endpoint| Assert only distinct professors from pending subjects are returned. |

## Threat Matrix

N/A — no routing, shell, subprocess, VCS/PR automation, executable-file classification, or process-integration boundary.

## Migration / Rollout

No migration required. The `exclude_professors` field is optional, ensuring backward compatibility with existing requests.

## Open Questions

- [ ] Does the `SaesConnectionWizard` require CAPTCHA handling in this iteration?
- [ ] Should `SavedPage` support bulk deletion of schedules?
</Design: implement-frontend-features>
