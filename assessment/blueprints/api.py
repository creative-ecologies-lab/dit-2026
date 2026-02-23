import os
from flask import Blueprint, request, jsonify, current_app

bp = Blueprint('api', __name__, url_prefix='/api')

# Keys that can be set via the UI
CONFIGURABLE_KEYS = {
    'openai': 'OPENAI_API_KEY',
    'anthropic': 'ANTHROPIC_API_KEY',
    'google': 'GOOGLE_API_KEY',
}


@bp.route('/search', methods=['POST'])
def semantic_search():
    data = request.get_json()
    query = data['query']
    top_k = data.get('top_k', 5)
    results = current_app.search_engine.search(query, top_k=top_k)
    return jsonify({"results": results, "query": query})


@bp.route('/providers')
def list_providers():
    providers = current_app.llm_registry.get_available_providers()
    return jsonify({"providers": providers})


@bp.route('/models')
def list_models():
    """Return full model catalog filtered to available providers."""
    catalog = current_app.llm_registry.get_models_catalog()
    return jsonify({"models": catalog})


@bp.route('/epias-questions')
def epias_questions():
    """Return EPIAS maturity questions for a given SAE level."""
    level = request.args.get('level', 1, type=int)
    from assessment.questions import get_epias_questions
    questions = get_epias_questions(level)
    return jsonify(questions)


@bp.route('/framework/matrix')
def get_matrix():
    from assessment.matrix import get_full_matrix
    return jsonify(get_full_matrix())


@bp.route('/heatmap')
def heatmap_data():
    """Return aggregated assessment results for the heatmap.

    Optional query param: ?cohort=<code> to filter by cohort.
    """
    from storage import get_heatmap_data
    cohort = request.args.get('cohort', '').strip().lower() or None
    return jsonify(get_heatmap_data(cohort=cohort))


@bp.route('/usage')
def usage_stats():
    """Return current daily token usage stats."""
    from usage_tracker import get_usage_stats
    return jsonify(get_usage_stats())


@bp.route('/keys', methods=['GET'])
def get_keys():
    """Keys are managed via GCP Secret Manager. No runtime key info exposed."""
    return jsonify({"message": "API keys are managed server-side."}), 403


@bp.route('/keys', methods=['POST'])
def set_keys():
    """Disabled in production. Keys are managed via GCP Secret Manager."""
    return jsonify({"error": "Key management is disabled in production."}), 403
