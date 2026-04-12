import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from http.server import BaseHTTPRequestHandler

# --- CONFIG ---
SPREADSHEET_ID = '1H4qEawa_At2v4UEILP8nxjkYoC4itB9QQlI5yckdkLQ'
TABS = [
    'GSC - mohinhkientruc.org', 
    'GSC - architecturalmodel.org',
    'GSC - mohinhsonganh.com',
    'GSC - lammohinh.vn',
    'Report'
]

def get_creds():
    # Priority 1: Environment Variable (Vercel)
    creds_json = os.environ.get('SERVICE_ACCOUNT_JSON')
    if creds_json:
        info = json.loads(creds_json)
        return service_account.Credentials.from_service_account_info(info)
    
    # Priority 2: Local File (Development)
    local_key = 'gen-lang-client-0944295787-7c6a5ec1c046.json'
    if os.path.exists(local_key):
        return service_account.Credentials.from_service_account_file(local_key)
    
    return None

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            creds = get_creds()
            if not creds:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b"Error: SERVICE_ACCOUNT_JSON environment variable not set.")
                return

            scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']
            creds = creds.with_scopes(scopes)
            service = build('sheets', 'v4', credentials=creds)

            all_data = {}
            for tab in TABS:
                try:
                    # Read columns A to F (Date, Domain, Clicks, Impressions, CTR, Position)
                    result = service.spreadsheets().values().get(
                        spreadsheetId=SPREADSHEET_ID, range=f"'{tab}'!A2:F").execute()
                    values = result.get('values', [])
                    
                    # Transform to object list
                    rows = []
                    for v in values:
                        if len(v) >= 6:
                            rows.append({
                                'date': v[0],
                                'domain': v[1],
                                'clicks': v[2],
                                'impressions': v[3],
                                'ctr': v[4],
                                'position': v[5]
                            })
                    all_data[tab] = rows
                except Exception as tab_err:
                    print(f"Error fetching tab {tab}: {tab_err}")
                    all_data[tab] = [] # Return empty list for missing tabs

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*') # Allow local dev
            self.end_headers()
            self.wfile.write(json.dumps(all_data).encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Error: {str(e)}".encode('utf-8'))
