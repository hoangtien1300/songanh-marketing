# -*- coding: utf-8 -*-
"""
Hệ thống Thông Báo Nhắc Việc Tuyển Dụng & Sắp Lịch Phỏng Vấn (08:00 Mỗi Sáng)
Chạy tự động mỗi sáng từ 29/09/2026 đến hết hạn tin đăng (26/10/2026).
Tương thích 100% trên cả Windows Task Scheduler & GitHub Actions Cloud (chạy độc lập khi tắt máy).
Gửi thông báo trực tiếp qua Telegram cá nhân Sếp Phạm Hoàng Tiến (chat_id: 1730306144)
"""
import os
import sys
import io
import json
import datetime
import requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "telegram_config.json")
POOL_FILE = os.path.join(BASE_DIR, "candidates_pool.json")
CV_DIR = os.path.join(BASE_DIR, "..", "outputs", "reports", "ho_so_ung_vien")
END_DATE_STR = "2026-10-26"
LIVE_POST_URL = "https://vieclam24h.vn/xay-dung/nhan-vien-thi-cong-mo-hinh-sa-ban-luong-15-20-trieu-khong-yeu-cau-kinh-nghiem-c31p122id200948511.html"

DEFAULT_BOT_TOKEN = "8852452435:AAE9UYCPdCECPDfiV8M3cq2oycFqXV_wMpg"
DEFAULT_CHAT_ID = 1730306144

def load_telegram_credentials():
    # 1. Ưu tiên biến môi trường (GitHub Actions Secrets hoặc System Env)
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    
    # 2. Đọc file config local nếu có
    if not token or not chat_id:
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    token = token or cfg.get("bot_token", "")
                    chat_id = chat_id or cfg.get("chat_id", "")
            except Exception as e:
                print("Lỗi đọc telegram_config.json:", e)
                
    # 3. Fallback mặc định
    token = token or DEFAULT_BOT_TOKEN
    chat_id = chat_id or DEFAULT_CHAT_ID
    return str(token), str(chat_id)

def get_vietnam_time():
    # Chuẩn hóa múi giờ Việt Nam UTC+7
    tz_vn = datetime.timezone(datetime.timedelta(hours=7))
    return datetime.datetime.now(tz_vn)

def get_day_name_vn(date_obj):
    days = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ Nhật"]
    return days[date_obj.weekday()]

def get_candidate_items():
    items = []
    # 1. Đọc từ candidates_pool.json (dùng được trên cả GitHub Actions và local)
    if os.path.exists(POOL_FILE):
        try:
            with open(POOL_FILE, "r", encoding="utf-8") as f:
                cands = json.load(f)
                for c in cands:
                    name = c.get("name", "")
                    year = c.get("year", "")
                    skills = c.get("skills", "")
                    note = c.get("note", "")
                    items.append(f"• <b>{name} ({year}):</b> {skills} <i>[{note}]</i>")
                if items:
                    return items
        except Exception as e:
            print("Lỗi đọc candidates_pool.json:", e)

    # 2. Fallback đọc thư mục CV nếu candidates_pool.json chưa có
    if os.path.exists(CV_DIR):
        cv_files = [f for f in os.listdir(CV_DIR) if f.lower().endswith(".pdf")]
        for f in sorted(cv_files):
            f_lower = f.lower()
            if "tran quoc huy" in f_lower or "nguyen dat.pdf" in f_lower or "huynh anh thu" in f_lower:
                continue
            elif "nguyen minh dat" in f_lower:
                items.append("• <b>Nguyễn Minh Đạt (2002):</b> Đồ họa 3D, Cắt gọt kim loại, In 3D FDM <i>[Ưu tiên số 1 - Hẹn phỏng vấn]</i>")
            elif "vo ngoc tan" in f_lower:
                items.append("• <b>Võ Ngọc Tân (2002):</b> Gần xưởng (Lê Văn Việt), Vận hành mô hình VinWonders <i>[Thợ học việc - Hẹn phỏng vấn]</i>")
            elif "thach tuyet nhi" in f_lower:
                items.append("• <b>Thạch Tuyết Nhi (2004):</b> Cử nhân Đồ họa, Sketchup, Khéo tay làm đồ thủ công <i>[Hỏi xe & Hẹn test]</i>")
    return items

