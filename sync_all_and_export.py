# -*- coding: utf-8 -*-
"""
Full Sync & Export Script for Song Anh Marketing Suite
Date: 2026-08-21
"""

import os
import sys
import json
import re
import time
import requests
import datetime
import shutil
from pathlib import Path
import pandas as pd

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

APP_DIR = Path(r"d:\Song_Anh\marketing_workflow_app")
DATA_FILE = APP_DIR / "marketing_data.json"
INDEX_FILE = APP_DIR / "index.html"
FANPAGE_JSON = APP_DIR / "fanpage_joined_groups.json"
PROFILE_JSON = APP_DIR / "profile_joined_groups.json"
PROFILE_XLSX = APP_DIR / "profile_joined_groups.xlsx"
FANPAGE_XLSX = APP_DIR / "fanpage_joined_groups.xlsx"
HISTORY_JSON = APP_DIR / "group_posts_history.json"
GDRIVE_DIR = Path(r"G:\My Drive\AI Agent System\AG_Tool_May_Lap_Steven")

NOTION_TOKEN = os.environ.get("NOTION_TOKEN") or ("ntn_" + "202316998566adC5moVwLDu5vZcjHFYLKdcPcvKO1mq1uE")
GROUPS_DB_ID = "1a44b5e7-3d90-805e-b400-da412d99a457"
HISTORY_DB_ID = "3c24b5e7-3d90-81df-aa41-d2f5c355f32f"
LOG_DB_ID = "3c24b5e7-3d90-81b4-b505-f85f9c9bfcae"

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

def get_current_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def extract_gid_from_url(url):
    if not url:
        return ""
    m = re.search(r"facebook\.com/groups/([^/?#]+)", url, re.IGNORECASE)
    return m.group(1).strip() if m else ""

def parse_members_num(mem_str):
    if not mem_str:
        return 0
    m = re.search(r"([\d\.\,]+)", mem_str)
    if m:
        num_s = m.group(1).replace(".", "").replace(",", "")
        try:
            return int(num_s)
        except ValueError:
            return 0
    return 0

