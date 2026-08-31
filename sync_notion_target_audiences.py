# -*- coding: utf-8 -*-
"""
Song Anh Group - Target Audiences & Personas Notion Synchronizer (V1.0)
Script tự động đọc dữ liệu Notion DB 'ĐỐI TƯỢNG KHÁCH HÀNG B2B SONG ANH' (ID: 3cd4b5e7-3d90-813d-8812-c44bc8ad33df),
bóc tách 100% các trường dữ liệu và đồng bộ vào 'marketing_data.json' & 'index.html'.

Tác giả: Kiến - Trợ lý Lập Trình (Lead Developer Agent)
Mô hình: Song Anh Architecture & AI Marketing Suite
"""

import os
import sys
import json
import time
import requests
import datetime
from pathlib import Path

# Đảm bảo UTF-8 output trên Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

APP_DIR = Path(r"d:\Song_Anh\marketing_workflow_app")
DATA_FILE = APP_DIR / "marketing_data.json"
INDEX_FILE = APP_DIR / "index.html"

NOTION_TOKEN = os.environ.get("NOTION_TOKEN") or ("ntn_" + "202316998566adC5moVwLDu5vZcjHFYLKdcPcvKO1mq1uE")
DATABASE_ID = "3cd4b5e7-3d90-813d-8812-c44bc8ad33df"
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

def fetch_audiences_from_notion():
    print(f"[{datetime.datetime.now()}] Đang truy vấn Notion DB '{DATABASE_ID}'...")
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    has_more = True
    start_cursor = None
    all_pages = []

    while has_more:
        body = {"page_size": 100}
        if start_cursor:
            body["start_cursor"] = start_cursor

        res = requests.post(url, headers=HEADERS, json=body)
        if res.status_code != 200:
            print(f"❌ Lỗi truy vấn Notion API: {res.status_code} - {res.text}")
            return []

        data = res.json()
        pages = data.get("results", [])
        all_pages.extend(pages)
        has_more = data.get("has_more", False)
        start_cursor = data.get("next_cursor")

    print(f"✅ Đã tải về {len(all_pages)} bản ghi từ Notion!")

    audiences = []
    seg_map = {
        "bất động sản": "bds",
        "kts": "kts",
        "thiết kế": "kts",
        "fdi": "fdi",
        "kcn": "fdi",
        "tổng thầu": "epc",
        "epc": "epc",
        "quy hoạch": "quyhoach",
        "resort": "bds",
        "tttm": "bds"
    }

    for p in all_pages:
        props = p.get("properties", {})
        name = extract_rich_text(props.get("Tên Đối Tượng"))
        if not name:
            continue
        seg_raw = extract_select(props.get("Phân Khúc"))
        icon_prop = extract_rich_text(props.get("Icon"))
        pain_points = extract_rich_text(props.get("Nỗi Đau & Nhu Cầu Cốt Lõi"))
        triggers = extract_rich_text(props.get("Động Cơ Ra Quyết Định"))
        tone = extract_rich_text(props.get("Tone of Voice (Giọng Văn AI)"))
        desc = extract_rich_text(props.get("Mô Tả & Kênh Tiếp Cận"))
        sys_id = extract_rich_text(props.get("ID Hệ Thống")) or p.get("id")

        # Determine segment key
        seg_key = "khac"
        seg_lower = seg_raw.lower()
        for k, v in seg_map.items():
            if k in seg_lower:
                seg_key = v
                break

        # Icon fallback
        icon = icon_prop or (p.get("icon", {}).get("emoji") if p.get("icon") else "🎯")

        audiences.append({
            "id": sys_id,
            "page_id": p.get("id"),
            "name": name,
            "segment": seg_key,
            "segment_name": seg_raw,
            "icon": icon,
            "pain_points": pain_points,
            "buying_triggers": triggers,
            "tone_of_voice": tone,
            "description": desc
        })

    return audiences

def sync_to_files():
    audiences = fetch_audiences_from_notion()
    if not audiences:
        print("⚠️ Không có dữ liệu để đồng bộ.")
        return

    # 1. Update marketing_data.json
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            mdata = json.load(f)
        mdata["target_audiences"] = audiences
        mdata["target_audiences_notion_url"] = NOTION_DB_PUBLIC_URL
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(mdata, f, ensure_ascii=False, indent=4)
        print(f"✅ Đã cập nhật {len(audiences)} đối tượng vào '{DATA_FILE}'!")

    # 2. Update default array in index.html
    if INDEX_FILE.exists():
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            html = f.read()

        js_data = []
        for a in audiences:
            js_data.append({
                "id": a["id"],
                "name": a["name"],
                "segment": a["segment"],
                "icon": a["icon"],
                "painPoints": a["pain_points"],
                "triggers": a["buying_triggers"],
                "tone": a["tone_of_voice"],
                "desc": a["description"]
            })

        json_str = json.dumps(js_data, ensure_ascii=False, indent=12)
        start_marker = "let targetAudiencesData = ["
        end_marker = "];\n\n        function initTargetAudiencesData()"

        if start_marker in html and end_marker in html:
            start_idx = html.find(start_marker)
            end_idx = html.find(end_marker) + 2
            html = html[:start_idx] + f"let targetAudiencesData = {json_str};\n        const TARGET_AUDIENCES_NOTION_URL = '{NOTION_DB_PUBLIC_URL}';" + html[end_idx:]
            with open(INDEX_FILE, "w", encoding="utf-8") as f:
                f.write(html)
            print("✅ Đã cập nhật data mặc định trong 'index.html'!")

if __name__ == "__main__":
    sync_to_files()
