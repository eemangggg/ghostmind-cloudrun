import os
import sqlite3
from flask import Flask, request
import requests

app = Flask(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# SQLite setup
DB_FILE = "ghostmind.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            command TEXT,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

def save_log(user_id, command, message):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("INSERT INTO logs (user_id, command, message) VALUES (?, ?, ?)",
                (user_id, command, message))
    conn.commit()
    conn.close()

def send_message(chat_id, text):
    url = f"{BASE_URL}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_id = str(data["message"]["from"]["id"])
        text = data["message"].get("text", "")

        if text.startswith("/start"):
            send_message(chat_id, "👋 Welcome to Ghostmind v1.6 with SQLite tracking!")
            save_log(user_id, "start", text)

        elif text.startswith("/morning"):
            send_message(chat_id, "🌅 Morning protocol activated.")
            save_log(user_id, "morning", text)

        elif text.startswith("/log"):
            msg = text.replace("/log", "").strip()
            if msg:
                save_log(user_id, "log", msg)
                send_message(chat_id, f"📝 Logged: {msg}")
            else:
                send_message(chat_id, "Usage: /log your note here")

        else:
            send_message(chat_id, "⚡ Command not recognized. Try /start /morning /log")
    return {"ok": True}
