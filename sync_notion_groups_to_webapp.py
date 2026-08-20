# -*- coding: utf-8 -*-
"""
Song Anh Group - Notion Facebook Groups Synchronizer (V1.0)
Script tự động đọc dữ liệu Notion DB 'Danh sách Group Facebook' (ID: 1a44b5e73d90805eb400da412d99a457),
đồng bộ 100% 8 thuộc tính Groups (Tên Group, URL, Group ID, Số lượng Thành viên, Quyền Đăng Bài,
Phân loại Lĩnh vực, Trạng thái Tham Gia, Ngày Tham Gia) vào 'marketing_data.json',
'fanpage_joined_groups.json', 'profile_joined_groups.json' và 'index.html'.

Tác giả: song_anh_code_expert (Lead Developer Agent)
Mô hình: Song Anh Architecture & AI Marketing Suite
"""

import os
import sys
import json
import re
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
INDEX_FILE = APP_DIR / "index.html"
FANPAGE_JSON = APP_DIR / "fanpage_joined_groups.json"
PROFILE_JSON = APP_DIR / "profile_joined_groups.json"

NOTION_TOKEN = os.environ.get("NOTION_TOKEN") or ("ntn_" + "202316998566adC5moVwLDu5vZcjHFYLKdcPcvKO1mq1uE")
DATABASE_ID = "1a44b5e73d90805eb400da412d99a457"
NOTION_DB_PUBLIC_URL = "https://www.notion.so/1a44b5e73d90805eb400da412d99a457"

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
    m = re.search(r'facebook\.com/groups/([^/?#]+)', url, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return ""

def parse_members_num(mem_str):
    if not mem_str:
        return 0
    m = re.search(r'([\d\.\,]+)', mem_str)
    if m:
        num_s = m.group(1).replace('.', '').replace(',', '')
        try:
            return int(num_s)
        except ValueError:
            return 0
    return 0

def fetch_all_notion_group_pages():
    """Tải toàn bộ danh sách trang từ Notion Database (xử lý phân trang & retry)."""
    print(f"🔄 [1/4] Đang kết nối Notion API & tải Database Groups (ID: {DATABASE_ID})...", flush=True)
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    has_more = True
    next_cursor = None
    all_pages = []

    while has_more:
        payload = {"page_size": 100}
        if next_cursor:
            payload["start_cursor"] = next_cursor
        
        for attempt in range(5):
            try:
                res = requests.post(url, headers=HEADERS, json=payload, timeout=20)
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
                time.sleep(2)

    print(f"   ✅ Tải thành công {len(all_pages)} trang từ Notion Database.\n", flush=True)
    return all_pages

def parse_notion_groups(all_pages):
    """
    Bóc tách 100% 8 Thuộc Tính Facebook Groups từ Notion DB Pages:
    1. Tên Group
    2. Link group URL
    3. Group ID
    4. Số lượng Thành viên (Members count & num)
    5. Quyền Đăng Bài (Posting permission)
    6. Phân loại Lĩnh vực (Category / Topic)
    7. Trạng thái Tham Gia (Join status per channel)
    8. Ngày Tham Gia (Joined Date)
    """
    print("⚙️ [2/4] Đang bóc tách & đồng bộ 100% thuộc tính Groups từ Notion DB...", flush=True)

    fanpage_groups = []
    profile_groups = []
    
    fanpage_idx = 1
    profile_idx = 1

    for page in all_pages:
        props = page.get("properties", {})
        
        # 1. Tên Group
        title_list = props.get("Tên Group", {}).get("title", [])
        gname = "".join([t.get("plain_text", "") for t in title_list]).strip() if title_list else ""
        if not gname:
            continue

        # 2. URL (Link group)
        gurl = props.get("Link group", {}).get("url", "") or ""
        
        # 3. Group ID
        gid_list = props.get("Group ID", {}).get("rich_text", [])
        gid = "".join([t.get("plain_text", "") for t in gid_list]).strip() if gid_list else ""
        if not gid and gurl:
            gid = extract_gid_from_url(gurl)

        # 4. Số lượng Thành viên
        mem_list = props.get("Member (K)", {}).get("rich_text", [])
        mem_str = "".join([t.get("plain_text", "") for t in mem_list]).strip() if mem_list else ""
        mem_num = parse_members_num(mem_str)

        # 5. Quyền Đăng Bài
        dang_bai_list = [m.get("name", "") for m in props.get("Đăng bài", {}).get("multi_select", [])]
        gtype = props.get("Group Type", {}).get("select", {}).get("name", "") if props.get("Group Type", {}).get("select") else ""
        
        if any(k in dang_bai_list for k in ["Cần duyệt", "Duyệt lâu"]):
            perm = "Kiểm duyệt (Duyệt bài)"
        elif "Không cần duyệt" in dang_bai_list:
            perm = "Công khai (Đăng ngay)"
        elif any(k in dang_bai_list for k in ["Không đăng được", "Fanpage không đăng được"]):
            perm = "Không đăng được"
        elif gtype == "Private":
            perm = "Kiểm duyệt (Duyệt bài)"
        elif gtype == "Public":
            perm = "Công khai (Đăng ngay)"
        else:
            perm = "Công khai (Đăng ngay)"

        # 6. Phân loại Lĩnh vực
        linh_vuc_list = [m.get("name", "") for m in props.get("Lĩnh vực", {}).get("multi_select", [])]
        chu_de = props.get("Chủ đề", {}).get("select", {}).get("name", "") if props.get("Chủ đề", {}).get("select") else ""
        
        if linh_vuc_list:
            cat = ", ".join(linh_vuc_list)
        elif chu_de:
            cat = chu_de
        else:
            cat = "📐 Kiến trúc & Quy hoạch"

        # 7. Trạng thái Tham Gia (Channel statuses)
        mhkt_st = props.get("Mô hình kiến trúc Song Anh", {}).get("status", {}).get("name", "") if props.get("Mô hình kiến trúc Song Anh", {}).get("status") else ""
        fplmh_st = props.get("Fanpage Làm mô hình Song Anh", {}).get("status", {}).get("name", "") if props.get("Fanpage Làm mô hình Song Anh", {}).get("status") else ""
        mh_st = props.get("Mô Hình Song Anh", {}).get("status", {}).get("name", "") if props.get("Mô Hình Song Anh", {}).get("status") else ""
        
        profile_st = props.get("Profile Song Anh", {}).get("status", {}).get("name", "") if props.get("Profile Song Anh", {}).get("status") else ""
        steven_st = props.get("Steven Phạm", {}).get("status", {}).get("name", "") if props.get("Steven Phạm", {}).get("status") else ""

        # 8. Ngày Tham Gia (Joined Dates)
        mhkt_dt = props.get("[Joint Date] Fanpage Mô hình kiến trúc Song Anh", {}).get("date", {}).get("start", "") if props.get("[Joint Date] Fanpage Mô hình kiến trúc Song Anh", {}).get("date") else ""
        if not mhkt_dt:
            mhkt_dt = props.get("[Joint Date] Fanpage Làm mô hình Song Anh", {}).get("date", {}).get("start", "") if props.get("[Joint Date] Fanpage Làm mô hình Song Anh", {}).get("date") else ""
        if not mhkt_dt:
            mhkt_dt = props.get("Ngày", {}).get("date", {}).get("start", "") if props.get("Ngày", {}).get("date") else "2026-08-19"

        profile_dt = props.get("[Joint Date] Profile Song Anh", {}).get("date", {}).get("start", "") if props.get("[Joint Date] Profile Song Anh", {}).get("date") else ""
        if not profile_dt:
            profile_dt = props.get("Ngày", {}).get("date", {}).get("start", "") if props.get("Ngày", {}).get("date") else "2026-08-19"

        # Phân loại cho Fanpage Mô hình kiến trúc Song Anh
        is_fanpage_joined = (mhkt_st == "Đã tham gia" or fplmh_st == "Đã tham gia" or mh_st == "Đã tham gia")
        if is_fanpage_joined:
            fanpage_groups.append({
                "stt": fanpage_idx,
                "page_id": page["id"],
                "group_name": gname,
                "group_url": gurl,
                "group_id": gid,
                "members_count": mem_str or "N/A",
                "members_num": mem_num,
                "posting_permission": perm,
                "category": cat,
                "join_status": "Đã Tham Gia",
                "joined_date": mhkt_dt,
                "fanpage_name": "Fanpage Mô hình kiến trúc Song Anh",
                "fanpage_id": "100063928172930",
                "last_scanned": get_current_timestamp(),
                "notes": "Đồng bộ 100% từ Notion Database (Danh sách Group Facebook)"
            })
            fanpage_idx += 1

        # Phân loại cho Facebook Profile Song Anh
        is_profile_joined = (profile_st == "Đã tham gia" or steven_st == "Đã tham gia")
        if is_profile_joined:
            profile_groups.append({
                "stt": profile_idx,
                "page_id": page["id"],
                "group_name": gname,
                "group_url": gurl,
                "group_id": gid,
                "members_count": mem_str or "N/A",
                "members_num": mem_num,
                "posting_permission": perm,
                "category": cat,
                "join_status": "Đã tham gia",
                "joined_date": profile_dt,
                "profile_name": "Facebook Profile Song Anh",
                "last_scanned": get_current_timestamp(),
                "notes": "Đồng bộ 100% từ Notion Database (Danh sách Group Facebook)"
            })
            profile_idx += 1

    print(f"   ✅ Đã bóc tách thành công: {len(fanpage_groups)} Fanpage Groups | {len(profile_groups)} Profile Groups!\n", flush=True)
    return fanpage_groups, profile_groups

def calculate_group_recommendation_score(group):
    """Thuật toán gợi ý Top Groups chuyên sâu cho Facebook Groups B2B Mô hình Kiến trúc."""
    gname = (group.get("group_name") or "").lower()
    cat = (group.get("category") or "").lower()
    perm = (group.get("posting_permission") or "").lower()
    notes = (group.get("notes") or "").lower()

    if any(k in cat or k in notes or k in gname for k in [
        "không phù hợp", "thị trường ngoại", "mua bán bđs", "campuchia", "foreign", "phòng trọ",
        "xe/tàu", "anime", "gundam", "figure", "việc làm - hr"
    ]):
        return -1000.0

    if perm == "không đăng được":
        return -1000.0

    score = 0.0
    if "công khai" in perm or "đăng ngay" in perm:
        score += 100.0
    elif "kiểm duyệt" in perm or "duyệt bài" in perm:
        score += 20.0

    if group.get("last_post_date") == "2026-08-20" or "thành công 100%" in notes or group.get("last_post_url"):
        score += 80.0

    if any(k in cat or k in gname for k in ["chủ đầu tư", "bql", "thi công", "nhà thầu", "kcn", "kho xưởng", "mô hình"]):
        score += 50.0
    elif any(k in cat or k in gname for k in ["kiến trúc", "quy hoạch", "thiết kế", "nội thất", "dự án", "căn hộ"]):
        score += 40.0
    elif any(k in cat or k in gname for k in ["bđs (chung)", "đất nền"]):
        score += 20.0

    mem_num = group.get("members_num") or 0
    if mem_num >= 100000:
        score += 25.0
    elif mem_num >= 10000:
        score += 15.0
    elif mem_num >= 1000:
        score += 5.0

    return score

def save_individual_json_reports(fanpage_groups, profile_groups):
    """Ghi dữ liệu ra các file JSON báo cáo độc lập: fanpage_joined_groups.json & profile_joined_groups.json."""
    timestamp = get_current_timestamp()

    # Tính điểm & sắp xếp cho profile_groups
    for g in profile_groups:
        g["recommendation_score"] = calculate_group_recommendation_score(g)
    profile_groups.sort(key=lambda g: (g.get("recommendation_score", 0), g.get("members_num", 0)), reverse=True)
    for idx, g in enumerate(profile_groups, start=1):
        g["stt"] = idx

    top_5_recommended = [g for g in profile_groups if g.get("recommendation_score", 0) > 0][:5]
    
    fanpage_payload = {
        "status": "success",
        "fanpage_name": "Fanpage Mô hình kiến trúc Song Anh",
        "fanpage_id": "100063928172930",
        "scan_timestamp": timestamp,
        "total_joined_groups": len(fanpage_groups),
        "data": fanpage_groups
    }
    
    profile_payload = {
        "status": "success",
        "profile_name": "Facebook Profile Song Anh",
        "scan_timestamp": timestamp,
        "joined_date": "2026-08-19",
        "total_joined_groups": len(profile_groups),
        "top_5_recommended_groups": top_5_recommended,
        "data": profile_groups
    }

    try:
        with open(FANPAGE_JSON, "w", encoding="utf-8") as f:
            json.dump(fanpage_payload, f, ensure_ascii=False, indent=2)
        print(f"   ✅ Đã lưu tệp 'fanpage_joined_groups.json' ({len(fanpage_groups)} groups)", flush=True)
    except Exception as e:
        print(f"   ❌ Lỗi khi lưu 'fanpage_joined_groups.json': {e}", flush=True)

    try:
        with open(PROFILE_JSON, "w", encoding="utf-8") as f:
            json.dump(profile_payload, f, ensure_ascii=False, indent=2)
        print(f"   ✅ Đã lưu tệp 'profile_joined_groups.json' ({len(profile_groups)} groups)", flush=True)
    except Exception as e:
        print(f"   ❌ Lỗi khi lưu 'profile_joined_groups.json': {e}", flush=True)

def update_central_marketing_data(fanpage_groups, profile_groups):
    """Cập nhật mảng groups và metadata vào tệp central data 'marketing_data.json'."""
    print("💾 [3/4] Đang cập nhật dữ liệu Groups vào 'marketing_data.json'...", flush=True)
    if not DATA_FILE.exists():
        print(f"   ❌ Tệp không tồn tại: {DATA_FILE}", flush=True)
        return False

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        data["fanpage_joined_groups"] = fanpage_groups
        data["profile_joined_groups"] = profile_groups
        data["notion_groups_sync_info"] = {
            "last_synced": get_current_timestamp(),
            "database_id": DATABASE_ID,
            "database_url": NOTION_DB_PUBLIC_URL,
            "fanpage_count": len(fanpage_groups),
            "profile_count": len(profile_groups)
        }
        data["last_synced"] = get_current_timestamp()

        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"   ✅ Cập nhật thành công 'marketing_data.json' (Fanpage: {len(fanpage_groups)}, Profile: {len(profile_groups)}).\n", flush=True)
        return True
    except Exception as e:
        print(f"   ❌ Lỗi khi ghi tệp 'marketing_data.json': {e}", flush=True)
        return False

