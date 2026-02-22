from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey"


# -----------------------
# Database Init Function
# -----------------------

def init_db():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        user_id INTEGER NOT NULL
    )
    """)

    conn.commit()
    conn.close()

init_db()


# -----------------------
# Home Redirect
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

        cur.execute("INSERT INTO users (username, password) VALUES (?,?)",
                    (username, password))

        conn.commit()
        conn.close()

        return redirect('/login')

    return render_template('register.html')


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
            return redirect('/dashboard')

    return render_template('login.html')


# -----------------------
# Dashboard
# -----------------------

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    filter_status = request.args.get('status')

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    if filter_status:
        cur.execute("SELECT * FROM tasks WHERE user_id=? AND status=?",
                    (session['user_id'], filter_status))
    else:
        cur.execute("SELECT * FROM tasks WHERE user_id=?",
                    (session['user_id'],))

    tasks = cur.fetchall()
    conn.close()

    return render_template('dashboard.html', tasks=tasks)


# -----------------------
# Add Task
# -----------------------

@app.route('/add', methods=['POST'])
def add_task():
    if 'user_id' not in session:
        return redirect('/login')

    title = request.form['title']

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    cur.execute("INSERT INTO tasks (title, user_id) VALUES (?,?)",
                (title, session['user_id']))

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
# Logout
# -----------------------

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


if __name__ == "__main__":
    app.run(debug=True)
