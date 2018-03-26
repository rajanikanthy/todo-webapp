import os
from flask import Flask, render_template, request, flash, session, redirect, url_for
from models import DatabaseConnection
from users import UserRepository
from tasks import TaskRepository

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'tasks.db'),
    SECRET_KEY='task_development_key',
    USERNAME='admin',
    PASSWORD='default'
))

db_connection = DatabaseConnection(app.config['DATABASE'])

@app.cli.command('initdb')
def initdb_command():
    with app.open_resource('schema.sql', mode='r') as f:
        db_connection.init_db(f.read())


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
        ur = UserRepository(username=username, db_conn=db_connection)
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
        ur = UserRepository(username=username, db_conn=db_connection)
        tr = TaskRepository(username=username,db_conn=db_connection)
        u = ur.find_one()
        if u and u["password"] == password:
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
    ur = UserRepository(username=session['username'], db_conn=db_connection)
    tr = TaskRepository(username=session['username'], db_conn=db_connection)
    u = ur.find_one()
    tsks = tr.tasks()
    return render_template("tasks.html", tasks=tsks)

@app.route("/add_tasks", methods=["POST","GET"])
def add_tasks():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        tr = TaskRepository(db_conn=db_connection, username=session['username'])
        tr.add_task(title=title, description=description)
        flash("Task added successfully")
        return redirect(url_for("tasks"))
    else:
        return render_template("addTask.html")

@app.route("/about")
def about():
    return "This app is about tasks"

