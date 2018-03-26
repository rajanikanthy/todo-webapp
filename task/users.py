from models import DatabaseConnection

class UserRepository:

    def __init__(self, db_conn, username):
        self.username = username
        self.db_conn = db_conn

    def find_one(self):
        rv = self.db_conn.get_db()
        c = rv.cursor()
        t = (self.username, )
        c.execute("SELECT id, username, password, email_addr FROM users WHERE username = ?", t)
        u = c.fetchone()
        c.close()
        return u

    def register(self, password, email_addr):
        if self.find_one():
            raise Exception("Username already exists!!")
        rv = self.db_conn.get_db()
        t = (self.username, password, email_addr, )
        rv.execute("INSERT INTO users (username, password, email_addr) VALUES  (?,?,?)", t)
        rv.commit()