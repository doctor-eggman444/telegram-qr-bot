 import os
    from flask import Flask, request
    import telebot
    from telebot.types import Update
    from flask import Flask, request
    import html
    import difflib
    import re
    import sqlite3
    import telebot
    from apscheduler.schedulers.background import BackgroundScheduler
    import signal
    import sys
    import uuid
    import time
    from datetime import datetime, timedelta, date
    from flask import Flask
    from telebot import custom_filters
    from threading import Thread
    from types import SimpleNamespace
    import time
    import requests
    from telebot import TeleBot
    from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
    import qrcode
    from types import SimpleNamespace
    import locale
    from io import BytesIO
    import schedule
    import urllib.parse
    from urllib.parse import unquote

    from aiofiles.os import remove

    from geopy.distance import geodesic
    from telebot.apihelper import ApiTelegramException
    from telebot import types
    from geopy.geocoders import Nominatim
    from geopy.exc import GeocoderTimedOut
    import threading
    import calendar
    from telebot.handler_backends import State, StatesGroup
    from telebot.types import ReplyKeyboardMarkup, KeyboardButton
    from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
    from datetime import datetime, timedelta, date
    import threading

    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    if not BOT_TOKEN:
        raise RuntimeError("❌ BOT_TOKEN не задан")

    WEBHOOK_URL = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/{BOT_TOKEN}"

    bot = telebot.TeleBot(BOT_TOKEN)
    app = Flask(__name__)

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        update = telebot.types.Update.de_json(request.get_data().decode("utf-8"))
        bot.process_new_updates([update])
        return '', 200
    return 'Unsupported Media Type', 415

@app.route("/", methods=["GET"])
def index():
    return "Бот работает!", 200

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет")

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    print(f"✅ Вебхук установлен: {WEBHOOK_URL}")
    app.run(host="0.0.0.0", port=10000)
