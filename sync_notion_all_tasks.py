import os
import sys
import json
import datetime
import requests

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import base64

NOTION_TOKEN = os.environ.get("NOTION_TOKEN") or base64.b64decode("bnRuXzIwMjMxNjk5ODU2NmFkQzVtb1Z3TER1NXZaY2pIRllMS2RjUGN2S08xbXExdUU=").decode("utf-8")
NOTION_VERSION = "2022-06-28"

TASKS_DB_ID = "19a4b5e7-3d90-80f4-a51e-f769967547a5"
ROLES_DB_ID = "19d4b5e7-3d90-80bd-a732-f9156aac8cfa"
CATEGORIES_DB_ID = "19d4b5e7-3d90-80f9-876e-fecc0a3ee587"
CHANNELS_DB_ID = "39d4b5e7-3d90-8170-af7c-efd31f1d056b"
LINHVUC_DB_ID = "19a4b5e7-3d90-8063-b01f-def67e4ea2cd"

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": NOTION_VERSION,
    "Content-Type": "application/json"
}

def query_all_pages(db_id):
    pages = []
    has_more = True
    cursor = None
    while has_more:
        body = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        res = requests.post(f"https://api.notion.com/v1/databases/{db_id}/query", headers=HEADERS, json=body)
        if not res.ok:
            print(f"Error querying DB {db_id}: {res.status_code} - {res.text}")
            break
        data = res.json()
        pages.extend(data.get("results", []))
        has_more = data.get("has_more", False)
        cursor = data.get("next_cursor")
    return pages

def extract_title(prop):
    if not prop:
        return ""
    ptype = prop.get("type")
    if ptype == "title":
        return "".join([t.get("plain_text", "") for t in prop.get("title", [])]).strip()
    return ""

def extract_rich_text(prop):
    if not prop:
        return ""
    ptype = prop.get("type")
    if ptype == "rich_text":
        return "".join([t.get("plain_text", "") for t in prop.get("rich_text", [])]).strip()
    return ""

def format_date_vn(date_str):
    if not date_str:
        return ""
    try:
        if "T" in date_str:
            part = date_str.split("T")[0]
            time_part = date_str.split("T")[1][:5]
            y, m, d = part.split("-")
            return f"{d}/{m}/{y} {time_part}"
        else:
            y, m, d = date_str.split("-")
            return f"{d}/{m}/{y}"
    except Exception:
        return date_str

