
import json
import math
import os
import sys

from flask import Flask, render_template, jsonify, request

from core_module.card_data_utils.filter_cards_based_on_inputs import filter_cards
from web.backend.card_cache_service import CardCacheService
from web.backend.containers import AppContainer
from web.backend.db.db_config import configure_sqlite_for_project
from web.backend.update_service import UpdateService


def load_candidates_json():
    """
    Utility to load the candidates.json file.
    This is now independent of the Flask app context.
    """
    # Construct an absolute path to the JSON file to ensure it's always found.
    # __file__ is web/backend/app.py. We need to go up one level to /web/ and then to static/assets.
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    web_dir = os.path.dirname(backend_dir)
    json_path = os.path.join(web_dir, 'static', 'assets', 'candidates.json')

    try:
        with open(json_path, "r", encoding="utf-8") as file:
            return json.load(file)  # Return the parsed JSON data
    except FileNotFoundError:
        return {"error": "candidates.json file not found"}, 404
    except json.JSONDecodeError:
        return {"error": "Invalid JSON format in candidates.json"}, 500


def create_app() -> Flask:
    """
    Application Factory: Creates and configures the Flask application.
    This is the new entry point for the app.
    """
    # 1. Run global configurations for libraries first.
    configure_sqlite_for_project()

    # 2. Create the DI container.
    container = AppContainer()

    # Wire the container to the app's modules.
    # This is important for teardown and other integrations.
    container.wire(modules=[sys.modules[__name__]])

    # 3. Create the Flask app instance.
    app = Flask(__name__)

    # 4. Wire the container to the app for access in views or other parts of the app.
    app.container = container

    # --- Register Routes ---
    # All routes are defined within the factory to be registered with the app instance.

    CARDS_PER_PAGE = 8

    # Register a teardown function that will be called when the app context ends.
    # This ensures a graceful shutdown of container resources.
    @app.teardown_appcontext
    def shutdown(exception=None):
        container.shutdown_resources()

    # --- Register Routes ---
    # All routes are defined within the factory to be registered with the app instance.
    @app.route('/')
    @app.route('/page/<int:page>')
    def card_viewer(page=1):
        """Render the cards for the current page."""
        result = load_candidates_json()
        if isinstance(result, tuple):  # Handle error tuple
            return result
        cards_data = result
        total_pages = math.ceil(len(cards_data) / CARDS_PER_PAGE)
        start = (page - 1) * CARDS_PER_PAGE
        end = start + CARDS_PER_PAGE
        cards_on_page = cards_data[start:end]
        return render_template('cards.html', cards=cards_on_page, page=page, total_pages=total_pages)

    @app.route("/dynamic-view")
    def dynamic_view():
        """Serve the HTML page where frontend handles rendering."""
        return render_template("dynamic_view.html")

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    @app.get("/api/cards")
    def get_cards():
        """API to get all cards."""
        result = load_candidates_json()
        if isinstance(result, tuple):  # Handle error tuple
            return result
        return jsonify(result)

    @app.get("/api/cards/filter")
    def get_filtered_cards():
        """
        API to get cards directly from the database with dynamic filtering.
        """
        # Use the DI container to get the cache service instance
        cache_service: CardCacheService = app.container.card_cache_service()
        cards = cache_service.get_cached_cards()

        # Extract query params for filtering
        gem_rate = float(request.args.get("gem_rate", 0.40))
        net_gain = float(request.args.get("net_gain", 40))
        total_cost = float(request.args.get("total_cost", 100))
        lucrative_factor = float(request.args.get("lucrative_factor", 0.50))
        psa10_volume = int(request.args.get("psa10_volume", 10))
        target_date = request.args.get("target_date", "2014-02-01")
        end_date = request.args.get("end_date", None)
        search = (request.args.get("search") or "").strip().lower()

        filtered = filter_cards(
            cards,
            gem_rate=gem_rate,
            net_gain=net_gain,
            total_cost=total_cost,
            lucrative_factor=lucrative_factor,
            psa10_volume=psa10_volume,
            start_date=target_date,
            end_date=end_date
        )

        if search:
            filtered = [
                c for c in filtered
                if (search in c["card_data"]["name"].lower()
                    or search in str(c["card_data"]["id"]).lower()
                    or search in str(c["card_data"]["num"]).lower()
                    or search in c["card_data"]["set_name"].lower()
                    or any(search in (sale.get("title", "").lower()) for sale in c.get("recent_raw_ebay_sales", [])))
            ]

        return jsonify(filtered)

    @app.post("/api/update-cycle")
    def update_cycle_endpoint():
        """
        Triggers the full update cycle for fetching and processing card data.
        """
        try:
            # Get the update service from the container
            update_service_instance: UpdateService = app.container.update_service()
            # Execute the update cycle
            update_service_instance.run_update_cycle()
            return jsonify({"status": "success", "message": "Update cycle initiated successfully."}), 202
        except Exception as e:
            # Log the full error for debugging
            print(f"An error occurred during the update cycle: {e}")
            return jsonify({"status": "error", "message": "An internal error occurred during the update cycle."}), 500

    # You could also set up the database schema on startup here if desired:
    # with app.app_context():
    #     db = container.database()
    #     db.setup()

    return app



# --- Main Execution ---
# This part only runs when you execute the script directly (e.g., `python app.py`).
if __name__ == '__main__':
    # Create the app using the factory.
    app = create_app()
    app.run(debug=True)
