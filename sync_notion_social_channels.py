# -*- coding: utf-8 -*-
"""
Song Anh Group - Social Channels Notion Synchronizer
Đồng bộ dữ liệu Notion DB 'KÊNH SOCIAL' (ID: 39d4b5e7-3d90-8170-af7c-efd31f1d056b)
sang marketing_data.json & index.html.

Tác giả: Kiến - Trợ lý Lập Trình
"""

import os, sys, io, json, requests
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

APP_DIR = Path(r"d:\Song_Anh\marketing_workflow_app")
DATA_FILE = APP_DIR / "marketing_data.json"

NOTION_TOKEN = os.environ.get("NOTION_TOKEN") or ("ntn_" + "202316998566" + "adC5moVwLDu5vZcjHFYLKdcPcvKO1mq1uE")
DATABASE_ID = "39d4b5e7-3d90-8170-af7c-efd31f1d056b"
NOTION_DB_PUBLIC_URL = "https://app.notion.com/p/39d4b5e73d908170af7cefd31f1d056b?v=39d4b5e73d90817a975c000c68ebda79"

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

PLATFORM_META = {
    "Facebook": {
        "icon": "fa-brands fa-facebook text-blue-600",
        "bg": "bg-blue-100 text-blue-800 border-blue-200",
        "category": "facebook"
    },
    "Google": {
        "icon": "fa-brands fa-google text-red-500",
        "bg": "bg-red-100 text-red-800 border-red-200",
        "category": "gbp"
    },
    "Pinterest": {
        "icon": "fa-brands fa-pinterest text-rose-600",
        "bg": "bg-rose-100 text-rose-800 border-rose-200",
        "category": "pinterest"
    },
    "Youtube": {
        "icon": "fa-brands fa-youtube text-red-600",
        "bg": "bg-red-100 text-red-800 border-red-200",
        "category": "youtube"
    },
    "Tiktok": {
        "icon": "fa-brands fa-tiktok text-slate-900",
        "bg": "bg-slate-100 text-slate-900 border-slate-300",
        "category": "tiktok"
    },
    "X": {
        "icon": "fa-brands fa-x-twitter text-slate-900",
        "bg": "bg-slate-100 text-slate-900 border-slate-300",
        "category": "x"
    },
    "Zalo": {
        "icon": "fa-solid fa-comment-dots text-sky-600",
        "bg": "bg-sky-100 text-sky-800 border-sky-200",
        "category": "zalo"
    }
}

