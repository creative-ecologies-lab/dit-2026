import os
from pathlib import Path

from flask import Flask
from dotenv import load_dotenv

load_dotenv()


def create_app() -> Flask:
    app = Flask(__name__, static_folder='static', static_url_path='/static', template_folder='templates')
    app.secret_key = os.environ.get('SECRET_KEY', 'dit-assessment-dev-key')

    # Initialize search engine (loads pre-computed embeddings)
    from embeddings.search import SearchEngine
    app.search_engine = SearchEngine()

    # Initialize LLM provider registry
    from llm import create_provider_registry
    app.llm_registry = create_provider_registry()

    # Register blueprints
    from blueprints import register_all_blueprints
    register_all_blueprints(app)

    # Inject has_llm into all templates
    @app.context_processor
    def inject_globals():
        available = [p for p in app.llm_registry.get_available_providers() if p['available']]
        return {'has_llm': bool(available)}

    return app


# Module-level app instance for gunicorn (Cloud Run uses `app:app`)
app = create_app()
