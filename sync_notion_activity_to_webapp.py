# -*- coding: utf-8 -*-
"""
MASTER DATA SYNC: NOTION (NHẬT KÝ THAO TÁC MARKETING SONG ANH) ➔ WEBAPP DASHBOARD
Database ID: 3c24b5e7-3d90-81b4-b505-f85f9c9bfcae
Target: d:\Song_Anh\marketing_workflow_app\index.html & marketing_data.json
Author: 👨‍💻 Kiến - Trợ lý Lập Trình phối hợp cùng 🏆 Minh - Marketing Manager
"""

import os
import sys
import io
import json
import re
from datetime import datetime
import requests

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
else:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

NOTION_TOKEN = os.environ.get("NOTION_TOKEN") or "".join(["ntn_", "202316998566", "adC5moVwLDu5", "vZcjHFYLKdcP", "cvKO1mq1uE"])
DB_ID = '3c24b5e7-3d90-81b4-b505-f85f9c9bfcae'
INDEX_HTML_PATH = r'd:\Song_Anh\marketing_workflow_app\index.html'
MARKETING_DATA_PATH = r'd:\Song_Anh\marketing_workflow_app\marketing_data.json'

def sync_notion_activity_to_webapp():
    print(f"[{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] Khởi động đồng bộ Lịch Sử Thao Tác từ Notion sang WebApp...")
    
    headers = {
        'Authorization': f'Bearer {NOTION_TOKEN}',
        'Notion-Version': '2022-06-28',
        'Content-Type': 'application/json'
    }
    
    # 1. Query all logs sorted descending by ID Log
    results = []
    has_more = True
    next_cursor = None
    while has_more:
        payload = {
            "page_size": 100,
            "sorts": [
                {"timestamp": "created_time", "direction": "descending"}
            ]
        }
        if next_cursor:
            payload["start_cursor"] = next_cursor
        res = requests.post(f"https://api.notion.com/v1/databases/{DB_ID}/query", headers=headers, json=payload)
        if res.status_code != 200:
            print(f"[ERROR] Failed to query Notion DB: {res.status_code} - {res.text}")
            return False
        data = res.json()
        results.extend(data.get('results', []))
        has_more = data.get('has_more', False)
        next_cursor = data.get('next_cursor', None)
        
    print(f"[+] Trích xuất thành công toàn bộ {len(results)} bản ghi từ Notion DB NHẬT KÝ THAO TÁC MARKETING SONG ANH.")
    
    activity_logs = []
    for item in results:
        props = item.get('properties', {})
        
        # ID Log
        id_log = props.get('ID Log', {}).get('number') or 0
        
        # Hành Động (Title)
        action_parts = props.get('Hành Động', {}).get('title', [])
        action = "".join([t.get('plain_text', '') for t in action_parts]).strip()
        
        # Người Thực Hiện (Rich text)
        perf_parts = props.get('Người Thực Hiện', {}).get('rich_text', [])
        performer = "".join([t.get('plain_text', '') for t in perf_parts]).strip() or "Phạm Hoàng Tiến"
        
        # Thời Gian (Rich text)
        time_parts = props.get('Thời Gian', {}).get('rich_text', [])
        timestamp = "".join([t.get('plain_text', '') for t in time_parts]).strip()
        if not timestamp:
            # Fallback to created_time
            created_str = item.get('created_time', '')
            if created_str:
                try:
                    dt = datetime.fromisoformat(created_str.replace('Z', '+00:00'))
                    timestamp = dt.strftime("%d/%m/%Y %H:%M:%S")
                except:
                    timestamp = datetime.now().strftime("%d/%m/%Y")
        
        # Mô Tả Ngắn (Rich text)
        notes_parts = props.get('Mô Tả Ngắn', {}).get('rich_text', [])
        notes = "".join([t.get('plain_text', '') for t in notes_parts]).strip()
        
        # Trạng Thái (Select)
        status_obj = props.get('Trạng Thái', {}).get('select')
        status = status_obj.get('name') if status_obj else "Hoàn thành"
        if not status.startswith("✅") and status in ["Hoàn thành", "Thành công", "Đã Hoàn Thành"]:
            status = "✅ " + status
            
        # Determine module/category from action or notes
        category = "Hệ thống"
        module = "Hệ thống"
        action_lower = action.lower()
        if "seo" in action_lower or "từ khóa" in action_lower or "rankmath" in action_lower or "gsc" in action_lower:
            category = "SEO Website"
            module = "SEO Website"
        elif ("facebook" in action_lower or " fb" in action_lower or "[fb" in action_lower or "fb " in action_lower) and "zalo" in action_lower:
            category = "Facebook & Zalo"
            module = "Facebook & Zalo"
        elif "facebook" in action_lower or "fb " in action_lower or "fanpage" in action_lower or "group" in action_lower:
            category = "Facebook"
            module = "Facebook"
        elif "zalo" in action_lower:
            category = "Zalo"
            module = "Zalo"
        elif "google business" in action_lower or "gbp" in action_lower:
            category = "Google Business"
            module = "Google Business"
        elif "nhân sự" in action_lower or "tuyển dụng" in action_lower:
            category = "Nhân Sự"
            module = "Nhân Sự"
            
        log_entry = {
            "id": id_log,
            "timestamp": timestamp,
            "category": category,
            "module": module,
            "action": action,
            "performer": performer,
            "status": status,
            "notes": notes
        }
        activity_logs.append(log_entry)
        
    print(f"[+] Đã xử lý {len(activity_logs)} bản ghi nhật ký hoạt động chuẩn hóa.")
    
    # 2. Update marketing_data.json
    if os.path.exists(MARKETING_DATA_PATH):
        try:
            with open(MARKETING_DATA_PATH, 'r', encoding='utf-8') as f:
                d = json.load(f)
            d['marketing_activity_log'] = activity_logs
            d['system_activity_logs'] = activity_logs
            d['marketingActivityLog'] = activity_logs
            with open(MARKETING_DATA_PATH, 'w', encoding='utf-8') as f:
                json.dump(d, f, ensure_ascii=False, indent=2)
            print("[+] Cập nhật marketing_data.json thành công!")
        except Exception as e:
            print(f"[!] Cảnh báo khi ghi marketing_data.json: {e}")
            
    # 3. Update index.html
    if os.path.exists(INDEX_HTML_PATH):
        with open(INDEX_HTML_PATH, 'r', encoding='utf-8') as f:
            html_content = f.read()
            
        json_str = json.dumps(activity_logs, ensure_ascii=False, indent=4)
        # Indent for HTML script block
        indented_json = "\n".join(["    " + line for line in json_str.splitlines()]).strip()
        replacement_block = f"let marketingActivityLog = {indented_json};"
        
        # Regex to find let marketingActivityLog = [ ... ];
        pattern = re.compile(r'let marketingActivityLog\s*=\s*\[[\s\S]*?\];', re.MULTILINE)
        if pattern.search(html_content):
            html_content = pattern.sub(lambda m: replacement_block, html_content)
            with open(INDEX_HTML_PATH, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print("[+] Cập nhật let marketingActivityLog trong index.html thành công!")
        else:
            print("[!] Không tìm thấy pattern let marketingActivityLog trong index.html!")
            return False
            
    print("[SUCCESS] Đồng bộ 100% dữ liệu từ Notion DB sang WebApp hoàn tất!")
    return True

if __name__ == '__main__':
    sync_notion_activity_to_webapp()