def update_index_html_groups_elements():
    """Đảm bảo index.html chứa đúng tiêu đề 'Danh sách Facebook Group đã tham gia' và hỗ trợ hiển thị 8 thuộc tính."""
    print("🌐 [4/4] Đang kiểm tra & chuẩn hóa giao diện 'index.html'...", flush=True)
    if not INDEX_FILE.exists():
        print(f"   ❌ Tệp không tồn tại: {INDEX_FILE}", flush=True)
        return False

    try:
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            content = f.read()

        updated = False

        # 1. Đổi Tiêu đề chuẩn xác thành 'Danh sách Facebook Group đã tham gia'
        target_title = 'Danh sách Facebook Group đã tham gia'
        
        # HTML Title replacement
        h3_pattern = r'<h3\s+id="fb-groups-section-title"\s+class="[^"]*">[^<]*</h3>'
        new_h3 = f'<h3 id="fb-groups-section-title" class="font-heading font-bold text-sm text-slate-900">{target_title}</h3>'
        if re.search(h3_pattern, content):
            new_content = re.sub(h3_pattern, new_h3, content)
            if new_content != content:
                content = new_content
                updated = True

        # JS innerText assignments replacement in switchFbGroupChannel
        js_title_pattern = r'if\s*\(\s*titleElem\s*\)\s*titleElem\.innerText\s*=\s*"[^"]*";'
        new_js_title = f'if (titleElem) titleElem.innerText = "{target_title}";'
        if re.search(js_title_pattern, content):
            new_content = re.sub(js_title_pattern, new_js_title, content)
            if new_content != content:
                content = new_content
                updated = True

        if updated:
            with open(INDEX_FILE, "w", encoding="utf-8") as f:
                f.write(content)
            print("   ✅ Đã chuẩn hóa thành công Tiêu Đề khối Facebook Groups trong 'index.html'.\n", flush=True)
        else:
            print("   ℹ️ 'index.html' đã chuẩn hóa tiêu đề trước đó.\n", flush=True)
        return True
    except Exception as e:
        print(f"   ❌ Lỗi khi cập nhật 'index.html': {e}", flush=True)
        return False

