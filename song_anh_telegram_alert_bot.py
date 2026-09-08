import os, sys, io, json, datetime, requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "")
if not NOTION_TOKEN and os.path.exists(os.path.join(os.path.dirname(__file__), "telegram_config.json")):
    try:
        with open(os.path.join(os.path.dirname(__file__), "telegram_config.json"), "r", encoding="utf-8") as f:
            cfg = json.load(f)
            NOTION_TOKEN = cfg.get("notion_token", "")
    except Exception:
        pass
NOTION_VERSION = "2022-06-28"

TASKS_DB_ID = "19a4b5e73d9080f4a51ef769967547a5"
CONTENT_DB_ID = "33d4b5e73d90809faebfd11a9a8b0c0e"
GROUPS_HISTORY_DB_ID = "3c24b5e73d9081dfaa41d2f5c355f32f"

CONFIG_FILE = r"d:\Song_Anh\marketing_workflow_app\telegram_config.json"

def load_telegram_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            pass
    return {
        "bot_token": "",
        "chat_id": "",
        "bot_name": "Song Anh Alert Bot",
        "is_active": False,
        "alert_times": ["08:30", "14:00", "20:00"]
    }

def save_telegram_config(cfg):
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

def send_telegram_message(bot_token, chat_id, text, parse_mode="HTML", reply_markup=None):
    if not bot_token or not chat_id:
        return {"ok": False, "error": "Chưa cấu hình bot_token hoặc chat_id"}
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": False
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        res = requests.post(url, json=payload, timeout=10)
        return res.json()
    except Exception as e:
        return {"ok": False, "error": str(e)}

def get_today_notion_alerts():
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json"
    }
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    alerts = []
    
    # 1. Query Active Tasks from Notion Tasks DB
    try:
        body = {
            "filter": {
                "property": "Trạng thái",
                "select": {
                    "equals": "Đang thực hiện"
                }
            }
        }
        res = requests.post(f"https://api.notion.com/v1/databases/{TASKS_DB_ID}/query", headers=headers, json=body, timeout=10)
        if res.status_code == 200:
            tasks = res.json().get("results", [])
            for t in tasks:
                t_title = t.get("properties", {}).get("Tên công việc", {}).get("title", [])
                name = t_title[0]["plain_text"] if t_title else "Công việc"
                kpi = t.get("properties", {}).get("KPI Tuần", {}).get("number") or 0
                done = t.get("properties", {}).get("Đã thực hiện", {}).get("number") or 0
                alerts.append({
                    "type": "task",
                    "title": name,
                    "kpi": f"{done}/{kpi}",
                    "url": t.get("url")
                })
    except Exception as e:
        print(f"Lỗi query Tasks DB: {e}")

    # 2. Query Group Re-comment schedules
    try:
        res_grp = requests.post(f"https://api.notion.com/v1/databases/{GROUPS_HISTORY_DB_ID}/query", headers=headers, json={"page_size": 5}, timeout=10)
        if res_grp.status_code == 200:
            grps = res_grp.json().get("results", [])
            for g in grps:
                g_title = g.get("properties", {}).get("Tên Bài Đăng", {}).get("title", [])
                g_name = g_title[0]["plain_text"] if g_title else "Bài Group"
                g_link = g.get("properties", {}).get("Link Bài Đăng Thực Tế", {}).get("url")
                g_next = g.get("properties", {}).get("Ngày Re-Comment Tiếp Theo", {}).get("formula", {}).get("date", {}).get("start")
                alerts.append({
                    "type": "recomment_group",
                    "title": g_name,
                    "link": g_link,
                    "next_date": g_next
                })
    except Exception as e:
        print(f"Lỗi query Groups DB: {e}")
        
    return alerts

def format_daily_briefing_message(alerts):
    now = datetime.datetime.now().strftime("%H:%M - %d/%m/%Y")
    msg = f"🏛️ <b>BÁO CÁO NHẮC HẸN & NHIỆM VỤ SONG ANH</b> 🔔\n"
    msg += f"⏰ <i>Thời gian: {now}</i>\n"
    msg += f"──────────────────────\n\n"
    
    msg += f"📋 <b>CÁC ĐẦU VIỆC QUAN TRỌNG ĐANG CHẠY:</b>\n"
    for idx, a in enumerate(alerts[:5], 1):
        if a.get("type") == "task":
            msg += f" {idx}. 🔹 <b>{a['title']}</b> (Tiến độ: {a['kpi']})\n"
        elif a.get("type") == "recomment_group":
            msg += f" {idx}. 💬 <b>Re-cmt Group:</b> {a['title'][:35]}...\n"
            
    msg += f"\n💡 <i>Mẹo: Nhấp các nút bên dưới để xem chi tiết hoặc mở nhanh Dashboard!</i>\n"
    return msg


