import datetime
import sys
import os
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Ensure UTF-8 output for Windows terminal
if sys.platform == "win32" and isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# --- CONFIGURATION ---
KEY_FILE = 'gen-lang-client-0944295787-7c6a5ec1c046.json'
SPREADSHEET_ID = '1H4qEawa_At2v4UEILP8nxjkYoC4itB9QQlI5yckdkLQ'

# Mapping of site URL to Sheet Tab name
CONFIG = {
    'https://mohinhkientruc.org/': {
        'tab': 'GSC - mohinhkientruc.org',
        'domain': 'mohinhkientruc.org'
    },
    'https://architecturalmodel.org/': {
        'tab': 'GSC - architecturalmodel.org',
        'domain': 'architecturalmodel.org'
    }
}

SCOPES = [
    'https://www.googleapis.com/auth/webmasters.readonly',
    'https://www.googleapis.com/auth/spreadsheets'
]

def get_services():
    if not os.path.exists(KEY_FILE):
        raise FileNotFoundError(f"Key file {KEY_FILE} not found.")
    
    credentials = service_account.Credentials.from_service_account_file(KEY_FILE, scopes=SCOPES)
    gsc_service = build('searchconsole', 'v1', credentials=credentials)
    sheets_service = build('sheets', 'v4', credentials=credentials)
    return gsc_service, sheets_service

def get_last_date(sheets_service, tab_name):
    """Finds the last date in Column A of the specified tab."""
    try:
        range_name = f"'{tab_name}'!A2:A"
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID, range=range_name).execute()
        values = result.get('values', [])
        
        if not values:
            return None
        
        last_date_str = values[-1][0]
        # Format DD/MM/YYYY
        return datetime.datetime.strptime(last_date_str, "%d/%m/%Y").date()
    except Exception as e:
        print(f"Warning: Could not get last date for {tab_name}: {e}")
        return None

def fetch_gsc_data(gsc_service, site_url, start_date, end_date):
    """Fetches daily performance data from GSC."""
    request = {
        'startDate': start_date.isoformat(),
        'endDate': end_date.isoformat(),
        'dimensions': ['date'],
        'rowLimit': 1000
    }
    try:
        response = gsc_service.searchanalytics().query(siteUrl=site_url, body=request).execute()
        rows = response.get('rows', [])
        # Sort by date
        rows.sort(key=lambda x: x['keys'][0])
        return rows
    except Exception as e:
        print(f"Error fetching GSC data for {site_url}: {e}")
        return []

