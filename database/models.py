from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
import datetime
from sqlalchemy.orm import relationship

Base = declarative_base()

class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    description = Column(String, nullable=False)
    deadline = Column(DateTime, nullable=True)
    completed = Column(Boolean, default=False)
    user_id = Column(Integer, nullable=False)
    reminder_24h_sent = Column(Boolean, default=False)
    reminder_1h_sent = Column(Boolean, default=False)   
    reminder_15m_sent = Column(Boolean, default=False)

# Модель для состояния пользователя
class UserState(Base):
    __tablename__ = 'user_states'

    user_id = Column(Integer, primary_key=True)
    action = Column(String, nullable=False)
    task_id = Column(Integer, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<UserState(user_id={self.user_id}, action={self.action}, task_id={self.task_id})>"

