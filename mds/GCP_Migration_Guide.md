# GCP Project & Billing Migration Guide — AskTennis

This guide walks through migrating the **AskTennis** application (FastAPI backend + React frontend on Cloud Run, Cloud SQL Postgres, Gemini API) from the current GCP project to a **new GCP Project with a new Billing Account**.

> Timeframe assumption: current project/billing expires in ~5 days. Plan for **~2–4 hours** end-to-end, with most time spent waiting for Cloud SQL provisioning and DB import.

---

## 0. What's currently deployed (reference)

From `.github/workflows/pipeline.yml` and `backend/app/infrastructure/database/cloud_sql_config.py`:

| Component | Current Value |
|---|---|
| Region | `us-central1` |
| Backend Cloud Run service | `asktennis-backend` (port 8000, 2 CPU / 2 Gi) |
| Frontend Cloud Run service | `asktennis-frontend` (port 80, 1 CPU / 512 Mi) |
| Artifact Registry repo | `asktennis` (Docker, `us-central1`) |
| Cloud SQL engine | PostgreSQL (pg8000 driver) |
| Cloud SQL databases | `tennis_data_with_mcp`, `asktennis_auth` |
| Secret Manager secrets | `GOOGLE_API_KEY`, `JWT_SECRET_KEY`, `DEFAULT_MODEL`, `TENNIS_DB_PASSWORD`, `AUTH_DB_PASSWORD` |
| GitHub Actions secrets | `GCP_SA_KEY`, `GCP_PROJECT_ID`, `CLOUD_SQL_CONNECTION_NAME`, `TENNIS_DB_NAME`, `TENNIS_DB_USER`, `AUTH_DB_NAME`, `AUTH_DB_USER`, `BACKEND_URL` |

---

## 1. Pre-migration — capture current state (do this FIRST, while old project still works)

Run these against the **OLD** project to gather values you'll need to recreate.

```bash
# Set the old project so you don't accidentally mutate it
export OLD_PROJECT_ID=<your-old-project-id>
gcloud config set project "$OLD_PROJECT_ID"
```

### 1.1 Record Cloud Run service configs

```bash
gcloud run services describe asktennis-backend  --region us-central1 --format=yaml > backend-old.yaml
gcloud run services describe asktennis-frontend --region us-central1 --format=yaml > frontend-old.yaml
```

Keep these as reference for env vars, memory/cpu, and concurrency.

### 1.2 Record Cloud SQL instance shape

```bash
gcloud sql instances list
gcloud sql instances describe <OLD_INSTANCE_NAME> --format=yaml > cloudsql-old.yaml
gcloud sql databases list --instance=<OLD_INSTANCE_NAME>
gcloud sql users list --instance=<OLD_INSTANCE_NAME>
```

Note: Postgres version, tier (e.g. `db-custom-1-3840`), region, zone, storage size, flags.

### 1.3 Back up Cloud SQL data (CRITICAL — blocks migration if skipped)

**Option A — Export to Cloud Storage (recommended):**

```bash
# Create a bucket in the OLD project to stage the dumps
gsutil mb -l us-central1 gs://$OLD_PROJECT_ID-sql-migration/

# Grant the Cloud SQL service account write access to the bucket
SA=$(gcloud sql instances describe <OLD_INSTANCE_NAME> --format="value(serviceAccountEmailAddress)")
gsutil iam ch serviceAccount:$SA:objectAdmin gs://$OLD_PROJECT_ID-sql-migration/

# Export each database as SQL dump
gcloud sql export sql <OLD_INSTANCE_NAME> \
  gs://$OLD_PROJECT_ID-sql-migration/tennis_data_with_mcp.sql.gz \
  --database=tennis_data_with_mcp

gcloud sql export sql <OLD_INSTANCE_NAME> \
  gs://$OLD_PROJECT_ID-sql-migration/asktennis_auth.sql.gz \
  --database=asktennis_auth
```

**Option B — Local `pg_dump` fallback** (if Cloud Storage export is restricted):

```bash
# In a separate terminal, run cloud-sql-proxy for the OLD instance
./cloud-sql-proxy <OLD_INSTANCE_CONNECTION_NAME> &

pg_dump -h 127.0.0.1 -U <user> -d tennis_data_with_mcp -Fc -f tennis_data_with_mcp.dump
pg_dump -h 127.0.0.1 -U <user> -d asktennis_auth       -Fc -f asktennis_auth.dump
```

### 1.4 Save all secret values

Dump the plaintext of every secret you will need to recreate. **Store these somewhere safe — do not commit.**

