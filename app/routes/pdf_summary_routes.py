from flask import Blueprint, request, jsonify
from app.controllers.pdf_summary_controller import PdfSummaryController


class PdfSummaryRoutes:
    def __init__(self):
        self.bp = Blueprint('pdf_summary', __name__)
        self.controller = PdfSummaryController()

    def register(self):
        self.bp.route('/api/pdf-summaries', methods=['GET'])(self.list_summaries)
        self.bp.route('/api/pdf-summaries/<slug>', methods=['GET'])(self.get_summary)
        self.bp.route('/api/pdf-summaries', methods=['POST'])(self.create_summary)
        return self.bp

    def list_summaries(self):
        summaries = self.controller.list_summaries()
        return jsonify({'status': 'success', 'summaries': summaries}), 200

    def get_summary(self, slug):
        summary = self.controller.get_summary_by_slug(slug)
        if not summary:
            return jsonify({'status': 'error', 'message': 'Summary not found'}), 404
        return jsonify({'status': 'success', 'summary': summary}), 200

    def create_summary(self):
        payload = request.get_json() or {}
        slug = payload.get('slug')
        title = payload.get('title')
        content = payload.get('content')
        source_file = payload.get('source_file')
        author_id = payload.get('author_id')
        published = payload.get('published', False)

        if not slug or not title or not content:
            return jsonify({'status': 'error', 'message': 'slug, title, and content are required'}), 400

        try:
            new_id = self.controller.create_summary(slug, title, content, source_file, author_id, published)
            return jsonify({'status': 'success', 'id': new_id}), 201
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500


pdf_summary_bp = PdfSummaryRoutes().register()
