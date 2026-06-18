from app.models.base_model import BaseModel
from app.models.database import ensure_database_exists


class DeactivatedAccount(BaseModel):
    @property
    def table(self):
        return 'deactivated_accounts'

    @classmethod
    def ensure_table_exists(cls):
        ensure_database_exists()
        inst = cls()
        inst.execute(
            "CREATE TABLE IF NOT EXISTS deactivated_accounts ("
            "id INT AUTO_INCREMENT PRIMARY KEY,"
            "user_id INT NOT NULL UNIQUE,"
            "reason TEXT NULL,"
            "deactivated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,"
            "INDEX idx_deactivated_user (user_id)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
        )

    def deactivate(self, user_id, reason=None):
        self.ensure_table_exists()
        return self.execute(
            "INSERT INTO deactivated_accounts (user_id, reason) VALUES (%s, %s) "
            "ON DUPLICATE KEY UPDATE reason = VALUES(reason), deactivated_at = CURRENT_TIMESTAMP",
            (user_id, reason),
        )

    def is_deactivated(self, user_id):
        self.ensure_table_exists()
        r = self.fetch_one(
            "SELECT id FROM deactivated_accounts WHERE user_id = %s LIMIT 1",
            (user_id,),
        )
        return bool(r)

    def get_by_user(self, user_id):
        self.ensure_table_exists()
        return self.fetch_one(
            "SELECT * FROM deactivated_accounts WHERE user_id = %s LIMIT 1",
            (user_id,),
        )


# module-level helpers
_da = DeactivatedAccount()


def ensure_table_exists():
    return DeactivatedAccount.ensure_table_exists()


def deactivate_account(user_id, reason=None):
    return _da.deactivate(user_id, reason)


def is_deactivated(user_id):
    return _da.is_deactivated(user_id)


def get_by_user(user_id):
    return _da.get_by_user(user_id)
