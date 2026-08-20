import json
import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

URL_MAP_CORRECT = {
    "mô hình quy hoạch": "https://mohinhkientruc.org/danh-muc-du-an/mo-hinh-quy-hoach/",
    "sa bàn quy hoạch": "https://mohinhkientruc.org/dich-vu-lam-sa-ban-quy-hoach/",
    "mô hình kiến trúc": "https://mohinhkientruc.org/mo-hinh-kien-truc/",
    "sa bàn kiến trúc": "https://mohinhkientruc.org/sa-ban-kien-truc/",
    "mô hình cao tầng": "https://mohinhkientruc.org/sa-ban-cao-tang/",
    "sa bàn cao tầng": "https://mohinhkientruc.org/sa-ban-cao-tang/",
    "mô hình nhà máy": "https://mohinhkientruc.org/mo-hinh-nha-may/",
    "sa bàn nhà máy": "https://mohinhkientruc.org/thi-cong-sa-ban-nha-may-khu-cong-nghiep/",
    "mô hình thiết bị": "https://mohinhkientruc.org/mo-hinh-3d/",
    "sa bàn thiết bị": "https://mohinhkientruc.org/sa-ban-noi-that/",
    "mô hình trường học": "https://mohinhkientruc.org/lam-sa-ban-truong-hoc/",
    "sa bàn trường học": "https://mohinhkientruc.org/lam-sa-ban-truong-hoc/",
    "mô hình bệnh viện": "https://mohinhkientruc.org/mo-hinh-tod-sa-ban/",
    "sa bàn bệnh viện": "https://mohinhkientruc.org/du-an-noi-bat/",
    "vận chuyển mô hình": "https://mohinhkientruc.org/van-chuyen-sa-ban-kien-truc/",
    "vận chuyển sa bàn": "https://mohinhkientruc.org/van-chuyen-sa-ban-kien-truc/",
    "sửa chữa mô hình": "https://mohinhkientruc.org/sua-chua-mo-hinh-kien-truc/",
    "sửa chữa sa bàn": "https://mohinhkientruc.org/sua-chua-mo-hinh-kien-truc/",
    "công ty mô hình kiến trúc": "https://mohinhkientruc.org/cong-ty-lam-mo-hinh/",
    "công ty sa bàn kiến trúc": "https://mohinhkientruc.org/",
    "làm mô hình": "https://mohinhkientruc.org/lam-mo-hinh-kien-truc/",
    "làm sa bàn": "https://mohinhkientruc.org/lam-sa-ban/"
}

print("=== CHECKING MARKETING_DATA.JSON ===")
with open('marketing_workflow_app/marketing_data.json', 'r', encoding='utf-8') as f:
    mdata = json.load(f)

for item in mdata.get('seo_keywords', []):
    kw = item.get('keyword', '').strip()
    url = str(item.get('target_url') or item.get('url') or item.get('landing_page') or '').strip()
    expected = URL_MAP_CORRECT.get(kw.lower(), '')
    match = (url == expected or url == expected.replace("https://", ""))
    print(f"[{'OK' if match else 'DIFF'}] KW: '{kw}' | Current URL: '{url}' | Expected: '{expected}'")

print("\n=== CHECKING MASTER CSV ===")
df_master = pd.read_csv('marketing_workflow_app/song_anh_seo_keywords_master_dataset.csv', encoding='utf-8')
print("Master CSV Columns:", list(df_master.columns))
for idx, row in df_master.iterrows():
    kw = str(row.get('keyword', '')).strip()
    url = str(row.get('target_url', row.get('url', ''))).strip()
    expected = URL_MAP_CORRECT.get(kw.lower(), '')
    match = (url == expected or url == expected.replace("https://", ""))
    print(f"[{'OK' if match else 'DIFF'}] Row {idx+1} KW: '{kw}' | Current URL: '{url}' | Expected: '{expected}'")
