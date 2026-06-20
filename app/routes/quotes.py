from flask import Blueprint, jsonify
from app.controllers.quote_controller import QuoteController


class QuoteRoutes:
    def __init__(self):
        self.bp = Blueprint('quotes', __name__)

    def register(self):
        self.bp.route('/api/quote', methods=['GET'])(self.get_quote)
        return self.bp

    def get_quote(self):
        """Return a single random motivational line."""
        controller = QuoteController()
        try:
            quote = controller.get_random_quote()
            return jsonify({
                'status': 'success',
                'quote': quote,
            }), 200
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'An error occurred while fetching a quote: {str(e)}',
            }), 500


# Expose module-level blueprint for compatibility with imports elsewhere
quote_bp = QuoteRoutes().register()
