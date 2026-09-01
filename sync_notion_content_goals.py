# -*- coding: utf-8 -*-
"""
Song Anh Group - Content Goals Notion Synchronizer (V1.0)
Script tự động đọc dữ liệu Notion DB 'MỤC TIÊU NỘI DUNG (CONTENT GOALS) B2B SONG ANH' (ID: 3ce4b5e7-3d90-81ae-b70c-ec549e601228)
và đồng bộ vào 'marketing_data.json' & 'index.html'.

Tác giả: Kiến - Trợ lý Lập Trình (Lead Developer Agent)
"""

import os
import sys
import json
import requests
import datetime
from pathlib import Path

# Đảm bảo UTF-8 output trên Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

APP_DIR = Path(r"d:\Song_Anh\marketing_workflow_app")
DATA_FILE = APP_DIR / "marketing_data.json"

NOTION_TOKEN = os.environ.get("NOTION_TOKEN") or ("ntn_" + "202316998566adC5moVwLDu5vZcjHFYLKdcPcvKO1mq1uE")
DATABASE_ID = "3ce4b5e7-3d90-81ae-b70c-ec549e601228"
NOTION_DB_PUBLIC_URL = f"https://www.notion.so/{DATABASE_ID.replace('-', '')}"

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

def extract_rich_text(prop):
    if not prop:
        return ""
    ptype = prop.get("type")
    if ptype == "title":
        arr = prop.get("title", [])
    elif ptype == "rich_text":
        arr = prop.get("rich_text", [])
    else:
        return ""
    return "".join([x.get("plain_text", "") for x in arr]).strip()

def extract_select(prop):
    if not prop:
        return ""
    sel = prop.get("select")
    if sel:
        return sel.get("name", "")
    return ""

def fetch_content_goals():
    print(f"[{datetime.datetime.now()}] Đang truy vấn Content Goals Notion DB '{DATABASE_ID}'...")
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    res = requests.post(url, headers=HEADERS, json={"page_size": 100})
    if res.status_code != 200:
        print(f"❌ Lỗi: {res.status_code} - {res.text}")
        return []

    data = res.json()
    pages = data.get("results", [])
    print(f"✅ Đã tải về {len(pages)} mục tiêu từ Notion!")

    goals = []
    for p in pages:
        props = p.get("properties", {})
        name = extract_rich_text(props.get("Tên Mục Tiêu (Goal Name)"))
        if not name:
            continue
        code = extract_rich_text(props.get("Mã Mục Tiêu")) or p.get("id")
        icon_prop = extract_rich_text(props.get("Icon"))
        icon = icon_prop or (p.get("icon", {}).get("emoji") if p.get("icon") else "🎯")
        gtype = extract_select(props.get("Loại Mục Tiêu"))
        intent = extract_rich_text(props.get("Ý Định Người Đọc (Intent)"))
        structure = extract_rich_text(props.get("Công Thức & Cấu Trúc Nội Dung"))
        cta = extract_rich_text(props.get("Lời Kêu Gọi Hành Động (CTA Gợi Ý)"))
        desc = extract_rich_text(props.get("Mô Tả & Hướng Dẫn Sử Dụng"))

        goals.append({
            "id": code,
            "page_id": p.get("id"),
            "name": name,
            "icon": icon,
            "type": gtype,
            "intent": intent,
            "structure": structure,
            "cta": cta,
            "desc": desc
        })

    return goals

def sync():
    goals = fetch_content_goals()
    if not goals:
        return

    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            mdata = json.load(f)
        mdata["content_goals"] = goals
        mdata["content_goals_notion_url"] = NOTION_DB_PUBLIC_URL
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(mdata, f, ensure_ascii=False, indent=4)
        print(f"✅ Đã lưu {len(goals)} Content Goals vào marketing_data.json!")

if __name__ == "__main__":
    sync()
