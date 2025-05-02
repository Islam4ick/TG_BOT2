
import logging
import requests
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Чтение ключа из переменной окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

print("Ключ OpenRouter:", OPENROUTER_API_KEY)
print("Ключ Telegram:", TELEGRAM_TOKEN)

# Загрузка базы знаний
def load_knowledge():
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        knowledge_path = os.path.join(current_dir, "knowledge.txt")
        with open(knowledge_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Нет базы знаний. Пожалуйста, добавьте файл knowledge.txt."

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот поддержки. Задай вопрос по товарам или доставке.")

# Ответ на обычное сообщение
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    knowledge = load_knowledge()

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://yourdomain.com",
            "X-Title": "TelegramBot",
        },
        json={
            "model": "openai/gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        f"Ты — профессиональный и вежливый чат-бот поддержки.\n"
                        f"Вот база знаний:\n{knowledge}\n"
                        "Отвечай кратко и строго по теме. Не выдумывай ответы. "
                        "Если информации нет в базе — скажи об этом честно."
                    )
                },
                {"role": "user", "content": user_input}
            ]
        }
    )

    if response.status_code == 200:
        data = response.json()
        reply = data["choices"][0]["message"]["content"]
    else:
        reply = f"Ошибка: {response.status_code}\n{response.text}"

    await update.message.reply_text(reply)

# Запуск
def main():
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