```bash
for s in GOOGLE_API_KEY JWT_SECRET_KEY DEFAULT_MODEL TENNIS_DB_PASSWORD AUTH_DB_PASSWORD; do
  echo "=== $s ==="
  gcloud secrets versions access latest --secret="$s"
  echo
done > secrets-old.txt
chmod 600 secrets-old.txt
```

> If you want to rotate the Gemini key (recommended), skip `GOOGLE_API_KEY` here — you'll mint a fresh one in step 4.

### 1.5 List Artifact Registry images (optional)

You will **rebuild** images in the new project via CI, so migration of images is optional. If you want a safety copy:

```bash
gcloud artifacts docker images list \
  us-central1-docker.pkg.dev/$OLD_PROJECT_ID/asktennis
```

---

## 2. Create the new GCP Project and link the new Billing Account

```bash
export NEW_PROJECT_ID=<your-new-project-id>            # e.g. asktennis-prod-2
export NEW_BILLING_ACCOUNT_ID=<XXXXXX-XXXXXX-XXXXXX>   # from `gcloud beta billing accounts list`
export REGION=us-central1

gcloud projects create "$NEW_PROJECT_ID" --name="AskTennis"
gcloud beta billing projects link "$NEW_PROJECT_ID" --billing-account="$NEW_BILLING_ACCOUNT_ID"
gcloud config set project "$NEW_PROJECT_ID"
```

Verify in the Console → Billing that the new billing account is attached.

---

## 3. Enable required APIs

```bash
gcloud services enable \
  run.googleapis.com \
  sqladmin.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  cloudbuild.googleapis.com \
  iam.googleapis.com \
  iamcredentials.googleapis.com \
  compute.googleapis.com \
  generativelanguage.googleapis.com \
  aiplatform.googleapis.com
```

`generativelanguage.googleapis.com` is required for the Gemini API key used by `langchain-google-genai`.

---

## 4. Create a new Gemini API key

The Gemini API key is **project-bound**. The old key will stop working when the old project is disabled.

