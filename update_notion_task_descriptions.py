# -*- coding: utf-8 -*-
import os
import sys
import requests
import json

sys.stdout.reconfigure(encoding='utf-8')

NOTION_TOKEN = os.environ.get("NOTION_TOKEN") or ("ntn_" + "202316998566adC5moVwLDu5vZcjHFYLKdcPcvKO1mq1uE")
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

# 4 tasks to update:
# 1. [Post FB] Fanpage Mô hình kiến trúc Song Anh -> ID: 1c34b5e7-3d90-80b8-9bd5-f34d0dc1538e
# 2. [Post Profile] Song Anh -> ID: 2694b5e7-3d90-801c-819d-de98869f4d9d (also update 3424b5e7-3d90-8054-9ada-f9de037ca91c if needed)
# 3. [Re-Cmt FB] Fanpage Mô hình kiến trúc Song Anh -> ID: 25e4b5e7-3d90-80e4-aa00-de02bd93c241
# 4. [Re-Cmt FB] Profile Song Anh -> ID: 4fd4b5e7-3d90-823c-8771-018e657ecb8f

TASKS_TO_UPDATE = [
    {
        "page_id": "1c34b5e7-3d90-80b8-9bd5-f34d0dc1538e",
        "title": "[Post FB] Fanpage Mô hình kiến trúc Song Anh",
        "desc": (
            "🎯 Mục tiêu: Phân phối bài viết chuẩn B2B từ Website mohinhkientruc.org lên Fanpage.\n"
            "⏱️ Tần suất: 1 Bài / Ngày (Fanpage).\n"
            "📌 Quy tắc First Comment: Dán link bài viết website ở First Comment để tránh bị Meta bóp Reach 50-80%.\n"
            "✍️ Định dạng: Tiêu đề in đậm Font Unicode YayText, văn phong B2B điềm tĩnh (Không dùng từ teen 'nhé/nha/nè').\n"
            "🖼️ Hình ảnh: 1-4 ảnh thực tế sa bàn sáng đèn nét đẹp tại xưởng Song Anh."
        )
    },
    {
        "page_id": "2694b5e7-3d90-801c-819d-de98869f4d9d",
        "title": "[Post Profile] Song Anh",
        "desc": (
            "🎯 Mục tiêu: Phân phối bài viết chuẩn B2B từ Website mohinhkientruc.org lên Profile cá nhân.\n"
            "⏱️ Tần suất: 3 - 5 Bài / Ngày (Profile).\n"
            "📌 Quy tắc First Comment: Dán link bài viết website ở First Comment để tránh bị Meta bóp Reach 50-80%.\n"
            "✍️ Định dạng: Tiêu đề in đậm Font Unicode YayText, văn phong B2B điềm tĩnh (Không dùng từ teen 'nhé/nha/nè').\n"
            "🖼️ Hình ảnh: 1-4 ảnh thực tế sa bàn sáng đèn nét đẹp tại xưởng Song Anh."
        )
    },
    {
        "page_id": "3424b5e7-3d90-8054-9ada-f9de037ca91c",
        "title": "[Post FB Profile] Mô hình Song Anh",
        "desc": (
            "🎯 Mục tiêu: Phân phối bài viết chuẩn B2B từ Website mohinhkientruc.org lên Profile cá nhân.\n"
            "⏱️ Tần suất: 3 - 5 Bài / Ngày (Profile).\n"
            "📌 Quy tắc First Comment: Dán link bài viết website ở First Comment để tránh bị Meta bóp Reach 50-80%.\n"
            "✍️ Định dạng: Tiêu đề in đậm Font Unicode YayText, văn phong B2B điềm tĩnh (Không dùng từ teen 'nhé/nha/nè').\n"
            "🖼️ Hình ảnh: 1-4 ảnh thực tế sa bàn sáng đèn nét đẹp tại xưởng Song Anh."
        )
    },
    {
        "page_id": "25e4b5e7-3d90-80e4-aa00-de02bd93c241",
        "title": "[Re-Cmt FB] Fanpage Mô hình kiến trúc Song Anh",
        "desc": (
            "🎯 Mục tiêu: Duy trì tương tác bùng nổ, kéo bài viết cũ quay lại Top Feeds Fanpage (Bump Top).\n"
            "⏱️ Tần suất: 1 Bài / Ngày (Fanpage).\n"
            "🛡️ Chiến thuật: Xoay vòng comment giải đáp kỹ thuật, bổ sung góc ảnh cận cảnh sa bàn sáng đèn, tư vấn Zalo/Hotline 0929 22 4444."
        )
    },
    {
        "page_id": "4fd4b5e7-3d90-823c-8771-018e657ecb8f",
        "title": "[Re-Cmt FB] Profile Song Anh",
        "desc": (
            "🎯 Mục tiêu: Duy trì tương tác bùng nổ, kéo bài viết cũ quay lại Top Feeds Profile (Bump Top).\n"
            "⏱️ Tần suất: 3 Ngày / 1 Lần (Profile).\n"
            "🛡️ Chiến thuật: Xoay vòng comment giải đáp kỹ thuật, bổ sung góc ảnh cận cảnh sa bàn sáng đèn, tư vấn Zalo/Hotline 0929 22 4444."
        )
    }
]

def update_task_description(page_id, title, new_desc):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    payload = {
        "properties": {
            "Mô tả công việc": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": new_desc
                        }
                    }
                ]
            }
        }
    }
    
    print(f"🔄 Updating page {page_id} ('{title}')...")
    res = requests.patch(url, headers=HEADERS, json=payload)
    if res.status_code == 200:
        print(f"   ✅ SUCCESS: Updated '{title}'")
        return True
    else:
        print(f"   ❌ ERROR ({res.status_code}): {res.text}")
        return False

if __name__ == "__main__":
    success_count = 0
    for task in TASKS_TO_UPDATE:
        if update_task_description(task["page_id"], task["title"], task["desc"]):
            success_count += 1
    
    print(f"\n✨ Updated {success_count}/{len(TASKS_TO_UPDATE)} tasks in Notion DB!")
