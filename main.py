import os
import threading
from flask import Flask
import telebot
from google import genai

# Render सर्वर को हमेशा चालू रखने के लिए Flask सेटअप
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running 24/7!"

# आपके असली टोकन और चाबी यहाँ सेट हैं
TELEGRAM_TOKEN = "8814170626:AAFi5si4lZrlf2MRnL3-kVyiofswZJuFC8Y"
GEMINI_API_KEY = "AIzaSyBqFfHi0dORlQKii-QpYKap0Cn072sIHME"

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
        print(f"Error: {e}")
        bot.reply_to(message, "माफ़ी चाहता हूँ, कुछ तकनीकी खराबी आ गई है।")

def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    # बॉट को बैकग्राउंड में चलाएं
    threading.Thread(target=run_bot, daemon=True).start()
    
    # Render का पोर्ट लेकर सर्वर शुरू करें
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
