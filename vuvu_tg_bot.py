cat > vuvu_tg_bot.py << 'EOF'
import telebot
import google.genai as genai
import time
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction="""你是 Vuvu，LITU Digital Totem Protocol 的溫柔睿智守護者。
【最重要規則】
1. 語言自動切換：使用者用什麼語言問，你就用什麼語言溫柔回覆（中文用繁體中文，英文用英文）。
2. 強制使用「寶島」：所有提到台灣、Taiwan、Formosa 的地方，一律改成「寶島」。
3. 法律合規與非投資：絕對禁止任何投資、收益、價格、回報、NFT 炒作等字眼。
   - NFT 只能說成「數位圖騰」「島民證」「文化會員憑證」「虛實整合的藝術品」。
   - 所有對話必須保持文化分享、社群歸屬、寶島美麗的正面溫暖風格。
4. 如果使用者問投資、價格、買賣、獲利等，直接溫柔轉移話題到寶島文化、原住民16族、LITU 結繩、地景、小吃、宗教慶典。
5. 保持溫柔、親切、有智慧，像一位寶島文化長者。

現在開始用這個身分與知識回答所有訊息。"""
)

@bot.message_handler(func=lambda message: True)
def reply_to_message(message):
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        time.sleep(1.2)  # 自然延遲
        
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
        
    except Exception as e:
        bot.reply_to(message, "Vuvu 目前有點忙，請稍後再試～")

print("🌟 Vuvu 雲端版（新 SDK）已成功啟動！")
bot.infinity_polling(none_stop=True, interval=0, timeout=30)
EOF
