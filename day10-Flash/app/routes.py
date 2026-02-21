from flask import Blueprint, render_template, request, redirect, flash
from .models import Task
from . import db

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        task_content = request.form['content']

        # Validation
        if not task_content.strip():
            flash("Task cannot be empty!", "error")
            return redirect('/')

        new_task = Task(content=task_content)
        db.session.add(new_task)
        db.session.commit()

        flash("Task added successfully!", "success")
        return redirect('/')

    tasks = Task.query.order_by(Task.date_created).all()
    return render_template('index.html', tasks=tasks)


@main.route('/delete/<int:id>')
def delete(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()

    flash("Task deleted successfully!", "success")
    return redirect('/')


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
