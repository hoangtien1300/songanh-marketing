# -*- coding: utf-8 -*-
"""
Song Anh Group - Daily Marketing Sync Engine (V21.0 Upgraded)
Worker Script tự động nạp/cập nhật dữ liệu từ Google Sheets CSV / Notion API
và tính toán động Summary KPI Cards cho SEO Keywords, đồng bộ sang Google Drive.

Tác giả: song_anh_code_expert (Lead Developer Agent)
Mô hình: Song Anh Architecture & AI Marketing Suite
"""

import os
import sys
import json
import csv
import re
import shutil
import datetime
import urllib.request
import urllib.error
import argparse
from pathlib import Path

# Đảm bảo UTF-8 output trên Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Cấu hình đường dẫn mặc định
APP_DIR = Path(r"d:\Song_Anh\marketing_workflow_app")
DATA_FILE = APP_DIR / "marketing_data.json"
INDEX_FILE = APP_DIR / "index.html"
GDRIVE_DIR = Path(r"G:\My Drive\AI Agent System\AG_Tool_May_Lap_Steven")

def get_current_timestamp():
    """Trả về timestamp định dạng YYYY-MM-DD HH:MM:SS"""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def parse_rank_val(rank_str):
    """Trích xuất giá trị số thực thứ hạng từ chuỗi thứ hạng."""
    if isinstance(rank_str, (int, float)):
        return float(rank_str)
    if not rank_str:
        return 999.0
    match = re.search(r"(\d+(?:\.\d+)?)", str(rank_str))
    return float(match.group(1)) if match else 999.0

def load_marketing_data(file_path=DATA_FILE):
    """Nạp dữ liệu từ tệp JSON trung tâm"""
    if not file_path.exists():
        print(f"[ERROR] Tệp dữ liệu không tồn tại: {file_path}")
        return None
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"[ERROR] Lỗi nạp JSON {file_path}: {e}")
        return None

def save_marketing_data(data, file_path=DATA_FILE):
    """Lưu dữ liệu và cập nhật timestamp nạp dữ liệu"""
    try:
        data["last_synced"] = get_current_timestamp()
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[SUCCESS] Đã lưu và cập nhật tệp JSON: {file_path} (lúc {data['last_synced']})")
        return True
    except Exception as e:
        print(f"[ERROR] Lỗi khi lưu tệp JSON: {e}")
        return False

def recalculate_seo_summary(data):
    """Tự động tính toán động các chỉ số Summary KPI Cards từ danh sách từ khóa."""
    keywords = data.get("seo_keywords", [])
    total = len(keywords)
    top1_3 = 0
    top4_10 = 0
    top11_30 = 0
    top31_plus = 0
    total_impressions = 0
    total_clicks = 0

    for kw in keywords:
        rank_val = parse_rank_val(kw.get("gscPos") if kw.get("gscPos") is not None else kw.get("currRank", ""))
        if rank_val <= 3.0:
            top1_3 += 1
        elif rank_val <= 10.0:
            top4_10 += 1
        elif rank_val <= 30.0:
            top11_30 += 1
        else:
            top31_plus += 1
        
        total_impressions += int(kw.get("impressions") or 0)
        total_clicks += int(kw.get("clicks") or 0)

    avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0.0

    summary_kpi = {
        "total_keywords": total,
        "top1_3": top1_3,
        "top4_10": top4_10,
        "top11_30": top11_30,
        "top31_plus": top31_plus,
        "total_impressions": total_impressions,
        "total_clicks": total_clicks,
        "avg_ctr": f"{avg_ctr:.2f}%",
        "last_calculated": get_current_timestamp()
    }

    data["seo_summary_kpi"] = summary_kpi
    print(f"[CALCULATE KPI] Tổng số: {total} | Top 1-3: {top1_3} | Top 4-10: {top4_10} | Top 11-30: {top11_30} | Top 31+: {top31_plus}")
    return summary_kpi

