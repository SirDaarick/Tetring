## Exploration: Missing Frontend Features for Tetring

### Current State
The project has a basic frontend and backend setup, but several critical features are either missing or placeholders:
1. **SAES Connection**: The dashboard has a simple "Sincronizar ahora" button that calls `/dashboard/sync`. However, if the user doesn't have credentials linked, this call fails. There is no UI wizard to handle the multi-step credentials linking process (credentials input, captcha retrieval, captcha solving, and initial synchronization).
2. **Professor Filtering**: The backtracking scheduler in `backend/app/algorithms/scheduler.py` supports filtering groups by a list of professors (`profesores` key in `filters`). However, `GenerateRequest` does not expose this parameter, and the frontend `FilterPanel.tsx` has no professor filter multi-select control.
3. **Saved Schedules**: The `/saved` route loads `SavedPage.tsx`, which is a static placeholder displaying "Aún no has guardado ningún horario". The components `SavedScheduleCard` are not integrated, and there is no mechanism to fetch saved schedules from `/schedules/saved`, toggle favorites, or delete them.
4. **Profile Page**: `ProfilePage.tsx` displays user information from `useAuth()` but lacks any display of linked SAES details (like school name and boleta) or option to unlink the credentials.

### Affected Areas
- [frontend/src/lib/api.ts](file:///home/daarick/Proyectos/Tetring/frontend/src/lib/api.ts) — Define types for `OptionItemResponse`, update `SavedScheduleResponse`, and add types for professor lists and SAES profile.
- [frontend/src/components/dashboard/SaesConnectionWizard.tsx](file:///home/daarick/Proyectos/Tetring/frontend/src/components/dashboard/SaesConnectionWizard.tsx) — Create a new multi-step wizard component (stepper with 3 steps).
- [frontend/src/pages/DashboardPage.tsx](file:///home/daarick/Proyectos/Tetring/frontend/src/pages/DashboardPage.tsx) — Connect the SAES Connection Wizard to the sync status card.
- [frontend/src/components/scheduler/FilterPanel.tsx](file:///home/daarick/Proyectos/Tetring/frontend/src/components/scheduler/FilterPanel.tsx) — Add a professor filter multi-select inside the filter panel.
- [frontend/src/pages/SchedulerPage.tsx](file:///home/daarick/Proyectos/Tetring/frontend/src/pages/SchedulerPage.tsx) — Query the backend for professors when subjects are chosen, manage selection state, and integrate the professor filter list in the generate payload.
- [frontend/src/pages/SavedPage.tsx](file:///home/daarick/Proyectos/Tetring/frontend/src/pages/SavedPage.tsx) — Implement fetching of saved schedules, rendering of cards, and favorite/delete actions, plus a details view.
- [frontend/src/pages/ProfilePage.tsx](file:///home/daarick/Proyectos/Tetring/frontend/src/pages/ProfilePage.tsx) — Fetch and show SAES profile details, add an unlinking action, and embed the connection wizard.
- [backend/app/schemas/schedule.py](file:///home/daarick/Proyectos/Tetring/backend/app/schemas/schedule.py) — Add `profesores` list to `GenerateRequest`.
- [backend/app/services/schedule_service.py](file:///home/daarick/Proyectos/Tetring/backend/app/services/schedule_service.py) — Extract and pass `profesores` to backtracking `filters` inside `generate`, and add business logic to fetch unique professors for a list of claves.
- [backend/app/api/v1/schedules.py](file:///home/daarick/Proyectos/Tetring/backend/app/api/v1/schedules.py) — Add route `POST /schedules/professors` to get the list of unique professors.

### Approaches

#### 1. Professor Filtering Integration
- **Option A: Real-time backend-assisted filtering (Recommended)**
  - Brief Description: The frontend queries a new `POST /schedules/professors` endpoint when subjects change to get a list of active professors. The user selects from these, and the list of allowed professors is passed to the backend during schedule generation.
  - Pros: Early backtracking pruning (extremely efficient), precise matching options, matches backend filter capability.
  - Cons: Requires a new endpoint, adds an API call when subjects are selected.
  - Effort: Medium

- **Option B: Client-side post-filtering**
  - Brief Description: The frontend fetches all generated schedules and filters the list locally on the client.
  - Cons: Highly inefficient; does not prune backtracking early; if combinations exceed `max_results`, matching schedules might be lost.
  - Pros: No new endpoint needed.
  - Effort: Low

#### 2. SAES Connection Wizard Structure
- **Option A: Dialog-based reusable wizard (Recommended)**
  - Brief Description: Build a `SaesConnectionWizard` as a modal dialog that can be triggered from both the Dashboard (for unsynced users) and the Profile page (to connect).
  - Pros: Clean separation of concerns, highly reusable, isolated wizard state.
  - Cons: Requires modal state management.
  - Effort: Medium

- **Option B: Inline wizard steps on Dashboard**
  - Brief Description: Replace the sync card on the Dashboard with the wizard stepper directly in the page layout.
  - Pros: Simpler component layout, no dialog overlays.
  - Cons: Clutters the dashboard, hard to reuse on the Profile page.
  - Effort: Medium

### Recommendation
1. Implement the **Dialog-based reusable wizard** for SAES connection to ensure a smooth, multi-step flow that is accessible from both the Dashboard and the Profile Page.
2. Implement **Real-time backend-assisted filtering** for the professor selection. By adding a simple `/schedules/professors` endpoint and passing the selected list to `/schedules/generate`, we keep the backtracking generation highly optimized and avoid generating combinations that will just be discarded by the client.

### Risks
- **SAES API Outages / Captcha expiration**: The SAES credentials verification requires solving a captcha. The captcha token session lives for 10 minutes in memory. If a user delays solving the captcha or the connection to the SAES scrapers is flaky, the flow will fail. We must implement proper error handling and a refresh/retry captcha action.
- **Backtracking Complexity**: If a user selects many subjects and many professors, the backtracking can take some time. We should ensure the max results parameter is respected.

### Ready for Proposal
Yes — The proposed changes are clear and can be outlined in a formal change proposal. The orchestrator should tell the user that the exploration is complete, highlighting the design details for the SAES connection wizard, the new professor filtering route, the SavedPage grid implementation, and the ProfilePage integration.
