import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(_name_)

# Конфигурация API ключей
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"

# Настройка Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# Словарь для хранения истории чатов
chat_sessions = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user_id = update.effective_user.id
    chat_sessions[user_id] = model.start_chat(history=[])
    
    await update.message.reply_text(
        "Привет! Я бот с искусственным интеллектом Gemini. "
        "Задавайте мне любые вопросы, и я постараюсь помочь!\n\n"
        "Команды:\n"
        "/start - начать новый диалог\n"
        "/clear - очистить историю чата"
    )

async def clear_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /clear"""
    user_id = update.effective_user.id
    chat_sessions[user_id] = model.start_chat(history=[])
    await update.message.reply_text("История чата очищена. Начинаем новый диалог!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    user_id = update.effective_user.id
    user_message = update.message.text
    
    # Создаем новую сессию чата, если её нет
    if user_id not in chat_sessions:
        chat_sessions[user_id] = model.start_chat(history=[])
    
    # Показываем, что бот печатает
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        # Получаем ответ от Gemini
        chat = chat_sessions[user_id]
        response = chat.send_message(user_message)
        
        # Отправляем ответ пользователю
        await update.message.reply_text(response.text)
        
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {e}")
        await update.message.reply_text(
            "Извините, произошла ошибка при обработке вашего сообщения. "
            "Попробуйте еще раз или используйте /clear для начала нового диалога."
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Update {update} caused error {context.error}")

def main():
    """Основная функция"""
    # Создаем приложение
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("clear", clear_chat))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Добавляем обработчик ошибок
    application.add_error_handler(error_handler)
    
    # Запускаем бота
    logger.info("Бот запущен...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if _name_ == '_main_':
    main()