def fetch_from_google_sheet_csv(csv_url_or_id):
    """
    Đầu nối Tích hợp Google Sheet CSV.
    Nhận vào URL CSV trực tiếp hoặc Google Sheet ID và parse danh sách từ khóa.
    """
    if not csv_url_or_id.startswith("http://") and not csv_url_or_id.startswith("https://"):
        csv_url = f"https://docs.google.com/spreadsheets/d/{csv_url_or_id}/export?format=csv"
    else:
        csv_url = csv_url_or_id

    print(f"\n[GOOGLE SHEET CONNECTOR] Đang nạp dữ liệu từ CSV: {csv_url}...")
    try:
        req = urllib.request.Request(csv_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=15) as response:
            content = response.read().decode('utf-8')

        lines = content.splitlines()
        reader = csv.DictReader(lines)
        parsed_keywords = []

        for idx, row in enumerate(reader, start=1):
            # Hỗ trợ linh hoạt nhiều tên cột khác nhau trên Google Sheet
            name = row.get("Từ Khóa") or row.get("Keyword") or row.get("name") or f"KW-{idx}"
            init_rank = row.get("Rank Ban Đầu") or row.get("initRank") or "Top 20.0"
            init_date = row.get("Ngày Ban Đầu") or row.get("initDate") or "18/08/2026"
            curr_rank = row.get("Rank Hiện Tại") or row.get("currRank") or "Top 10.0"
            url = row.get("URL") or row.get("url") or "mohinhkientruc.org"
            change = row.get("Thay Đổi") or row.get("change") or "Giữ nguyên"
            kw_type = row.get("Loại Từ Khóa") or row.get("type") or "Từ Khóa Phụ"
            intent = row.get("Intent") or row.get("intent") or "Transactional B2B"
            priority = row.get("Ưu Tiên") or row.get("priority") or "Ưu Tiên 2 (P2)"
            silo = row.get("Cụm Silo") or row.get("silo") or "Cụm SEO"
            highlight = str(row.get("Highlight") or row.get("highlight")).strip().lower() in ["true", "1", "yes"]

            parsed_keywords.append({
                "id": idx,
                "name": name.strip(),
                "initRank": init_rank.strip(),
                "initDate": init_date.strip(),
                "currRank": curr_rank.strip(),
                "url": url.strip(),
                "change": change.strip(),
                "type": kw_type.strip(),
                "intent": intent.strip(),
                "priority": priority.strip(),
                "silo": silo.strip(),
                "highlight": highlight
            })

        print(f"[GOOGLE SHEET CONNECTOR] Nạp thành công {len(parsed_keywords)} từ khóa từ Google Sheet!")
        return parsed_keywords
    except Exception as e:
        print(f"[ERROR GOOGLE SHEET] Không thể đọc dữ liệu từ Google Sheet CSV: {e}")
        return None

