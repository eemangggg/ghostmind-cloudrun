import os
import sqlite3
from flask import Flask, request
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

DB_FILE = "ghostmind.db"

# ------------------ DB INIT ------------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS streaks (
                    chat_id INTEGER PRIMARY KEY,
                    streak_count INTEGER,
                    last_morning TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS moods (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER,
                    mood TEXT,
                    timestamp TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER,
                    entry TEXT,
                    timestamp TEXT
                )''')
    conn.commit()
    conn.close()

init_db()

# ------------------ HELPERS ------------------
def send_message(chat_id, text):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

def update_streak(chat_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT streak_count, last_morning FROM streaks WHERE chat_id=?", (chat_id,))
    row = c.fetchone()

    today = datetime.utcnow().date()
    if row:
        streak_count, last_morning = row
        last_morning_date = datetime.strptime(last_morning, "%Y-%m-%d").date()
        if last_morning_date == today:
            msg = f"⚡ Already logged morning today. Streak: {streak_count} days."
        elif last_morning_date == today - timedelta(days=1):
            streak_count += 1
            c.execute("UPDATE streaks SET streak_count=?, last_morning=? WHERE chat_id=?",
                      (streak_count, str(today), chat_id))
            msg = f"🔥 Morning logged. Current streak: {streak_count} days."
        else:
            streak_count = 1
            c.execute("UPDATE streaks SET streak_count=?, last_morning=? WHERE chat_id=?",
                      (streak_count, str(today), chat_id))
            msg = "🌅 New streak started: 1 day."
    else:
        streak_count = 1
        c.execute("INSERT INTO streaks (chat_id, streak_count, last_morning) VALUES (?, ?, ?)",
                  (chat_id, streak_count, str(today)))
        msg = "🌅 First morning logged. Streak: 1 day."

    conn.commit()
    conn.close()
    return msg

def log_mood(chat_id, mood):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO moods (chat_id, mood, timestamp) VALUES (?, ?, ?)",
              (chat_id, mood, str(datetime.utcnow())))
    conn.commit()
    conn.close()
    return f"🧠 Mood logged: {mood}"

def log_entry(chat_id, entry):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO logs (chat_id, entry, timestamp) VALUES (?, ?, ?)",
              (chat_id, entry, str(datetime.utcnow())))
    conn.commit()
    conn.close()
    return "📖 Journal entry saved."

def weekly_summary(chat_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    week_ago = datetime.utcnow() - timedelta(days=7)

    c.execute("SELECT mood, timestamp FROM moods WHERE chat_id=? AND timestamp>=?",
              (chat_id, str(week_ago)))
    moods = c.fetchall()

    c.execute("SELECT entry, timestamp FROM logs WHERE chat_id=? AND timestamp>=?",
              (chat_id, str(week_ago)))
    logs = c.fetchall()
    conn.close()

    summary = "📊 Weekly Summary\n\n"
    summary += "🧠 Moods:\n"
    if moods:
        for m, t in moods:
            summary += f"- {m} ({t})\n"
    else:
        summary += "No moods logged.\n"

    summary += "\n📖 Logs:\n"
    if logs:
        for e, t in logs:
            summary += f"- {e} ({t})\n"
    else:
        summary += "No journal entries.\n"

    return summary

# ------------------ ROUTES ------------------
@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text.startswith("/morning"):
            send_message(chat_id, update_streak(chat_id))
        elif text.startswith("/mood"):
            mood = text.replace("/mood", "").strip()
            send_message(chat_id, log_mood(chat_id, mood if mood else "unspecified"))
        elif text.startswith("/log"):
            entry = text.replace("/log", "").strip()
            send_message(chat_id, log_entry(chat_id, entry if entry else "empty"))
        elif text.startswith("/weekly"):
            send_message(chat_id, weekly_summary(chat_id))
        elif text.startswith("/reset"):
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("DELETE FROM streaks WHERE chat_id=?", (chat_id,))
            conn.commit()
            conn.close()
            send_message(chat_id, "🔄 Streak reset.")
        else:
            send_message(chat_id, f"Echo: {text}")

    return {"ok": True}

@app.route("/", methods=["GET"])
def home():
    return "Ghostmind v1.6 running with SQLite."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
