# Cloud Run Deployment - Quick Reference

## Prerequisites Checklist

- [ ] GCP project created with billing enabled
- [ ] Cloud SQL instance running: `asktennis:us-central1:asktennis-akb-nitr`
- [ ] Service account created with proper roles
- [ ] Service account JSON key downloaded
- [ ] GitHub repository secrets configured

## Required GitHub Secrets

```bash
# Set these in GitHub Settings → Secrets → Actions
GCP_PROJECT_ID=asktennis
GCP_SA_KEY=<service-account-json-content>
CLOUD_SQL_CONNECTION_NAME=asktennis:us-central1:asktennis-akb-nitr
DB_NAME=tennis_data_with_mcp
DB_USER=<your-db-user>
GCP_SERVICE_ACCOUNT_EMAIL=github-actions@asktennis.iam.gserviceaccount.com
BACKEND_URL=<set-after-first-backend-deployment>
```

## Required GCP Secrets (Secret Manager)

```bash
# Create these in Google Cloud Secret Manager
GOOGLE_API_KEY=<your-google-api-key>
API_SECRET_KEY=<your-api-secret-key>
DB_PASSWORD=<your-db-password>
```

## Quick Setup Commands

### 1. Enable APIs

```bash
gcloud config set project asktennis
gcloud services enable run.googleapis.com artifactregistry.googleapis.com secretmanager.googleapis.com
```

### 2. Create Artifact Registry

```bash
gcloud artifacts repositories create asktennis \
  --repository-format=docker \
  --location=us-central1
```

### 3. Create Service Account

```bash
gcloud iam service-accounts create github-actions
export SA_EMAIL="github-actions@asktennis.iam.gserviceaccount.com"

# Grant roles
for role in run.admin iam.serviceAccountUser artifactregistry.writer secretmanager.secretAccessor cloudsql.client; do
  gcloud projects add-iam-policy-binding asktennis \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/${role}"
done

# Create key
gcloud iam service-accounts keys create ~/gcp-key.json --iam-account=${SA_EMAIL}
```

### 4. Create GCP Secrets

```bash
echo -n "YOUR_GOOGLE_API_KEY" | gcloud secrets create GOOGLE_API_KEY --data-file=-
echo -n "YOUR_API_SECRET_KEY" | gcloud secrets create API_SECRET_KEY --data-file=-
echo -n "YOUR_DB_PASSWORD" | gcloud secrets create DB_PASSWORD --data-file=-

# Grant access
for secret in GOOGLE_API_KEY API_SECRET_KEY DB_PASSWORD; do
  gcloud secrets add-iam-policy-binding $secret \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/secretmanager.secretAccessor"
done
```

### 5. Set GitHub Secrets

```bash
gh secret set GCP_PROJECT_ID --body "asktennis"
gh secret set GCP_SA_KEY < ~/gcp-key.json
gh secret set CLOUD_SQL_CONNECTION_NAME --body "asktennis:us-central1:asktennis-akb-nitr"
gh secret set DB_NAME --body "tennis_data_with_mcp"
gh secret set DB_USER --body "YOUR_DB_USER"
gh secret set GCP_SERVICE_ACCOUNT_EMAIL --body "${SA_EMAIL}"
```

## Deployment

### Automatic (via GitHub Actions)

```bash
# Simply push to main branch
git push origin main

# Or manually trigger workflow
# GitHub → Actions → "Deploy Backend to Cloud Run" → Run workflow
```

### Manual (via gcloud)

```bash
# Backend
cd backend
gcloud run deploy asktennis-backend \
  --source . \
  --region=us-central1 \
  --allow-unauthenticated

# Frontend
cd frontend
gcloud run deploy asktennis-frontend \
  --source . \
  --region=us-central1 \
  --allow-unauthenticated
```

## Quick Commands

### View Logs

```bash
# Backend logs (last 50 lines)
gcloud run services logs read asktennis-backend --region=us-central1 --limit=50

# Frontend logs
gcloud run services logs read asktennis-frontend --region=us-central1 --limit=50

# Stream logs
gcloud run services logs tail asktennis-backend --region=us-central1
```

### Get Service URLs

```bash
# Backend URL
gcloud run services describe asktennis-backend --region=us-central1 --format='value(status.url)'

# Frontend URL
gcloud run services describe asktennis-frontend --region=us-central1 --format='value(status.url)'
```

### Health Check

```bash
BACKEND_URL=$(gcloud run services describe asktennis-backend --region=us-central1 --format='value(status.url)')
curl $BACKEND_URL/health
```

### Update Environment Variables

```bash
# Update backend CORS
gcloud run services update asktennis-backend \
  --region=us-central1 \
  --update-env-vars="ALLOWED_ORIGINS=https://your-frontend-url.a.run.app"
```

### Rollback

```bash
# List revisions
gcloud run revisions list --service=asktennis-backend --region=us-central1

# Rollback to previous
gcloud run services update-traffic asktennis-backend \
  --region=us-central1 \
  --to-revisions=REVISION_NAME=100
```

## Troubleshooting

### Check Service Status

```bash
gcloud run services describe asktennis-backend --region=us-central1
```

### Test Database Connection

```bash
# From Cloud Shell or local machine with gcloud auth
gcloud sql connect asktennis-akb-nitr --user=YOUR_USER --database=tennis_data_with_mcp
```

### Debug Container Issues

```bash
# Build locally to test
cd backend
docker build -t test-backend .
docker run -p 8000:8000 -e PORT=8000 test-backend

# Check health
curl localhost:8000/health
```

## Important Files

- `.github/workflows/deploy-backend.yml` - Backend deployment workflow
- `.github/workflows/deploy-frontend.yml` - Frontend deployment workflow
- `backend/Dockerfile` - Backend container definition
- `frontend/Dockerfile` - Frontend container definition
- `docs/deployment.md` - Full deployment guide

## Support

For detailed instructions, see [`docs/deployment.md`](deployment.md)