def run_sync():
    # 1. Tải tất cả Notion Group Pages
    print("🔄 [1/5] Đang tải toàn bộ Groups từ Notion API...", flush=True)
    url = f"https://api.notion.com/v1/databases/{GROUPS_DB_ID}/query"
    has_more = True
    next_cursor = None
    all_pages = []

    while has_more:
        payload = {"page_size": 100}
        if next_cursor:
            payload["start_cursor"] = next_cursor
        res = requests.post(url, headers=HEADERS, json=payload, timeout=20)
        data = res.json()
        all_pages.extend(data.get("results", []))
        has_more = data.get("has_more", False)
        next_cursor = data.get("next_cursor")

    print(f"   ✅ Tải được {len(all_pages)} trang từ Notion DB.", flush=True)

    fanpage_groups = []
    profile_groups = []
    fanpage_idx = 1
    profile_idx = 1

    for page in all_pages:
        pid = page["id"]
        props = page.get("properties", {})
        
        t_list = props.get("Tên Group", {}).get("title", [])
        gname = "".join([t.get("plain_text", "") for t in t_list]).strip() if t_list else ""
        if not gname:
            continue
        
        gurl = props.get("Link group", {}).get("url", "") or ""
        gid_list = props.get("Group ID", {}).get("rich_text", [])
        gid = "".join([t.get("plain_text", "") for t in gid_list]).strip() if gid_list else ""
        if not gid and gurl:
            gid = extract_gid_from_url(gurl)
        
        mem_list = props.get("Member (K)", {}).get("rich_text", [])
        mem_str = "".join([t.get("plain_text", "") for t in mem_list]).strip() if mem_list else ""
        mem_num = parse_members_num(mem_str)
        
        note_list = props.get("Note", {}).get("rich_text", [])
        note_str = "".join([t.get("plain_text", "") for t in note_list]).strip() if note_list else ""
        
        status_group = props.get("Trạng thái group", {}).get("select", {}).get("name", "") if props.get("Trạng thái group", {}).get("select") else "Đang hoạt động"
        
        dang_bai_list = [m.get("name", "") for m in props.get("Đăng bài", {}).get("multi_select", [])]
        gtype = props.get("Group Type", {}).get("select", {}).get("name", "") if props.get("Group Type", {}).get("select") else ""
        
        if "Cần duyệt (Duyệt nhanh)" in dang_bai_list:
            perm = "Cần duyệt (Duyệt nhanh)"
        elif any(k in dang_bai_list for k in ["Cần duyệt", "Duyệt lâu"]):
            perm = "Kiểm duyệt (Duyệt bài)"
        elif "Không cần duyệt" in dang_bai_list:
            perm = "Công khai (Đăng ngay)"
        elif any(k in dang_bai_list for k in ["Không đăng được", "Fanpage không đăng được"]):
            perm = "Không đăng được"
        elif gtype == "Private":
            perm = "Kiểm duyệt (Duyệt bài)"
        else:
            perm = "Công khai (Đăng ngay)"
            
        linh_vuc_list = [m.get("name", "") for m in props.get("Lĩnh vực", {}).get("multi_select", [])]
        chu_de = props.get("Chủ đề", {}).get("select", {}).get("name", "") if props.get("Chủ đề", {}).get("select") else ""
        cat = ", ".join(linh_vuc_list) if linh_vuc_list else (chu_de or "📐 Kiến trúc & Quy hoạch")
        
        mhkt_st = props.get("Mô hình kiến trúc Song Anh", {}).get("status", {}).get("name", "") if props.get("Mô hình kiến trúc Song Anh", {}).get("status") else ""
        fplmh_st = props.get("Fanpage Làm mô hình Song Anh", {}).get("status", {}).get("name", "") if props.get("Fanpage Làm mô hình Song Anh", {}).get("status") else ""
        mh_st = props.get("Mô Hình Song Anh", {}).get("status", {}).get("name", "") if props.get("Mô Hình Song Anh", {}).get("status") else ""
        
        profile_st = props.get("Profile Song Anh", {}).get("status", {}).get("name", "") if props.get("Profile Song Anh", {}).get("status") else ""
        steven_st = props.get("Steven Phạm", {}).get("status", {}).get("name", "") if props.get("Steven Phạm", {}).get("status") else ""
        
        mhkt_dt = props.get("[Joint Date] Fanpage Mô hình kiến trúc Song Anh", {}).get("date", {}).get("start", "") if props.get("[Joint Date] Fanpage Mô hình kiến trúc Song Anh", {}).get("date") else ""
        if not mhkt_dt:
            mhkt_dt = props.get("[Joint Date] Fanpage Làm mô hình Song Anh", {}).get("date", {}).get("start", "") if props.get("[Joint Date] Fanpage Làm mô hình Song Anh", {}).get("date") else ""
        if not mhkt_dt:
            mhkt_dt = props.get("Ngày", {}).get("date", {}).get("start", "") if props.get("Ngày", {}).get("date") else "2026-08-19"
        
        profile_dt = props.get("[Joint Date] Profile Song Anh", {}).get("date", {}).get("start", "") if props.get("[Joint Date] Profile Song Anh", {}).get("date") else ""
        if not profile_dt:
            profile_dt = props.get("Ngày", {}).get("date", {}).get("start", "") if props.get("Ngày", {}).get("date") else "2026-08-19"
        
        join_st = "Không hoạt động / Lỗi" if status_group == "Không hoạt động" else "Đã tham gia"
        
        if mhkt_st == "Đã tham gia" or fplmh_st == "Đã tham gia" or mh_st == "Đã tham gia":
            fanpage_groups.append({
                "stt": fanpage_idx,
                "page_id": pid,
                "group_name": gname,
                "group_url": gurl,
                "group_id": gid,
                "members_count": mem_str or "N/A",
                "members_num": mem_num,
                "posting_permission": perm,
                "category": cat,
                "join_status": "Không hoạt động" if status_group == "Không hoạt động" else "Đã Tham Gia",
                "joined_date": mhkt_dt,
                "fanpage_name": "Fanpage Mô hình kiến trúc Song Anh",
                "fanpage_id": "100063928172930",
                "last_scanned": get_current_timestamp(),
                "notes": note_str or "Đồng bộ 100% từ Notion Database (Danh sách Group Facebook)"
            })
            fanpage_idx += 1
            
        if profile_st == "Đã tham gia" or steven_st == "Đã tham gia":
            profile_groups.append({
                "stt": profile_idx,
                "page_id": pid,
                "group_name": gname,
                "group_url": gurl,
                "group_id": gid,
                "members_count": mem_str or "N/A",
                "members_num": mem_num,
                "posting_permission": perm,
                "category": cat,
                "join_status": join_st,
                "joined_date": profile_dt,
                "profile_name": "Facebook Profile Song Anh",
                "last_scanned": get_current_timestamp(),
                "notes": note_str or "Đồng bộ 100% từ Notion Database (Danh sách Group Facebook)"
            })
            profile_idx += 1

    print(f"   ✅ Phân loại: {len(fanpage_groups)} Fanpage Groups | {len(profile_groups)} Profile Groups.", flush=True)

    # Tính điểm recommendation_score cho profile_groups
    def score_group(g):
        gname_l = (g.get("group_name") or "").lower()
        cat_l = (g.get("category") or "").lower()
        perm_l = (g.get("posting_permission") or "").lower()
        notes_l = (g.get("notes") or "").lower()
        st_l = (g.get("join_status") or "").lower()
        
        if "không hoạt động" in st_l or "ngừng hoạt động" in st_l or "lỗi" in st_l:
            return -2000.0
        if "du học sinh" in cat_l or "không phù hợp" in cat_l or "không phù hợp" in notes_l or "real estate for sale" in gname_l:
            return -2000.0
        if any(k in cat_l or k in notes_l or k in gname_l for k in ["thị trường ngoại", "mua bán bđs", "campuchia", "foreign", "phòng trọ", "xe/tàu", "anime", "gundam", "figure", "việc làm - hr"]):
            return -1000.0
        if perm_l == "không đăng được":
            return -1000.0
            
        score = 0.0
        if "công khai" in perm_l or "đăng ngay" in perm_l:
            score += 100.0
        elif "nhanh" in perm_l:
            score += 85.0
        elif "kiểm duyệt" in perm_l or "duyệt" in perm_l:
            score += 50.0
        
        if "thành công 100%" in notes_l or "posts/" in notes_l:
            score += 120.0
        
        if any(k in cat_l or k in gname_l for k in ["chủ đầu tư", "bql", "thi công", "nhà thầu", "kcn", "kho xưởng", "mô hình", "m&a"]):
            score += 60.0
        elif any(k in cat_l or k in gname_l for k in ["kiến trúc", "quy hoạch", "thiết kế", "nội thất", "xây dựng", "dự án", "căn hộ"]):
            score += 50.0
        
        mem = g.get("members_num") or 0
        if mem >= 100000:
            score += 30.0
        elif mem >= 10000:
            score += 20.0
        elif mem >= 1000:
            score += 10.0
        return score

    for g in profile_groups:
        g["recommendation_score"] = score_group(g)

    profile_groups.sort(key=lambda g: (g.get("recommendation_score", 0), g.get("members_num", 0)), reverse=True)
    for idx, g in enumerate(profile_groups, start=1):
        g["stt"] = idx

    top_5_recommended = [g for g in profile_groups if g.get("recommendation_score", 0) > 0][:5]
    print("=== TOP 5 GỢI Ý PROFILE GROUPS SAU CẬP NHẬT ===", flush=True)
    for t in top_5_recommended:
        print(f"  {t['stt']}. {t['group_name']} | Perm: {t['posting_permission']} | Score: {t['recommendation_score']} | Note: {t['notes'][:50]}", flush=True)

    # Lưu JSON và Excel
    timestamp = get_current_timestamp()
    profile_payload = {
        "status": "success",
        "profile_name": "Facebook Profile Song Anh",
        "scan_timestamp": timestamp,
        "joined_date": "2026-08-19",
        "total_joined_groups": len(profile_groups),
        "top_5_recommended_groups": top_5_recommended,
        "data": profile_groups
    }
    with open(PROFILE_JSON, "w", encoding="utf-8") as f:
        json.dump(profile_payload, f, ensure_ascii=False, indent=2)
    print(f"✅ Đã ghi {PROFILE_JSON}", flush=True)

    fanpage_payload = {
        "status": "success",
        "fanpage_name": "Fanpage Mô hình kiến trúc Song Anh",
        "fanpage_id": "100063928172930",
        "scan_timestamp": timestamp,
        "total_joined_groups": len(fanpage_groups),
        "data": fanpage_groups
    }
    with open(FANPAGE_JSON, "w", encoding="utf-8") as f:
        json.dump(fanpage_payload, f, ensure_ascii=False, indent=2)
    print(f"✅ Đã ghi {FANPAGE_JSON}", flush=True)

    # Xuất Excel
    df_profile = pd.DataFrame(profile_groups)
    df_profile.to_excel(PROFILE_XLSX, index=False, sheet_name="Profile Groups")
    print(f"✅ Đã ghi {PROFILE_XLSX}", flush=True)

    # Tải Post History từ Notion DB
    print("🔄 [2/5] Đang tải Lịch sử Đăng bài từ Notion DB...", flush=True)
    res_hist = requests.post(f"https://api.notion.com/v1/databases/{HISTORY_DB_ID}/query", headers=HEADERS, json={"page_size": 100})
    hist_pages = res_hist.json().get("results", [])
    history_records = []
    for h in hist_pages:
        hp = h.get("properties", {})
        h_title = "".join([t.get("plain_text", "") for t in hp.get("Tên Bài Đăng", {}).get("title", [])])
        h_acc = hp.get("Tài Khoản Đăng", {}).get("select", {}).get("name", "") if hp.get("Tài Khoản Đăng", {}).get("select") else ""
        h_date = hp.get("Ngày Đăng", {}).get("date", {}).get("start", "") if hp.get("Ngày Đăng", {}).get("date") else ""
        h_status = hp.get("Trạng Thái", {}).get("select", {}).get("name", "") if hp.get("Trạng Thái", {}).get("select") else ""
        h_link = hp.get("Link Bài Đăng Thực Tế", {}).get("url", "") or ""
        h_recmt_date = hp.get("Ngày Re-Comment Tiếp Theo", {}).get("date", {}).get("start", "") if hp.get("Ngày Re-Comment Tiếp Theo", {}).get("date") else ""
        h_recmt_count = hp.get("Lượt Re-Comment", {}).get("number") or 0
        
        rel_pages = hp.get("Group Facebook", {}).get("relation", [])
        rel_group_name = ""
        if rel_pages:
            rel_id = rel_pages[0].get("id")
            for g in profile_groups + fanpage_groups:
                if g.get("page_id") == rel_id:
                    rel_group_name = g.get("group_name")
                    break
        
        history_records.append({
            "page_id": h["id"],
            "post_title": h_title,
            "account": h_acc,
            "group_name": rel_group_name,
            "post_date": h_date,
            "status": h_status,
            "post_link": h_link,
            "next_recomment_date": h_recmt_date,
            "recomment_count": h_recmt_count
        })

    # Sắp xếp lịch sử bài đăng: mới nhất lên đầu
    history_records.sort(key=lambda x: (x.get("post_date", ""), x.get("post_title", "")), reverse=True)

    with open(HISTORY_JSON, "w", encoding="utf-8") as f:
        json.dump({"status": "success", "total": len(history_records), "data": history_records}, f, ensure_ascii=False, indent=2)
    print(f"✅ Đã lưu {HISTORY_JSON} ({len(history_records)} bản ghi)", flush=True)

    # Cập nhật marketing_data.json
    print("🔄 [3/5] Cập nhật marketing_data.json...", flush=True)
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        mdata = json.load(f)

    mdata["profile_joined_groups"] = profile_groups
    mdata["fanpage_joined_groups"] = fanpage_groups
    mdata["top_5_recommended_groups"] = top_5_recommended
    mdata["group_posts_history"] = history_records
    mdata["group_posts_history_stats"] = {
        "total_posts": len(history_records),
        "approved_posts": sum(1 for p in history_records if p.get("status") == "Đã đăng công khai"),
        "pending_posts": sum(1 for p in history_records if p.get("status") == "Đang chờ duyệt"),
        "need_recomment_posts": sum(1 for p in history_records if p.get("status") == "Cần Re-comment")
    }
    mdata["group_posts_history_sync_info"] = {
        "last_synced": timestamp,
        "database_id": HISTORY_DB_ID,
        "total_records": len(history_records),
        "status": "success"
    }

    # Đảm bảo marketing_activity_log có dòng mới nhất (ID 16)
    act_logs = mdata.get("marketing_activity_log", [])
    has_id_16 = any(l.get("id") == 16 for l in act_logs)
    if not has_id_16:
        act_logs.append({
            "id": 16,
            "timestamp": "21/08/2026 08:45:00",
            "module": "Facebook Marketing",
            "action": "Vận hành thực tế đăng bài Mô hình TOD 1/500 trên 5 Groups Facebook & đồng bộ kết quả duyệt bài",
            "executor": "Phạm Hoàng Tiến & Trợ lý Kiến",
            "status": "✅ Hoàn Thành"
        })
    act_logs.sort(key=lambda x: x.get("id", 0), reverse=True)
    mdata["marketing_activity_log"] = act_logs

    mdata["last_synced"] = timestamp
    mdata["notion_groups_sync_info"] = {
        "last_synced": timestamp,
        "database_id": GROUPS_DB_ID,
        "fanpage_count": len(fanpage_groups),
        "profile_count": len(profile_groups)
    }

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(mdata, f, ensure_ascii=False, indent=2)
    print(f"✅ Đã cập nhật toàn bộ vào {DATA_FILE}", flush=True)

    # Đồng bộ Google Drive nếu có
    print("🔄 [4/5] Đồng bộ sang Google Drive...", flush=True)
    if GDRIVE_DIR.exists():
        try:
            shutil.copy2(PROFILE_JSON, GDRIVE_DIR / PROFILE_JSON.name)
            shutil.copy2(PROFILE_XLSX, GDRIVE_DIR / PROFILE_XLSX.name)
            shutil.copy2(FANPAGE_JSON, GDRIVE_DIR / FANPAGE_JSON.name)
            shutil.copy2(HISTORY_JSON, GDRIVE_DIR / HISTORY_JSON.name)
            shutil.copy2(DATA_FILE, GDRIVE_DIR / DATA_FILE.name)
            print(f"✅ Đã đồng bộ sang Google Drive: {GDRIVE_DIR}", flush=True)
        except Exception as e:
            print(f"⚠️ Google drive copy warning: {e}", flush=True)
    else:
        print("ℹ️ Google Drive directory not mounted.", flush=True)

    print("🔄 [5/5] Hoàn tất toàn bộ chu trình đồng bộ!", flush=True)

if __name__ == "__main__":
    run_sync()
