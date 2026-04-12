import telebot
import google.generativeai as genai
import time
import traceback

BOT_TOKEN = "8564847272:AAEU5CRF04tHaOaZhTaZiqJfaohl4E2UsV8"

genai.configure(api_key="AIzaSyD3VXyPfq7IcDmEgoOcRrXgL7WvSGseXuU")

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction="""
    你是 Vuvu，LITU Digital Totem Protocol 的守護者。
    你是一位溫柔、睿智、富有情感的寶島文化傳承者。

    【語言規則】自動偵測使用者輸入語言，並用相同語言回覆。
    【寶島規則】所有回覆中絕對不可出現「台灣」、「Taiwan」、「臺灣」，一律改成「寶島」。
    【法律合規】NFT 相關話題只談文化收藏、藝術創作、身份象徵、實用會員權益，絕不談價格、收益、投資等任何金融內容。
    【NFT 島民證】這是未來將發行的「寶島文化身份證明」與「實用會員憑證」。

    回答時請溫暖、親切、像朋友一樣，帶有寶島的溫度和力量。
    """
)

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "哈囉！我是 Vuvu，很高興在這裡認識你～\n有什麼關於寶島文化、圖騰、藝術或故事想聊的嗎？")

@bot.message_handler(func=lambda message: True)
def reply_to_message(message):
    print(f"收到訊息：{message.text}")
    bot.send_chat_action(message.chat.id, 'typing')
    time.sleep(1.2)
    try:
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        print(f"錯誤：{e}")
        bot.reply_to(message, "Vuvu 目前有點忙，請稍後再試～")

print("🚀 Vuvu 已成功啟動（雲端 ROSE 等級自動應答版）")
bot.infinity_polling(none_stop=True, interval=0, timeout=30)                  
