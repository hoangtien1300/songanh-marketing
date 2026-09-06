import os, sys, io, json, requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

CONFIG_FILE = r"d:\Song_Anh\marketing_workflow_app\telegram_config.json"

def get_updates(bot_token):
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        if data.get("ok"):
            results = data.get("results", []) or data.get("result", [])
            if results:
                latest = results[-1]
                msg = latest.get("message", {})
                chat = msg.get("chat", {})
                chat_id = chat.get("id")
                from_user = msg.get("from", {})
                username = from_user.get("username") or from_user.get("first_name")
                return chat_id, username
        return None, None
    except Exception as e:
        print(f"Lỗi: {e}")
        return None, None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        token = sys.argv[1].strip()
        cid, user = get_updates(token)
        if cid:
            print(f"✅ Tìm thấy Chat ID của {user}: {cid}")
            cfg = {"bot_token": token, "chat_id": cid, "user": user, "is_active": True}
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(cfg, f, ensure_ascii=False, indent=2)
            print("✅ Đã lưu cấu hình tự động!")
        else:
            print("❌ Chưa thấy tin nhắn /start từ Sếp. Hãy mở Bot trên Telegram và bấm 'Start' (hoặc gửi tin nhắn bất kỳ cho Bot) rồi chạy lại!")
    else:
        print("Vui lòng truyền Bot Token: python get_telegram_chat_id.py <BOT_TOKEN>")
