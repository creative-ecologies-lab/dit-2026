# DNS & Subdomain Setup: aiskillsmap.noahratzan.com

This guide covers how to make the DIT Assessment Flask app (deployed on GCP Cloud Run) accessible at `aiskillsmap.noahratzan.com`.

---

## Current Setup

- **Main site**: `noahratzan.com` -- Next.js 16 on Vercel
- **DIT app**: Flask app, will be deployed to GCP Cloud Run
- **DNS**: Managed wherever `noahratzan.com` nameservers point (likely Vercel DNS or your registrar -- see "Determine Your DNS Provider" below)
- **No existing subdomains** configured

---

## Step 0: Determine Your DNS Provider

Before anything else, you need to know where DNS for `noahratzan.com` is managed.

### Check nameservers

```bash
# On Windows (PowerShell)
nslookup -type=NS noahratzan.com

# On macOS/Linux
dig NS noahratzan.com +short
```

**If the nameservers are:**
- `ns1.vercel-dns.com` / `ns2.vercel-dns.com` --> DNS is managed by **Vercel**
- `*.cloudflare.com` --> DNS is managed by **Cloudflare**
- Something else (e.g., `ns1.registrar.com`) --> DNS is managed at your **domain registrar** (Namecheap, Google Domains, GoDaddy, etc.)

This determines where you add DNS records in the steps below.

---

## Approach A: DNS-Level Routing (Recommended)

This is the simplest and most performant approach. The subdomain `aiskillsmap.noahratzan.com` points directly to Cloud Run. Vercel is not involved at all for subdomain traffic.

### Why This Is Better

- Complete separation of concerns -- the Flask app and Next.js site are fully independent
- No Vercel middleware/rewrites processing subdomain requests
- Cloud Run handles its own SSL certificate via Google-managed certificates
- Lower latency (one hop, not two)
- No risk of Vercel middleware interfering (CSRF checks, auth, etc.)

### Step 1: Deploy to Cloud Run

Deploy the Flask app to Cloud Run first (you need the service URL).

```bash
# From the dit-2026/assessment directory
gcloud run deploy dit-assessment \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --set-env-vars "SECRET_KEY=$(openssl rand -hex 32)"
```

After deployment, note the auto-assigned URL (e.g., `dit-assessment-abc123-uc.a.run.app`).

### Step 2: Map the Custom Domain in Cloud Run

```bash
gcloud run domain-mappings create \
  --service dit-assessment \
  --domain aiskillsmap.noahratzan.com \
  --region us-central1
```

This command will output the DNS records you need to add. Typically it will ask you to add one of:

- **Option 1 (CNAME)**: A CNAME record pointing to `ghs.googlehosted.com`
- **Option 2 (A/AAAA)**: A records pointing to Google's IP addresses

**CNAME is preferred** for subdomains because it automatically follows Google's IP changes.

### Step 3: Add DNS Records

#### If DNS is on Vercel

