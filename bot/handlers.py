import re
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from bot.tasks import get_tasks, add_task, delete_task, edit_task, complete_task
from database.db import get_user_state, set_user_state, clear_user_state
from config.config import config
from logger.logger import logger
from datetime import datetime

# Функция для отображения основного меню
async def show_main_menu(update, context):
    logger.info(f"Пользователь {update.effective_user.id} открыл основное меню")
    keyboard = [
        [InlineKeyboardButton("Добавить задачу", callback_data='add_task')],
        [InlineKeyboardButton("Просмотреть задачи", callback_data='view_tasks')],
        [InlineKeyboardButton("Удалить задачу", callback_data='delete_task')],
        [InlineKeyboardButton("Редактировать задачу", callback_data='edit_task')],
        [InlineKeyboardButton("Завершить задачу", callback_data='complete_task')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Выберите действие:', reply_markup=reply_markup)

# Стартовое сообщение
async def start(update: Update, context):
    logger.info(f"Пользователь {update.effective_user.id} начал взаимодействие с ботом")
    await show_main_menu(update, context)

# Функция для отображения меню фильтрации задач
async def show_filter_menu(update, context):
    logger.info(f"Пользователь {update.effective_user.id} выбрал просмотр задач")
    keyboard = [
        [InlineKeyboardButton("В процессе", callback_data='filter_in_progress')],
        [InlineKeyboardButton("Выполнено", callback_data='filter_completed')],
        [InlineKeyboardButton("Просрочено", callback_data='filter_overdue')],
        [InlineKeyboardButton("Все задачи", callback_data='filter_all')],
        [InlineKeyboardButton("Назад", callback_data='back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.reply_text('Выберите фильтр для задач:', reply_markup=reply_markup)

# Функция для отображения задач с фильтрацией
async def show_tasks(update, context, filter_type=None):
    logger.info(f"Пользователь {update.effective_user.id} просматривает задачи с фильтром {filter_type}")
    tasks = get_tasks(filter_type=filter_type)
    keyboard = []
    
    if tasks:
        for task in tasks:
            task_str = f"{task.description} (до {task.deadline.strftime('%d.%m.%Y %H:%M')})"
            keyboard.append([InlineKeyboardButton(task_str, callback_data=f"task_{task.id}")])
    
    keyboard.append([InlineKeyboardButton("Назад", callback_data='back')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.reply_text('Ваши задачи:', reply_markup=reply_markup)

# Обработчик кнопок
async def button_callback(update: Update, context):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    state = get_user_state(user_id) 
    logger.info(f"Пользователь {user_id} нажал на кнопку {query.data}")

    if query.data == 'back':
        clear_user_state(user_id)
        await query.edit_message_text(text="Возвращаемся в главное меню.")
        await show_main_menu(update.callback_query, context)
        return

    # Обработка просмотра задач и фильтрации
    if query.data == 'view_tasks':
        await show_filter_menu(update, context)
    elif query.data == 'filter_in_progress':
        await show_tasks(update, context, filter_type='in_progress')
    elif query.data == 'filter_completed':
        await show_tasks(update, context, filter_type='completed')
    elif query.data == 'filter_overdue':
        await show_tasks(update, context, filter_type='overdue')
    elif query.data == 'filter_all':
        await show_tasks(update, context, filter_type=None)

    # Добавление задачи
    elif query.data == 'add_task':
        set_user_state(user_id, 'add_task')
        logger.info(f"Пользователь {user_id} начал добавление задачи")
        await query.edit_message_text(text="Введите описание задачи и дедлайн в формате: Описание задачи Дата(ДД.ММ.ГГГГ) время (ЧЧ:ММ)")

    # Удаление задачи
    elif query.data == 'delete_task':
        set_user_state(user_id, 'delete_task')  # Устанавливаем состояние для удаления задачи
        logger.info(f"Пользователь {user_id} выбрал удаление задачи")
        await show_tasks(update, context, filter_type=None)  # Показываем задачи для удаления

    # Редактирование задачи
    elif query.data == 'edit_task':
        set_user_state(user_id, 'edit_task')  # Устанавливаем состояние для редактирования задачи
        logger.info(f"Пользователь {user_id} выбрал редактирование задачи")
        await show_tasks(update, context, filter_type=None)  # Показываем задачи для редактирования

    # Завершение задачи
    elif query.data == 'complete_task':
        set_user_state(user_id, 'complete_task')  # Устанавливаем состояние для завершения задачи
        logger.info(f"Пользователь {user_id} выбрал завершение задачи")
        await show_tasks(update, context, filter_type='in_progress')

    # Обработка действий с задачами
    elif query.data.startswith('task_'):
        task_id = int(query.data.split('_')[1])
        logger.info(f"Пользователь {user_id} выбрал задачу с ID {task_id}")

        # Проверяем состояние пользователя перед выполнением действия
        if state and state.action == 'delete_task':
            delete_task(task_id)
            logger.info(f"Пользователь {user_id} удалил задачу с ID {task_id}")
            await query.edit_message_text(text="Задача удалена.")
        elif state and state.action == 'edit_task':
            set_user_state(user_id, 'edit_task', task_id)  
            logger.info(f"Пользователь {user_id} начал редактирование задачи с ID {task_id}")
            await query.edit_message_text(text="Введите новое описание задачи в формате: Описание задачи Дата(ДД.ММ.ГГГГ) время (ЧЧ:ММ)")
            return  
        elif state and state.action == 'complete_task':
            complete_task(task_id)
            logger.info(f"Пользователь {user_id} завершил задачу с ID {task_id}")
            await query.edit_message_text(text="Задача завершена.")

        if state.action != 'edit_task':
            clear_user_state(user_id)
            await show_main_menu(update.callback_query, context)

# Обработчик текстовых сообщений (добавление и редактирование задач)
async def handle_message(update: Update, context):
    user_id = update.effective_user.id
    state = get_user_state(user_id)

    if state:
        action = state.action
        text = update.message.text
        logger.info(f"Пользователь {user_id} ввел текст: {text} в режиме {action}")

        # Регулярное выражение для извлечения даты и времени
        match = re.search(r'(\d{2}\.\d{2}\.\d{4}) (\d{2}:\d{2})$', text)
        
        if not match:
            logger.warning(f"Пользователь {user_id} ввел некорректный формат задачи: {text}")
            await update.message.reply_text("Неверный формат. Попробуйте снова: Описание задачи Дата(ДД.ММ.ГГГГ) время (ЧЧ:ММ)")
            return
        
        description = text[:match.start()].strip()  # Описание задачи до даты
        date_str = match.group(1)  # Дата
        time_str = match.group(2)  # Время

        try:
            deadline_str = f"{date_str} {time_str}"
            deadline = datetime.strptime(deadline_str, "%d.%m.%Y %H:%M")
        except ValueError:
            logger.error(f"Пользователь {user_id} ввел некорректные дату и время: {text}")
            await update.message.reply_text("Неверный формат даты или времени. Попробуйте снова.")
            return

        if action == 'add_task':
            add_task(description, deadline, user_id)
            logger.info(f"Пользователь {user_id} добавил задачу: {description} с дедлайном {deadline.strftime('%д.%м.%Y %H:%M')}")
            await update.message.reply_text(f"Задача добавлена: {description} с дедлайном {deadline.strftime('%d.%m.%Y %H:%M')}")
        elif action == 'edit_task':
            task_id = state.task_id
            edit_task(task_id, description=description, deadline=deadline)
            logger.info(f"Пользователь {user_id} обновил задачу: {description} с новым дедлайном {deadline.strftime('%д.%м.%Y %H:%М')}")
            await update.message.reply_text(f"Задача обновлена: {description} с новым дедлайном {deadline.strftime('%d.%m.%Y %H:%M')}")

        clear_user_state(user_id)
        await show_main_menu(update, context)
