from flask import Blueprint, render_template, request, redirect, flash
from .models import Task, User
from . import db
from werkzeug.security import generate_password_hash

main = Blueprint('main', __name__)

# ---------------- HOME ----------------
@main.route('/')
def index():
    tasks = Task.query.order_by(Task.date_created).all()
    return render_template('index.html', tasks=tasks)


# ---------------- ADD TASK ----------------
@main.route('/add', methods=['POST'])
def add_task():
    task_content = request.form['content']

    if not task_content.strip():
        flash("Task cannot be empty!", "error")
        return redirect('/')

    new_task = Task(content=task_content)
    db.session.add(new_task)
    db.session.commit()

    flash("Task added successfully!", "success")
    return redirect('/')


# ---------------- DELETE ----------------
@main.route('/delete/<int:id>')
def delete(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()

    flash("Task deleted successfully!", "success")
    return redirect('/')


# ---------------- UPDATE ----------------
@main.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Task.query.get_or_404(id)

    if request.method == 'POST':
        new_content = request.form['content']

        if not new_content.strip():
            flash("Task cannot be empty!", "error")
            return redirect(f'/update/{id}')

        task.content = new_content
        db.session.commit()

        flash("Task updated successfully!", "success")
        return redirect('/')

    return render_template('update.html', task=task)


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

        flash("Registration successful!", "success")
        return redirect('/')

    return render_template('register.html')
