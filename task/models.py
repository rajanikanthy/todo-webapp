import sqlite3


class DatabaseConnection:
    def __init__(self, database):
        self.database = database
        self.rv = sqlite3.connect(self.database, check_same_thread=False)
        self.rv.row_factory = sqlite3.Row

    def init_db(self, schema):
        db = self.get_db()
        db.cursor().executescript(schema)
        db.commit()

    def get_db(self):
        if not self.rv:
            self.rv = sqlite3.connect(self.database, check_same_thread=False)
            self.rv.row_factory = sqlite3.Row
        return self.rv

    def close_db(self):
        if self.rv:
            self.rv.close()