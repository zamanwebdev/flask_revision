from flask import Blueprint, render_template, request, redirect, flash, session
from .models import Task, User
from . import db
from werkzeug.security import generate_password_hash, check_password_hash

main = Blueprint('main', __name__)

# ---------------- HOME / DASHBOARD ----------------
@main.route('/')
def index():
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    tasks = Task.query.filter_by(user_id=user_id).order_by(Task.date_created).all()

    total_tasks = len(tasks)

    return render_template(
        'index.html',
        tasks=tasks,
        total_tasks=total_tasks
    )


# ---------------- REGISTER ----------------
@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash("All fields are required!", "error")
            return redirect('/register')

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists!", "error")
            return redirect('/register')

        hashed_password = generate_password_hash(password)

        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please login.", "success")
        return redirect('/login')

    return render_template('register.html')


# ---------------- LOGIN ----------------
@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash("Login successful!", "success")
            return redirect('/')
        else:
            flash("Invalid credentials!", "error")
            return redirect('/login')

    return render_template('login.html')


# ---------------- LOGOUT ----------------
@main.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully!", "success")
    return redirect('/login')


# ---------------- ADD TASK ----------------
@main.route('/add', methods=['POST'])
def add_task():
    if 'user_id' not in session:
        return redirect('/login')

    task_content = request.form['content']

    if not task_content.strip():
        flash("Task cannot be empty!", "error")
        return redirect('/')

    new_task = Task(
        content=task_content,
        user_id=session['user_id']
    )

    db.session.add(new_task)
    db.session.commit()

    flash("Task added successfully!", "success")
    return redirect('/')


# ---------------- DELETE ----------------
@main.route('/delete/<int:id>')
def delete(id):
    if 'user_id' not in session:
        return redirect('/login')

    task = Task.query.get_or_404(id)

    if task.user_id != session['user_id']:
        flash("Unauthorized action!", "error")
        return redirect('/')

    db.session.delete(task)
    db.session.commit()

    flash("Task deleted!", "success")
    return redirect('/')


# ---------------- UPDATE ----------------
@main.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    if 'user_id' not in session:
        return redirect('/login')

    task = Task.query.get_or_404(id)

    if task.user_id != session['user_id']:
        flash("Unauthorized action!", "error")
        return redirect('/')

    if request.method == 'POST':
        new_content = request.form['content']

        if not new_content.strip():
            flash("Task cannot be empty!", "error")
            return redirect(f'/update/{id}')

        task.content = new_content
        db.session.commit()

        flash("Task updated!", "success")
        return redirect('/')

    return render_template('update.html', task=task)
