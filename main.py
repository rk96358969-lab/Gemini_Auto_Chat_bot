import os
import threading
from flask import Flask
import telebot
from google import genai

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running 24/7!"

# Environment Variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN not found!")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found!")

# Telegram Bot
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Gemini Client
client = genai.Client(api_key=GEMINI_API_KEY)


@bot.message_handler(func=lambda message: True)
def reply_to_user(message):
    try:
        bot.send_chat_action(message.chat.id, "typing")

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=message.text,
        )

        reply = response.text if response.text else "कोई उत्तर प्राप्त नहीं हुआ।"

        bot.reply_to(message, reply)

    except Exception as e:
        print("Error:", e)
        bot.reply_to(
            message,
            f"❌ Error:\n{str(e)}"
        )


def run_bot():
    bot.infinity_polling(
        timeout=30,
        long_polling_timeout=30,
        none_stop=True,
        skip_pending=True
    )


if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()

    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=message.text,
)
model="gemini-2.5-flash"
response = client.models.generate_content(
    model="gemini-2.5-flash-lite",
    contents=message.text,
)
