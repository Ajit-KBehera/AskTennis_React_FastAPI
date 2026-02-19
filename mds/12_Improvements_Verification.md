# Backend & Frontend Improvements – Verification Checklist

Last verified: all items below are **done** unless marked otherwise.

---

## Backend (`docs_new/11_Backend_Improvements.md`)

| # | Item | Status | Where |
|---|------|--------|-------|
| 1 | 429 response includes `Retry-After` header | ✅ | `backend/main.py` – custom `rate_limit_exceeded_handler` |
| 2 | Query text max length (2000 chars) | ✅ | `backend/api/routers/query.py` – `QueryRequest.query` with `Field(max_length=2000)` |
| 3 | Sanitize 500 error detail in production | ✅ | `backend/utils/error_utils.py` + query, matches, filters routers use `get_500_detail()` |
| 4 | Timeout for AI query (default 120s, env `QUERY_TIMEOUT_SECONDS`) | ✅ | `backend/api/routers/query.py` – `asyncio.wait_for(..., timeout)`; 504 on timeout |
| 5 | `/health` (liveness) + `/ready` (auth DB check) | ✅ | `backend/main.py` |
| 6 | Auth hardening: username (alphanumeric + underscore), password (letter + digit), JWT required in prod | ✅ | `backend/api/auth_schemas.py` validators; `backend/main.py` `startup_checks` |
| 7 | Global exception handler (sanitized 500, re-raise `HTTPException`) | ✅ | `backend/main.py` – `global_exception_handler` |

---

## Frontend (`docs_new/10_Frontend_UI_UX_Improvements.md`)

| # | Area | Item | Status | Where |
|---|------|------|--------|-------|
| 1 | Query history | Recent questions in UI (last 5–10, click to re-run) | ✅ | `App.tsx` – `getQueryHistory(10)`; `QuickInsights` – `recentQueries` |
| 2 | Empty states | “Select a player…” when Stats + All Players | ✅ | `App.tsx` – `showStatsEmpty` + empty state card |
| 2 | Empty states | Retry + Edit question on error | ✅ | `App.tsx` – error card with Retry and Edit question buttons |
| 3 | AI response | Skeleton while loading (2–3 lines) | ✅ | `App.tsx` – skeleton below TennisLoader; `index.css` – `.skeleton-line` |
| 3 | AI response | Copy answer / Copy SQL / Expand all / Collapse all | ❌ Removed | Per user request; doc “consider” only |
| 4 | Search & Quick Insights | Placeholder rotation (4 options, 4s) | ✅ | `SearchPanel.tsx` – `PLACEHOLDERS`, `setPlaceholderIndex` interval |
| 4 | Search & Quick Insights | More chips + “Surprise me” + recent query chips | ✅ | `QuickInsights.tsx` – categories, Surprise me, `recentQueries` |
| 4 | Search & Quick Insights | Mic tip when speech supported | ✅ | `SearchPanel.tsx` – tip text when `speechSupported` |
| 5 | Navigation | Ask AI vs Stats tabs | ✅ | `App.tsx` – mode, tab buttons |
| 5 | Navigation | Logout in header user menu | ✅ | `Header.tsx` – user dropdown with Logout |
| 5 | Navigation | Breadcrumb “Stats → [Player]” | ✅ | `Header.tsx` – when `mode === 'stats'` and player selected |
| 5 | Navigation | Clear filters in sidebar | ✅ | `Sidebar.tsx` – Clear button, `handleClearFilters` |
| 6 | Loading & errors | “Analyzing tennis data…” message | ✅ | `App.tsx` – loading block |
| 6 | Loading & errors | 429: show countdown using `Retry-After` | ✅ | `useAiQuery.ts` – `retryAfterSeconds`; `App.tsx` – countdown + “You can try again now” |
| 7 | Mobile | Touch targets ≥ 44px (chips, buttons) | ✅ | `QuickInsights.tsx`, `Sidebar.tsx`, `Header.tsx`, `App.tsx` – `min-h-[44px]` |
| 8 | A11y | Skip to main content | ✅ | `Layout.tsx` – “Skip to main content” link |
| 8 | A11y | Focus to answer after submit | ✅ | `App.tsx` – `answerHeadingRef.current?.focus()` |
| 8 | A11y | `aria-live` on answer + error | ✅ | `AiResponseView.tsx` – `aria-live="polite"`; error card – `aria-live="assertive"` |
| 10 | Keyboard | `/` to focus search; Escape to clear/blur | ✅ | `App.tsx` – global `/`; `SearchPanel.tsx` – Escape |
| 11 | DataTable | Sticky header | ✅ | `DataTable.tsx` – `sticky top-0 z-10` on header row |

---

## Optional / Not implemented (by design or later phase)

- **Frontend:** Dedicated History page/drawer; search bar suggestions from history; Read out loud (TTS); rate limit countdown on **Login** (Login already shows 429 message with Retry-After text).
- **Backend:** Optional `X-RateLimit-*` headers on limiter; agent init check in `/ready` (only auth DB checked).

---

## How to re-verify

- **Backend:** `cd backend && python3 -m pytest tests/ -v`
- **Frontend:** `cd frontend && npm run build`
- **Manual:** Trigger 429 (e.g. exceed query rate limit), confirm `Retry-After` header and frontend countdown; confirm `/ready` returns 200 when DB is up.
