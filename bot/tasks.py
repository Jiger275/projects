from database.db import get_session
from database.models import Task
import datetime

def add_task(description, deadline, user_id):
    session = get_session()
    
    task = Task(description=description, deadline=deadline, user_id=user_id)
    session.add(task)
    session.commit()
    session.close()

def get_tasks(filter_type=None):
    session = get_session()
    now = datetime.datetime.now()
    
    query = session.query(Task)
    
    if filter_type == 'in_progress':
        query = query.filter(Task.completed == False, Task.deadline >= now)  # Задачи в процессе (не завершены и не просрочены)
    elif filter_type == 'completed':
        query = query.filter(Task.completed == True)  # Завершенные задачи
    elif filter_type == 'overdue':
        query = query.filter(Task.completed == False, Task.deadline < now)  # Просроченные задачи
    else:
        query = query.order_by(Task.deadline)  # Все задачи без фильтрации
    
    tasks = query.all()
    session.close()
    return tasks

def delete_task(task_id):
    session = get_session()
    task = session.query(Task).filter(Task.id == task_id).first()
    if task:
        session.delete(task)
        session.commit()
    session.close()

def edit_task(task_id, description=None, deadline=None):
    session = get_session()
    task = session.query(Task).filter(Task.id == task_id).first()
    if task:
        if description:
            task.description = description
        if deadline:
            task.deadline = deadline
        session.commit()
    session.close()

def complete_task(task_id):
    session = get_session()
    task = session.query(Task).filter(Task.id == task_id).first()
    if task:
        task.completed = True
        session.commit()
    session.close()
