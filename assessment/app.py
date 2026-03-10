import os
import secrets
from pathlib import Path

from flask import Flask
from dotenv import load_dotenv

load_dotenv()

_FIRESTORE_ON = os.environ.get('FIRESTORE_ENABLED', '').lower() in ('1', 'true')


def create_app() -> Flask:
    app = Flask(__name__, static_folder='static', static_url_path='/static', template_folder='templates')

    # --- Secret key: require explicit key in production ---
    _secret = os.environ.get('SECRET_KEY')
    if not _secret:
        if _FIRESTORE_ON:
            raise RuntimeError("SECRET_KEY env var must be set in production")
        _secret = secrets.token_hex(32)  # random per-process for local dev
    app.secret_key = _secret

    # --- Session cookie hardening ---
    app.config.update(
        SESSION_COOKIE_SECURE=_FIRESTORE_ON,    # HTTPS-only in prod
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        MAX_CONTENT_LENGTH=16 * 1024,           # 16 KB max request body
    )

    # --- Security headers ---
    @app.after_request
    def _security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https://users.ece.cmu.edu; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        if _FIRESTORE_ON:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response

    # --- CSRF protection (admin forms) ---
    from flask_wtf.csrf import CSRFProtect
    csrf = CSRFProtect()
    csrf.init_app(app)

    # --- Rate limiting ---
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    limiter = Limiter(
        get_remote_address, app=app,
        default_limits=["200 per minute"],
        storage_uri="memory://",
    )
    app.limiter = limiter  # expose for blueprint use

    # Initialize search engine (loads pre-computed embeddings)
    from embeddings.search import SearchEngine
    app.search_engine = SearchEngine()

    # Register blueprints
    from blueprints import register_all_blueprints
    register_all_blueprints(app)

    # Exempt JSON API endpoints from CSRF — they use fetch(), not HTML forms.
    # csrf.exempt() with strings expects module.func format, so exempt the
    # actual view functions directly.
    csrf.exempt(app.view_functions['api.submit_feedback'])
    csrf.exempt(app.view_functions['api.edit_feedback'])
    csrf.exempt(app.view_functions['assessment.submit_assessment'])

    # Pre-populate in-memory store with synthetic data when Firestore is off
    _seed_demo_data()

    return app


def _seed_demo_data():
    """Load synthetic results into the in-memory store so the heatmap is
    populated even without Firestore.  No-op if Firestore is enabled or
    the export file is missing."""
    import json, random

    from storage import _is_enabled, store_result

    if _is_enabled():
        return  # Firestore active — skip seeding

    from storage import _memory_store
    if _memory_store:
        return  # Already seeded

    export_path = Path(__file__).parent / 'results_export.json'
    if not export_path.exists():
        return

    data = json.load(export_path.open(encoding='utf-8'))

    # Flatten and take a deterministic 500-record sample for the global heatmap
    random.seed(42)
    all_records = [r for records in data.values() for r in records]
    sample = random.sample(all_records, min(500, len(all_records)))

    for r in sample:
        store_result(r['sae_level'], r['epias_stage'],
                     cohort=None,
                     age_range=r.get('age_range'),
                     role=r.get('role'))

    # Ensure every cell has at least 1 result for a realistic-looking heatmap.
    # Use deterministic varied counts so edge cells aren't all identical.
    from storage import get_heatmap_data
    hm = get_heatmap_data()
    stages = ['E', 'P', 'I', 'A', 'S']
    # Varied fill counts per cell — looks natural, not uniform
    _fill = [3, 1, 2, 4, 1, 2, 1, 3, 2, 1,
             5, 2, 1, 3, 1, 2, 4, 1, 1, 3,
             1, 2, 1, 3, 2, 1, 2, 1, 4, 1]
    idx = 0
    for level in range(6):
        for stage in stages:
            key = f"{level}_{stage}"
            if hm['counts'].get(key, 0) == 0:
                for _ in range(_fill[idx]):
                    store_result(level, stage, cohort=None)
            idx += 1

    # ── Trend injection: create realistic cross-diagonal patterns ──
    # High automation / low maturity: L4-L5 people at Explorer & Practitioner
    # Senior leaders / low automation: L0-L2 people at Architect & Steward
    _trend_boost = {
        # (level, stage): extra_count
        # --- High-SAE, early-EPIAS cluster ---
        (5, 'E'): 12, (5, 'P'): 10,
        (4, 'E'): 15, (4, 'P'): 18,
        # --- Low-SAE, senior-EPIAS cluster ---
        (0, 'A'): 8,  (0, 'S'): 10,
        (1, 'A'): 12, (1, 'S'): 14,
        (2, 'A'): 10, (2, 'S'): 8,
        # Mild secondary presence (not zero but not dominant)
        (3, 'E'): 4,  (3, 'S'): 3,
        (5, 'I'): 3,  (0, 'I'): 4,
    }
    for (level, stage), extra in _trend_boost.items():
        for _ in range(extra):
            store_result(level, stage, cohort=None)

    # Also load cohort-specific data (with gap-filling + trend injection)
    for cohort_code, records in data.items():
        for r in records:
            store_result(r['sae_level'], r['epias_stage'],
                         cohort=cohort_code,
                         age_range=r.get('age_range'),
                         role=r.get('role'))
        # Fill gaps for each cohort too
        chm = get_heatmap_data(cohort=cohort_code)
        idx = 0
        for level in range(6):
            for stage in stages:
                key = f"{level}_{stage}"
                if chm['counts'].get(key, 0) == 0:
                    for _ in range(_fill[idx]):
                        store_result(level, stage, cohort=cohort_code)
                idx += 1
        # Apply same trend boost to each cohort
        for (level, stage), extra in _trend_boost.items():
            for _ in range(extra):
                store_result(level, stage, cohort=cohort_code)


# Module-level app instance for gunicorn (Cloud Run uses `app:app`)
app = create_app()
