from flask import Flask, request
import os, requests

app = Flask(__name__)
TOKEN = os.getenv("BOT_TOKEN")
TG = f"https://api.telegram.org/bot{TOKEN}"

@app.get("/")
def health():
    return "Ghostmind is running on Cloud Run!"

@app.post("/webhook")
def webhook():
    data = request.get_json(silent=True) or {}
    if "message" in data:
        chat = data["message"]["chat"]["id"]
        text = data["message"].get("text","")
        requests.post(f"{TG}/sendMessage", json={"chat_id": chat, "text": f"You said: {text}"})
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
