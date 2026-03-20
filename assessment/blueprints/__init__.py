def register_all_blueprints(app):
    from blueprints.assessment import bp as assessment_bp
    from blueprints.api import bp as api_bp
    from blueprints.admin import bp as admin_bp
    app.register_blueprint(assessment_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(admin_bp)

    # --- Rate limits on sensitive endpoints ---
    # Limits are per-IP (via X-Forwarded-For).  Assessment submit is the hot
    # path during SXSW — one person won't submit more than a few times, but
    # the old limit of 6/min blocked everyone when Cloud Run collapsed all
    # users to the same proxy IP.  Now with real IPs, 10/min per user is safe.
    limiter = app.limiter
    limiter.limit("10 per minute")(app.view_functions['assessment.submit_assessment'])
    limiter.limit("60 per minute")(app.view_functions['api.track_event'])
    limiter.limit("5 per minute")(app.view_functions['api.submit_feedback'])
    limiter.limit("5 per minute")(app.view_functions['api.edit_feedback'])
    limiter.limit("5 per minute")(app.view_functions['admin.login'])
