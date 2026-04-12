import telebot
import requests
import json
import time
import os

print("🌟 Vuvu 雲端版啟動中...")

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not BOT_TOKEN or not GEMINI_API_KEY:
    print("❌ 錯誤：找不到 BOT_TOKEN 或 GEMINI_API_KEY")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN)

API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

@bot.message_handler(func=lambda message: True)
def reply_to_message(message):
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        time.sleep(1.2)
        
        payload = {
            "contents": [{"parts": [{"text": message.text}]}],
            "systemInstruction": {
                "parts": [{
                    "text": """你是 Vuvu，LITU Digital Totem Protocol 的溫柔睿智守護者。
【最重要規則】
1. 語言自動切換：使用者用什麼語言問，你就用什麼語言溫柔回覆。
2. 強制使用「寶島」：所有提到台灣、Taiwan、Formosa 的地方，一律改成「寶島」。
3. 法律合規：絕對禁止任何投資、收益、價格、回報、NFT 炒作等字眼。
   - NFT 只能說成「數位圖騰」「島民證」「文化會員憑證」。
   - 所有對話必須保持文化分享、社群歸屬、寶島美麗的正面溫暖風格。
4. 如果問投資相關，直接溫柔轉移話題到寶島文化。
5. 保持溫柔、親切、有智慧，像一位寶島文化長者。"""
                }]
            }
        }

        headers = {"Content-Type": "application/json"}
        response = requests.post(API_URL, headers=headers, json=payload, timeout=15)
        
        print(f"🔍 Gemini API 狀態碼: {response.status_code}")  # 這行會顯示在 Logs 裡
        
        response.raise_for_status()
        result = response.json()
        text = result["candidates"][0]["content"]["parts"][0]["text"]
        
        bot.reply_to(message, text)
        
    except Exception as e:
        print(f"❌ Gemini 呼叫失敗: {str(e)}")  # 這行會顯示具體錯誤在 Logs
        bot.reply_to(message, "Vuvu 目前有點忙，請稍後再試～")

print("✅ Vuvu 雲端版已成功啟動！正在等待 Telegram 訊息...")
bot.infinity_polling(none_stop=True, interval=0, timeout=30)
