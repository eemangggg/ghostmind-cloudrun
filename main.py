# main.py
import os, json, logging, requests
from flask import Flask, request, abort

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
WEBHOOK_SECRET_TOKEN = os.environ.get("WEBHOOK_SECRET_TOKEN", "")  # optional
COMMAND_ONLY = os.environ.get("COMMAND_ONLY", "true").lower() in ("1","true","yes")

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

def tg_send(chat_id, text):
    try:
        requests.post(f"{TELEGRAM_API}/sendMessage", json={"chat_id": chat_id, "text": text})
    except Exception as e:
        app.logger.exception("Failed to send Telegram message: %s", e)

@app.get("/")
def root():  # Cloud Run health/root
    return "Ghostmind is live", 200

@app.get("/healthz")
def healthz():
    return "ok", 200

@app.post("/webhook")
def webhook():
    # Optional header check to ensure the request is from Telegram (if you set secret_token)
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

    # Handle commands
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
            # (Optional) Free-text handling; you can integrate OpenAI here later.
            tg_send(chat_id, f"Echo: {text}")

    return ("ok", 200)

@app.post("/set-webhook")
def set_webhook():
    """Optional helper endpoint to set Telegram webhook after deploy.
       Provide ?url=https://YOUR_SERVICE_URL/webhook when calling this endpoint.
    """
    if not TELEGRAM_TOKEN:
        return ("Missing TELEGRAM_TOKEN", 400)
    url = request.args.get("url")
    if not url:
        return ("Missing url param", 400)
    payload = {"url": url}
    if WEBHOOK_SECRET_TOKEN:
        payload["secret_token"] = WEBHOOK_SECRET_TOKEN
    r = requests.post(f"{TELEGRAM_API}/setWebhook", json=payload)
    return (r.text, r.status_code)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    # Use Flask dev server only for local testing. Cloud Run uses gunicorn (see Dockerfile).
    app.run(host="0.0.0.0", port=port)