def format_recruitment_alert_message():
    vn_now = get_vietnam_time()
    today = vn_now.date()
    today_str = today.strftime("%d/%m/%Y")
    today_day_name = get_day_name_vn(today)
    
    end_date = datetime.datetime.strptime(END_DATE_STR, "%Y-%m-%d").date()
    days_left = (end_date - today).days
    
    # Kiểm tra xem đã hết hạn chiến dịch chưa
    if days_left < 0:
        return (
            f"🛑 <b>THÔNG BÁO KẾT THÚC ĐỢT 1 TIN TUYỂN DỤNG ({today_str})</b>\n"
            f"🏢 <i>Đơn vị: Mô Hình Kiến Trúc Song Anh</i>\n"
            f"👤 <i>Phụ trách: Vy - Nhân Sự &amp; Kiến - Lập Trình</i>\n"
            f"──────────────────────\n\n"
            f"Tin tuyển dụng trên Việc Làm 24h đã hết hạn 4 tuần vào ngày 26/10/2026.\n"
            f"👉 <i>Đề xuất Sếp kiểm tra kích hoạt gói quà tặng 4 tuần tương đương để mở đợt tuyển bổ sung nếu cần!</i>"
        )
    
    cand_list = get_candidate_items()
    
    msg = f"👥 <b>NHẮC VIỆC TUYỂN DỤNG &amp; SẮP LỊCH PHỎNG VẤN (08:00)</b>\n"
    msg += f"🏢 <i>Đơn vị: Mô Hình Kiến Trúc Song Anh</i>\n"
    msg += f"👤 <i>Phụ trách: Vy - Nhân Sự &amp; Kiến - Lập Trình</i>\n"
    msg += f"──────────────────────\n\n"
    
    msg += f"🎯 <b>Chiến dịch:</b> Tuyển 04 Thợ Thi Công Mô Hình - Sa Bàn\n"
    msg += f"⏳ <b>Thời hạn tin:</b> 29/09 - 26/10/2026 (Hôm nay: {today_day_name} {today_str} - Còn <b>{days_left} ngày</b>)\n"
    msg += f"🌐 <b>Kênh:</b> Việc Làm 24h (Ưu tiên Tuyển Gấp Trang Chủ &amp; Auto làm mới 15 lần/ngày)\n\n"
    
    msg += f"📋 <b>CÁC ĐẦU VIỆC SÁNG 08:00 CẦN XỬ LÝ:</b>\n"
    msg += f"1. 📬 <b>Kiểm tra hồ sơ mới:</b> Đăng nhập tài khoản Việc Làm 24h kiểm tra có CV ứng tuyển mới nộp qua đêm.\n"
    msg += f"2. 📞 <b>Liên hệ &amp; Sắp lịch phỏng vấn:</b>\n"
    msg += f"   • Gọi điện / nhắn Zalo cho ứng viên tiềm năng để sơ vấn nhanh.\n"
    msg += f"   • Chốt lịch ứng viên ghé xưởng tham quan và test tay nghề cắt ráp cơ bản.\n"
    msg += f"   📍 <i>Xưởng sản xuất: 230/70/28 Nguyễn Xiển, Long Phước, Thủ Đức, TP.HCM</i>\n"
    msg += f"3. 🔄 <b>Theo dõi hiển thị:</b> Đảm bảo tin vẫn đang duy trì ở Top ngành Xây dựng / Kiến trúc.\n\n"
    
    if cand_list:
        msg += f"📁 <b>DANH SÁCH ỨNG VIÊN TIỀM NĂNG TRONG KHO:</b>\n"
        for item in cand_list:
            msg += f"{item}\n"
        msg += "\n"
        
    msg += f"🔗 <a href='{LIVE_POST_URL}'>Xem Tin Đăng Live</a> | <a href='https://songanh-marketing.phamhoangtien1300.workers.dev/#nhan-su'>WebApp Nhân Sự</a>\n"
    return msg

def send_recruitment_telegram_alert():
    bot_token, chat_id = load_telegram_credentials()
    
    today = get_vietnam_time().date()
    end_date = datetime.datetime.strptime(END_DATE_STR, "%Y-%m-%d").date()
    
    if (today - end_date).days > 1:
        print(f"Tin đăng đã kết thúc vào ngày {END_DATE_STR}. Tự động ngưng gửi thông báo.")
        return {"ok": True, "message": "Campaign expired"}
    
    msg = format_recruitment_alert_message()
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": msg,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    
    try:
        res = requests.post(url, json=payload, timeout=15)
        res_json = res.json()
        if res_json.get("ok"):
            print("✅ Gửi thông báo Tuyển Dụng qua Telegram thành công!")
        else:
            print(f"❌ Telegram API trả về lỗi: {res_json}")
        return res_json
    except Exception as e:
        print(f"❌ Lỗi kết nối Telegram API: {e}")
        return {"ok": False, "error": str(e)}

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].lower() in ["--preview", "-p"]:
        print("--- XEM TRƯỚC NỘI DUNG THÔNG BÁO 08:00 ---\n")
        print(format_recruitment_alert_message())
    else:
        print("Đang thực thi gửi thông báo Tuyển Dụng 08:00...")
        send_recruitment_telegram_alert()
