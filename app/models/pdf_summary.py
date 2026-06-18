from app.models.base_model import BaseModel
from app.models.database import ensure_database_exists


class PdfSummary(BaseModel):
    @property
    def table(self):
        return 'pdf_summaries'

    @classmethod
    def ensure_table_exists(cls):
        """Create the `pdf_summaries` table using raw SQL."""
        ensure_database_exists()
        inst = cls()
        inst.execute(
            "CREATE TABLE IF NOT EXISTS pdf_summaries ("
            "id INT AUTO_INCREMENT PRIMARY KEY,"
            "slug VARCHAR(255) NOT NULL UNIQUE,"
            "title VARCHAR(255) NOT NULL,"
            "content LONGTEXT NOT NULL,"
            "source_file VARCHAR(255) NULL,"
            "author_id INT NULL,"
            "published BOOLEAN NOT NULL DEFAULT FALSE,"
            "created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,"
            "updated_at TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,"
            "FULLTEXT KEY idx_pdf_summaries_fulltext (title, content)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
        )


# Module-level convenience
_pdf_summary = PdfSummary()


def ensure_table_exists():
    return PdfSummary.ensure_table_exists()
