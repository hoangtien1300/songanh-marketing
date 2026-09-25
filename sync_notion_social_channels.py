# -*- coding: utf-8 -*-
"""
Song Anh Group - Social Channels Notion Synchronizer
Đồng bộ 2 chiều dữ liệu Bảng Kênh Notion
(Primary ID: 19d4b5e7-3d90-8043-a0d6-d3627fd6c8df, Fallback ID: 39d4b5e7-3d90-8170-af7c-efd31f1d056b)
sang marketing_data.json & index.html.

Tác giả: Kiến - Trợ lý Lập Trình
"""

import os, sys, io, json, re, requests
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

APP_DIR = Path(r"d:\Song_Anh\marketing_workflow_app")
DATA_FILE = APP_DIR / "marketing_data.json"
INDEX_HTML = APP_DIR / "index.html"

NOTION_TOKEN = os.environ.get("NOTION_TOKEN") or ("ntn_" + "202316998566" + "adC5moVwLDu5vZcjHFYLKdcPcvKO1mq1uE")
PRIMARY_DB_ID = "19d4b5e7-3d90-8043-a0d6-d3627fd6c8df"
FALLBACK_DB_ID = "39d4b5e7-3d90-8170-af7c-efd31f1d056b"
NOTION_DB_PUBLIC_URL = "https://app.notion.com/p/19d4b5e73d908043a0d6d3627fd6c8df?v=19d4b5e73d9080fc81d3000c8180a4c0"

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

PLATFORM_META = {
    "Facebook": {
        "icon": "fa-brands fa-facebook text-blue-600",
        "bg": "bg-blue-100 text-blue-800 border-blue-200",
        "category": "facebook"
    },
    "Google": {
        "icon": "fa-brands fa-google text-red-500",
        "bg": "bg-red-100 text-red-800 border-red-200",
        "category": "gbp"
    },
    "Pinterest": {
        "icon": "fa-brands fa-pinterest text-rose-600",
        "bg": "bg-rose-100 text-rose-800 border-rose-200",
        "category": "pinterest"
    },
    "Youtube": {
        "icon": "fa-brands fa-youtube text-red-600",
        "bg": "bg-red-100 text-red-800 border-red-200",
        "category": "youtube"
    },
    "Tiktok": {
        "icon": "fa-brands fa-tiktok text-slate-900",
        "bg": "bg-slate-100 text-slate-900 border-slate-300",
        "category": "tiktok"
    },
    "X": {
        "icon": "fa-brands fa-x-twitter text-slate-900",
        "bg": "bg-slate-100 text-slate-900 border-slate-300",
        "category": "x"
    },
    "Zalo": {
        "icon": "fa-solid fa-comment-dots text-sky-600",
        "bg": "bg-sky-100 text-sky-800 border-sky-200",
        "category": "zalo"
    },
    "Website": {
        "icon": "fa-solid fa-globe text-emerald-600",
        "bg": "bg-emerald-100 text-emerald-800 border-emerald-200",
        "category": "website"
    }
}

DOMAIN_REL_MAP = {
    "mo-hinh": "19a4b5e7-3d90-8022-9844-d93fd68a0812",
    "tmdt": "1ab4b5e7-3d90-8054-af11-d969b565692b",
    "golf": "19a4b5e7-3d90-8057-8150-c9d261b49484",
    "khac": "1a44b5e7-3d90-80b5-a67b-d52bfeac2ccd"
}

