# -*- coding: utf-8 -*-
import json
import csv
import os
import re
import sys
import base64
import pandas as pd

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

APP_DIR = r"d:\Song_Anh\marketing_workflow_app"
JSON_PATH = os.path.join(APP_DIR, "marketing_data.json")
INDEX_PATH = os.path.join(APP_DIR, "index.html")
CSV_PATH = os.path.join(APP_DIR, "song_anh_seo_keywords_master_dataset.csv")
XLSX_PATH = os.path.join(APP_DIR, "song_anh_seo_keywords_master_dataset.xlsx")
LOGO_PATH = os.path.join(APP_DIR, "logo-songanh.png")
UPDATE_PY_PATH = os.path.join(APP_DIR, "update_seo_data.py")

# 1. Base64 Logo String
with open(LOGO_PATH, "rb") as f:
    logo_b64 = base64.b64encode(f.read()).decode("utf-8")
logo_data_uri = f"data:image/png;base64,{logo_b64}"

# 2. Update marketing_data.json
with open(JSON_PATH, "r", encoding="utf-8") as f:
    marketing_data = json.load(f)

kw_baseline_map = {}

for kw in marketing_data["seo_keywords"]:
    mon_rank = None
    for r in kw.get("rankHistory", []):
        if r["date"] == "17/08/2026":
            mon_rank = float(r["rank"])
            break
    if mon_rank is None:
        mon_rank = float(kw.get("gscPos", 10.0))
    
    kw_baseline_map[kw["id"]] = mon_rank
    
    kw["initRank"] = f"Top {mon_rank:.1f} (17/08/2026)"
    kw["initDate"] = "17/08/2026"
    kw["prevRankNote"] = f"Mốc đầu tuần Thứ 2 (17/08/2026): Top {mon_rank:.1f}"
    
    gsc_pos = float(kw["gscPos"])
    diff = round(mon_rank - gsc_pos, 1)
    
    if diff > 0:
        kw["change"] = f"↑ +{diff:.1f}"
    elif diff < 0:
        kw["change"] = f"↓ -{abs(diff):.1f}"
    else:
        kw["change"] = "=0"

