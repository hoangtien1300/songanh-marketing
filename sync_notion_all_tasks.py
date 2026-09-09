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
                    channels_map[p["id"]] = t

    print(f"✅ Mappings nạp xong: {len(roles_map)} Vai trò - {len(cats_map)} Hạng mục - {len(channels_map)} Kênh.")

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

        formatted_tasks.append({
            "id": page_id,
            "title": title or "(Không có tiêu đề)",
            "status": status_name,
            "remind_date": remind_start,
            "remind_date_vn": remind_vn,
            "role_ids": role_ids,
            "role_names": role_names,
            "category_ids": cat_ids,
            "category_names": cat_names,
            "channel_ids": ch_ids,
            "channel_names": ch_names,
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

    def sort_key(t):
        r = t["remind_date"]
        has_remind = 0 if r else 1
        st_priority = 0 if t["status"] in ["Đang làm", "Duy trì"] else (1 if t["status"] == "Giao việc" else 2)
        return (has_remind, r if r else "9999", st_priority)

    formatted_tasks.sort(key=sort_key)

    filter_options = {
        "roles": sorted([{"id": k, "name": v} for k, v in roles_map.items()], key=lambda x: x["name"]),
        "categories": sorted([{"id": k, "name": v} for k, v in cats_map.items()], key=lambda x: x["name"]),
        "channels": sorted([{"id": k, "name": v} for k, v in channels_map.items()], key=lambda x: x["name"]),
        "statuses": sorted(list(status_set))
    }

    json_path = os.path.join(r"d:\Song_Anh\marketing_workflow_app", "marketing_data.json")
    with open(json_path, "r", encoding="utf-8") as f:
        mkt_data = json.load(f)

    mkt_data["songanh_tasks_db"] = formatted_tasks
    mkt_data["task_filter_options"] = filter_options
    mkt_data["songanh_tasks_total"] = len(formatted_tasks)
    mkt_data["tasks_last_synced"] = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(mkt_data, f, ensure_ascii=False, indent=2)

    print(f"🎉 ĐÃ ĐỒNG BỘ THÀNH CÔNG {len(formatted_tasks)} TASKS VÀO marketing_data.json!")
    print(f"   • Danh mục bộ lọc: {len(filter_options['roles'])} Vai trò - {len(filter_options['categories'])} Hạng mục - {len(filter_options['channels'])} Kênh")

if __name__ == "__main__":
    main()