def fetch_from_notion_db(database_id, api_token):
    """
    Đầu nối Tích hợp Notion API Database.
    Truy vấn Notion Database endpoint v1/databases/{database_id}/query để lấy thứ hạng SEO.
    """
    print(f"\n[NOTION API CONNECTOR] Đang nạp dữ liệu từ Notion Database ID: {database_id}...")
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }

    try:
        req = urllib.request.Request(url, data=json.dumps({}).encode('utf-8'), headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=15) as response:
            res_body = response.read().decode('utf-8')
            res_json = json.loads(res_body)

        results = res_json.get("results", [])
        parsed_keywords = []

        for idx, page in enumerate(results, start=1):
            props = page.get("properties", {})

            # Trích xuất Title/Name
            title_prop = props.get("Name") or props.get("Từ Khóa") or props.get("Keyword") or {}
            title_list = title_prop.get("title", [])
            name = title_list[0].get("text", {}).get("content", f"KW-{idx}") if title_list else f"KW-{idx}"

            # Trích xuất Rank hiện tại
            curr_prop = props.get("CurrRank") or props.get("Rank Hiện Tại") or {}
            curr_list = curr_prop.get("rich_text", [])
            curr_rank = curr_list[0].get("text", {}).get("content", "Top 10.0") if curr_list else "Top 10.0"

            # Trích xuất Rank ban đầu
            init_prop = props.get("InitRank") or props.get("Rank Ban Đầu") or {}
            init_list = init_prop.get("rich_text", [])
            init_rank = init_list[0].get("text", {}).get("content", "Top 15.0") if init_list else "Top 15.0"

            # Trích xuất URL
            url_prop = props.get("URL") or props.get("Url") or {}
            page_url = url_prop.get("url") or (url_prop.get("rich_text", [{}])[0].get("text", {}).get("content", "mohinhkientruc.org") if url_prop.get("rich_text") else "mohinhkientruc.org")

            # Trích xuất Change
            change_prop = props.get("Change") or props.get("Thay Đổi") or {}
            change_list = change_prop.get("rich_text", [])
            change = change_list[0].get("text", {}).get("content", "Giữ nguyên") if change_list else "Giữ nguyên"

            parsed_keywords.append({
                "id": idx,
                "name": name,
                "initRank": init_rank,
                "initDate": "18/08/2026",
                "currRank": curr_rank,
                "url": page_url,
                "change": change,
                "type": "Từ Khóa Chính (Core Focus)",
                "intent": "Transactional B2B",
                "priority": "Ưu Tiên 1 (P1)",
                "silo": "Notion Auto Sync",
                "highlight": False
            })

        print(f"[NOTION API CONNECTOR] Nạp thành công {len(parsed_keywords)} từ khóa từ Notion Database!")
        return parsed_keywords
    except Exception as e:
        print(f"[ERROR NOTION API] Không thể truy vấn Notion Database: {e}")
        return None

CSV_FILE = APP_DIR / "song_anh_seo_keywords_master_dataset.csv"
XLSX_FILE = APP_DIR / "song_anh_seo_keywords_master_dataset.xlsx"
HISTORICAL_CSV_FILE = APP_DIR / "song_anh_seo_keywords_historical_database.csv"
HISTORICAL_XLSX_FILE = APP_DIR / "song_anh_seo_keywords_historical_database.xlsx"
HISTORICAL_BUILDER_FILE = APP_DIR / "build_historical_db.py"
EXTRACTOR_FILE = APP_DIR / "gsc_ga4_seo_extractor.py"
ENGINE_FILE = APP_DIR / "song_anh_daily_sync_engine.py"
BAT_FILE = APP_DIR / "run_daily_seo_sync.bat"
GS_FILE = APP_DIR / "song_anh_gsc_ga4_auto_fetcher.gs"
NOTION_FB_TASKS_SYNC_FILE = APP_DIR / "sync_notion_fb_tasks_to_webapp.py"

def sync_to_gdrive(source_files=[INDEX_FILE, DATA_FILE, CSV_FILE, XLSX_FILE, HISTORICAL_CSV_FILE, HISTORICAL_XLSX_FILE, HISTORICAL_BUILDER_FILE, EXTRACTOR_FILE, ENGINE_FILE, BAT_FILE, GS_FILE, NOTION_FB_TASKS_SYNC_FILE], dest_dir=GDRIVE_DIR):
    """Đồng bộ các tệp chỉ định sang Google Drive"""
    print(f"\n[SYNC ENGINE] Bắt đầu đồng bộ sang Google Drive...")
    print(f"--> Thư mục đích: {dest_dir}")
    
    if not dest_dir.exists():
        try:
            dest_dir.mkdir(parents=True, exist_ok=True)
            print(f"[INFO] Đã tạo thư mục đích trên Google Drive: {dest_dir}")
        except Exception as e:
            print(f"[ERROR] Không thể tạo thư mục Google Drive: {e}")
            return False

    success_count = 0
    for src in source_files:
        src_path = Path(src)
        if not src_path.exists():
            print(f"[WARN] Tệp nguồn không tồn tại, bỏ qua: {src_path}")
            continue
        
        dst_path = dest_dir / src_path.name
        try:
            shutil.copy2(src_path, dst_path)
            file_size_kb = os.path.getsize(dst_path) / 1024
            print(f"  [✔ SYNCED] {src_path.name} -> {dst_path} ({file_size_kb:.2f} KB)")
            success_count += 1
        except Exception as e:
            print(f"  [❌ FAILED] Không thể đồng bộ {src_path.name}: {e}")
            
    print(f"[SYNC ENGINE] Hoàn tất đồng bộ {success_count}/{len(source_files)} tệp sang Google Drive.\n")
    return success_count == len(source_files)