def format_hr_morning_report():
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    today_str = today.strftime("%d/%m/%Y")
    yesterday_str = yesterday.strftime("%d/%m/%Y")
    
    msg = f"🏢 <b>BÁO CÁO NHANH NHÂN SỰ SÁNG {today_str}</b>\n"
    msg += f"🏢 <i>Đơn vị: Mô Hình Kiến Trúc Song Anh</i>\n"
    msg += f"👤 <i>Trợ lý: Vy - Nhân Sự</i>\n"
    msg += f"──────────────────────\n\n"
    
    msg += f"👥 <b>TỔNG QUÂN SỐ CÔNG TY: 19 Nhân sự</b>\n"
    msg += f"• Khối Văn phòng: 05 | Nhóm Thế Anh: 05\n"
    msg += f"• Nhóm Huynh: 04 | Nhóm Hiển: 05\n"
    msg += f"<i>(Hành chính: 06 | Cơ bản + Khoán: 10 | CTV: 02 | Thử việc: 01)</i>\n\n"
    
    msg += f"⏪ <b>DIỄN BIẾN HÔM QUA ({yesterday_str}):</b>\n"
    msg += f"• Ghi nhận thưởng nóng 1 triệu cho 3 nhân sự: Sơn (Nippon), Hiển (Trách nhiệm), Quỳnh (Nỗ lực).\n"
    msg += f"• Tiếp nhận 02 hồ sơ ứng viên: Nguyen Dat (In 3D) &amp; Trần Quốc Huy (Sale B2B) từ vieclam24h.\n"
    msg += f"• Đã số hóa và cập nhật dữ liệu 2 ứng viên vào Notion DB Thành viên.\n\n"
    
    msg += f"⏩ <b>VIỆC CẦN LÀM HÔM NAY ({today_str}):</b>\n"
    msg += f"1. Theo dõi phản hồi Zalo/mail của 02 ứng viên Đạt &amp; Huy để xếp lịch trao đổi/phỏng vấn.\n"
    msg += f"2. Họp giao ban đánh giá kết thúc 02 tuần thử việc của Phạm Vũ Luân (Nhóm Hiển).\n"
    msg += f"3. Kiểm soát quân số xưởng ca sáng và chuyên cần các nhóm thi công.\n\n"
    
    msg += f"🔗 <a href='https://songanh-marketing.phamhoangtien1300.workers.dev/#nhan-su'>Mở WebApp Nhân Sự</a> | <a href='https://songanh-marketing.phamhoangtien1300.workers.dev/ho_so_nhan_vien.html'>Xem Biểu Mẫu Hồ Sơ</a>\n"
    return msg

def send_daily_hr_morning_alert():
    cfg = load_telegram_config()
    bot_token = cfg.get("bot_token")
    chat_id = cfg.get("chat_id")
    if not bot_token or not chat_id:
        print("Lỗi: Chưa cấu hình bot_token hoặc chat_id trong telegram_config.json")
        return {"ok": False, "error": "Chưa cấu hình bot_token hoặc chat_id"}
    msg = format_hr_morning_report()
    res = send_telegram_message(bot_token, chat_id, msg, parse_mode="HTML")
    print("Kết quả gửi thông báo Nhân Sự qua Telegram:", res)
    return res


if __name__ == "__main__":
    cfg = load_telegram_config()
    print("=== TELEGRAM ALERT BOT ENGINE SẴN SÀNG ===")
    print(f"Config hiện tại: Bot Token = {'ĐÃ CÓ' if cfg.get('bot_token') else 'CHƯA CÓ'} | Chat ID = {cfg.get('chat_id') or 'CHƯA CÓ'}")
    alerts = get_today_notion_alerts()
    print(f"Tìm thấy {len(alerts)} alerts từ Notion.")
    sample_msg = format_daily_briefing_message(alerts)
    print("\n--- MẪU TIN NHẮN BOT SẼ GỬI QUA TELEGRAM ---\n")
    print(sample_msg)