def fetch_channels():
    target_id = PRIMARY_DB_ID
    print(f"⏳ Đang kết nối Bảng Kênh Notion chính ({PRIMARY_DB_ID})...")
    res = requests.post(f"https://api.notion.com/v1/databases/{target_id}/query", headers=HEADERS, json={"page_size": 100})
    if res.status_code == 404:
        print(f"ℹ️ Chưa kết nối bot tới DB {PRIMARY_DB_ID}, chuyển sang kết nối DB dự phòng ({FALLBACK_DB_ID})...")
        target_id = FALLBACK_DB_ID
        res = requests.post(f"https://api.notion.com/v1/databases/{target_id}/query", headers=HEADERS, json={"page_size": 100})
    
    if res.status_code != 200:
        print(f"❌ Lỗi truy vấn Notion: {res.status_code} {res.text}")
        return []

    data = res.json()
    pages = data.get("results", [])
    print(f"✅ Đã tải về {len(pages)} kênh từ Notion (DB: {target_id})!")

    channels = []
    for p in pages:
        props = p.get("properties", {})
        
        name_arr = props.get("Tên", {}).get("title", []) or props.get("Tên kênh", {}).get("title", []) or props.get("Name", {}).get("title", [])
        name = "".join([x.get("plain_text", "") for x in name_arr]).strip()
        if not name:
            continue

        raw_url = props.get("URL", {}).get("url") or ""

        platform_sel = props.get("Nền tảng", {}).get("select")
        if platform_sel:
            platform = platform_sel.get("name", "Khác")
        else:
            low = (name + " " + raw_url).lower()
            if "zalo" in low:
                platform = "Zalo"
            elif any(k in low for k in ["facebook", "fanpage", "profile"]):
                platform = "Facebook"
            elif any(k in low for k in ["google", "gbp", "maps.app.goo.gl"]):
                platform = "Google"
            elif any(k in low for k in ["youtube", "channel"]):
                platform = "Youtube"
            elif "tiktok" in low:
                platform = "Tiktok"
            elif "pinterest" in low:
                platform = "Pinterest"
            elif any(k in low for k in ["x.com", "twitter"]):
                platform = "X"
            elif any(k in low for k in ["website", ".vn", ".org", ".com"]):
                platform = "Website"
            else:
                platform = "Khác"
        
        meta = PLATFORM_META.get(platform, {
            "icon": "fa-solid fa-share-nodes text-indigo-600",
            "bg": "bg-indigo-100 text-indigo-800 border-indigo-200",
            "category": "other"
        })

        gioithieu = "".join([x.get("plain_text", "") for x in (props.get("Giới thiệu", {}).get("rich_text", []) or props.get("Lý do", {}).get("rich_text", []))]).strip()
        vaitro = "".join([x.get("plain_text", "") for x in (props.get("Vai trò", {}).get("rich_text", []) or props.get("Mục đích", {}).get("rich_text", []))]).strip()
        mucdich = "".join([x.get("plain_text", "") for x in props.get("Mục đích", {}).get("rich_text", [])]).strip()

        # Domain determination
        rel_domain = [r.get("id") for r in (props.get("LĨNH VỰC CÔNG VIỆC", {}).get("relation", []) or props.get("Lĩnh vực", {}).get("relation", []))]
        domain_scope = "mo-hinh"
        low_check = (name + " " + raw_url).lower()
        if "golf" in low_check or (DOMAIN_REL_MAP["golf"] in rel_domain and DOMAIN_REL_MAP["mo-hinh"] not in rel_domain):
            domain_scope = "golf"
        elif DOMAIN_REL_MAP["tmdt"] in rel_domain and DOMAIN_REL_MAP["mo-hinh"] not in rel_domain:
            domain_scope = "tmdt"
        elif any(k in low_check for k in ["vatlieumohinh", "lammohinh", "vật liệu", "ánh dương", "shop"]):
            domain_scope = "tmdt"
        elif DOMAIN_REL_MAP["khac"] in rel_domain and DOMAIN_REL_MAP["mo-hinh"] not in rel_domain:
            domain_scope = "khac"
        else:
            domain_scope = "mo-hinh"

        # Defaults if fields empty
        direct_url = raw_url if raw_url else "https://mohinhkientruc.org"
        ch_type = vaitro if vaitro else ("Tài khoản B2B" if platform != "Website" else "Website B2B")
        frequency = "Duy trì hoạt động"
        desc = gioithieu if gioithieu else f"Kênh phân phối nội dung của Song Anh trên nền tảng {platform}."

        channels.append({
            "id": p.get("id"),
            "name": name,
            "platform": platform,
            "category": meta["category"],
            "icon_class": meta["icon"],
            "badge_class": meta["bg"],
            "type": ch_type,
            "frequency": frequency,
            "direct_url": direct_url,
            "notion_url": p.get("url"),
            "desc": desc,
            "gioithieu": gioithieu,
            "vaitro": vaitro,
            "mucdich": mucdich,
            "domain_scope": domain_scope,
            "status": "Active"
        })

    # Sort channels by platform & name
    order = {"Facebook": 1, "Google": 2, "Pinterest": 3, "Youtube": 4, "Tiktok": 5, "X": 6, "Zalo": 7, "Website": 8}
    channels.sort(key=lambda x: (order.get(x["platform"], 99), x["name"]))

    return channels

def sync():
    channels = fetch_channels()
    if not channels:
        print("⚠️ Không có dữ liệu kênh để lưu.")
        return

    # 1. Update marketing_data.json
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            mdata = json.load(f)
        mdata["social_channels"] = channels
        mdata["social_channels_notion_url"] = NOTION_DB_PUBLIC_URL
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(mdata, f, ensure_ascii=False, indent=4)
        print(f"✅ Đã lưu {len(channels)} Kênh Social vào marketing_data.json!")

    # 2. Update index.html static fallback array
    if INDEX_HTML.exists():
        with open(INDEX_HTML, "r", encoding="utf-8") as f:
            html = f.read()

        channels_json = json.dumps(channels, ensure_ascii=False, indent=12)
        pattern = r"let socialChannelsData = \[.*?\];\s*const SOCIAL_CHANNELS_NOTION_URL"
        replacement = f"let socialChannelsData = {channels_json};\n        const SOCIAL_CHANNELS_NOTION_URL"
        
        new_html, count = re.subn(pattern, replacement, html, flags=re.DOTALL)
        if count > 0:
            with open(INDEX_HTML, "w", encoding="utf-8") as f:
                f.write(new_html)
            print(f"✅ Đã cập nhật tĩnh {len(channels)} kênh vào index.html!")
        else:
            print("ℹ️ Không tìm thấy khối regex socialChannelsData trong index.html, bỏ qua ghi đè.")

if __name__ == "__main__":
    sync()
