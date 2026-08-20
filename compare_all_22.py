import json
import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

TARGET_MAP = {
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

for idx, item in enumerate(mdata.get('seo_keywords', [])):
    kw = item.get('name', '').strip()
    url = item.get('url', '').strip()
    expected = TARGET_MAP.get(kw.lower(), '')
    match = (url == expected or url == expected.replace("https://", ""))
    status = "OK" if match else f"DIFF (Current: {url} | Expected: {expected})"
    print(f"{idx+1:2d}. {kw:25s} -> {status}")
