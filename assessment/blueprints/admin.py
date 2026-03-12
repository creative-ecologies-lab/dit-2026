"""Admin blueprint — feedback review with simple password auth."""

import os
import time
from functools import wraps
from flask import Blueprint, render_template, request, redirect, session, url_for, jsonify

bp = Blueprint('admin', __name__, url_prefix='/admin')

_FIRESTORE_ON = os.environ.get('FIRESTORE_ENABLED', '').lower() in ('1', 'true')

# Brute-force protection: {ip: (fail_count, last_fail_time)}
_login_attempts: dict[str, tuple[int, float]] = {}
_MAX_ATTEMPTS = 5
_LOCKOUT_SECONDS = 300  # 5 minutes


def require_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin'):
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated


@bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        from config import settings

        # Block default password in production
        if _FIRESTORE_ON and settings.admin_password in ('admin', 'password', ''):
            return "Admin disabled: set ADMIN_PASSWORD env var", 503

        # Brute-force lockout
        ip = request.remote_addr or 'unknown'
        attempts, last_time = _login_attempts.get(ip, (0, 0.0))
        if attempts >= _MAX_ATTEMPTS and (time.time() - last_time) < _LOCKOUT_SECONDS:
            error = 'Too many attempts. Try again in a few minutes.'
        elif request.form.get('password') == settings.admin_password:
            _login_attempts.pop(ip, None)
            session['admin'] = True
            return redirect(url_for('admin.feedback_list'))
        else:
            _login_attempts[ip] = (attempts + 1, time.time())
            error = 'Wrong password.'
    return render_template('admin_login.html', error=error)


@bp.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('admin.login'))


@bp.route('/feedback')
@require_admin
def feedback_list():
    from storage import list_feedback
    items = list_feedback()
    counts = {
        'total': len(items),
        'new': sum(1 for i in items if i.get('status') == 'new'),
        'reviewed': sum(1 for i in items if i.get('status') == 'reviewed'),
        'resolved': sum(1 for i in items if i.get('status') == 'resolved'),
    }
    return render_template('admin_feedback.html', items=items, counts=counts)


@bp.route('/analytics')
@require_admin
def analytics():
    from storage import get_analytics_data
    cohort = request.args.get('cohort') or None
    include_test = request.args.get('include_test', '').lower() in ('1', 'true')
    data = get_analytics_data(cohort=cohort, include_test=include_test)
    return render_template('admin_analytics.html', data=data, cohort=cohort, include_test=include_test)


@bp.route('/feedback/<fb_id>/status', methods=['POST'])
@require_admin
def toggle_status(fb_id):
    from storage import update_feedback_status
    # Cycle: new → reviewed → resolved → new
    cycle = {'new': 'reviewed', 'reviewed': 'resolved', 'resolved': 'new'}
    current = request.form.get('current', 'new')
    new_status = cycle.get(current, 'reviewed')
    update_feedback_status(fb_id, new_status)
    return redirect(url_for('admin.feedback_list'))
