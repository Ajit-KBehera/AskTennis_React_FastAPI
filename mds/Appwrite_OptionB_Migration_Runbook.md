# Appwrite Option B Migration Runbook

This runbook targets a single Appwrite project with a big-bang cutover.

## 1) Pre-cutover configuration

### Frontend (Appwrite Sites)
- Root: `frontend`
- Install command: `npm ci`
- Build command: `npm run build`
- Output directory: `dist`
- Environment:
  - `VITE_API_URL=https://<appwrite-functions-base>/api`

### Backend (Appwrite Functions)
Deploy three function services from `backend` context:
- Auth: `functions/auth/main.py` (`uvicorn functions.auth.main:app`)
- Data: `functions/data/main.py` (`uvicorn functions.data.main:app`)
- Query: `functions/query/main.py` (`uvicorn functions.query.main:app`)

Required env vars for each function:
- `APPWRITE=true`
- `ENVIRONMENT=production`
- `JWT_SECRET_KEY`
- `GOOGLE_API_KEY` (query function required)
- `REDIS_URL` (required in production)
- Database env vars for your external DB
- `ALLOWED_ORIGINS=https://<your-appwrite-site-domain>`

## 2) Endpoint parity checklist

- Auth routes:
  - `GET /auth/check-username`
  - `POST /auth/register`
  - `POST /auth/login`
  - `GET /auth/me`
  - `POST /auth/logout`
- Data routes:
  - `GET /api/filters`
  - `POST /api/matches`
  - `POST /api/stats/serve`
  - `POST /api/stats/return`
  - `POST /api/stats/ranking`
- Query routes:
  - `POST /api/query`
  - `GET /api/query/history`

Behavior checks:
- All `/api/*` routes require `Authorization: Bearer <jwt>`.
- Login returns `access_token`, `token_type`, `expires_in`, `username`.
- Frontend persists token and sends it on each protected request.

## 3) Smoke test script (manual)

1. Register user.
2. Login and capture JWT.
3. Call `/auth/me` with `Authorization: Bearer`.
4. Call `/api/filters`.
5. Call `/api/stats/serve` with minimal valid payload.
6. Call `/api/matches`.
7. Call `/api/query` with simple query.
8. Call `/api/query/history`.
9. Logout.

## 4) Big-bang cutover sequence

1. Deploy all three backend functions.
2. Validate health endpoints and auth flow with direct URLs.
3. Update frontend `VITE_API_URL` to Appwrite function base.
4. Redeploy frontend site.
5. Run smoke test list against production domain.
6. Monitor logs/errors for 30-60 minutes.

## 5) Rollback

If severe regression occurs:
1. Repoint frontend `VITE_API_URL` to previous backend URL.
2. Redeploy frontend.
3. Keep Appwrite functions deployed for debugging.
4. Re-run parity checklist before next cutover attempt.
