# Artifact Registry Setup - Quick Fix

## Error You're Seeing

```
name unknown: Repository "***" not found
```

This means the Artifact Registry repository doesn't exist yet in your GCP project.

## Quick Fix

Run these commands to create the Artifact Registry repository:

```bash
# 1. Set your project
gcloud config set project asktennis

# 2. Enable Artifact Registry API (if not already enabled)
gcloud services enable artifactregistry.googleapis.com

# 3. Create the Docker repository
gcloud artifacts repositories create asktennis \
  --repository-format=docker \
  --location=us-central1 \
  --description="AskTennis Docker images for Cloud Run"

# 4. Verify it was created
gcloud artifacts repositories list --location=us-central1
```

## Expected Output

After step 3, you should see:
```
Create request issued for: [asktennis]
Waiting for operation [projects/asktennis/locations/us-central1/operations/xxx] to complete...done.
Created repository [asktennis].
```

After step 4, you should see:
```
REPOSITORY  FORMAT  DESCRIPTION                          LOCATION      LABELS  ENCRYPTION
asktennis   DOCKER  AskTennis Docker images for Cloud Run  us-central1          Google-managed key
```

## Alternative: Using Cloud Console

If you prefer the web UI:

1. Go to: https://console.cloud.google.com/artifacts?project=asktennis
2. Click **"+ CREATE REPOSITORY"**
3. Fill in:
   - **Name**: `asktennis`
   - **Format**: Docker
   - **Location type**: Region
   - **Region**: `us-central1`
   - **Description**: AskTennis Docker images for Cloud Run
4. Click **CREATE**

## After Setup

Once the repository is created, re-run your GitHub Actions workflow:
- Go to GitHub Actions
- Click on the failed workflow run
- Click "Re-run all jobs"

The deployment should now succeed!

## Troubleshooting

**If you get "permission denied":**
```bash
# Make sure you're authenticated
gcloud auth login

# Set the project
gcloud config set project asktennis
```

**If the API isn't enabled:**
```bash
# Enable it explicitly
gcloud services enable artifactregistry.googleapis.com

# Wait a minute for it to propagate, then try creating the repository again
```
