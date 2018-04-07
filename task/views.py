import os
from flask import Flask, render_template, request, flash, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'tasks.db'),
    SECRET_KEY='task_development_key',
    USERNAME='admin',
    PASSWORD='default',
    SQLALCHEMY_DATABASE_URI='sqlite:////' + os.path.join(app.root_path, 'tasks.db')
))

db = SQLAlchemy(app)


class User(db.Model):

    __tablename__ = "users"
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    username = db.Column('username', db.Unicode)
    password = db.Column('password', db.Unicode)
    email_addr = db.Column('email_addr', db.Unicode)
    tasks = db.relationship('Task', backref="creator", lazy='dynamic')

    def __init__(self, username, password, email_addr):
        self.username = username
        self.password = password
        self.email_addr = email_addr


class Task(db.Model):

    __tablename__ = "tasks"
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    title = db.Column("title", db.Unicode)
    description = db.Column("description", db.Unicode)
    created_date = db.Column("created_date", db.DateTime, default=datetime.utcnow())
    completed_date = db.Column("completed_date", db.DateTime)

    def __init__(self, title, description):
        self.title = title
        self.description = description


class TaskRepository:

    def __init__(self, username):
        self.username = username

    def tasks(self):
        ur = UserRepository(username=self.username)
        u = ur.find_one()
        if not u:
            raise Exception("No user found")
        else:
            return Task.query.filter_by(user_id=u.id).all()

    def find_by_id(self, id):
        ur = UserRepository(username=self.username)
        u = ur.find_one()
        if not u:
            raise Exception("No user found")
        else:
            return Task.query.filter_by(user_id=u.id, id=id).first()

    def add_task(self, title, description):
        ur = UserRepository(username=self.username)
        u = ur.find_one()
        if not u:
            raise Exception("No user found")
        else:
            task = Task(title=title, description=description)
            task.creator = u;
            db.session.add(task)
            db.session.commit()

    def edit_task(self, id, title, description, done):
        ur = UserRepository(username=self.username)
        u = ur.find_one()
        if not u:
            raise Exception("no user found")
        else:
            t = self.find_by_id(id)
            if t:
                t.title = title
                t.description = description
                if done == "on":
                    t.completed_date = datetime.utcnow()
                db.session.commit()

    def delete_task(self, id):
        ur = UserRepository(username=self.username)
        u = ur.find_one()
        if not u:
            raise Exception("no user found")
        else:
            t = self.find_by_id(id)
            if t:
                db.session.delete(t)
                db.session.commit()

class UserRepository:

    def __init__(self, username):
        self.username = username

    def find_one(self):
        return User.query.filter_by(username=self.username).first()

    def register(self, password, email_addr):
        if self.find_one():
            raise Exception("Username already exists!!")
        new_user = User(username=self.username, password=password, email_addr=email_addr)
        db.session.add(new_user)
        db.session.commit()



# db_connection = DatabaseConnection(app.config['DATABASE'])

# @app.cli.command('initdb')
# def initdb_command():
#     with app.open_resource('schema.sql', mode='r') as f:
#         db_connection.init_db(f.read())


@app.route("/")
def index():
    return render_template("login.html")


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method =='GET':
        return render_template("register.html")
    else:
        username = request.form["username"]
        password = request.form["password"]
        email_addr = request.form["email_addr"]
        ur = UserRepository(username=username)
        try:
            ur.register(password=password, email_addr=email_addr)
        except Exception as e:
            flash(e.message)
        return redirect(url_for("login"))


@app.route("/login", methods=["POST", "GET"])
def login():
    error = None
    if request.method == 'GET':
        return render_template("login.html")
    else:
        username = request.form["username"]
        password = request.form["password"]
        ur = UserRepository(username=username)
        tr = TaskRepository(username=username)
        u = ur.find_one()
        if u and u.password == password:
            session['username'] = username
            tasks = tr.tasks()
            return render_template("tasks.html", tasks=tasks)
        else:
            flash("Invalid credentials")
            return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect(url_for("login"))


@app.route("/tasks")
def tasks():
    ur = UserRepository(username=session['username'])
    tr = TaskRepository(username=session['username'])
    u = ur.find_one()
    tsks = tr.tasks()
    return render_template("tasks.html", tasks=tsks)

@app.route("/add_tasks", methods=["POST","GET"])
def add_tasks():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        tr = TaskRepository(username=session['username'])
        tr.add_task(title=title, description=description)
        flash("Task added successfully")
        return redirect(url_for("tasks"))
    else:
        return render_template("task.html")


@app.route("/edit_task/<id>", methods=["POST", "GET"])
def edit_task(id):
    tr = TaskRepository(username=session['username'])
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        done = request.form['done']
        tr.edit_task(id=id, title=title, description=description, done=done)
        flash("Task updated successfully")
        return redirect(url_for("tasks"))
    else:
        t = tr.find_by_id(id)
        return render_template("task.html", editmode=True, task=t)


@app.route("/delete_task/<id>", methods=["GET"])
def delete_task(id):
    tr = TaskRepository(username=session['username'])
    tr.delete_task(id)
    return redirect(url_for("tasks"))

@app.route("/about")
def about():
    return "This app is about tasks"

