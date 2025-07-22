import os
from flask import Flask, request
import telebot
import signal

# --- Инициализация ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("❌ BOT_TOKEN не задан в переменных окружения")

WEBHOOK_URL = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/{BOT_TOKEN}"
bot = telebot.TeleBot(BOT_TOKEN)

app = Flask(__name__)

# --- Эндпоинт вебхука ---
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    if request.headers.get("content-type") == "application/json":
        json_string = request.get_data().decode("utf-8")
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "", 200
    return "Unsupported Media Type", 415

# --- Проверка работоспособности ---
@app.route("/", methods=["GET"])
def index():
    return "Бот работает!", 200

# --- Обработчики команд ---
@bot.message_handler(commands=["start"])
def cmd_start(message):
    bot.reply_to(message, "Привет! Я QR‑бот, работаю через вебхук 🚀")

# Можно добавить другие хендлеры ниже

# --- Остановка по сигналу ---
def shutdown_scheduler(signum, frame):
    print("⛔ Остановка приложения...")
    exit(0)

signal.signal(signal.SIGINT, shutdown_scheduler)
signal.signal(signal.SIGTERM, shutdown_scheduler)

# --- Точка входа ---
if __name__ == "__main__":
    # Сбрасываем вебхук и устанавливаем снова
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    print("✅ Вебхук установлен:", WEBHOOK_URL)

    # Запуск Flask — через Gunicorn в production
    app.run(host="0.0.0.0", port=10000)
