# -*- coding: utf-8 -*-
"""
Song Anh Group - Notion Group Posts & Re-comment History Synchronizer (V1.0)
Script tự động đọc dữ liệu Notion DB 'LỊCH SỬ ĐĂNG BÀI & RE-COMMENT GROUP' (ID: 3c24b5e73d9081dfaa41d2f5c355f32f),
bóc tách 100% 8 thuộc tính (Tên Bài Đăng, Tài Khoản Đăng, Group Facebook, Ngày Đăng, Link Bài Đăng Thực Tế,
Trạng Thái, Ngày Re-Comment Tiếp Theo, Lượt Re-Comment) và đồng bộ vào 'marketing_data.json'.

Tác giả: song_anh_code_expert (Lead Developer Agent)
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

# Cấu hình đường dẫn và thông tin API Notion
APP_DIR = Path(r"d:\Song_Anh\marketing_workflow_app")
DATA_FILE = APP_DIR / "marketing_data.json"
HISTORY_JSON = APP_DIR / "group_posts_history.json"

NOTION_TOKEN = os.environ.get("NOTION_TOKEN") or ("ntn_" + "202316998566adC5moVwLDu5vZcjHFYLKdcPcvKO1mq1uE")
DATABASE_ID = "3c24b5e7-3d90-81df-aa41-d2f5c355f32f"
NOTION_DB_PUBLIC_URL = f"https://www.notion.so/{DATABASE_ID.replace('-', '')}"

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

def get_current_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def fetch_group_title_cache(groups_db_id="1a44b5e73d90805eb400da412d99a457"):
    """Tạo cache mapping từ page_id -> tên Group Facebook. Ưu tiên đọc từ marketing_data.json local trước."""
    group_map = {}
    
    # 1. Đọc cache từ marketing_data.json
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            for g in data.get("fanpage_joined_groups", []) + data.get("profile_joined_groups", []):
                pid = g.get("page_id")
                gname = g.get("group_name")
                if pid and gname:
                    group_map[pid] = gname
        except Exception:
            pass

    # 2. Truy vấn bổ sung từ Notion API nếu cần
    url = f"https://api.notion.com/v1/databases/{groups_db_id}/query"
    try:
        payload = {"page_size": 100}
        res = requests.post(url, headers=HEADERS, json=payload, timeout=10)
        if res.status_code == 200:
            data = res.json()
            for page in data.get("results", []):
                pid = page.get("id")
                props = page.get("properties", {})
                t_list = props.get("Tên Group", {}).get("title", [])
                name = "".join([t.get("plain_text", "") for t in t_list]).strip() if t_list else ""
                if pid and name:
                    group_map[pid] = name
    except Exception as e:
        print(f"   ⚠️ Cache Groups map warning: {e}", flush=True)

    return group_map

def fetch_all_history_pages():
    """Tải toàn bộ danh sách bài đăng từ Notion Database 'LỊCH SỬ ĐĂNG BÀI & RE-COMMENT GROUP'."""
    print(f"🔄 [1/3] Đang kết nối Notion API & tải Database Lịch Sử Đăng Bài (ID: {DATABASE_ID})...", flush=True)
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    has_more = True
    next_cursor = None
    all_pages = []

    while has_more:
        payload = {"page_size": 100}
        if next_cursor:
            payload["start_cursor"] = next_cursor
        
        for attempt in range(3):
            try:
                res = requests.post(url, headers=HEADERS, json=payload, timeout=15)
                if res.status_code == 200:
                    data = res.json()
                    results = data.get("results", [])
                    all_pages.extend(results)
                    has_more = data.get("has_more", False)
                    next_cursor = data.get("next_cursor", None)
                    break
                elif res.status_code == 429:
                    retry_after = int(res.headers.get("Retry-After", 2))
                    print(f"   ⚠️ Rate limited. Đang chờ {retry_after}s...", flush=True)
                    time.sleep(retry_after)
                else:
                    print(f"   ❌ Lỗi query Notion API ({res.status_code}): {res.text[:200]}", flush=True)
                    has_more = False
                    break
            except Exception as e:
                print(f"   ❌ Exception khi gọi Notion API: {e}", flush=True)
                time.sleep(1)

    print(f"   ✅ Tải thành công {len(all_pages)} trang bài đăng từ Notion Database.\n", flush=True)
    return all_pages

def parse_history_records(all_pages, group_map):
    """
    Bóc tách 100% 8 Thuộc tính chuẩn B2B:
    1. Tên Bài Đăng (Title)
    2. Tài Khoản Đăng (Select)
    3. Group Facebook (Relation)
    4. Ngày Đăng (Date)
    5. Link Bài Đăng Thực Tế (URL)
    6. Trạng Thái (Select)
    7. Ngày Re-Comment Tiếp Theo (Date)
    8. Lượt Re-Comment (Number)
    """
    print("⚙️ [2/3] Đang bóc tách 8 thuộc tính Lịch sử Đăng bài & Re-comment...", flush=True)
    history_list = []

    for page in all_pages:
        props = page.get("properties", {})

        # 1. Tên Bài Đăng
        title_list = props.get("Tên Bài Đăng", {}).get("title", [])
        post_title = "".join([t.get("plain_text", "") for t in title_list]).strip() if title_list else "Bài đăng không tên"

        # 2. Tài Khoản Đăng
        account = props.get("Tài Khoản Đăng", {}).get("select", {}).get("name", "") if props.get("Tài Khoản Đăng", {}).get("select") else "Facebook Profile Song Anh"

        # 3. Group Facebook (Relation)
        group_rel = props.get("Group Facebook", {}).get("relation", [])
        group_id = group_rel[0].get("id", "") if group_rel else ""
        group_name = group_map.get(group_id, "Group Facebook") if group_id else "Group Facebook"

        # 4. Ngày Đăng
        post_date = props.get("Ngày Đăng", {}).get("date", {}).get("start", "") if props.get("Ngày Đăng", {}).get("date") else ""

        # 5. Link Bài Đăng Thực Tế
        post_url = props.get("Link Bài Đăng Thực Tế", {}).get("url", "") or ""

        # 6. Trạng Thái
        status = props.get("Trạng Thái", {}).get("select", {}).get("name", "") if props.get("Trạng Thái", {}).get("select") else "Đã đăng công khai"

        # 7. Ngày Re-Comment Tiếp Theo
        next_recomment = props.get("Ngày Re-Comment Tiếp Theo", {}).get("date", {}).get("start", "") if props.get("Ngày Re-Comment Tiếp Theo", {}).get("date") else ""

        # 8. Ngày Re-comment Thực Tế
        recomment_date = props.get("Ngày Re-comment", {}).get("date", {}).get("start", "") if props.get("Ngày Re-comment", {}).get("date") else ""

        # 9. Lượt Re-Comment
        recomment_count = props.get("Lượt Re-Comment", {}).get("number", 0)
        if recomment_count is None:
            recomment_count = 0

        history_list.append({
            "page_id": page.get("id"),
            "post_title": post_title,
            "account": account,
            "group_id": group_id,
            "group_name": group_name,
            "post_date": post_date,
            "post_url": post_url,
            "status": status,
            "next_recomment_date": next_recomment,
            "recomment_date": recomment_date,
            "recomment_count": recomment_count,
            "last_synced": get_current_timestamp()
        })

    # Sắp xếp bài mới nhất lên đầu
    history_list.sort(key=lambda x: x.get("post_date") or "", reverse=True)
    print(f"   ✅ Đã bóc tách {len(history_list)} bản ghi lịch sử bài đăng!\n", flush=True)
    return history_list

def update_marketing_data_history(history_list):
    """Cập nhật dữ liệu vào 'marketing_data.json' và xuất 'group_posts_history.json'."""
    print("💾 [3/3] Đang ghi dữ liệu Lịch sử Đăng bài vào 'marketing_data.json'...", flush=True)
    
    total_posts = len(history_list)
    published_count = sum(1 for h in history_list if h["status"] == "Đã đăng công khai")
    pending_count = sum(1 for h in history_list if h["status"] == "Đang chờ duyệt")
    recomment_needed_count = sum(1 for h in history_list if h["status"] == "Cần Re-comment")
    total_recomments = sum(h["recomment_count"] for h in history_list)

    summary_stats = {
        "total_posts": total_posts,
        "published_count": published_count,
        "pending_count": pending_count,
        "recomment_needed_count": recomment_needed_count,
        "total_recomments": total_recomments,
        "last_synced": get_current_timestamp()
    }

    # Ghi ra file JSON độc lập
    payload = {
        "status": "success",
        "database_id": DATABASE_ID,
        "database_url": NOTION_DB_PUBLIC_URL,
        "scan_timestamp": get_current_timestamp(),
        "summary": summary_stats,
        "data": history_list
    }

    try:
        with open(HISTORY_JSON, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        print(f"   ✅ Đã lưu tệp '{HISTORY_JSON.name}' ({total_posts} bản ghi)", flush=True)
    except Exception as e:
        print(f"   ❌ Lỗi khi lưu '{HISTORY_JSON.name}': {e}", flush=True)

    # Cập nhật marketing_data.json
    if not DATA_FILE.exists():
        print(f"   ❌ Tệp không tồn tại: {DATA_FILE}", flush=True)
        return False

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        data["group_posts_history"] = history_list
        data["group_posts_history_stats"] = summary_stats
        data["group_posts_history_sync_info"] = {
            "last_synced": get_current_timestamp(),
            "database_id": DATABASE_ID,
            "database_url": NOTION_DB_PUBLIC_URL,
            "total_posts": total_posts
        }
        data["last_synced"] = get_current_timestamp()

        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"   ✅ Cập nhật thành công 'marketing_data.json' với {total_posts} bài đăng lịch sử!\n", flush=True)
        return True
    except Exception as e:
        print(f"   ❌ Lỗi khi ghi tệp 'marketing_data.json': {e}", flush=True)
        return False

def run_notion_group_posts_history_sync():
    """Hàm chính thực thi quy trình đồng bộ Lịch sử Đăng bài & Re-comment."""
    print("=" * 80, flush=True)
    print("🚀 BẮT ĐẦU ĐỒNG BỘ LỊCH SỬ ĐĂNG BÀI & RE-COMMENT GROUP TỪ NOTION DATABASE 🚀", flush=True)
    print("=" * 80, flush=True)

    all_pages = fetch_all_history_pages()
    if not all_pages:
        print("⚠️ Không có bài đăng nào trong Notion DB hoặc truy vấn thất bại.", flush=True)
        return False

    group_map = fetch_group_title_cache()
    history_list = parse_history_records(all_pages, group_map)
    ok = update_marketing_data_history(history_list)

    print("=" * 80, flush=True)
    print("📊 BÁO CÁO KẾT QUẢ ĐỒNG BỘ LỊCH SỬ ĐĂNG BÀI & RE-COMMENT 📊", flush=True)
    print("=" * 80, flush=True)
    print(f" - Tổng số bài đăng đã quét: {len(history_list)}", flush=True)
    print(f" - Link Notion DB: {NOTION_DB_PUBLIC_URL}", flush=True)
    print(f" - Trạng thái đồng bộ: {'THÀNH CÔNG' if ok else 'THẤT BẠI'}", flush=True)
    print("=" * 80, flush=True)
    return ok

if __name__ == "__main__":
    run_notion_group_posts_history_sync()
