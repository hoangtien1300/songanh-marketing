# -*- coding: utf-8 -*-
"""
Script Python Synchronizer: sync_notion_fb_tasks_to_webapp.py
Tự động đồng bộ Bảng Danh Sách Công Việc Facebook Marketing từ Notion Database sang Web App.
Lấy dữ liệu từ Notion DB ID: 19a4b5e7-3d90-80f4-a51e-f769967547a5
Cập nhật tệp central data 'marketing_data.json' và 'index.html'

Tác giả: song_anh_code_expert (Lead Developer Agent)
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

NOTION_TOKEN = os.environ.get("NOTION_TOKEN") or ("ntn_" + "202316998566adC5moVwLDu5vZcjHFYLKdcPcvKO1mq1uE")
DATABASE_ID = "19a4b5e7-3d90-80f4-a51e-f769967547a5"
FB_ROOT_TASK_ID = "25e4b5e7-3d90-8054-ac71-f9a6ef89e045"
NOTION_DB_PUBLIC_URL = "https://www.notion.so/19a4b5e73d9080f4a51ef769967547a5"

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

def get_current_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def fetch_all_notion_pages():
    """Tải toàn bộ danh sách trang từ Notion Database (xử lý phân trang & retry)."""
    print(f"🔄 [1/4] Đang kết nối Notion API & tải Bảng Công Việc (DB ID: {DATABASE_ID})...", flush=True)
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
                time.sleep(2)

    print(f"   ✅ Tải thành công {len(all_pages)} trang từ Notion Database.\n", flush=True)
    return all_pages

def filter_and_parse_fb_tasks(all_pages):
    """
    Bóc tách và chuyển đổi toàn bộ danh sách Task Facebook Marketing sang định dạng Web App.
    Trích xuất: Task Name, Người Phụ Trách, Duy Trì (Lặp Lại), KPI Tuần, Đã Thực Hiện, % Công Việc, Status Text, Color/Icon Class.
    """
    print("⚙️ [2/4] Đang phân tích và bóc tách các trường dữ liệu Facebook Marketing...", flush=True)
    
    # 1. Tìm danh sách tất cả các ID thuộc cây con (descendants) của task "Facebook Marketing"
    descendants = set()
    to_visit = [FB_ROOT_TASK_ID]
    while to_visit:
        curr_id = to_visit.pop(0)
        for page in all_pages:
            props = page.get("properties", {})
            muc_goc_list = [g.get("id") for g in props.get("mục gốc", {}).get("relation", [])]
            if curr_id in muc_goc_list and page["id"] not in descendants:
                descendants.add(page["id"])
                to_visit.append(page["id"])

    parsed_tasks = []
    task_idx = 1

    # Ưu tiên xếp các task chính lên đầu
    primary_task_keywords = ["[Post FB]", "[Re-Cmt FB]", "[Re-cmt FB]", "[Re-cmt FB Group]", "[Post Fanpage]", "[Post Profile]", "[Join FB Group]"]

    for page in all_pages:
        props = page.get("properties", {})
        
        # 1. Task Name & Mô tả công việc
        title_list = props.get("Tên công việc", {}).get("title", [])
        task_name = "".join([t.get("plain_text", "") for t in title_list]).strip() if title_list else ""
        
        desc_list = props.get("Mô tả công việc", {}).get("rich_text", []) if props.get("Mô tả công việc") else []
        raw_desc = "".join([t.get("plain_text", "") for t in desc_list]).strip() if desc_list else ""
        task_description = raw_desc.replace('\r\n', ' \\n ').replace('\n', ' \\n ') if raw_desc else ""

        
        if not task_name or task_name == "Facebook Marketing":
            continue

        # Kiểm tra xem task có thuộc Facebook Marketing hay không
        is_descendant = page["id"] in descendants
        is_pattern_match = any(kw.lower() in task_name.lower() for kw in ["[post fb]", "[re-cmt fb]", "[re-cmt fb group]", "[post fanpage]", "[join fb group]", "[clean data group fb]", "facebook profile", "fanpage", "fb task"])
        
        if not (is_descendant or is_pattern_match):
            continue

        # === QUY TẮC 1: Scoping Lĩnh Vực Tab 'MÔ HÌNH' (Giữ lại Mô hình kiến trúc & Sa bàn, loại bỏ Thương mại, TMĐT, Vật liệu mô hình, Golf, Tien RS) ===
        task_name_lower = task_name.lower()
        exclude_keywords = [
            "làm mô hình song anh",
            "vật liệu mô hình",
            "vatlieumohinh",
            "golf",
            "thương mại",
            "thương mai",
            "thuong mai",
            "tmđt",
            "tmdt",
            "tien rs",
            "tiến rs"
        ]
        if any(kw in task_name_lower for kw in exclude_keywords):
            continue

        # === QUY TẮC 2: Lọc Task Active & KPI > 0 trong Bảng Facebook Marketing ===
        # Ẩn/Loại bỏ tất cả các task có trạng thái 'Đã xong', 'Đã hủy' hoặc KPI = 0 khỏi bảng.
        notion_status = props.get("Trạng thái", {}).get("status", {}).get("name", "Duy trì")
        kpi_raw = props.get("KPI", {}).get("number")
        kpi_num = float(kpi_raw) if kpi_raw is not None else 0.0

        is_completed_or_cancelled = notion_status in ["Hoàn thành", "Đã xong", "Hủy", "Đã hủy"]
        is_paused = notion_status in ["Tạm hoãn"]
        is_active_status = notion_status in ["Đang làm", "Duy trì", "Giao việc", "Đang thực hiện", "In Progress", "Active"]

        if is_completed_or_cancelled:
            continue
        if is_paused and kpi_num <= 0:
            continue
        if not (is_active_status or kpi_num > 0):
            continue

        # 2. Người Phụ Trách & Role
        assignee = ""
        people = props.get("Người theo", {}).get("people", [])
        if people:
            names = [person.get("name", "").strip() for person in people if person.get("name")]
            assignee = ", ".join(names)
        
        if "Tiến Phạm Hoàng" in assignee or "Pham Hoang Tien" in assignee:
            assignee = "Phạm Hoàng Tiến"
        elif "Sang" in assignee:
            assignee = "Sang (Marketing Admin)"

        if not assignee:
            # Kiểm tra xem có người theo chưa có Acc hoặc Auto-bot hay không
            acc_rel = props.get("Người theo (chưa có Acc)", {}).get("relation", [])
            if acc_rel or "robot" in task_name.lower() or "auto" in task_name.lower():
                assignee = "Trợ Lý AI Song Anh"
            else:
                assignee = "Phạm Hoàng Tiến"

        # Determination of Assignee Role
        assignee_role = "user-tie"
        if any(bot_kw in assignee.lower() or bot_kw in task_name.lower() for bot_kw in ["ai", "robot", "bot", "trợ lý"]):
            assignee_role = "robot"
            if assignee == "Phạm Hoàng Tiến" and "robot" in task_name.lower():
                assignee = "Trợ Lý AI Song Anh"
        elif any(sup_kw in assignee.lower() for sup_kw in ["tư vấn", "cskh", "support"]):
            assignee_role = "headset"

        # 3. Duy Trì (Lặp Lại) / Frequency
        laps_list = [m.get("name") for m in props.get("Lặp lại", {}).get("multi_select", [])] if props.get("Lặp lại", {}).get("type") == "multi_select" else []
        if len(laps_list) >= 7:
            frequency = "Hàng Ngày"
        elif len(laps_list) > 0:
            frequency = ", ".join(laps_list)
        else:
            # Check Ghi chú or default
            ghi_chu = "".join([t.get("plain_text", "") for t in props.get("Ghi chú", {}).get("rich_text", [])]) if props.get("Ghi chú") else ""
            if "2 bài/ tuần" in ghi_chu.lower():
                frequency = "2 Lần / Tuần"
            elif "hàng ngày" in ghi_chu.lower():
                frequency = "Hàng Ngày"
            else:
                frequency = "Hàng Tuần (Duy trì)"

        # 4. Units determination
        unit = "Bài" if "post" in task_name.lower() else ("Group" if "group" in task_name.lower() else ("Lần" if "cmt" in task_name.lower() or "re-cmt" in task_name.lower() else "Task"))

        # 5. KPI Tuần & Đã Thực Hiện
        kpi_raw = props.get("KPI", {}).get("number")
        completed_raw = props.get("Đã thực hiện", {}).get("number")

        kpi_num = float(kpi_raw) if kpi_raw is not None else 0.0
        completed_num = float(completed_raw) if completed_raw is not None else 0.0

        if kpi_num > 0:
            kpi_weekly = f"{int(kpi_num)} {unit} / Tuần"
        else:
            kpi_weekly = "100% Phản Hồi" if "cmt" in task_name.lower() else "Duy Trì 100%"

        if completed_raw is not None:
            completed_str = f"{int(completed_num)} {unit}" if kpi_num > 0 else f"{int(completed_num)}"
        else:
            completed_str = f"{int(completed_num)} {unit}" if kpi_num > 0 else "0"

        # 6. % Công Việc (Progress percent)
        pct_formula = props.get("% công việc", {}).get("formula", {}).get("number")
        if pct_formula is not None:
            progress_percent = round(pct_formula * 100, 1) if pct_formula <= 1.0 else round(pct_formula, 1)
        elif kpi_num > 0:
            progress_percent = round((completed_num / kpi_num) * 100, 1)
        else:
            progress_percent = 100.0 if completed_num > 0 else 0.0

        if progress_percent > 100.0:
            progress_percent = 100.0

        # 7. Status Text & Color / Icon Class
        notion_status = props.get("Trạng thái", {}).get("status", {}).get("name", "Duy trì")
        
        if progress_percent >= 100.0 or notion_status == "Hoàn thành":
            status_text = "100% Hoàn Thành"
            color_class = "emerald"
        elif progress_percent >= 75.0:
            status_text = f"{progress_percent}% Đạt KPI"
            color_class = "blue"
        elif progress_percent >= 50.0:
            status_text = f"{progress_percent}% Đạt KPI"
            color_class = "purple"
        elif progress_percent > 0:
            status_text = f"{progress_percent}% Đạt KPI"
            color_class = "amber"
        else:
            status_text = f"{notion_status}"
            color_class = "amber"

        icon_color = "emerald-600" if color_class == "emerald" else ("blue-600" if color_class == "blue" else ("purple-600" if color_class == "purple" else "amber-500"))
        icon_class = f"fa-square-check text-{icon_color}"

        task_obj = {
            "id": task_idx,
            "task_name": task_name,
            "description": task_description,
            "assignee": assignee,
            "assignee_role": assignee_role,
            "frequency": frequency,
            "kpi_weekly": kpi_weekly,
            "completed": completed_str,
            "progress_percent": progress_percent,
            "status_text": status_text,
            "color_class": color_class,
            "icon_class": icon_class
        }
        parsed_tasks.append(task_obj)
        task_idx += 1

    # Sắp xếp để đưa các task chính (chứa [Post FB], [Re-Cmt FB]...) lên trên cùng
    def task_sort_key(t):
        tname = t["task_name"]
        for idx, kw in enumerate(primary_task_keywords):
            if kw.lower() in tname.lower():
                return (0, idx, tname)
        return (1, 0, tname)

    parsed_tasks.sort(key=task_sort_key)

    # Đánh lại ID theo thứ tự sau khi sắp xếp
    for i, t in enumerate(parsed_tasks, start=1):
        t["id"] = i

    print(f"   ✅ Đã bóc tách thành công {len(parsed_tasks)} Facebook Marketing Tasks!\n", flush=True)
    return parsed_tasks

def update_central_json(facebook_tasks):
    """Cập nhật mảng 'facebook_tasks' trong tệp central data 'marketing_data.json'."""
    print("💾 [3/4] Đang cập nhật mảng 'facebook_tasks' vào 'marketing_data.json'...", flush=True)
    if not DATA_FILE.exists():
        print(f"   ❌ Tệp không tồn tại: {DATA_FILE}", flush=True)
        return False

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        data["facebook_tasks"] = facebook_tasks
        data["last_synced"] = get_current_timestamp()

        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"   ✅ Cập nhật thành công 'marketing_data.json' ({len(facebook_tasks)} tasks, synced lúc {data['last_synced']}).\n", flush=True)
        return True
    except Exception as e:
        print(f"   ❌ Lỗi khi ghi tệp 'marketing_data.json': {e}", flush=True)
        return False

def update_index_html_embedded_tasks(facebook_tasks):
    """Cập nhật mảng 'let fbTaskList = [...]' nhúng trực tiếp trong 'index.html'."""
    print("🌐 [4/4] Đang đồng bộ mảng 'fbTaskList' nhúng trong 'index.html'...", flush=True)
    if not INDEX_FILE.exists():
        print(f"   ❌ Tệp không tồn tại: {INDEX_FILE}", flush=True)
        return False

    try:
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            content = f.read()

        formatted_js_array = "let fbTaskList = " + json.dumps(facebook_tasks, ensure_ascii=False, indent=12) + ";"
        
        # Regex replacement for `let fbTaskList = [...];`
        pattern = r"let\s+fbTaskList\s*=\s*\[[\s\S]*?\];"
        if re.search(pattern, content):
            new_content = re.sub(pattern, formatted_js_array, content, count=1)
            with open(INDEX_FILE, "w", encoding="utf-8") as f:
                f.write(new_content)
            print("   ✅ Đã cập nhật thành công mảng 'fbTaskList' trong 'index.html'.\n", flush=True)
            return True
        else:
            print("   ⚠️ Không tìm thấy biến 'let fbTaskList' trong 'index.html'!", flush=True)
            return False
    except Exception as e:
        print(f"   ❌ Lỗi khi cập nhật 'index.html': {e}", flush=True)
        return False

def run_notion_fb_tasks_sync():
    """Hàm chính để thực thi quy trình đồng bộ Notion FB Tasks."""
    print("=" * 80, flush=True)
    print("🚀 BẮT ĐẦU ĐỒNG BỘ TASK FACEBOOK MARKETING TỪ NOTION SANG WEB APP 🚀", flush=True)
    print("=" * 80, flush=True)
    
    all_pages = fetch_all_notion_pages()
    if not all_pages:
        print("❌ Không lấy được dữ liệu từ Notion API. Hủy quy trình đồng bộ.", flush=True)
        return False

    facebook_tasks = filter_and_parse_fb_tasks(all_pages)
    if not facebook_tasks:
        print("⚠️ Không có task Facebook Marketing nào được bóc tách. Hủy lưu.", flush=True)
        return False

    ok_json = update_central_json(facebook_tasks)
    ok_html = update_index_html_embedded_tasks(facebook_tasks)

    print("=" * 80, flush=True)
    print("📊 BÁO CÁO KẾT QUẢ ĐỒNG BỘ TASK FACEBOOK MARKETING NOTION 📊", flush=True)
    print("=" * 80, flush=True)
    print(f" - Tổng số Task FB bóc tách từ Notion: {len(facebook_tasks)}", flush=True)
    print(f" - Trạng thái cập nhật marketing_data.json: {'THÀNH CÔNG' if ok_json else 'THẤT BẠI'}", flush=True)
    print(f" - Trạng thái cập nhật index.html: {'THÀNH CÔNG' if ok_html else 'THẤT BẠI'}", flush=True)
    print("=" * 80, flush=True)
    return ok_json and ok_html

if __name__ == "__main__":
    run_notion_fb_tasks_sync()