1. Go to [Google AI Studio → API keys](https://aistudio.google.com/app/apikey).
2. Click **Create API key** → select the **new GCP project** (`$NEW_PROJECT_ID`).
3. Copy the key — you will store it as `GOOGLE_API_KEY` in Secret Manager in step 7.
4. (Optional) Restrict the key to the `generativelanguage.googleapis.com` API.

> Make sure "Generative Language API" is enabled in the new project (step 3 handles this).

---

## 5. Create the Artifact Registry repo

```bash
gcloud artifacts repositories create asktennis \
  --repository-format=docker \
  --location=$REGION \
  --description="AskTennis container images"
```

---

## 6. Provision Cloud SQL (Postgres) in the new project

### 6.1 Create the instance

Match or exceed the old instance's tier/size (use values from `cloudsql-old.yaml`).

```bash
gcloud sql instances create asktennis-db \
  --database-version=POSTGRES_15 \
  --tier=db-custom-1-3840 \
  --region=$REGION \
  --storage-size=10GB \
  --storage-auto-increase \
  --backup-start-time=03:00 \
  --enable-point-in-time-recovery
```

Record the connection name:

```bash
export NEW_INSTANCE_CONNECTION_NAME=$(gcloud sql instances describe asktennis-db \
  --format="value(connectionName)")
echo "$NEW_INSTANCE_CONNECTION_NAME"   # <project>:<region>:asktennis-db
```

### 6.2 Create databases and users

```bash
gcloud sql databases create tennis_data_with_mcp --instance=asktennis-db
gcloud sql databases create asktennis_auth       --instance=asktennis-db

# Pick strong passwords (reuse old or generate new — save them for step 7)
gcloud sql users create tennis_app --instance=asktennis-db --password='<TENNIS_DB_PASSWORD>'
gcloud sql users create auth_app   --instance=asktennis-db --password='<AUTH_DB_PASSWORD>'
```

> Adjust `tennis_app` / `auth_app` to match `TENNIS_DB_USER` / `AUTH_DB_USER` from the GitHub secrets you plan to set.

### 6.3 Import data into the new instance

**Option A — Import from the old bucket** (fastest):

```bash
# Copy the old dumps into a NEW-project bucket so the NEW instance's SA can read them
gsutil mb -l $REGION gs://$NEW_PROJECT_ID-sql-migration/
gsutil cp gs://$OLD_PROJECT_ID-sql-migration/*.sql.gz gs://$NEW_PROJECT_ID-sql-migration/

# Grant the NEW Cloud SQL service account read access
NEW_SA=$(gcloud sql instances describe asktennis-db --format="value(serviceAccountEmailAddress)")
gsutil iam ch serviceAccount:$NEW_SA:objectViewer gs://$NEW_PROJECT_ID-sql-migration/

# Import each DB
gcloud sql import sql asktennis-db \
  gs://$NEW_PROJECT_ID-sql-migration/tennis_data_with_mcp.sql.gz \
  --database=tennis_data_with_mcp

gcloud sql import sql asktennis-db \
  gs://$NEW_PROJECT_ID-sql-migration/asktennis_auth.sql.gz \
  --database=asktennis_auth
```

**Option B — Import local dumps via proxy:**

```bash
./cloud-sql-proxy $NEW_INSTANCE_CONNECTION_NAME &
pg_restore -h 127.0.0.1 -U tennis_app -d tennis_data_with_mcp tennis_data_with_mcp.dump
pg_restore -h 127.0.0.1 -U auth_app   -d asktennis_auth       asktennis_auth.dump
```

### 6.4 Grant schema ownership / privileges

After import, ensure the app users can read/write their DBs:

```bash
gcloud sql connect asktennis-db --user=postgres --database=tennis_data_with_mcp
# In psql:
# GRANT ALL ON SCHEMA public TO tennis_app;
# GRANT ALL ON ALL TABLES IN SCHEMA public TO tennis_app;
# GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO tennis_app;
# ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO tennis_app;
```

Repeat for `asktennis_auth` / `auth_app`.

---

## 7. Create secrets in Secret Manager

```bash
# For each secret, pipe the value from stdin (safer than passing on the command line)
printf '%s' "<NEW_GEMINI_API_KEY>"     | gcloud secrets create GOOGLE_API_KEY     --data-file=-
printf '%s' "<JWT_SECRET_KEY>"         | gcloud secrets create JWT_SECRET_KEY     --data-file=-
printf '%s' "openai/gpt-4o-mini"       | gcloud secrets create DEFAULT_MODEL      --data-file=-
printf '%s' "<TENNIS_DB_PASSWORD>"     | gcloud secrets create TENNIS_DB_PASSWORD --data-file=-
printf '%s' "<AUTH_DB_PASSWORD>"       | gcloud secrets create AUTH_DB_PASSWORD   --data-file=-
```

> Reuse `JWT_SECRET_KEY` from the old project **only if you want existing user JWT tokens to stay valid**. Otherwise rotate it (`openssl rand -hex 32`) — users will be silently logged out.

---

## 8. Create the CI/CD service account and grant IAM

The GitHub Actions workflow authenticates via `secrets.GCP_SA_KEY` (a service account JSON key).

```bash
export SA_NAME=github-deployer
export SA_EMAIL="${SA_NAME}@${NEW_PROJECT_ID}.iam.gserviceaccount.com"

gcloud iam service-accounts create $SA_NAME --display-name="GitHub Actions Deployer"

# Roles needed by the workflow
for role in \
  roles/run.admin \
  roles/artifactregistry.writer \
  roles/cloudsql.client \
  roles/secretmanager.secretAccessor \
  roles/iam.serviceAccountUser \
  roles/storage.admin
do
  gcloud projects add-iam-policy-binding $NEW_PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" --role="$role"
done

# Generate JSON key — paste into GitHub secret GCP_SA_KEY
gcloud iam service-accounts keys create gcp-sa-key.json --iam-account=$SA_EMAIL
```

### 8.1 Grant the Cloud Run runtime SA access to Cloud SQL + secrets

Cloud Run uses the project's default compute SA unless overridden. Grant it the minimum it needs:

```bash
PROJECT_NUMBER=$(gcloud projects describe $NEW_PROJECT_ID --format="value(projectNumber)")
RUNTIME_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

gcloud projects add-iam-policy-binding $NEW_PROJECT_ID \
  --member="serviceAccount:$RUNTIME_SA" --role="roles/cloudsql.client"

gcloud projects add-iam-policy-binding $NEW_PROJECT_ID \
  --member="serviceAccount:$RUNTIME_SA" --role="roles/secretmanager.secretAccessor"
```

> **Better**: create a dedicated runtime SA (e.g. `asktennis-run`) and pass `--service-account=...` to `gcloud run deploy`. Recommended for least-privilege.

---

## 9. Update GitHub repository secrets

In GitHub → **Settings → Secrets and variables → Actions**, update the following (overwrite existing values):

| Secret | New Value |
|---|---|
| `GCP_PROJECT_ID` | `$NEW_PROJECT_ID` |
| `GCP_SA_KEY` | contents of `gcp-sa-key.json` from step 8 |
| `CLOUD_SQL_CONNECTION_NAME` | `$NEW_INSTANCE_CONNECTION_NAME` (e.g. `new-proj:us-central1:asktennis-db`) |
| `TENNIS_DB_NAME` | `tennis_data_with_mcp` |
| `TENNIS_DB_USER` | `tennis_app` (match the user created in 6.2) |
| `AUTH_DB_NAME` | `asktennis_auth` |
| `AUTH_DB_USER` | `auth_app` (match the user created in 6.2) |
| `BACKEND_URL` | *leave placeholder — will update after first backend deploy in step 10.3* |

> **Delete** the local `gcp-sa-key.json` after pasting it into GitHub.

---

## 10. Deploy to the new project

### 10.1 Option A — Trigger CI/CD (recommended)

Push a trivial change (e.g. whitespace in `backend/main.py`) to `main`:

```bash
git commit --allow-empty -m "chore: trigger deploy to new GCP project"
git push origin main
```

The `deploy-backend` job will:
- build & push the backend image to `us-central1-docker.pkg.dev/$NEW_PROJECT_ID/asktennis/asktennis-backend`,
- deploy `asktennis-backend` on Cloud Run, wired to the new Cloud SQL instance & secrets.

### 10.2 Option A — Manual first deploy (fallback)

If the CI `changes` filter skips your branch, deploy manually once:

```bash
cd backend
IMAGE="us-central1-docker.pkg.dev/$NEW_PROJECT_ID/asktennis/asktennis-backend:manual"
gcloud auth configure-docker us-central1-docker.pkg.dev
docker build -t $IMAGE .
docker push $IMAGE

gcloud run deploy asktennis-backend \
  --image $IMAGE --region $REGION --platform managed --allow-unauthenticated \
  --cpu 2 --memory 2Gi --min-instances 0 --max-instances 10 --timeout 300 --port 8000 \
  --set-env-vars ENVIRONMENT=production,OTEL_SDK_DISABLED=true,ALLOW_ALL_ORIGINS=true,DB_TYPE=cloudsql \
  --set-env-vars INSTANCE_CONNECTION_NAME=$NEW_INSTANCE_CONNECTION_NAME \
  --set-env-vars TENNIS_DB_NAME=tennis_data_with_mcp,TENNIS_DB_USER=tennis_app \
  --set-env-vars AUTH_DB_NAME=asktennis_auth,AUTH_DB_USER=auth_app \
  --set-env-vars RATE_LIMIT_PER_MINUTE=30,QUERY_RATE_LIMIT_PER_MINUTE=10 \
  --set-secrets GOOGLE_API_KEY=GOOGLE_API_KEY:latest,JWT_SECRET_KEY=JWT_SECRET_KEY:latest,DEFAULT_MODEL=DEFAULT_MODEL:latest,TENNIS_DB_PASSWORD=TENNIS_DB_PASSWORD:latest,AUTH_DB_PASSWORD=AUTH_DB_PASSWORD:latest \
  --add-cloudsql-instances $NEW_INSTANCE_CONNECTION_NAME
```

### 10.3 Capture the new backend URL and update `BACKEND_URL`

```bash
gcloud run services describe asktennis-backend --region $REGION --format="value(status.url)"
# e.g. https://asktennis-backend-xxxxxx-uc.a.run.app
```

Update the GitHub secret **`BACKEND_URL`** to this value (no trailing slash). The frontend build bakes this into the bundle via `VITE_API_URL=$BACKEND_URL/api`.

### 10.4 Deploy the frontend

Trigger CI again (touch any file under `frontend/` and push), **or** manually:

```bash
cd frontend
BACKEND_URL="https://asktennis-backend-xxxxxx-uc.a.run.app"
IMAGE="us-central1-docker.pkg.dev/$NEW_PROJECT_ID/asktennis/asktennis-frontend:manual"
docker build --build-arg VITE_API_URL=$BACKEND_URL/api -t $IMAGE .
docker push $IMAGE

gcloud run deploy asktennis-frontend \
  --image $IMAGE --region $REGION --platform managed --allow-unauthenticated \
  --cpu 1 --memory 512Mi --min-instances 0 --max-instances 5 --timeout 60 --port 80 \
  --set-env-vars VITE_API_URL=$BACKEND_URL/api
```

---

## 11. Verify end-to-end

```bash
# Backend health
curl -s "$(gcloud run services describe asktennis-backend --region $REGION --format='value(status.url)')/health"

# Frontend
open "$(gcloud run services describe asktennis-frontend --region $REGION --format='value(status.url)')"
```

Checklist:
- [ ] `/health` returns OK.
- [ ] Login with an existing user works (confirms `asktennis_auth` import + `JWT_SECRET_KEY` OK).
- [ ] Ask a tennis question end-to-end (confirms `tennis_data_with_mcp` import + new Gemini key OK).
- [ ] Cloud Run logs (`gcloud run services logs read asktennis-backend --region $REGION`) show no DB / LLM errors.

---

## 12. DNS / custom domain (only if you had one)

If the old project had a Cloud Run domain mapping:

```bash
gcloud run domain-mappings create --service=asktennis-frontend --domain=<your-domain> --region=$REGION
```

Update your DNS provider's CNAME/A records to the new mapping targets shown by:

```bash
gcloud run domain-mappings describe --domain=<your-domain> --region=$REGION
```

Wait for TLS cert provisioning (can take up to ~60 min).

---

## 13. Decommission the old project

**Only after** the new deployment has been serving traffic successfully for at least 24 hours.

```bash
gcloud config set project $OLD_PROJECT_ID

# Stop Cloud Run services (fast, reversible)
gcloud run services update-traffic asktennis-backend  --region=us-central1 --to-revisions=LATEST=0
gcloud run services update-traffic asktennis-frontend --region=us-central1 --to-revisions=LATEST=0

# Final DB snapshot before destroying
gcloud sql backups create --instance=<OLD_INSTANCE_NAME> --description="pre-shutdown final"

# Delete (irreversible — do last)
gcloud sql instances delete <OLD_INSTANCE_NAME>
gcloud run services delete asktennis-backend  --region=us-central1
gcloud run services delete asktennis-frontend --region=us-central1
gcloud artifacts repositories delete asktennis --location=us-central1

# Unlink billing so you don't get charged if anything lingers
gcloud beta billing projects unlink $OLD_PROJECT_ID

# Optional: schedule project deletion (30-day grace period)
gcloud projects delete $OLD_PROJECT_ID
```

Revoke the **old** Gemini API key in AI Studio.

---

## 14. Rollback plan

If the new deployment has issues **and** the old project is still active:

1. In GitHub, revert the `BACKEND_URL`, `GCP_PROJECT_ID`, `CLOUD_SQL_CONNECTION_NAME`, and `GCP_SA_KEY` secrets to the old values.
2. Re-trigger the workflow on `main` (empty commit).
3. If you pointed a custom domain at the new service, re-map it to the old one.

> Because the migration does **not** modify the old project until step 13, rollback is essentially free before that point.

---

## Appendix A — Values cheat sheet (fill in before you start)

```
OLD_PROJECT_ID              = ______________________
NEW_PROJECT_ID              = ______________________
NEW_BILLING_ACCOUNT_ID      = ______________________
REGION                      = us-central1
OLD_INSTANCE_NAME           = ______________________
OLD_INSTANCE_CONNECTION     = ______________________
NEW_INSTANCE_CONNECTION     = ______________________   (set after step 6.1)
TENNIS_DB_USER              = tennis_app
AUTH_DB_USER                = auth_app
TENNIS_DB_PASSWORD          = ______________________
AUTH_DB_PASSWORD            = ______________________
JWT_SECRET_KEY              = (reuse old, or `openssl rand -hex 32`)
NEW_GEMINI_API_KEY          = ______________________   (from step 4)
BACKEND_URL (new)           = ______________________   (set after step 10.3)
```

## Appendix B — Common pitfalls

- **"connection refused" from Cloud Run to Cloud SQL** → forgot `--add-cloudsql-instances` or runtime SA missing `roles/cloudsql.client`.
- **`Secret not found`** → secret created in wrong project, or runtime SA missing `roles/secretmanager.secretAccessor`.
- **Gemini `PERMISSION_DENIED`** → `generativelanguage.googleapis.com` not enabled in new project, or API key still bound to old project.
- **Frontend calls `localhost` / wrong URL** → `BACKEND_URL` secret not updated before the frontend deploy; Vite bakes it at build time, not runtime.
- **`pg_restore` permission errors** → import as the `postgres` superuser, then `GRANT` to the app users (step 6.4).
- **CI skips deploy** → `dorny/paths-filter` didn't detect changes. Use `workflow_dispatch` (Run workflow button) or push an empty commit.
