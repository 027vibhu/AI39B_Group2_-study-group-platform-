from app.models.base_model import BaseModel

# Kanban columns a task can live in. Anything else falls back to 'todo'.
TASK_STATUSES = ('todo', 'in_progress', 'in_review', 'done')

# Priority levels for a task. Anything else falls back to 'medium'.
TASK_PRIORITIES = ('low', 'medium', 'high')


def create_tasks_table():
    """Create the dashboard_tasks table if it does not exist."""
    from app.models.database import ensure_database_exists, get_database_connection

    ensure_database_exists()
    connection = get_database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS dashboard_tasks ("
                "id INT AUTO_INCREMENT PRIMARY KEY,"
                "user_id INT NOT NULL,"
                "title VARCHAR(255) NOT NULL,"
                "description TEXT NULL,"
                "status VARCHAR(20) NOT NULL DEFAULT 'todo',"
                "priority VARCHAR(10) NOT NULL DEFAULT 'medium',"
                "due_date DATE NULL,"
                "is_done TINYINT(1) NOT NULL DEFAULT 0,"
                "created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"
                ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
            )
            try:
                cursor.execute(
                    "ALTER TABLE dashboard_tasks ADD INDEX idx_dashboard_tasks_user (user_id)"
                )
            except Exception:
                pass
            # Migrate existing tables that predate the schedule board.
            try:
                cursor.execute(
                    "ALTER TABLE dashboard_tasks "
                    "ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'todo'"
                )
            except Exception:
                pass
            try:
                cursor.execute(
                    "ALTER TABLE dashboard_tasks ADD COLUMN due_date DATE NULL"
                )
            except Exception:
                pass
            try:
                cursor.execute(
                    "ALTER TABLE dashboard_tasks "
                    "ADD COLUMN priority VARCHAR(10) NOT NULL DEFAULT 'medium'"
                )
            except Exception:
                pass
            try:
                cursor.execute(
                    "ALTER TABLE dashboard_tasks ADD COLUMN description TEXT NULL"
                )
            except Exception:
                pass
    finally:
        connection.close()


class Task(BaseModel):
    """Model for a user's simple dashboard to-do items (raw SQL)."""

    @property
    def table(self):
        return 'dashboard_tasks'

    @classmethod
    def ensure_table_exists(cls):
        create_tasks_table()

    @classmethod
    def create(cls, user_id: int, title: str, status: str = 'todo',
               due_date=None, priority: str = 'medium', description=None):
        """Insert a task and return the new row id."""
        cls.ensure_table_exists()
        from app.models.database import Database

        status = status if status in TASK_STATUSES else 'todo'
        priority = priority if priority in TASK_PRIORITIES else 'medium'
        is_done = 1 if status == 'done' else 0
        due_date = due_date or None
        description = description or None

        db = Database()
        try:
            return db.execute(
                "INSERT INTO dashboard_tasks "
                "(user_id, title, description, status, priority, due_date, is_done) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (user_id, title, description, status, priority, due_date, is_done),
            )
        finally:
            db.close()

    @classmethod
    def find_for_user(cls, user_id: int, limit: int = 50):
        """Return a user's tasks: unfinished first, newest first."""
        cls.ensure_table_exists()
        from app.models.database import Database

        db = Database()
        try:
            return db.fetch_all(
                "SELECT * FROM dashboard_tasks WHERE user_id = %s "
                "ORDER BY is_done ASC, created_at DESC LIMIT %s",
                (user_id, limit),
            )
        finally:
            db.close()

    @classmethod
    def toggle(cls, task_id: int, user_id: int):
        """Flip a task's done state. Scoped to the owning user."""
        cls.ensure_table_exists()
        from app.models.database import Database

        db = Database()
        try:
            db.execute(
                "UPDATE dashboard_tasks SET is_done = 1 - is_done "
                "WHERE id = %s AND user_id = %s",
                (task_id, user_id),
            )
            row = db.fetch_one(
                "SELECT is_done FROM dashboard_tasks WHERE id = %s AND user_id = %s",
                (task_id, user_id),
            )
            return row['is_done'] if row else None
        finally:
            db.close()

    @classmethod
    def update(cls, task_id: int, user_id: int, status=None, due_date=None,
               priority=None, title=None, description=None):
        """Update a task's fields. Scoped to the user.

        Only the arguments that are passed (not None) are written, so a
        status-only move won't wipe the title/description (and vice versa).
        Returns the updated row, or None if nothing matched. Pass `due_date=''`
        or `description=''` to clear those; leave them None to keep them.
        """
        cls.ensure_table_exists()
        from app.models.database import Database

        sets = []
        params = []
        if title is not None:
            sets.append("title = %s")
            params.append(title[:255])
        if description is not None:
            sets.append("description = %s")
            params.append(description or None)
        if status is not None:
            status = status if status in TASK_STATUSES else 'todo'
            sets.append("status = %s")
            params.append(status)
            sets.append("is_done = %s")
            params.append(1 if status == 'done' else 0)
        if due_date is not None:
            sets.append("due_date = %s")
            params.append(due_date or None)
        if priority is not None:
            priority = priority if priority in TASK_PRIORITIES else 'medium'
            sets.append("priority = %s")
            params.append(priority)

        if not sets:
            return None

        params.extend([task_id, user_id])

        db = Database()
        try:
            db.execute(
                f"UPDATE dashboard_tasks SET {', '.join(sets)} "
                "WHERE id = %s AND user_id = %s",
                tuple(params),
            )
            return db.fetch_one(
                "SELECT * FROM dashboard_tasks WHERE id = %s AND user_id = %s",
                (task_id, user_id),
            )
        finally:
            db.close()

    @classmethod
    def delete(cls, task_id: int, user_id: int):
        """Delete a task. Scoped to the owning user."""
        cls.ensure_table_exists()
        from app.models.database import Database

        db = Database()
        try:
            return db.execute(
                "DELETE FROM dashboard_tasks WHERE id = %s AND user_id = %s",
                (task_id, user_id),
            )
        finally:
            db.close()
