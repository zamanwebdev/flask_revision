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
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'user'
    )
    """)

    # Tasks table with due_date
    cur.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        user_id INTEGER NOT NULL,
        due_date TEXT
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

        # Check if username exists
        cur.execute("SELECT * FROM users WHERE username=?", (username,))
        existing_user = cur.fetchone()

        if existing_user:
            conn.close()
            return render_template("register.html", error="Username already exists! Please choose another.")

        # Insert new user
        cur.execute("INSERT INTO users (username, password) VALUES (?,?)",
                    (username, password))
        conn.commit()
        conn.close()
        return redirect('/login')

    return render_template('register.html', error=None)

# ----------------------