def run_update():
    print(f"--- Starting GSC to Google Sheets Sync - {datetime.datetime.now()} ---")
    gsc_service, sheets_service = get_services()
    
    # Yesterday is the target end date
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    
    for site_url, info in CONFIG.items():
        tab_name = info['tab']
        domain = info['domain']
        
        print(f"\nProcessing {domain}...")
        
        last_date = get_last_date(sheets_service, tab_name)
        if last_date:
            if last_date >= yesterday:
                print(f"Dữ liệu đã mới nhất cho {domain} (Ngày cuối: {last_date.strftime('%d/%m/%Y')})")
                continue
            start_date = last_date + datetime.timedelta(days=1)
        else:
            # If no data, start from 30 days ago as a default
            start_date = yesterday - datetime.timedelta(days=30)
            print(f"No existing data found for {domain}. Starting from default: {start_date}")

        print(f"Fetching data from {start_date} to {yesterday}...")
        rows = fetch_gsc_data(gsc_service, site_url, start_date, yesterday)
        
        if not rows:
            print(f"No new GSC data available for {domain} in the requested period.")
            continue
            
        # Format rows for Sheets
        # Columns: A-Date, B-Website, C-Clicks, D-Impressions, E-CTR, F-Position
        data_to_append = []
        actual_start = rows[0]['keys'][0]
        actual_end = rows[-1]['keys'][0]
        
        for r in rows:
            gsc_date = datetime.datetime.strptime(r['keys'][0], "%Y-%m-%d").strftime("%d/%m/%Y")
            ctr_percent = r['ctr'] # CTR is usually decimal (0.01 = 1%)
            row = [
                gsc_date,
                domain,
                int(r['clicks']),
                int(r['impressions']),
                f"{ctr_percent*100:.2f}%",
                round(r['position'], 1)
            ]
            data_to_append.append(row)
            
        # Append to Sheets
        try:
            body = {'values': data_to_append}
            sheets_service.spreadsheets().values().append(
                spreadsheetId=SPREADSHEET_ID,
                range=f"'{tab_name}'!A1", # Append logic handles finding bottom
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            
            # Final required response format
            print(f"Đã cập nhật xong dữ liệu tổng quan cho {domain} từ ngày {actual_start} đến ngày {actual_end}. Tổng số dòng đã thêm: {len(data_to_append)}.")
        except Exception as e:
            print(f"Error appending data to Google Sheets for {domain}: {e}")

def update_weekly_report(sheets_service):
    """Aggregates all daily GSC data in the spreadsheet into weekly summaries in a 'Report' tab."""
    print("\n--- Generating Weekly Aggregate Report ---")
    
    # 1. Ensure 'Report' tab exists
    try:
        ss = sheets_service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
        sheets = [s['properties']['title'] for s in ss.get('sheets', [])]
        if 'Report' not in sheets:
            sheets_service.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID, body={
                'requests': [{'addSheet': {'properties': {'title': 'Report'}}}]
            }).execute()
            # Add Headers
            headers = [['Week', 'Website', 'Tổng Nhấp chuột', 'Tổng Hiển thị', 'CTR Trung bình', 'Vị trí TB']]
            sheets_service.spreadsheets().values().update(
                spreadsheetId=SPREADSHEET_ID, range="'Report'!A1", 
                valueInputOption='USER_ENTERED', body={'values': headers}
            ).execute()
            print("Created new 'Report' tab.")
    except Exception as e:
        print(f"Error initializing Report tab: {e}")
        return

    # 2. Extract and Aggregate Data
    # Keys will be (Year, WeekNumber, Domain) -> {clicks, impressions, ctr_sum, pos_sum, count}
    weekly_data = {}
    
    for _, info in CONFIG.items():
        tab = info['tab']
        domain = info['domain']
        try:
            result = sheets_service.spreadsheets().values().get(
                spreadsheetId=SPREADSHEET_ID, range=f"'{tab}'!A2:F").execute()
            values = result.get('values', [])
            
            for v in values:
                if len(v) < 6: continue
                try:
                    date_obj = datetime.datetime.strptime(v[0], "%d/%m/%Y").date()
                    # ISO Week: returns (year, week_num, weekday)
                    iso_cal = date_obj.isocalendar()
                    key = (iso_cal[0], iso_cal[1], domain)
                    
                    if key not in weekly_data:
                        weekly_data[key] = {'clicks': 0, 'impressions': 0, 'ctr_sum': 0.0, 'pos_sum': 0.0, 'count': 0}
                    
                    # Clean numeric data
                    clicks = int(v[2])
                    impressions = int(v[3])
                    ctr = float(v[4].replace('%', ''))
                    pos = float(str(v[5]).replace(',', '.'))
                    
                    weekly_data[key]['clicks'] += clicks
                    weekly_data[key]['impressions'] += impressions
                    weekly_data[key]['ctr_sum'] += ctr
                    weekly_data[key]['pos_sum'] += pos
                    weekly_data[key]['count'] += 1
                except: continue
        except: continue

    if not weekly_data:
        print("No data found to aggregate.")
        return

    # 3. Prepare Report Rows
    report_rows = []
    # Sort by year desc, week desc to keep latest at top if we were overriding, but requested format usually appends
    sorted_keys = sorted(weekly_data.keys(), key=lambda x: (x[0], x[1]))
    for key in sorted_keys:
        year, week, domain = key
        stats = weekly_data[key]
        
        # V12: Generate date range label (e.g., 06/04 - 12/04)
        monday = datetime.date.fromisocalendar(year, week, 1)
        sunday = monday + datetime.timedelta(days=6)
        week_label = f"{monday.strftime('%d/%m')} - {sunday.strftime('%d/%m')}"
        
        row = [
            week_label,
            domain,
            stats['clicks'],
            stats['impressions'],
            f"{(stats['ctr_sum'] / stats['count']):.2f}%",
            round(stats['pos_sum'] / stats['count'], 1)
        ]
        report_rows.append(row)

    # 4. Overwrite/Update logic for Report tab (Simplest is to overwrite A2:F to maintain order)
    try:
        # Clear existing data first? Or just update? Let's overwrite A2:F with our full sync
        sheets_service.spreadsheets().values().clear(
            spreadsheetId=SPREADSHEET_ID, range="'Report'!A2:F"
        ).execute()
        
        sheets_service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID, range="'Report'!A2",
            valueInputOption='USER_ENTERED', body={'values': report_rows}
        ).execute()
        print(f"Successfully updated Weekly Report for {len(report_rows)} week-site entries.")
    except Exception as e:
        print(f"Error updating Report tab: {e}")

if __name__ == '__main__':
    run_update()
    # Initialize services again for reporting or pass them through
    _, sheets_service = get_services()
    update_weekly_report(sheets_service)
