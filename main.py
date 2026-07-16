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
            model='gemini-flash-latest',
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
import os
import threading
import base64
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

# हर chat_id की बातचीत यहाँ याद रखी जाएगी
chat_histories = {}

# कितने पुराने messages याद रखने हैं (ज़्यादा रखने से API कॉल महंगी/धीमी हो सकती है)
MAX_HISTORY = 20


@bot.message_handler(commands=['reset'])
def reset_history(message):
    chat_histories.pop(message.chat.id, None)
    bot.reply_to(message, "ठीक है, मैंने पुरानी बातचीत भुला दी है। नई शुरुआत करते हैं!")


@bot.message_handler(content_types=['photo'])
def reply_to_image(message):
    chat_id = message.chat.id
    try:
        bot.send_chat_action(chat_id, 'typing')

        # Telegram पर सबसे बड़े साइज़ वाली फ़ोटो लो (सबसे अच्छी quality)
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # अगर फ़ोटो के साथ कोई caption/सवाल लिखा है तो वो इस्तेमाल करो, वरना डिफ़ॉल्ट सवाल
        user_text = message.caption if message.caption else "इस तस्वीर में क्या है? हिंदी में बताओ।"

        history = chat_histories.get(chat_id, [])
        history.append({
            "role": "user",
            "parts": [
                {"text": user_text},
                {
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": base64.b64encode(downloaded_file).decode("utf-8"),
                    }
                },
            ],
        })

        response = client.models.generate_content(
            model='gemini-flash-latest',
            contents=history,
        )

        history.append({"role": "model", "parts": [{"text": response.text}]})

        if len(history) > MAX_HISTORY:
            history = history[-MAX_HISTORY:]

        chat_histories[chat_id] = history

        bot.reply_to(message, response.text)
    except Exception as e:
        print(f"Error: {e}")
        bot.reply_to(message, f"माफ़ी चाहता हूँ, तस्वीर समझने में यह एरर आया है:\n\n`{e}`")


@bot.message_handler(func=lambda message: True)
def reply_to_user(message):
    chat_id = message.chat.id
    try:
        bot.send_chat_action(chat_id, 'typing')

        # इस user की history निकालो (अगर नहीं है तो नई बनाओ)
        history = chat_histories.get(chat_id, [])

        # user का नया message history में जोड़ो
        history.append({"role": "user", "parts": [{"text": message.text}]})

        response = client.models.generate_content(
            model='gemini-flash-latest',
            contents=history,
        )

        # bot का जवाब भी history में जोड़ो ताकि अगली बार याद रहे
        history.append({"role": "model", "parts": [{"text": response.text}]})

        # history को ज़्यादा बड़ी होने से रोको (सिर्फ़ आखिरी MAX_HISTORY messages रखो)
        if len(history) > MAX_HISTORY:
            history = history[-MAX_HISTORY:]

        chat_histories[chat_id] = history

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
