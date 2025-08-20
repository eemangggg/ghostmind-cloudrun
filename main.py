import os
import requests
from flask import Flask, request, jsonify

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing. Set it in Cloud Run → Environment variables.")

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

app = Flask(__name__)

def send_message(chat_id: int, text: str):
    try:
        requests.post(
            f"{TELEGRAM_API}/sendMessage",
            json={"chat_id": chat_id, "text": text},
            timeout=10
        )
    except Exception as e:
        print("send_message error:", e, flush=True)

@app.get("/")
def root():
    return "Ghostmind webhook is running.", 200

@app.get("/healthz")
def healthz():
    return jsonify(ok=True), 200

@app.post("/webhook")
def webhook():
    try:
        update = request.get_json(silent=True) or {}
        msg = update.get("message") or update.get("edited_message") or {}
        chat = msg.get("chat", {})
        chat_id = chat.get("id")
        text = (msg.get("text") or "").strip()

        if not chat_id:
            # nothing to do (callback_query, etc.)
            return jsonify(ok=True), 200

        t = text.lower()
        if t.startswith("/start"):
            send_message(chat_id,
                "👋 Ghostmind is live.\n\n"
                "Commands:\n"
                "/ping – check bot\n"
                "/morning – mini morning protocol\n"
                "/evening – mini evening protocol\n"
                "(Say anything and I’ll echo it for now.)"
            )
        elif t.startswith("/ping"):
            send_message(chat_id, "pong ✅")
        elif t.startswith("/morning"):
            send_message(chat_id,
                "🌅 Morning (lite):\n"
                "1) Water + face wash\n"
                "2) 1-min breath reset\n"
                "3) 5-min move (pushups/squats)\n"
                "4) One win for today → name it"
            )
        elif t.startswith("/evening"):
            send_message(chat_id,
                "🌙 Evening (lite):\n"
                "1) Quick win review\n"
                "2) One improvement for tomorrow\n"
                "3) Brain dump → sleep"
            )
        else:
            send_message(chat_id, f"Echo: {text}" if text else "Got it.")

        return jsonify(ok=True), 200
    except Exception as e:
        print("webhook error:", e, flush=True)
        # Always 200 so Telegram keeps delivering
        return jsonify(ok=True), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
