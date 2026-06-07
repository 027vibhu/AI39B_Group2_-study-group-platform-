from app.models.base_model import BaseModel
from app.models.database import ensure_database_exists


class DatabaseSetupModel(BaseModel):
    @property
    def table(self):
        return 'project_metadata'

    def create_database(self):
        """Ensure the Lorevia database exists using raw SQL."""
        ensure_database_exists()
        return True

    def create_project_metadata_table(self):
        """Create a lightweight project metadata table for database initialization."""
        ensure_database_exists()
        return self.execute(
            "CREATE TABLE IF NOT EXISTS project_metadata ("
            "id INT AUTO_INCREMENT PRIMARY KEY,"
            "key_name VARCHAR(100) NOT NULL UNIQUE,"
            "value_text TEXT NULL,"
            "created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
        )


_db_setup = DatabaseSetupModel()


def create_database():
    return _db_setup.create_database()


def create_project_metadata_table():
    return _db_setup.create_project_metadata_table()
