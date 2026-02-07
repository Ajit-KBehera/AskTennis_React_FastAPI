# Backend improvements (optional)

Short list of improvements you can make to the AskTennis backend. None are blocking; the app is already in good shape.

**Status:** All items below have been implemented.

---

## 1. **429 rate limit: add `Retry-After`** ✅

**Why:** The frontend doc suggests showing “Try again in X seconds” with a countdown when the backend sends `Retry-After`.

**Current:** SlowAPI’s default `_rate_limit_exceeded_handler` returns 429 but does not set `Retry-After`.

**Change:** Register a custom exception handler for `RateLimitExceeded` that builds a JSON response and sets the `Retry-After` header (e.g. 60 seconds, or derive from the rate-window if SlowAPI exposes it). Optionally enable `headers_enabled` on the limiter so clients also get `X-RateLimit-*` headers.

**Where:** `backend/main.py` (replace or wrap the current handler), and possibly `backend/config/rate_limiter.py` if you need to pass retry-after logic.

---

## 2. **Query length limit** ✅

**Why:** Avoid very long payloads and abuse; keeps logs and DB history bounded.

**Current:** `QueryRequest.query` is only validated for non-empty/whitespace.

**Change:** In `api/routers/query.py`, add a `Field(..., max_length=2000)` (or similar) on `QueryRequest.query` and optionally a validator that strips/truncates or rejects over-length. Align with any DB column limit for `query_text` in query history.

**Where:** `backend/api/routers/query.py` – `QueryRequest`.

---

## 3. **Sanitize 500 error detail in production** ✅

**Why:** Avoid leaking stack traces or internal messages to clients.

**Current:** Several routes use `detail=str(e)` or `detail=f"Failed to ...: {str(e)}"` on 500 (e.g. query, matches, filters). That can expose internal details in production.

**Change:** In production (`ENVIRONMENT=production`), return a generic message (e.g. “An error occurred. Please try again.”) and log the real exception (you already use structlog). Optionally add a global exception handler for uncaught exceptions that does the same.

**Where:** `api/routers/query.py`, `api/routers/matches.py`, `api/routers/filters.py`, and optionally `main.py` for a global handler.

---

## 4. **Timeout for AI query processing** ✅

**Why:** Long-running or stuck agent calls can hold connections and confuse users.

**Current:** `query_processor.handle_user_query` calls `agent_graph.invoke()` with no timeout.

**Change:** Run the invoke inside a timeout (e.g. `asyncio.wait_for` with a wrapper, or a thread-pool call with a timeout). On timeout, return 504 or 503 with a clear message (“Query took too long. Try a simpler question or try again.”). Tune the limit (e.g. 60–120 seconds) via env.

**Where:** `backend/api/routers/query.py` (around `run_in_threadpool`) and/or `backend/services/query_service.py`.

---

## 5. **Health/readiness** ✅

**Why:** Load balancers and orchestrators often expect a health endpoint; “deep” checks help during deployments.

**Current:** `GET /health` returns a static `{"status": "healthy"}` with no dependency checks.

**Change (optional):**
- Keep `/health` as a cheap liveness check (current behavior).
- Add something like `GET /ready` that optionally checks DB connectivity (and maybe that the agent can be initialized) and returns 503 if not ready. Use this as the readiness probe in Cloud Run/K8s.

**Where:** `backend/main.py`, and optionally a small helper that pings the auth DB and/or the analytics DB.

---

## 6. **Auth: optional hardening** ✅

**Already in place:** Username/password length and JWT/cookie auth are in place. No urgent changes.

**Optional:**
- **Username format:** Restrict to a safe pattern (e.g. alphanumeric + underscore) in `UserBase` / `UserCreate` with a Pydantic validator.
- **Password strength:** No current strength rules; you could add a simple check (e.g. require a digit or symbol) in `auth_schemas` or in the register endpoint.
- **JWT secret:** Ensure `JWT_SECRET_KEY` is always set in production (e.g. fail startup if `ENVIRONMENT=production` and it’s missing or still the default).

**Where:** `backend/api/auth_schemas.py`, `backend/constants.py` or `config/auth.py`.

---

## 7. **Structured 500 response (optional)** ✅

**Why:** Consistent JSON shape for errors makes frontend handling easier.

**Current:** FastAPI already returns JSON for `HTTPException`. Uncaught exceptions may return a different shape.

**Change:** Add a global exception handler that catches unhandled exceptions and returns a JSON body like `{"detail": "An error occurred. Please try again."}` (with sanitized message in production) and status 500, and log the real error. Keeps behavior consistent with your existing `HTTPException` usage.

**Where:** `backend/main.py`.

---

## Summary

| Item                         | Impact        | Effort |
|-----------------------------|---------------|--------|
| 429 Retry-After             | UX (countdown)| Low    |
| Query max length            | Safety/abuse  | Low    |
| Sanitize 500 in production  | Security      | Low    |
| Query timeout               | Reliability   | Medium |
| Health/readiness            | Ops           | Low    |
| Auth hardening (optional)   | Security      | Low    |
| Global 500 handler          | Consistency   | Low    |

Implement in the order above if you want quick wins first; 1–3 and 7 are small changes.
