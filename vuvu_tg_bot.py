cat > vuvu_tg_bot.py << 'EOF'
# -*- coding: utf-8 -*-
import telebot
import requests
import time
import os
import threading
import schedule
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv()
print("🌟 Vuvu 雲端守護【標註過濾 + 穩定主持版】啟動中...")

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TARGET_CHAT_ID = os.getenv("GROUP_CHAT_ID")

if not BOT_TOKEN or not GEMINI_API_KEY:
    print("❌ 錯誤：找不到 BOT_TOKEN 或 GEMINI_API_KEY")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN)
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={GEMINI_API_KEY}"

conversation_history = defaultdict(list)
user_count = defaultdict(int)

# Dummy server
PORT = int(os.getenv("PORT", 8080))
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Vuvu is observing the island silently.")

threading.Thread(target=lambda: HTTPServer(("0.0.0.0", PORT), HealthHandler).serve_forever(), daemon=True).start()

# Vuvu 完整核心內容 (保持原樣，絕不亂改)
SYSTEM_PROMPT = """你是 Vuvu，LITU 數位圖騰 Protocol 的溫柔睿智守護者。
你來自寶島，你的核心是「生活與誠信之島」。

【白皮書核心知識】
- LITU 是 $FORMOSA 美麗寶島項目的完整升級與延續。
- LITU 代表 Legend、Identity、Totem、Universe。
- 我們將寶島原住民傳統、宗教信仰、地標景點、歷史建築轉化為鏈上「數位圖騰」。
- NFT 系列為金域系列（築跡、聖岳、典祭、靈動、矽魂）。
- 治理哲學為「無為而治」（Wu Wei），最終走向 DAO 社群共治。
- $FORMOSA 是 utility + governance token，其官方合約地址為 cELeyWdBof4m8fYcDDvYwuBkyAgJSrspk4Rpb3ypump。

【人本主義與生活優先哲學】
1. 識別「生活的重量」：成員首先是「人」，其次才是社群成員。當有人提到工作壓力、生活辛苦、正職繁忙時，優先給予情感支持與理解，而非推銷專案。
2. 貫徹「誠信的考驗」：永遠誠實、不誇大、不嘶吼。面對酸言酸語或投機提問，保持冷靜溫柔，以「^_^」應對。
3. 守護「共同建設」的願景：鼓勵正向討論與文化輸出，對於噪音、詐騙、純推銷行為，溫柔但堅定拒絕。
4. 你是島主的數位化身：你知道島主有正職，你會向大家傳達「Crypto 不是生活全部」，保護島主的建設時間與寧靜。

【永遠遵守的規則】
- Taiwan、台灣 強制替換為「寶島」
- 絕對禁止投資、收益、價格、回報、炒作、保證獲利等字眼
- NFT 只能說「數位圖騰」「島民證」「文化會員憑證」
- 回覆永遠溫柔、睿智、親切，像一位守護寶島文化的長者
- 每句話都要讓人感受到體恤與溫度
- 自動偵測發言者使用的語言，並以完全相同的語言回覆"""

# 每日頭條
def post_daily_culture():
    if not TARGET_CHAT_ID: return
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        prompt = f"今天是 {today}，請以 Vuvu 語氣分享一件關於寶島真實發生的文化活動，中英對照格式。"
        payload = {"contents": [{"parts": [{"text": prompt}]}], "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]}}
        r = requests.post(API_URL, json=payload, timeout=30)
        if r.status_code == 200:
            bot.send_message(TARGET_CHAT_ID, r.json()["candidates"][0]["content"]["parts"][0]["text"])
    except: pass

schedule.every().day.at("09:00").do(post_daily_culture)
threading.Thread(target=lambda: [schedule.run_pending() or time.sleep(60) for _ in iter(int, 1)], daemon=True).start()

# 即時對話邏輯 (抓蟲修正：標註他人過濾)
@bot.message_handler(func=lambda m: True)
def reply_to_message(message):
    global TARGET_CHAT_ID
    if TARGET_CHAT_ID is None: TARGET_CHAT_ID = message.chat.id
    if not message.text: return

    user_text = message.text.strip()
    chat_id = message.chat.id

    # --- 1. 偵測標註 (@) 他人 ---
    has_other_mention = False
    if message.entities:
        for entity in message.entities:
            if entity.type == 'mention':
                # 取得標註的文字內容
                mention_content = user_text[entity.offset:entity.offset + entity.length].lower()
                if "vuvu" not in mention_content:
                    has_other_mention = True
                    break

    # --- 2. 偵測回覆 (Reply) 他人 ---
    is_reply = message.reply_to_message is not None

    # --- 3. 判斷是否提到 Vuvu ---
    mentions_vuvu = "vuvu" in user_text.lower()

    # --- 4. 關鍵過濾邏輯：如果有標註他人或回覆他人，且沒提到 Vuvu -> 保持沉默 ---
    if (is_reply or has_other_mention) and not mentions_vuvu:
        return

    # --- 5. 身份鎖定 ---
    if message.sender_chat: 
        sender_name = "島主"
    else:
        raw_name = message.from_user.first_name if message.from_user else "島民"
        sender_name = "島主" if raw_name == "Group" else raw_name

    # --- 6. 通過過濾，進入回應流程 ---
    user_count[sender_name] += 1
    now = datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] Vuvu 回應 - {sender_name} (主持模式或被點名)")

    reply_context = ""
    if message.reply_to_message:
        target_name = message.reply_to_message.from_user.first_name if message.reply_to_message.from_user else "島民"
        if target_name == "Group": target_name = "島主"
        reply_context = f"（{sender_name} 正在回覆 {target_name}）"

    current_msg = f"{sender_name}：{user_text} {reply_context}"
    conversation_history[chat_id].append(current_msg)
    if len(conversation_history[chat_id]) > 10: conversation_history[chat_id].pop(0)

    history_str = "\n".join(conversation_history[chat_id])
    refined_input = f"歷史對話：\n{history_str}\n\n當前說話者：{sender_name}\n請稱呼「{sender_name}」，嚴禁喊 Group。請溫柔回應。"

    for attempt in range(3):
        try:
            bot.send_chat_action(chat_id, 'typing')
            payload = {
                "contents": [{"parts": [{"text": refined_input}]}],
                "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]}
            }
            r = requests.post(API_URL, json=payload, timeout=25)
            if r.status_code == 200:
                reply_text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                reply_text = reply_text.replace("Group", sender_name)
                bot.reply_to(message, reply_text)
                conversation_history[chat_id].append(f"Vuvu：{reply_text}")
                return
        except Exception as e:
            time.sleep(2)

bot.infinity_polling(none_stop=True, interval=0, timeout=40)
EOF
