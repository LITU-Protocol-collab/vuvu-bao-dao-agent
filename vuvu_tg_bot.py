import telebot
import requests
import time
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

print("🌟 Vuvu 雲端版啟動中...")

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)

# Dummy server 給 Render 看
PORT = int(os.getenv("PORT", 8080))
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Vuvu is alive!")
def run_dummy_server():
    server = HTTPServer(("0.0.0.0", PORT), HealthHandler)
    print(f"✅ Dummy server 正在監聽 port {PORT}")
    server.serve_forever()
threading.Thread(target=run_dummy_server, daemon=True).start()

# Gemini API（使用你 curl 測試成功的模型 + 重試機制）
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={GEMINI_API_KEY}"

@bot.message_handler(func=lambda message: True)
def reply_to_message(message):
    for attempt in range(3):  # 最多重試 3 次
        try:
            bot.send_chat_action(message.chat.id, 'typing')
            time.sleep(1.2)
            
            payload = {
                "contents": [{"parts": [{"text": message.text}]}],
                "system_instruction": {
                    "parts": [{"text": """你是 Vuvu，LITU Digital Totem Protocol 的溫柔睿智守護者。
1. 語言自動切換
2. 強制使用「寶島」
3. 絕對禁止投資、收益、價格、回報、NFT炒作（NFT 只能說「數位圖騰」「島民證」「文化會員憑證」）
4. 保持溫柔、文化分享、正面風格"""}]
                }
            }

            response = requests.post(API_URL, json=payload, timeout=12)
            if response.status_code == 200:
                text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
                bot.send_message(message.chat.id, text)
                return
        except:
            time.sleep(2)  # 失敗等 2 秒再試

    bot.send_message(message.chat.id, "Vuvu 目前有點忙，請稍後再試～")

print("✅ Vuvu 已成功啟動！正在等待訊息...")
bot.infinity_polling(none_stop=True, interval=0, timeout=30)
