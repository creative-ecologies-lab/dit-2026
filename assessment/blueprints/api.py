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


@bp.route('/heatmap')
def heatmap_data():
    """Return aggregated assessment results for the heatmap.

    Optional query param: ?group=<code> (or ?cohort= for compat) to filter.
    """
    from storage import get_heatmap_data
    cohort = (request.args.get('group') or request.args.get('cohort', '')).strip().lower() or None
    include_test = request.args.get('include_test', '').lower() in ('1', 'true')
    return jsonify(get_heatmap_data(cohort=cohort, include_test=include_test))


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
