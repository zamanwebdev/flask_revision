from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import date

app = Flask(__name__)
app.secret_key = "supersecretkey"


# -----------------------
# Database Init
# -----------------------
def init_db():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    # Users table with role
    cur.execute("""
                CREATE TABLE IF NOT EXISTS users
                (
                    id
                    INTEGER
                    PRIMARY
                    KEY
                    AUTOINCREMENT,
                    username
                    TEXT
                    UNIQUE
                    NOT
                    NULL,
                    password
                    TEXT
                    NOT
                    NULL,
                    role
                    TEXT
                    DEFAULT
                    'user'
                )
                """)

    # Tasks table with due_date + priority
    cur.execute("""
                CREATE TABLE IF NOT EXISTS tasks
                (
                    id
                    INTEGER
                    PRIMARY
                    KEY
                    AUTOINCREMENT,
                    title
                    TEXT
                    NOT
                    NULL,
                    status
                    TEXT
                    DEFAULT
                    'pending',
                    user_id
                    INTEGER
                    NOT
                    NULL,
                    due_date
                    TEXT,
                    priority
                    TEXT
                    DEFAULT
                    'Medium'
                )
                """)

    conn.commit()
    conn.close()


init_db()


# -----------------------
# Home
# -----------------------
@app.route('/')
def home():
    return redirect('/login')


# -----------------------
# Register
# -----------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()

        # Check duplicate username
        cur.execute("SELECT * FROM users WHERE username=?", (username,))
        if cur.fetchone():
            conn.close()
            return render_template("register.html", error="Username already exists!")

        cur.execute("INSERT INTO users (username, password) VALUES (?,?)",
                    (username, password))
        conn.commit()
        conn.close()
        return redirect('/login')

    return render_template('register.html', error=None)


# -----------------------
# Login
# -----------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?",
                    (username, password))
        user = cur.fetchone()
        conn.close()

        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[3]
            return redirect('/dashboard')

    return render_template('login.html')


# -----------------------
# Dashboard
# -----------------------
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    search = request.args.get('search')
    filter_status = request.args.get('status')

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    if session.get('role') == 'admin':
        query = "SELECT tasks.id, tasks.title, tasks.status, users.username, tasks.due_date, tasks.priority FROM tasks JOIN users ON tasks.user_id=users.id"
        params = ()
        if filter_status:
            query += " WHERE tasks.status=?"
            params = (filter_status,)
        if search:
            if params:
                query += " AND tasks.title LIKE ?"
                params = (filter_status, f"%{search}%")
            else:
                query += " WHERE tasks.title LIKE ?"
                params = (f"%{search}%",)
        cur.execute(query, params)
        tasks = cur.fetchall()
    else:
        query = "SELECT * FROM tasks WHERE user_id=?"
        params = [session['user_id']]
        if filter_status:
            query += " AND status=?"
            params.append(filter_status)
        if search:
            query += " AND title LIKE ?"
            params.append(f"%{search}%")
        cur.execute(query, tuple(params))
        tasks = cur.fetchall()

    if session.get('role') != 'admin':
        cur.execute("SELECT COUNT(*) FROM tasks WHERE user_id=?",
                    (session['user_id'],))
        total = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM tasks WHERE user_id=? AND status='completed'",
                    (session['user_id'],))
        completed = cur.fetchone()[0]
        pending = total - completed
    else:
        total = completed = pending = None

    conn.close()
    today_str = date.today().isoformat()
    return render_template("dashboard.html", tasks=tasks, total=total, completed=completed, pending=pending,
                           today=today_str)


# -----------------------
# Add Task
# -----------------------
@app.route('/add', methods=['POST'])
def add_task():
    if 'user_id' not in session:
        return redirect('/login')

    title = request.form['title']
    due_date = request.form.get('due_date')
    priority = request.form.get('priority', 'Medium')

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("INSERT INTO tasks (title, user_id, due_date, priority) VALUES (?,?,?,?)",
                (title, session['user_id'], due_date, priority))
    conn.commit()
    conn.close()

    return redirect('/dashboard')


# -----------------------
# Complete Task
# -----------------------
@app.route('/complete/<int:id>')
def complete_task(id):
    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("UPDATE tasks SET status='completed' WHERE id=? AND user_id=?",
                (id, session['user_id']))
    conn.commit()
    conn.close()
    return redirect('/dashboard')


# -----------------------
# Edit Task
# -----------------------
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_task(id):
    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    if request.method == 'POST':
        new_title = request.form['title']
        new_due_date = request.form.get('due_date')
        new_priority = request.form.get('priority', 'Medium')
        cur.execute("UPDATE tasks SET title=?, due_date=?, priority=? WHERE id=? AND user_id=?",
                    (new_title, new_due_date, new_priority, id, session['user_id']))
        conn.commit()
        conn.close()
        return redirect('/dashboard')

    cur.execute("SELECT * FROM tasks WHERE id=? AND user_id=?",
                (id, session['user_id']))
    task = cur.fetchone()
    conn.close()
    return render_template('edit.html', task=task)


# -----------------------
# Delete Task
# -----------------------
@app.route('/delete/<int:id>')
def delete_task(id):
    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id=? AND user_id=?",
                (id, session['user_id']))
    conn.commit()
    conn.close()
    return redirect('/dashboard')


# -----------------------
# Logout
# -----------------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


if __name__ == "__main__":
    app.run(debug=True)
