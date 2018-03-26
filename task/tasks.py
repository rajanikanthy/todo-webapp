from models import DatabaseConnection
from users import UserRepository
from datetime import datetime


class TaskRepository:

    def __init__(self, db_conn, username):
        self.username = username
        self.db_conn = db_conn

    def tasks(self):
        ur = UserRepository(username=self.username, db_conn=self.db_conn)
        u = ur.find_one()
        if not u:
            raise Exception("No user found")
        else:
            rv = self.db_conn.get_db()
            c = rv.cursor()
            t = (u["id"],)
            c.execute("SELECT id, user_id, title, description, created_date, completed_date FROM tasks WHERE user_id = ?", t)
            u = c.fetchall()
            c.close()
            return u

    def add_task(self, title, description):
        ur = UserRepository(username=self.username, db_conn=self.db_conn)
        u = ur.find_one()
        if not u:
            raise Exception("No user found")
        else:
            rv = self.db_conn.get_db()
            t = (u["id"], title, description, datetime.utcnow())
            query = """
                INSERT INTO tasks(user_id, title, description, created_date, completed_date) VALUES (?,?,?,?,NULL)
            """
            rv.execute(query, t)
            rv.commit()

