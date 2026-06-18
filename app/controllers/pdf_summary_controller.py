from app.controllers.base_controller import BaseController
from app.models.pdf_summary import PdfSummary


class PdfSummaryController(BaseController):
    def __init__(self):
        super().__init__()
        self._model = PdfSummary()

    def ensure_table(self):
        """Ensure the underlying `pdf_summaries` table exists."""
        return self._model.ensure_table_exists()

    def list_summaries(self, order_by='created_at'):
        """Return all summaries ordered by the given column."""
        self._model.ensure_table_exists()
        return self._model.find_all(order_by=order_by)

    def get_summary_by_slug(self, slug: str):
        """Fetch a single summary by its slug."""
        self._model.ensure_table_exists()
        return self._model.find_by('slug', slug)
