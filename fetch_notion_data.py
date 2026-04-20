import requests
import json
import os
import sys
import io

# Ensure UTF-8 output for Windows
if sys.platform == "win32" and isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# --- Cấu hình Notion ---
NOTION_TOKEN = os.getenv("NOTION_API_TOKEN")

if not NOTION_TOKEN:
    print("WARNING: NOTION_API_TOKEN environment variable is not set.")
    # Fallback for local testing if needed, though NOT recommended
    # NOTION_TOKEN = "your_debug_token" 

DATABASES = {
    "dashboard": {
        "id": "19a4b5e73d9080f4a51ef769967547a5",
        "output": "notion_dashboard_data.json"
    },
    "facebook_posts": {
        "id": "25d4b5e73d9080ab83a8e2660e1e8e59",
        "output": "facebook_posts_data.json"
    }
}

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def get_notion_data(database_id):
    all_results = []
    next_cursor = None
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    
    while True:
        payload = {}
        if next_cursor:
            payload["start_cursor"] = next_cursor
            
        try:
            response = requests.post(url, headers=HEADERS, json=payload)
            response.raise_for_status()
            data = response.json()
            all_results.extend(data.get("results", []))
            
            next_cursor = data.get("next_cursor")
            if not next_cursor:
                break
            print(f"Fetched {len(all_results)} rows so far from {database_id}...")
        except Exception as e:
            print(f"Lỗi khi kết nối Notion API ({database_id}): {e}")
            break
            
    return all_results

def parse_notion_properties(properties):
    parsed_data = {}
    for prop_name, prop_data in properties.items():
        prop_type = prop_data.get("type")
        val = None
        
        if prop_type == "title":
            val = "".join([t.get("plain_text", "") for t in prop_data.get("title", [])])
        elif prop_type == "rich_text":
            val = "".join([t.get("plain_text", "") for t in prop_data.get("rich_text", [])])
        elif prop_type == "number":
            val = prop_data.get("number")
        elif prop_type == "select":
            select = prop_data.get("select")
            val = select.get("name") if select else None
        elif prop_type == "multi_select":
            val = [item.get("name") for item in prop_data.get("multi_select", [])]
        elif prop_type == "date":
            date_data = prop_data.get("date")
            val = date_data.get("start") if date_data else None
        elif prop_type == "checkbox":
            val = prop_data.get("checkbox")
        elif prop_type == "url":
            val = prop_data.get("url")
        elif prop_type == "status":
            status = prop_data.get("status")
            val = status.get("name") if status else None
        elif prop_type == "relation":
            val = [r.get("id") for r in prop_data.get("relation", [])]
        elif prop_type == "people":
            val = [p.get("name") for p in prop_data.get("people", []) if p.get("name")]
        elif prop_type == "rollup":
            rollup = prop_data.get("rollup", {})
            r_type = rollup.get("type")
            if r_type == "number":
                val = rollup.get("number")
            elif r_type == "array":
                val = rollup.get("array")
        elif prop_type == "formula":
            formula = prop_data.get("formula", {})
            f_type = formula.get("type")
            val = formula.get(f_type)

        parsed_data[prop_name] = val
    return parsed_data

def process_database(db_key):
    config = DATABASES[db_key]
    print(f"Processing {db_key} (ID: {config['id']})...")
    results = get_notion_data(config['id'])
    
    if not results:
        print(f"No data found for {db_key}")
        return

    processed_results = []
    for page in results:
        properties = page.get("properties", {})
        processed_data = parse_notion_properties(properties)
        processed_data["id"] = page.get("id")
        processed_results.append(processed_data)

    with open(config['output'], "w", encoding="utf-8") as f:
        json.dump(processed_results, f, ensure_ascii=False, indent=4)
    
    print(f"Success! Saved {len(processed_results)} rows to {config['output']}")

def main():
    for db_key in DATABASES:
        process_database(db_key)

if __name__ == "__main__":
    main()
