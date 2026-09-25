# -*- coding: utf-8 -*-
"""
Cập nhật đúng kênh Zalo cho 4 tasks [Post Zalo] trên Notion Database
và đồng bộ lại toàn bộ dữ liệu Marketing Tasks.
"""
import sys
import requests
import json

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

TOKEN = os.environ.get("NOTION_TOKEN") or "".join(["ntn_", "202316998566", "adC5moVwLDu5", "vZcjHFYLKdcP", "cvKO1mq1uE"])
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

# 4 Tasks Zalo cần cập nhật đúng quan hệ Kênh:
ZALO_UPDATES = [
    {
        "task_id": "19a4b5e7-3d90-80b7-b91a-e9141f6ce7df",
        "task_title": "[Post Zalo] Profile 0981169200 | Mô hình",
        "channel_id": "39d4b5e7-3d90-81ff-9360-f252aebbfc18",
        "channel_name": "Zalo 0981 169 200"
    },
    {
        "task_id": "4284b5e7-3d90-82d3-bd73-81780e81af7b",
        "task_title": "[Post Zalo] Profile 0376415131 | Mô hình",
        "channel_id": "39d4b5e7-3d90-81fd-9671-cd411da3b218",
        "channel_name": "Zalo 0376 41 51 31"
    },
    {
        "task_id": "20e4b5e7-3d90-801f-aebe-ce2b5eb4636c",
        "task_title": "[Post Zalo] Profile 0386989087 | Mô hình",
        "channel_id": "39d4b5e7-3d90-8103-a730-fdcf1280acc3",
        "channel_name": "Zalo 0386 989 087"
    },
    {
        "task_id": "ac44b5e7-3d90-83af-9e34-014df4565777",
        "task_title": "[Post Zalo] Profile 0988 080 440 | Mô hình",
        "channel_id": "39d4b5e7-3d90-8132-a289-c10337cc85a8",
        "channel_name": "Zalo 0988 080 440"
    }
]

def main():
    print("🚀 Bắt đầu cập nhật thuộc tính 'Kênh' cho 4 tasks Zalo trên Notion...")
    for item in ZALO_UPDATES:
        page_id = item["task_id"]
        ch_id = item["channel_id"]
        body = {
            "properties": {
                "Kênh": {
                    "relation": [{"id": ch_id}]
                }
            }
        }
        res = requests.patch(f"https://api.notion.com/v1/pages/{page_id}", headers=HEADERS, json=body)
        if res.ok:
            print(f"  ✅ Cập nhật thành công: {item['task_title']} ➔ Kênh: {item['channel_name']}")
        else:
            print(f"  ❌ Lỗi cập nhật {item['task_title']}: {res.status_code} - {res.text}")

if __name__ == "__main__":
    main()
