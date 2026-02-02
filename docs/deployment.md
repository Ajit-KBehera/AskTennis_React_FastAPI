# GCP Cloud Run Deployment Guide

This guide walks you through deploying the AskTennis application to Google Cloud Platform using Cloud Run and automated CI/CD with GitHub Actions.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [GCP Project Setup](#gcp-project-setup)
3. [Service Account Configuration](#service-account-configuration)
4. [GitHub Secrets Configuration](#github-secrets-configuration)
5. [First Deployment](#first-deployment)
6. [Monitoring and Debugging](#monitoring-and-debugging)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before you begin, ensure you have:

- ✅ A Google Cloud Platform account with billing enabled
- ✅ `gcloud` CLI installed ([Installation Guide](https://cloud.google.com/sdk/docs/install))
- ✅ GitHub repository with admin access
- ✅ Cloud SQL PostgreSQL instance (already running at `asktennis:us-central1:asktennis-akb-nitr`)
- ✅ Google API Key for Gemini AI

---

## GCP Project Setup

### 1. Create or Select a GCP Project

```bash
# Create a new project (or use existing)
export PROJECT_ID="asktennis"
gcloud projects create $PROJECT_ID --name="AskTennis"

# Set as active project
gcloud config set project $PROJECT_ID

# Enable billing (must be done via console or API)
# Visit: https://console.cloud.google.com/billing/linkedaccount?project=$PROJECT_ID
```

### 2. Enable Required APIs

```bash
# Enable Cloud Run API
gcloud services enable run.googleapis.com

# Enable Artifact Registry API (for Docker images)
gcloud services enable artifactregistry.googleapis.com

# Enable Cloud SQL Admin API
gcloud services enable sqladmin.googleapis.com

# Enable Secret Manager API (for storing secrets)
gcloud services enable secretmanager.googleapis.com
```

### 3. Create Artifact Registry Repository

```bash
# Create a Docker repository in Artifact Registry
gcloud artifacts repositories create asktennis \
  --repository-format=docker \
  --location=us-central1 \
  --description="AskTennis Docker images"

# Verify creation
gcloud artifacts repositories list --location=us-central1
```

---

## Service Account Configuration

### 1. Create a Service Account for GitHub Actions

```bash
# Create service account
gcloud iam service-accounts create github-actions \
  --display-name="GitHub Actions Deployment" \
  --description="Service account for CI/CD deployments"

# Set the service account email
export SA_EMAIL="github-actions@${PROJECT_ID}.iam.gserviceaccount.com"
```

### 2. Grant Required Roles

```bash
# Cloud Run Admin (deploy and manage services)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/run.admin"

# Service Account User (run services as service account)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/iam.serviceAccountUser"

# Artifact Registry Writer (push Docker images)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/artifactregistry.writer"

# Secret Manager Secret Accessor (access secrets)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/secretmanager.secretAccessor"

# Cloud SQL Client (connect to database)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/cloudsql.client"
```

### 3. Generate Service Account Key

```bash
# Create and download JSON key
gcloud iam service-accounts keys create ~/gcp-key.json \
  --iam-account=${SA_EMAIL}

# Display the key (you'll need this for GitHub)
cat ~/gcp-key.json

# IMPORTANT: Store this securely and delete the local file after adding to GitHub
```

---

## Create Secrets in Google Cloud Secret Manager

Store sensitive values in Secret Manager instead of environment variables:

```bash
# Store Google API Key
echo -n "your-actual-google-api-key" | \
  gcloud secrets create GOOGLE_API_KEY --data-file=-

# Store API Secret Key
echo -n "your-actual-api-secret-key" | \
  gcloud secrets create API_SECRET_KEY --data-file=-

# Store Database Password
echo -n "your-actual-db-password" | \
  gcloud secrets create DB_PASSWORD --data-file=-

# Grant the Cloud Run service account access to secrets
# (You'll need to do this after first deployment, or use the github-actions SA)
gcloud secrets add-iam-policy-binding GOOGLE_API_KEY \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding API_SECRET_KEY \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding DB_PASSWORD \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/secretmanager.secretAccessor"
```

---

## GitHub Secrets Configuration

Add the following secrets to your GitHub repository:

**Settings → Secrets and variables → Actions → New repository secret**

### Required Secrets

| Secret Name | Value | Description |
|------------|-------|-------------|
| `GCP_PROJECT_ID` | `asktennis` | Your GCP project ID |
| `GCP_SA_KEY` | `<contents of gcp-key.json>` | Service account JSON key |
| `CLOUD_SQL_CONNECTION_NAME` | `asktennis:us-central1:asktennis-akb-nitr` | Cloud SQL connection string |
| `DB_NAME` | `tennis_data_with_mcp` | Database name |
| `DB_USER` | `your-db-username` | Database user |
| `GCP_SERVICE_ACCOUNT_EMAIL` | `github-actions@asktennis.iam.gserviceaccount.com` | Service account email |
| `BACKEND_URL` | (Set after first backend deployment) | Backend Cloud Run URL |

### Setting Secrets via GitHub CLI

```bash
# Install GitHub CLI if not already installed
# https://cli.github.com/

# Login to GitHub
gh auth login

# Navigate to your repository
cd /Users/ajitbehera/Codes/AskTennis_React_FastAPI

# Set secrets
gh secret set GCP_PROJECT_ID --body "asktennis"
gh secret set GCP_SA_KEY < ~/gcp-key.json
gh secret set CLOUD_SQL_CONNECTION_NAME --body "asktennis:us-central1:asktennis-akb-nitr"
gh secret set DB_NAME --body "tennis_data_with_mcp"
gh secret set DB_USER --body "your-db-username"
gh secret set GCP_SERVICE_ACCOUNT_EMAIL --body "${SA_EMAIL}"

# BACKEND_URL will be set after first deployment
```

---

## First Deployment

### Deploy Backend

1. **Trigger the deployment workflow:**

   ```bash
   # Option A: Manual trigger via GitHub UI
   # Go to: Actions → Deploy Backend to Cloud Run → Run workflow
   
   # Option B: Push to main branch
   git add .
   git commit -m "feat: add Cloud Run deployment"
   git push origin main
   ```

2. **Monitor the deployment:**
   - Go to GitHub Actions tab
   - Watch the "Deploy Backend to Cloud Run" workflow
   - Note the backend URL from the workflow output

3. **Update the BACKEND_URL secret:**

   ```bash
   # After backend deployment completes, get the URL
   # It will be shown in the GitHub Actions logs, something like:
   # https://asktennis-backend-xxxxx-uc.a.run.app
   
   gh secret set BACKEND_URL --body "https://asktennis-backend-xxxxx-uc.a.run.app"
   ```

### Deploy Frontend

1. **Trigger the frontend deployment:**

   ```bash
   # Option A: Manual trigger via GitHub UI
   # Go to: Actions → Deploy Frontend to Cloud Run → Run workflow
   
   # Option B: Make a change to frontend and push
   cd frontend
   # Make any change, then:
   git add .
   git commit -m "feat: trigger frontend deployment"
   git push origin main
   ```

2. **Access your application:**
   - Frontend URL will be shown in GitHub Actions logs
   - Visit the URL to access your application

### Update CORS Settings

After both services are deployed, you need to update the backend's CORS configuration:

1. **Update backend environment variables in Cloud Run:**

   ```bash
   # Get the frontend URL from the deployment logs
   export FRONTEND_URL="https://asktennis-frontend-xxxxx-uc.a.run.app"
   
   # Update the backend service
   gcloud run services update asktennis-backend \
     --region=us-central1 \
     --set-env-vars="ALLOWED_ORIGINS=${FRONTEND_URL}"
   ```

2. **Or redeploy the backend** after adding the frontend URL to your secrets.

---

## Monitoring and Debugging

### View Cloud Run Logs

```bash
# Backend logs
gcloud run services logs read asktennis-backend \
  --region=us-central1 \
  --limit=50

# Frontend logs
gcloud run services logs read asktennis-frontend \
  --region=us-central1 \
  --limit=50

# Stream logs in real-time
gcloud run services logs tail asktennis-backend --region=us-central1
```

### Check Service Health

```bash
# Get backend URL
gcloud run services describe asktennis-backend \
  --region=us-central1 \
  --format='value(status.url)'

# Test health endpoint
curl $(gcloud run services describe asktennis-backend \
  --region=us-central1 \
  --format='value(status.url)')/health
```

### View Service Details

```bash
# Backend service details
gcloud run services describe asktennis-backend --region=us-central1

# Frontend service details
gcloud run services describe asktennis-frontend --region=us-central1
```

### Cloud Console Monitoring

Visit the Cloud Run console:
```
https://console.cloud.google.com/run?project=asktennis
```

Key metrics to monitor:
- Request count
- Request latency
- Instance count
- Memory utilization
- CPU utilization
- Error rate

---

## Troubleshooting

### Common Issues

#### 1. **Cloud SQL Connection Errors**

**Error:** `Could not connect to Cloud SQL instance`

**Solution:**
```bash
# Verify Cloud SQL instance is running
gcloud sql instances describe asktennis-akb-nitr

# Ensure Public IP is enabled
gcloud sql instances patch asktennis-akb-nitr \
  --assign-ip

# Verify the Cloud Run service account has cloudsql.client role
gcloud projects add-iam-policy-binding asktennis \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/cloudsql.client"
```

#### 2. **Secret Access Denied**

**Error:** `Permission denied on secret`

**Solution:**
```bash
# Grant access to the secret
gcloud secrets add-iam-policy-binding GOOGLE_API_KEY \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/secretmanager.secretAccessor"
```

#### 3. **CORS Errors in Frontend**

**Error:** `Access to fetch at ... from origin ... has been blocked by CORS policy`

**Solution:**
Update backend's `ALLOWED_ORIGINS` environment variable:
```bash
gcloud run services update asktennis-backend \
  --region=us-central1 \
  --update-env-vars="ALLOWED_ORIGINS=https://your-frontend-url.a.run.app"
```

#### 4. **Container Fails to Start**

**Error:** `Container failed to start`

**Solution:**
- Check logs: `gcloud run services logs read asktennis-backend --limit=100`
- Verify Dockerfile builds locally: `docker build -t test ./backend`
- Check health endpoint is responding
- Ensure PORT environment variable is being used correctly

#### 5. **Build Timeouts**

**Error:** `Build timed out`

**Solution:**
- Increase timeout in GitHub Actions workflow
- Optimize Dockerfile layer caching
- Consider using Cloud Build instead of GitHub Actions for building

### Rollback to Previous Version

```bash
# List revisions
gcloud run revisions list --service=asktennis-backend --region=us-central1

# Rollback to a specific revision
gcloud run services update-traffic asktennis-backend \
  --region=us-central1 \
  --to-revisions=asktennis-backend-00001-abc=100
```

### Cost Optimization

1. **Set min instances to 0** (already configured) to scale to zero during idle
2. **Set appropriate memory/CPU** - backend uses 2Gi RAM, frontend uses 512Mi
3. **Monitor with budgets:**
   ```bash
   # Create a budget alert
   gcloud billing budgets create \
     --billing-account=YOUR_BILLING_ACCOUNT_ID \
     --display-name="Cloud Run Budget" \
     --budget-amount=50USD
   ```

---

## Next Steps

- [ ] Set up custom domain mapping
- [ ] Configure CDN for frontend
- [ ] Set up Cloud Armor for DDoS protection
- [ ] Implement CloudSQL Connection Pooling
- [ ] Set up Uptime checks and alerting
- [ ] Configure staging environment

---

## Useful Links

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Artifact Registry Documentation](https://cloud.google.com/artifact-registry/docs)
- [Cloud SQL Documentation](https://cloud.google.com/sql/docs)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GCP IAM Roles](https://cloud.google.com/iam/docs/understanding-roles)
