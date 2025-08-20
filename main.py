
from flask import Flask, request
import requests
import os

app = Flask(__name__)

TOKEN = os.getenv("TOKEN")  # make sure TOKEN is set in your environment
URL = f"https://api.telegram.org/bot{TOKEN}"

# Health check route
@app.route('/', methods=['GET'])
def index():
    return "Ghostmind is running on Cloud Run!"

# Webhook route
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    print("Incoming update:", data)  # log update to Cloud Run logs

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        reply = f"You said: {text}"
        requests.post(f"{URL}/sendMessage", json={"chat_id": chat_id, "text": reply})

    return "ok", 200


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
