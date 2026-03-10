def register_all_blueprints(app):
    from blueprints.assessment import bp as assessment_bp
    from blueprints.api import bp as api_bp
    from blueprints.admin import bp as admin_bp
    app.register_blueprint(assessment_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(admin_bp)

    # --- Rate limits on sensitive endpoints ---
    limiter = app.limiter
    limiter.limit("6 per minute")(app.view_functions['assessment.submit_assessment'])
    limiter.limit("3 per minute")(app.view_functions['api.submit_feedback'])
    limiter.limit("3 per minute")(app.view_functions['api.edit_feedback'])
    limiter.limit("5 per minute")(app.view_functions['admin.login'])
