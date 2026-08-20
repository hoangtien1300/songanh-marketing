# -*- coding: utf-8 -*-
"""
Song Anh Historical SEO Database Builder & Incremental Daily Append Engine
Tạo & Quản lý Sổ Cái Lưu Trữ Lịch Sử Thứ Hạng Google Sheet Append-Only Database
Master Files: song_anh_seo_keywords_historical_database.csv & .xlsx

Chỉ đạo kiến trúc: Sếp Phạm Hoàng Tiến
Thi công: song_anh_code_expert (Lead Developer Agent)
"""

import os
import sys
import json
import csv
import pandas as pd
from datetime import datetime

# Đảm bảo UTF-8 output trên Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

APP_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_DATA_PATH = os.path.join(APP_DIR, 'marketing_data.json')
HISTORICAL_CSV_PATH = os.path.join(APP_DIR, 'song_anh_seo_keywords_historical_database.csv')
HISTORICAL_XLSX_PATH = os.path.join(APP_DIR, 'song_anh_seo_keywords_historical_database.xlsx')

HISTORICAL_HEADERS = [
    "Ngày", "ID Từ Khóa", "Từ Khóa", "Vị Trí GSC",
    "Impressions", "Clicks", "CTR %", "URL Xếp Hạng", "Search Feature"
]

