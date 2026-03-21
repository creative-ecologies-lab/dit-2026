import hashlib
import hmac
import re
import time

from flask import Blueprint, request, jsonify, current_app

bp = Blueprint('api', __name__, url_prefix='/api')

# Per-IP feedback submission counter: {ip: (count, first_submit_time)}
_feedback_counts: dict[str, tuple[int, float]] = {}
_MAX_FEEDBACK_PER_IP = 10  # max submissions per IP per hour
_FEEDBACK_WINDOW = 3600    # 1 hour


def _limiter():
    return current_app.limiter


def _short_ua(ua: str) -> str:
    """Strip full User-Agent to just browser name for privacy."""
    for pattern, name in [
        (r'Edg/([\d]+)', 'Edge'),
        (r'Chrome/([\d]+)', 'Chrome'),
        (r'Firefox/([\d]+)', 'Firefox'),
        (r'Safari/([\d]+)', 'Safari'),
    ]:
        m = re.search(pattern, ua)
        if m:
            return f"{name} {m.group(1)}"
    return 'Other'


def _feedback_token(fb_id: str) -> str:
    """HMAC token so only the original submitter can edit feedback."""
    key = current_app.secret_key
    if isinstance(key, str):
        key = key.encode()
    return hmac.new(key, fb_id.encode(), hashlib.sha256).hexdigest()[:16]


@bp.route('/tree-progress/<tree_id>')
def get_tree_progress(tree_id):
    """Fetch assessment progress or completed result by tree ID."""
    from storage import get_tree_progress as _get
    tree_id = tree_id.strip().upper()[:10]
    record = _get(tree_id)
    if record is None:
        return jsonify({"error": "Tree ID not found"}), 404
    # Strip internal fields, return what the client needs
    result = {
        "tree_id": record.get("tree_id"),
        "status": record.get("status", "partial"),
        "completed_stages": record.get("completed_stages", []),
        "answers": record.get("answers", {}),
        "role": record.get("role"),
        "cohort": record.get("cohort"),
    }
    # If complete, include the full result for loading into results page
    if result["status"] == "complete":
        for key in ("root_depth", "canopy_width", "canopy_height",
                     "root_stage", "canopy_stage", "balance",
                     "tree_key", "tree_species"):
            if key in record:
                result[key] = record[key]
    return jsonify(result)


@bp.route('/tree-progress', methods=['POST'])
def save_tree_progress():
    """Save partial assessment progress at a stage boundary."""
    from storage import save_tree_progress as _save, generate_tree_id
    data = request.get_json(silent=True) or {}

    tree_id = (data.get('tree_id') or '').strip().upper()[:10]
    stage = (data.get('stage') or '').strip()[:10]
    answers = data.get('answers') or {}
    role = (data.get('role') or '')[:20].strip() or None
    cohort = (data.get('cohort') or '')[:64].strip().lower() or None

    if stage not in ('intake', 'root', 'sae', 'canopy'):
        return jsonify({"error": "Invalid stage"}), 400

    # Generate new ID if not provided
    if not tree_id:
        tree_id = generate_tree_id()

    _save(tree_id, stage, answers, role=role, cohort=cohort)
    return jsonify({"tree_id": tree_id, "stage": stage})


@bp.route('/epias-questions')
def epias_questions():
    """Return EPIAS maturity questions for a given SAE level and role."""
    level = request.args.get('level', 1, type=int)
    role = request.args.get('role', 'design')
    from assessment.questions import get_epias_questions
    questions = get_epias_questions(level, role=role)
    return jsonify(questions)


@bp.route('/framework/matrix')
def get_matrix():
    from assessment.matrix import get_full_matrix
    return jsonify(get_full_matrix())


@bp.route('/analytics')
def analytics_data():
    """Rich aggregated analytics. Admin-only via secret key or session."""
    from flask import session
    # Allow if admin session OR ?key=<ADMIN_PASSWORD> for simple API access
    from config import settings
    api_key = request.args.get('key', '')
    if not session.get('admin') and api_key != settings.admin_password:
        return jsonify({"error": "Unauthorized"}), 403
    from storage import get_analytics_data
    cohort = (request.args.get('group') or request.args.get('cohort', '')).strip().lower() or None
    include_test = request.args.get('include_test', '').lower() in ('1', 'true')
    return jsonify(get_analytics_data(cohort=cohort, include_test=include_test))