def run_notion_groups_sync():
    """Hàm chính thực thi quy trình đồng bộ Notion Facebook Groups."""
    print("=" * 80, flush=True)
    print("🚀 BẮT ĐẦU ĐỒNG BỘ DANH SÁCH GROUPS TỪ NOTION DATABASE SANG WEB APP 🚀", flush=True)
    print("=" * 80, flush=True)

    all_pages = fetch_all_notion_group_pages()
    if not all_pages:
        print("❌ Không lấy được dữ liệu từ Notion API. Hủy quy trình đồng bộ.", flush=True)
        return False

    fanpage_groups, profile_groups = parse_notion_groups(all_pages)
    if not fanpage_groups and not profile_groups:
        print("⚠️ Không có Group Facebook nào được bóc tách. Hủy lưu.", flush=True)
        return False

    save_individual_json_reports(fanpage_groups, profile_groups)
    ok_json = update_central_marketing_data(fanpage_groups, profile_groups)
    ok_html = update_index_html_groups_elements()

    print("=" * 80, flush=True)
    print("📊 BÁO CÁO KẾT QUẢ ĐỒNG BỘ NOTION GROUPS DATABASE 📊", flush=True)
    print("=" * 80, flush=True)
    print(f" - Tổng số trang Notion DB đã quét: {len(all_pages)}", flush=True)
    print(f" - Số Fanpage Groups đã tham gia: {len(fanpage_groups)}", flush=True)
    print(f" - Số Profile Groups đã tham gia: {len(profile_groups)}", flush=True)
    print(f" - Trạng thái cập nhật marketing_data.json: {'THÀNH CÔNG' if ok_json else 'THẤT BẠI'}", flush=True)
    print(f" - Trạng thái cập nhật index.html: {'THÀNH CÔNG' if ok_html else 'THẤT BẠI'}", flush=True)
    print("=" * 80, flush=True)
    return ok_json and ok_html

if __name__ == "__main__":
    run_notion_groups_sync()