def main():
    print("🚀 [BẮT ĐẦU] Đồng bộ BẢNG DANH SÁCH CÔNG VIỆC SONG ANH từ Notion...")
    
    print("⏳ Đang tải danh sách Vai trò...")
    role_pages = query_all_pages(ROLES_DB_ID)
    roles_map = {}
    for p in role_pages:
        for k, v in p["properties"].items():
            if v.get("type") == "title":
                t = extract_title(v)
                if t:
                    roles_map[p["id"]] = t

    print("⏳ Đang tải danh sách Hạng mục...")
    cat_pages = query_all_pages(CATEGORIES_DB_ID)
    cats_map = {}
    for p in cat_pages:
        for k, v in p["properties"].items():
            if v.get("type") == "title":
                t = extract_title(v)
                if t:
                    cats_map[p["id"]] = t

    print("⏳ Đang tải danh sách Kênh Social...")
    ch_pages = query_all_pages(CHANNELS_DB_ID)
    channels_map = {}
    for p in ch_pages:
        for k, v in p["properties"].items():
            if v.get("type") == "title":
                t = extract_title(v)
                if t:
                    channels_map[p["id"]] = " ".join(t.split())

    print("⏳ Đang tải danh sách Lĩnh vực...")
    linhvuc_pages = query_all_pages(LINHVUC_DB_ID)
    linhvuc_map = {}
    for p in linhvuc_pages:
        for k, v in p["properties"].items():
            if v.get("type") == "title":
                t = extract_title(v)
                if t:
                    linhvuc_map[p["id"]] = t

    print(f"✅ Mappings nạp xong: {len(roles_map)} Vai trò - {len(cats_map)} Hạng mục - {len(channels_map)} Kênh - {len(linhvuc_map)} Lĩnh vực.")

    print("⏳ Đang tải toàn bộ Tasks từ BẢNG DANH SÁCH CÔNG VIỆC...")
    task_pages = query_all_pages(TASKS_DB_ID)
    print(f"📊 Tổng số tasks lấy về từ Notion: {len(task_pages)}")

    formatted_tasks = []
    status_set = set()

    for p in task_pages:
        props = p["properties"]
        page_id = p["id"]
        
        title = extract_title(props.get("Tên công việc"))
        if not title:
            for k, v in props.items():
                if v.get("type") == "title":
                    title = extract_title(v)
                    break
        
        status_obj = props.get("Trạng thái", {}).get("status")
        status_name = status_obj.get("name", "Chưa lên lịch") if status_obj else "Chưa lên lịch"
        status_set.add(status_name)

        remind_date_obj = props.get("Nhắc hẹn", {}).get("date")
        remind_start = remind_date_obj.get("start", "") if remind_date_obj else ""
        remind_vn = format_date_vn(remind_start)

        role_ids = [r["id"] for r in props.get("Vai trò", {}).get("relation", [])]
        role_names = [roles_map.get(rid, rid) for rid in role_ids]

        cat_ids = [r["id"] for r in props.get("Hạng mục", {}).get("relation", [])]
        cat_names = [cats_map.get(cid, cid) for cid in cat_ids]

        ch_prop = props.get("Kênh Social") or props.get("Kênh")
        if not ch_prop:
            for k, v in props.items():
                if "kênh" in k.lower() or "kenh" in k.lower():
                    ch_prop = v
                    break
        ch_ids = [r["id"] for r in ch_prop.get("relation", [])] if ch_prop else []
        ch_names = [channels_map.get(chid, chid) for chid in ch_ids]

        lv_prop = props.get("Lĩnh vực") or props.get("Linh vuc")
        lv_ids = [r["id"] for r in lv_prop.get("relation", [])] if lv_prop else []
        lv_names = [linhvuc_map.get(lvid, lvid) for lvid in lv_ids]

        note = extract_rich_text(props.get("Ghi chú"))
        description = extract_rich_text(props.get("Mô tả công việc"))
        
        people_prop = props.get("Người theo", {}).get("people", [])
        performers = [p_user.get("name", "") for p_user in people_prop if p_user.get("name")]
        performer_str = ", ".join(performers) if performers else ""

        repeat_list = [item.get("name", "") for item in props.get("Lặp lại", {}).get("multi_select", [])]
        slot_list = [item.get("name", "") for item in props.get("Buổi", {}).get("multi_select", [])]

        done_count = props.get("Đã thực hiện", {}).get("number", 0) or 0
        kpi = props.get("KPI", {}).get("number", 0) or 0

        notion_url = p.get("url", f"https://notion.so/{page_id.replace('-', '')}")

        # Parent / Subtasks relations & % công việc
        parent_prop = props.get("mục gốc", {}).get("relation", [])
        parent_id = parent_prop[0]["id"] if parent_prop else None

        subtasks_prop = props.get("mục con", {}).get("relation", [])
        subtask_ids = [r["id"] for r in subtasks_prop]

        pct_prop = props.get("% công việc", {})
        percent_work = None
        if pct_prop.get("type") == "formula":
            percent_work = pct_prop.get("formula", {}).get("number")
        elif pct_prop.get("type") == "number":
            percent_work = pct_prop.get("number")

        formatted_tasks.append({
            "id": page_id,
            "title": title or "(Không có tiêu đề)",
            "status": status_name,
            "percent_work": percent_work,
            "remind_date": remind_start,
            "remind_date_vn": remind_vn,
            "field_ids": lv_ids,
            "field_names": lv_names,
            "linhvuc_ids": lv_ids,
            "linhvuc_names": lv_names,
            "role_ids": role_ids,
            "role_names": role_names,
            "category_ids": cat_ids,
            "category_names": cat_names,
            "channel_ids": ch_ids,
            "channel_names": ch_names,
            "parent_id": parent_id,
            "subtask_ids": subtask_ids,
            "note": note,
            "description": description,
            "performer": performer_str,
            "repeat": repeat_list,
            "slot": slot_list,
            "done_count": done_count,
            "kpi": kpi,
            "notion_url": notion_url,
            "created_time": p.get("created_time", ""),
            "last_edited_time": p.get("last_edited_time", "")
        })

    # =========================================================================
    # 🎯 LỌC BỎ CÁC TASK PHI MARKETING (CHỈ GIỮ LẠI MARKETING SUITE SONG ANH)
    # =========================================================================
    raw_task_map = {t["id"]: t for t in formatted_tasks}
    def get_root_task(t, t_map):
        curr = t
        visited = set()
        while curr.get("parent_id") and curr.get("parent_id") in t_map:
            if curr["id"] in visited:
                break
            visited.add(curr["id"])
            curr = t_map[curr["parent_id"]]
        return curr

    non_mkt_keywords = ['SALE - MÔ HÌNH', 'TRỢ LÝ', 'NHÂN SỰ', 'POTATO', 'POTATO ENGLISH']
    marketing_tasks = []
    for t in formatted_tasks:
        root = get_root_task(t, raw_task_map)
        root_title = (root.get("title") or "").strip().upper()
        task_title = (t.get("title") or "").strip().upper()
        roles = [r.strip().lower() for r in t.get("role_names", [])]
        is_non_mkt_root = any(k in root_title for k in non_mkt_keywords) or any(k in task_title for k in non_mkt_keywords)
        is_pure_non_mkt_role = bool(roles) and ("marketing" not in roles) and any(r in ['sale', 'nhân sự', 'nhan su', 'trợ lý', 'tro ly'] for r in roles)
        if not is_non_mkt_root and not is_pure_non_mkt_role:
            marketing_tasks.append(t)

    print(f"🎯 Đã lọc giữ lại {len(marketing_tasks)} Tasks Marketing Song Anh thuần túy (loại bỏ {len(formatted_tasks) - len(marketing_tasks)} tasks Sale/Nhân sự/Trợ lý/Potato English).")

    # QUY TẮC 15: TỔNG HỢP CHỈ SỐ KPI VÀ ĐÃ THỰC HIỆN TỪ TASK CON LÊN TASK CHA (Parent Task KPI Aggregation)
    tasks_by_id = {t["id"]: t for t in marketing_tasks}
    # Tìm liên kết cha-con theo child ID (hỗ trợ cả trường mục con và trường mục gốc)
    parent_to_children = {}
    for t in marketing_tasks:
        pid = t.get("parent_id")
        if pid:
            parent_to_children.setdefault(pid, {})[t["id"]] = t
        for sid in t.get("subtask_ids", []):
            if sid in tasks_by_id and sid != t["id"]:
                parent_to_children.setdefault(t["id"], {})[sid] = tasks_by_id[sid]

    # Cập nhật KPI & Done cho các Task Cha
    for pid, children_dict in parent_to_children.items():
        children = list(children_dict.values())
        if pid in tasks_by_id and children:
            parent_task = tasks_by_id[pid]
            total_child_kpi = sum(c.get("kpi", 0) or 0 for c in children)
            total_child_done = sum(c.get("done_count", 0) or 0 for c in children)
            if total_child_kpi > 0:
                parent_task["kpi"] = total_child_kpi
                parent_task["done_count"] = total_child_done
                parent_task["percent_work"] = round(total_child_done / total_child_kpi, 4)

    def sort_key(t):
        r = t["remind_date"]
        has_remind = 0 if r else 1
        st_priority = 0 if t["status"] in ["Đang làm", "Duy trì"] else (1 if t["status"] == "Giao việc" else 2)
        return (has_remind, r if r else "9999", st_priority)

    marketing_tasks.sort(key=sort_key)

    # Lọc lại roles/categories/channels chỉ thuộc marketing_tasks
    active_role_ids = set()
    active_cat_ids = set()
    active_ch_ids = set()
    active_lv_ids = set()
    active_statuses = set()
    for t in marketing_tasks:
        active_role_ids.update(t.get("role_ids", []))
        active_cat_ids.update(t.get("category_ids", []))
        active_ch_ids.update(t.get("channel_ids", []))
        active_lv_ids.update(t.get("field_ids", []))
        if t.get("status"):
            active_statuses.add(t["status"])

    # Đảm bảo cả 4 kênh Zalo chính thức của Song Anh luôn có mặt trong bộ lọc Kênh Marketing
    zalo_channel_ids = [
        "39d4b5e7-3d90-81ff-9360-f252aebbfc18",  # Zalo 0981 169 200
        "39d4b5e7-3d90-81fd-9671-cd411da3b218",  # Zalo 0376 41 51 31
        "39d4b5e7-3d90-8103-a730-fdcf1280acc3",  # Zalo 0386 989 087
        "39d4b5e7-3d90-8132-a289-c10337cc85a8"   # Zalo 0988 080 440
    ]
    for zid in zalo_channel_ids:
        if zid in channels_map:
            active_ch_ids.add(zid)

    filter_options = {
        "fields": sorted([{"id": k, "name": v} for k, v in linhvuc_map.items() if k in active_lv_ids], key=lambda x: x["name"]),
        "roles": sorted([{"id": k, "name": v} for k, v in roles_map.items() if k in active_role_ids and "marketing" in v.lower()], key=lambda x: x["name"]),
        "categories": sorted([{"id": k, "name": v} for k, v in cats_map.items() if k in active_cat_ids], key=lambda x: x["name"]),
        "channels": sorted([{"id": k, "name": v} for k, v in channels_map.items() if k in active_ch_ids], key=lambda x: x["name"]),
        "statuses": sorted(list(active_statuses))
    }

    json_path = os.path.join(r"d:\Song_Anh\marketing_workflow_app", "marketing_data.json")
    with open(json_path, "r", encoding="utf-8") as f:
        mkt_data = json.load(f)

    mkt_data["songanh_tasks_db"] = marketing_tasks
    mkt_data["task_filter_options"] = filter_options
    mkt_data["songanh_tasks_total"] = len(marketing_tasks)
    mkt_data["tasks_last_synced"] = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(mkt_data, f, ensure_ascii=False, indent=2)

    print(f"🎉 ĐÃ ĐỒNG BỘ THÀNH CÔNG {len(formatted_tasks)} TASKS VÀO marketing_data.json!")
    print(f"   • Danh mục bộ lọc: {len(filter_options['roles'])} Vai trò - {len(filter_options['categories'])} Hạng mục - {len(filter_options['channels'])} Kênh")

if __name__ == "__main__":
    main()
