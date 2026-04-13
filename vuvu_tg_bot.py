import telebot
import requests
import time
import os
import threading
import schedule
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime

print("🌟 Vuvu 雲端版啟動中...")

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CHAT_ID = None

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

# Gemini API
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={GEMINI_API_KEY}"

# ====================== 自動發文主持 ======================
def post_daily_culture():
    global CHAT_ID
    if not CHAT_ID:
        print("⚠️ 尚未記錄群組 ID，無法自動發文")
        return
    
    today = datetime.now().strftime("%Y-%m-%d")
    prompt = f"""今天是 {today}，請以 Vuvu 溫柔睿智的守護者語氣，寫一篇簡短溫暖的寶島文化貼文。
主題可以是當下寶島的節慶、傳統活動、文化新聞、地景、小吃、原住民智慧或宗教慶典。
必須：
- 全部使用「寶島」
- 保持正面、溫暖、文化分享風格
- 絕對不要提到投資、收益、價格、回報、NFT炒作
- 結尾邀請大家分享感受或一起守護寶島文化"""

    try:
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "system_instruction": {"parts": [{"text": """你是 Vuvu，LITU Digital Totem Protocol 的溫柔睿智守護者。
1. 語言自動切換
2. 強制使用「寶島」
3. 絕對禁止投資、收益、價格、回報、NFT炒作（NFT 只能說「數位圖騰」「島民證」「文化會員憑證」）
4. 保持溫柔、親切、有智慧，像一位寶島文化長者"""}]}
        }
        response = requests.post(API_URL, json=payload, timeout=15)
        if response.status_code == 200:
            text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            bot.send_message(CHAT_ID, text)
            print(f"✅ 自動發文成功：{today}")
    except Exception as e:
        print(f"❌ 自動發文失敗: {e}")

# 設定每天自動發文時間（可自行調整）
schedule.every().day.at("09:00").do(post_daily_culture)   # 早上 9 點
schedule.every().day.at("20:00").do(post_daily_culture)   # 晚上 8 點

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(60)

threading.Thread(target=run_scheduler, daemon=True).start()

# ====================== 即時回覆 ======================
@bot.message_handler(func=lambda message: True)
def reply_to_message(message):
    global CHAT_ID
    if CHAT_ID is None:
        CHAT_ID = message.chat.id
        print(f"✅ 已記錄群組 ID: {CHAT_ID}")

    for attempt in range(5):
        try:
            bot.send_chat_action(message.chat.id, 'typing')
            time.sleep(1.2)
            
            payload = {
                "contents": [{"parts": [{"text": message.text}]}],
                "system_instruction": {"parts": [{"text": """你是 Vuvu，LITU Digital Totem Protocol 的溫柔睿智守護者。
1. 語言自動切換
2. 強制使用「寶島」
3. 絕對禁止投資、收益、價格、回報、NFT炒作（NFT 只能說「數位圖騰」「島民證」「文化會員憑證」）
4. 保持溫柔、文化分享、正面風格"""}]}
            }

            response = requests.post(API_URL, json=payload, timeout=12)
            if response.status_code == 200:
                text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
                bot.send_message(message.chat.id, text)
                return
        except:
            time.sleep(2 ** attempt)

    bot.send_message(message.chat.id, "Vuvu 目前有點忙，請稍後再試～")

print("✅ Vuvu 已成功啟動！每日自動發文已排程")
bot.infinity_polling(none_stop=True, interval=0, timeout=30)
