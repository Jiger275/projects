import logging
import os

# Создаем директорию для логов, если она не существует
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Настраиваем логирование
log_file = os.path.join(log_dir, 'bot.log')
logging.basicConfig(
    level=logging.INFO,  # Уровень логирования
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),  # Логирование в файл
        logging.StreamHandler()  # Вывод логов в консоль
    ]
)

# Основной логгер для проекта
logger = logging.getLogger("TaskBot")
