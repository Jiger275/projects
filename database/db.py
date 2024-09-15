from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, Task, UserState

DATABASE_URL = 'sqlite:///tasks.db'

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)

def get_session():
    return Session()

# Работа с состояниями пользователей
def get_user_state(user_id):
    session = get_session()
    state = session.query(UserState).filter_by(user_id=user_id).first()
    session.close()
    return state

def set_user_state(user_id, action, task_id=None):
    session = get_session()
    state = session.query(UserState).filter_by(user_id=user_id).first()
    if state:
        state.action = action
        state.task_id = task_id
    else:
        state = UserState(user_id=user_id, action=action, task_id=task_id)
        session.add(state)
    session.commit()
    session.close()

def clear_user_state(user_id):
    session = get_session()
    state = session.query(UserState).filter_by(user_id=user_id).first()
    if state:
        session.delete(state)
        session.commit()
    session.close()
