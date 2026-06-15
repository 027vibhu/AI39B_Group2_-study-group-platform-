from app.controllers.base_controller import BaseController
from app.models.database_setup import create_database, create_project_metadata_table


class DatabaseSetupController(BaseController):
    def initialize_database(self):
        """Create the Lorevia database and ensure the metadata table exists."""
        create_database()
        create_project_metadata_table()
        return {
            'status': 'ok',
            'message': 'Database initialized and project metadata table created.'
        }
