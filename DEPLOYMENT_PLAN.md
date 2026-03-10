# DIT 2026 Assessment -- Cloud Run Deployment Plan

## Purpose

This document provides a complete, actionable plan for deploying the DIT 2026 Assessment Flask app to Google Cloud Run behind `aiskillsmap.noahratzan.com`, with CI/CD automation via GitHub Actions.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Subdomain Strategy & DNS](#2-subdomain-strategy--dns)
3. [Cloud Run Service Configuration](#3-cloud-run-service-configuration)
4. [Docker Strategy](#4-docker-strategy)
5. [Secret Management](#5-secret-management)
6. [CI/CD Pipeline](#6-cicd-pipeline)
7. [SSL/TLS & Domain Mapping](#7-ssltls--domain-mapping)
8. [Cost Estimation](#8-cost-estimation)
9. [CORS Considerations](#9-cors-considerations)
10. [Monitoring & Logging](#10-monitoring--logging)
11. [Implementation Checklist](#11-implementation-checklist)

---

## 1. Architecture Overview

```
                    DNS (CNAME)
aiskillsmap.noahratzan.com ──────────────> Cloud Run (ghs.googlehosted.com)
                                       |
                                       v
                               ┌───────────────────┐
                               │  Cloud Run Service │
                               │  dit-assessment    │
                               │  us-central1       │
                               │                    │
                               │  ┌──────────────┐  │
                               │  │ Container     │  │
                               │  │ python:3.12   │  │
                               │  │ gunicorn      │  │
                               │  │ Flask app     │  │
                               │  │ numpy/sklearn │  │
                               │  │ embeddings    │  │
                               │  └──────────────┘  │
                               └────────┬───────────┘
                                        │
                             Outbound API calls
                                        │
                     ┌──────────────────┼──────────────────┐
                     v                  v                   v
               OpenAI API        Anthropic API       Google AI API


noahratzan.com ───────────────> Vercel (unchanged)
```

**Key design decisions:**

- **Cloud Run direct domain mapping** (not a load balancer). The app is a single service with no path-based routing needs. Cloud Run's built-in domain mapping provides free managed SSL and is simpler to configure.
- **No load balancer required.** A load balancer adds ~$18/month minimum cost and operational complexity. It would only be justified if you needed CDN, Cloud Armor WAF, or path-based routing to multiple backends.
- **Artifact Registry** for container image storage. Cloud Build (triggered by GitHub Actions) pushes images there.
- **GCP Secret Manager** for API keys. Avoids storing secrets in Cloud Run environment variables or GitHub Secrets beyond the GCP service account credential.

---

## 2. Subdomain Strategy & DNS

### Recommended Subdomain

**`aiskillsmap.noahratzan.com`**

Rationale: Short, memorable, matches the project name. `assessment.noahratzan.com` is an alternative but longer.

### DNS Configuration

You will need to add a CNAME record at your domain registrar (or wherever DNS for `noahratzan.com` is managed).

**Step 1: Determine where DNS is managed.**

If your domain is registered through a registrar like Namecheap, Google Domains, or Cloudflare but uses Vercel's nameservers, DNS is managed in Vercel. If you use the registrar's nameservers, DNS is managed at the registrar.

Check this:
- Vercel Dashboard > your project > Settings > Domains. If `noahratzan.com` shows a DNS configuration, Vercel controls DNS.
- Alternatively, run: `nslookup -type=NS noahratzan.com` to see which nameservers are authoritative.

**Step 2: Add the CNAME record.**

| Type  | Name | Value                    | TTL  |
|-------|------|--------------------------|------|
| CNAME | dit  | ghs.googlehosted.com.    | 3600 |

This record is created after you configure domain mapping in Cloud Run (Step 7). Cloud Run will tell you the exact target to point to.

**Important:** Adding a subdomain CNAME does not affect the main `noahratzan.com` A/AAAA records pointing to Vercel. They are independent DNS records.

---

## 3. Cloud Run Service Configuration

### Service Specification

| Setting               | Value                    | Rationale                                                |
|-----------------------|--------------------------|----------------------------------------------------------|
| Service name          | `dit-assessment`         | Descriptive, matches project                             |
| Region                | `us-central1`            | Lowest cost, largest free tier, close to OpenAI servers   |
| CPU                   | 1 vCPU                   | Sufficient for gunicorn + numpy/sklearn cosine similarity |
| Memory                | 512 MiB                  | Embeddings ~762KB + numpy overhead + Flask + sklearn      |
| Min instances         | 0                        | Cost optimization -- scale to zero when idle              |
| Max instances         | 3                        | Prevents runaway costs; low-traffic app                   |
| Concurrency           | 80 (default)             | gunicorn 2 workers x 4 threads = 8 concurrent requests   |
| Request timeout       | 300 seconds               | LLM API calls can be slow                                |
| CPU allocation        | Request-based             | CPU throttled when idle -- cheapest option                |
| Startup CPU boost     | Enabled                  | Temporarily doubles CPU during cold start (free)          |
| Ingress               | All traffic               | Public-facing web app                                    |
| Authentication        | Allow unauthenticated     | Public web app, no auth required                         |

### Cold Start Analysis

**What happens on cold start:**
1. Container image pull (cached by Cloud Run after first pull)
2. Python interpreter startup
3. `numpy` import (~200ms)
4. `sklearn` import (~400ms)
5. `np.load("embeddings.npy")` -- 762KB file, ~50ms
6. `TfidfVectorizer.fit_transform()` on 62 chunks -- ~100ms
7. LLM provider registry initialization -- ~50ms

**Estimated cold start time: 2-4 seconds**

This is acceptable for a low-traffic app. Optimizations:

- **Startup CPU boost** (enabled above) temporarily provides 2x CPU, cutting import time roughly in half.
- **Min instances = 0** keeps costs at zero when idle. If cold starts become a problem, set `min-instances=1` (~$5-8/month additional).
- The existing Dockerfile already uses `python:3.12-slim`, which is the right choice.

### Concurrency Tuning

The gunicorn config in the Dockerfile uses `--workers 2 --threads 4`. This means 8 concurrent Python threads per container. Cloud Run's default concurrency of 80 is higher than the app can actually serve, but Cloud Run will scale out additional instances when the 8 threads are saturated. Consider setting:

```
--concurrency 10
```

This tells Cloud Run to send at most 10 concurrent requests per instance, which better matches the gunicorn thread pool (8 threads + 2 buffer).

---

## 4. Docker Strategy

### Existing Dockerfile Assessment

The existing `Dockerfile` at the repo root is well-structured and production-ready. It uses:

- Multi-stage build (builder stage for gcc/g++ compilation, slim runtime image)
- `python:3.12-slim` base image
- Non-root user (`appuser`)
- Correct `COPY` for both `assessment/` and `v-0.0.1/` source content
- Appropriate gunicorn configuration

### Recommended Changes

**4.1. Add a `.dockerignore` file** to exclude unnecessary files:

```dockerignore
# .dockerignore (place in repo root, next to Dockerfile)
.git
.gitignore
*.md
!v-0.0.1/*.md
.env
.env.*
__pycache__
*.pyc
.pytest_cache
.vscode
.idea
assets/
render.yaml
DEPLOYMENT_PLAN.md
```

Note: `v-0.0.1/*.md` files must NOT be ignored -- they are the framework content served at runtime.

**4.2. Pin dependency versions** in `requirements.txt` for reproducible builds. Run locally to capture current versions:

```bash
cd assessment
pip freeze > requirements-lock.txt
```

Then reference `requirements-lock.txt` in the Dockerfile instead of `requirements.txt`.

**4.3. Health check endpoint.** Add a simple health check to `app.py` for Cloud Run's startup probe:

```python
@app.route('/healthz')
def health():
    return 'ok', 200
```

Then configure Cloud Run's startup probe:

```
--startup-probe httpGet.path=/healthz
```

### Image Size Estimate

| Layer                      | Approx. Size |
|----------------------------|-------------|
| python:3.12-slim base      | ~130 MB     |
| numpy + sklearn + deps     | ~120 MB     |
| openai + anthropic + etc   | ~40 MB      |
| Application code + embeds  | ~5 MB       |
| **Total**                  | **~295 MB** |

This is a reasonable image size. No further optimization needed.

---

## 5. Secret Management

### Recommended: GCP Secret Manager

Use GCP Secret Manager for API keys. This is more secure than Cloud Run plain-text environment variables (which are visible in the GCP Console and API).

**Step 1: Create secrets.**

```bash
# Create each secret in GCP
echo -n "your-flask-secret-key" | \
  gcloud secrets create dit-secret-key --data-file=-

echo -n "sk-..." | \
  gcloud secrets create dit-openai-api-key --data-file=-

echo -n "sk-ant-..." | \
  gcloud secrets create dit-anthropic-api-key --data-file=-

echo -n "AI..." | \
  gcloud secrets create dit-google-api-key --data-file=-
```

**Step 2: Grant the Cloud Run service account access.**

```bash
PROJECT_NUMBER=$(gcloud projects describe $(gcloud config get-value project) --format='value(projectNumber)')

for secret in dit-secret-key dit-openai-api-key dit-anthropic-api-key dit-google-api-key; do
  gcloud secrets add-iam-policy-binding $secret \
    --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
done
```

**Step 3: Mount secrets as environment variables in Cloud Run.**

```bash
gcloud run deploy dit-assessment \
  --set-secrets="SECRET_KEY=dit-secret-key:latest,OPENAI_API_KEY=dit-openai-api-key:latest,ANTHROPIC_API_KEY=dit-anthropic-api-key:latest,GOOGLE_API_KEY=dit-google-api-key:latest"
```

### Runtime Key Setting via UI

The app has an `/api/keys` POST endpoint that allows setting API keys at runtime via the browser UI. These keys live only in the process environment and are lost when the container scales down. This is a useful feature for demos but should not be relied upon in production. The Secret Manager keys will be the baseline.

### Security Note on /api/keys

The `/api/keys` POST endpoint has no authentication. Anyone who discovers the URL can set arbitrary API keys. For a public deployment, consider either:

1. Removing the endpoint entirely, OR
2. Protecting it with a simple shared secret header check, OR
3. Accepting the risk since the worst case is someone sets their own API key (which they pay for)

This is a low-severity concern for a low-traffic demo app but worth noting.

---

## 6. CI/CD Pipeline

### Recommended: GitHub Actions with Workload Identity Federation

Workload Identity Federation (WIF) is the modern approach -- no long-lived service account key JSON files stored in GitHub Secrets.

### Prerequisites

```bash
# Set variables
PROJECT_ID="your-gcp-project-id"
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
REGION="us-central1"
REPO_OWNER="your-github-username"
REPO_NAME="dit-2026"

# Enable required APIs
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com \
  iamcredentials.googleapis.com

# Create Artifact Registry repository
gcloud artifacts repositories create dit-2026 \
  --repository-format=docker \
  --location=$REGION \
  --description="DIT 2026 Assessment container images"

# Create a service account for GitHub Actions
gcloud iam service-accounts create github-actions-dit \
  --display-name="GitHub Actions - DIT 2026"

SA_EMAIL="github-actions-dit@${PROJECT_ID}.iam.gserviceaccount.com"

# Grant required roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/iam.serviceAccountUser"

# Create Workload Identity Pool
gcloud iam workload-identity-pools create github-pool \
  --location="global" \
  --display-name="GitHub Actions Pool"

gcloud iam workload-identity-pools providers create-oidc github-provider \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --display-name="GitHub Provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
  --issuer-uri="https://token.actions.githubusercontent.com"

# Allow the GitHub repo to impersonate the service account
POOL_ID=$(gcloud iam workload-identity-pools describe github-pool \
  --location="global" --format='value(name)')

gcloud iam service-accounts add-iam-policy-binding $SA_EMAIL \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/${POOL_ID}/attribute.repository/${REPO_OWNER}/${REPO_NAME}"
```

### GitHub Actions Workflow

Create `.github/workflows/deploy.yaml`:

```yaml
name: Deploy to Cloud Run

on:
  push:
    branches: [main]
    paths:
      - 'assessment/**'
      - 'v-0.0.1/**'
      - 'Dockerfile'
      - '.github/workflows/deploy.yaml'

env:
  PROJECT_ID: your-gcp-project-id        # REPLACE
  REGION: us-central1
  SERVICE: dit-assessment
  REPOSITORY: dit-2026
  IMAGE: us-central1-docker.pkg.dev/${{ env.PROJECT_ID }}/dit-2026/dit-assessment

permissions:
  contents: read
  id-token: write  # Required for Workload Identity Federation

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Authenticate to Google Cloud
        uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/providers/github-provider  # REPLACE PROJECT_NUMBER
          service_account: github-actions-dit@your-gcp-project-id.iam.gserviceaccount.com  # REPLACE

      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v2

      - name: Configure Docker for Artifact Registry
        run: gcloud auth configure-docker us-central1-docker.pkg.dev --quiet

      - name: Build and push container image
        run: |
          IMAGE_TAG="us-central1-docker.pkg.dev/${{ env.PROJECT_ID }}/${{ env.REPOSITORY }}/${{ env.SERVICE }}:${{ github.sha }}"
          docker build -t $IMAGE_TAG .
          docker push $IMAGE_TAG

      - name: Deploy to Cloud Run
        run: |
          IMAGE_TAG="us-central1-docker.pkg.dev/${{ env.PROJECT_ID }}/${{ env.REPOSITORY }}/${{ env.SERVICE }}:${{ github.sha }}"
          gcloud run deploy ${{ env.SERVICE }} \
            --image=$IMAGE_TAG \
            --region=${{ env.REGION }} \
            --platform=managed \
            --allow-unauthenticated \
            --memory=512Mi \
            --cpu=1 \
            --min-instances=0 \
            --max-instances=3 \
            --concurrency=10 \
            --timeout=300 \
            --cpu-boost \
            --set-secrets="SECRET_KEY=dit-secret-key:latest,OPENAI_API_KEY=dit-openai-api-key:latest,ANTHROPIC_API_KEY=dit-anthropic-api-key:latest,GOOGLE_API_KEY=dit-google-api-key:latest" \
            --set-env-vars="DEBUG=false"

      - name: Show deployed URL
        run: |
          gcloud run services describe ${{ env.SERVICE }} \
            --region=${{ env.REGION }} \
            --format='value(status.url)'
```

### Key CI/CD Design Decisions

1. **Path-filtered triggers**: Only rebuilds when `assessment/`, `v-0.0.1/`, or `Dockerfile` change. Changes to `README.md` or `assets/` do not trigger a deploy.
2. **Workload Identity Federation**: No long-lived JSON key files. GitHub's OIDC token is exchanged for short-lived GCP credentials.
3. **Image tagged with commit SHA**: Every deploy is traceable to a specific commit. Easy rollback via `gcloud run deploy --image=...:<previous-sha>`.
4. **Artifact Registry** (not Container Registry, which is deprecated).

---

## 7. SSL/TLS & Domain Mapping

### Cloud Run Domain Mapping (Recommended)

Cloud Run provides free Google-managed SSL certificates for custom domains. No load balancer needed.

**Step 1: Verify domain ownership.**

```bash
# This opens a browser for domain verification via Google Search Console
gcloud domains verify noahratzan.com
```

Alternatively, add a TXT record to your DNS to prove ownership.

**Step 2: Create the domain mapping.**

```bash
gcloud run domain-mappings create \
  --service=dit-assessment \
  --domain=aiskillsmap.noahratzan.com \
  --region=us-central1
```

**Step 3: Add DNS records.**

Cloud Run will output the required DNS records. Typically:

| Type  | Name | Value                  |
|-------|------|------------------------|
| CNAME | dit  | ghs.googlehosted.com.  |

Add this CNAME record in your DNS provider (Vercel, registrar, or Cloudflare).

**Step 4: Wait for SSL provisioning.**

SSL certificate provisioning usually takes 15-30 minutes but can take up to 24 hours. During this time, `aiskillsmap.noahratzan.com` will show a certificate error. Once provisioned, Cloud Run auto-renews the certificate.

Check status:

```bash
gcloud run domain-mappings describe \
  --domain=aiskillsmap.noahratzan.com \
  --region=us-central1
```

### Why Not a Load Balancer

A Global External Application Load Balancer would provide:
- Cloud CDN (not needed -- the app serves dynamic content)
- Cloud Armor WAF (overkill for a low-traffic demo)
- Path-based routing (not needed -- single service)
- Custom SSL certificates (not needed -- Google-managed is fine)

A load balancer costs ~$18/month minimum (forwarding rule) plus data processing charges. Not justified for this use case.

---

## 8. Cost Estimation

### Monthly Cost for Low-Traffic Usage (< 100 users/month)

| Component                      | Estimated Usage        | Cost       |
|-------------------------------|------------------------|------------|
| **Cloud Run -- CPU**          | ~5,000 vCPU-seconds    | Free tier  |
| **Cloud Run -- Memory**       | ~10,000 GiB-seconds    | Free tier  |
| **Cloud Run -- Requests**     | ~5,000 requests        | Free tier  |
| **Artifact Registry storage** | ~300 MB (1-2 images)   | Free tier  |
| **Secret Manager**            | 4 secrets, ~100 access | Free tier  |
| **Egress (networking)**       | < 1 GiB               | Free tier  |
| **Domain mapping / SSL**      | --                     | Free       |
| **Total**                     |                        | **$0/mo**  |

### Free Tier Limits (for reference)

| Resource           | Free Tier Monthly Allowance |
|--------------------|-----------------------------|
| CPU                | 180,000 vCPU-seconds         |
| Memory             | 360,000 GiB-seconds          |
| Requests           | 2,000,000                    |
| Artifact Registry  | 0.5 GB storage               |
| Secret Manager     | 6 active secret versions     |
| Egress             | 1 GiB (North America)        |

### Scaling Scenarios

| Scenario                          | Estimated Monthly Cost |
|-----------------------------------|------------------------|
| Very low traffic (< 100 users)    | $0 (free tier)         |
| Light traffic (100-500 users)     | $0-2                   |
| Moderate traffic (500-2000 users) | $2-10                  |
| With min-instances=1 (warm)       | +$5-8/month            |

### Cost Controls

Set a budget alert to avoid surprises:

```bash
# Set max instances to 3 (already configured)
# Set a billing budget alert at $10/month
gcloud billing budgets create \
  --billing-account=BILLING_ACCOUNT_ID \
  --display-name="DIT Assessment" \
  --budget-amount=10 \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=90 \
  --threshold-rule=percent=100
```

---

## 9. CORS Considerations

### Current Assessment

The Flask app at `aiskillsmap.noahratzan.com` and the portfolio at `noahratzan.com` are different origins. CORS is only relevant if `noahratzan.com` makes client-side JavaScript `fetch()` calls to `aiskillsmap.noahratzan.com`.

**Current state:** The Flask app is a standalone web application with its own HTML pages, JavaScript, and CSS. Users navigate directly to `aiskillsmap.noahratzan.com`. The portfolio site (`noahratzan.com`) would link to it but not embed it or make API calls to it.

**Verdict: No CORS configuration is needed** for the initial deployment. The two sites are independent.

### If CORS Is Needed Later

If you later want `noahratzan.com` to make API calls to `aiskillsmap.noahratzan.com` (e.g., embedding the chat widget), add Flask-CORS:

```python
# In requirements.txt, add: flask-cors
# In app.py:
from flask_cors import CORS

def create_app():
    app = Flask(...)
    CORS(app, origins=["https://noahratzan.com"])
    ...
```

### Embedding via iframe

If you want to embed the assessment on the portfolio site via an iframe, no CORS is needed (iframes are not subject to CORS). Just add a link or iframe on the Vercel site:

```html
<iframe src="https://aiskillsmap.noahratzan.com" width="100%" height="800"></iframe>
```

Or simply link to it: `<a href="https://aiskillsmap.noahratzan.com">Take the DIT Assessment</a>`.

---

## 10. Monitoring & Logging

### Built-in Cloud Run Monitoring

Cloud Run automatically provides:

- **Request logs** (stdout/stderr from gunicorn `--access-logfile -` and `--error-logfile -`)
- **Container lifecycle events** (start, stop, scale-up, scale-down)
- **Metrics** in Cloud Console: request count, latency (p50/p95/p99), container instance count, CPU/memory utilization
- **Error Reporting** (automatic for uncaught exceptions)

### Recommended Alerting

Set up basic alerts in Cloud Monitoring:

```bash
# Alert on high error rate (> 5% of requests returning 5xx)
gcloud monitoring policies create \
  --display-name="DIT Assessment - High Error Rate" \
  --condition-display-name="5xx error rate > 5%" \
  --condition-filter='resource.type="cloud_run_revision" AND metric.type="run.googleapis.com/request_count" AND metric.label.response_code_class="5xx"'
```

Or configure alerts through the Cloud Console UI:
1. Go to Cloud Monitoring > Alerting > Create Policy
2. Add condition: Cloud Run Revision > Request Count > Filter by 5xx
3. Set notification channel (email)

### Log-based Metrics

Cloud Run logs are automatically available in Cloud Logging. Useful queries:

```
# View all requests to the service
resource.type="cloud_run_revision"
resource.labels.service_name="dit-assessment"

# View errors only
resource.type="cloud_run_revision"
resource.labels.service_name="dit-assessment"
severity>=ERROR

# View cold starts
resource.type="cloud_run_revision"
resource.labels.service_name="dit-assessment"
textPayload:"SearchEngine loaded"
```

### Application-level Logging

The app already logs via `print()` statements (e.g., `SearchEngine loaded 62 chunks`). These appear in Cloud Logging automatically because gunicorn forwards stdout/stderr.

For structured logging (optional improvement), add:

```python
import json
import sys

def log_json(severity, message, **kwargs):
    entry = {"severity": severity, "message": message, **kwargs}
    print(json.dumps(entry), file=sys.stderr)
```

This enables log-based queries on structured fields.

---

## 11. Implementation Checklist

### Phase 1: GCP Project Setup (One-time, ~30 minutes)

- [ ] Create a GCP project (or use an existing one)
- [ ] Enable billing on the project
- [ ] Enable required APIs: Cloud Run, Artifact Registry, Secret Manager, Cloud Build, IAM Credentials
- [ ] Create the Artifact Registry Docker repository (`dit-2026` in `us-central1`)
- [ ] Create secrets in Secret Manager (SECRET_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY)
- [ ] Set up Workload Identity Federation for GitHub Actions

### Phase 2: First Manual Deploy (~15 minutes)

```bash
# From the dit-2026 repo root
PROJECT_ID="your-project-id"
REGION="us-central1"

# Build and push the image
gcloud builds submit \
  --tag "us-central1-docker.pkg.dev/${PROJECT_ID}/dit-2026/dit-assessment:v1" \
  .

# Deploy to Cloud Run
gcloud run deploy dit-assessment \
  --image="us-central1-docker.pkg.dev/${PROJECT_ID}/dit-2026/dit-assessment:v1" \
  --region=$REGION \
  --platform=managed \
  --allow-unauthenticated \
  --memory=512Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=3 \
  --concurrency=10 \
  --timeout=300 \
  --cpu-boost \
  --set-secrets="SECRET_KEY=dit-secret-key:latest,OPENAI_API_KEY=dit-openai-api-key:latest,ANTHROPIC_API_KEY=dit-anthropic-api-key:latest,GOOGLE_API_KEY=dit-google-api-key:latest" \
  --set-env-vars="DEBUG=false"
```

- [ ] Verify the app works at the Cloud Run-provided URL (`*.run.app`)
- [ ] Test the assessment flow, chat, and framework pages
- [ ] Verify LLM providers are detected (check `/api/providers`)

### Phase 3: Custom Domain (~30 minutes, including DNS propagation)

- [ ] Verify domain ownership: `gcloud domains verify noahratzan.com`
- [ ] Create domain mapping: `gcloud run domain-mappings create --service=dit-assessment --domain=aiskillsmap.noahratzan.com --region=us-central1`
- [ ] Add CNAME record (`dit` -> `ghs.googlehosted.com`) in DNS provider
- [ ] Wait for SSL certificate provisioning (15-60 minutes)
- [ ] Verify `https://aiskillsmap.noahratzan.com` works with valid HTTPS

### Phase 4: CI/CD Automation (~20 minutes)

- [ ] Create `.github/workflows/deploy.yaml` (from Section 6)
- [ ] Replace placeholder values (PROJECT_ID, PROJECT_NUMBER, service account email)
- [ ] Push to main branch and verify the workflow runs successfully
- [ ] Verify auto-deploy on subsequent pushes to `assessment/` or `v-0.0.1/`

### Phase 5: Operational Hardening (Optional)

- [ ] Add `.dockerignore` file (from Section 4)
- [ ] Add `/healthz` endpoint for startup probe
- [ ] Pin dependency versions in `requirements-lock.txt`
- [ ] Set up billing budget alert ($10/month)
- [ ] Configure Cloud Monitoring alert for 5xx error rate
- [ ] Evaluate whether `/api/keys` POST endpoint should be protected or removed for production

---

## Appendix A: File Changes Required

### New Files

| File                              | Purpose                                    |
|-----------------------------------|--------------------------------------------|
| `.dockerignore`                   | Exclude unnecessary files from Docker build |
| `.github/workflows/deploy.yaml`  | GitHub Actions CI/CD pipeline               |

### Optional Modifications

| File                        | Change                                    |
|-----------------------------|-------------------------------------------|
| `assessment/app.py`        | Add `/healthz` health check endpoint       |
| `assessment/requirements.txt` | Pin versions for reproducibility        |

### No Changes Required

The existing `Dockerfile` is production-ready and does not need modification.

---

## Appendix B: Rollback Procedure

If a deployment causes issues:

```bash
# List recent revisions
gcloud run revisions list --service=dit-assessment --region=us-central1

# Route 100% traffic to a previous revision
gcloud run services update-traffic dit-assessment \
  --region=us-central1 \
  --to-revisions=dit-assessment-PREVIOUS_REVISION=100
```

Or redeploy a previous image:

```bash
gcloud run deploy dit-assessment \
  --image="us-central1-docker.pkg.dev/${PROJECT_ID}/dit-2026/dit-assessment:<previous-sha>" \
  --region=us-central1
```

---

## Appendix C: Alternative Approaches Considered

| Approach                     | Pros                          | Cons                                  | Verdict    |
|------------------------------|-------------------------------|---------------------------------------|------------|
| Cloud Run + domain mapping   | Free SSL, simple, no LB cost  | Domain mapping can be slow to provision| **Chosen** |
| Cloud Run + Load Balancer    | CDN, WAF, path routing        | ~$18/month minimum, more complex      | Rejected   |
| Cloud Run + Cloudflare proxy | Free CDN, DDoS protection     | Added complexity, CNAME flattening    | Alternative|
| Vercel rewrites to Cloud Run | Single domain, no subdomain   | Latency from proxy hop, config drift  | Rejected   |
| Render.com (render.yaml)     | Existing config, simple       | Less control, no free tier for web     | Rejected   |
| Fly.io                       | Edge deployment, good DX      | Learning curve, different ecosystem    | Rejected   |

---

## Appendix D: Estimated Timeline

| Phase       | Duration          | Blocker?        |
|-------------|-------------------|-----------------|
| GCP Setup   | 30 min            | Need billing    |
| First Deploy| 15 min            | None            |
| DNS + SSL   | 30 min + wait     | DNS propagation |
| CI/CD       | 20 min            | None            |
| **Total**   | **~2 hours**      |                 |

The longest wait is DNS propagation and SSL certificate provisioning, which happens in the background.
