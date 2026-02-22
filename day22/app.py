from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secretkey"


# =========================
# DATABASE INIT
# =========================
def init_db():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT DEFAULT 'user'
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS tasks(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        status TEXT DEFAULT 'pending',
        user_id INTEGER,
        priority TEXT,
        due_date TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS comments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER,
        user_id INTEGER,
        note TEXT
    )
    """)

    conn.commit()
    conn.close()


init_db()


# =========================
# HOME
# =========================
@app.route('/')
def index():
    return render_template('index.html')


# =========================
# REGISTER
# =========================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO users(username,password) VALUES(?,?)",
                        (username, password))
            conn.commit()
        except:
            return "Username already exists"
        conn.close()
        return redirect('/login')

    return render_template('register.html')


# =========================
# LOGIN
# =========================
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
        else:
            return "Invalid credentials"

    return render_template('login.html')


# =========================
# LOGOUT
# =========================
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# =========================
# DASHBOARD
# =========================
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    if session['role'] == 'admin':
        cur.execute("SELECT * FROM tasks")
    else:
        cur.execute("SELECT * FROM tasks WHERE user_id=?",
                    (session['user_id'],))

    tasks = cur.fetchall()
    conn.close()

    return render_template('dashboard.html', tasks=tasks)


# =========================
# ADD TASK
# =========================
@app.route('/add', methods=['POST'])
def add_task():
    title = request.form['title']
    priority = request.form['priority']
    due_date = request.form['due_date']

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO tasks(title,user_id,priority,due_date)
    VALUES(?,?,?,?)
    """, (title, session['user_id'], priority, due_date))

    conn.commit()
    conn.close()
    return redirect('/dashboard')


# =========================
# COMPLETE TASK
# =========================
@app.route('/complete/<int:id>')
def complete_task(id):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("UPDATE tasks SET status='completed' WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/dashboard')


# =========================
# DELETE TASK
# =========================
@app.route('/delete/<int:id>')
def delete_task(id):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/dashboard')


# =========================
# EDIT TASK
# =========================
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_task(id):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    if request.method == 'POST':
        title = request.form['title']
        priority = request.form['priority']
        due_date = request.form['due_date']

        cur.execute("""
        UPDATE tasks
        SET title=?, priority=?, due_date=?
        WHERE id=?
        """, (title, priority, due_date, id))
        conn.commit()
        conn.close()
        return redirect('/dashboard')

    cur.execute("SELECT * FROM tasks WHERE id=?", (id,))
    task = cur.fetchone()
    conn.close()

    return render_template('edit_task.html', task=task)


# =========================
# COMMENTS
# =========================
@app.route('/comments/<int:task_id>', methods=['GET', 'POST'])
def task_comments(task_id):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    if request.method == 'POST':
        note = request.form['note']
        cur.execute("INSERT INTO comments(task_id,user_id,note) VALUES(?,?,?)",
                    (task_id, session['user_id'], note))
        conn.commit()

    cur.execute("""
    SELECT comments.id, comments.note, users.username
    FROM comments
    JOIN users ON comments.user_id = users.id
    WHERE task_id=?
    """, (task_id,))
    comments = cur.fetchall()
    conn.close()

    return render_template('comments.html',
                           comments=comments,
                           task_id=task_id)


@app.route('/comments/delete/<int:id>')
def delete_comment(id):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM comments WHERE id=? AND user_id=?",
                (id, session['user_id']))
    conn.commit()
    conn.close()
    return redirect(request.referrer)


if __name__ == '__main__':
    app.run(debug=True)
