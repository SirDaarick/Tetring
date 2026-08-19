## Intent
Complete missing frontend-backend integrations for SAES scraping, professor filtering, saved schedules, and profile management to deliver a functional schedules dashboard.

## Scope

### In Scope
- Reusable `SaesConnectionWizard` modal for linking SAES credentials (stepper: credentials input, captcha, sync).
- Real-time professor filtering (backend `/schedules/professors` endpoint, frontend `FilterPanel` multi-select).
- Saved schedules page `/saved` displaying schedules, favoring, deleting, and details view.
- `ProfilePage` showing user info, SAES status (school, boleta), credentials unlinking, and wizard trigger.

### Out of Scope
- Automatic captcha solving (must remain manual).
- Advanced backtracking optimization parameters beyond professor filtering.

## Capabilities

### New Capabilities
- `saes-connection`: Account linking, credentials input, captcha verification, and synchronization.
- `professor-filtering`: Multi-select professor filter constraints during backtracking schedule generation.
- `saved-schedules`: Favorite, delete, list, and view details of saved schedule options.
- `user-profile`: Display user/SAES account info and unlink credentials.

### Modified Capabilities
None

## Approach
- **SAES Wizard**: Build a 3-step modal wizard. Fetch captcha from scraper API, display it, submit details.
- **Professor Filter**: Add `POST /schedules/professors` query by subject claves. Send selections in `GenerateRequest.filters.profesores`.
- **Saved Schedules**: Replace `/saved` placeholder with dynamic fetching and card actions.
- **Profile**: Enrich page with SAES attributes and unlink action.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `frontend/src/lib/api.ts` | Modified | Add SAES API types and saved schedule types. |
| `frontend/src/components/dashboard/SaesConnectionWizard.tsx` | New | Multi-step connection/captcha dialog. |
| `frontend/src/pages/DashboardPage.tsx` | Modified | Connect wizard to sync status action. |
| `frontend/src/components/scheduler/FilterPanel.tsx` | Modified | Multi-select for professor names. |
| `frontend/src/pages/SchedulerPage.tsx` | Modified | Load/pass professor filters to generator. |
| `frontend/src/pages/SavedPage.tsx` | Modified | Display and manage saved schedules. |
| `frontend/src/pages/ProfilePage.tsx` | Modified | Display SAES status, unlink button, and wizard. |
| `backend/app/schemas/schedule.py` | Modified | Add `profesores` list to `GenerateRequest`. |
| `backend/app/services/schedule_service.py` | Modified | Prune backtracking using professor filter. |
| `backend/app/api/v1/schedules.py` | Modified | Add `POST /schedules/professors` endpoint. |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| SAES captcha session timeout | Med | Catch error, allow quick captcha refresh in wizard. |
| Flaky SAES scrapers | Med | Show descriptive error messages and fallback instructions. |

## Rollback Plan
Revert git commits of frontend components and backend API/services changes to restore placeholder UI and old schemas.

## Dependencies
- Running `saes-api` scraper service for captcha generation and syncing.

## Success Criteria
- [ ] Users can connect SAES via wizard with credentials + manual captcha.
- [ ] Users can filter generated schedules by specific professors.
- [ ] Saved schedules can be listed, favorited, deleted, and inspected.
- [ ] Profile shows correct SAES details and allows unlinking.

## Proposal question round

1. **Captcha Fetching/State**: Does the captcha API return a base64-encoded image directly, or a URL? Is there an associated session/token ID that the frontend must hold and submit back?
2. **SAES Error Handling**: What specific error states (e.g., incorrect password, IP block, scraper timeout) should we support in the wizard UI, and should there be a fallback for manual upload if scraping fails completely?
3. **Saved Schedules Sync**: Are saved schedules stored exclusively server-side, or should there be local caching/fallback when offline?
4. **Professor Normalization**: Scraped SAES names can be messy. Should the backend clean/normalize professor names (e.g., trimming, casing) before exposing them in the filter?