def run_daily_sync(gsheet_url=None, notion_db_id=None, notion_token=None):
    """Hàm chạy quy trình đồng bộ hàng ngày"""
    print(f"==================================================")
    print(f" SONG ANH GROUP - DAILY SYNC ENGINE V21.0")
    print(f" Thời gian: {get_current_timestamp()}")
    print(f"==================================================")

    # 1. Load data
    data = load_marketing_data()
    if data is None:
        print("[CANCELLED] Không thể tải dữ liệu marketing_data.json")
        return False

    # 2. Kiểm tra nạp dữ liệu từ Google Sheets hoặc Notion nếu được cung cấp
    external_kw = None
    gs_url = gsheet_url or os.environ.get("GOOGLE_SHEET_CSV_URL")
    notion_id = notion_db_id or os.environ.get("NOTION_DATABASE_ID")
    notion_tk = notion_token or os.environ.get("NOTION_API_TOKEN")

    if gs_url:
        external_kw = fetch_from_google_sheet_csv(gs_url)
    elif notion_id and notion_tk:
        external_kw = fetch_from_notion_db(notion_id, notion_tk)

    if external_kw:
        data["seo_keywords"] = external_kw
        print(f"[SYNC ENGINE] Đã cập nhật {len(external_kw)} từ khóa từ Nguồn Tích Hợp Ngoại Thành Công!")

    # 2.5. Tự động chạy đồng bộ Task Facebook Marketing từ Notion DB
    try:
        from sync_notion_fb_tasks_to_webapp import run_notion_fb_tasks_sync
        print("\n[SYNC ENGINE] Kích hoạt Synchronizer Task Facebook Marketing từ Notion...")
        run_notion_fb_tasks_sync()
        refreshed = load_marketing_data()
        if refreshed:
            data = refreshed
    except Exception as e:
        print(f"[NOTION FB TASKS WARN] Lỗi khi thực thi sync_notion_fb_tasks_to_webapp: {e}")

    # 3. Tính toán Động KPI Summary Cards
    recalculate_seo_summary(data)
    data["system_info"]["last_engine_run"] = get_current_timestamp()
    
    # 4. Save JSON
    saved = save_marketing_data(data)
    if not saved:
        print("[CANCELLED] Lưu tệp JSON thất bại!")
        return False

    # 4.5. Trigger Incremental Daily Append Engine cho Sổ Cái Lịch Sử Database
    try:
        from build_historical_db import append_incremental_daily_log
        append_incremental_daily_log(data.get("seo_keywords", []))
    except Exception as e:
        print(f"[HISTORICAL DB WARN] Không thể chạy append_incremental_daily_log: {e}")

    # 5. Sync to Google Drive
    synced = sync_to_gdrive()
    
    if synced:
        print(f"[COMPLETE] Tự động hóa đồng bộ thành công 100%!")
    else:
        print(f"[WARNING] Quy trình đồng bộ hoàn tất với cảnh báo.")
        
    return synced

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Song Anh Daily Marketing Sync Engine")
    parser.add_argument("--gsheet", help="Google Sheet CSV Export URL hoặc Sheet ID")
    parser.add_argument("--notion-db", help="Notion Database ID")
    parser.add_argument("--notion-token", help="Notion Integration API Token")
    args = parser.parse_args()

    run_daily_sync(gsheet_url=args.gsheet, notion_db_id=args.notion_db, notion_token=args.notion_token)
