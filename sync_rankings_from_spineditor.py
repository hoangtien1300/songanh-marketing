import sys
import io
import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import unicodedata

# Ensure UTF-8 output
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# --- CONFIGURATION ---
SPREADSHEET_ID = '1xXvpAlJkpxg7S6M49acRFSM7key8oXUSmOkRxg6nqlc'
WS_SOURCE = "Check từ khóa"
WS_MAIN = "Topical Map mohinhkientruc.org"

SCOPES = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]

def normalize_text(text):
    if not text: return ""
    return unicodedata.normalize('NFC', text.lower().strip())

def get_google_creds():
    # Try environment variable first (for Vercel/Production)
    google_auth_json = os.environ.get("GOOGLE_AUTH_JSON")
    if google_auth_json:
        try:
            return ServiceAccountCredentials.from_json_keyfile_dict(json.loads(google_auth_json), SCOPES)
        except Exception as e:
            print(f"Error parsing GOOGLE_AUTH_JSON: {e}")

    # Fallback to local file for desktop development
    key_file_local = r'd:\01 Song Anh\Report_marketing\gen-lang-client-0944295787-7c6a5ec1c046.json'
    if os.path.exists(key_file_local):
        return ServiceAccountCredentials.from_json_keyfile_name(key_file_local, SCOPES)
    
    print("ERROR: No Google credentials found (GOOGLE_AUTH_JSON or local file).")
    return None

def main():
    # 1. Authorize
    creds = get_google_creds()
    if not creds: return

    gc = gspread.authorize(creds)
    sh = gc.open_by_key(SPREADSHEET_ID)
    
    # 2. Read Source Data (Spineditor results)
    print(f"Reading rankings from '{WS_SOURCE}'...")
    ws_source = sh.worksheet(WS_SOURCE)
    source_values = ws_source.get_all_values()
    
    source_rankings = {} # keyword -> {"rank": X, "date": Y, "url": Z}
    if len(source_values) > 1:
        for row in source_values[1:]: # Skip header
            if len(row) >= 4:
                kw = normalize_text(row[0])
                rank = row[1].strip()
                date_val = row[2].strip()
                url = row[3].strip()
                if kw:
                    source_rankings[kw] = {"rank": rank, "date": date_val, "url": url}
    
    print(f"Collected {len(source_rankings)} keywords from source.")

    # 3. Handle Main Worksheet
    ws_main = sh.worksheet(WS_MAIN)
    main_values = ws_main.get_all_values()
    
    # Identify Header in main sheet
    header_idx = -1
    for i, row in enumerate(main_values):
        if "Danh sách từ khóa SEO" in row:
            header_idx = i
            break
            
    if header_idx == -1:
        print(f"ERROR: Could not find 'Danh sách từ khóa SEO' header in '{WS_MAIN}'.")
        return

    # 4. Process Keywords and Update Main Sheet (Batch)
    updates = []
    updated_count = 0
    
    # We use the same header_idx found before
    if header_idx == -1:
        print(f"ERROR: Could not find 'Danh sách từ khóa SEO' header in '{WS_MAIN}'.")
        return

    for i, row in enumerate(main_values[header_idx + 1:], start=header_idx + 2):
        if len(row) < 12: continue
        
        kw_cell = row[11].strip()
        if not kw_cell: continue
        
        # Split keywords if comma separated
        kws = [normalize_text(k) for k in kw_cell.split(',')]
        
        found = False
        target_rank = ""
        target_date = ""
        target_url = ""
        
        for kw in kws:
            # Match directly from our source_rankings
            if kw in source_rankings:
                found = True
                target_rank = source_rankings[kw]["rank"]
                target_date = source_rankings[kw]["date"]
                target_url = source_rankings[kw]["url"]
                break # Take the first match
            else:
                # Try partial match if exact fails
                for src_kw in source_rankings:
                    if (len(kw) > 5 and kw in src_kw) or (len(src_kw) > 5 and src_kw in kw):
                        found = True
                        target_rank = source_rankings[src_kw]["rank"]
                        target_date = source_rankings[src_kw]["date"]
                        target_url = source_rankings[src_kw]["url"]
                        break
                if found: break
        
        if found:
            cell_range = f"M{i}:O{i}"
            updates.append({
                'range': cell_range,
                'values': [[target_date, target_rank, target_url]]
            })
            updated_count += 1
            
    # 5. Execute Update
    if updates:
        print(f"Updating {len(updates)} rows in '{WS_MAIN}'...")
        ws_main.batch_update(updates)
        print("Success! Dashboard updated from Spineditor data.")
    else:
        print("No matches found in 'Check từ khóa' for the main dashboard.")

if __name__ == "__main__":
    main()
