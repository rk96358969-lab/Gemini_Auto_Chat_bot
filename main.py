import os
import threading
from flask import Flask
import telebot
from google import genai

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running 24/7!"

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = genai.Client(api_key=GEMINI_API_KEY)

@bot.message_handler(func=lambda message: True)
def reply_to_user(message):
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=message.text,
        )
        bot.reply_to(message, response.text)
    except Exception as e:
        # अगर कोई एरर आएगा, तो बॉट सीधे आपको टेलीग्राम चैट पर ही बता देगा!
        print(f"Error: {e}")
        bot.reply_to(message, f"माफ़ी चाहता हूँ, जेमिनी से यह एरर आया है:\n\n`{e}`")

def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

    
