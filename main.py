import os, json, logging, requests
from flask import Flask, request, abort

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
WEBHOOK_SECRET_TOKEN = os.environ.get("WEBHOOK_SECRET_TOKEN", "")
COMMAND_ONLY = os.environ.get("COMMAND_ONLY", "true").lower() in ("1","true","yes")

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

def tg_send(chat_id, text):
    try:
        requests.post(f"{TELEGRAM_API}/sendMessage", json={"chat_id": chat_id, "text": text})
    except Exception as e:
        app.logger.exception("Failed to send Telegram message: %s", e)

@app.get("/")
def root():
    return "Ghostmind is live", 200

@app.get("/healthz")
def healthz():
    return "ok", 200

@app.post("/webhook")
def webhook():
    if WEBHOOK_SECRET_TOKEN:
        if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != WEBHOOK_SECRET_TOKEN:
            app.logger.warning("Invalid secret token header")
            return abort(401)

    update = request.get_json(silent=True) or {}
    app.logger.info("Update: %s", json.dumps(update))

    message = update.get("message") or update.get("edited_message")
    if not message:
        return ("no message", 200)

    chat_id = message["chat"]["id"]
    text = (message.get("text") or "").strip()

    if text.startswith("/start"):
        tg_send(chat_id, "👋 Ghostmind online. Use /morning, /focus, /evening, /reset.")
    elif text.startswith("/morning"):
        tg_send(chat_id, "🌅 Morning Armor loaded. Log your first move.")
    elif text.startswith("/focus"):
        tg_send(chat_id, "🎯 What’s the one thing you’ll complete today?")
    elif text.startswith("/evening"):
        tg_send(chat_id, "🌙 Evening reset: wins, mood, and one improvement?")
    elif text.startswith("/reset"):
        tg_send(chat_id, "♻️ System reset acknowledged. Fresh start.")
    else:
        if COMMAND_ONLY:
            tg_send(chat_id, "Command-only mode is ON. Try /morning, /focus, /evening, or /reset.")
        else:
            tg_send(chat_id, f"Echo: {text}")

    return ("ok", 200)
