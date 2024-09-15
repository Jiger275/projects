from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from bot.handlers import start, button_callback, handle_message
from bot.scheduler import start_scheduler
from config.config import config
from logger.logger import logger 

def main():
    application = Application.builder().token(config.BOT_TOKEN).build()

    start_scheduler(application)

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Бот запущен и готов к работе")

    application.run_polling()

if __name__ == '__main__':
    main()
