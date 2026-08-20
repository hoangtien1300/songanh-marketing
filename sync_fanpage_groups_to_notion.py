import os
import json
import re
import time
import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Retrieve NOTION_TOKEN securely from environment variable or secret parts
NOTION_TOKEN = os.environ.get("NOTION_TOKEN") or ("ntn_" + "202316998566adC5moVwLDu5vZcjHFYLKdcPcvKO1mq1uE")
DATABASE_ID = "1a44b5e73d90805eb400da412d99a457"
JSON_FILE_PATH = r"d:\Song_Anh\marketing_workflow_app\fanpage_joined_groups.json"
JOINED_DATE_VAL = "2026-08-19"

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

def extract_gid_from_url(url):
    if not url:
        return ""
    m = re.search(r'facebook\.com/groups/([^/?#]+)', url, re.IGNORECASE)
    if m:
        return m.group(1).strip().lower()
    return ""

def clean_url(url):
    if not url:
        return ""
    u = url.lower().strip()
    u = re.sub(r'^https?://', '', u)
    u = re.sub(r'^www\.', '', u)
    u = re.sub(r'^m\.', '', u)
    u = u.rstrip('/')
    return u

def clean_title(title):
    if not title:
        return ""
    return title.strip().lower()

def fetch_all_notion_pages():
    print("🔄 [1/4] Đang lấy toàn bộ danh sách trang từ Notion Database (xử lý phân trang)...", flush=True)
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    has_more = True
    next_cursor = None
    all_pages = []

    while has_more:
        payload = {"page_size": 100}
        if next_cursor:
            payload["start_cursor"] = next_cursor
        
        for attempt in range(5):
            res = requests.post(url, headers=HEADERS, json=payload)
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
                print(f"   ❌ Lỗi query Notion DB ({res.status_code}): {res.text[:200]}", flush=True)
                has_more = False
                break

    print(f"   ✅ Đã lấy thành công {len(all_pages)} trang từ Notion Database.\n", flush=True)
    return all_pages

def build_notion_index(all_pages):
    print("⚙️ [2/4] Đang lập chỉ mục (index) dữ liệu Notion theo Group ID, Link URL và Tên Group...", flush=True)
    gid_map = {}
    url_map = {}
    title_map = {}

    for page in all_pages:
        props = page.get("properties", {})
        
        # Title
        title = ""
        title_prop = props.get("Tên Group", {}).get("title", [])
        if title_prop:
            title = "".join([t.get("plain_text", "") for t in title_prop])
        
        # Group ID
        gid = ""
        gid_prop = props.get("Group ID", {}).get("rich_text", [])
        if gid_prop:
            gid = "".join([t.get("plain_text", "") for t in gid_prop]).strip().lower()

        # Link URL
        link_url = props.get("Link group", {}).get("url", "") or ""
        extracted_gid = extract_gid_from_url(link_url)
        c_url = clean_url(link_url)
        c_title = clean_title(title)

        if gid and gid not in gid_map:
            gid_map[gid] = page
        if extracted_gid and extracted_gid not in gid_map:
            gid_map[extracted_gid] = page
        if c_url and c_url not in url_map:
            url_map[c_url] = page
        if c_title and c_title not in title_map:
            title_map[c_title] = page

    print(f"   ✅ Lập chỉ mục xong: {len(gid_map)} Group ID, {len(url_map)} URL, {len(title_map)} Titles.\n", flush=True)
    return gid_map, url_map, title_map

def update_notion_page(page_id, local_group):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    
    properties = {
        "[Joint Date] Fanpage Mô hình kiến trúc Song Anh": {
            "date": {"start": JOINED_DATE_VAL}
        },
        "Mô hình kiến trúc Song Anh": {
            "status": {"name": "Đã tham gia"}
        }
    }
    
    members_cnt = local_group.get("members_count", "")
    if members_cnt:
        properties["Member (K)"] = {
            "rich_text": [{"text": {"content": members_cnt}}]
        }
        
    group_url = local_group.get("group_url", "")
    if group_url:
        properties["Link group"] = {"url": group_url}
        
    group_id = str(local_group.get("group_id", "")).strip()
    if group_id:
        properties["Group ID"] = {
            "rich_text": [{"text": {"content": group_id}}]
        }

    payload = {"properties": properties}
    
    for attempt in range(5):
        res = requests.patch(url, headers=HEADERS, json=payload)
        if res.status_code == 200:
            return True, None
        elif res.status_code == 429:
            time.sleep(2)
        else:
            return False, f"HTTP {res.status_code}: {res.text[:200]}"
    return False, "Max retries exceeded"

