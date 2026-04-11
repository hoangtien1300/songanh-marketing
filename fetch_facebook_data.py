import requests
import json
import datetime
import os

# --- CONFIGURATION ---
# 1. Get your Page Access Token from https://developers.facebook.com/tools/explorer/
# 2. Find your Page ID (e.g., in Page Settings -> Page Info)
PAGE_ID = '1621988744780815'
ACCESS_TOKEN = os.environ.get("FB_ACCESS_TOKEN", "YOUR_FACEBOOK_ACCESS_TOKEN_HERE")

# Output file path
OUTPUT_FILE = 'facebook_dashboard_data.json'

# Metrics to fetch
METRICS = [
    'page_impressions',             # Lượt xem (Reach/Reach is impressions in some contexts)
    'page_engaged_users',           # Tương tác nội dung
    'page_views_total',             # Lượt truy cập trang
    'page_fan_adds',                # Lượt theo dõi mới
    'page_post_engagements'         # Tương tác chi tiết
]

def fetch_metric(metric_name, days_back=14):
    url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/insights"
    params = {
        'metric': metric_name,
        'period': 'day',
        'access_token': ACCESS_TOKEN,
        'since': (datetime.date.today() - datetime.timedelta(days=days_back)).isoformat(),
        'until': datetime.date.today().isoformat()
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        if 'error' in data:
            print(f"Error fetching {metric_name}: {data['error']['message']}")
            return []
        
        values = data['data'][0]['values'] if data['data'] else []
        return values
    except Exception as e:
        print(f"Exception fetching {metric_name}: {e}")
        return []

def calculate_trend(current, previous):
    if previous == 0:
        return '↑ 100%' if current > 0 else '--%'
    diff = ((current - previous) / previous) * 100
    arrow = '↑' if diff >= 0 else '↓'
    return f"{arrow} {abs(diff):.1f}%"

def run_sync():
    print(f"Fetching Facebook Insights for Page {PAGE_ID}...")
    
    # Check if config is set
    if PAGE_ID == 'YOUR_PAGE_ID_HERE' or ACCESS_TOKEN == 'YOUR_PAGE_ACCESS_TOKEN_HERE':
        print("WARNING: Please set your PAGE_ID and ACCESS_TOKEN in the script.")
        # Create a mock file for testing frontend if tokens are missing
        create_mock_data()
        return

    report_data = {
        'page_name': 'Mô hình kiến trúc Song Anh',
        'last_updated': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'sectors': {
            'mohinh': {
                'metrics': {},
                'posts': []
            }
        }
    }

    # Fetch daily metrics
    results = {}
    for m in METRICS:
        results[m] = fetch_metric(m)

    # Process metrics (last 7 days vs previous 7 days)
    # We assume 'results' has at least 14 days of data
    for m in METRICS:
        vals = [v['value'] for v in results[m]]
        if len(vals) >= 14:
            current_7d = sum(vals[-7:])
            prev_7d = sum(vals[-14:-7])
            trend = calculate_trend(current_7d, prev_7d)
        else:
            current_7d = sum(vals) if vals else 0
            trend = '--%'

        report_data['sectors']['mohinh']['metrics'][m] = {
            'total': current_7d,
            'trend': trend
        }

    # Optional: Fetch recent posts (last 3)
    posts_url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/published_posts"
    posts_params = {
        'fields': 'message,created_time,full_picture,insights.metric(post_impressions_unique,post_engagements)',
        'limit': 3,
        'access_token': ACCESS_TOKEN
    }
    try:
        posts_resp = requests.get(posts_url, params=posts_params).json()
        if 'data' in posts_resp:
            for p in posts_resp['data']:
                insights = p.get('insights', {}).get('data', [])
                reach = next((i['values'][0]['value'] for i in insights if i['name'] == 'post_impressions_unique'), 0)
                engagement = next((i['values'][0]['value'] for i in insights if i['name'] == 'post_engagements'), 0)
                
                report_data['sectors']['mohinh']['posts'].append({
                    'id': p['id'],
                    'message': p.get('message', ''),
                    'created_time': p['created_time'],
                    'picture': p.get('full_picture', ''),
                    'reach': reach,
                    'engagement': engagement
                })
    except Exception as e:
        print(f"Error fetching posts: {e}")

    # Save to JSON
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)
    
    print(f"Facebook data saved to {OUTPUT_FILE}")

def create_mock_data():
    mock_data = {
        'page_name': 'Mô hình kiến trúc Song Anh (DEMO)',
        'last_updated': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'sectors': {
            'mohinh': {
                'metrics': {
                    'page_impressions': {'total': 4520, 'trend': '↑ 12.5%'},
                    'page_engaged_users': {'total': 324, 'trend': '↑ 8.2%'},
                    'page_views_total': {'total': 512, 'trend': '↓ 3.1%'},
                    'page_post_clicks_by_type': {'total': 86, 'trend': '↑ 20.5%'},
                    'page_fan_adds': {'total': 15, 'trend': '↑ 50%'},
                    'page_post_engagements': {'total': 120, 'trend': '↑ 5.5%'}
                },
                'posts': [
                    {
                        'message': 'Mẫu sa bàn quy hoạch KCN tỉ lệ 1/2000 vừa hoàn thiện.',
                        'created_time': '2026-04-07T10:00:00+0000',
                        'reach': 1250,
                        'engagement': 45
                    },
                    {
                        'message': 'Cận cảnh chi tiết nội thất mô hình biệt thự cao cấp.',
                        'created_time': '2026-04-05T14:30:00+0000',
                        'reach': 840,
                        'engagement': 32
                    }
                ]
            }
        }
    }
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(mock_data, f, ensure_ascii=False, indent=2)
    print(f"Mock data created as {OUTPUT_FILE} for testing.")

if __name__ == '__main__':
    run_sync()