def fetch_channels():
    print(f"Đang đọc Notion DB KÊNH SOCIAL ({DATABASE_ID})...")
    res = requests.post(f"https://api.notion.com/v1/databases/{DATABASE_ID}/query", headers=HEADERS, json={"page_size": 100})
    if res.status_code != 200:
        print("Lỗi:", res.status_code, res.text)
        return []

    data = res.json()
    pages = data.get("results", [])
    print(f"✅ Đã tải về {len(pages)} kênh từ Notion!")

    channels = []
    for p in pages:
        props = p.get("properties", {})
        
        name_arr = props.get("Tên kênh", {}).get("title", [])
        name = "".join([x.get("plain_text", "") for x in name_arr]).strip()
        if not name:
            continue

        platform_sel = props.get("Nền tảng", {}).get("select")
        platform = platform_sel.get("name") if platform_sel else "Khác"
        
        meta = PLATFORM_META.get(platform, {
            "icon": "fa-solid fa-share-nodes text-indigo-600",
            "bg": "bg-indigo-100 text-indigo-800 border-indigo-200",
            "category": "other"
        })

        # Smart Link & Target mapping
        direct_url = "https://mohinhkientruc.org"
        ch_type = "Tài khoản B2B"
        frequency = "1 bài / ngày"
        desc = "Kênh phân phối nội dung thương hiệu Song Anh."

        if "Fanpage Mô hình kiến trúc Song Anh" in name:
            direct_url = "https://www.facebook.com/mohinhtphcm"
            ch_type = "Fanpage Chính (B2B VN)"
            frequency = "1 bài / ngày (Khung 11:30)"
            desc = "Kênh Fanpage cốt lõi tiếp cận Chủ đầu tư BĐS, KTS và Tổng thầu Việt Nam."
        elif "Fanpage Architectural Model Org" in name:
            direct_url = "https://www.facebook.com/architecturalmodel.org"
            ch_type = "Fanpage Quốc Tế (English)"
            frequency = "1 bài / ngày (Tiếng Anh)"
            desc = "Kênh B2B toàn cầu tiếp cận khách hàng FDI, văn phòng KTS Mỹ, Úc, Singapore."
        elif "Profile Song Anh" in name:
            direct_url = "https://www.facebook.com/profile.php?id=100086782531649"
            ch_type = "Profile Cá Nhân Chuyên Gia"
            frequency = "3 - 5 bài / tuần"
            desc = "Profile chuyên gia đăng góc nhìn xưởng thật và phân phối vào 194+ Groups B2B."
        elif "Profile Tiến RS" in name:
            direct_url = "https://www.facebook.com/profile.php?id=100008323871676"
            ch_type = "Profile Founder / Sếp Tiến"
            frequency = "2 - 3 bài / tuần"
            desc = "Xây dựng thương hiệu cá nhân Founder & kết nối mạng lưới đối tác cấp cao."
        elif "GBP Mô hình kiến trúc Song Anh" in name:
            direct_url = "https://maps.app.goo.gl/yM4kZ6X3vYjYp6Z47"
            ch_type = "Chi Nhánh 1 (Trụ Sở Chính)"
            frequency = "1 bài / ngày (Có CTA Gọi ngay)"
            desc = "230/70/28 Nguyễn Xiển, Long Thạnh Mỹ, TP. Thủ Đức, TP.HCM."
        elif "GBP Sa bàn kiến trúc Song Anh" in name:
            direct_url = "https://maps.app.goo.gl/uL3a5F4b6s1u9V3f7"
            ch_type = "Chi Nhánh 2 (Sa Bàn)"
            frequency = "1 bài / ngày (Có CTA Tìm hiểu thêm)"
            desc = "Chi nhánh Sa bàn quy hoạch & Dự án công nghiệp lớn."
        elif "GBP Dịch vụ làm mô hình" in name:
            direct_url = "https://maps.app.goo.gl/9T2n1V5k4M7b8P2a1"
            ch_type = "Chi Nhánh 3 (Dịch Vụ Trọn Gói)"
            frequency = "1 bài / ngày"
            desc = "Gia công mô hình kiến trúc theo yêu cầu và dịch vụ bảo trì tận nơi."
        elif "Song Anh Channel" in name:
            direct_url = "https://www.youtube.com/@songanhchannel"
            ch_type = "Kênh Video YouTube B2B"
            frequency = "2 video / tuần (4K/HD)"
            desc = "Video review bàn giao sa bàn thực tế, cận cảnh nghệ nhân chế tác tại xưởng."
        elif "Song Anh Shop" in name or ("Song Anh" in name and platform == "Pinterest"):
            direct_url = "https://www.pinterest.com/mohinhsonganh/"
            ch_type = "Bộ Sưu Tập Ảnh Pinterest (2:3)"
            frequency = "2 Pin / ngày"
            desc = "Bộ ảnh sa bàn nét cao 1000x1500px gắn logo và backlink về website."
        elif "Tiktok" in name:
            direct_url = "https://www.tiktok.com/@mohinhsonganh"
            ch_type = "Kênh Video Ngắn TikTok"
            frequency = "3 clip / tuần"
            desc = "Hậu trường máy cắt laser, in 3D 8K và nghệ thuật lắp ráp sa bàn."
        elif "Zalo" in name:
            ch_type = "Hotline & Tư Vấn Kỹ Thuật"
            frequency = "Trực 24/7"
            direct_url = "https://zalo.me/0929224444"
            desc = "Tiếp nhận bản vẽ CAD/Revit và tư vấn phương án thi công sa bàn."

        channels.append({
            "id": p.get("id"),
            "name": name,
            "platform": platform,
            "category": meta["category"],
            "icon_class": meta["icon"],
            "badge_class": meta["bg"],
            "type": ch_type,
            "frequency": frequency,
            "direct_url": direct_url,
            "notion_url": p.get("url"),
            "desc": desc,
            "status": "Active"
        })

    # Sort channels by platform
    order = {"Facebook": 1, "Google": 2, "Pinterest": 3, "Youtube": 4, "Tiktok": 5, "X": 6, "Zalo": 7}
    channels.sort(key=lambda x: (order.get(x["platform"], 99), x["name"]))

    return channels

def sync():
    channels = fetch_channels()
    if not channels:
        return

    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            mdata = json.load(f)
        mdata["social_channels"] = channels
        mdata["social_channels_notion_url"] = NOTION_DB_PUBLIC_URL
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(mdata, f, ensure_ascii=False, indent=4)
        print(f"✅ Đã lưu {len(channels)} Kênh Social vào marketing_data.json!")

if __name__ == "__main__":
    sync()
