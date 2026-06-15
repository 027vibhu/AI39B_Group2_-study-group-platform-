from app.models.base_model import BaseModel
from app.models.database import ensure_database_exists


class Lore(BaseModel):
    @property
    def table(self):
        return 'lore'

    @classmethod
    def ensure_table_exists(cls):
        """Create the `lore` table using raw SQL."""
        ensure_database_exists()
        inst = cls()
        inst.execute(
            "CREATE TABLE IF NOT EXISTS lore ("
            "id INT AUTO_INCREMENT PRIMARY KEY,"
            "slug VARCHAR(255) NOT NULL UNIQUE,"
            "title VARCHAR(255) NOT NULL,"
            "content LONGTEXT NOT NULL,"
            "author_id INT NULL,"
            "published BOOLEAN NOT NULL DEFAULT FALSE,"
            "created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,"
            "updated_at TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,"
            "FULLTEXT KEY idx_lore_fulltext (title, content)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
        )


# Module-level convenience
_lore = Lore()


def ensure_table_exists():
    return Lore.ensure_table_exists()
