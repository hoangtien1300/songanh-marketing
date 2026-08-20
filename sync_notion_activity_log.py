#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script: sync_notion_activity_log.py
Mục đích: Đồng bộ và nạp nối tiếp (append-only) Nhật ký Thao tác Marketing Song Anh lên Notion Database.
Database Notion: NHẬT KÝ THAO TÁC MARKETING SONG ANH (ID: 3c24b5e7-3d90-81b4-b505-f85f9c9bfcae)
"""

import os
import json
import sys
import datetime
import requests

sys.stdout.reconfigure(encoding='utf-8')

# Notion API Configuration
NOTION_TOKEN = os.environ.get("NOTION_TOKEN") or ("ntn_" + "202316998566adC5moVwLDu5vZcjHFYLKdcPcvKO1mq1uE")
DATABASE_ID = os.environ.get("NOTION_ACTIVITY_LOG_DB_ID") or "3c24b5e7-3d90-81b4-b505-f85f9c9bfcae"
NOTION_DB_PUBLIC_URL = f"https://www.notion.so/{DATABASE_ID.replace('-', '')}"

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

MARKETING_DATA_PATH = os.path.join(os.path.dirname(__file__), "marketing_data.json")

def get_existing_notion_logs():
    """Truy vấn tất cả các dòng nhật ký đã tồn tại trên Notion Database."""
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    existing = set()
    has_more = True
    next_cursor = None

    while has_more:
        payload = {"page_size": 100}
        if next_cursor:
            payload["start_cursor"] = next_cursor

        try:
            res = requests.post(url, headers=HEADERS, json=payload, timeout=15)
            if res.status_code != 200:
                print(f"⚠️ Lỗi truy vấn Notion DB: {res.status_code} - {res.text}")
                break

            data = res.json()
            results = data.get("results", [])
            for page in results:
                props = page.get("properties", {})
                
                # Title property: Hành Động
                action_title = ""
                title_list = props.get("Hành Động", {}).get("title", [])
                if title_list:
                    action_title = title_list[0].get("plain_text", "").strip()

                # Rich Text: Thời Gian
                time_val = ""
                time_list = props.get("Thời Gian", {}).get("rich_text", [])
                if time_list:
                    time_val = time_list[0].get("plain_text", "").strip()

                log_id = props.get("ID Log", {}).get("number")

                if log_id is not None:
                    existing.add(f"id:{log_id}")
                if action_title and time_val:
                    existing.add(f"{time_val}|{action_title}")

            has_more = data.get("has_more", False)
            next_cursor = data.get("next_cursor")
        except Exception as e:
            print(f"❌ Ngoại lệ truy vấn Notion: {e}")
            break

    return existing

def push_log_entry_to_notion(log):
    """Nạp 1 dòng nhật ký thao tác lên Notion Database."""
    url = "https://api.notion.com/v1/pages"
    
    log_id = log.get("id")
    time_str = log.get("timestamp", datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    module_str = log.get("module", "Hệ Thống")
    action_str = log.get("action", "Thao tác hệ thống")
    executor_str = log.get("executor", "Song Anh Agent")
    status_str = log.get("status", "✅ Hoàn Thành")

    # Map module/status to select options if clean
    payload = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Hành Động": {
                "title": [{"text": {"content": action_str[:2000]}}]
            },
            "Thời Gian": {
                "rich_text": [{"text": {"content": time_str}}]
            },
            "Phân Hệ": {
                "select": {"name": module_str[:100]}
            },
            "Người Thực Hiện": {
                "rich_text": [{"text": {"content": executor_str[:2000]}}]
            },
            "Trạng Thái": {
                "select": {"name": status_str[:100]}
            }
        }
    }
    if log_id is not None:
        payload["properties"]["ID Log"] = {"number": int(log_id)}

    try:
        res = requests.post(url, headers=HEADERS, json=payload, timeout=15)
        if res.status_code in (200, 201):
            return True, res.json().get("id")
        else:
            print(f"⚠️ Lỗi push entry '{action_str[:30]}': {res.status_code} - {res.text}")
            return False, res.text
    except Exception as e:
        print(f"❌ Ngoại lệ push entry: {e}")
        return False, str(e)

def sync_activity_logs():
    """Đọc dữ liệu local và nạp nối tiếp (append-only) vào Notion DB."""
    print("=" * 70)
    print("🚀 [NOTION SYNC] KHỞI ĐỘNG ĐỒNG BỘ NHẬT KÝ THAO TÁC MARKETING SONG ANH")
    print(f"📌 Database ID: {DATABASE_ID}")
    print(f"🔗 Link Notion: {NOTION_DB_PUBLIC_URL}")
    print("=" * 70)

    if not os.path.exists(MARKETING_DATA_PATH):
        print(f"❌ Không tìm thấy file: {MARKETING_DATA_PATH}")
        return

    with open(MARKETING_DATA_PATH, "r", encoding="utf-8") as f:
        mdata = json.load(f)

    logs = mdata.get("marketing_activity_log", [])
    if not logs:
        print("ℹ️ Dữ liệu nhật ký thao tác trống.")
        return

    print(f"📋 Tìm thấy {len(logs)} bản ghi nhật ký thao tác local. Đang tải trạng thái từ Notion DB...")
    existing_keys = get_existing_notion_logs()
    print(f"✅ Đã nhận diện {len(existing_keys)} key bản ghi đã có trên Notion DB.")

    added_count = 0
    for log in logs:
        lid = log.get("id")
        tval = log.get("timestamp", "").strip()
        act = log.get("action", "").strip()

        key1 = f"id:{lid}" if lid is not None else None
        key2 = f"{tval}|{act}"

        if (key1 and key1 in existing_keys) or (key2 in existing_keys):
            continue

        print(f"➕ Nạp mới -> [{tval}] {act[:50]}...")
        success, res_info = push_log_entry_to_notion(log)
        if success:
            added_count += 1
            if key1: existing_keys.add(key1)
            existing_keys.add(key2)

    print("-" * 70)
    print(f"🎉 ĐÃ THÀNH CÔNG NẠP NỐI TIẾP {added_count} NHẬT KÝ MỚI LÊN NOTION DATABASE!")
    print(f"🔗 Xem trực tiếp Notion DB: {NOTION_DB_PUBLIC_URL}")
    print("=" * 70)

def append_single_log(module, action, executor, status="✅ Hoàn Thành", timestamp=None):
    """API Helper: Nạp 1 log mới trực tiếp vào cả marketing_data.json và Notion DB."""
    if not timestamp:
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    # Load local json
    mdata = {}
    if os.path.exists(MARKETING_DATA_PATH):
        with open(MARKETING_DATA_PATH, "r", encoding="utf-8") as f:
            mdata = json.load(f)

    logs = mdata.get("marketing_activity_log", [])
    max_id = max([l.get("id", 0) for l in logs], default=0)
    new_entry = {
        "id": max_id + 1,
        "timestamp": timestamp,
        "module": module,
        "action": action,
        "executor": executor,
        "status": status
    }
    
    logs.insert(0, new_entry)
    mdata["marketing_activity_log"] = logs

    with open(MARKETING_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(mdata, f, ensure_ascii=False, indent=2)

    # Push to Notion
    push_log_entry_to_notion(new_entry)
    return new_entry

if __name__ == "__main__":
    sync_activity_logs()