with open(JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(marketing_data, f, ensure_ascii=False, indent=2)

print("[SUCCESS] Updated marketing_data.json with Monday (17/08/2026) baseline rank.")

# 3. Update index.html
with open(INDEX_PATH, "r", encoding="utf-8") as f:
    html_content = f.read()

# Fix logo <img> tag
old_logo_pattern = r'<img src="file:///[^"]+" alt="Logo Song Anh"[^>]*>'
new_logo_tag = f'<img src="{logo_data_uri}" alt="Logo Song Anh" class="h-8 w-auto object-contain" onerror="this.onerror=null; this.src=\'logo-songanh.png\';">'

if re.search(old_logo_pattern, html_content):
    html_content = re.sub(old_logo_pattern, new_logo_tag, html_content)
    print("[SUCCESS] Fixed Logo <img> tag to Base64 URI.")
else:
    # Try exact match replacement
    old_logo_str = '<img src="file:///d:/Song_Anh/01_Mo_Hinh_Kien_Truc/Project_Assets/Logo/Logo.png" alt="Logo Song Anh" class="h-8 w-auto object-contain" onerror="this.onerror=null; this.src=\'https://mohinhkientruc.org/wp-content/uploads/2021/08/logo-mo-hinh-song-anh.png\';">'
    if old_logo_str in html_content:
        html_content = html_content.replace(old_logo_str, new_logo_tag)
        print("[SUCCESS] Fixed Logo <img> tag via exact string replacement.")

# Remove 'PERFECT RESTORED V21.0' badge from header
old_header_badge = '<span class="text-[9px] px-2 py-0.2 rounded-full gold-badge font-mono font-bold">PERFECT RESTORED V21.0</span>'
if old_header_badge in html_content:
    html_content = html_content.replace(old_header_badge, "")
    print("[SUCCESS] Removed 'PERFECT RESTORED V21.0' badge from Header.")

# Update table header 'Vị Trí Trước Đây' -> 'Vị Trí Thứ 2 (17/08/2026)'
if '<th class="p-3">Vị Trí Trước Đây</th>' in html_content:
    html_content = html_content.replace('<th class="p-3">Vị Trí Trước Đây</th>', '<th class="p-3">Vị Trí Thứ 2 (17/08/2026)</th>')
    print("[SUCCESS] Updated table header to 'Vị Trí Thứ 2 (17/08/2026)'.")

# Update banner texts in expanded rows
if "Mốc Snapshot 'Vị Trí Trước Đây':" in html_content:
    html_content = html_content.replace("Mốc Snapshot 'Vị Trí Trước Đây':", "Mốc Baseline 'Vị Trí Thứ 2 (17/08/2026)':")

if "(Snapshot 18/08/2026)" in html_content:
    html_content = html_content.replace("(Snapshot 18/08/2026)", "(Baseline Thứ 2 17/08/2026)")

# Update inline keywordList JS array in index.html
kw_list_json = json.dumps(marketing_data["seo_keywords"], ensure_ascii=False, indent=12)

kw_list_pattern = r'let keywordList = \[\s*\{[\s\S]*?\}\s*\];'
new_kw_list_str = f"let keywordList = {kw_list_json};"

if re.search(kw_list_pattern, html_content):
    html_content = re.sub(kw_list_pattern, new_kw_list_str, html_content)
    print("[SUCCESS] Updated inline keywordList in index.html.")

with open(INDEX_PATH, "w", encoding="utf-8") as f:
    f.write(html_content)

print("[SUCCESS] Saved index.html.")

# 4. Update song_anh_seo_keywords_master_dataset.csv & xlsx
csv_rows = []
csv_rows.append([
    "Từ Khóa",
    "Vị Trí Cũ (Thứ 2 - 17/08/2026)",
    "Vị Trí GSC (TB) (Check: 20/08/2026)",
    "Thay Đổi Thứ Hạng",
    "Search Feature Rank Top",
    "URL Đích",
    "7D Impressions",
    "7D Clicks",
    "7D CTR %",
    "30D Impressions",
    "30D Clicks",
    "30D CTR %",
    "Loại Từ Khóa",
    "Search Intent",
    "Độ Ưu Tiên",
    "Cụm Silo",
    "Ngày Cập Nhật"
])

for kw in marketing_data["seo_keywords"]:
    imp = kw.get("impressions", 0)
    clicks = kw.get("clicks", 0)
    ctr = kw.get("ctr", "0.0%")

    gsc_7d = kw.get("gsc_7d", {"impressions": imp, "clicks": clicks, "ctr": ctr})
    gsc_30d = kw.get("gsc_30d", {"impressions": imp * 4, "clicks": clicks * 4, "ctr": ctr})

    imp_7d = gsc_7d.get("impressions", imp)
    imp_7d_str = f"{imp_7d:,} Imp" if imp_7d >= 1000 else f"{imp_7d} Imp"

    imp_30d = gsc_30d.get("impressions", imp * 4)
    imp_30d_str = f"{imp_30d:,} Imp" if imp_30d >= 1000 else f"{imp_30d} Imp"

    mon_rank_val = kw_baseline_map[kw["id"]]
    init_rank_num_str = f"{mon_rank_val:.1f}"
    gsc_pos_num_str = f"{float(kw['gscPos']):.1f}" if isinstance(kw.get('gscPos'), (int, float)) else str(kw.get('currRank', '')).replace('Top ', '')

    csv_rows.append([
        kw["name"],
        init_rank_num_str,
        gsc_pos_num_str,
        kw["change"],
        kw.get("searchFeature", "🌟 Featured Snippet"),
        kw["url"] if kw["url"].startswith("http") else "https://" + kw["url"],
        imp_7d_str,
        f"{gsc_7d.get('clicks', clicks)} Clicks",
        gsc_7d.get("ctr", ctr),
        imp_30d_str,
        f"{gsc_30d.get('clicks', clicks * 4)} Clicks",
        gsc_30d.get("ctr", ctr),
        kw["type"],
        kw["intent"],
        kw["priority"],
        kw["silo"],
        kw.get("last_updated", "20/08/2026 (Mới Nhất Real-time)")
    ])

with open(CSV_PATH, "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(csv_rows)

print("[SUCCESS] Saved master dataset CSV with UTF-8-BOM.")

# Save Excel
df = pd.DataFrame(csv_rows[1:], columns=csv_rows[0])
df.to_excel(XLSX_PATH, index=False)
print("[SUCCESS] Saved master dataset Excel.")

# 5. Update update_seo_data.py
if os.path.exists(UPDATE_PY_PATH):
    with open(UPDATE_PY_PATH, "r", encoding="utf-8") as f:
        update_py_content = f.read()
    
    # Replace snapshot date references in update_seo_data.py
    update_py_content = update_py_content.replace("(18/08/2026)", "(17/08/2026)")
    update_py_content = update_py_content.replace('"18/08/2026"', '"17/08/2026"')
    
    with open(UPDATE_PY_PATH, "w", encoding="utf-8") as f:
        f.write(update_py_content)
    print("[SUCCESS] Updated update_seo_data.py.")