1. Go to [Vercel Dashboard](https://vercel.com/dashboard) > your project > Settings > Domains
2. You are NOT adding `aiskillsmap.noahratzan.com` to the Vercel project. Instead:
3. Go to the **Vercel DNS** page (separate from project domains): https://vercel.com/dashboard/domains
4. Click on `noahratzan.com`
5. Add a new DNS record:

| Type  | Name | Value                  | TTL  |
|-------|------|------------------------|------|
| CNAME | dit  | ghs.googlehosted.com  | 3600 |

#### If DNS is on Cloudflare

1. Go to Cloudflare Dashboard > noahratzan.com > DNS
2. Add a new record:

| Type  | Name | Target                 | Proxy Status |
|-------|------|------------------------|-------------|
| CNAME | dit  | ghs.googlehosted.com  | **DNS only** (grey cloud) |

**Important**: Set proxy status to "DNS only" (grey cloud icon, not orange). Cloudflare's proxy would intercept SSL and break Cloud Run's certificate provisioning.

#### If DNS is at Your Registrar

1. Log into your registrar's DNS management panel
2. Add a CNAME record:

| Type  | Name              | Value                  | TTL  |
|-------|-------------------|------------------------|------|
| CNAME | aiskillsmap.noahratzan.com | ghs.googlehosted.com  | 3600 |

Note: Some registrars want the full subdomain name, others just want "dit".

### Step 4: Verify Domain Ownership

Cloud Run may require domain verification:

```bash
# Check if verification is needed
gcloud domains list-user-verified

# If not verified, verify via Google Search Console or TXT record
gcloud domains verify noahratzan.com
```

This will either:
- Open a browser for Google Search Console verification, OR
- Ask you to add a TXT record to your DNS

### Step 5: Wait for SSL Certificate Provisioning

Google automatically provisions a managed SSL certificate. This can take **15-60 minutes** after DNS propagation.

```bash
# Check certificate status
gcloud run domain-mappings describe \
  --domain aiskillsmap.noahratzan.com \
  --region us-central1
```

Look for `certificateStatus: ACTIVE` in the output. While provisioning, you may see `PROVISIONING` or `PENDING`.

### Step 6: Verify Everything Works

```bash
# Check DNS propagation
nslookup aiskillsmap.noahratzan.com

# Test HTTP (should redirect to HTTPS)
curl -I http://aiskillsmap.noahratzan.com

# Test HTTPS
curl -I https://aiskillsmap.noahratzan.com

# Full page load
curl https://aiskillsmap.noahratzan.com
```

---

## Approach B: Vercel Rewrites (Alternative)

Route traffic through Vercel, which proxies requests to Cloud Run. Use this only if you cannot manage DNS records or need Vercel's edge network in front.

### Why You Might Use This

- You want a path-based approach (`noahratzan.com/dit/`) instead of a subdomain
- You cannot add DNS records (rare)
- You want Vercel's CDN/edge caching in front of Cloud Run

### Why This Is Worse

- Adds latency (Vercel edge -> Cloud Run, instead of direct)
- Vercel middleware runs on every request (CSRF checks, auth logic) -- may interfere
- The Flask app's session cookies and redirects need to account for the proxy
- More configuration surface area for bugs

### Option B1: Path-Based Rewrite (noahratzan.com/dit/*)

Add to `website/vercel.json`:

```json
{
  "rewrites": [
    {
      "source": "/dit/:path*",
      "destination": "https://dit-assessment-abc123-uc.a.run.app/:path*"
    }
  ]
}
```

**Problem**: The Flask app's templates reference `/static/...` paths, which would be intercepted by Next.js. You would need to either:
1. Rewrite all static paths to `/dit/static/...` in the Flask app
2. Add additional rewrite rules for static assets

This gets messy fast. Not recommended.

### Option B2: Subdomain Rewrite via vercel.json

Add `aiskillsmap.noahratzan.com` as a domain in your Vercel project, then use rewrites:

1. Add `aiskillsmap.noahratzan.com` to Vercel project domains (Settings > Domains)
2. Add to `website/vercel.json`:

```json
{
  "rewrites": [
    {
      "source": "/:path*",
      "has": [
        {
          "type": "host",
          "value": "aiskillsmap.noahratzan.com"
        }
      ],
      "destination": "https://dit-assessment-abc123-uc.a.run.app/:path*"
    }
  ]
}
```

3. **Critical**: Update `website/middleware.ts` to skip processing for the subdomain:

```typescript
export async function middleware(request: NextRequest) {
  // Skip all middleware for dit subdomain (proxied to Cloud Run)
  const host = request.headers.get('host') || '';
  if (host.startsWith('dit.')) {
    return NextResponse.next({ request });
  }

  // ... rest of existing middleware
}
```

Without this middleware change, the CSRF protection would block cross-origin requests, and the auth middleware would redirect unauthenticated users.

### Option B2 DNS Setup

If DNS is on Vercel, the domain will be configured automatically when you add it to the Vercel project. If DNS is elsewhere, add a CNAME:

| Type  | Name | Value                  |
|-------|------|------------------------|
| CNAME | dit  | cname.vercel-dns.com  |

---

## CORS Configuration

If the main `noahratzan.com` site ever needs to interact with `aiskillsmap.noahratzan.com` (e.g., embedding in an iframe, making API calls), the Flask app needs CORS headers.

### Flask CORS Setup

Install flask-cors:

```bash
pip install flask-cors
```

Add to `app.py`:

```python
from flask_cors import CORS

def create_app() -> Flask:
    app = Flask(__name__, static_folder='static', static_url_path='/static', template_folder='templates')
    app.secret_key = os.environ.get('SECRET_KEY', 'dit-assessment-dev-key')

    # CORS: allow the main site to make requests to this app
    CORS(app, resources={
        r"/api/*": {
            "origins": [
                "https://noahratzan.com",
                "https://www.noahratzan.com",
                "http://localhost:3000",  # local Next.js dev
            ],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
        }
    })

    # ... rest of create_app
```

### iframe Embedding

If you embed the DIT app in an iframe on the main site, the Flask app also needs to allow framing:

```python
@app.after_request
def set_frame_headers(response):
    # Allow embedding from the main site
    response.headers['X-Frame-Options'] = 'ALLOW-FROM https://noahratzan.com'
    # Modern browsers use Content-Security-Policy instead
    response.headers['Content-Security-Policy'] = (
        "frame-ancestors 'self' https://noahratzan.com"
    )
    return response
```

Note: The main Next.js site currently sets `X-Frame-Options: SAMEORIGIN` (see `next.config.ts`). This prevents the main site from being framed, but does not affect the Flask app's ability to be framed.

### When CORS Is NOT Needed

If the Flask app is completely standalone (users navigate directly to `aiskillsmap.noahratzan.com` and never interact with the main site via JavaScript), no CORS configuration is needed. The two sites are fully independent.

---

## Troubleshooting

### DNS not propagating

```bash
# Check current DNS records
nslookup aiskillsmap.noahratzan.com
# Or with more detail:
nslookup -type=CNAME aiskillsmap.noahratzan.com

# Check from Google's DNS (bypasses local cache)
nslookup aiskillsmap.noahratzan.com 8.8.8.8
```

DNS changes typically propagate within 5-30 minutes, but can take up to 48 hours in rare cases.

### SSL certificate stuck in PROVISIONING

Common causes:
1. **DNS not pointing correctly** -- verify the CNAME resolves to `ghs.googlehosted.com`
2. **Domain not verified** -- run `gcloud domains list-user-verified`
3. **CAA records blocking Google** -- check for CAA records that restrict certificate issuers:
   ```bash
   nslookup -type=CAA noahratzan.com
   ```
   If CAA records exist, add `pki.goog` as an allowed issuer:
   | Type | Name          | Value                    |
   |------|---------------|--------------------------|
   | CAA  | noahratzan.com | 0 issue "pki.goog"      |

4. **Wait longer** -- sometimes it just takes 30-60 minutes

### Cloud Run returns 403 or requires authentication

Make sure the service allows unauthenticated access:

```bash
gcloud run services add-iam-policy-binding dit-assessment \
  --region us-central1 \
  --member="allUsers" \
  --role="roles/run.invoker"
```

### Vercel middleware blocking requests (Approach B only)

Symptoms: 403 errors, unexpected redirects to login page.

Cause: The middleware in `website/middleware.ts` applies CSRF checks and auth redirects to all requests, including those for the `dit` subdomain.

Fix: Add the host check at the top of the middleware function as shown in Approach B2 above.

### Flask app returns wrong URLs / broken static assets

If using Approach B (Vercel rewrites), the Flask app may generate URLs that don't account for the proxy. Set `PREFERRED_URL_SCHEME` and `SERVER_NAME`:

```python
app.config['PREFERRED_URL_SCHEME'] = 'https'
app.config['SERVER_NAME'] = 'aiskillsmap.noahratzan.com'
```

With Approach A, this is not needed -- Flask sees the request directly.

### Mixed content warnings

If the Flask app serves pages over HTTPS but references HTTP resources, browsers will block them. Ensure all templates use relative URLs or `https://` for external resources.

---

## Summary: Recommended Path

1. **Use Approach A** (DNS-level routing with CNAME to Cloud Run)
2. Deploy the Flask app to Cloud Run
3. Map `aiskillsmap.noahratzan.com` in Cloud Run
4. Add a single CNAME record (`dit` -> `ghs.googlehosted.com`) in your DNS provider
5. Wait for SSL provisioning
6. Done -- no changes needed to the Next.js site or Vercel configuration

The two applications remain completely independent, each handling their own SSL, routing, and sessions.
