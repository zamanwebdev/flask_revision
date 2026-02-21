from flask import Blueprint, render_template, request, redirect
from .models import Task
from . import db

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        new_task = Task(content=task_content)

        db.session.add(new_task)
        db.session.commit()
        return redirect('/')

    tasks = Task.query.order_by(Task.date_created).all()
    return render_template('index.html', tasks=tasks)


@main.route('/delete/<int:id>')
def delete(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return redirect('/')


@main.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Task.query.get_or_404(id)

    if request.method == 'POST':
        task.content = request.form['content']
        db.session.commit()
        return redirect('/')

    return render_template('update.html', task=task)