def load_marketing_json():
    if not os.path.exists(JSON_DATA_PATH):
        print(f"[ERROR] Không tìm thấy tệp JSON: {JSON_DATA_PATH}")
        return None
    with open(JSON_DATA_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_historical_files(rows_df):
    """Xuất cả CSV (UTF-8 BOM) và XLSX từ DataFrame"""
    df = pd.DataFrame(rows_df)
    # Đảm bảo thứ tự cột chuẩn
    df = df[HISTORICAL_HEADERS]
    
    # Export CSV utf-8-sig
    df.to_csv(HISTORICAL_CSV_PATH, index=False, encoding='utf-8-sig')
    print(f"[HISTORICAL DB] Đã tạo/cập nhật Sổ Cái Master CSV: {HISTORICAL_CSV_PATH} ({len(df)} dòng)")
    
    # Export Excel .xlsx
    df.to_excel(HISTORICAL_XLSX_PATH, index=False, engine='openpyxl')
    print(f"[HISTORICAL DB] Đã tạo/cập nhật Sổ Cái Master XLSX: {HISTORICAL_XLSX_PATH} ({len(df)} dòng)")
    return df

def build_initial_historical_database():
    """Trích xuất toàn bộ rankHistory từ marketing_data.json để xây dựng Sổ Cái Lịch Sử ban đầu"""
    data = load_marketing_json()
    if not data:
        return False

    keywords = data.get("seo_keywords", [])
    print(f"[BUILD HISTORICAL DB] Đang xử lý {len(keywords)} từ khóa từ marketing_data.json...")

    all_rows = []
    
    for kw in keywords:
        kw_id = kw.get("id")
        kw_name = kw.get("name", "").strip()
        kw_url = kw.get("url", "").strip()
        if kw_url and not kw_url.startswith("http"):
            kw_url = f"https://{kw_url}"
        kw_feature = kw.get("searchFeature", "🖼️ Image Pack" if kw.get("highlight") else "Standard Snippet")
        
        rank_history = kw.get("rankHistory", [])
        for entry in rank_history:
            date_str = entry.get("date", "").strip()
            gsc_pos = entry.get("rank") if entry.get("rank") is not None else entry.get("gscPos", 999.0)
            imp = entry.get("impressions", 0)
            clicks = entry.get("clicks", 0)
            ctr_val = entry.get("ctr", "0.00%")
            if isinstance(ctr_val, (int, float)):
                ctr_str = f"{ctr_val:.2f}%"
            else:
                ctr_str = str(ctr_val)
            
            all_rows.append({
                "Ngày": date_str,
                "ID Từ Khóa": kw_id,
                "Từ Khóa": kw_name,
                "Vị Trí GSC": gsc_pos,
                "Impressions": imp,
                "Clicks": clicks,
                "CTR %": ctr_str,
                "URL Xếp Hạng": kw_url,
                "Search Feature": kw_feature
            })

    # Sắp xếp lại theo ngày (DD/MM/YYYY) và ID Từ Khóa
    def date_key(item):
        try:
            return datetime.strptime(item["Ngày"], "%d/%m/%Y")
        except Exception:
            return datetime.min

    all_rows.sort(key=lambda x: (date_key(x), x["ID Từ Khóa"]))

    save_historical_files(all_rows)
    print(f"[BUILD HISTORICAL DB] Hoàn thành xây dựng Sổ Cái ban đầu với tổng cộng {len(all_rows)} bản ghi nhật ký!")
    return True

def append_incremental_daily_log(current_keywords_data=None, target_date_str=None):
    """
    Cơ Chế Nạp Nối Tiếp Tự Động (Incremental Daily Append Engine):
    1. Kiểm tra file Sổ Cái CSV & XLSX. Nếu chưa tồn tại -> Tạo mới từ rankHistory.
    2. Đọc danh sách các ngày đã có trong Sổ Cái.
    3. Nếu ngày hôm nay (VD: 20/08/2026) ĐÃ CÓ -> Giữ nguyên 100%, không ghi đè.
    4. Nếu ngày hôm nay CHƯA CÓ -> Truy xuất số liệu mới và NẠP NỐI TIẾP (APPEND) 22 dòng vào Sổ Cái & marketing_data.json.
    """
    if not os.path.exists(HISTORICAL_CSV_PATH):
        print("[HISTORICAL DB] Sổ Cái chưa tồn tại. Đang khởi tạo từ dữ liệu lịch sử...")
        build_initial_historical_database()

    # Đọc dữ liệu CSV hiện tại
    try:
        df_existing = pd.read_csv(HISTORICAL_CSV_PATH, encoding='utf-8-sig')
        existing_dates = set(df_existing["Ngày"].astype(str).tolist())
    except Exception as e:
        print(f"[HISTORICAL DB ERROR] Không thể đọc file CSV: {e}")
        existing_dates = set()
        df_existing = pd.DataFrame(columns=HISTORICAL_HEADERS)

    today_str = target_date_str or datetime.now().strftime("%d/%m/%Y")
    print(f"[INCREMENTAL APPEND ENGINE] Kiểm tra mốc ngày sync: {today_str}...")

    if today_str in existing_dates:
        print(f"[HISTORICAL DB] Mốc ngày '{today_str}' ĐÃ TỒN TẠI trong Sổ Cái ({len(df_existing[df_existing['Ngày'] == today_str])} dòng).")
        print(f"[PRESERVATION RULE] Giữ nguyên 100% dữ liệu lịch sử cũ, KHÔNG GHI ĐÈ.")
        return False, len(df_existing)

    # Ngày chưa có -> Nạp nối tiếp 22 dòng mới
    print(f"[INCREMENTAL APPEND ENGINE] Mốc ngày '{today_str}' CHƯA CÓ. Tiến hành NẠP NỐI TIẾP (APPEND)...")
    
    if not current_keywords_data:
        data = load_marketing_json()
        current_keywords_data = data.get("seo_keywords", []) if data else []

    new_rows = []
    for kw in current_keywords_data:
        kw_id = kw.get("id")
        kw_name = kw.get("name", "").strip()
        gsc_pos = kw.get("gscPos") if kw.get("gscPos") is not None else 999.0
        imp = kw.get("impressions", 0)
        clicks = kw.get("clicks", 0)
        ctr_val = kw.get("ctr", "0.00%")
        if isinstance(ctr_val, (int, float)):
            ctr_str = f"{ctr_val:.2f}%"
        else:
            ctr_str = str(ctr_val)
        
        kw_url = kw.get("url", "").strip()
        if kw_url and not kw_url.startswith("http"):
            kw_url = f"https://{kw_url}"
        
        kw_feature = kw.get("searchFeature", "🖼️ Image Pack" if kw.get("highlight") else "Standard Snippet")

        new_rows.append({
            "Ngày": today_str,
            "ID Từ Khóa": kw_id,
            "Từ Khóa": kw_name,
            "Vị Trí GSC": gsc_pos,
            "Impressions": imp,
            "Clicks": clicks,
            "CTR %": ctr_str,
            "URL Xếp Hạng": kw_url,
            "Search Feature": kw_feature
        })

    # Nạp nối tiếp vào DataFrame và xuất file
    df_updated = pd.concat([df_existing, pd.DataFrame(new_rows)], ignore_index=True)
    save_historical_files(df_updated.to_dict('records'))

    # ĐỒNG THỜI cập nhật mảng rankHistory trong marketing_data.json
    json_data = load_marketing_json()
    if json_data and "seo_keywords" in json_data:
        updated_json = False
        for kw in json_data["seo_keywords"]:
            kw_id = kw.get("id")
            # Tìm match từ kw mới
            match_row = next((r for r in new_rows if r["ID Từ Khóa"] == kw_id), None)
            if match_row:
                rank_hist = kw.get("rankHistory", [])
                hist_dates = set(r.get("date") for r in rank_hist)
                if today_str not in hist_dates:
                    rank_hist.append({
                        "date": today_str,
                        "rank": match_row["Vị Trí GSC"],
                        "impressions": match_row["Impressions"],
                        "clicks": match_row["Clicks"],
                        "ctr": match_row["CTR %"]
                    })
                    kw["rankHistory"] = rank_hist
                    updated_json = True
        
        if updated_json:
            with open(JSON_DATA_PATH, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            print(f"[HISTORICAL DB] Đã đồng bộ 22 dòng ngày {today_str} vào mảng rankHistory của marketing_data.json.")

    print(f"[SUCCESS] Đã nạp nối tiếp thành công {len(new_rows)} dòng của ngày {today_str} vào Sổ Cái Lịch Sử Database!")
    return True, len(df_updated)

if __name__ == "__main__":
    print("[START] Chạy script khởi tạo / kiểm tra Sổ Cái Lịch Sử Google Sheet Database...")
    build_initial_historical_database()
    append_incremental_daily_log()
