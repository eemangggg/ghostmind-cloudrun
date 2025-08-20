import os
from flask import Flask, request
import requests

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

@app.route("/")
def home():
    return "Ghostmind is running on Cloud Run!"

@app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
def webhook():
    if request.method == "POST":
        data = request.get_json()
        if data and "message" in data:
            chat_id = data["message"]["chat"]["id"]
            text = data["message"].get("text", "")
            reply = f"You said: {text}"
            requests.post(f"{BASE_URL}/sendMessage",
                          json={"chat_id": chat_id, "text": reply})
        return {"ok": True}
    return {"ok": False}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
