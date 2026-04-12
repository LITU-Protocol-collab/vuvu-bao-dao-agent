import telebot
from google.genai import Client
import time
import os

print("🌟 Vuvu 雲端版啟動中...")

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not BOT_TOKEN or not GEMINI_API_KEY:
    print("❌ 錯誤：找不到 BOT_TOKEN 或 GEMINI_API_KEY")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN)

client = Client(api_key=GEMINI_API_KEY)
model = client.models.get("gemini-2.5-flash")

@bot.message_handler(func=lambda message: True)
def reply_to_message(message):
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        time.sleep(1.2)
        
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
        
    except Exception as e:
        bot.reply_to(message, "Vuvu 目前有點忙，請稍後再試～")

print("✅ Vuvu 雲端版已成功啟動！正在等待 Telegram 訊息...")
bot.infinity_polling(none_stop=True, interval=0, timeout=30)