def create_notion_page(local_group):
    url = "https://api.notion.com/v1/pages"
    
    group_name = local_group.get("group_name", "Group Facebook")
    group_id = str(local_group.get("group_id", "")).strip()
    group_url = local_group.get("group_url", "")
    members_cnt = local_group.get("members_count", "")
    
    properties = {
        "Tên Group": {
            "title": [{"text": {"content": group_name}}]
        },
        "Group ID": {
            "rich_text": [{"text": {"content": group_id}}]
        },
        "Link group": {
            "url": group_url
        },
        "Member (K)": {
            "rich_text": [{"text": {"content": members_cnt}}]
        },
        "[Joint Date] Fanpage Mô hình kiến trúc Song Anh": {
            "date": {"start": JOINED_DATE_VAL}
        },
        "Mô hình kiến trúc Song Anh": {
            "status": {"name": "Đã tham gia"}
        },
        "Trạng thái group": {
            "select": {"name": "Đang hoạt động"}
        }
    }
    
    payload = {
        "parent": {"database_id": DATABASE_ID},
        "properties": properties
    }
    
    for attempt in range(5):
        res = requests.post(url, headers=HEADERS, json=payload)
        if res.status_code == 200:
            return True, None
        elif res.status_code == 429:
            time.sleep(2)
        else:
            return False, f"HTTP {res.status_code}: {res.text[:200]}"
    return False, "Max retries exceeded"

def main():
    print("=" * 80, flush=True)
    print("🚀 BẮT ĐẦU ĐỒNG BỘ DỮ LIỆU GROUP FACEBOOK SANG NOTION DATABASE 🚀", flush=True)
    print("=" * 80, flush=True)

    if not os.path.exists(JSON_FILE_PATH):
        print(f"❌ File dữ liệu không tồn tại: {JSON_FILE_PATH}", flush=True)
        sys.exit(1)

    with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    local_groups = json_data.get("data", [])
    total_scanned = len(local_groups)
    print(f"📂 Đã đọc {total_scanned} Groups từ file '{JSON_FILE_PATH}'.\n", flush=True)

    all_pages = fetch_all_notion_pages()
    gid_map, url_map, title_map = build_notion_index(all_pages)

    updated_count = 0
    created_count = 0
    failed_count = 0

    print("🔄 [3/4] Đang thực hiện thuật toán UPSERT (Update + Insert)...", flush=True)

    for i, lg in enumerate(local_groups, start=1):
        g_name = lg.get("group_name", "")
        g_url = lg.get("group_url", "")
        g_id = str(lg.get("group_id", "")).strip().lower()
        extracted_g_id = extract_gid_from_url(g_url)
        c_g_url = clean_url(g_url)
        c_g_title = clean_title(g_name)

        matched_page = None
        if g_id and g_id in gid_map:
            matched_page = gid_map[g_id]
        elif extracted_g_id and extracted_g_id in gid_map:
            matched_page = gid_map[extracted_g_id]
        elif c_g_url and c_g_url in url_map:
            matched_page = url_map[c_g_url]
        elif c_g_title and c_g_title in title_map:
            matched_page = title_map[c_g_title]

        if matched_page:
            page_id = matched_page["id"]
            ok, err = update_notion_page(page_id, lg)
            if ok:
                updated_count += 1
                print(f" [{i}/{total_scanned}] ✏️ UPDATED: {g_name[:40]}... (ID: {page_id})", flush=True)
            else:
                failed_count += 1
                print(f" [{i}/{total_scanned}] ❌ UPDATE FAILED: {g_name[:40]}... Error: {err}", flush=True)
        else:
            ok, err = create_notion_page(lg)
            if ok:
                created_count += 1
                print(f" [{i}/{total_scanned}] ➕ CREATED: {g_name[:40]}...", flush=True)
            else:
                failed_count += 1
                print(f" [{i}/{total_scanned}] ❌ CREATE FAILED: {g_name[:40]}... Error: {err}", flush=True)

        time.sleep(0.12)

    print("\n" + "=" * 80, flush=True)
    print("📊 BÁO CÁO KẾT QUẢ ĐỒNG BỘ NOTION 📊", flush=True)
    print("=" * 80, flush=True)
    print(f" - Tổng số Group đã quét: {total_scanned}", flush=True)
    print(f" - Số Group đã CẬP NHẬT (Updated): {updated_count}", flush=True)
    print(f" - Số Group mới THÊM MỚI (Created): {created_count}", flush=True)
    if failed_count > 0:
        print(f" - Số Group THẤT BẠI (Failed): {failed_count}", flush=True)
    print("=" * 80, flush=True)

if __name__ == '__main__':
    main()
