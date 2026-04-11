import requests
import json
import os

# --- Cấu hình Notion ---
NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "YOUR_NOTION_TOKEN_HERE")
DATABASE_ID = "19a4b5e73d9080f4a51ef769967547a5"
OUTPUT_FILE = "notion_dashboard_data.json"

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def get_notion_data():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    try:
        response = requests.post(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        return data.get("results", [])
    except Exception as e:
        print(f"Lỗi khi kết nối Notion API: {e}")
        return []

def parse_notion_properties(properties):
    parsed_data = {}
    for prop_name, prop_data in properties.items():
        prop_type = prop_data.get("type")
        
        if prop_type == "title":
            title_list = prop_data.get("title", [])
            parsed_data[prop_name] = "".join([t.get("plain_text", "") for t in title_list])
        
        elif prop_type == "rich_text":
            text_list = prop_data.get("rich_text", [])
            parsed_data[prop_name] = "".join([t.get("plain_text", "") for t in text_list])
            
        elif prop_type == "number":
            parsed_data[prop_name] = prop_data.get("number")
            
        elif prop_type == "select":
            select_data = prop_data.get("select")
            parsed_data[prop_name] = select_data.get("name") if select_data else None
            
        elif prop_type == "multi_select":
            multi_select = prop_data.get("multi_select", [])
            parsed_data[prop_name] = [item.get("name") for item in multi_select]
            
        elif prop_type == "date":
            date_data = prop_data.get("date")
            parsed_data[prop_name] = date_data.get("start") if date_data else None
            
        elif prop_type == "checkbox":
            parsed_data[prop_name] = prop_data.get("checkbox")
            
        elif prop_type == "url":
            parsed_data[prop_name] = prop_data.get("url")
            
        elif prop_type == "email":
            parsed_data[prop_name] = prop_data.get("email")

        elif prop_type == "phone_number":
            parsed_data[prop_name] = prop_data.get("phone_number")

        # Mặc định nếu không xử lý được
        else:
            parsed_data[prop_name] = None
            
    return parsed_data

def main():
    print(f"Fetching data from Notion Database: {DATABASE_ID}...")
    results = get_notion_data()
    
    if not results:
        print("No data found or an error occurred.")
        return

    processed_results = []
    for page in results:
        properties = page.get("properties", {})
        processed_results.append(parse_notion_properties(properties))

    # Save results to JSON file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(processed_results, f, ensure_ascii=False, indent=4)
    
    print(f"Success! Saved {len(processed_results)} rows to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
