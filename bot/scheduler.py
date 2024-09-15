from apscheduler.schedulers.asyncio import AsyncIOScheduler
from bot.tasks import get_tasks
from datetime import datetime, timedelta
from telegram.ext import Application
from database.db import get_session 
from database.models import Task

# Асинхронная функция для отправки напоминаний пользователям
async def notify_users(application: Application):

    session = get_session()  # Открываем сессию для базы данных напрямую через функцию get_session()
    tasks = session.query(Task).all()

    now = datetime.now()


    for task in tasks:
        if task.deadline and not task.completed:
            time_left = task.deadline - now

            # Напоминание за 24 часа
            if time_left <= timedelta(hours=24) and not task.reminder_24h_sent:
                task.reminder_24h_sent = True  # Отметим, что напоминание отправлено
                await application.bot.send_message(chat_id=task.user_id, text=f"Напоминание: осталось меньше 24 часов для задачи '{task.description}'")

            # Напоминание за 1 час
            elif time_left <= timedelta(hours=1) and not task.reminder_1h_sent:
                task.reminder_1h_sent = True  # Отметим, что напоминание отправлено
                await application.bot.send_message(chat_id=task.user_id, text=f"Напоминание: осталось меньше часа для задачи '{task.description}'")

            # Напоминание за 15 минут
            elif time_left <= timedelta(minutes=15) and not task.reminder_15m_sent:
                task.reminder_15m_sent = True  # Отметим, что напоминание отправлено
                await application.bot.send_message(chat_id=task.user_id, text=f"Напоминание: осталось 15 минут для задачи '{task.description}'")

    session.commit()  # Сохраняем изменения в базе данных
    session.close()

# Запуск планировщика
def start_scheduler(application: Application):
    scheduler = AsyncIOScheduler()

    # Планируем выполнение notify_users каждую минуту
    scheduler.add_job(notify_users, 'interval', minutes=1, args=[application])

    # Запускаем планировщик
    scheduler.start()
