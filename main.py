import os
import telebot
from flask import Flask, request
import sqlite3
import threading

BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise Exception("BOT_TOKEN не найден в переменных окружения")

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

DB_NAME = 'database.sqlite'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user (
        telegram_id INTEGER PRIMARY KEY,
        name TEXT,
        balance REAL DEFAULT 0.0,
        bonus REAL DEFAULT 0.0
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER,
        station_id TEXT,
        amount REAL,
        bonus_given REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()

init_db()

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user WHERE telegram_id = ?", (chat_id,))
    user = cursor.fetchone()
    if not user:
        cursor.execute("INSERT INTO user (telegram_id, name) VALUES (?, ?)", (chat_id, message.from_user.first_name))
        conn.commit()
    conn.close()
    bot.send_message(chat_id, "Привет! Используй /balance чтобы проверить баланс и /scan для сканирования QR.")

@bot.message_handler(commands=['balance'])
def balance(message):
    chat_id = message.chat.id
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT balance, bonus FROM user WHERE telegram_id = ?", (chat_id,))
    user = cursor.fetchone()
    conn.close()
    if user:
        bot.send_message(chat_id, f"💰 Баланс: {user['balance']:.2f} ₽\n🎁 Бонусы: {user['bonus']:.2f} ₽")
    else:
        bot.send_message(chat_id, "Вы не зарегистрированы, используйте /start.")

@bot.message_handler(commands=['topup'])
def topup(message):
    chat_id = message.chat.id
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE user SET balance = balance + 500 WHERE telegram_id = ?", (chat_id,))
    conn.commit()
    conn.close()
    bot.send_message(chat_id, "Баланс пополнен на 500 ₽")

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

@bot.message_handler(commands=['scan'])
def scan(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📷 Сканировать QR", web_app=WebAppInfo(url="https://doctor-eggman444.github.io/qr-scanner/")))
    bot.send_message(message.chat.id, "Открой камеру и наведи на QR код заправки:", reply_markup=markup)

@bot.message_handler(content_types=['web_app_data'])
def web_app_data(message):
    station_id = message.web_app_data.data
    chat_id = message.chat.id
    amount = 100.0
    bonus = 10.0

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT balance, bonus FROM user WHERE telegram_id = ?", (chat_id,))
    user = cursor.fetchone()

    if not user or user['balance'] < amount:
        bot.send_message(chat_id, "🚫 Недостаточно средств для оплаты.")
        conn.close()
        return

    new_balance = user['balance'] - amount
    new_bonus = user['bonus'] + bonus

    cursor.execute("UPDATE user SET balance = ?, bonus = ? WHERE telegram_id = ?", (new_balance, new_bonus, chat_id))
    cursor.execute("INSERT INTO transactions (telegram_id, station_id, amount, bonus_given) VALUES (?, ?, ?, ?)", (chat_id, station_id, amount, bonus))
    conn.commit()
    conn.close()

    bot.send_message(chat_id, f"✅ Оплата {amount}₽ на станции {station_id} успешно проведена.\n🎁 Бонусы начислены: {bonus}₽")

@app.route('/' + BOT_TOKEN, methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return '', 200

def run_bot():
    bot.remove_webhook()
    bot.set_webhook(url=f"https://your-render-url.onrender.com/{BOT_TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))

if __name__ == '__main__':
    threading.Thread(target=run_bot).start()