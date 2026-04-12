import telebot
import requests
import time
import os

print("🌟 Vuvu 雲端版啟動中...")

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not BOT_TOKEN or not GEMINI_API_KEY:
    print("❌ 錯誤：找不到 BOT_TOKEN 或 GEMINI_API_KEY")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN)

# 使用你 curl 測試成功的模型
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={GEMINI_API_KEY}"

@bot.message_handler(func=lambda message: True)
def reply_to_message(message):
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        time.sleep(1.2)
        
        payload = {
            "contents": [{"parts": [{"text": message.text}]}],
            "system_instruction": {
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

        response = requests.post(API_URL, json=payload, timeout=15)
        response.raise_for_status()
        result = response.json()
        text = result["candidates"][0]["content"]["parts"][0]["text"]
        
        bot.send_message(message.chat.id, text)   # 改用 send_message 避免 400 錯誤
        
    except Exception as e:
        print(f"❌ Gemini 呼叫失敗: {str(e)}")
        bot.send_message(message.chat.id, "Vuvu 目前有點忙，請稍後再試～")

print("✅ Vuvu 雲端版已成功啟動！正在等待 Telegram 訊息...")
bot.infinity_polling(none_stop=True, interval=0, timeout=30)
