from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "supersecretkey"


# ---------- DATABASE INIT ----------
def init_db():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            due_date TEXT,
            user_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()

init_db()


# ---------- HOME ----------
@app.route("/")
def index():
    return render_template("index.html")


# ---------- REGISTER ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        try:
            cur.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed_password)
            )
            conn.commit()
            flash("Registration Successful! Please Login.", "success")
            return redirect("/login")
        except sqlite3.IntegrityError:
            flash("Username already exists!", "danger")

        conn.close()

    return render_template("register.html")


# ---------- LOGIN ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cur.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session["user_id"] = user[0]
            session["username"] = user[1]
            session["role"] = user[3]
            flash("Login Successful!", "success")
            return redirect("/dashboard")
        else:
            flash("Invalid Credentials!", "danger")

    return render_template("login.html")


# ---------- DASHBOARD ----------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    search = request.args.get("search", "")

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    if search:
        cur.execute("""
            SELECT * FROM tasks
            WHERE user_id=? AND title LIKE ?
        """, (session["user_id"], f"%{search}%"))
    else:
        cur.execute("SELECT * FROM tasks WHERE user_id=?",
                    (session["user_id"],))

    tasks = cur.fetchall()

    # Stats
    cur.execute("SELECT COUNT(*) FROM tasks WHERE user_id=?",
                (session["user_id"],))
    total = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*) FROM tasks
        WHERE user_id=? AND status='Completed'
    """, (session["user_id"],))
    completed = cur.fetchone()[0]

    conn.close()

    return render_template(
        "dashboard.html",
        tasks=tasks,
        total=total,
        completed=completed
    )


# ---------- ADD TASK ----------
@app.route("/add_task", methods=["POST"])
def add_task():
    if "user_id" not in session:
        return redirect("/login")

    title = request.form["title"]
    due_date = request.form["due_date"]

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO tasks (title, due_date, status, user_id)
        VALUES (?, ?, ?, ?)
    """, (title, due_date, "Pending", session["user_id"]))

    conn.commit()
    conn.close()

    flash("Task Added Successfully!", "success")
    return redirect("/dashboard")


# ---------- EDIT TASK ----------
@app.route("/edit_task/<int:id>", methods=["GET", "POST"])
def edit_task(id):
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM tasks WHERE id=? AND user_id=?",
                (id, session["user_id"]))
    task = cur.fetchone()

    if not task:
        conn.close()
        flash("Unauthorized Access!", "danger")
        return redirect("/dashboard")

    if request.method == "POST":
        title = request.form["title"]
        due_date = request.form["due_date"]

        cur.execute("UPDATE tasks SET title=?, due_date=? WHERE id=?",
                    (title, due_date, id))
        conn.commit()
        conn.close()

        flash("Task Updated Successfully!", "success")
        return redirect("/dashboard")

    conn.close()
    return render_template("edit_task.html", task=task)


# ---------- DELETE TASK ----------
@app.route("/delete_task/<int:id>")
def delete_task(id):
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("DELETE FROM tasks WHERE id=? AND user_id=?",
                (id, session["user_id"]))
    conn.commit()
    conn.close()

    flash("Task Deleted Successfully!", "warning")
    return redirect("/dashboard")


# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged Out Successfully!", "warning")
    return redirect("/")
@app.route("/complete_task/<int:id>")
def complete_task(id):
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("""
        UPDATE tasks SET status='Completed'
        WHERE id=? AND user_id=?
    """, (id, session["user_id"]))

    conn.commit()
    conn.close()

    flash("Task Marked as Completed!", "success")
    return redirect("/dashboard")


if __name__ == "__main__":
    app.run(debug=True)