@bp.route('/forest-data')
def forest_data():
    """Return forest SVGs and stats for a group/cohort."""
    from storage import get_forest_svg
    group = (request.args.get('group') or request.args.get('cohort', '')).strip().lower()
    if not group:
        return jsonify({"error": "group parameter required"}), 400
    trees_svg, forest_svg, stats = get_forest_svg(cohort=group)
    return jsonify({
        "trees_svg": trees_svg,
        "forest_svg": forest_svg,
        "stats": stats,
    })


@bp.route('/heatmap')
def heatmap_data():
    """Return aggregated assessment results for the heatmap.

    Optional query param: ?group=<code> (or ?cohort= for compat) to filter.
    """
    from storage import get_heatmap_data
    cohort = (request.args.get('group') or request.args.get('cohort', '')).strip().lower() or None
    include_test = request.args.get('include_test', '').lower() in ('1', 'true')
    return jsonify(get_heatmap_data(cohort=cohort, include_test=include_test))


@bp.route('/event', methods=['POST'])
def track_event():
    """Store a lightweight analytics event. Fire-and-forget from client."""
    from storage import store_event

    data = request.get_json(silent=True) or {}
    event = (data.get('event') or '').strip()[:50]
    session_id = (data.get('sid') or '').strip()[:64]
    if not event or not session_id:
        return jsonify({"ok": False}), 400

    # Sanitize props — only allow known keys, cap sizes
    raw_props = data.get('props') or {}
    props = {}
    for key in ('path', 'referrer', 'viewport', 'device', 'question',
                'stage', 'level', 'role', 'cohort', 'action', 'tab',
                'elapsed_ms', 'utm_source', 'utm_medium', 'utm_campaign'):
        val = raw_props.get(key)
        if val is not None:
            props[key] = str(val)[:200]

    ua = _short_ua(request.headers.get('User-Agent', ''))
    ok = store_event(event=event, session_id=session_id, props=props, ua=ua)
    return jsonify({"ok": ok}), (200 if ok else 400)


@bp.route('/feedback', methods=['POST'])
def submit_feedback():
    """Store user feedback, return its ID + HMAC token for edits."""
    from storage import store_feedback

    # Per-IP hourly cap
    ip = request.remote_addr or 'unknown'
    count, first_time = _feedback_counts.get(ip, (0, 0.0))
    if time.time() - first_time > _FEEDBACK_WINDOW:
        count, first_time = 0, time.time()
    if count >= _MAX_FEEDBACK_PER_IP:
        return jsonify({"error": "Too many submissions. Please try again later."}), 429

    data = request.get_json(silent=True) or {}
    message = (data.get('message') or '').strip()[:2000]
    category = data.get('category', 'general')
    page = (data.get('page') or '')[:200]
    if not message:
        return jsonify({"error": "Message is required"}), 400
    if category not in ('bug', 'suggestion', 'general'):
        category = 'general'
    fb_id = store_feedback(
        category=category,
        message=message,
        page=page,
        user_agent=_short_ua(request.headers.get('User-Agent', '')),
    )
    _feedback_counts[ip] = (count + 1, first_time)
    return jsonify({"id": fb_id, "token": _feedback_token(fb_id)}), 201


@bp.route('/feedback/<fb_id>', methods=['PUT'])
def edit_feedback(fb_id):
    """User edits their own feedback (requires HMAC token from submit)."""
    from storage import update_feedback
    data = request.get_json(silent=True) or {}
    token = (data.get('token') or '').strip()
    if not token or not hmac.compare_digest(token, _feedback_token(fb_id)):
        return jsonify({"error": "Unauthorized"}), 403
    message = (data.get('message') or '').strip()[:2000]
    category = data.get('category', 'general')
    if not message:
        return jsonify({"error": "Message is required"}), 400
    if category not in ('bug', 'suggestion', 'general'):
        category = 'general'
    ok = update_feedback(fb_id, message=message, category=category)
    if not ok:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"ok": True})
